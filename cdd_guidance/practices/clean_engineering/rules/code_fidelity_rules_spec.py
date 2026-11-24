"""A rule Clean Engineering states only at the code fidelity judges a class read at the code fidelity, one whose
operations have bodies, and leaves a class read at the model fidelity out, whatever format it is written in. A rule
stated at the model fidelity judges both."""

from pathlib import Path
import sys

_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import equal, expect
from mamba import before, context, description, it

from cdd_guidance.practices.clean_engineering.clean_engineering import CleanEngineering
from cdd_guidance.practices.clean_engineering.rules import BY_SLUG, RULES
from cdd_guidance.practices.clean_engineering.rules.rule_examples import MEASURES_CHOSEN, practice_from_files

# The rules the practice's document states at the code fidelity and at no other.
_CODE_ONLY = (
    "no-prototype-swapping", "keep-operations-small-focused", "simplify-control-flow", "use-exceptions-properly",
    "never-swallow-exceptions", "provide-meaningful-context", "prefer-instance-operations",
    "limit-paths-through-a-function", "keep-functions-readable", "limit-function-lines",
    "limit-class-complexity", "limit-class-methods", "keep-class-methods-sharing-data",
)
# The rules about use the practice's document states at the model fidelity, which judge a class at either fidelity.
_USE = (
    "delete-unused-classes", "delete-unused-operations", "check-use-the-graph-cannot-see",
    "make-module-only-operations-private", "connect-disconnected-classes", "merge-one-class-packages",
)
_METHODS = "".join(f"    def step_{index}(self) -> None:\n        ...\n\n" for index in range(31))
# A class of the model fidelity written in Python: 31 operations, a classmethod named current among them, a
# five-parameter operation, and no body anywhere.
_DECLARED_ONLY = (
    "class Board:\n"
    "    @classmethod\n    def current(cls) -> 'Board':\n        raise NotImplementedError\n\n"
    "    def place(self, sku: str, quantity: int, price: int, note: str, gift: bool) -> None:\n        ...\n\n" + _METHODS
)
# The same class once one operation has a body.
_WRITTEN = _DECLARED_ONLY.replace("    def step_0(self) -> None:\n        ...\n", "    def step_0(self) -> None:\n        self.started = True\n")


def _stated_at(fidelity: str) -> set[str]:
    return {rule.slug for rule in CleanEngineering(fidelity=fidelity).fidelities.current.rules}


with description("a rule Clean Engineering states only at the code fidelity") as self:
    with before.all:
        self.declared_only = practice_from_files({**MEASURES_CHOSEN, "board/board.py": _DECLARED_ONLY})
        self.written = practice_from_files({**MEASURES_CHOSEN, "board/board.py": _WRITTEN})

    with it("should be each graph rule the document states at code and at neither modules nor the model"):
        checked = {rule.slug for rule in RULES}
        only_code = (_stated_at("code") - _stated_at("model") - _stated_at("modules")) & checked
        expect(sorted(only_code - {"source-parses"})).to(equal(sorted(_CODE_ONLY)))

    with it("should say on its check that it judges the code fidelity alone"):
        expect([BY_SLUG[slug].code_fidelity_only for slug in _CODE_ONLY]).to(equal([True] * len(_CODE_ONLY)))

    with context("on a class whose operations have no bodies"):
        # Each rule's hits run every rule of the practice again, so the code-only rules are run once, before the example.
        with before.all:
            self.reported = {slug: self.declared_only.hits(BY_SLUG[slug]) for slug in _CODE_ONLY}

        with it("should report nothing, since a class at the model fidelity has no body to judge"):
            expect({slug: hits for slug, hits in self.reported.items() if hits}).to(equal({}))

    with context("on the same class once one operation has a body"):
        with it("should report the class for its 33 methods"):
            expect(self.written.hits(BY_SLUG["limit-class-methods"])).to(equal(["Class 'Board' has 33 methods, over the limit of 30. Group the methods by the data they use; each group that stands alone is a class."]))

        with it("should report its classmethod named current"):
            expect(len(self.written.hits(BY_SLUG["prefer-instance-operations"]))).to(equal(1))


with description("a rule Clean Engineering states at the model fidelity") as self:
    with it("should hold each rule about use"):
        expect(sorted(set(_USE) & _stated_at("model"))).to(equal(sorted(_USE)))

    with context("on a class whose operations have no bodies"):
        with it("should report the class nothing uses, since a design nobody uses is one to fix"):
            declared_only = practice_from_files({"board/board.py": _DECLARED_ONLY})
            expect(len(declared_only.hits(BY_SLUG["delete-unused-classes"]))).to(equal(1))

        with it("should still report an operation that takes five parameters"):
            declared_only = practice_from_files({"board/board.py": _DECLARED_ONLY})
            expect(declared_only.hits(BY_SLUG["limit-operation-parameters"])).to(equal(["Operation 'place' takes 5 parameters (maximum 3, excluding self)."]))
