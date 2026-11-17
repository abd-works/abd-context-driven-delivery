from __future__ import annotations

import tempfile
from pathlib import Path

from expects import be_empty, contain, equal, expect, have_len, raise_error

from harness.mcp.server_lanes import LaneCallFailed
from harness.mcp.examples.server_lanes_examples import DevLaneInProcess, FEATURE_TOOL, LEDGER_FOLDER_TOOL, LEDGER_IS_LOCKED, LOCKED_LEDGER_TOOL, seed_feature_host, seed_host, seed_main_checkout, seed_stable_lane_routing, seed_ticket_worktree
from story_test import and_, but_, given, scenario, story, then, when

# Epic: Register And Install Toolsets
# Sub-epic: Serve CDD Code In Lanes
# Map: ../../../../.context/story-map.md#e-serve-cdd-code-in-lanes
# Decision: ../../../../harness/mcp/.context/cdr/0003-two-lanes-main-stable-features-dev.md
# Requested 2026-11-16: every session is in the dev lane by default, except main. Every chat connects to the stable
# lane's address, so the stable lane's server hands a dev-lane chat's calls to the dev lane's server.

# Story: Send A Dev-Lane Chat's Calls To The Dev Lane
# Actor: CDD Server (system)
with story("Send A Dev-Lane Chat's Calls To The Dev Lane"):
    with scenario("Answer a ticket worktree's call on the served feature"):
        with given("the dev lane serves checkout-flow's worktree seed_ticket_worktree"):
            root = Path(tempfile.mkdtemp())
            self.worktree = seed_ticket_worktree(root, seed_main_checkout(root / "dev-side"))
            self.dev_lane = DevLaneInProcess(seed_host(self.worktree))
            self.lanes, self.stable_host = seed_stable_lane_routing(root, self.dev_lane)
            self.lanes.dev.home.serve_from(self.worktree)
        with when("a chat in checkout-flow's worktree calls LEDGER_FOLDER_TOOL on the stable lane"):
            # McpHost.answer -> ServerLanes.other_lane_answering(stable home, worktree) <- dev
            # ServerLane.answer -> McpAddress.send_lane_call -> dev McpHost._answer_lane_call -> McpHost.answer
            self.answer = self.stable_host.dispatch(LEDGER_FOLDER_TOOL, {}, self.worktree)
        with then("the dev lane's server answers it with checkout-flow's worktree"):
            expect(self.answer).to(equal(str(self.worktree)))
        with and_("the stable lane handed exactly that call to the dev lane"):
            expect(self.dev_lane.handed_over).to(have_len(1))
    with scenario("Answer a main chat's call on the stable lane"):
        with given("the dev lane serves checkout-flow's worktree seed_ticket_worktree"):
            root = Path(tempfile.mkdtemp())
            worktree = seed_ticket_worktree(root, seed_main_checkout(root / "dev-side"))
            self.dev_lane = DevLaneInProcess(seed_host(worktree))
            self.lanes, self.stable_host = seed_stable_lane_routing(root, self.dev_lane)
            self.lanes.dev.home.serve_from(worktree)
            self.main = root / "abd-context-driven-delivery"
        with when("a chat in the main checkout seed_main_checkout calls LEDGER_FOLDER_TOOL"):
            self.answer = self.stable_host.dispatch(LEDGER_FOLDER_TOOL, {}, self.main)
        with then("the stable lane's server answers it with the main checkout"):
            expect(self.answer).to(equal(str(self.main)))
        with and_("nothing was handed to the dev lane"):
            expect(self.dev_lane.handed_over).to(be_empty)
    with scenario("Run dev-lane chats on main until a feature is served"):
        with given("checkout-flow's worktree seed_ticket_worktree"):
            root = Path(tempfile.mkdtemp())
            self.worktree = seed_ticket_worktree(root, seed_main_checkout(root / "dev-side"))
            self.dev_lane = DevLaneInProcess(seed_host(self.worktree))
            self.lanes, self.stable_host = seed_stable_lane_routing(root, self.dev_lane)
        with but_("the dev lane serves no feature yet"):
            pass
        with when("a chat in checkout-flow's worktree calls LEDGER_FOLDER_TOOL"):
            self.answer = self.stable_host.dispatch(LEDGER_FOLDER_TOOL, {}, self.worktree)
        with then("the stable lane's server answers it, on main"):
            expect(self.answer).to(equal(str(self.worktree)))
        with and_("nothing was handed to the dev lane"):
            expect(self.dev_lane.handed_over).to(be_empty)
    with scenario("Show the chat the failure the dev lane met"):
        with given("the dev lane serves checkout-flow's worktree seed_ticket_worktree"):
            root = Path(tempfile.mkdtemp())
            self.worktree = seed_ticket_worktree(root, seed_main_checkout(root / "dev-side"))
            self.lanes, self.stable_host = seed_stable_lane_routing(root, DevLaneInProcess(seed_host(self.worktree)))
            self.lanes.dev.home.serve_from(self.worktree)
        with when("a chat in checkout-flow's worktree calls LOCKED_LEDGER_TOOL, whose ledger is locked"):
            self.calling = lambda: self.stable_host.dispatch(LOCKED_LEDGER_TOOL, {}, self.worktree)
        with then("the chat sees LEDGER_IS_LOCKED from the dev lane"):
            expect(self.calling).to(raise_error(LaneCallFailed, contain(LEDGER_IS_LOCKED)))
    # Seen 2026-11-17: a dev-lane chat could not call fidelity-session-output.add_root, which only the served feature
    # has, because the stable lane listed its own tools to every chat.
    with scenario("List the served feature's tools to a dev-lane chat"):
        with given("the dev lane serves checkout-flow's worktree seed_ticket_worktree on a feature that adds FEATURE_TOOL"):
            root = Path(tempfile.mkdtemp())
            self.worktree = seed_ticket_worktree(root, seed_main_checkout(root / "dev-side"))
            self.dev_lane = DevLaneInProcess(seed_feature_host(self.worktree))
            self.lanes, self.stable_host = seed_stable_lane_routing(root, self.dev_lane)
            self.lanes.dev.home.serve_from(self.worktree)
            self.main = root / "abd-context-driven-delivery"
        with when("a chat in checkout-flow's worktree asks the stable lane for its tools"):
            # McpHost.tools_listed_for(worktree) -> ServerLane.tools -> dev McpHost.answer(cdd.list_tools)
            self.listed = [tool["name"] for tool in self.stable_host.tools_listed_for(self.worktree)]
        with then("the list holds FEATURE_TOOL, which only the dev lane serves"):
            expect(self.listed).to(contain(FEATURE_TOOL))
        with but_("a chat in the main checkout seed_main_checkout is listed no FEATURE_TOOL"):
            expect([tool["name"] for tool in self.stable_host.tools_listed_for(self.main)]).not_to(contain(FEATURE_TOOL))
