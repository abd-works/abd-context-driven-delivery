"""Hook process helpers that race threads on purpose. Heavy: four hook commands arrive together on threads, and the
first one's daemon takes the start-up poll to answer."""
import os
import sys
import tempfile
import threading
import time
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import equal, expect
from mamba import description, it


with description("hook process helpers"):

    with it("should start a single daemon when several hook commands arrive together"):
        from harness.hooks.hook_daemon import HookDaemon
        from harness.process.process import RunningProcess
        from harness.process.server_daemon import RunningServer

        calls: list[float] = []

        class _CountingDaemon(HookDaemon):
            def running(self):
                if calls and time.time() >= calls[0] + 0.4:
                    return RunningServer(RunningProcess(os.getpid()), self.repo, self.source_stamp)
                return None

            def spawn(self):
                calls.append(time.time())

        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            errors: list[BaseException] = []

            def arrive():
                try:
                    _CountingDaemon(repo).ensure()
                except BaseException as exc:
                    errors.append(exc)

            arrivals = [threading.Thread(target=arrive) for _ in range(4)]
            for arrival in arrivals:
                arrival.start()
            for arrival in arrivals:
                arrival.join(5)
        expect(errors).to(equal([]))
        expect(len(calls)).to(equal(1))
