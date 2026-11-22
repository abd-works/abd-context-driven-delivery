# ---
# fidelity: [specification, engineering]
# artifact: [story-scenarios]
# format: py
# ---
#
# Report Unused Class For Deletion, Report Operation Used Only Inside Its Module, Report Disconnected Class and Report
# One-Class Package, run on the shop project read by Clean Engineering as a live load reads it
# (cdd_guidance/practices/clean_engineering/rules/code_use_examples.py).

from __future__ import annotations

from expects import equal, expect

from cdd_guidance.practices.clean_engineering.rules import BY_SLUG
from cdd_guidance.practices.clean_engineering.rules.code_use_examples import example_pair, situation
from story_test import and_, but_, given, scenario, story, then, when

# Epic: Map Work Into Knowledge Graph
# Sub-epic: Check Clean Engineering Code Through The Graph
# Map: ../../../../.context/story-map.md#e-check-clean-engineering-code-through-the-graph
# Scenarios: report_unused_and_disconnected_code_story.test.md


def _named(messages: list[str]) -> list[str]:
    """The name each message opens with, in quotes, sorted."""
    return sorted(message.split("'")[1] for message in messages)


with story("Report Unused Class For Deletion"):
    with scenario("Report a class nothing uses for deletion"):
        with given("`cart.py` also holds the class Coupon, which no class uses and which uses no class"):
            self.pair = example_pair("delete-unused-classes")
        with when("the graph rules run"):
            # InGraph.check -> DeleteUnusedClasses.check_practice -> CodeUse.unused_classes
            self.reported = self.pair.faulty.hits(self.pair.rule)
        with then("delete-unused-classes reports Coupon as no use, to delete with its specs"):
            expect([(_named([said]), "no use" in said and "delete" in said) for said in self.reported]).to(equal([(["Coupon"], True)]))
        with and_("delete-unused-operations reports none of Coupon's operations, which go with it"):
            expect(self.pair.faulty.hits(BY_SLUG["delete-unused-operations"])).to(equal([]))
    with scenario("Pass a class another class uses"):
        with given("the till takes a Coupon off each line it rings up"):
            self.pair = example_pair("delete-unused-classes")
        with when("the graph rules run"):
            self.reported = self.pair.repaired.hits(self.pair.rule)
        with then("delete-unused-classes reports nothing"):
            expect(self.reported).to(equal([]))
    with scenario("Report an operation, a private operation, a property and a module function nothing uses for deletion"):
        with given("Cart also has the operation clear, the private operation recount and the property empty, which nothing calls or reads"):
            self.pair = example_pair("delete-unused-operations")
        with and_("`cart.py` holds the function count_lines, which Cart's total calls, and the function count_twice, which nothing calls"):
            pass
        with when("the graph rules run"):
            self.reported = self.pair.faulty.hits(self.pair.rule)
        with then("delete-unused-operations reports clear, recount, empty and count_twice as no use, to delete with their specs"):
            expect((_named(self.reported), all("no use" in said for said in self.reported))).to(equal((["_recount", "clear", "count_twice", "empty"], True)))
        with and_("it does not report count_lines, which its own file uses"):
            expect("count_lines" in _named(self.reported)).to(equal(False))
    with scenario("Pass operations, private operations and properties that are used"):
        with given("count_twice is deleted, the cart's clear calls its own recount, and the till clears the cart once it has rung a line up, when the cart is not empty"):
            self.pair = example_pair("delete-unused-operations")
        with when("the graph rules run"):
            self.reported = self.pair.repaired.hits(self.pair.rule)
        with then("delete-unused-operations reports nothing"):
            expect(self.reported).to(equal([]))
    with scenario("Count a use from example code only when production imports it"):
        with given("the class Printer, which only the receipt examples use, a file named as example code that nothing in production imports"):
            self.without, self.within = situation("example code nothing in production imports")
        with when("the graph rules run"):
            self.reported = (self.without.hits(BY_SLUG["delete-unused-classes"]), self.within.hits(BY_SLUG["delete-unused-classes"]))
        with then("delete-unused-classes reports Printer as no use"):
            expect(_named(self.reported[0])).to(equal(["Printer"]))
        with but_("once the till rings up the receipt example, so production imports the example code and runs it, delete-unused-classes reports nothing"):
            expect(self.reported[1]).to(equal([]))
    with scenario("Count no use from spec support the project's config names as test code"):
        with given("the class Printer, which only the print checks use, spec support kept under a production name"):
            self.without, self.within = situation("spec support the config names as test code")
        with when("the graph rules run"):
            self.reported = (self.without.hits(BY_SLUG["delete-unused-classes"]), self.within.hits(BY_SLUG["delete-unused-classes"]))
        with then("delete-unused-classes reports nothing, since the print checks read as production code"):
            expect(self.reported[0]).to(equal([]))
        with but_("once the shop's config names the print checks as test code under `test_code`, delete-unused-classes reports Printer as no use"):
            expect(_named(self.reported[1])).to(equal(["Printer"]))
    with scenario("List a member a library outside the code read may call as a candidate, not a violation"):
        with given("the shop's start builds a ShopFormatter, which extends a formatter from a library outside the code read"):
            _, self.shop = situation("a class extending a class from outside the code read")
        with and_("nothing the read sees calls ShopFormatter's example_passed"):
            pass
        with when("the graph rules run"):
            self.listed = self.shop.hits(BY_SLUG["check-use-the-graph-cannot-see"])
        with then("check-use-the-graph-cannot-see lists example_passed as a candidate for a reading"):
            expect(_named(self.listed)).to(equal(["example_passed"]))
        with and_("delete-unused-operations does not report it, since the library may call it as an override"):
            expect(_named(self.shop.hits(BY_SLUG["delete-unused-operations"]))).to(equal([]))
    with scenario("Count a call through a protocol as a use of each class that satisfies it"):
        with given("Book has price and label, and nothing calls them"):
            self.without, self.within = situation("an operation called through a protocol its class satisfies")
        with when("the graph rules run"):
            self.reported = (self.without.hits(BY_SLUG["delete-unused-operations"]), self.within.hits(BY_SLUG["delete-unused-operations"]))
        with then("delete-unused-operations reports price and label as no use"):
            expect(_named(self.reported[0])).to(equal(["label", "price"]))
        with but_("once the till prices whatever satisfies the protocol Priced, which Book satisfies by shape, delete-unused-operations reports nothing"):
            expect(self.reported[1]).to(equal([]))
    with scenario("List a class an unseen call may use as a candidate, not a violation"):
        with given("`cart.py` also holds the classes Coupon and Voucher, which no class uses, and which each have value"):
            self.pair = example_pair("check-use-the-graph-cannot-see")
        with and_("the till takes value off an offer whose class no hint says"):
            pass
        with when("the graph rules run"):
            self.listed = self.pair.faulty.hits(self.pair.rule)
        with then("check-use-the-graph-cannot-see lists Coupon and Voucher as candidates for a reading"):
            expect((_named(self.listed), self.pair.rule.requires_judge)).to(equal((["Coupon", "Voucher"], True)))
        with and_("delete-unused-classes reports nothing"):
            expect(self.pair.faulty.hits(BY_SLUG["delete-unused-classes"])).to(equal([]))

