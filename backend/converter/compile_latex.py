"""Compile LaTeX to PDF via latexmk/pdflatex (optional; requires TeX Live)."""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


# 常见 TeX 安装路径（安装后即使当前 shell 未更新 PATH 也能找到）
def _tex_search_dirs() -> list[Path]:
    dirs = [
        Path("/Library/TeX/texbin"),  # MacTeX / BasicTeX 符号链接 (macOS)
        Path("/usr/local/texlive/2026basic/bin/universal-darwin"),
        Path("/usr/local/texlive/2026/bin/universal-darwin"),
        Path("/usr/local/texlive/2024/bin/universal-darwin"),
        Path("/usr/local/texlive/2023/bin/universal-darwin"),
        Path("/usr/local/texlive/2024/bin/x86_64-darwin"),
        Path("/usr/local/texlive/2023/bin/x86_64-darwin"),
    ]
    # TeX Live 根目录下的任意版本 /bin/*/
    tl_root = Path("/usr/local/texlive")
    if tl_root.exists():
        for tl in tl_root.iterdir():
            bin_dir = tl / "bin"
            if bin_dir.is_dir():
                for arch in bin_dir.iterdir():
                    if arch.is_dir():
                        dirs.append(arch)
    texlive_home = os.environ.get("TEXLIVE_HOME", "")
    if texlive_home:
        dirs.insert(0, Path(texlive_home) / "bin")
    return dirs


def _find_tex_cmd(name: str) -> str | None:
    """先查 PATH，再查常见安装目录。"""
    out = shutil.which(name)
    if out:
        return out
    for d in _tex_search_dirs():
        if not d.is_dir():
            continue
        p = d / name
        if p.is_file() and os.access(p, os.X_OK):
            return str(p)
    return None


def compile_tex_to_pdf(
    tex_content: str,
    work_dir: Path,
    main_name: str = "main.tex",
    timeout_seconds: int = 180,
) -> tuple[Path | None, str]:
    """
    Write tex to work_dir/main.tex, run latexmk (or pdflatex), return (pdf_path, log).
    If compilation fails, returns (None, log).
    """
    work_dir.mkdir(parents=True, exist_ok=True)
    main_path = work_dir / main_name
    main_path.write_text(tex_content, encoding="utf-8")

    log_lines: list[str] = []
    pdf_path = work_dir / main_name.replace(".tex", ".pdf")

    env = os.environ.copy()
    # 把 latexmk 与 pdflatex 所在目录都加入 PATH，否则 latexmk 子进程里会找不到 pdflatex
    tex_bin_dirs: list[str] = []
    latexmk_cmd = _find_tex_cmd("latexmk")
    if latexmk_cmd:
        tex_bin_dirs.append(str(Path(latexmk_cmd).resolve().parent))
    pdflatex_cmd = _find_tex_cmd("pdflatex")
    if pdflatex_cmd:
        d = str(Path(pdflatex_cmd).resolve().parent)
        if d not in tex_bin_dirs:
            tex_bin_dirs.append(d)
    if tex_bin_dirs:
        env["PATH"] = os.pathsep.join(tex_bin_dirs) + os.pathsep + env.get("PATH", "")

    if latexmk_cmd:
        # 显式指定 pdflatex 完整路径，避免子进程 PATH 里找不到
        cmd = [
            latexmk_cmd,
            "-pdf",
            "-interaction=nonstopmode",
            "-halt-on-error",
            str(main_path.name),
        ]
        if pdflatex_cmd:
            cmd.insert(-1, f"-pdflatex={pdflatex_cmd}")
        cwd = str(work_dir)
    else:
        if not pdflatex_cmd:
            return None, "未检测到 TeX Live（未找到 latexmk / pdflatex），无法生成 PDF。请安装 TeX Live 或 MacTeX 后重试。"
        cmd = [
            pdflatex_cmd,
            "-interaction=nonstopmode",
            "-halt-on-error",
            str(main_path.name),
        ]
        cwd = str(work_dir)

    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            env=env,
        )
        log_lines.append(result.stdout or "")
        log_lines.append(result.stderr or "")
        if not latexmk_cmd and result.returncode == 0:
            # Run twice for refs
            subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                timeout=timeout_seconds,
                env=env,
            )
        if pdf_path.exists():
            return pdf_path, "\n".join(log_lines)
        # 无 PDF 时附上 pdflatex 生成的 .log，里面有具体报错
        out_log = "\n".join(log_lines)
        log_file = work_dir / main_path.name.replace(".tex", ".log")
        if log_file.exists():
            try:
                out_log += "\n\n--- pdflatex .log 文件 ---\n" + log_file.read_text(encoding="utf-8", errors="replace")
            except Exception:
                pass
        return None, out_log
    except subprocess.TimeoutExpired:
        return None, "PDF 编译超时（超过 {} 秒）。".format(timeout_seconds)
    except Exception as e:
        return None, str(e)
