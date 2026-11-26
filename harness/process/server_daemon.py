"""ServerDaemon - a long-running server of this computer, started on demand, found by asking it, and stopped."""
from __future__ import annotations

import os
import time
from abc import ABC, abstractmethod
from pathlib import Path

from harness.process.capped_log_file import CappedLogFile
from harness.process.lock_file import LockFile
from harness.process.process import BackgroundStart, ExclusivePort, RunningProcess

# How often a start asks the server again while it waits for it to answer.
_POLL_SECONDS = 0.2
# How many of the log's last lines a server that did not start reports.
_LOG_LINES_SHOWN = 20


class RunningServer:
    """A long-running server that answered when asked: its process, the folder it serves code from (none for a server
    of an older layout, which does not say), the stamp of the code it loaded (empty when it keeps none), and the
    projects its chats have worked on (the cdd server's only)."""

    def __init__(self, process: RunningProcess, serves: Path | None = None, code: str = "", projects: tuple[str, ...] = ()) -> None:
        self.process = process
        self.serves = serves
        self.code = code
        self.projects = projects

    @property
    def pid(self) -> int:
        return self.process.pid

    def is_serving(self, folder: Path) -> bool:
        """Whether the server says it serves folder; a server of an older layout says nothing."""
        return self.serves is not None and os.path.normcase(str(self.serves)) == os.path.normcase(str(folder))


class ServerDidNotStart(Exception):
    """A server was started but did not answer within its wait."""

    def __init__(self, daemon: ServerDaemon, seconds: float, log_tail: str) -> None:
        super().__init__(f"{daemon} did not answer within {seconds:g} seconds. Last log lines:\n{log_tail}")
        self.daemon = daemon


class ServerDaemon(ABC):
    """A server that keeps running past the command that started it, on the one port it may hold, with its output in a
    capped log file, such as the hook daemon of a checkout and the one cdd server. `running()` asks it who it is;
    `ensure()` starts it when none answers, one start at a time (a start lock beside its log lets one caller start it
    while the others wait for that start), stopping first a process that holds the port without answering, and waits
    until it answers or raises *ServerDidNotStart* with the log's last
    lines; `stop()` stops the process that answers, or, when none does, the one holding the port, since a server that
    holds its port without answering keeps every new one from claiming it. Each kind says how it is asked, run, and
    named."""

    # How long a start waits for the server to answer, and a stop for its process to end.
    START_SECONDS: float = 60
    STOP_SECONDS: float = 10

    def __init__(self, port: ExclusivePort, log: CappedLogFile) -> None:
        self._port = port
        self.log = log

    @property
    def port(self) -> int:
        return self._port.port

    @abstractmethod
    def running(self) -> RunningServer | None:
        """The server answering on the port as this daemon's; none when none does."""

    def is_running(self) -> bool:
        return self.running() is not None

    def ensure(self) -> RunningServer:
        """The running server, starting it first when none answers."""
        running = self.running()
        if running is not None:
            return running
        with LockFile(self.log.path.with_name("start.lock"), self.START_SECONDS).held():
            return self.running() or self._started()

    def stop(self) -> None:
        """Stop the server's process; raises *ProcessNotStopped* when it keeps running."""
        process = self._process_to_stop()
        if process is not None:
            process.stop(self.STOP_SECONDS)

    def restart(self) -> RunningServer:
        """Stop the running server and start it again."""
        self.stop()
        return self.ensure()

    def spawn(self) -> RunningProcess:
        """Start the server in the background, past the caller, with its output in its log; a log that reached its size
        starts again, its earlier output kept in its previous file."""
        self.log.path.parent.mkdir(parents=True, exist_ok=True)
        self.log.roll_when_full()
        with open(self.log.path, "a", encoding="utf-8") as output:
            return BackgroundStart(output).run(self._command(), self._folder(), self._environment())

    @abstractmethod
    def _command(self) -> list[str]:
        """The command that runs the server."""

    @abstractmethod
    def _folder(self) -> Path:
        """The folder the server runs in."""

    @abstractmethod
    def _environment(self) -> dict[str, str]:
        """The environment the server runs with."""

    def _process_to_stop(self) -> RunningProcess | None:
        """The process answering as the server, else the one holding its port; none when neither is there."""
        running = self.running()
        return running.process if running is not None else self._port.holder()

    def _started(self) -> RunningServer:
        """Start the server, holding the start lock, once nothing answers: a process still holding the port without
        answering, such as a hung server, is stopped first, since the new server could never claim the port past it."""
        holder = self._port.holder()
        if holder is not None:
            holder.stop(self.STOP_SECONDS)
        self.spawn()
        return self._wait_until_answering()

    def _wait_until_answering(self) -> RunningServer:
        deadline = time.monotonic() + self.START_SECONDS
        while time.monotonic() < deadline:
            running = self.running()
            if running is not None:
                return running
            time.sleep(_POLL_SECONDS)
        raise ServerDidNotStart(self, self.START_SECONDS, self.log.last_lines(_LOG_LINES_SHOWN))
