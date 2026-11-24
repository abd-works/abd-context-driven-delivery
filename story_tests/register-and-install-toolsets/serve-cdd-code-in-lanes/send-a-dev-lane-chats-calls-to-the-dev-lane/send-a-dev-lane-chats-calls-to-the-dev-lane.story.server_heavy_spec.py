"""Send A Dev-Lane Chat's Calls To The Dev Lane over real HTTP: a dev lane's cdd server listening on a port of its own,
and the stable lane's host handing it a ticket worktree's call. The story test reaches the dev lane's route in
process; this spec checks the same answer crosses a real connection."""

import shutil
import socket
import sys
import tempfile
import threading
import time
from pathlib import Path

_REPO = Path(__file__).resolve().parents[4]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from expects import contain, equal, expect, raise_error
from mamba import after, before, description, it

from harness.mcp.examples import server_lanes_examples as examples
from harness.mcp.cdd_home import CddHome
from harness.mcp.mcp_address import DEV_LANE_FOLDER, McpAddress
from harness.mcp.mcp_daemon import McpDaemon
from harness.mcp.mcp_server import HttpEndpoints
from harness.mcp.server_lanes import LaneCallFailed, ServerLanes

_START_SECONDS = 20


def _listening_dev_lane(home: CddHome, worktree: Path) -> McpAddress:
    """A dev lane's host serving the ledger toolset for worktree's chats, on a free loopback port of its own."""
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind((McpAddress.HOST, 0))
    listener.listen()
    address = McpAddress(listener.getsockname()[1])
    daemon = McpDaemon(home, address)
    threading.Thread(target=HttpEndpoints(examples.seed_host(worktree)).serve, args=(daemon, listener), daemon=True).start()
    deadline = time.time() + _START_SECONDS
    while address.ping_answer(1) is None and time.time() < deadline:
        time.sleep(0.1)
    return address


with description("Send A Dev-Lane Chat's Calls To The Dev Lane") as self:
    with before.all:
        self.root = Path(tempfile.mkdtemp())
        self.worktree = examples.seed_ticket_worktree(self.root, examples.seed_main_checkout(self.root / "dev-side"))
        dev_home = CddHome(self.root / ".cdd" / DEV_LANE_FOLDER)
        dev_address = _listening_dev_lane(dev_home, self.worktree)
        self.lanes = ServerLanes(CddHome(self.root / ".cdd"), McpAddress(examples.STABLE_PORT), dev_address)
        self.lanes.dev.home.serve_from(self.worktree)
        self.stable_host = examples.seed_host(examples.seed_main_checkout(self.root), self.lanes)

    with after.all:
        shutil.rmtree(self.root, ignore_errors=True)

    with it("should answer a ticket worktree's call on the dev lane's server, over its port"):
        expect(self.stable_host.dispatch(examples.LEDGER_FOLDER_TOOL, {}, self.worktree)).to(equal(str(self.worktree)))

    with it("should show the chat the failure the dev lane met"):
        calling = lambda: self.stable_host.dispatch(examples.LOCKED_LEDGER_TOOL, {}, self.worktree)
        expect(calling).to(raise_error(LaneCallFailed, contain(examples.LEDGER_IS_LOCKED)))
