"""Clean Engineering's rules across files: what only shows when the whole code is read at once. Each rule has scope all,
so validate runs it over the whole working copy; the judged ones list candidates, and only when validate is asked for
the judged pass. Each is checked against its failing and repaired example, read as a working copy is."""

from pathlib import Path
import sys

_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import contain, equal, expect
from mamba import before, context, description, it

from cdd_guidance.practices.clean_engineering.rules import BY_SLUG
from cdd_guidance.practices.clean_engineering.rules.fixtures import cross_file_examples as examples
from cdd_guidance.practices.clean_engineering.rules.rule_examples import files_rule_pair, practice_from_files

_OWNED = "put-logic-on-the-owning-resource"
_COPIES = "eliminate-duplication"
_HELD_STATE = "hold-state-on-the-object-not-in-parameters"
_ONE_MODEL = "do-not-invent-parallel-object-models"
_ONE_VERB = "use-consistent-naming"
_CARD = "seam-names-current-code"


def _listed(slug: str, files: dict[str, str]) -> list[str]:
    return practice_from_files(files).hits(BY_SLUG[slug])


def _violations(fixture, slug: str) -> list:
    """Each violation and candidate the rule recorded on the fixture's nodes, after the graph has checked them."""
    fixture.hits(BY_SLUG[slug])
    entries = [node.rules.entries.get(slug) for node in fixture.practice.reading.in_graph.nodes()]
    return [violation for entry in entries if entry is not None for violation in entry.violations]


