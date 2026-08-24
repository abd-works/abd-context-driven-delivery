# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""BDD spec for Improvement — /repair inlines the manual diagnose recipe."""

import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities", "context_tools", "context_tools/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be_true, equal, expect
from mamba import before, context, description, it

from primitives.actions.action import _ActionRunRequest, _ActionRunner
from primitives.instructions import Instruction
from primitives.instructions import _path_for_name
from tools.tool import Toolset, _ToolsetLoader

_KIT_DIR = Path(__file__).resolve().parent
_IMPROVEMENT = "improvement.improvement:Improvement"


def _expand(
    instance: Toolset,
    action_name: str,
    *,
    toolset_path: str,
    arguments: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return _ActionRunner.instance().invoke_action(
        _ActionRunRequest(
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
            cls = _ToolsetLoader.instance().load(_IMPROVEMENT)
            self.kit = cls()
            self.response = _expand(
                self.kit,
                "repair",
                toolset_path=_IMPROVEMENT,
                arguments={
                    "tools": [],
                    "asset": "context_tools/base/base_context_tool.md",
                    "violation": "generate swallowed a whole model in one turn",
                },
            )

        with it("should inline the repair.md recipe"):
            expect(_section("repair") in self.response["instructions"]).to(be_true)

        with it("should require a proposed kit change before any test"):
            expect("proposed kit change" in self.response["instructions"]).to(be_true)

        with it("should tell the agent not to list tactical diffs"):
            expect("tactical diffs" in self.response["instructions"]).to(be_true)
