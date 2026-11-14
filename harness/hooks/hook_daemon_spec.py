"""A checkout's hook daemon finding its port held: by this checkout's daemon on the current code, or by a process that is
no hook daemon. The daemon the older layout started, and the daemon stopping when its checkout closes, are in
hook_daemon_heavy_spec.py: each starts a daemon process."""
import shutil
import socket
import sys
import tempfile
import threading
import time
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import be_false, be_none, be_true, equal, expect, raise_error
from mamba import after, before, context, description, it

from harness.hooks.hook_daemon import HookDaemon, HookPortTaken
from harness.hooks.hook_server import HandlerCatalog, HookServer

def _free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


with description("a checkout's hook daemon") as self:

    with before.each:
        self.repo = Path(tempfile.mkdtemp(prefix="hook-daemon-"))
        self.port = _free_port()
        self.daemon = HookDaemon(self.repo, port=self.port)
        self.listener = None

    with after.each:
        if self.listener is not None:
            self.listener.close()
        shutil.rmtree(self.repo, ignore_errors=True)

    with context("with its port held by a process that answers no hook ping"):

        with before.each:
            self.listener = socket.socket()
            self.listener.bind(("127.0.0.1", self.port))
            self.listener.listen()
            self.closing = threading.Thread(target=self._close_every_caller, daemon=True)
            self.closing.start()

        def _close_every_caller(self):
            while True:
                try:
                    conn, _ = self.listener.accept()
                except OSError:
                    return
                conn.close()

        with it("should refuse to serve, naming the port"):
            expect(lambda: self.daemon.claim_port()).to(raise_error(HookPortTaken))

    with context("with its port held by this checkout's daemon on the current code"):

        with before.each:
            self.serving = threading.Thread(
                target=self.daemon.serve, args=(HookServer(self.repo, HandlerCatalog([], self.repo)),), daemon=True
            )
            self.serving.start()
            deadline = time.time() + 5
            while not self.daemon.is_running() and time.time() < deadline:
                time.sleep(0.05)

        with it("should leave the port to that daemon"):
            expect(HookDaemon(self.repo, port=self.port).claim_port()).to(be_none)
