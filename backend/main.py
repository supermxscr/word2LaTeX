"""FastAPI app: Word to LaTeX conversion API."""
from __future__ import annotations

import base64
import io
import os
import tempfile
import zipfile
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, StreamingResponse, JSONResponse

from presets import PRESETS, get_preset
from converter import (
    convert_upload_to_tex,
    convert_upload_to_tex_with_media,
    postprocess_tex,
    compile_tex_to_pdf,
)

app = FastAPI(
    title="Word to LaTeX API",
    description="Convert Word (.docx) to LaTeX with journal presets (e.g. Aries EM).",
    version="0.1.0",
)

# CORS：通过 CORS_ORIGINS 配置（逗号分隔）；未设置时允许本地 + 生产前端
_default_origins = "http://localhost:3000,http://127.0.0.1:3000,https://word2-latex.vercel.app"
_cors_origins = os.getenv("CORS_ORIGINS", _default_origins)
_origins = [o.strip() for o in _cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> dict[str, str]:
    return {"service": "word2latex", "status": "ok"}


@app.get("/presets")
async def list_presets() -> dict[str, Any]:
    """Return available format presets for dropdown."""
    items = [
        {
            "id": p.id,
            "name": p.name,
            "description": p.description,
        }
        for p in PRESETS.values()
    ]
    return {"presets": items}


@app.post("/convert", response_model=None)
async def convert(
    file: UploadFile = File(...),
    preset_id: str = "aries_em",
):
    """
    Convert uploaded .docx to LaTeX. Returns zip (flat) with main .tex.
    """
    if not file.filename or not file.filename.lower().endswith(".docx"):
        raise HTTPException(status_code=400, detail="Only .docx files are accepted")

    preset = get_preset(preset_id)
    if not preset:
        raise HTTPException(status_code=400, detail=f"Unknown preset: {preset_id}")

    try:
        raw_bytes = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {e}") from e

    try:
        raw_tex, media_files = convert_upload_to_tex_with_media(raw_bytes)
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail=f"Pandoc conversion failed: {str(e)}",
        ) from e

    tex_content = postprocess_tex(raw_tex, preset_id)

    # ZIP: flat directory per EM — main.tex + all images (+ main.pdf if compile succeeds)
    main_name = "main.tex"
    pdf_name = "main.pdf"
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(main_name, tex_content.encode("utf-8"))
        for name, data in media_files:
            zf.writestr(name, data)
        with tempfile.TemporaryDirectory(prefix="word2latex_zip_") as tmp:
            tmpdir = Path(tmp)
            for name, data in media_files:
                (tmpdir / name).write_bytes(data)
            pdf_path, _ = compile_tex_to_pdf(tex_content, tmpdir, timeout_seconds=180)
            if pdf_path and pdf_path.exists():
                zf.writestr(pdf_name, pdf_path.read_bytes())

    buf.seek(0)
    download_name = file.filename or "document.docx"
    base = download_name.rsplit(".", 1)[0] if "." in download_name else "document"
    zip_name = f"{base}_latex.zip"

    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="{zip_name}"',
        },
    )


@app.post("/convert/tex")
async def convert_tex_only(
    file: UploadFile = File(...),
    preset_id: str = "aries_em",
) -> PlainTextResponse:
    """Convert to LaTeX and return raw .tex content (for preview without zip)."""
    if not file.filename or not file.filename.lower().endswith(".docx"):
        raise HTTPException(status_code=400, detail="Only .docx files are accepted")

    preset = get_preset(preset_id)
    if not preset:
        raise HTTPException(status_code=400, detail=f"Unknown preset: {preset_id}")

    try:
        raw_bytes = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {e}") from e

    try:
        raw_tex = convert_upload_to_tex(raw_bytes)
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail=f"Pandoc conversion failed: {str(e)}",
        ) from e

    tex_content = postprocess_tex(raw_tex, preset_id)
    return PlainTextResponse(tex_content, media_type="text/plain; charset=utf-8")


@app.post("/convert/preview")
async def convert_preview(
    file: UploadFile = File(...),
    preset_id: str = "aries_em",
) -> JSONResponse:
    """
    一步转换：生成 LaTeX 并编译 PDF，返回两者供预览。
    无需 Redis。PDF 编译需要本机安装 TeX Live（或 Docker 内安装）。
    """
    if not file.filename or not file.filename.lower().endswith(".docx"):
        raise HTTPException(status_code=400, detail="Only .docx files are accepted")

    preset = get_preset(preset_id)
    if not preset:
        raise HTTPException(status_code=400, detail=f"Unknown preset: {preset_id}")

    try:
        raw_bytes = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {e}") from e

    try:
        raw_tex, media_files = convert_upload_to_tex_with_media(raw_bytes)
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail=f"Pandoc conversion failed: {str(e)}",
        ) from e

    tex_content = postprocess_tex(raw_tex, preset_id)

    payload: dict[str, Any] = {"tex_content": tex_content, "pdf_base64": None}
    compile_log: str | None = None

    with tempfile.TemporaryDirectory(prefix="word2latex_preview_") as tmp:
        tmpdir = Path(tmp)
        for name, data in media_files:
            (tmpdir / name).write_bytes(data)
        pdf_path, log = compile_tex_to_pdf(tex_content, tmpdir, timeout_seconds=180)
        if pdf_path and pdf_path.exists():
            payload["pdf_base64"] = base64.b64encode(pdf_path.read_bytes()).decode("ascii")
        else:
            compile_log = log or "PDF 编译未成功（可能未安装 TeX Live）。"
    if compile_log:
        # 保留日志末尾，便于看到 pdflatex 的实际报错
        payload["compile_log"] = compile_log[-8000:] if len(compile_log) > 8000 else compile_log

    return JSONResponse(content=payload)
