"""BDD spec for CreateContextTool - meta generator face (scaffold domains)."""

import sys
from pathlib import Path

from expects import equal, expect
from mamba import before, context, description, it

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("practices", "tools", "actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from builders.create_context_tool.create_context_tool import CreateContextTool

_CREATE_DIR = Path(__file__).resolve().parent
_META_CONTEXT_MARKER = "scaffold-vs-patch"


with description("CreateContextTool meta generator"):
    with before.all:
        self.generator = CreateContextTool()

    with context("that has been created"):
        with it("should key the context index as create_context_tool"):
            expect(type(self.generator).context_index_key).to(
                equal("create_context_tool")
            )

        with it("should default the workspace folder to the repo root"):
            expect(type(self.generator).default_workspace_folder).to(equal("."))

        with it("should resolve module_dir to the create_context_tool package"):
            expect(self.generator.module_dir).to(equal(_CREATE_DIR.resolve()))

        with it(
            "should not expose generate, validate, satisfy, or repair on Guidance"
        ):
            signature = self.generator.tools
            for name in ("generate", "validate", "satisfy", "repair"):
                expect(name in signature).to(equal(False))

    with context("guidance expands meta face"):
        with before.each:
            self.prose = self.generator.instructions or ""

        with it("should inline meta contexts from create_context_tool.md"):
            expect(_META_CONTEXT_MARKER in self.prose).to(equal(True))