with story("Report Operation Used Only Inside Its Module"):
    with scenario("List a public operation only its own module calls"):
        with given("only the till, in the shop module, calls the cart's add and total"):
            self.pair = example_pair("make-module-only-operations-private")
        with when("the graph rules run"):
            self.listed = self.pair.faulty.hits(self.pair.rule)
        with then("make-module-only-operations-private lists add and total as candidates for a reading"):
            expect((_named(self.listed), self.pair.rule.requires_judge)).to(equal((["add", "total"], True)))
    with scenario("Pass a public operation another module calls"):
        with given("the till sits in the orders module, and an app folder starts the shop"):
            self.pair = example_pair("make-module-only-operations-private")
        with when("the graph rules run"):
            self.listed = self.pair.repaired.hits(self.pair.rule)
        with then("make-module-only-operations-private lists nothing"):
            expect(self.listed).to(equal([]))

with story("Report Disconnected Class"):
    with scenario("List a class joined to others only by inheritance"):
        with given("`receipt.py` holds Receipt, which extends Printable, and no class holds, creates or calls either"):
            self.pair = example_pair("connect-disconnected-classes")
        with when("the graph rules run"):
            self.listed = self.pair.faulty.hits(self.pair.rule)
        with then("connect-disconnected-classes lists Printable and Receipt as candidates, each naming the relationship that may be missing"):
            expect((_named(self.listed), all("composition" in said for said in self.listed))).to(equal((["Printable", "Receipt"], True)))
    with scenario("Pass a class a way the project reaches code holds, such as a registry or a publishing decorator"):
        with given("Receipt is registered with the printers registry, which holds it"):
            _, self.shop = situation("a class a registry holds")
        with when("the graph rules run"):
            self.listed = self.shop.hits(BY_SLUG["connect-disconnected-classes"])
        with then("connect-disconnected-classes lists neither Receipt nor Printable, which the registry connects"):
            expect(self.listed).to(equal([]))
    with scenario("Pass a class another class holds"):
        with given("the till holds the receipt it prints"):
            self.pair = example_pair("connect-disconnected-classes")
        with when("the graph rules run"):
            self.listed = self.pair.repaired.hits(self.pair.rule)
        with then("connect-disconnected-classes lists nothing"):
            expect(self.listed).to(equal([]))

with story("Report One-Class Package"):
    with scenario("List a package that holds one class"):
        with given("the shop module's coupons package, a folder with no module card, holds only Coupon"):
            self.pair = example_pair("merge-one-class-packages")
        with when("the graph rules run"):
            self.listed = self.pair.faulty.hits(self.pair.rule)
        with then("merge-one-class-packages lists coupons as a candidate to merge, delete or model"):
            expect((_named(self.listed), self.pair.rule.requires_judge)).to(equal((["coupons"], True)))
    with scenario("Pass a package that holds several classes"):
        with given("the coupons package holds Coupon and Voucher"):
            self.pair = example_pair("merge-one-class-packages")
        with when("the graph rules run"):
            self.listed = self.pair.repaired.hits(self.pair.rule)
        with then("merge-one-class-packages lists nothing"):
            expect(self.listed).to(equal([]))
