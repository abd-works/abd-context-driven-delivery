"""BDD spec for practices/bdd/bdd.py — Bdd toolset CE delegation.
"""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("cdd_guidance/practices", "tools"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be_a, be_true, contain, equal, expect, raise_error
from mamba import context, description, it

from cdd_guidance.practices.bdd.bdd import Bdd
from cdd_guidance.practices.clean_engineering.clean_engineering import CleanEngineering
from harness.agent_tools.agent_tools import AgentInstructions
from harness.guidance.practice_catalogue import PracticeCatalogue


def _expanded(bdd, action_name):
    """Expand action body with a live Bdd instance and return all prose joined."""
    func = getattr(type(bdd), action_name)
    body = AgentInstructions.for_callable(func, bdd)
    return "\n".join(body.prompt)


def _bdd():
    """Bdd at development fidelity, made with its set, so it holds the Clean Engineering companion of that set."""
    return PracticeCatalogue.create("bdd", fidelity="development")


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
                companion = PracticeCatalogue.create("bdd", fidelity="behavior").fidelities.current.clean_engineering
                expect(companion.name).to(equal("model"))

        with context("with development fidelity"):
            with it("should treat the code fidelity as the companion"):
                companion = PracticeCatalogue.create("bdd", fidelity="development").fidelities.current.clean_engineering
                expect(companion.name).to(equal("code"))

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
                expect(name in practice.tools).to(equal(False))

    with context("whose render tool is called"):
        with it("should render a sketch to python"):
            result = Bdd().render(
                "python",
                "a cart\n  that has been created\n    it should hold no items\n",
                source="markdown",
            )
            expect(result).to(be_a(dict))
            expect(str(result.get("content"))).to(contain("description"))

    with context("that reads a spec file into the graph"):
        with it("should read a Python spec with its Python format"):
            expect(type(Bdd().format_for(Path("cart_spec.py"))).__name__).to(equal("PythonBddModel"))

        with it("should read a JavaScript spec with its TypeScript format"):
            expect(type(Bdd().format_for(Path("cart.spec.js"))).__name__).to(equal("TypeScriptBddModel"))
