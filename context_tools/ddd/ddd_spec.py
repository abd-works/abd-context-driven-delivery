"""BDD spec for context_tools/ddd/ddd.py — Ddd toolset CE delegation.
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

from expects import be_a, be_true, equal, expect, raise_error
from mamba import context, description, it

from context_tools.clean_engineering.clean_engineering import CleanEngineering
from context_tools.ddd.ddd import Ddd
from primitives.actions.action import _ActionExpander
from utilities.diagnose.diagnose import Diagnose


class _DddSpecSupport:
    """Shared arrange helpers kept on a class (not module-level functions)."""

    def expanded(self, ddd: Ddd, action_name: str) -> str:
        func = getattr(type(ddd), action_name)
        body = _ActionExpander.instance().parse_body(func, ddd)
        return "\n".join(body.prose_parts)

    def tool_steps(self, ddd: Ddd, action_name: str) -> tuple:
        func = getattr(type(ddd), action_name)
        body = _ActionExpander.instance().parse_body(func, ddd)
        return body.tool_steps

    def ddd(self) -> Ddd:
        return Ddd(fidelity="bounded_context", path="context_tools/ddd")


_support = _DddSpecSupport()


with description("a Ddd toolset"):
    with context("that is created"):
        with context("with bounded_context fidelity"):
            with it("should default to markdown format"):
                expect(Ddd(fidelity="bounded_context").format).to(equal("markdown"))

        with context("with building_blocks fidelity"):
            with it("should default to markdown format"):
                expect(Ddd(fidelity="building_blocks").format).to(equal("markdown"))

        with context("with code fidelity"):
            with it("should default to python format"):
                expect(Ddd(fidelity="code").format).to(equal("python"))

        with context("with an unsupported fidelity"):
            with it("should raise ValueError"):
                expect(lambda: Ddd(fidelity="modules")).to(raise_error(ValueError))

        with context("with an unsupported format"):
            with it("should raise ValueError"):
                expect(
                    lambda: Ddd(fidelity="bounded_context", format="yaml")
                ).to(raise_error(ValueError))

    with context("that provides a CleanEngineering companion"):
        with context("with bounded_context fidelity"):
            with it("should return a CleanEngineering instance at modules fidelity"):
                ce = Ddd(fidelity="bounded_context").ce()
                expect(ce).to(be_a(CleanEngineering))
                expect(ce.fidelity).to(equal("modules"))

        with context("with building_blocks fidelity"):
            with it("should return a CleanEngineering instance at model fidelity"):
                ce = Ddd(fidelity="building_blocks").ce()
                expect(ce).to(be_a(CleanEngineering))
                expect(ce.fidelity).to(equal("model"))

        with context("with code fidelity"):
            with it("should return a CleanEngineering instance at code fidelity"):
                ce = Ddd(fidelity="code").ce()
                expect(ce).to(be_a(CleanEngineering))
                expect(ce.fidelity).to(equal("code"))

        with context("with a path set"):
            with it("should carry the same path to the CE companion"):
                ce = Ddd(fidelity="bounded_context", path="context_tools/ddd").ce()
                expect(ce._raw_path).to(equal("context_tools/ddd"))

        with context("with a session set"):
            with it("should carry the same session name to the CE companion"):
                ce = Ddd(fidelity="code", session="satisfy").ce()
                expect(ce.workspace.name).to(equal("satisfy"))

        with it("should return a companion with mode set to tool"):
            ce = Ddd().ce()
            expect(ce.mode).to(equal("tool"))

    with context("that provides a diagnostic companion"):
        with it("should return a Diagnose instance"):
            expect(Ddd().diagnostic()).to(be_a(Diagnose))

    with context("whose contexts instruction is expanded"):
        with it("should include the experts-words-preferred rule slug"):
            prose = Ddd().contexts().expand()
            expect("experts-words-preferred" in prose).to(be_true)

        with it("should name the bounded_context fidelity"):
            prose = Ddd().contexts().expand()
            expect("bounded_context" in prose).to(be_true)

    with context("whose generate_output action is expanded"):
        with it("should tell the agent to call ce().generate()"):
            prose = _support.expanded(_support.ddd(), "generate_output")
            expect("ce().generate()" in prose).to(be_true)

        with it("should NOT inline CleanEngineering generate instructions"):
            prose = _support.expanded(_support.ddd(), "generate_output")
            expect("Deepen OO design" in prose).to(equal(False))

    with context("whose validate action is expanded"):
        with it("should include DDD validation context"):
            prose = _support.expanded(_support.ddd(), "validate")
            expect("bounded context" in prose.lower() or "bounded_context" in prose).to(
                be_true
            )

        with it("should tell the agent to call ce().validate() when DDD validation passes"):
            prose = _support.expanded(_support.ddd(), "validate")
            expect("ce().validate()" in prose).to(be_true)

        with it("should NOT inline CleanEngineering validate instructions"):
            prose = _support.expanded(_support.ddd(), "validate")
            expect("Deepen OO design" in prose).to(equal(False))

    with context("whose satisfy action is expanded"):
        with it("should include the RED confirmation instruction"):
            prose = _support.expanded(_support.ddd(), "satisfy")
            expect("RED" in prose).to(be_true)

        with it("should tell the agent to call ce().satisfy() when BDD violations are resolved"):
            prose = _support.expanded(_support.ddd(), "satisfy")
            expect("ce().satisfy()" in prose).to(be_true)

        with it("should tell the agent to call diagnostic().diagnose() when a test keeps failing"):
            prose = _support.expanded(_support.ddd(), "satisfy")
            expect("diagnostic().diagnose()" in prose).to(be_true)

        with it("should list diagnose as a tool step without inlining the six phases"):
            steps = _support.tool_steps(_support.ddd(), "satisfy")
            expect("diagnose" in steps).to(be_true)
            prose = _support.expanded(_support.ddd(), "satisfy")
            expect("Phase 1 - Build a feedback loop" in prose).to(equal(False))

        with it("should instruct the agent to scan production source for coverage gaps"):
            prose = _support.expanded(_support.ddd(), "satisfy")
            expect("coverage gap" in prose.lower()).to(be_true)

        with it("should NOT inline CleanEngineering satisfy instructions"):
            prose = _support.expanded(_support.ddd(), "satisfy")
            expect("Deepen OO design" in prose).to(equal(False))

    with context("whose repair action is expanded"):
        with it("should tell the agent to call ce().repair() when the DDD artifact is clean"):
            prose = _support.expanded(_support.ddd(), "repair")
            expect("ce().repair()" in prose).to(be_true)

    with context("whose transform tool is called"):
        with it("should delegate to CleanEngineering and return a dict"):
            result = Ddd().transform("python", "markdown", "class Foo:\n    pass\n")
            expect(result).to(be_a(dict))
            expect(result["format"]).to(equal("markdown"))
