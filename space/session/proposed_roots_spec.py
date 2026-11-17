"""BDD development — the roots a fidelity proposes for the pieces a ticket works on."""
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import contain, equal, expect
from mamba import after, before, context, description, it

import cdd_guidance.practices  # noqa: F401 - registers the practices with the practice catalogue
from harness.guidance.practice_catalogue import PRACTICE_CATALOGUE
from space.session import Sessions
from space.session.throwaway_project import ExampleHome

PRACTICE_CATALOGUE.create_all()

# One aggregate's pieces, Refund, and its neighbours': a session for Refund's ticket roots on Refund's folders alone.
# An aggregate's code carries its stereotype, which tells DDD the file is a domain's.
_AGGREGATES = {
    "domain/orders/refund/refund.py": "@aggregate_root\nclass Refund:\n    pass\n",
    "domain/orders/payment/payment.py": "@aggregate_root\nclass Payment:\n    pass\n",
}
_PROJECT_FILES = (
    "src/orders/refund/refund_policy.py",
    "src/orders/payment/charge.py",
    "story_tests/manage-orders/refund-order/refund_order_story.test.md",
    "story_tests/manage-orders/refund-order/refund-order.story.shared.py",
    "story_tests/manage-orders/refund-order/issue-refund/issue_refund_story.test.py",
    "story_tests/manage-orders/place-order/place_order_story.test.md",
)


# (E) Guide Work Through Practices On Board
# (S) Person --> Choose Session And Practice Roots
with description("a fidelity's proposed roots"):
    with before.each:
        self.home = ExampleHome()
        self.repo = Path(tempfile.mkdtemp())
        for file, source in {**{file: "x = 1\n" for file in _PROJECT_FILES}, **_AGGREGATES}.items():
            (self.repo / file).parent.mkdir(parents=True, exist_ok=True)
            (self.repo / file).write_text(source, encoding="utf-8")
        Sessions(self.repo).switch("refund-order", None)
        self.session = Sessions.of_project(self.repo).current()
        self.proposed = lambda practice, fidelity: (
            self.session.practice(practice).of_fidelity(self.session.practice(practice).fidelities.entries[fidelity]).proposed_roots
        )
        self.changed = lambda *files: [self.repo / file for file in files]

    with after.each:
        self.home.close()

    with context("for the files the ticket's branch changed"):
        with it("should propose the aggregate's folder for the DDD model"):
            holding = self.proposed("ddd", "model").holding(self.changed("domain/orders/refund/refund.py"))
            expect(holding).to(equal(["domain/orders/refund"]))

        with it("should propose the aggregate's folder for the DDD tactics, which write a folder per aggregate"):
            holding = self.proposed("ddd", "tactics").holding(self.changed("domain/orders/refund/refund.py"))
            expect(holding).to(equal(["domain/orders/refund"]))

        with it("should propose the package for Clean Engineering's code"):
            holding = self.proposed("clean_engineering", "code").holding(self.changed("src/orders/refund/refund_policy.py"))
            expect(holding).to(equal(["src/orders/refund"]))

        with it("should propose the sub-epic's folder for a story test in a story's own folder"):
            changed = self.changed("story_tests/manage-orders/refund-order/issue-refund/issue_refund_story.test.py", "story_tests/manage-orders/refund-order/refund-order.story.shared.py")
            expect(self.proposed("stories", "acceptance_tests").holding(changed)).to(equal(["story_tests/manage-orders/refund-order"]))

        with it("should propose the sub-epic's folder for its scenarios"):
            holding = self.proposed("stories", "scenarios").holding(self.changed("story_tests/manage-orders/refund-order/refund_order_story.test.md"))
            expect(holding).to(equal(["story_tests/manage-orders/refund-order"]))

        with it("should propose nothing for a file the fidelity does not write"):
            holding = self.proposed("stories", "scenarios").holding(self.changed("src/orders/refund/refund_policy.py"))
            expect(holding).to(equal([]))

        with it("should leave test code out of Clean Engineering's code"):
            holding = self.proposed("clean_engineering", "code").holding(self.changed("story_tests/manage-orders/refund-order/refund-order.story.shared.py"))
            expect(holding).to(equal([]))

    with context("for the names the ticket gives"):
        with it("should propose the folder of the aggregate named, and not its neighbour's, for the DDD model"):
            expect(self.proposed("ddd", "model").named(["Refund"])).to(equal(["domain/orders/refund"]))

        with it("should propose the sub-epic named, and not its sibling, for the scenarios"):
            expect(self.proposed("stories", "scenarios").named(["refund"])).to(equal(["story_tests/manage-orders/refund-order"]))

        with it("should propose the package named for Clean Engineering's code"):
            expect(self.proposed("clean_engineering", "code").named(["refund"])).to(contain("src/orders/refund"))

        with it("should propose nothing for no names"):
            expect(self.proposed("ddd", "model").named([])).to(equal([]))

    with context("that an agent asks a fidelity for the roots it proposes"):
        with it("should answer the pieces the names name, in a project whose branch changed nothing"):
            scenarios = self.session.practice("stories").of_fidelity(self.session.practice("stories").fidelities.entries["scenarios"])
            expect(scenarios.propose_roots(["Refund"])).to(equal(["story_tests/manage-orders/refund-order"]))
