"""BDD spec for ArtifactLifecycle — generate / validate / satisfy prose on hosts."""

import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[3]
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
_BASE_TOOLSET = "context_tools.base.context_tool:ContextTool"


def _expand(
    instance: Toolset,
    action_name: str,
    *,
    toolset_path: str,
) -> dict[str, Any]:
    return _ActionRunner.instance().run(
        _ActionRunRequest(
            request={"toolset": toolset_path, "context": {}},
            toolset_path=toolset_path,
            action_name=action_name,
            context={},
            arguments={},
            instance=instance,
        )
    )


def _section(name: str) -> str:
    return Instruction(_path_for_name(_KIT_DIR, name), _KIT_DIR).expand()


with description("ArtifactLifecycle kit prose"):
    with it("should resolve generate / validate / satisfy from kit markdown"):
        expect("# Generate" in _section("generate")).to(be_true)
        expect("# Validate" in _section("validate")).to(be_true)
        expect("# Satisfy" in _section("satisfy")).to(be_true)


with description("ArtifactLifecycle on a ContextTool host"):
    with context("CarChronicle"):
        with before.all:
            cls = _ToolsetLoader.instance().load(_CAR_CHRONICLE_TOOLSET)
            self.host = cls()
            self.template = Instruction(
                "car_chronicle-templates",
                _CAR_CHRONICLE_DIR,
                domain_slug="car_chronicle",
            ).expand()

        with context("generate"):
            with before.each:
                self.response = _expand(
                    self.host, "generate", toolset_path=_CAR_CHRONICLE_TOOLSET
                )

            with it("should set action to generate"):
                expect(self.response["action"]).to(equal("generate"))

            with it("should inline generate prose"):
                expect(_section("generate") in self.response["instructions"]).to(
                    be_true
                )

        with context("validate"):
            with before.each:
                self.response = _expand(
                    self.host, "validate", toolset_path=_CAR_CHRONICLE_TOOLSET
                )

            with it("should set action to validate"):
                expect(self.response["action"]).to(equal("validate"))

            with it("should name scan on tools"):
                expect(self.response["tools"]).to(equal(["scan"]))

            with it("should inline validate prose"):
                expect(_section("validate") in self.response["instructions"]).to(
                    be_true
                )

        with context("satisfy"):
            with before.each:
                self.response = _expand(
                    self.host, "satisfy", toolset_path=_CAR_CHRONICLE_TOOLSET
                )

            with it("should set action to satisfy"):
                expect(self.response["action"]).to(equal("satisfy"))

            with it("should name no tools on satisfy"):
                expect(self.response["tools"]).to(equal([]))

            with it("should inline satisfy prose"):
                expect(_section("satisfy") in self.response["instructions"]).to(
                    be_true
                )

            with it("should inline the domain template"):
                expect(self.template in self.response["instructions"]).to(be_true)

    with context("base ContextTool generate"):
        with before.all:
            cls = _ToolsetLoader.instance().load(_BASE_TOOLSET)
            self.host = cls()
            self.response = _expand(
                self.host, "generate", toolset_path=_BASE_TOOLSET
            )

        with it("should inline generate prose on the composer"):
            expect(_section("generate") in self.response["instructions"]).to(be_true)
