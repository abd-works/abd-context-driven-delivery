"""An app's ports, read from the one ports.json its servers also read."""
import json
import tempfile
from pathlib import Path

from expects import equal, expect
from mamba import context, description, it

from harness.installation.app_ports import AppPorts


with description("an app's ports"):
    # The graph app and the session board each keep their ports in one ports.json their own servers read.
    with context("read from a ports file that names two servers"):
        with it("should give each server its ports in the order it tries them"):
            file = Path(tempfile.mkdtemp(prefix="app-ports-")) / "ports.json"
            file.write_text(json.dumps({"app": [5173, 5174], "web": [3000]}), encoding="utf-8")
            ports = AppPorts(file)
            expect((ports.of("app"), ports.of("web"))).to(equal(((5173, 5174), (3000,))))
