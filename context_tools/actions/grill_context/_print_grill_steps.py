"""Print grill_with_context prose parts (for agent BDD #26)."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities", "context_tools", "context_tools/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from primitives.actions.action import _ActionExpander
from grill_context.grill_context import GrillContext

body = _ActionExpander.instance().parse_body(
    GrillContext.grill_with_context, GrillContext()
)
print("\n".join(body.prose_parts))
