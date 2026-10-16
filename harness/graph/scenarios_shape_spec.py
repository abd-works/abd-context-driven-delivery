"""scenarios-shape accepts a Given on the scenario or on its story background."""

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from expects import equal, expect
from mamba import description, it

from practices.stories.rules.scenarios import ScenariosShape


class _Node:
    def __init__(self, type: str, name: str, phase: str = "") -> None:
        self.type = type
        self.name = name
        self.data = {"phase": phase, "keyword": phase} if phase else {}
        self.parent = None


class _Context:
    def __init__(self, links: dict) -> None:
        self._links = links

    def children(self, node, edge_kind: str) -> list:
        return self._links.get((id(node), edge_kind), [])

    def node_data(self, node) -> dict:
        return node.data

    def step_keyword(self, node) -> str:
        return str(node.data.get("keyword") or "")


def _step(phase: str) -> _Node:
    return _Node(phase[:1].upper() + phase[1:], f"{phase} the account", phase)


def _check(scenario_phases: list[str], background_phases: list[str] | None) -> list[str]:
    scenario = _Node("Scenario", "Display Create Account")
    links = {(id(scenario), "steps"): [_step(phase) for phase in scenario_phases]}
    if background_phases is not None:
        story = _Node("Story", "Create Account")
        background = _Node("Background", "each")
        scenario.parent = story
        links[(id(story), "background")] = [background]
        links[(id(background), "steps")] = [_step(phase) for phase in background_phases]
    return ScenariosShape().check(scenario, _Context(links))


with description("scenarios-shape"):
    with it("should accept when and then when the background has a given"):
        expect(_check(["when", "then"], ["given"])).to(equal([]))

    with it("should accept a given on the scenario"):
        expect(_check(["given", "when", "then"], None)).to(equal([]))

    with it("should flag a missing given when the background has none"):
        expect(_check(["when", "then"], [])).to(equal([
            "Scenario 'Display Create Account' is missing required phase(s): Given."
        ]))

    with it("should flag a missing given when there is no background"):
        expect(_check(["when", "then"], None)).to(equal([
            "Scenario 'Display Create Account' is missing required phase(s): Given."
        ]))
