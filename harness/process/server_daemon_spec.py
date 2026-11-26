"""A long-running server started on demand: a start when one already answers starts nothing, a start that never answers
reports the log's last lines, and a stop ends the process that answers, else the one holding the port. The server is a
double that starts no process and opens no socket; each daemon's heavy spec runs the real one."""
import os
import shutil
import tempfile
from pathlib import Path

from expects import be_none, contain, equal, expect, raise_error
from mamba import after, before, context, description, it

from harness.process.capped_log_file import CappedLogFile
from harness.process.process import RunningProcess
from harness.process.server_daemon import RunningServer, ServerDaemon, ServerDidNotStart


class _RecordingProcess(RunningProcess):
    """A process that records that it was asked to stop."""

    def __init__(self) -> None:
        super().__init__(0)
        self.stopped = False

    def stop(self, wait_seconds: float) -> None:
        self.stopped = True


class _Port:
    """The server's port, naming one holder."""

    def __init__(self, holder: RunningProcess | None) -> None:
        self.port = 47998
        self._holder = holder

    def holder(self) -> RunningProcess | None:
        return self._holder


class _Daemon(ServerDaemon):
    """A server that answers once it was started, when it starts at all; one that never does is waited for not at all."""

    def __init__(self, log: CappedLogFile, port: _Port, comes_up: bool) -> None:
        super().__init__(port, log)
        self.answering: RunningServer | None = None
        self.spawned = 0
        self._comes_up = comes_up
        self.START_SECONDS = 1 if comes_up else 0

    def __str__(self) -> str:
        return "the double server"

    def running(self) -> RunningServer | None:
        return self.answering

    def spawn(self) -> RunningProcess:
        self.spawned += 1
        if self._comes_up:
            self.answering = RunningServer(_RecordingProcess(), Path("served"))
        return RunningProcess(0)

    def _command(self) -> list[str]:
        return []

    def _folder(self) -> Path:
        return Path(".")

    def _environment(self) -> dict[str, str]:
        return dict(os.environ)


with description("a long-running server") as self:
    with before.each:
        self.folder = Path(tempfile.mkdtemp(prefix="server-daemon-"))
        self.log = CappedLogFile(self.folder / "server.log")
        self.holder = _RecordingProcess()

    with after.each:
        shutil.rmtree(self.folder, ignore_errors=True)

    with context("that is not running"):
        with before.each:
            self.daemon = _Daemon(self.log, _Port(None), comes_up=True)

        with it("should start it once when ensured"):
            self.daemon.ensure()
            expect(self.daemon.spawned).to(equal(1))

        with it("should answer the server that came up"):
            expect(self.daemon.ensure().serves).to(equal(Path("served")))

        with it("should stop nothing"):
            self.daemon.stop()
            expect(self.holder.stopped).to(equal(False))

    with context("that is already running"):
        with before.each:
            self.daemon = _Daemon(self.log, _Port(None), comes_up=True)
            self.daemon.answering = RunningServer(self.holder, Path("served"))

        with it("should start nothing when ensured"):
            self.daemon.ensure()
            expect(self.daemon.spawned).to(equal(0))

        with it("should stop the process that answers"):
            self.daemon.stop()
            expect(self.holder.stopped).to(equal(True))

    with context("that holds its port without answering"):
        with before.each:
            self.daemon = _Daemon(self.log, _Port(self.holder), comes_up=True)

        with it("should stop the process holding the port"):
            self.daemon.stop()
            expect(self.holder.stopped).to(equal(True))

        # A hung server keeps every new one from claiming the port, so a start waited its whole minute and failed.
        with it("should stop the process holding the port when ensured"):
            self.daemon.ensure()
            expect(self.holder.stopped).to(equal(True))

        with it("should start the server once the holder is stopped"):
            self.daemon.ensure()
            expect(self.daemon.spawned).to(equal(1))

    with context("that never answers once started"):
        with before.each:
            self.log.path.write_text("first line\nlast line\n", encoding="utf-8")
            self.daemon = _Daemon(self.log, _Port(None), comes_up=False)

        with it("should say it did not start, with its log's last lines"):
            expect(self.daemon.ensure).to(raise_error(ServerDidNotStart, contain("the double server", "last line")))


with description("a running server") as self:
    with it("should say it serves the folder it names"):
        expect(RunningServer(RunningProcess(0), Path("C:/dev/repo")).is_serving(Path("C:/dev/repo"))).to(equal(True))

    with it("should say nothing of a folder when it names none, as a server of an older layout does"):
        expect(RunningServer(RunningProcess(0)).serves).to(be_none)
