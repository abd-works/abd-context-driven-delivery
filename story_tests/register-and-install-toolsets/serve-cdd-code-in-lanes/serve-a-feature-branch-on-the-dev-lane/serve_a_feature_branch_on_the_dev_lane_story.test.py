from __future__ import annotations

import tempfile
from pathlib import Path

from expects import be_false, equal, expect

from harness.mcp.server_lanes import ServerLanes
from harness.mcp.examples.server_lanes_examples import seed_lanes, seed_main_checkout, seed_ticket_worktree, CHECKOUT_FLOW
from story_test import and_, given, scenario, story, then, when

# Epic: Register And Install Toolsets
# Sub-epic: Serve CDD Code In Lanes
# Map: ../../../../.context/story-map.md#e-serve-cdd-code-in-lanes
# Decision: ../../../../harness/mcp/.context/cdr/0003-two-lanes-main-stable-features-dev.md
# Requested 2026-11-16: every session is in the dev lane by default, except main; repinning goes to the
# feature's branch directly; only one feature runs at a time, and chats coordinate the switch.

# Story: Serve A Feature Branch On The Dev Lane
# Actor: Person
with story("Serve A Feature Branch On The Dev Lane"):
    with scenario("Serve the feature's worktree as it is on disk"):
        with given("checkout-flow's worktree seed_ticket_worktree has its branch CHECKOUT_FLOW out"):
            self.lanes = seed_lanes(Path(tempfile.mkdtemp()))
            root = self.lanes.stable.home.folder.parent
            self.worktree = seed_ticket_worktree(root, seed_main_checkout(root))
        with when("the Person serves that worktree from disk"):
            # ServedCheckout.serve_on_disk -> CddHome.serve_from(worktree) -> runtime.json {source, branch, worktree}
            self.lanes.for_project(self.worktree).home.serve_from(self.worktree)
        with then("the dev lane serves the worktree on disk"):
            expect(self.lanes.dev.home.source).to(equal(self.worktree.resolve()))
        with and_("the dev lane names the branch CHECKOUT_FLOW"):
            expect(self.lanes.dev.home.served_branch).to(equal(CHECKOUT_FLOW))
        with and_("the stable lane serves nothing new"):
            expect(self.lanes.stable.home.is_installed).to(be_false)
