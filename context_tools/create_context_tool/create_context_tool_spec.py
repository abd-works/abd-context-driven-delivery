"""BDD spec for CreateContextTool — meta generator face (scaffold domains)."""

from pathlib import Path
from typing import Any

from expects import equal, expect
from mamba import before, context, description, it

import context_tools  # noqa: F401
from primitives.actions.action import _ActionRunRequest, _ActionRunner
from primitives.instructions import Instruction
from tools.tool import Toolset, _ToolsetLoader

_REPO_ROOT = Path(__file__).resolve().parents[2]
_CREATE_DIR = Path(__file__).resolve().parent
_CREATE_TOOLSET = (
    "context_tools.create_context_tool.create_context_tool:CreateContextTool"
)
_META_CONTEXT_MARKER = "scaffold-vs-patch"


def _load_create() -> Toolset:
    return _ToolsetLoader.instance().load(_CREATE_TOOLSET)()


def _expand_action(
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


def _load_meta_concepts() -> str:
    return Instruction(
        "\u00a7 Contexts", _CREATE_DIR, domain_slug="create_context_tool"
    ).expand()


def _load_scaffold_templates() -> str:
    from primitives.assets import AssetCollection
    from primitives.assets import AssetLocation

    location = AssetLocation(
        "folder",
        _CREATE_DIR,
        "create_context_tool",
        folder=_CREATE_DIR / "templates",
    )
    return AssetCollection(location).merged()


with description("CreateContextTool meta generator"):
    with before.all:
        self.generator = _load_create()
        self.meta_concepts = _load_meta_concepts()
        self.template = _load_scaffold_templates()

    with context("generate expands meta face"):
        with before.each:
            self.response = _expand_action(
                self.generator,
                "generate",
                toolset_path=_CREATE_TOOLSET,
            )

        with it("should inline meta contexts from create_context_tool.md"):
            expect(_META_CONTEXT_MARKER in self.response["instructions"]).to(
                equal(True)
            )
            expect(self.meta_concepts in self.response["instructions"]).to(equal(True))

        with it("should inline all files from create_context_tool/templates/"):
            expect(self.template in self.response["instructions"]).to(equal(True))
            expect("@base_context_tool" in self.response["instructions"]).to(
                equal(True)
            )
            expect("# Instructions" in self.response["instructions"]).to(equal(True))
            expect("# Worked examples" in self.response["instructions"]).to(
                equal(True)
            )

        with it("should inline worked samples from create_context_tool/examples"):
            expect("use-driving-voice" in self.response["instructions"]).to(
                equal(True)
            )
