from __future__ import annotations

from expects import contain, equal, expect, raise_error

from cdd_guidance.practices.tdd.examples.module_tiers_examples import (
    MAMBA,
    ORDERS_BROWSER_STORY_TEST,
    ORDERS_SERVER_STORY_TEST,
    ORDERS_TYPESCRIPT_SPEC,
    ORDERS_UNIT_SPEC,
    PAY_SERVER_STORY_TEST,
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
# Sub-epic: Produce Formal Artifacts
# Map: ../../../../.context/story-map.md#e-produce-formal-artifacts
# Scenarios: ../record_test_tiers_of_module_story.test.md#story-record-test-tiers-of-module
# Decided 2026-11-22 (defect analysis, change 6): the tiers each module uses are kept in session.json, and the generate
# or render that writes a module's tests fills the record; nobody fills it by hand at setup.

# Story: Record Test Tiers Of Module
# Actor: Agent
with story("Record Test Tiers Of Module"):
    with scenario("Record the unit tier as a module's specs are generated"):
        with given("the bookshop session writes its BDD development specs under SHOP_ORDERS, a module, with no test tier recorded"):
            self.bookshop = seed_bookshop()
            self.session = session_of(self.bookshop.root)
            bdd_development_under(self.session, SHOP_ORDERS)
        with when("the agent generates bdd-development"):
            # Agent -> Generate.generate -> FidelityGuidance.supplement_records -> Tdd.records_for -> TestTiers.record
            self.reply = generate_reply(self.bookshop.root, "bdd-development")
        with then("session.json records the unit tier of SHOP_ORDERS with MAMBA"):
            expect(self.session.test_tiers.recorded).to(equal({SHOP_ORDERS: {"unit": MAMBA}}))
        with and_("the reply says what the record holds"):
            expect(self.reply).to(contain(f"{SHOP_ORDERS}: unit ({MAMBA})"))
            self.bookshop.close()
    with scenario("Ask the agent to decide the tiers no test file shows"):
        with given("the bookshop session writes its BDD development specs under SHOP_ORDERS, which has no server or browser test"):
            self.bookshop = seed_bookshop()
            bdd_development_under(session_of(self.bookshop.root), SHOP_ORDERS)
        with when("the agent generates bdd-development"):
            self.reply = generate_reply(self.bookshop.root, "bdd-development")
        with then("the reply says it cannot tell whether SHOP_ORDERS publishes operations through a server or shows a page"):
            expect(self.reply).to(contain(f"cannot tell whether {SHOP_ORDERS}", "the server tier", "the web tier"))
        with and_("the reply asks the agent to record each tier the module needs with session.record_test_tier"):
            expect(self.reply).to(contain("session.record_test_tier"))
            self.bookshop.close()
    with scenario("Record the server and web tiers a module's story tests show"):
        with given("SHOP_ORDERS holds ORDERS_SERVER_STORY_TEST and ORDERS_BROWSER_STORY_TEST, just rendered"):
            self.bookshop = seed_bookshop()
            self.session = session_of(self.bookshop.root)
            self.development = bdd_development_under(self.session, SHOP_ORDERS)
            self.saved = [seed_file(self.bookshop.root, path) for path in (ORDERS_SERVER_STORY_TEST, ORDERS_BROWSER_STORY_TEST)]
        with when("the render records what the saved files show"):
            # Render -> FidelityGuidance.supplement_records(saved) -> Tdd.records_for -> TestTiers.record
            self.said = self.development.supplement_records(self.saved)
        with then("session.json records unit and server with MAMBA and web with PLAYWRIGHT for SHOP_ORDERS"):
            expect(self.session.test_tiers.of(SHOP_ORDERS)).to(equal({"unit": MAMBA, "server": MAMBA, "web": PLAYWRIGHT}))
        with and_("the render asks nothing more about the tiers of SHOP_ORDERS"):
            expect(self.said).not_to(contain("cannot tell whether"))
            self.bookshop.close()
    with scenario("Ask the agent for the module of a story test under no module's folder"):
        with given("PAY_SERVER_STORY_TEST, just rendered under story_tests, where no folder holds a module card"):
            self.bookshop = seed_bookshop()
            self.session = session_of(self.bookshop.root)
            self.development = bdd_development_under(self.session, "story_tests")
            self.saved = [seed_file(self.bookshop.root, PAY_SERVER_STORY_TEST)]
        with when("the render records what the saved file shows"):
            self.said = self.development.supplement_records(self.saved)
        with then("session.json records no module"):
            expect(self.session.test_tiers.recorded).to(equal({}))
        with and_("the render names PAY_SERVER_STORY_TEST as a server tier test and asks the agent to record it for the module it tests"):
            expect(self.said).to(contain(PAY_SERVER_STORY_TEST, "server tier", "session.record_test_tier"))
            self.bookshop.close()
    with scenario("Ask the agent for the test tool a file's name does not say"):
        with given("ORDERS_TYPESCRIPT_SPEC, just rendered, a unit test in TypeScript"):
            self.bookshop = seed_bookshop()
            self.session = session_of(self.bookshop.root)
            self.development = bdd_development_under(self.session, SHOP_ORDERS)
            self.saved = [seed_file(self.bookshop.root, ORDERS_TYPESCRIPT_SPEC)]
        with when("the render records what the saved file shows"):
            self.said = self.development.supplement_records(self.saved)
        with then("session.json records no tier for SHOP_ORDERS"):
            expect(self.session.test_tiers.of(SHOP_ORDERS)).to(equal({}))
        with and_("the render asks the agent to record the unit tier with the test tool the module's tests run with"):
            expect(self.said).to(contain(ORDERS_TYPESCRIPT_SPEC, "test tool"))
            self.bookshop.close()
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
