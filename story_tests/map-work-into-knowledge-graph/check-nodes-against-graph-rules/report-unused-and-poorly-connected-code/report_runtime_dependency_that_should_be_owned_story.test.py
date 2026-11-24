# ---
# fidelity: [specification, engineering]
# artifact: [story-scenarios]
# format: py
# ---
#
# Report Runtime Dependency That Should Be Owned, run on the domain objects: the shop project's classes read as a
# working copy is, and the judged rule put-logic-on-the-owning-resource reading the dependencies the read records.

from __future__ import annotations

from expects import be_true, equal, expect

from cdd_guidance.practices.clean_engineering.rules import BY_SLUG
from cdd_guidance.practices.clean_engineering.rules.fixtures import cross_file_examples as examples
from cdd_guidance.practices.clean_engineering.rules.rule_examples import files_rule_pair, practice_from_files
from harness.graph.violation import Violation
from harness.installation.data_class import data_of
from story_test import and_, given, scenario, story, then, when

# Epic: Map Work Into Knowledge Graph
# Sub-epic: Report Unused And Poorly Connected Code
# Map: ../../../../.context/story-map.md#e-report-unused-and-poorly-connected-code

_SLUG = "put-logic-on-the-owning-resource"
_RULE = BY_SLUG[_SLUG]
# Outline: each way Cart reaches PriceList that is owned or handed in.
_OWNED_OR_HANDED = (examples.CART_HOLDS_WHAT_IT_IS_HANDED, examples.CART_IS_HANDED_A_PARAMETER, examples.CART_BUILDS_IN_ITS_CONSTRUCTOR)

with story("Report Runtime Dependency That Should Be Owned"):
    with scenario("List a class that builds another on each call from strings"):
        with given('Cart\'s operation total builds `PriceList("usd")` on each call'):
            self.shop = practice_from_files(examples.CART_BUILDS_PER_CALL)
        with when("the graph rules run"):
            # InGraph.check -> PutLogicOnTheOwningResource.check_practice -> Node.get_fact(dependencies_to_own)
            self.listed = self.shop.hits(_RULE)
        with then("put-logic-on-the-owning-resource lists Cart as a candidate, saying it builds a PriceList on each call in total"):
            expect([said.startswith("Class 'Cart' builds a 'PriceList' on each call (in total)") for said in self.listed]).to(equal([True]))
        with and_("the candidate names Cart as the owner to consider, with the PriceList as a part it builds once and keeps (composition) or one handed to it and held (association)"):
            expect("(composition)" in self.listed[0] and "(association)" in self.listed[0]).to(be_true)
    with scenario("List a class that looks another up by name"):
        with given('Cart\'s operation park finds a Depot by name, `Depot.named("north")`'):
            self.shop = practice_from_files(examples.CART_LOOKS_UP_BY_NAME)
        with when("the graph rules run"):
            self.listed = self.shop.hits(_RULE)
        with then("put-logic-on-the-owning-resource lists Cart as a candidate, saying it looks up a Depot by name in park"):
            expect([said.startswith("Class 'Cart' looks up a 'Depot' by name (in park)") for said in self.listed]).to(equal([True]))
    with scenario("Pass a dependency that is owned or handed in"):
        with given("Cart reaches PriceList <how>"):
            self.shops = [practice_from_files(files) for files in _OWNED_OR_HANDED]
        with when("the graph rules run"):
            self.listed = [shop.hits(_RULE) for shop in self.shops]
        with then("put-logic-on-the-owning-resource lists nothing"):
            expect(self.listed).to(equal([[]] * len(_OWNED_OR_HANDED)))
    with scenario("Pass a class built on each call from a formatted message"):
        with given("Cart's operation warn builds `Note(f\"no price for {sku}\")` on each call"):
            self.shop = practice_from_files(examples.CART_BUILDS_A_MESSAGE_PER_CALL)
        with when("the graph rules run"):
            self.listed = self.shop.hits(_RULE)
        with then("put-logic-on-the-owning-resource lists nothing"):
            expect(self.listed).to(equal([]))
    with scenario("Report a rule's failing example and pass its repaired example"):
        with given("the failing example, where Cart builds a PriceList on each call, and the repaired example, where Cart holds the PriceList it is handed"):
            self.pair = files_rule_pair(_SLUG, examples.CART_BUILDS_PER_CALL, examples.CART_HOLDS_WHAT_IT_IS_HANDED)
        with when("the graph rules run"):
            self.faulty, self.repaired = self.pair.faulty.hits(_RULE), self.pair.repaired.hits(_RULE)
        with then("put-logic-on-the-owning-resource lists the failing example"):
            expect(len(self.faulty)).to(equal(1))
        with and_("it lists nothing in the repaired example"):
            expect(self.repaired).to(equal([]))
    with scenario("List the candidates outside the paths given only when validate asks for the judged pass"):
        with given("Cart builds a PriceList on each call in `shop/cart.py`"):
            self.shop = practice_from_files(examples.CART_BUILDS_PER_CALL)
            self.shop.hits(_RULE)
            cart = next(node for node in self.shop.practice.reading.in_graph.nodes("OoadClass") if node.name == "Cart")
            self.found = cart.rules[_SLUG].violations[0]
        with when("Claude Code validates clean-engineering-model on `docs` without the judged pass"):
            # Violation.is_reported_for: a judged rule of scope all lists its candidates outside the paths only for the judged pass
            self.without = self.found.is_reported_for(["docs"], judge_all=False)
        with then("the report lists no put-logic-on-the-owning-resource candidate"):
            expect(self.without).to(equal(False))
        with and_("validated on `shop` without the judged pass, it lists the candidate, as it lists every candidate in the paths given"):
            expect(self.found.is_reported_for(["shop"], judge_all=False)).to(equal(True))
        with and_("validated on `docs` with the judged pass, it lists the candidate in `shop/cart.py`, marked as found outside the paths given"):
            expect((self.found.is_reported_for(["docs"], judge_all=True), Violation.from_data(data_of(self.found)).runs_over_all)).to(equal((True, True)))
