"""Hook daemons serving on real ports, and hook_server.py run as a subprocess. Heavy: starts servers and processes."""
import json
import os
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

from expects import equal, expect
from mamba import description, it

from harness.hooks.hook_server import HandlerCatalog, HookResult, HookServer
from harness.installation.installer import Installer


with description("a hook daemon"):

    with it("should hold one daemon when several start for the same checkout"):
        from harness.hooks.hook_daemon import HookDaemon

        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            marker = repo / ".cursor" / "hook-server.json"
            original_state_path = HookServer.state_path
            HookServer.state_path = classmethod(lambda cls, _repo: marker)
            try:
                inner = HookServer(repo, HandlerCatalog([], repo))
                daemons = [
                    threading.Thread(
                        target=HookDaemon().serve,
                        args=(repo,),
                        kwargs={"inner": inner},
                        daemon=True,
                    )
                    for _ in range(4)
                ]
                for daemon in daemons:
                    daemon.start()
                deadline = time.time() + 5
                while not marker.is_file() and time.time() < deadline:
                    time.sleep(0.05)
                for daemon in daemons:
                    daemon.join(1)
                expect(len([d for d in daemons if d.is_alive()])).to(equal(1))
                expect(json.loads(marker.read_text(encoding="utf-8"))["port"]).to(
                    equal(HookDaemon().repo_port(repo))
                )
            finally:
                HookServer.state_path = original_state_path

    with it("should stay reachable while a dispatch is still in flight"):
        from harness.hooks.hook_daemon import HookDaemon

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
            marker = root / ".cursor" / "hook-server.json"
            original_state_path = HookServer.state_path
            HookServer.state_path = classmethod(lambda cls, _repo: marker)
            blocking = _BlockingServer()
            try:
                threading.Thread(
                    target=HookDaemon().serve,
                    args=(root,),
                    kwargs={"inner": blocking},
                    daemon=True,
                ).start()
                deadline = time.time() + 5
                while not marker.is_file() and time.time() < deadline:
                    time.sleep(0.05)
                state = json.loads(marker.read_text(encoding="utf-8"))
                threading.Thread(
                    target=HookDaemon(state["host"], state["port"]).call_handle_stdin,
                    args=(b'{"hook_event_name":"stop"}',),
                    daemon=True,
                ).start()
                expect(blocking.started.wait(5)).to(equal(True))
                expect(HookDaemon().live_address(marker) is not None).to(equal(True))
            finally:
                blocking.release.set()
                HookServer.state_path = original_state_path


with description("the Cursor hook_server.py command"):

    with it("should dispatch sessionStart over stdin without an import error"):
        proc = subprocess.run(
            [
                sys.executable,
                "-u",
                str(_REPO_ROOT / "harness" / "hooks" / "hook_server.py"),
            ],
            input=b'{"hook_event_name":"sessionStart"}',
            cwd=str(_REPO_ROOT),
            capture_output=True,
            env={
                **os.environ,
                "PYTHONPATH": Installer(repo=_REPO_ROOT).pythonpath(),
                "PYTHONPYCACHEPREFIX": Installer(repo=_REPO_ROOT).pycache_prefix(),
            },
        )
        expect(proc.returncode).to(equal(0))
        expect(json.loads(proc.stdout.decode("utf-8"))["permission"]).to(equal("allow"))
