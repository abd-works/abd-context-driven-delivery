"""The ports the graph explorer app answers on, read from the one file its servers also read."""
from __future__ import annotations

from pathlib import Path

from harness.installation.app_ports import AppPorts

# The graph explorer app's ports, as ``app/ports.json`` gives them: ``app``, the ports its Vite server tries in turn, and
# ``web``, the port of its web server. The Vite config, the web server, the server health report, and the instance
# scripts all read this one file, so the ports are written once; read once here, when this module is imported.
GRAPH_APP_PORTS = AppPorts(Path(__file__).resolve().parent / "app" / "ports.json")
