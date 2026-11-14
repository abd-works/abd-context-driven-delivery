"""The Graph app's start runs both its servers in one process, so ending that process, as the chat that opened the app
does when it ends, stops both: on Windows, ending a process ends none of its child processes."""

import json
import socket
import subprocess
import time
from pathlib import Path

from expects import be_false, be_true, expect
from mamba import after, before, description, it

_APP = Path(__file__).resolve().parent / "app"
_PORTS = json.loads((_APP / "ports.json").read_text(encoding="utf-8"))
_START_SECONDS = 60
_CHECK_SECONDS = 0.5


def _answers(port: int) -> bool:
    with socket.socket() as probe:
        probe.settimeout(0.05)
        return probe.connect_ex(("127.0.0.1", port)) == 0


def _page_port_answering(before_start: set[int]) -> int | None:
    """The first of the page's ports answering that was not answering before the start: another copy of the app, such
    as the person's own, may already hold the first."""
    return next((port for port in _PORTS["app"] if port not in before_start and _answers(port)), None)


# A checkout where npm install has not run, such as a fresh worktree, has no tsx to start the app with.
_NOT_INSTALLED = f"the Graph app is not installed in this checkout: run npm install in {_APP}"


with description("the Graph app's start"):
    with before.all:
        if not (_APP / "node_modules" / "tsx").is_dir():
            raise AssertionError(_NOT_INSTALLED)
        self.busy = {port for port in _PORTS["app"] if _answers(port)}
        self.web = _PORTS["web"][0]
        self.web_was_busy = _answers(self.web)
        self.server = subprocess.Popen(["node", "--import", "tsx", "start.ts"], cwd=_APP, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=False)
        deadline = time.monotonic() + _START_SECONDS
        while time.monotonic() < deadline and (_page_port_answering(self.busy) is None or not _answers(self.web)):
            time.sleep(_CHECK_SECONDS)
        self.page = _page_port_answering(self.busy)
        self.started = self.page is not None and _answers(self.web)
        self.server.kill()
        self.server.wait()
        time.sleep(_CHECK_SECONDS)

    with after.all:
        if getattr(self, "server", None) is not None and self.server.poll() is None:
            self.server.kill()

    with it("should answer on a page port and the web port from its one process"):
        expect(self.started).to(be_true)

    with it("should stop answering on the page port once that process is ended"):
        expect(_answers(self.page) if self.page is not None else True).to(be_false)

    with it("should stop answering on the web port once that process is ended"):
        expect(self.web_was_busy or _answers(self.web)).to(be_false)
