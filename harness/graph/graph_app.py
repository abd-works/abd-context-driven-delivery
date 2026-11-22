"""The Graph app: the ports its servers answer on, read from the one file they also read, and the app itself, which
harness/graph makes and registers with *App* when this module is imported."""
from __future__ import annotations

from pathlib import Path

from harness.apps.app import App, AppPackage, AppPage, AppServer, NodeScript
from harness.installation.app_ports import AppPorts

# The graph explorer app's ports, as ``app/ports.json`` gives them: ``app``, the ports its Vite server tries in turn, and
# ``web``, the port of its web server. The Vite config, the web server, the server health report, and the instance
# scripts all read this one file, so the ports are written once; read once here, when this module is imported.
GRAPH_APP_PORTS = AppPorts(Path(__file__).resolve().parent / "app" / "ports.json")

_FOLDER = GRAPH_APP_PORTS.file.path.parent
GRAPH_APP = App("Graph", AppPackage(_FOLDER), AppPage(AppServer(NodeScript(_FOLDER, "start.ts"), GRAPH_APP_PORTS.of("app")))).register()
