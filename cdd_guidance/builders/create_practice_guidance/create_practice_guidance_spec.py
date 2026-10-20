"""BDD spec for CreatePracticeGuidance - meta generator face (scaffold domains)."""

import sys
from pathlib import Path

from expects import equal, expect
from mamba import before, context, description, it

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("cdd_guidance/practices", "tools", "cdd_guidance/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from cdd_guidance.builders.create_practice_guidance.create_practice_guidance import CreatePracticeGuidance

_CREATE_DIR = Path(__file__).resolve().parent
_GUIDANCE_MARKER = "scaffold-vs-patch"


with description("CreatePracticeGuidance meta generator"):
    with before.all:
        self.generator = CreatePracticeGuidance()

    with context("that has been created"):
        with it("should key the index from the install folder name"):
            expect(self.generator.context_index_key).to(equal("create_practice_guidance"))

        with it("should default the workspace folder to the repo root"):
            expect(type(self.generator).default_workspace_folder).to(equal("."))

        with it("should resolve module_dir to the create_practice_guidance package"):
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

        with it("should inline practice guidance from create_practice_guidance.md"):
            expect(_GUIDANCE_MARKER in self.prose).to(equal(True))
