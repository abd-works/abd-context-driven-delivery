"""Import toolsets that declare ``@hook`` handlers so the registry is populated."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]

for _cat in ("primitives", "utilities", "primitives/hooks"):
    _path = str(_REPO_ROOT / _cat)
    if _path not in sys.path:
        sys.path.insert(0, _path)

_BOOTSTRAP_MODULES = (
    "workspace.workspace",
)


def load() -> None:
    for module_name in _BOOTSTRAP_MODULES:
        importlib.import_module(module_name)
