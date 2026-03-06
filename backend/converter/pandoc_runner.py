"""Run Pandoc to convert Word (.docx) to LaTeX."""
from __future__ import annotations

import re
import tempfile
from pathlib import Path

import pypandoc

from .postprocess import _safe_basename


def docx_to_tex(docx_path: Path, output_path: Path | None = None) -> str:
    """
    Convert a .docx file to LaTeX using Pandoc.
    Returns the LaTeX content as string. If output_path is given, also writes there.
    """
    latex = pypandoc.convert_file(
        str(docx_path),
        "latex",
        format="docx",
        extra_args=[
            "--standalone",
            "--wrap=preserve",
        ],
    )
    if output_path is not None:
        output_path.write_text(latex, encoding="utf-8")
    return latex


def convert_upload_to_tex(docx_bytes: bytes) -> str:
    """
    Write uploaded bytes to a temp .docx, convert to LaTeX, return LaTeX string.
    """
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
        f.write(docx_bytes)
        path = Path(f.name)
    try:
        return docx_to_tex(path)
    finally:
        path.unlink(missing_ok=True)


def convert_upload_to_tex_with_media(docx_bytes: bytes) -> tuple[str, list[tuple[str, bytes]]]:
    """
    Convert .docx to LaTeX and extract all images/media. Returns (tex_content, [(zip_name, file_bytes), ...]).
    Media are flattened to a single directory level with EM-safe filenames.
    """
    with tempfile.TemporaryDirectory(prefix="word2latex_") as tmp:
        tmpdir = Path(tmp)
        docx_path = tmpdir / "input.docx"
        docx_path.write_bytes(docx_bytes)
        main_tex = tmpdir / "main.tex"
        pypandoc.convert_file(
            str(docx_path),
            "latex",
            format="docx",
            outputfile=str(main_tex),
            extra_args=[
                "--standalone",
                "--wrap=preserve",
                f"--extract-media={tmpdir}",
            ],
        )
        tex_content = main_tex.read_text(encoding="utf-8")

        media_dir = tmpdir / "media"
        media_list: list[tuple[str, bytes]] = []
        path_to_zip_name: dict[str, str] = {}
        seen: set[str] = set()

        if media_dir.exists():
            for f in sorted(media_dir.rglob("*")):
                if f.is_file():
                    rel = f.relative_to(media_dir)
                    path_in_tex = Path("media") / rel
                    path_key = str(path_in_tex).replace("\\", "/")
                    base = _safe_basename(f.name)
                    name = base
                    i = 2
                    while name in seen:
                        stem, ext = f.stem, f.suffix
                        name = f"{stem}_{i}{ext}"
                        i += 1
                    seen.add(name)
                    path_to_zip_name[path_key] = name
                    media_list.append((name, f.read_bytes()))

        # Replace \includegraphics{path} in tex with zip names so they match the flat zip
        def repl(m: re.Match) -> str:
            opts = m.group(1) or ""
            path = m.group(2).strip().replace("\\", "/")
            name = path_to_zip_name.get(path, _safe_basename(Path(path).name))
            return f"\\includegraphics[{opts}]{{{name}}}"

        tex_content = re.sub(
            r"\\includegraphics\s*(\[[^\]]*\])?\s*\{([^}]+)\}",
            repl,
            tex_content,
        )

        return tex_content, media_list
