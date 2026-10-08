"""Kill the hook daemon, then start one."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
_SCRIPTS = Path(__file__).resolve().parent
for entry in (str(_REPO), str(_SCRIPTS)):
    if entry not in sys.path:
        sys.path.insert(0, entry)

from start import ServiceStart

if __name__ == "__main__":
    raise SystemExit(ServiceStart().hook())
