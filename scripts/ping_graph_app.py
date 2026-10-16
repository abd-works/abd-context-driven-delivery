"""Ping the graph explorer. The reply includes url and port.

Stops extra Vite processes when more than one is running.
"""
from __future__ import annotations

import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from instances import GRAPH_APP_PORTS, HttpPing, graph_app

if __name__ == "__main__":
    raise SystemExit(
        HttpPing().run(graph_app, preferred_ports=GRAPH_APP_PORTS, expect_service="graph_app")
    )
