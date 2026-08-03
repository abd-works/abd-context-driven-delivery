"""BDD spec for context_tools/bdd/bdd.py — Bdd toolset CE delegation.
# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("context_tools", "primitives", "utilities"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be_a, be_true, contain, equal, expect, raise_error
from mamba import context, description, it

from context_tools.bdd.bdd import Bdd
from context_tools.clean_engineering.clean_engineering import CleanEngineering
from primitives.actions.action import _ActionExpander
from utilities.diagnose.diagnose import Diagnose


def _expanded(bdd, action_name):
    """Expand action body with a live Bdd instance and return all prose joined."""
    func = getattr(type(bdd), action_name)
    body = _ActionExpander.instance().parse_body(func, bdd)
    return "\n".join(body.prose_parts)


def _bdd():
    return Bdd(fidelity="development", path="context_tools/bdd")


with description("a Bdd toolset"):
    with context("that is created"):
        with context("with behavior fidelity"):
            with it("should default to python format"):
                expect(Bdd(fidelity="behavior").format).to(equal("python"))

        with context("with development fidelity"):
            with it("should default to python format"):
                expect(Bdd(fidelity="development").format).to(equal("python"))

        with context("with modules fidelity"):
            with it("should default to markdown format"):
                expect(Bdd(fidelity="modules").format).to(equal("markdown"))

        with context("with an unsupported format"):
            with it("should raise ValueError"):
                expect(lambda: Bdd(fidelity="behavior", format="drawio")).to(raise_error(ValueError))

    with context("that provides a CleanEngineering companion"):
        with context("with modules fidelity"):
            with it("should return a CleanEngineering instance at modules fidelity"):
                ce = Bdd(fidelity="modules").ce()
                expect(ce).to(be_a(CleanEngineering))
                expect(ce.fidelity).to(equal("modules"))

        with context("with behavior fidelity"):
            with it("should return a CleanEngineering instance at model fidelity"):
                ce = Bdd(fidelity="behavior").ce()
                expect(ce).to(be_a(CleanEngineering))
                expect(ce.fidelity).to(equal("model"))

        with context("with development fidelity"):
            with it("should return a CleanEngineering instance at code fidelity"):
                ce = Bdd(fidelity="development").ce()
                expect(ce).to(be_a(CleanEngineering))
                expect(ce.fidelity).to(equal("code"))

        with context("with a path set"):
            with it("should carry the same path to the CE companion"):
                ce = Bdd(fidelity="behavior", path="context_tools/bdd").ce()
                expect(ce._raw_path).to(equal("context_tools/bdd"))

        with context("with a session set"):
            with it("should carry the same session name to the CE companion"):
                ce = Bdd(fidelity="development", session="satisfy").ce()
                expect(ce.workspace.name).to(equal("satisfy"))

        with it("should return a companion with mode set to tool"):
            ce = Bdd().ce()
            expect(ce.mode).to(equal("tool"))

    with context("that provides a Diagnose companion"):
        with it("should return a Diagnose instance"):
            expect(_bdd().diagnostic()).to(be_a(Diagnose))

    with context("whose generate action is expanded"):
        with it("should include BDD test generation guidance"):
            prose = _expanded(_bdd(), "generate")
            expect("SIGNATURE" in prose).to(be_true)

        with it("should include the RED before GREEN cycle instruction"):
            prose = _expanded(_bdd(), "generate")
            expect("RED" in prose).to(be_true)

        with it("should tell the agent to call ce().generate() when BDD is complete"):
            prose = _expanded(_bdd(), "generate")
            expect("ce().generate()" in prose).to(be_true)

        with it("should instruct the agent to scan production source for coverage gaps"):
            prose = _expanded(_bdd(), "generate")
            expect("scan" in prose.lower()).to(be_true)

        with it("should NOT inline CleanEngineering generate instructions"):
            prose = _expanded(_bdd(), "generate")
            expect("Deepen OO design" in prose).to(equal(False))

    with context("whose validate action is expanded"):
        with it("should include BDD validation context"):
            prose = _expanded(_bdd(), "validate")
            expect("Behavior-driven development" in prose).to(be_true)

        with it("should tell the agent to call ce().validate() when BDD validation passes"):
            prose = _expanded(_bdd(), "validate")
            expect("ce().validate()" in prose).to(be_true)

        with it("should NOT inline CleanEngineering validate instructions"):
            prose = _expanded(_bdd(), "validate")
            expect("Deepen OO design" in prose).to(equal(False))

    with context("whose satisfy action is expanded"):
        with it("should include the RED confirmation instruction"):
            prose = _expanded(_bdd(), "satisfy")
            expect("RED" in prose).to(be_true)

        with it("should include BDD behavior hierarchy rules"):
            prose = _expanded(_bdd(), "satisfy")
            expect("Behavior-driven development" in prose).to(be_true)

        with it("should tell the agent to call ce().satisfy() when BDD violations are resolved"):
            prose = _expanded(_bdd(), "satisfy")
            expect("ce().satisfy()" in prose).to(be_true)

        with it("should tell the agent to call diagnostic().diagnose() when a test keeps failing"):
            prose = _expanded(_bdd(), "satisfy")
            expect("diagnostic().diagnose()" in prose).to(be_true)

        with it("should list diagnose as a tool step without inlining the six phases"):
            func = getattr(type(_bdd()), "satisfy")
            body = _ActionExpander.instance().parse_body(func, _bdd())
            expect("diagnose" in body.tool_steps).to(be_true)
            prose = "\n".join(body.prose_parts)
            expect("Phase 1 - Build a feedback loop" in prose).to(equal(False))

        with it("should instruct the agent to scan production source for coverage gaps"):
            prose = _expanded(_bdd(), "satisfy")
            expect("coverage gap" in prose.lower()).to(be_true)

        with it("should NOT inline CleanEngineering satisfy instructions"):
            prose = _expanded(_bdd(), "satisfy")
            expect("Deepen OO design" in prose).to(equal(False))

    with context("whose iterate action is expanded"):
        with it("should tell the agent to call ce().iterate() after confirming RED"):
            prose = _expanded(_bdd(), "iterate")
            expect("ce().iterate()" in prose).to(be_true)

        with it("should tell the agent to call diagnostic().diagnose() when a test keeps failing"):
            prose = _expanded(_bdd(), "iterate")
            expect("diagnostic().diagnose()" in prose).to(be_true)

        with it("should list diagnose as a tool step without inlining the six phases"):
            func = getattr(type(_bdd()), "iterate")
            body = _ActionExpander.instance().parse_body(func, _bdd())
            expect("diagnose" in body.tool_steps).to(be_true)
            prose = "\n".join(body.prose_parts)
            expect("Phase 1 - Build a feedback loop" in prose).to(equal(False))

    with context("whose grill action is expanded"):
        with it("should tell the agent to call ce().grill() when BDD grill is complete"):
            prose = _expanded(_bdd(), "grill")
            expect("ce().grill()" in prose).to(be_true)

    with context("whose sketch action is expanded"):
        with it("should tell the agent to call ce().sketch() when BDD sketch is complete"):
            prose = _expanded(_bdd(), "sketch")
            expect("ce().sketch()" in prose).to(be_true)

    with context("whose repair action is expanded"):
        with it("should tell the agent to call ce().repair() when the BDD artifact is clean"):
            prose = _expanded(_bdd(), "repair")
            expect("ce().repair()" in prose).to(be_true)

    with context("whose transform tool is called"):
        with it("should delegate to CleanEngineering and return a dict"):
            result = Bdd().transform("python", "markdown", "class Foo:\n    pass\n")
            expect(result).to(be_a(dict))
