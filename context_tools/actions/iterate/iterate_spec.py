"""BDD spec for Iterator toolset + ActionExpander integration."""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities", "context_tools", "context_tools/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.modules.pop("iterate", None)

from expects import contain, equal, expect
from mamba import context, description, it

from primitives.actions.action import _ActionExpander
from iterate import Iterator


with description("an Iterator"):
    with context("that records an iterate tick"):
        with it("should return the iterate-tick marker"):
            # Arrange / Act
            result = Iterator().mark_iterate_tick()
            # Assert
            expect(result).to(equal("iterate-tick"))

    with context("with iterate_session in its manifest"):
        with it("should expose iterate_session as an action with no decorator chain"):
            entry = Iterator.manifest.signature["iterate_session"]
            expect(entry["kind"]).to(equal("action"))
            expect(entry.get("chain")).to(equal(None))

    with context("with the iterate_session action body"):
        with it("should require one scan and one fix pass with no rescan"):
            iterator = Iterator()
            body = _ActionExpander.instance().parse_body(
                Iterator.iterate_session, iterator
            )
            joined = "\n".join(body.prose_parts)
            expect(joined).to(contain("one fix"))
            expect(joined).to(contain("Do NOT re-scan"))

        with it("should forbid dumping the whole artifact in one tick"):
            iterator = Iterator()
            body = _ActionExpander.instance().parse_body(
                Iterator.iterate_session, iterator
            )
            joined = "\n".join(body.prose_parts)
            expect(joined).to(contain("DEFECT"))
            expect(joined).to(contain("ONLY that unlocked slice"))
            expect(joined).to(contain("Do not chain ticks"))
            expect(joined).to(contain("Hard gate"))
            expect(joined).to(contain("Ask ONE question at a time"))


class _ContextTool:
    def __init__(self, steps: list[str]) -> None:
        self.steps = steps
        self.workspace = self
        self.decisions = self

    def open(self) -> None:
        self.steps.append("open")

    def record_decisions_session(self) -> None:
        self.steps.append("record_decisions")

    def generate(self) -> str:
        self.steps.append("generate")
        return "ok"


class _Iterator(Iterator):
    def __init__(self, steps: list[str]) -> None:
        self.steps = steps

    def iterate_session(self, plan: str = "") -> str:
        self.steps.append("iterate_session")
        return "ok"


with description("an iterate action"):
    with context("that is given one context tool"):
        with it("should open the workspace, record decisions, run iterate_session, and generate"):
            steps: list[str] = []
            _Iterator(steps).iterate(tools=[_ContextTool(steps)])
            expect(steps).to(
                equal(["open", "record_decisions", "iterate_session", "generate"])
            )
