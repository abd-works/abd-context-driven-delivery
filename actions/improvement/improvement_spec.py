"""BDD spec for Improvement — /repair inlines the manual diagnose recipe."""

import inspect
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities", "practices", "actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be_true, equal, expect
from mamba import before, context, description, it

from primitives.harness.runner import InstructionRunRequest, InstructionRunner
from primitives.instructions import Instruction
from primitives.instructions import _path_for_name
from agent_tools import AgentToolSet
from primitives.harness.toolset_loader import ToolsetLoader

_KIT_DIR = Path(__file__).resolve().parent
_IMPROVEMENT = "improvement.improvement:Improvement"


def _expand(
    instance: AgentToolSet,
    action_name: str,
    *,
    toolset_path: str,
    arguments: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return InstructionRunner.instance().invoke_action(
        InstructionRunRequest(
            request={"toolset": toolset_path, "context": {}},
            toolset_path=toolset_path,
            action_name=action_name,
            context={},
            arguments=arguments or {},
            instance=instance,
        )
    )


def _section(name: str) -> str:
    text = _path_for_name(_KIT_DIR, name).replace(" \u00a7 ", " # ", 1)
    return Instruction(text, _KIT_DIR, domain_slug="improvement").expand()


with description("Improvement repair recipe"):
    with it("should document diagnose then proposed kit change before any test"):
        content = _section("repair")
        expect("proposed kit change" in content).to(be_true)
        expect("Diagnose" in content).to(be_true)
        expect("tactical file fixes" in content or "tactical diffs" in content).to(
            be_true
        )

    with context("when repair is expanded"):
        with before.all:
            cls = ToolsetLoader.instance().load(_IMPROVEMENT)
            self.kit = cls()
            self.response = _expand(
                self.kit,
                "repair",
                toolset_path=_IMPROVEMENT,
                arguments={
                    "tools": [],
                    "asset": "practices/base/base_context_tool.md",
                    "violation": "generate swallowed a whole model in one turn",
                },
            )

        with it("should inline the repair.md recipe"):
            expect(_section("repair") in self.response["instructions"]).to(be_true)

        with it("should require a proposed kit change before any test"):
            expect("proposed kit change" in self.response["instructions"]).to(be_true)

        with it("should tell the agent not to list tactical diffs"):
            expect("tactical diffs" in self.response["instructions"]).to(be_true)

        with it("should keep the turn open until after fail-first"):
            expect(
                "leave the turn open" in self.response["instructions"].lower()
            ).to(be_true)
            expect("finish_turn" in inspect.getsource(type(self.kit).repair)).to(
                equal(False)
            )
