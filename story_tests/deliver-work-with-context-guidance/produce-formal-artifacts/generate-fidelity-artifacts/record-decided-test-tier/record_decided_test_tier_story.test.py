from __future__ import annotations

from expects import contain, equal, expect, raise_error

from cdd_guidance.practices.tdd.examples.module_tiers_examples import (
    MAMBA,
    ORDERS_UNIT_SPEC,
    PLAYWRIGHT,
    PYTEST,
    SHOP_ORDERS,
    bdd_development_under,
    generate_reply,
    seed_bookshop,
    seed_file,
    seed_misshapen_record,
    session_of,
)
from harness.agent_tools.recipe import RecipeLineFailed
from space.session.test_tiers import TestToolRequiredError, UnknownTestTierError
from story_test import and_, given, scenario, story, then, when

# Epic: Deliver Work With Context Guidance
# Sub-epic: Generate Fidelity Artifacts
# Map: ../../../../../.context/story-map.md#e-generate-fidelity-artifacts
# Scenarios: ../record_test_tiers_of_module_story.test.md#story-record-decided-test-tier
# Decided 2026-11-22 (defect analysis, change 6): the tiers each module uses are kept in session.json, and the generate
# or render that writes a module's tests fills the record; nobody fills it by hand at setup.

# Story: Record Decided Test Tier
# Actor: Agent
with story("Record Decided Test Tier"):
    with scenario("Keep the test tool an agent recorded"):
        with given("the agent recorded the unit tier of SHOP_ORDERS with PYTEST"):
            self.bookshop = seed_bookshop()
            self.session = session_of(self.bookshop.root)
            self.development = bdd_development_under(self.session, SHOP_ORDERS)
            self.session.record_test_tier(SHOP_ORDERS, "unit", PYTEST)
        with when("a render saves ORDERS_UNIT_SPEC and records what it shows"):
            self.development.supplement_records([seed_file(self.bookshop.root, ORDERS_UNIT_SPEC)])
        with then("the unit tier of SHOP_ORDERS is still recorded with PYTEST"):
            expect(self.session.test_tiers.of(SHOP_ORDERS)).to(equal({"unit": PYTEST}))
            self.bookshop.close()
    with scenario("Record a tier the agent decided"):
        with given("session.json records the unit tier of SHOP_ORDERS with MAMBA"):
            self.bookshop = seed_bookshop()
            self.session = session_of(self.bookshop.root)
            self.session.record_test_tier(SHOP_ORDERS, "unit", MAMBA)
        with when("the agent records the web tier of SHOP_ORDERS with PLAYWRIGHT"):
            # Agent -> Session.record_test_tier(module, tier, tool) -> TestTiers.record
            self.answered = self.session.record_test_tier(SHOP_ORDERS, "web", PLAYWRIGHT)
        with then("the session answers SHOP_ORDERS with unit MAMBA and web PLAYWRIGHT"):
            expect(self.answered).to(equal({SHOP_ORDERS: {"unit": MAMBA, "web": PLAYWRIGHT}}))
        with and_("another reader of session.json reads the same tiers"):
            expect(session_of(self.bookshop.root).test_tiers.recorded).to(equal({SHOP_ORDERS: {"unit": MAMBA, "web": PLAYWRIGHT}}))
            self.bookshop.close()
    with scenario("Refuse a tier that is none of unit, server and web"):
        with given("the bookshop session with no test tier recorded"):
            self.bookshop = seed_bookshop()
            self.session = session_of(self.bookshop.root)
        with when("the agent records the heavy tier of SHOP_ORDERS with MAMBA"):
            self.recording = lambda: self.session.record_test_tier(SHOP_ORDERS, "heavy", MAMBA)
        with then("the agent is told heavy is no tier, and that the tiers are unit, server, web"):
            expect(self.recording).to(raise_error(UnknownTestTierError, contain("heavy", "unit, server, web")))
        with and_("session.json records no tier"):
            expect(self.session.test_tiers.recorded).to(equal({}))
            self.bookshop.close()
    with scenario("Refuse a tier recorded with no test tool"):
        with given("the bookshop session with no test tier recorded"):
            self.bookshop = seed_bookshop()
            self.session = session_of(self.bookshop.root)
        with when("the agent records the server tier of SHOP_ORDERS with an empty test tool"):
            self.recording = lambda: self.session.record_test_tier(SHOP_ORDERS, "server", " ")
        with then("the agent is told to name the test tool of the server tier"):
            expect(self.recording).to(raise_error(TestToolRequiredError, contain("server", "name the tool")))
        with and_("session.json records no tier"):
            expect(self.session.test_tiers.recorded).to(equal({}))
            self.bookshop.close()
    with scenario("Refuse a record that is wrongly shaped"):
        with given("the bookshop's session.json holds its test tiers as a list of tiers"):
            self.bookshop = seed_bookshop()
            self.session = session_of(self.bookshop.root)
            bdd_development_under(self.session, SHOP_ORDERS)
            seed_misshapen_record(self.session)
        with when("the agent generates bdd-development"):
            self.generating = lambda: generate_reply(self.bookshop.root, "bdd-development")
        with then("the generate is refused, naming test_tiers and what it holds, and is not read as no tiers chosen"):
            expect(self.generating).to(raise_error(RecipeLineFailed, contain("MisshapenTestTiersError", "test_tiers", "['unit']")))
            self.bookshop.close()
