from __future__ import annotations

import tempfile
from pathlib import Path

from expects import equal, expect

from harness.mcp.server_lanes import ServerLanes
from harness.mcp.examples.server_lanes_examples import (
    ADAPTER_FILE,
    ADAPTER_TEXT,
    DEV_PORT,
    IDE_FOLDER,
    seed_lanes,
    seed_main_checkout,
    seed_ticket_worktree,
    seed_written_language_adapters,
)
from story_test import and_, given, scenario, story, then, when

# Epic: Register And Install Toolsets
# Sub-epic: Serve CDD Code In Lanes
# Map: ../../../../.context/story-map.md#e-serve-cdd-code-in-lanes
# Decision: ../../../../harness/mcp/.context/cdr/0003-two-lanes-main-stable-features-dev.md
# Requested 2026-11-16: every session is in the dev lane by default, except main; repinning goes to the
# feature's branch directly; only one feature runs at a time, and chats coordinate the switch.

# Story: Install Into The Lane Of The Checkout
# Actor: Person
with story("Install Into The Lane Of The Checkout"):
    with scenario("Install from the main checkout into the stable lane"):
        with given("the main checkout seed_main_checkout"):
            self.lanes = seed_lanes(Path(tempfile.mkdtemp()))
            self.main = seed_main_checkout(self.lanes.stable.home.folder.parent)
        with when("the Person installs CDD from it"):
            # McpInstallation -> ServerLanes.for_project(checkout).served_checkout(checkout)
            self.served = self.lanes.for_project(self.main).served_checkout(self.main)
        with then("the checkout is served from the stable lane's home"):
            expect(self.served.home.folder).to(equal(self.lanes.stable.home.folder))
    with scenario("Install from a ticket's worktree into the dev lane"):
        with given("checkout-flow's worktree seed_ticket_worktree"):
            self.lanes = seed_lanes(Path(tempfile.mkdtemp()))
            root = self.lanes.stable.home.folder.parent
            self.worktree = seed_ticket_worktree(root, seed_main_checkout(root))
        with when("the Person installs CDD from it"):
            # McpInstallation -> ServerLanes.for_project(worktree).served_checkout(worktree)
            self.lane = self.lanes.for_project(self.worktree)
            self.served = self.lane.served_checkout(self.worktree)
        with then("the worktree is served from the dev lane's home, inside the stable lane's"):
            expect(self.served.home.folder).to(equal(self.lanes.stable.home.folder / ServerLanes.DEV_FOLDER))
        with and_("the dev lane answers on DEV_PORT, the port after the stable lane's"):
            expect(self.lane.port).to(equal(DEV_PORT))
    with scenario("Copy the worktree's language adapters into the dev lane's runtime"):
        with given("checkout-flow's worktree seed_ticket_worktree, its install having written its language adapters"):
            self.lanes = seed_lanes(Path(tempfile.mkdtemp()))
            root = self.lanes.stable.home.folder.parent
            self.worktree = seed_ticket_worktree(root, seed_main_checkout(root))
            self.adapters = seed_written_language_adapters(self.worktree)
        with when("the Person pins it, and its lane takes the adapters its install wrote"):
            # install.py -> McpInstallation.served.home.take_language_adapters(installer adapters, IDE folder)
            self.served = self.lanes.for_project(self.worktree).served_checkout(self.worktree)
            self.served.home.take_language_adapters(self.adapters, IDE_FOLDER)
        with then("the dev lane's runtime holds them, where the apps it serves import them"):
            copied = self.lanes.dev.home.pinned_checkout / IDE_FOLDER / "language-adapters" / ADAPTER_FILE
            expect(copied.read_text(encoding="utf-8")).to(equal(ADAPTER_TEXT))
        with and_("the stable lane's runtime holds none"):
            expect((self.lanes.stable.home.pinned_checkout / IDE_FOLDER).exists()).to(equal(False))
