"""Post-process generated LaTeX according to preset (e.g. Aries EM)."""
from __future__ import annotations

import re
from pathlib import Path

from presets import PresetConfig, get_preset


# Reserved filenames per EM guide (no extension)
_RESERVED = {
    "CON", "PRN", "AUX", "NUL",
    "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
    "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9",
}


def _safe_basename(name: str) -> str:
    """Ensure filename has only one period (extension) and no reserved names."""
    base = Path(name).stem
    ext = Path(name).suffix
    if base.upper() in _RESERVED:
        base = f"file_{base}"
    # Remove special chars that EM excludes
    base = re.sub(r"[^a-zA-Z0-9_-]", "_", base)
    if not base:
        base = "file"
    return base + ext


def apply_preset(tex_content: str, preset_id: str) -> str:
    """
    Apply preset to raw LaTeX: documentclass, packages, optional first-line directives.
    Does not change \\includegraphics paths here (that would need file listing).
    """
    preset = get_preset(preset_id)
    if not preset:
        return tex_content

    # Optional first-line directives (prepend)
    prefix_lines: list[str] = []
    if preset.use_xelatex:
        prefix_lines.append("%!TEX TS-program = xelatex")
    if preset.use_biber:
        prefix_lines.append("% !BIB TS-program = biber")

    # Replace \\documentclass[...]{...} or \\documentclass{...} with preset
    docclass_re = re.compile(r"\\documentclass(?:\[[^\]]*\])?\{[^}]+\}")
    opts = "[" + ",".join(preset.documentclass_options) + "]" if preset.documentclass_options else ""
    new_docclass = f"\\documentclass{opts}{{{preset.documentclass}}}"
    # Use a function replacement so backslashes aren't treated as escapes
    text = docclass_re.sub(lambda _m: new_docclass, tex_content, count=1)
    if prefix_lines:
        text = "\n".join(prefix_lines) + "\n" + text

    # Ensure required packages in preamble (append before \\begin{document})
    pack_need = [p for p in preset.packages if f"\\usepackage{{{p}}}" not in text]
    if pack_need:
        pack_line = "\n".join(f"\\usepackage{{{p}}}" for p in pack_need)
        text = text.replace("\\begin{document}", pack_line + "\n\\begin{document}", 1)

    return text


def normalize_includegraphics_paths(tex_content: str) -> str:
    """
    Replace \\includegraphics{path/to/file.ext} with \\includegraphics[opts]{file.ext}
    so all references are flat (EM requirement). Also fix double brackets [[...]] from Pandoc.
    """
    # Pandoc 有时输出 [[width=...,height=...]]，先统一成单层 [...]
    tex_content = re.sub(
        r"\\includegraphics\s*\[\[([^\]]*)\]\]\s*\{",
        r"\\includegraphics[\1]{",
        tex_content,
    )

    def repl(m: re.Match) -> str:
        opts = (m.group(1) or "").strip()
        if opts.startswith("[") and opts.endswith("]"):
            opts = opts[1:-1]
        path = m.group(2).strip()
        base = _safe_basename(Path(path).name)
        opts_part = f"[{opts}]" if opts else ""
        return f"\\includegraphics{opts_part}{{{base}}}"

    return re.sub(
        r"\\includegraphics\s*(\[[^\]]*\])?\s*\{([^}]+)\}",
        repl,
        tex_content,
    )


def _fix_common_math(tex_content: str) -> str:
    """
    Fix common OMML->LaTeX issues from Pandoc (per EM guide and TeX FAQ).
    """
    # \deltat is not valid; use \delta t
    text = re.sub(r"\\deltat\b", r"\\delta t", tex_content)
    return text


def postprocess_tex(tex_content: str, preset_id: str) -> str:
    """Full postprocess: formula fixes + preset + flatten includegraphics paths."""
    content = _fix_common_math(tex_content)
    content = apply_preset(content, preset_id)
    content = normalize_includegraphics_paths(content)
    return content
