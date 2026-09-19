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
from tools.diagnose.diagnose import Diagnose


def _expanded(bdd, action_name):
    """Expand action body with a live Bdd instance and return all prose joined."""
    func = getattr(type(bdd), action_name)
    body = AgentInstructions.for_callable(func, bdd)
    return "\n".join(body.prompt)


def _bdd():
    return Bdd(fidelity="development", path="practices/bdd")


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
            with it("should return a CleanEngineering instance at model fidelity"):
                ce = Bdd(fidelity="behavior").ce()
                expect(ce).to(be_a(CleanEngineering))
                expect(ce.fidelities.current.fidelity).to(equal("model"))

        with context("with development fidelity"):
            with it("should return a CleanEngineering instance at code fidelity"):
                ce = Bdd(fidelity="development").ce()
                expect(ce).to(be_a(CleanEngineering))
                expect(ce.fidelities.current.fidelity).to(equal("code"))

        with context("with a path set"):
            with it("should carry the same path to the CE companion"):
                ce = Bdd(fidelity="behavior", path="practices/bdd").ce()
                expect(ce.path).to(equal("practices/bdd"))

        with context("with a session set"):
            with it("should carry the same session name to the CE companion"):
                ce = Bdd(fidelity="development", session="satisfy").ce()
                expect(ce.workspace.current_work_session.name if ce.workspace.current_work_session else None).to(equal("satisfy"))

        with it("should return a companion with mode set to tool"):
            ce = Bdd().ce()
            expect(ce.mode).to(equal("tool"))

    with context("that provides a Diagnose companion"):
        with it("should return a Diagnose instance"):
            expect(_bdd().diagnostic()).to(be_a(Diagnose))

    with context("whose guidance action is expanded"):
        with it("should include BDD test generation guidance"):
            prose = _expanded(_bdd(), "guidance")
            expect("SIGNATURE" in prose).to(be_true)

        with it("should tell the agent to call companion guidance and pass it to this action"):
            prose = _expanded(_bdd(), "guidance")
            expect("call guidance" in prose).to(be_true)
            expect("pass that companion to this action" in prose).to(be_true)
            expect("already knows what to do" in prose).to(be_true)
            expect("ce().generate()" in prose).to(equal(False))

        with it("should instruct the agent to scan production source for coverage gaps"):
            prose = _expanded(_bdd(), "guidance")
            expect("scan" in prose.lower()).to(be_true)

        with it("should tell the caller to pass the CE companion to this action as a separate run"):
            prose = _expanded(_bdd(), "guidance")
            expect("separate tools run" in prose).to(be_true)
            expect("Clean Engineering" in prose).to(be_true)

        with it("should NOT inline CleanEngineering generate instructions"):
            prose = _expanded(_bdd(), "guidance")
            expect("Deepen OO design" in prose).to(equal(False))

    with context("that does not own kit lifecycle actions"):
        with it("should not expose generate, validate, satisfy, repair, grill, sketch, or iterate"):
            host = _bdd()
            for name in (
                "generate",
                "validate",
                "satisfy",
                "repair",
                "grill",
                "sketch",
                "iterate",
            ):
                expect(name in host.agent_tools).to(equal(False))

    with context("whose transform tool is called"):
        with it("should delegate to CleanEngineering and return a dict"):
            result = Bdd().render("markdown", "class Foo:\n    pass\n", source="python")
            expect(result).to(be_a(dict))
