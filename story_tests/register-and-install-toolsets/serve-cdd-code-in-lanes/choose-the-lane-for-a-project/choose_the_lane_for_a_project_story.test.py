from __future__ import annotations

import tempfile
from pathlib import Path

from expects import equal, expect

from harness.mcp.server_lanes import ServerLanes
from harness.mcp.examples.server_lanes_examples import seed_folder_outside_any_checkout, seed_lanes, seed_main_checkout, seed_ticket_worktree
from story_test import given, scenario, story, then, when

# Epic: Register And Install Toolsets
# Sub-epic: Serve CDD Code In Lanes
# Map: ../../../../.context/story-map.md#e-serve-cdd-code-in-lanes
# Decision: ../../../../harness/mcp/.context/cdr/0003-two-lanes-main-stable-features-dev.md
# Requested 2026-11-16: every session is in the dev lane by default, except main; repinning goes to the
# feature's branch directly; only one feature runs at a time, and chats coordinate the switch.

# Story: Choose The Lane For A Project
# Actor: CDD Server (system)
with story("Choose The Lane For A Project"):
    with scenario("Run a chat in the main checkout on the stable lane"):
        with given("the main checkout seed_main_checkout, whose .git is a folder"):
            self.lanes = seed_lanes(Path(tempfile.mkdtemp()))
            self.main = seed_main_checkout(self.lanes.stable.home.folder.parent)
        with when("the CDD Server chooses the lane for that checkout"):
            # CDD Server -> ServerLanes.for_project(main checkout) <- ServerLane stable
            self.lane = self.lanes.for_project(self.main)
        with then("the chat runs on the stable lane"):
            expect(self.lane.name).to(equal(ServerLanes.STABLE))
    with scenario("Run a chat in a folder inside the main checkout on the stable lane"):
        with given("the folder harness/mcp inside the main checkout seed_main_checkout"):
            self.lanes = seed_lanes(Path(tempfile.mkdtemp()))
            self.folder = seed_main_checkout(self.lanes.stable.home.folder.parent) / "harness" / "mcp"
        with when("the CDD Server chooses the lane for that folder"):
            # CDD Server -> ServerLanes.for_project(folder) <- ServerLane stable
            self.lane = self.lanes.for_project(self.folder)
        with then("the chat runs on the stable lane"):
            expect(self.lane.name).to(equal(ServerLanes.STABLE))
    with scenario("Run a chat in a ticket's worktree on the dev lane"):
        with given("checkout-flow's worktree seed_ticket_worktree, whose .git is a file naming the main checkout"):
            self.lanes = seed_lanes(Path(tempfile.mkdtemp()))
            root = self.lanes.stable.home.folder.parent
            self.worktree = seed_ticket_worktree(root, seed_main_checkout(root))
        with when("the CDD Server chooses the lane for that worktree"):
            # CDD Server -> ServerLanes.for_project(worktree) <- ServerLane dev
            self.lane = self.lanes.for_project(self.worktree)
        with then("the chat runs on the dev lane"):
            expect(self.lane.name).to(equal(ServerLanes.DEV))
    with scenario("Run a chat outside any checkout on the dev lane"):
        with given("a folder seed_folder_outside_any_checkout that no git checkout holds"):
            self.lanes = seed_lanes(Path(tempfile.mkdtemp()))
            self.folder = seed_folder_outside_any_checkout(self.lanes.stable.home.folder.parent)
        with when("the CDD Server chooses the lane for that folder"):
            # CDD Server -> ServerLanes.for_project(folder) <- ServerLane dev
            self.lane = self.lanes.for_project(self.folder)
        with then("the chat runs on the dev lane"):
            expect(self.lane.name).to(equal(ServerLanes.DEV))
