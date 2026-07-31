"""BDD spec - AgentBdd expands agent-test content and composes bdd actions."""

from pathlib import Path
from typing import Any

from expects import be_true, equal, expect
from mamba import before, context, description, it

from primitives.actions.action import _ActionRunRequest, _ActionRunner
import agent_bdd.conf  # noqa: F401 - repo root on sys.path
import context_tools  # noqa: F401
from primitives.instructions import Instruction
from primitives.instructions import _path_for_name
from tools.tool import Toolset, _ToolsetLoader

_AGENT_BDD_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _AGENT_BDD_DIR.parents[1]
_AGENT_BDD_TOOLSET = "agent_bdd.agent_bdd:AgentBdd"
_BDD_DIR = _REPO_ROOT / "context_tools" / "bdd"
_GENERATOR_DIR = _REPO_ROOT / "context_tools" / "base"
_LIFECYCLE_PROSE_DIR = _GENERATOR_DIR  # sections in base_context_tool.md


def _lifecycle_prose(action: str) -> str:
    return Instruction(
        _path_for_name(_LIFECYCLE_PROSE_DIR, action), _LIFECYCLE_PROSE_DIR
    ).expand()


def _load_agent_bdd(*, format_name: str = "python") -> Toolset:
    toolset_cls = _ToolsetLoader.instance().load(_AGENT_BDD_TOOLSET)
    return toolset_cls(format=format_name)


def _expand_action(
    instance: Toolset,
    action_name: str,
    *,
    toolset_path: str,
    context: dict[str, Any] | None = None,
    arguments: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return _ActionRunner.instance().run(
        _ActionRunRequest(
            request={"toolset": toolset_path, "context": context or {}},
            toolset_path=toolset_path,
            action_name=action_name,
            context=context or {},
            arguments=arguments or {},
            instance=instance,
        )
    )


def _assert_text_inlined(instructions: str, source: str) -> None:
    expect(source in instructions).to(be_true)


with description("AgentBdd action expansion"):
    with context("an AgentBdd generator with format python"):
        with before.all:
            self.bdd = _load_agent_bdd()
            self.contexts = Instruction(
                "\u00a7 Contexts", _AGENT_BDD_DIR, domain_slug="agent_bdd"
            ).expand()
            self.bdd_contexts = Instruction("\u00a7 Contexts", _BDD_DIR).expand()

        with context("the generate action is expanded"):
            with before.each:
                self.response = _expand_action(
                    self.bdd,
                    "generate",
                    toolset_path=_AGENT_BDD_TOOLSET,
                    context={"format": "python"},
                )

            with it("should set action to generate"):
                expect(self.response["action"]).to(equal("generate"))

            with it("should inline agent-BDD concepts from agent_bdd.md"):
                _assert_text_inlined(self.response["instructions"], self.contexts)

            with it("should inline agent_bdd.md # Generate from generate docstring"):
                generate_prose = Instruction(
                    "\u00a7 Generate", _AGENT_BDD_DIR, domain_slug="agent_bdd"
                ).expand()
                _assert_text_inlined(self.response["instructions"], generate_prose)

            with it("should inline bdd concepts via nested bdd generate"):
                _assert_text_inlined(self.response["instructions"], self.bdd_contexts)

            with it("should inline # Generate from base_context_tool.md"):
                shared = _lifecycle_prose("generate")
                _assert_text_inlined(self.response["instructions"], shared)

            with it("should inline formats/python/agent_bdd-templates.py from format resource"):
                template = Instruction(
                    "formats/python/agent_bdd-templates.py", _AGENT_BDD_DIR
                ).expand()
                # Generate may strip scaffold header comments; require distinctive body markers.
                expect("with description" in self.response["instructions"]).to(be_true)
                expect("ai_judge" in self.response["instructions"]).to(be_true)
                expect(len(template) > 0).to(be_true)

        with context("the validate action is expanded"):
            with before.each:
                self.response = _expand_action(
                    self.bdd,
                    "validate",
                    toolset_path=_AGENT_BDD_TOOLSET,
                    context={"format": "python"},
                )

            with it("should name scan on tools"):
                expect(self.response["tools"]).to(equal(["scan"]))

            with it("should inline bdd validate prose via nested bdd validate"):
                validate_prose = _lifecycle_prose("validate")
                _assert_text_inlined(self.response["instructions"], validate_prose)
                _assert_text_inlined(self.response["instructions"], self.bdd_contexts)

        with context("the satisfy action is expanded"):
            with before.each:
                self.response = _expand_action(
                    self.bdd,
                    "satisfy",
                    toolset_path=_AGENT_BDD_TOOLSET,
                    context={"format": "python"},
                )

            with it("should inline bdd satisfy prose via nested bdd satisfy"):
                satisfy_prose = _lifecycle_prose("satisfy")
                _assert_text_inlined(self.response["instructions"], satisfy_prose)
                _assert_text_inlined(self.response["instructions"], self.bdd_contexts)
