"""BDD spec for WorkspaceSession - kit prose + tools on BaseContextTool hosts."""

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
from tools.tool import Toolset, _ToolsetLoader, _discover_tools

_KIT_DIR = Path(__file__).resolve().parent
_CAR_CHRONICLE_TOOLSET = (
    "context_tools.create_context_tool.examples.car_chronicle.car_chronicle:CarChronicle"
)
_CHRONICLE_WITH_OUTPUT_TOOLSET = (
    "context_tools.create_context_tool.examples.car_chronicle.chronicle_with_output:ChronicleWithOutput"
)
_BASE_TOOLSET = "context_tools.base.base_context_tool:BaseContextTool"


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


with description("WorkspaceSession kit prose"):
    with it("should resolve create_session from sessions.md section"):
        text = _section("create_session")
        expect(text.startswith("# Create Session")).to(be_true)
        expect("kebab-slug" in text).to(be_true)

    with it("should resolve session guidance from sessions.md section"):
        text = _section("session")
        expect("# Session" in text).to(be_true)
        expect("session.path" in text).to(be_true)
        expect("context-index.md" in text).to(be_true)


with description("WorkspaceSession on a BaseContextTool host"):
    with context("CarChronicle generate"):
        with before.all:
            cls = _ToolsetLoader.instance().load(_CAR_CHRONICLE_TOOLSET)
            self.host = cls()
            self.response = _expand(
                self.host, "generate", toolset_path=_CAR_CHRONICLE_TOOLSET
            )

        with it("should name read_context_index and record_context_root on tools"):
            expect(self.response["tools"]).to(
                equal(["read_context_index", "record_context_root"])
            )

        with it("should inline Session section guidance"):
            expect("# Session" in self.response["instructions"]).to(be_true)
            expect("session.folder" in self.response["instructions"]).to(be_true)

        with it("should expand session resource from the host instance"):
            expect(
                f"Resource `session` = {self.host.session!r}."
                in self.response["instructions"]
            ).to(be_true)

        with it("should expand kit tool instructions from sessions.md"):
            tools = _discover_tools(self.host)
            expect(tools["create_session"].instructions.startswith("# Create Session")).to(
                be_true
            )
            expect(
                tools["read_context_index"].instructions.startswith("# Read Context Index")
            ).to(be_true)

    with context("ChronicleWithOutput generate"):
        with before.all:
            cls = _ToolsetLoader.instance().load(_CHRONICLE_WITH_OUTPUT_TOOLSET)
            self.host = cls()
            self.response = _expand(
                self.host, "generate", toolset_path=_CHRONICLE_WITH_OUTPUT_TOOLSET
            )

        with it("should keep session tools ahead of nested generate_output tools"):
            expect(self.response["tools"]).to(
                equal(
                    ["read_context_index", "record_context_root", "add_epic"]
                )
            )

    with context("BaseContextTool generate"):
        with before.all:
            cls = _ToolsetLoader.instance().load(_BASE_TOOLSET)
            self.host = cls()
            self.response = _expand(
                self.host, "generate", toolset_path=_BASE_TOOLSET
            )

        with it("should inline session guidance on the composer"):
            expect("# Session" in self.response["instructions"]).to(be_true)
