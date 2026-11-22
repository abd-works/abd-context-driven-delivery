"""Seeds for a session rooted on the pieces its ticket works on: the ticket refund-order, whose Refund aggregate sits
beside Payment's in a small project, one folder per aggregate, package and sub-epic."""

from __future__ import annotations

import tempfile
from pathlib import Path

import cdd_guidance.practices  # noqa: F401 - registers the practices with the practice catalogue
from harness.guidance.practice_catalogue import PRACTICE_CATALOGUE
from space.session import Sessions
from space.session.practices.practice_session_output import FidelitySessionOutput
from space.session.session import Session
from space.session.spec_support.throwaway_project import ExampleHome

PRACTICE_CATALOGUE.create_all()

# Seed: refund-order, the ticket whose session the examples set up.
REFUND_ORDER = "refund-order"
# Seed: the folders of Refund's pieces, one per practice that writes them, and of Payment's beside them.
REFUND_DOMAIN = "domain/orders/refund"
REFUND_CODE = "src/orders/refund"
REFUND_STORIES = "story_tests/manage-orders/refund-order"
PAYMENT_DOMAIN = "domain/orders/payment"
PAYMENT_CODE = "src/orders/payment"
PLACE_ORDER_STORIES = "story_tests/manage-orders/place-order"
# Seed: a sub-epic of another epic that holds a story test of the Refund aggregate, found after the roots are set.
RETURN_PARCEL_STORIES = "story_tests/ship-orders/return-parcel"
# An aggregate's code carries its stereotype, which tells DDD the file is a domain's.
REFUND_AGGREGATE = f"{REFUND_DOMAIN}/refund.py"
REFUND_POLICY = f"{REFUND_CODE}/refund_policy.py"
REFUND_SHARED_STORY = f"{REFUND_STORIES}/refund-order.story.shared.py"
REFUND_SCENARIOS = f"{REFUND_STORIES}/refund_order_story.test.md"
REFUND_STORY_TEST = f"{REFUND_STORIES}/issue-refund/issue_refund_story.test.py"
REFUND_ORDER_FILES = {
    REFUND_AGGREGATE: "@aggregate_root\nclass Refund:\n    pass\n",
    f"{PAYMENT_DOMAIN}/payment.py": "@aggregate_root\nclass Payment:\n    pass\n",
    REFUND_POLICY: "x = 1\n",
    f"{PAYMENT_CODE}/charge.py": "x = 1\n",
    REFUND_SCENARIOS: "x = 1\n",
    REFUND_SHARED_STORY: "x = 1\n",
    REFUND_STORY_TEST: "x = 1\n",
    f"{PLACE_ORDER_STORIES}/place_order_story.test.md": "x = 1\n",
    f"{RETURN_PARCEL_STORIES}/return-parcel.story.shared.py": "x = 1\n",
}
# Seed: the files refund-order's branch changed, one piece of Refund for each practice.
REFUND_ORDER_CHANGES = (REFUND_AGGREGATE, REFUND_POLICY, REFUND_SCENARIOS, REFUND_SHARED_STORY)
# The practices and fidelities refund-order's session roots, each by its practice's and its own name.
ROOTED_FIDELITIES = (("ddd", "model"), ("ddd", "tactics"), ("clean_engineering", "code"), ("stories", "scenarios"), ("stories", "acceptance_tests"))


class ChangedOnBranch:
    """What git answers for the files a session's branch changed, as a project with no clone cannot."""

    def __init__(self, repo: Path, files: tuple[str, ...]) -> None:
        self._changed = {(repo / file).resolve() for file in files}

    def files(self) -> set[Path]:
        return set(self._changed)


class RefundOrderSession:
    """refund-order's session in a project of its own, with a cdd home of its own; close it after the example."""

    def __init__(self, changed: tuple[str, ...] = ()) -> None:
        self.home = ExampleHome()
        self.repo = Path(tempfile.mkdtemp(prefix="refund-order-"))
        for file, source in REFUND_ORDER_FILES.items():
            (self.repo / file).parent.mkdir(parents=True, exist_ok=True)
            (self.repo / file).write_text(source, encoding="utf-8")
        Sessions(self.repo).switch(REFUND_ORDER, None)
        self.session: Session = Sessions.of_project(self.repo).current()
        self.session.session_files.branch_changes = ChangedOnBranch(self.repo, changed)

    def output(self, practice: str, fidelity: str) -> FidelitySessionOutput:
        """The session's output of fidelity, one of practice's by name."""
        guidance = self.session.practice(practice)
        return guidance.of_fidelity(guidance.fidelities.entries[fidelity])

    def roots(self, practice: str, fidelity: str) -> list[str]:
        """The folders fidelity writes under, each a path from the project."""
        return [root.resolve().relative_to(self.repo.resolve()).as_posix() for root in self.output(practice, fidelity).roots]

    def changed(self, *files: str) -> list[Path]:
        return [self.repo / file for file in files]

    def close(self) -> None:
        self.home.close()
