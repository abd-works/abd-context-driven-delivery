"""An app's server restarted after an install: a server keeps the code it started with, so an install restarts each
running one on the code it just wrote. These start real node servers on free ports."""
import shutil
import socket
import subprocess
import tempfile
import time
from urllib.request import urlopen
from pathlib import Path

from expects import be_false, be_true, equal, expect
from mamba import after, before, context, description, it

from harness.diagnostics.app import AppServer, _process_listening_on, _stop_process

STARTED_WITHIN_SECONDS = 15


def free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


def page_on(port: int) -> str:
    with urlopen(f"http://127.0.0.1:{port}/", timeout=5) as answer:
        return answer.read().decode()


def answering(server: AppServer) -> None:
    deadline = time.monotonic() + STARTED_WITHIN_SECONDS
    while server.port is None and time.monotonic() < deadline:
        time.sleep(0.1)


with description("an app's server") as self:
    with before.each:
        self.folder = Path(tempfile.mkdtemp())
        self.port = free_port()
        # The server reads the version it serves once, when it starts, as a built server keeps the code it started with.
        (self.folder / "serve.js").write_text(
            "const version = require('fs').readFileSync('version.txt', 'utf8')\n"
            f"require('http').createServer((_request, response) => response.end(version)).listen({self.port}, '127.0.0.1')\n",
            encoding="utf-8",
        )
        (self.folder / "version.txt").write_text("old", encoding="utf-8")
        self.server = AppServer(self.folder, "serve.js", (self.port,))

    with after.each:
        listening = _process_listening_on(self.port) if self.server.port is not None else None
        if listening is not None:
            _stop_process(listening)
        shutil.rmtree(self.folder, ignore_errors=True)

    with context("that is not running"):
        with it("should not restart, leaving it for the chat that opens its app"):
            expect(self.server.restart()).to(be_false)

    with context("that is running on the code it started with, after an install wrote new code"):
        with before.each:
            self.first = subprocess.Popen(["node", "serve.js"], cwd=self.folder, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            answering(self.server)
            (self.folder / "version.txt").write_text("new", encoding="utf-8")

        with after.each:
            self.first.kill()

        with it("should serve the old code until it is restarted"):
            expect(page_on(self.port)).to(equal("old"))

        with it("should answer that it restarted"):
            expect(self.server.restart()).to(be_true)

        with it("should serve the new code once restarted"):
            self.server.restart()
            expect(page_on(self.port)).to(equal("new"))

        with it("should stop the process that served the old code"):
            self.server.restart()
            expect(self.first.wait(timeout=5) is not None).to(be_true)
