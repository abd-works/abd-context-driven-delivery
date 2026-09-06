"""Hook deploy metadata — re-export from ``dispatch``."""

import sys
from pathlib import Path

_root = Path(__file__).resolve().parents[2]
for _cat in ("primitives", "utilities", "primitives/hooks"):
    _p = str(_root / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from hooks.dispatch import (
    DISPATCH_SCRIPT,
    HookBinding,
    deploy_dispatch,
    hook_skill_sources,
)

__all__ = [
    "DISPATCH_SCRIPT",
    "HookBinding",
    "deploy_dispatch",
    "hook_skill_sources",
]