with description("a rule that reads the whole code at once") as self:
    with context("of scope all"):
        with it("should be each rule this step adds"):
            expect([BY_SLUG[slug].scope for slug in (_OWNED, _COPIES, _HELD_STATE, _ONE_MODEL, _ONE_VERB, _CARD)]).to(equal(["all"] * 6))

        with it("should list candidates for a judge, except the card's and the word-for-word copies, which the graph decides"):
            expect([BY_SLUG[slug].requires_judge for slug in (_OWNED, _COPIES, _HELD_STATE, _ONE_MODEL, _ONE_VERB, _CARD)]).to(
                equal([True, False, True, True, True, False])
            )

    with context("about a class that reaches another it should own"):
        with before.all:
            self.pair = files_rule_pair(_OWNED, examples.CART_BUILDS_PER_CALL, examples.CART_HOLDS_WHAT_IT_IS_HANDED)
            self.per_call = _listed(_OWNED, examples.CART_BUILDS_PER_CALL)

        with it("should list the class that builds it per call from strings, and pass once it holds the one it is handed"):
            self.pair.check()

        with it("should name the owner to consider and the relationship it could be"):
            expect(self.per_call).to(equal([
                "Class 'Cart' builds a 'PriceList' on each call (in total), from strings or dicts. Read whether 'Cart' "
                "should own it: a part it builds once and keeps (composition), or a PriceList handed to it and held (association)."
            ]))

        with it("should list the class that looks it up by name"):
            expect(_listed(_OWNED, examples.CART_LOOKS_UP_BY_NAME)).to(equal([
                "Class 'Cart' looks up a 'Depot' by name (in park). Read whether 'Cart' should hold the Depot it means, "
                "handed to it (association), or own it as a part it builds once and keeps (composition)."
            ]))

        with it("should not list one built on each call from a formatted message"):
            expect(_listed(_OWNED, examples.CART_BUILDS_A_MESSAGE_PER_CALL)).to(equal([]))

        with it("should not list one handed to an operation as a parameter"):
            expect(_listed(_OWNED, examples.CART_IS_HANDED_A_PARAMETER)).to(equal([]))

        with it("should not list one its constructor builds and keeps"):
            expect(_listed(_OWNED, examples.CART_BUILDS_IN_ITS_CONSTRUCTOR)).to(equal([]))

    with context("about operations in different files that do the same work"):
        with before.all:
            self.pair = files_rule_pair(_COPIES, examples.TOTALLED_IN_TWO_FILES, examples.TOTALLED_IN_ONE_PLACE)
            self.fixture = practice_from_files(examples.TOTALLED_IN_TWO_FILES)
            self.listed = self.fixture.hits(BY_SLUG[_COPIES])
            self.copied = practice_from_files(examples.COPIED_IN_TWO_FILES)

        with it("should list the copies whatever their local names, and pass once the work has one home"):
            self.pair.check()

        with it("should list them once, as one group"):
            expect(self.listed).to(equal([
                "Operations 'billing/invoice.py: Invoice.total', 'shipping/parcel.py: Parcel.cost' do the same work: their "
                "bodies match once their local names are set aside. Read whether they are one behaviour; if they are, give "
                "it one home and have the others call it."
            ]))

        with it("should list the group as a candidate for a judge, not a violation"):
            expect([violation.is_candidate for violation in _violations(self.fixture, _COPIES)]).to(equal([True]))

        with it("should not list one-line operations that read alike"):
            expect([said for said in self.listed if "number" in said or "label" in said]).to(equal([]))

        with it("should report a body copied word for word as a violation the graph decides, and list no group beside it"):
            expect([(violation.message, violation.is_candidate) for violation in _violations(self.copied, _COPIES)]).to(
                equal([("Operation 'total' duplicates the body of 'total'.", False)])
            )

    with context("about state handed down as parameters"):
        with before.all:
            self.pair = files_rule_pair(_HELD_STATE, examples.SESSION_HANDED_DOWN, examples.SESSION_HELD)

        with it("should list a parameter handed on unchanged to two other classes, and pass once the object holds it"):
            self.pair.check()

        with it("should list it once, on the operation that starts handing it down, with each operation it passes"):
            expect(_listed(_HELD_STATE, examples.SESSION_HANDED_DOWN)).to(equal([
                "Operation 'Desk.open' hands its parameter 'session' on unchanged to 2 other classes: Desk.open, Clerk.file, "
                "Archive.store. Read which object should hold the session, so the operations below it read it there."
            ]))

        with it("should not list a parameter one class hands between its own operations"):
            expect(_listed(_HELD_STATE, examples.SESSION_HANDED_WITHIN_ONE_CLASS)).to(equal([]))

        with it("should not list a parameter handed to the constructor of the object made for it"):
            expect(_listed(_HELD_STATE, examples.SESSION_HANDED_TO_A_CONSTRUCTOR)).to(equal([]))

        with it("should list a class every operation of which takes the same parameter"):
            expect(_listed(_HELD_STATE, examples.TICKET_TO_EVERY_OPERATION)).to(equal([
                "Every operation of 'Board' (3) takes 'ticket'. Read whether 'Board' is made for one ticket and should hold it."
            ]))

        with it("should not list the class once it holds what it was handed"):
            expect(_listed(_HELD_STATE, examples.TICKET_HELD)).to(equal([]))

    with context("about a second registry of the same classes"):
        with before.all:
            self.pair = files_rule_pair(_ONE_MODEL, examples.SECOND_REGISTRY, examples.ONE_REGISTRY)

        with it("should list the second list of classes another already holds, and pass once it reads the first"):
            self.pair.check()

        with it("should name both registries and the classes they share"):
            expect(_listed(_ONE_MODEL, examples.SECOND_REGISTRY)).to(equal([
                "'checks/registry.py' CHECKS and 'report/listing.py' LISTED hold the same classes: Alpha, Beta, Gamma. "
                "Read whether one is a second registry; if it is, read the classes from the other."
            ]))

        with it("should not list a list of exported names, or one that spells the classes' names as labels"):
            expect(_listed(_ONE_MODEL, examples.NAMES_EXPORTED_AND_SPELLED)).to(equal([]))

    with context("about two verbs for one concept"):
        with before.all:
            self.pair = files_rule_pair(_ONE_VERB, examples.TWO_VERBS_FOR_ORDER, examples.ONE_VERB_FOR_ORDER)

        with it("should list the operations that name one target with two verbs, and pass once they share one"):
            self.pair.check()

        with it("should name the operations, the target and the verbs"):
            expect(_listed(_ONE_VERB, examples.TWO_VERBS_FOR_ORDER)).to(equal([
                "Operations 'store/cart.py: Cart.get_order', 'store/till.py: Till.fetch_order' name one concept, 'order', with the verbs fetch, get. "
                "Read whether they do the same kind of work; if they do, use one verb."
            ]))

    with context("about a module card the code has moved on from"):
        with before.all:
            self.pair = files_rule_pair(_CARD, examples.CARD_BEHIND_THE_CODE, examples.CARD_MATCHING_THE_CODE)
            self.reported = _listed(_CARD, examples.CARD_BEHIND_THE_CODE)

        with it("should report the card, and pass once it names what the code holds"):
            self.pair.check()

        with it("should report a seam term no class of the module declares"):
            expect(self.reported).to(contain("Module 'shop' card names 'Basket' in its seam, which no class in the module declares."))

        with it("should report a dependency the code does not import"):
            expect(self.reported).to(contain("Module 'shop' card names the dependency 'stock', which its code does not import."))

        with it("should report a dependency that is no folder of the code"):
            expect(self.reported).to(contain("Module 'shop' card names 'ledger/books', which is no folder of the code."))

        with it("should not report a card whose module declares no code yet, which its seam is written ahead of"):
            expect(_listed(_CARD, examples.CARD_BEFORE_ANY_CODE)).to(equal([]))

        with it("should read a dependency's path from the module's own folder too"):
            expect(_listed(_CARD, examples.CARD_NAMING_ITS_OWN_PACKAGE)).to(equal([]))

        with it("should report a module the code imports that the card does not name"):
            expect(self.reported).to(contain("Module 'shop' imports 'tax', which its card does not name among its dependencies."))
