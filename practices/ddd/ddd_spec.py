"""BDD spec for practices/ddd/ddd.py — Ddd toolset CE delegation.
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

from expects import be_a, be_true, equal, expect, raise_error
from mamba import context, description, it

from practices.clean_engineering.clean_engineering import CleanEngineering
from practices.ddd.ddd import Ddd
from harness.agent_tools.agent_tools import AgentInstructions


class _DddSpecSupport:
    """Shared arrange helpers kept on a class (not module-level functions)."""

    def expanded(self, ddd: Ddd, action_name: str) -> str:
        func = getattr(type(ddd), action_name)
        body = AgentInstructions.for_callable(func, ddd)
        return "\n".join(body.prompt)

    def tool_steps(self, ddd: Ddd, action_name: str) -> tuple:
        func = getattr(type(ddd), action_name)
        body = AgentInstructions.for_callable(func, ddd)
        return body.tool_steps

    def ddd(self) -> Ddd:
        return Ddd(fidelity="bounded_context")


_support = _DddSpecSupport()


with description("a Ddd toolset"):
    with context("that is created"):
        with context("with discovery stage"):
            with it("should resolve to bounded_context and default to markdown format"):
                tool = Ddd(stage="discovery")
                expect(tool.fidelities.current.fidelity).to(equal("bounded_context"))
                expect(tool.format).to(equal("markdown"))

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

    with context("whose generate default working folder is src"):
        with it("should keep src as the generate default"):
            expect(Ddd().default_workspace_folder).to(equal("src"))

    with context("that provides a CleanEngineering companion"):
        with context("with bounded_context fidelity"):
            with it("should treat the modules fidelity as the companion"):
                companion = Ddd(fidelity="bounded_context").fidelities.current.clean_engineering
                expect(companion.fidelity).to(equal("modules"))

        with context("with building_blocks fidelity"):
            with it("should treat the model fidelity as the companion"):
                companion = Ddd(fidelity="building_blocks").fidelities.current.clean_engineering
                expect(companion.fidelity).to(equal("model"))

        with context("with tactics fidelity"):
            with it("should treat the code fidelity as the companion"):
                companion = Ddd(fidelity="tactics").fidelities.current.clean_engineering
                expect(companion.fidelity).to(equal("code"))

    with context("whose contexts instruction is expanded"):
        with it("should include the experts-words-preferred rule slug"):
            prose = Ddd().scoped_markdown()
            expect("experts-words-preferred" in prose).to(be_true)

        with it("should include the bc-by-lifecycle-not-ui-themes rule slug"):
            prose = Ddd().scoped_markdown()
            expect("bc-by-lifecycle-not-ui-themes" in prose).to(be_true)

        with it("should include the repository-is-collection-lifecycle rule slug"):
            prose = Ddd().scoped_markdown()
            expect("repository-is-collection-lifecycle" in prose).to(be_true)

        with it("should include the shared-identity-is-generalisation rule slug"):
            prose = Ddd().scoped_markdown()
            expect("shared-identity-is-generalisation" in prose).to(be_true)

        with it("should include the hang-deps-on-owning-bc rule slug"):
            prose = Ddd().scoped_markdown()
            expect("hang-deps-on-owning-bc" in prose).to(be_true)

        with it("should include the user-facing-system-first rule slug"):
            prose = Ddd().scoped_markdown()
            expect("user-facing-system-first" in prose).to(be_true)

        with it("should include the context-tree-bc-aggregate-concept rule slug"):
            prose = Ddd().scoped_markdown()
            expect("context-tree-bc-aggregate-concept" in prose).to(be_true)

        with it("should include the link-arrow-target rule slug"):
            prose = Ddd().scoped_markdown()
            expect("link-arrow-target" in prose).to(be_true)

        with it("should name the bounded_context fidelity"):
            prose = Ddd().scoped_markdown()
            expect("bounded_context" in prose).to(be_true)

    with context("that does not own kit lifecycle actions"):
        with it("should not expose generate, validate, satisfy, repair, grill, sketch, iterate, or document"):
            practice = _support.ddd()
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
                expect(name in practice.agent_tools).to(equal(False))

    with context("whose guidance action is expanded"):
        with it("should include the Clean Engineering companion's instructions"):
            prose = _support.expanded(_support.ddd(), "guidance")
            expect("independent modules" in prose).to(be_true)

        with it("should NOT inline CleanEngineering generate instructions"):
            prose = _support.expanded(_support.ddd(), "guidance")
            expect("Deepen OO design" in prose).to(equal(False))

    with context("whose transform tool is called"):
        with it("should delegate to CleanEngineering and return a dict"):
            result = Ddd().render("markdown", "class Foo:\n    pass\n", source="python")
            expect(result).to(be_a(dict))
            expect(result["format"]).to(equal("markdown"))
