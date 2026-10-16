"""given-names-complex-state-root-first does not require a repository or an aggregate-root word."""

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from expects import equal, expect
from mamba import description, it

from practices.stories.rules.scenarios import GivenNamesComplexStateRootFirst


class _Step:
    def __init__(self, name: str, keyword: str, node_type: str) -> None:
        self.type = node_type
        self.name = name
        self.data = {"keyword": keyword, "phase": "given" if node_type == "Given" else ""}


class _Context:
    def step_keyword(self, node) -> str:
        return node.data["keyword"]

    def step_text(self, node) -> str:
        return node.name


def _check(name: str, keyword: str, node_type: str = "Given") -> list[str]:
    return GivenNamesComplexStateRootFirst().check(_Step(name, keyword, node_type), _Context())


with description("given-names-complex-state-root-first"):
    with it("should accept an and that continues a given"):
        expect(_check("a validation code has been sent to the User", "and")).to(equal([]))

    with it("should accept a given that names no repository and no aggregate root"):
        expect(
            _check(
                "the customer already has a saved profile and a preferred language",
                "given",
            )
        ).to(equal([]))
