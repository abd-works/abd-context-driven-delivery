from __future__ import annotations

import tempfile
from pathlib import Path

from expects import equal, expect

from harness.apps.examples.lane_app_examples import seed_files_server
from harness.mcp.cdd_home import CddHome
from harness.mcp.examples.server_lanes_examples import seed_lanes
from harness.mcp.server_lanes import ServerLane, ServerLanes
from story_test import and_, given, scenario, story, then, when

# Epic: Register And Install Toolsets
# Sub-epic: Serve CDD Code In Lanes
# Map: ../../../../.context/story-map.md#e-serve-cdd-code-in-lanes
# Decision: ../../../../harness/mcp/.context/cdr/0003-two-lanes-main-stable-features-dev.md
# Requested 2026-11-16: both lanes register the same apps, so the stable lane's Files server held 8783 and a worktree
# chat could not start the feature's Files app; every dev-lane app answers on ports of its own, one offset away.

# Story: Serve Dev Lane Apps On Their Own Ports
# Actor: CDD Server (system)
with story("Serve Dev Lane Apps On Their Own Ports"):
    with scenario("Start the dev lane's Files app on a port of its own"):
        with given("the Files app's server seed_files_server, whose ports file gives it 8783, made by the dev lane"):
            dev_lane = seed_lanes(Path(tempfile.mkdtemp())).dev
            self.server = seed_files_server(dev_lane)
            self.server_lane_home = dev_lane.home.folder.as_posix()
        with when("a chat opening the Files app asks the server's ports"):
            # App.open -> AppServer.ports -> ServerLane.app_ports((8783,)) <- (9783,)
            self.ports = self.server.ports
        with then("the server answers on 9783, which no stable-lane app takes"):
            expect(self.ports).to(equal((9783,)))
        with and_("the command the chat starts it with names that port and the dev lane's home, so the app's calls reach the dev lane's server whatever environment starts it"):
            # AppServer.command <- [..., PORT_ARGUMENT, "9783", CDD_HOME_ARGUMENT, ServerLane.home.folder]
            expect(self.server.command).to(equal(["node", "--import", "tsx", "serve.ts", "--port", "9783", "--cdd-home", self.server_lane_home]))
    with scenario("Start the stable lane's Files app as before"):
        with given("the Files app's server seed_files_server made by the stable lane"):
            self.server = seed_files_server(seed_lanes(Path(tempfile.mkdtemp())).stable)
        with when("a chat opening the Files app asks the server's ports"):
            # App.open -> AppServer.ports -> ServerLane.app_ports((8783,)) <- (8783,)
            self.ports = self.server.ports
        with then("the server answers on 8783, the port its ports file gives it"):
            expect(self.ports).to(equal((8783,)))
        with and_("the command the chat starts it with names no port, so the server reads its ports file"):
            expect(self.server.command).to(equal(["node", "--import", "tsx", "serve.ts"]))
    with scenario("Know the dev lane from the home the server runs from"):
        with given("the dev lane's home, the folder DEV_LANE_FOLDER inside the stable lane's"):
            self.lanes = seed_lanes(Path(tempfile.mkdtemp()))
            self.home = CddHome(self.lanes.dev.home.folder)
        with when("the server running from that home asks which lane it serves"):
            # ServerLane.from_home(home) -> ServerLanes.from_serving(home) <- ServerLane dev
            self.lane = ServerLane.from_home(self.home)
        with then("it serves the dev lane"):
            expect(self.lane.name).to(equal(ServerLanes.DEV))
    with scenario("Know the stable lane from the home the server runs from"):
        with given("the stable lane's home"):
            self.home = CddHome(seed_lanes(Path(tempfile.mkdtemp())).stable.home.folder)
        with when("the server running from that home asks which lane it serves"):
            # ServerLane.from_home(home) -> ServerLanes.from_serving(home) <- ServerLane stable
            self.lane = ServerLane.from_home(self.home)
        with then("it serves the stable lane"):
            expect(self.lane.name).to(equal(ServerLanes.STABLE))
