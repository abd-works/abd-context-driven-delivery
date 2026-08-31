"""BDD spec - AgentBdd expands agent-test content and composes bdd actions."""

import sys
from pathlib import Path
from typing import Any

from expects import be_true, equal, expect
from mamba import before, context, description, it

_AGENT_BDD_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _AGENT_BDD_DIR.parents[1]
for _p in [
    str(_REPO_ROOT),
    *[
        str(_REPO_ROOT / c)
        for c in ("context_tools", "primitives", "utilities", "context_tools/actions")
    ],
]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from primitives.actions.action import _ActionRunRequest, _ActionRunner
import agent_bdd.conf  # noqa: F401 - repo root on sys.path
import context_tools  # noqa: F401
from primitives.instructions import Instruction
from tools.tool import Toolset, _ToolsetLoader
from validate.validate import Validate

_AGENT_BDD_TOOLSET = "agent_bdd.agent_bdd:AgentBdd"
_GENERATE_DIR = _REPO_ROOT / "context_tools" / "actions" / "generate"
_VALIDATE_DIR = _REPO_ROOT / "context_tools" / "actions" / "validate"
_GENERATE_TOOLSET = "generate.generate:Generate"
_VALIDATE_TOOLSET = "validate.validate:Validate"


def _kit_prose(action: str, kit_dir: Path) -> str:
    from primitives.instructions import _path_for_name

    return Instruction(_path_for_name(kit_dir, action), kit_dir).expand()


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
    return _ActionRunner.instance().invoke_action(
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

        with context("that does not own kit lifecycle actions"):
            with it("should not expose generate, validate, satisfy, or repair"):
                for name in ("generate", "validate", "satisfy", "repair"):
                    expect(name in self.bdd.actions).to(equal(False))

        with context("the guidance action is expanded"):
            with before.each:
                self.response = _expand_action(
                    self.bdd,
                    "guidance",
                    toolset_path=_AGENT_BDD_TOOLSET,
                    context={"format": "python"},
                )

            with it("should set action to guidance"):
                expect(self.response["action"]).to(equal("guidance"))

            with it("should inline agent-BDD concepts from agent_bdd.md"):
                _assert_text_inlined(self.response["instructions"], self.contexts)

            with it("should inline templates/agent_bdd-templates.py from format resource"):
                template = Instruction(
                    "templates/agent_bdd-templates.py", _AGENT_BDD_DIR
                ).expand()
                expect("with description" in self.response["instructions"]).to(be_true)
                expect("ai_judge" in self.response["instructions"]).to(be_true)
                expect(len(template) > 0).to(be_true)

            with it("should inline vanilla BDD hierarchy and signature guidance"):
                prose = self.response["instructions"]
                expect("Hierarchy shape" in prose).to(be_true)
                expect("observable-behavior" in prose).to(be_true)
                expect("state-not-when" in prose).to(be_true)
                expect("SIGNATURE" in prose).to(be_true)

            with it("should tell the caller to pass the CE companion to this action as a separate run"):
                prose = self.response["instructions"]
                expect("separate tools run" in prose).to(be_true)
                expect("Clean Engineering" in prose).to(be_true)

            with it("should NOT inline CleanEngineering generate instructions"):
                expect("Deepen OO design" in self.response["instructions"]).to(equal(False))

            with it("should list companion guidance as a deferred tool hop"):
                expect("guidance" in self.response["tools"]).to(be_true)

        with context("the Validate kit is expanded with this host"):
            with before.each:
                self.response = _expand_action(
                    Validate(),
                    "validate",
                    toolset_path=_VALIDATE_TOOLSET,
                    arguments={"tools": [self.bdd]},
                )

            with it("should inline validate kit prose"):
                _assert_text_inlined(
                    self.response["instructions"],
                    _kit_prose("validate", _VALIDATE_DIR),
                )
