"""Put ``lib/``, this skill's ``scripts`` and **story-graph-ops** on ``sys.path``."""
from __future__ import annotations

import sys
from pathlib import Path

_skill_root = Path(__file__).resolve().parents[1]
_scripts = _skill_root / "scripts"
_skills_dir = _skill_root.parent
_package_root = _skills_dir.parent
_lib = _package_root / "lib"
_ops = _skills_dir / "story-graph-ops" / "scripts"

for _p in (_lib, _scripts, _ops):
    if _p.is_dir() and str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
