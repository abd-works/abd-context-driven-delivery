"""Ping the CodeQL graph web server. The reply includes url and port.

Stops extra server.ts processes when more than one is running.
"""
from __future__ import annotations

import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from instances import HttpPing, codeql_web

if __name__ == "__main__":
    raise SystemExit(HttpPing().run(codeql_web))
