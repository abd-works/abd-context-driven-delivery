"""and-chaining accepts When followed by Then. It flags a When that never reaches a Then."""

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from expects import equal, expect
from mamba import description, it

from practices.stories.rules.scenarios import AndChaining


class _Step:
    def __init__(self, phase: str, name: str) -> None:
        self.type = phase[:1].upper() + phase[1:]
        self.name = name
        self.data = {"phase": phase, "keyword": phase}


class _Context:
    def __init__(self, steps: list[_Step]) -> None:
        self._steps = steps

    def story_model(self):
        return None

    def children(self, node, edge_kind: str) -> list:
        return self._steps if edge_kind == "steps" else []

    def node_data(self, node) -> dict:
        return node.data

    def step_keyword(self, node) -> str:
        return node.data["keyword"]


class _Scenario:
    type = "Scenario"
    name = "Enter validation code"


def _check(*phases: str) -> list[str]:
    steps = [_Step(phase, f"{phase} the account") for phase in phases]
    return AndChaining().check(_Scenario(), _Context(steps))


with description("and-chaining"):
    with it("should accept given, when, then"):
        expect(_check("given", "when", "then")).to(equal([]))

    with it("should accept when then with no given"):
        expect(_check("when", "then")).to(equal([]))

    with it("should accept when then continued with and"):
        expect(_check("when", "then", "and", "and")).to(equal([]))

    with it("should accept a second when after a then"):
        expect(_check("given", "when", "then", "when", "then")).to(equal([]))

    with it("should flag a when that has no then"):
        expect(_check("given", "when")).to(equal([
            "Scenario 'Enter validation code' has a When with no Then; add the result or chain it with And."
        ]))

    with it("should flag two when steps with no then between them"):
        expect(_check("given", "when", "when", "then")).to(equal([
            "Scenario 'Enter validation code' has two When steps with no Then between them; continue that interaction with And."
        ]))
