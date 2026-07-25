"""BDD spec for Repair kit — action expansion on ContextTool hosts."""

import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities", "context_tools"):
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
_CAR_CHRONICLE_DIR = (
    _REPO_ROOT / "context_tools" / "base" / "examples" / "car_chronicle"
)
_CAR_CHRONICLE_TOOLSET = (
    "context_tools.base.examples.car_chronicle.car_chronicle:CarChronicle"
)
_LIFECYCLE_DIR = _REPO_ROOT / "context_tools" / "base" / "artifact_lifecycle"


def _expand(
    instance: Toolset,
    action_name: str,
    *,
    toolset_path: str,
    arguments: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return _ActionRunner.instance().run(
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
    return Instruction(_path_for_name(_KIT_DIR, name), _KIT_DIR).expand()


def _lifecycle(name: str) -> str:
    return Instruction(_path_for_name(_LIFECYCLE_DIR, name), _LIFECYCLE_DIR).expand()


with description("Repair kit prose"):
    with it("should resolve repair from kit markdown"):
        text = _section("repair")
        expect("Iterate until **validate** passes" in text or "# Repair" in text).to(
            be_true
        )


with description("Repair on a ContextTool host"):
    with context("repair expanded on CarChronicle"):
        with before.all:
            cls = _ToolsetLoader.instance().load(_CAR_CHRONICLE_TOOLSET)
            self.host = cls()
            self.contexts = Instruction(
                "\u00a7 Contexts", _CAR_CHRONICLE_DIR, domain_slug="car_chronicle"
            ).expand()
            self.examples = Instruction(
                "examples", _CAR_CHRONICLE_DIR, domain_slug="car_chronicle"
            ).expand()
            self.template = Instruction(
                "car_chronicle-templates",
                _CAR_CHRONICLE_DIR,
                domain_slug="car_chronicle",
            ).expand()
            self.response = _expand(
                self.host,
                "repair",
                toolset_path=_CAR_CHRONICLE_TOOLSET,
                arguments={
                    "asset": (
                        "context_tools/base/examples/car_chronicle/output/driving-log.md"
                    ),
                    "violation": (
                        "Scanner: use-driving-voice — chronicle reads like a spec sheet"
                    ),
                },
            )

        with it("should set action to repair"):
            expect(self.response["action"]).to(equal("repair"))

        with it("should name scan on tools"):
            expect(self.response["tools"]).to(equal(["scan"]))

        with it("should inline repair prose"):
            expect(
                "Iterate until **validate** passes" in self.response["instructions"]
            ).to(be_true)
            expect(
                "<domain>/examples/<descriptive-folder>/"
                in self.response["instructions"]
            ).to(be_true)
            expect(
                "Delete `runs/` when the repair is done"
                in self.response["instructions"]
            ).to(be_true)

        with it("should inline generator-fix prose"):
            instructions = self.response["instructions"]
            expect("Fix the generator" in instructions).to(be_true)
            expect("Do not hand-edit" in instructions).to(be_true)
            expect("Re-run **generate**" in instructions).to(be_true)

        with it("should inline contexts examples and template for root cause"):
            expect(self.contexts in self.response["instructions"]).to(be_true)
            expect(self.examples in self.response["instructions"]).to(be_true)
            expect(self.template in self.response["instructions"]).to(be_true)

        with it("should substitute asset and violation arguments"):
            instructions = self.response["instructions"]
            expect(
                "context_tools/base/examples/car_chronicle/output/driving-log.md"
                in instructions
            ).to(be_true)
            expect("use-driving-voice" in instructions).to(be_true)

        with it("should nest validate prose"):
            expect(_lifecycle("validate") in self.response["instructions"]).to(be_true)
