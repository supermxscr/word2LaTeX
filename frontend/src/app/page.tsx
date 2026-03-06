"use client";

import { useEffect, useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { FileText, Download, Loader2, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8005";

type Preset = { id: string; name: string; description: string | null };

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [presetId, setPresetId] = useState<string>("aries_em");
  const [presets, setPresets] = useState<Preset[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [texContent, setTexContent] = useState<string | null>(null);
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [compileLog, setCompileLog] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetch(`${API_BASE}/presets`)
      .then((res) => res.json())
      .then((data) => {
        if (cancelled) return;
        const list = data.presets || [];
        setPresets(list.length ? list : [{ id: "aries_em", name: "Aries EM", description: "Editorial Manager" }]);
      })
      .catch(() => {
        if (!cancelled) setPresets([{ id: "aries_em", name: "Aries EM", description: "Editorial Manager" }]);
      });
    return () => { cancelled = true; };
  }, []);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const f = acceptedFiles[0];
    if (f?.name?.toLowerCase().endsWith(".docx")) {
      setFile(f);
      setError(null);
      setTexContent(null);
      setPdfUrl(null);
      setCompileLog(null);
    } else {
      setError("请上传 .docx 文件");
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"] },
    maxFiles: 1,
    disabled: loading,
  });

  const convertAndPreview = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    setTexContent(null);
    setPdfUrl(null);
    setCompileLog(null);
    // Revoke previous PDF blob URL if any
    if (pdfUrl) URL.revokeObjectURL(pdfUrl);

    try {
      const form = new FormData();
      form.append("file", file);
      const res = await fetch(`${API_BASE}/convert/preview?preset_id=${presetId}`, {
        method: "POST",
        body: form,
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(err.detail || "转换失败");
      }
      const data = await res.json();
      setTexContent(data.tex_content ?? null);
      if (data.compile_log) setCompileLog(data.compile_log);
      if (data.pdf_base64) {
        const bin = Uint8Array.from(atob(data.pdf_base64), (c) => c.charCodeAt(0));
        const blob = new Blob([bin], { type: "application/pdf" });
        setPdfUrl(URL.createObjectURL(blob));
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "转换失败");
    } finally {
      setLoading(false);
    }
  };

  const downloadZip = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      const form = new FormData();
      form.append("file", file);
      const res = await fetch(`${API_BASE}/convert?preset_id=${presetId}`, {
        method: "POST",
        body: form,
      });
      if (!res.ok) throw new Error("下载失败");
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = (file.name.replace(/\.docx$/i, "") || "document") + "_latex.zip";
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      setError(e instanceof Error ? e.message : "下载失败");
    } finally {
      setLoading(false);
    }
  };

  const downloadTex = () => {
    if (!texContent) return;
    const blob = new Blob([texContent], { type: "text/plain; charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = (file?.name.replace(/\.docx$/i, "") || "main") + ".tex";
    a.click();
    URL.revokeObjectURL(url);
  };

  const downloadPdf = () => {
    if (!pdfUrl) return;
    const a = document.createElement("a");
    a.href = pdfUrl;
    a.download = (file?.name.replace(/\.docx$/i, "") || "document") + ".pdf";
    a.click();
  };

  return (
    <div className="min-h-screen bg-background p-4 md:p-8">
      <div className="mx-auto max-w-4xl space-y-6">
        <header className="text-center">
          <h1 className="text-3xl font-bold tracking-tight">Word → LaTeX</h1>
          <p className="mt-2 text-muted-foreground">上传 Word 文档，选择格式预设，一键转换为 LaTeX 并预览 PDF</p>
        </header>

        <Card>
          <CardHeader>
            <CardTitle>上传与预设</CardTitle>
            <CardDescription>支持 .docx，一步生成 LaTeX 与 PDF 预览</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div
              {...getRootProps()}
              className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                isDragActive ? "border-primary bg-muted/50" : "border-muted-foreground/25 hover:border-primary/50"
              }`}
            >
              <input {...getInputProps()} />
              <FileText className="mx-auto h-12 w-12 text-muted-foreground" />
              <p className="mt-2 text-sm text-muted-foreground">
                {file ? file.name : "拖拽 .docx 到此处或点击选择"}
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-4">
              <span className="text-sm text-muted-foreground">格式预设：</span>
              <Select value={presetId} onValueChange={setPresetId}>
                <SelectTrigger className="w-[280px]">
                  <SelectValue placeholder="选择预设" />
                </SelectTrigger>
                <SelectContent>
                  {presets.map((p) => (
                    <SelectItem key={p.id} value={p.id}>
                      {p.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {error && (
              <div className="flex items-center gap-2 rounded-md border border-destructive/50 bg-destructive/10 px-4 py-3 text-sm text-destructive">
                <AlertCircle className="h-4 w-4 shrink-0" />
                {error}
              </div>
            )}

            <div className="flex flex-wrap gap-3">
              <Button onClick={convertAndPreview} disabled={!file || loading}>
                {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
                转换并预览
              </Button>
              <Button variant="outline" onClick={downloadZip} disabled={!file || loading}>
                直接下载 ZIP
              </Button>
            </div>
            {loading && (
              <p className="text-sm text-muted-foreground">
                含 PDF 时约需 30 秒～2 分钟，请勿关闭页面。
              </p>
            )}
          </CardContent>
        </Card>

        {(texContent || pdfUrl || compileLog || loading) && (
          <Card>
            <CardHeader>
              <CardTitle>转换预览</CardTitle>
              <CardDescription>LaTeX 源码与 PDF 预览</CardDescription>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="latex">
                <TabsList>
                  <TabsTrigger value="latex">LaTeX</TabsTrigger>
                  <TabsTrigger value="pdf">PDF</TabsTrigger>
                </TabsList>
                <TabsContent value="latex" className="mt-4">
                  {loading && !texContent && (
                    <div className="flex flex-col items-center justify-center gap-3 py-16 text-muted-foreground">
                      <Loader2 className="h-10 w-10 animate-spin" />
                      <p>正在转换并生成 LaTeX…</p>
                    </div>
                  )}
                  {compileLog && !loading && (
                    <div className="mb-4 rounded-md border border-amber-500/50 bg-amber-500/10 p-3 text-sm text-amber-800 dark:text-amber-200">
                      <strong>编译说明：</strong>
                      <pre className="mt-1 max-h-32 overflow-auto whitespace-pre-wrap font-mono text-xs">{compileLog}</pre>
                    </div>
                  )}
                  {texContent && (
                    <>
                      <div className="flex justify-end">
                        <Button variant="outline" size="sm" onClick={downloadTex}>
                          <Download className="h-4 w-4 mr-1" />
                          下载 .tex
                        </Button>
                      </div>
                      <pre className="mt-2 max-h-[60vh] overflow-auto rounded-md border bg-muted/30 p-4 text-left text-sm font-mono whitespace-pre-wrap break-words">
                        {texContent}
                      </pre>
                    </>
                  )}
                </TabsContent>
                <TabsContent value="pdf" className="mt-4">
                  {loading && !pdfUrl && (
                    <div className="flex flex-col items-center justify-center gap-4 rounded-md border bg-muted/30 py-20">
                      <Loader2 className="h-12 w-12 animate-spin text-muted-foreground" />
                      <div className="text-center space-y-1">
                        <p className="font-medium">PDF 正在生成中…</p>
                        <p className="text-sm text-muted-foreground">
                          通常需要 30 秒～2 分钟，请稍候、勿关闭页面。
                        </p>
                      </div>
                    </div>
                  )}
                  {!loading && pdfUrl && (
                    <>
                      <div className="flex justify-end mb-2">
                        <Button variant="outline" size="sm" onClick={downloadPdf}>
                          <Download className="h-4 w-4 mr-1" />
                          下载 PDF
                        </Button>
                      </div>
                      <iframe
                        src={pdfUrl}
                        title="PDF 预览"
                        className="w-full h-[70vh] rounded-md border bg-muted/30"
                      />
                    </>
                  )}
                  {!loading && !pdfUrl && (texContent || compileLog) && (
                    <div className="rounded-md border border-amber-500/50 bg-amber-500/10 p-4 text-sm text-amber-800 dark:text-amber-200">
                      <p className="font-medium">未生成 PDF</p>
                      <p className="mt-1 text-muted-foreground">可能未安装 TeX Live、编译超时或文档有 LaTeX 错误。LaTeX 已生成，可下载 .tex 或 ZIP 后在本地用 TeX Live 编译。</p>
                      {(compileLog?.includes("latexmk") ?? false) && (
                        <p className="mt-2 text-xs text-muted-foreground">若下方日志显示 “Rerun” 或 “applying rule” 但无后续错误，多为首次编译较慢导致超时，可再试一次或本地编译。</p>
                      )}
                      {compileLog && (
                        <pre className="mt-3 max-h-56 overflow-auto whitespace-pre-wrap rounded bg-black/10 p-2 font-mono text-xs">{compileLog}</pre>
                      )}
                    </div>
                  )}
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
