"""Load and expose format presets."""
from __future__ import annotations

import json
from pathlib import Path

from .schema import PresetConfig

_PRESETS_DIR = Path(__file__).resolve().parent
_PRESET_FILES = ["aries_em.json"]


def load_presets() -> dict[str, PresetConfig]:
    """Load all preset JSON files and return id -> PresetConfig."""
    out: dict[str, PresetConfig] = {}
    for name in _PRESET_FILES:
        path = _PRESETS_DIR / name
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            cfg = PresetConfig.model_validate(data)
            out[cfg.id] = cfg
    return out


PRESETS = load_presets()


def get_preset(preset_id: str) -> PresetConfig | None:
    """Return preset by id or None."""
    return PRESETS.get(preset_id)
