"""Ping the graph web server. The reply includes url and port.

Stops extra server.ts processes when more than one is running.
"""
from __future__ import annotations

import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from instances import GRAPH_WEB, HttpPing  # noqa: I001 - instances puts the checkout on the import path

if __name__ == "__main__":
    raise SystemExit(HttpPing().run(GRAPH_WEB))
