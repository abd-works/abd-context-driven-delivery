"""Ping the hook server. Stop extra daemons when more than one is running."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
_SCRIPTS = Path(__file__).resolve().parent
for entry in (str(_REPO), str(_SCRIPTS)):
    if entry not in sys.path:
        sys.path.insert(0, entry)

from instances import HookPing

if __name__ == "__main__":
    raise SystemExit(HookPing().run())
