"""RQ job: run Word -> LaTeX conversion in background."""
from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

from converter import convert_upload_to_tex, postprocess_tex, compile_tex_to_pdf

OUTPUT_PDF_DIR = Path(os.environ.get("OUTPUT_PDF_DIR", "/tmp/word2latex_pdfs"))


def run_convert_task(docx_bytes: bytes, preset_id: str, compile_pdf: bool = False) -> dict[str, Any]:
    """
    Execute conversion. Called by RQ worker. Returns dict for GET /jobs/:id.
    If compile_pdf=True and TeX is available, compiles to PDF and stores under OUTPUT_PDF_DIR.
    """
    job_id = None
    try:
        import rq
        job = rq.get_current_job()
        if job:
            job_id = job.id
    except Exception:
        pass

    try:
        raw_tex = convert_upload_to_tex(docx_bytes)
        tex_content = postprocess_tex(raw_tex, preset_id)
        result: dict[str, Any] = {
            "status": "done",
            "tex_content": tex_content,
            "error": None,
            "pdf_available": False,
        }

        if compile_pdf and job_id:
            with tempfile.TemporaryDirectory(prefix="word2latex_") as tmp:
                pdf_path, log = compile_tex_to_pdf(tex_content, Path(tmp))
                if pdf_path and pdf_path.exists():
                    OUTPUT_PDF_DIR.mkdir(parents=True, exist_ok=True)
                    dest = OUTPUT_PDF_DIR / f"{job_id}.pdf"
                    shutil.copy2(pdf_path, dest)
                    result["pdf_available"] = True
                else:
                    result["compile_log"] = log[:2000] if log else "Compilation failed."

        return result
    except Exception as e:
        return {
            "status": "failed",
            "tex_content": None,
            "error": str(e),
            "pdf_available": False,
        }
