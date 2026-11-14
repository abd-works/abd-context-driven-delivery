"""The Files app, made once and registered here: the file viewer as an app of its own, with its own server on its own
port, which reads only the files its link names and never the board."""
from __future__ import annotations

from pathlib import Path

from harness.diagnostics.app import LANGUAGE_ADAPTER_FOLDER, App, AppServer
from harness.installation.app_ports import AppPorts

FILES_APP_FOLDER = Path(__file__).resolve().parent / "app"
# The page shows each file in the graph explorer's source view, which it builds from the Graph app's folder, so a
# change there builds the Files app again.
SOURCE_VIEW_FOLDER = Path(__file__).resolve().parents[3] / "harness" / "graph" / "app" / "source"

# The Files app's ports, as ``app/ports.json`` gives them: ``files``, the ports its server listens on. Its server reads
# the same file, so the port is written once.
FILES_APP_PORTS = AppPorts(FILES_APP_FOLDER / "ports.json")

FILES_SERVER = AppServer(FILES_APP_FOLDER, "serve.ts", FILES_APP_PORTS.of("files"))
FILES_APP = App("Files", FILES_APP_FOLDER, FILES_SERVER, imports=(LANGUAGE_ADAPTER_FOLDER, SOURCE_VIEW_FOLDER)).register()
