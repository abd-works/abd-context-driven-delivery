# ---
# fidelity: [specification, engineering]
# artifact: [story-scenarios]
# format: py
# ---
#
# Judge Clean Engineering Rules Across Files, run on the domain objects: small projects read as a working copy is, and
# the rules of scope all that compare their files: the same work in two files, state handed down, a second registry,
# two verbs for one concept, and a module card the code has moved on from.

from __future__ import annotations

from expects import contain, equal, expect

from cdd_guidance.practices.clean_engineering.rules import BY_SLUG
from cdd_guidance.practices.clean_engineering.rules.fixtures import cross_file_examples as examples
from cdd_guidance.practices.clean_engineering.rules.rule_examples import files_rule_pair, practice_from_files
from story_test import and_, given, scenario, story, then, when

# Epic: Map Work Into Knowledge Graph
# Sub-epic: Check Clean Engineering Code Through The Graph
# Map: ../../../../.context/story-map.md#e-check-clean-engineering-code-through-the-graph

# Outline: each rule, its failing example and its repaired example.
_PAIRS = (
    ("eliminate-duplication", examples.TOTALLED_IN_TWO_FILES, examples.TOTALLED_IN_ONE_PLACE),
    ("hold-state-on-the-object-not-in-parameters", examples.SESSION_HANDED_DOWN, examples.SESSION_HELD),
    ("hold-state-on-the-object-not-in-parameters", examples.TICKET_TO_EVERY_OPERATION, examples.TICKET_HELD),
    ("do-not-invent-parallel-object-models", examples.SECOND_REGISTRY, examples.ONE_REGISTRY),
    ("use-consistent-naming", examples.TWO_VERBS_FOR_ORDER, examples.ONE_VERB_FOR_ORDER),
    ("seam-names-current-code", examples.CARD_BEHIND_THE_CODE, examples.CARD_MATCHING_THE_CODE),
)

with story("Judge Clean Engineering Rules Across Files"):
    with scenario("List operations in different files that do the same work, once as a group"):
        with given("Invoice.total in `billing/invoice.py` and Parcel.cost in `shipping/parcel.py` total their lines with the same four statements, each under own names of its own"):
            self.project = practice_from_files(examples.TOTALLED_IN_TWO_FILES)
        with when("the graph rules run"):
            # InGraph.check -> EliminateDuplication.check_practice -> own_fact(same_body_elsewhere)
            self.listed = self.project.hits(BY_SLUG["eliminate-duplication"])
        with then("eliminate-duplication lists both operations in one candidate"):
            expect([said.split(" do the same work")[0] for said in self.listed]).to(equal(["Operations 'billing/invoice.py: Invoice.total', 'shipping/parcel.py: Parcel.cost'"]))
    with scenario("Report a body copied word for word"):
        with given("Invoice.total and Parcel.total have the same body, word for word"):
            self.project = practice_from_files(examples.COPIED_IN_TWO_FILES)
        with when("the graph rules run"):
            self.listed = self.project.hits(BY_SLUG["eliminate-duplication"])
            parcel = next(node for node in self.project.practice.reading.in_graph.nodes("Operation") if node.source.file == "shipping/parcel.py" and node.name == "total")
            self.found = parcel.rules["eliminate-duplication"].violations
        with then("eliminate-duplication reports Parcel.total as a violation the graph decides"):
            expect([violation.severity for violation in self.found]).to(equal(["error"]))
        with and_("it lists no group of the two beside it"):
            expect([said for said in self.listed if "do the same work" in said]).to(equal([]))
    with scenario("List two verbs for one concept"):
        with given("Cart has get_order and Till has fetch_order"):
            self.project = practice_from_files(examples.TWO_VERBS_FOR_ORDER)
        with when("the graph rules run"):
            self.listed = self.project.hits(BY_SLUG["use-consistent-naming"])
        with then("use-consistent-naming lists both operations, the target order, and the verbs fetch and get"):
            expect([said.split(". Read")[0] for said in self.listed]).to(equal(["Operations 'store/cart.py: Cart.get_order', 'store/till.py: Till.fetch_order' name one concept, 'order', with the verbs fetch, get"]))
    with scenario("Report a module card the code has moved on from"):
        with given("the shop card names Basket in its seam and stock and `ledger/books` as dependencies, and the shop code imports tax"):
            self.project = practice_from_files(examples.CARD_BEHIND_THE_CODE)
        with when("the graph rules run"):
            # InGraph.check -> SeamNamesCurrentCode.check_practice -> Node.get_fact(card_drift)
            self.reported = self.project.hits(BY_SLUG["seam-names-current-code"])
        with then("seam-names-current-code reports the seam term, the dependency not imported, the dependency that is no folder, and the import the card does not name"):
            expect(len(self.reported)).to(equal(4))
        with and_("each is a violation the graph decides, not a candidate"):
            expect(BY_SLUG["seam-names-current-code"].requires_judge).to(equal(False))
    with scenario("Report each rule's failing example and pass its repaired example"):
        with given("the failing example and the repaired example of <rule>"):
            self.pairs = [files_rule_pair(slug, faulty, repaired) for slug, faulty, repaired in _PAIRS]
        with when("the graph rules run"):
            self.results = [(bool(pair.faulty.hits(pair.rule)), pair.repaired.hits(pair.rule)) for pair in self.pairs]
        with then("<rule> lists the failing example"):
            expect([listed for listed, _repaired in self.results]).to(equal([True] * len(_PAIRS)))
        with and_("it lists nothing in the repaired example"):
            expect([repaired for _listed, repaired in self.results]).to(equal([[]] * len(_PAIRS)))
    with scenario("Run each rule over the whole working copy"):
        with given("the rules that compare files"):
            self.rules = [BY_SLUG[slug] for slug, _faulty, _repaired in _PAIRS]
        with when("validate is given paths"):
            self.scopes = {rule.scope for rule in self.rules}
        with then("each rule still runs over the whole working copy"):
            expect(self.scopes).to(equal({"all"}))


