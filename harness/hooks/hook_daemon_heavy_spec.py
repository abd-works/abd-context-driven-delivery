"""Hook daemons serving on real ports, and the hook command hook_daemon.py run as a subprocess. Heavy: starts servers and processes."""
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("tools", "cdd_guidance/practices", "cdd_guidance/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.modules.pop("tools", None)
sys.modules.pop("hooks", None)

from expects import be_false, be_none, be_true, equal, expect
from mamba import after, before, context, description, it

from harness.hooks.fixtures.older_layout_daemon import OlderLayoutDaemon
from harness.hooks.hook_daemon import HookDaemon
from harness.hooks.hook_server import HandlerCatalog, HookResult, HookServer
from harness.installation.repository_toolsets import RepositoryToolsets


with description("a hook daemon"):

    with it("should hold one daemon when several start for the same checkout"):
        from harness.hooks.hook_daemon import HookDaemon

        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            marker = HookDaemon(repo).address_file.path
            inner = HookServer(repo, HandlerCatalog([], repo))
            daemons = [
                threading.Thread(target=HookDaemon(repo).serve, args=(inner,), daemon=True) for _ in range(4)
            ]
            for daemon in daemons:
                daemon.start()
            deadline = time.time() + 5
            while not marker.is_file() and time.time() < deadline:
                time.sleep(0.05)
            for daemon in daemons:
                daemon.join(1)
            expect(len([d for d in daemons if d.is_alive()])).to(equal(1))
            expect(json.loads(marker.read_text(encoding="utf-8"))["port"]).to(equal(HookDaemon(repo).port))

    with it("should stay reachable while a dispatch is still in flight"):
        from harness.hooks.hook_daemon import HookDaemon, HookDaemonAddress

        class _BlockingServer:
            def __init__(self) -> None:
                self.started = threading.Event()
                self.release = threading.Event()

            def handle_stdin(self, raw: bytes) -> HookResult:
                self.started.set()
                self.release.wait(10)
                return HookResult()

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            daemon = HookDaemon(root)
            blocking = _BlockingServer()
            try:
                threading.Thread(target=daemon.serve, args=(blocking,), daemon=True).start()
                deadline = time.time() + 5
                while not daemon.address_file.path.is_file() and time.time() < deadline:
                    time.sleep(0.05)
                state = json.loads(daemon.address_file.path.read_text(encoding="utf-8"))
                threading.Thread(
                    target=HookDaemonAddress(state["host"], state["port"]).handle_stdin,
                    args=(b'{"hook_event_name":"stop"}',),
                    daemon=True,
                ).start()
                expect(blocking.started.wait(5)).to(equal(True))
                expect(daemon.is_running()).to(equal(True))
            finally:
                blocking.release.set()


with description("the IDE hook command, hook_daemon.py"):

    with it("should dispatch sessionStart over stdin without an import error"):
        proc = subprocess.run(
            [
                sys.executable,
                "-u",
                str(_REPO_ROOT / "harness" / "hooks" / "hook_daemon.py"),
            ],
            input=b'{"hook_event_name":"sessionStart"}',
            cwd=str(_REPO_ROOT),
            capture_output=True,
            env={
                **os.environ,
                "PYTHONPATH": RepositoryToolsets(_REPO_ROOT).pythonpath(),
                "PYTHONPYCACHEPREFIX": RepositoryToolsets(_REPO_ROOT).pycache_prefix(),
            },
        )
        expect(proc.returncode).to(equal(0))
        expect(json.loads(proc.stdout.decode("utf-8"))["permission"]).to(equal("allow"))

with description("a checkout whose hook port the daemon of the older layout holds") as self:

    with before.each:
        from harness.hooks.fixtures.older_layout_daemon import OlderLayoutDaemon
        from harness.hooks.hook_daemon import HookDaemon

        self.repo = Path(tempfile.mkdtemp(prefix="older-hook-daemon-"))
        self.daemon = HookDaemon(self.repo)
        self.older = OlderLayoutDaemon(self.repo, self.daemon.port).start()
        # The started daemon imports harness from this checkout, whatever folder it runs in.
        self.pythonpath = os.environ.get("PYTHONPATH", "")
        os.environ["PYTHONPATH"] = os.pathsep.join(part for part in (str(_REPO_ROOT), self.pythonpath) if part)

    with after.each:
        self.daemon.stop()
        self.older.kill()
        os.environ["PYTHONPATH"] = self.pythonpath

    with it("should answer the next hook command from a daemon on the current code"):
        address = self.daemon.ensure()
        expect(address.stamp).to(equal(self.daemon.source_stamp))

    with it("should stop the older daemon"):
        self.daemon.ensure()
        expect(self.older.ended()).to(equal(True))

    with it("should stop the daemon when the checkout closes"):
        address = self.daemon.ensure()
        self.daemon.stop()
        expect(address.answers()).to(equal(False))


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

    with context("with its port held by the daemon the older layout started"):

        with before.each:
            self.older = OlderLayoutDaemon(self.repo, self.port).start()

        with after.each:
            self.older.kill()

        with it("should claim the port"):
            self.listener = self.daemon.claim_port()
            expect(self.listener is not None).to(be_true)

        with it("should stop the older daemon"):
            self.listener = self.daemon.claim_port()
            expect(self.older.ended()).to(be_true)

        with it("should remove the older layout's address file"):
            self.listener = self.daemon.claim_port()
            expect(self.older.published_file.is_file()).to(be_false)

    with context("with its port held by the daemon the older layout started, with no address file left"):

        with before.each:
            self.older = OlderLayoutDaemon(self.repo, self.port).start(publishes=False)

        with after.each:
            self.older.kill()

        with it("should stop the process that holds the port"):
            self.listener = self.daemon.claim_port()
            expect(self.older.ended()).to(be_true)

    with context("whose checkout closes"):

        with before.each:
            self.older = OlderLayoutDaemon(self.repo, self.port).start()

        with after.each:
            self.older.kill()

        with it("should stop the daemon serving the checkout"):
            self.daemon.stop()
            expect(self.older.ended()).to(be_true)

        with it("should leave the port free"):
            self.daemon.stop()
            self.older.ended()
            expect(HookDaemon(self.repo, port=self.port).live_address()).to(be_none)
