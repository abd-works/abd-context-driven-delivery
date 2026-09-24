"""Read module-context.md next to the class CodeQL named."""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import equal, expect
from mamba import description, it

from practices.clean_engineering.model.module_context_files import ModuleContextFiles

_EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


class ContextRow:
    def for_folder(self, class_name: str, folder: str) -> dict:
        path = _EXAMPLES / folder / "faultyAsset.py"
        return {"name": class_name, "message": str(path.resolve()), "contributor": class_name}


with description("module-context.md next to a CodeQL class"):
    with it("should flag a class folder with no module-context.md"):
        hits = ModuleContextFiles().rows_for_missing_module_context([ContextRow().for_folder("OrphanModule", "missing-module-context")])
        expect(any("OrphanModule" in (h["name"] + h["message"]) for h in hits)).to(equal(True))

    with it("should flag a Modules heading"):
        hits = ModuleContextFiles().rows_for_language_modules_one_section(
            [ContextRow().for_folder("LanguageSplit", "language-modules-one-section")]
        )
        expect(any("Modules" in h["message"] for h in hits)).to(equal(True))

    with it("should flag Internal design and a private name"):
        hits = ModuleContextFiles().rows_for_public_seam_only([ContextRow().for_folder("LeakySeam", "public-seam-only")])
        blob = " ".join(h["message"] for h in hits)
        expect("Internal design" in blob).to(equal(True))
        expect("_CartLog" in blob).to(equal(True))

    with it("should flag a typed dump"):
        hits = ModuleContextFiles().rows_for_modules_not_model_blocks(
            [ContextRow().for_folder("ModelDump", "modules-not-model-blocks")]
        )
        blob = " ".join(h["message"] for h in hits)
        expect("Live instance" in blob).to(equal(True))
