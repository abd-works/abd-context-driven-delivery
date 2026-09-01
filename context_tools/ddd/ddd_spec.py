"""BDD spec for context_tools/ddd/ddd.py — Ddd toolset CE delegation.
# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
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
        with context("with scaffold fidelity"):
            with it("should default to markdown format"):
                expect(Ddd(fidelity="scaffold").format).to(equal("markdown"))

        with context("with building_blocks fidelity"):
            with it("should default to markdown format"):
                expect(Ddd(fidelity="building_blocks").format).to(equal("markdown"))

        with context("with tactics fidelity"):
            with it("should default to python format"):
                expect(Ddd(fidelity="tactics").format).to(equal("python"))

        with context("with an unsupported fidelity"):
            with it("should raise ValueError"):
                expect(lambda: Ddd(fidelity="modules")).to(raise_error(ValueError))

        with context("with an unsupported format"):
            with it("should raise ValueError"):
                expect(
                    lambda: Ddd(fidelity="bounded_context", format="yaml")
                ).to(raise_error(ValueError))

    with context("whose document action chooses a working folder"):
        with it("should keep src as the generate default"):
            expect(Ddd().workspace.default_workspace_folder).to(equal("src"))
            expect(Path(Ddd().workspace.path).name).to(equal("src"))

        with it("should switch the working folder to domain"):
            ddd = Ddd()
            ddd.apply_document_workspace_default()
            expect(ddd.workspace.default_workspace_folder).to(equal("domain"))
            expect(Path(ddd.workspace.path).name).to(equal("domain"))

        with it("should keep an explicit path"):
            ddd = Ddd(path="wraps")
            ddd.apply_document_workspace_default()
            expect(ddd.workspace.path).to(equal("wraps"))

        with it("should keep an overwritten default_workspace_folder"):
            ddd = Ddd()
            ddd.workspace.default_workspace_folder = "packages"
            ddd.workspace.path = str(Path(ddd.workspace.workspace_root) / "packages")
            ddd.apply_document_workspace_default()
            expect(Path(ddd.workspace.path).name).to(equal("packages"))

        with it("should expose apply_document_workspace_default as a host tool"):
            expect("apply_document_workspace_default" in _support.ddd().tools).to(be_true)

        with it("should pass DDD's working path into CleanEngineering without changing CE's default"):
            ddd = Ddd()
            ddd.apply_document_workspace_default()
            ce = ddd.ce()
            expect(Path(ce.workspace.path).name).to(equal("domain"))
            expect(CleanEngineering.default_workspace_folder).to(equal("src"))

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

        with context("with tactics fidelity"):
            with it("should return a CleanEngineering instance at code fidelity"):
                ce = Ddd(fidelity="tactics").ce()
                expect(ce).to(be_a(CleanEngineering))
                expect(ce.fidelity).to(equal("code"))

        with context("with a path set"):
            with it("should carry the same path to the CE companion"):
                ce = Ddd(fidelity="bounded_context", path="context_tools/ddd").ce()
                expect(ce._raw_path).to(equal("context_tools/ddd"))

        with context("with a session set"):
            with it("should carry the same session name to the CE companion"):
                ce = Ddd(fidelity="tactics", session="satisfy").ce()
                expect(ce.workspace.current_work_session.name if ce.workspace.current_work_session else None).to(equal("satisfy"))

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

        with it("should include the bc-by-lifecycle-not-ui-themes rule slug"):
            prose = Ddd().contexts().expand()
            expect("bc-by-lifecycle-not-ui-themes" in prose).to(be_true)

        with it("should include the repository-is-collection-lifecycle rule slug"):
            prose = Ddd().contexts().expand()
            expect("repository-is-collection-lifecycle" in prose).to(be_true)

        with it("should include the shared-identity-is-generalisation rule slug"):
            prose = Ddd().contexts().expand()
            expect("shared-identity-is-generalisation" in prose).to(be_true)

        with it("should include the hang-deps-on-owning-bc rule slug"):
            prose = Ddd().contexts().expand()
            expect("hang-deps-on-owning-bc" in prose).to(be_true)

        with it("should include the user-facing-system-first rule slug"):
            prose = Ddd().contexts().expand()
            expect("user-facing-system-first" in prose).to(be_true)

        with it("should include the context-tree-bc-aggregate-concept rule slug"):
            prose = Ddd().contexts().expand()
            expect("context-tree-bc-aggregate-concept" in prose).to(be_true)

        with it("should include the link-arrow-target rule slug"):
            prose = Ddd().contexts().expand()
            expect("link-arrow-target" in prose).to(be_true)

        with it("should name the bounded_context fidelity"):
            prose = Ddd().contexts().expand()
            expect("bounded_context" in prose).to(be_true)

    with context("that does not own kit lifecycle actions"):
        with it("should not expose generate, validate, satisfy, repair, grill, sketch, iterate, or document"):
            host = _support.ddd()
            for name in (
                "generate",
                "validate",
                "satisfy",
                "repair",
                "grill",
                "sketch",
                "iterate",
                "document",
            ):
                expect(name in host.actions).to(equal(False))

    with context("whose guidance action is expanded"):
        with it("should tell the agent to call companion guidance and pass it to this action"):
            prose = _support.expanded(_support.ddd(), "guidance")
            expect("call guidance" in prose).to(be_true)
            expect("pass that companion to this action" in prose).to(be_true)
            expect("already knows what to do" in prose).to(be_true)
            expect("ce().generate()" in prose).to(equal(False))

        with it("should include the RED confirmation instruction"):
            prose = _support.expanded(_support.ddd(), "guidance")
            expect("RED" in prose).to(be_true)

        with it("should tell the agent to call diagnostic().diagnose() when a test keeps failing"):
            prose = _support.expanded(_support.ddd(), "guidance")
            expect("diagnostic().diagnose()" in prose).to(be_true)

        with it("should instruct the agent to scan production source for coverage gaps"):
            prose = _support.expanded(_support.ddd(), "guidance")
            expect("coverage gap" in prose.lower()).to(be_true)

        with it("should tell the caller to pass the CE companion to this action as a separate run"):
            prose = _support.expanded(_support.ddd(), "guidance")
            expect("separate tools run" in prose).to(be_true)
            expect("Clean Engineering" in prose).to(be_true)

        with it("should NOT inline CleanEngineering generate instructions"):
            prose = _support.expanded(_support.ddd(), "guidance")
            expect("Deepen OO design" in prose).to(equal(False))

    with context("whose transform tool is called"):
        with it("should delegate to CleanEngineering and return a dict"):
            result = Ddd().transform("python", "markdown", "class Foo:\n    pass\n")
            expect(result).to(be_a(dict))
            expect(result["format"]).to(equal("markdown"))
