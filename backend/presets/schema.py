"""Preset configuration schema for journal/format specifications."""
from __future__ import annotations

from pydantic import BaseModel, Field


class PresetConfig(BaseModel):
    """Schema for a single format preset (e.g. Aries EM)."""

    id: str = Field(..., description="Preset identifier")
    name: str = Field(..., description="Display name")
    documentclass: str = Field(default="article", description="LaTeX document class")
    documentclass_options: list[str] = Field(default_factory=list, description="Options for \\documentclass")
    packages: list[str] = Field(default_factory=lambda: ["graphicx", "amsmath", "hyperref"])
    bibliography_style: str | None = Field(default=None, description="e.g. plain or spmpsci")
    use_biber: bool = Field(default=False, description="Use Biber instead of BibTeX")
    use_xelatex: bool = Field(default=False, description="Add %!TEX TS-program = xelatex")
    image_format: str = Field(default="png", description="Preferred image extension for \\includegraphics")
    flat_zip: bool = Field(default=True, description="Zip must have no subfolders (EM requirement)")
    description: str | None = Field(default=None)
