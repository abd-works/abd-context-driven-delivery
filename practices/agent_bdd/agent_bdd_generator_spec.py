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
        for c in ("practices", "primitives", "tools", "actions")
    ],
]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from primitives.agent_tools.agent_tools import AgentToolSet
import agent_bdd.conf  # noqa: F401 - repo root on sys.path
import practices  # noqa: F401
from primitives.markdown import Markdown
from agent_tools import AgentToolSet
from validate.validate import Validate
from practices.bdd.bdd import Bdd

_AGENT_BDD_TOOLSET = "agent_bdd.agent_bdd:AgentBdd"
_BDD_DIR = _REPO_ROOT / "practices" / "bdd"
_GENERATE_DIR = _REPO_ROOT / "practices" / "actions" / "generate"
_VALIDATE_DIR = _REPO_ROOT / "practices" / "actions" / "validate"
_GENERATE_TOOLSET = "generate.generate:Generate"
_VALIDATE_TOOLSET = "validate.validate:Validate"


def _kit_prose(action: str, kit_dir: Path) -> str:
    return (kit_dir / f"{action}.md").read_text(encoding="utf-8")


def _load_agent_bdd(*, format_name: str = "python") -> AgentToolSet:
    toolset_cls = type(AgentToolSet.instantiate(_AGENT_BDD_TOOLSET))
    return toolset_cls(format=format_name)


def _expand_action(
    instance: AgentToolSet,
    action_name: str,
    *,
    context: dict[str, Any] | None = None,
    arguments: dict[str, Any] | None = None,
) -> Any:
    return instance.instructions[action_name].expand(
        context or {},
        arguments or {},
    )


def _assert_text_inlined(instructions: str, source: str) -> None:
    expect(source in instructions).to(be_true)


with description("AgentBdd action expansion"):
    with context("an AgentBdd generator with format python"):
        with before.all:
            self.bdd = _load_agent_bdd()
            self.contexts = Markdown.from_label(self.bdd, "contexts").extract()
            self.bdd_contexts = Markdown.from_label(Bdd(), "contexts").extract()

        with context("that does not own kit lifecycle actions"):
            with it("should not expose generate, validate, satisfy, or repair"):
                for name in ("generate", "validate", "satisfy", "repair"):
                    expect(name in self.bdd.agent_tools).to(equal(False))

        with context("the guidance action is expanded"):
            with before.each:
                self.response = _expand_action(
                    self.bdd,
                    "guidance",
                    context={"format": "python"},
                )

            with it("should inline agent-BDD concepts from agent_bdd.md"):
                _assert_text_inlined(self.response.instructions, self.contexts)

            with it("should inline templates/agent_bdd-templates.py from format resource"):
                template = Markdown.from_label(self.bdd, "templates").extract()
                expect("with description" in self.response.instructions).to(be_true)
                expect("ai_judge" in self.response.instructions).to(be_true)
                expect(len(template) > 0).to(be_true)

        with context("the Validate kit is expanded with this host"):
            with before.each:
                self.response = _expand_action(
                    Validate(),
                    "validate",
                    arguments={"tools": [self.bdd]},
                )

            with it("should inline validate kit prose"):
                _assert_text_inlined(
                    self.response.instructions,
                    _kit_prose("validate", _VALIDATE_DIR),
                )
