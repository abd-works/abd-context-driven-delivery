"""BDD development — the roots a fidelity proposes for the pieces a ticket works on."""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import contain, equal, expect
from mamba import after, before, context, description, it

from space.session.session_roots_examples import RefundOrderSession


# (E) Guide Work Through Practices On Board
# (S) Person --> Choose Session And Practice Roots
with description("a fidelity's proposed roots"):
    with before.each:
        self.refund = RefundOrderSession()
        self.session = self.refund.session
        self.proposed = lambda practice, fidelity: self.refund.output(practice, fidelity).proposed_roots
        self.changed = self.refund.changed

    with after.each:
        self.refund.close()

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

        # An epic that holds its stories directly has no sub-epic folder, so the epic's folder is the piece.
        with it("should propose the epic's folder for a story test of a story directly under an epic"):
            changed = self.changed("story_tests/fulfil-order/pack-order/pack_order_story.test.py", "story_tests/fulfil-order/fulfil-order.story.shared.py")
            expect(self.proposed("stories", "acceptance_tests").holding(changed)).to(equal(["story_tests/fulfil-order"]))

        with it("should propose nothing for a file the fidelity does not write"):
            holding = self.proposed("stories", "scenarios").holding(self.changed("src/orders/refund/refund_policy.py"))
            expect(holding).to(equal([]))

        # An aggregate's folder is DDD's piece; Clean Engineering's code is the package that implements it.
        with it("should leave the aggregate's code to DDD for Clean Engineering's code"):
            holding = self.proposed("clean_engineering", "code").holding(self.changed("domain/orders/refund/refund.py", "src/orders/refund/refund_policy.py"))
            expect(holding).to(equal(["src/orders/refund"]))

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
