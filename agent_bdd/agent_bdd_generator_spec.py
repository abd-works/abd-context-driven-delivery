"""BDD spec — AgentBdd expands agent-test content and composes bdd actions."""

from pathlib import Path
from typing import Any

from expects import be_true, equal, expect
from mamba import before, context, description, it

from agents.runner import ActionRunner
import agent_bdd.conf  # noqa: F401 — repo root on sys.path
import generator  # noqa: F401
from primitives.clean_code_ground_truth import load_concepts_section
from primitives.instruction import Instruction
from tools.tool import Toolset, ToolsetLoader

_AGENT_BDD_DIR = Path(__file__).resolve().parent
_AGENT_BDD_TOOLSET = "agent_bdd.agent_bdd:AgentBdd"
_BDD_DIR = _AGENT_BDD_DIR.parent / "bdd"
_GENERATOR_DIR = _AGENT_BDD_DIR.parent / "generator"


def _load_agent_bdd(*, format_name: str = "python") -> Toolset:
    toolset_cls = ToolsetLoader.instance().load(_AGENT_BDD_TOOLSET)
    return toolset_cls(format=format_name)


def _expand_action(
    instance: Toolset,
    action_name: str,
    *,
    toolset_path: str,
    context: dict[str, Any] | None = None,
    arguments: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return ActionRunner.instance().run(
        {"toolset": toolset_path, "context": context or {}},
        toolset_path=toolset_path,
        action_name=action_name,
        context=context or {},
        arguments=arguments or {},
        instance=instance,
    )


def _assert_text_inlined(instructions: str, source: str) -> None:
    expect(source in instructions).to(be_true)


with description("AgentBdd action expansion"):
    with context("an AgentBdd generator with format python"):
        with before.all:
            self.bdd = _load_agent_bdd()
            self.concepts = Instruction("§ Concepts", _AGENT_BDD_DIR, domain_slug="agent_bdd").expand()
            self.bdd_concepts = load_concepts_section(_BDD_DIR)

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
                _assert_text_inlined(self.response["instructions"], self.concepts)

            with it("should inline agent_bdd.md § Generate from generate_instructions slot"):
                generate_prose = Instruction(
                    "§ Generate", _AGENT_BDD_DIR, domain_slug="agent_bdd"
                ).expand()
                _assert_text_inlined(self.response["instructions"], generate_prose)

            with it("should inline bdd concepts via nested bdd generate"):
                _assert_text_inlined(self.response["instructions"], self.bdd_concepts)

            with it("should inline base-generator/generate.md action prose"):
                shared = Instruction("base-generator/generate", _GENERATOR_DIR).expand()
                _assert_text_inlined(self.response["instructions"], shared)

            with it("should inline formats/python/agent_bdd-templates.py from format resource"):
                template = Instruction(
                    "formats/python/agent_bdd-templates.py", _AGENT_BDD_DIR
                ).expand()
                _assert_text_inlined(self.response["instructions"], template)

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
                validate_prose = Instruction("base-generator/validate", _GENERATOR_DIR).expand()
                _assert_text_inlined(self.response["instructions"], validate_prose)
                _assert_text_inlined(self.response["instructions"], self.bdd_concepts)

        with context("the satisfy action is expanded"):
            with before.each:
                self.response = _expand_action(
                    self.bdd,
                    "satisfy",
                    toolset_path=_AGENT_BDD_TOOLSET,
                    context={"format": "python"},
                )

            with it("should inline bdd satisfy prose via nested bdd satisfy"):
                satisfy_prose = Instruction("base-generator/satisfy", _GENERATOR_DIR).expand()
                _assert_text_inlined(self.response["instructions"], satisfy_prose)
                _assert_text_inlined(self.response["instructions"], self.bdd_concepts)
