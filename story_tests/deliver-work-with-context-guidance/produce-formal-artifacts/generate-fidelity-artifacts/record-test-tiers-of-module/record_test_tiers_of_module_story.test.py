from __future__ import annotations

from expects import contain, equal, expect

from cdd_guidance.practices.tdd.examples.module_tiers_examples import (
    MAMBA,
    ORDERS_BROWSER_STORY_TEST,
    ORDERS_SERVER_STORY_TEST,
    ORDERS_TYPESCRIPT_SPEC,
    PAY_SERVER_STORY_TEST,
    PLAYWRIGHT,
    SHOP_ORDERS,
    bdd_development_under,
    generate_reply,
    seed_bookshop,
    seed_file,
    session_of,
)
from story_test import and_, given, scenario, story, then, when

# Epic: Deliver Work With Context Guidance
# Sub-epic: Generate Fidelity Artifacts
# Map: ../../../../../.context/story-map.md#e-generate-fidelity-artifacts
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