with story("Judge Passed Parameters And Second Registries"):
    with scenario("List a parameter handed down to two other classes"):
        with given("Desk.open hands its session to Clerk.file, which hands it to Archive.store"):
            self.project = practice_from_files(examples.SESSION_HANDED_DOWN)
        with when("the graph rules run"):
            self.listed = self.project.hits(BY_SLUG["hold-state-on-the-object-not-in-parameters"])
        with then("hold-state-on-the-object-not-in-parameters lists Desk.open, naming the session and each operation it passes"):
            expect(self.listed).to(contain(
                "Operation 'Desk.open' hands its parameter 'session' on unchanged to 2 other classes: Desk.open, Clerk.file, "
                "Archive.store. Read which object should hold the session, so the operations below it read it there."
            ))
    with scenario("Pass a parameter handed between one class's own operations, or to a constructor"):
        with given("Desk.open hands its session only to Desk's own operations, or to the constructor of the Clerk made for it"):
            self.projects = [practice_from_files(files) for files in (examples.SESSION_HANDED_WITHIN_ONE_CLASS, examples.SESSION_HANDED_TO_A_CONSTRUCTOR)]
        with when("the graph rules run"):
            self.listed = [project.hits(BY_SLUG["hold-state-on-the-object-not-in-parameters"]) for project in self.projects]
        with then("hold-state-on-the-object-not-in-parameters lists nothing"):
            expect(self.listed).to(equal([[], []]))
    with scenario("List a class every operation of which takes the same parameter"):
        with given("each of Board's three operations takes a ticket"):
            self.project = practice_from_files(examples.TICKET_TO_EVERY_OPERATION)
        with when("the graph rules run"):
            self.listed = self.project.hits(BY_SLUG["hold-state-on-the-object-not-in-parameters"])
        with then("hold-state-on-the-object-not-in-parameters lists Board"):
            expect(self.listed).to(equal(["Every operation of 'Board' (3) takes 'ticket'. Read whether 'Board' is made for one ticket and should hold it."]))
    with scenario("List a second registry of the same classes"):
        with given("`report/listing.py` lists Alpha, Beta and Gamma, which `checks/registry.py` already holds"):
            self.project = practice_from_files(examples.SECOND_REGISTRY)
        with when("the graph rules run"):
            self.listed = self.project.hits(BY_SLUG["do-not-invent-parallel-object-models"])
        with then("do-not-invent-parallel-object-models lists both collections and the classes they share"):
            expect([said.split(". Read")[0] for said in self.listed]).to(equal(["'checks/registry.py' CHECKS and 'report/listing.py' LISTED hold the same classes: Alpha, Beta, Gamma"]))
    with scenario("Pass a list of exported names, and one that spells the classes' names as labels"):
        with given("`checks/__init__.py` exports Alpha, Beta and Gamma in `__all__`, and `report/listing.py` lists their names as strings"):
            self.project = practice_from_files(examples.NAMES_EXPORTED_AND_SPELLED)
        with when("the graph rules run"):
            self.listed = self.project.hits(BY_SLUG["do-not-invent-parallel-object-models"])
        with then("do-not-invent-parallel-object-models lists nothing"):
            expect(self.listed).to(equal([]))
