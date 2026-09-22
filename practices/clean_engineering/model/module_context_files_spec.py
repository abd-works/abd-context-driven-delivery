"""Read module-context.md next to the class CodeQL named."""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import equal, expect
from mamba import description, it

from practices.clean_engineering.model.module_context_files import (
    rows_for_language_modules_one_section,
    rows_for_missing_module_context,
    rows_for_modules_not_model_blocks,
    rows_for_public_seam_only,
)

_EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


def _row(class_name: str, folder: str) -> dict:
    path = _EXAMPLES / folder / "faultyAsset.py"
    return {"name": class_name, "message": str(path.resolve()), "contributor": class_name}


with description("module-context.md next to a CodeQL class"):
    with it("should flag a class folder with no module-context.md"):
        hits = rows_for_missing_module_context([_row("OrphanModule", "missing-module-context")])
        expect(any("OrphanModule" in (h["name"] + h["message"]) for h in hits)).to(equal(True))

    with it("should flag a Modules heading"):
        hits = rows_for_language_modules_one_section(
            [_row("LanguageSplit", "language-modules-one-section")]
        )
        expect(any("Modules" in h["message"] for h in hits)).to(equal(True))

    with it("should flag Internal design and a private name"):
        hits = rows_for_public_seam_only([_row("LeakySeam", "public-seam-only")])
        blob = " ".join(h["message"] for h in hits)
        expect("Internal design" in blob).to(equal(True))
        expect("_CartLog" in blob).to(equal(True))

    with it("should flag a typed dump"):
        hits = rows_for_modules_not_model_blocks(
            [_row("ModelDump", "modules-not-model-blocks")]
        )
        blob = " ".join(h["message"] for h in hits)
        expect("Live instance" in blob).to(equal(True))
