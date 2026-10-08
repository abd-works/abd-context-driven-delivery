"""Ping the CodeQL graph Vite app. The reply includes url and port.

Stops extra Vite processes when more than one is running.
"""
from __future__ import annotations

import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from instances import HttpPing, codeql_app

if __name__ == "__main__":
    raise SystemExit(HttpPing().run(codeql_app))
