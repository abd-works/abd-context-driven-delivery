"""A throwaway cdd server, such as a spec run's on a port of its own, ends with the process it belongs to, so a run that
is killed or hangs leaves no server behind. These start a real cdd server on a free port."""
import os
import subprocess
import sys
import time

from expects import be_false, be_none, be_true, expect
from mamba import after, before, context, description, it

from harness.mcp.mcp_daemon import SERVER_OWNER_ENV
from harness.mcp.spec_support import SpecServer

# A process that lives until it is ended, to own the server.
OWNER_COMMAND = [sys.executable, "-c", "import time; time.sleep(600)"]
ENDED_WITHIN_SECONDS = 15


def ended_within(server: SpecServer, seconds: float) -> bool:
    deadline = time.monotonic() + seconds
    while server.daemon.running() is not None:
        if time.monotonic() > deadline:
            return False
        time.sleep(0.25)
    return True


def start_owned_server(spec) -> None:
    """A cdd server started on a port of its own, owned by a process that lives until it is ended."""
    spec.owner = subprocess.Popen(OWNER_COMMAND)
    spec.server = SpecServer(("tools.echo.echo:Echo",))
    spec.server.install()
    os.environ[SERVER_OWNER_ENV] = str(spec.owner.pid)
    spec.server.daemon.ensure()


def stop_owned_server(spec) -> None:
    spec.owner.kill()
    spec.server.stop()


# A server takes seconds to start and to end, so each context starts one, once, before its examples.
with description("a throwaway cdd server") as self:
    with context("whose owning process still runs"):
        with before.all:
            start_owned_server(self)

        with after.all:
            stop_owned_server(self)

        with it("should keep answering"):
            time.sleep(3)
            expect(self.server.daemon.running()).not_to(be_none)

    with context("whose owning process has ended"):
        with before.all:
            start_owned_server(self)
            self.owner.kill()
            self.owner.wait()
            self.ended = ended_within(self.server, ENDED_WITHIN_SECONDS)

        with after.all:
            stop_owned_server(self)

        with it("should end, freeing its port"):
            expect(self.ended).to(be_true)

        with it("should withdraw the address it published"):
            expect(self.server.home.state_path.exists()).to(be_false)
