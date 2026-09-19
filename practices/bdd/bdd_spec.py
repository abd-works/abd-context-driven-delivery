"""BDD spec for practices/bdd/bdd.py — Bdd toolset CE delegation.
"""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("practices", "harness", "tools"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be_a, be_true, contain, equal, expect, raise_error
from mamba import context, description, it

from practices.bdd.bdd import Bdd
from practices.clean_engineering.clean_engineering import CleanEngineering
from harness.agent_tools.agent_tools import AgentInstructions


def _expanded(bdd, action_name):
    """Expand action body with a live Bdd instance and return all prose joined."""
    func = getattr(type(bdd), action_name)
    body = AgentInstructions.for_callable(func, bdd)
    return "\n".join(body.prompt)


def _bdd():
    return Bdd(fidelity="development")


with description("a Bdd toolset"):
    with context("that is created"):
        with context("with behavior fidelity"):
            with it("should default to python format"):
                expect(Bdd(fidelity="behavior").format).to(equal("python"))

        with context("with development fidelity"):
            with it("should default to python format"):
                expect(Bdd(fidelity="development").format).to(equal("python"))

        with context("with an unsupported format"):
            with it("should raise ValueError"):
                expect(lambda: Bdd(fidelity="behavior", format="drawio")).to(raise_error(ValueError))

    with context("that provides a CleanEngineering companion"):
        with context("with behavior fidelity"):
            with it("should treat the model fidelity as the companion"):
                companion = Bdd(fidelity="behavior").fidelities.current.clean_engineering
                expect(companion.fidelity).to(equal("model"))

        with context("with development fidelity"):
            with it("should treat the code fidelity as the companion"):
                companion = Bdd(fidelity="development").fidelities.current.clean_engineering
                expect(companion.fidelity).to(equal("code"))

    with context("whose guidance action is expanded"):
        with it("should include the Clean Engineering companion's instructions"):
            prose = _expanded(_bdd(), "guidance")
            expect(prose).to(contain("Write working production code"))

        with it("should instruct the agent to scan production source for coverage gaps"):
            prose = _expanded(_bdd(), "guidance")
            expect("scan" in prose.lower()).to(be_true)

        with it("should NOT inline CleanEngineering generate instructions"):
            prose = _expanded(_bdd(), "guidance")
            expect("Deepen OO design" in prose).to(equal(False))

    with context("that does not own kit lifecycle actions"):
        with it("should not expose generate, validate, satisfy, repair, grill, sketch, or iterate"):
            practice = _bdd()
            for name in (
                "generate",
                "validate",
                "satisfy",
                "repair",
                "grill",
                "sketch",
                "iterate",
            ):
                expect(name in practice.agent_tools).to(equal(False))

    with context("whose transform tool is called"):
        with it("should delegate to CleanEngineering and return a dict"):
            result = Bdd().render("markdown", "class Foo:\n    pass\n", source="python")
            expect(result).to(be_a(dict))
