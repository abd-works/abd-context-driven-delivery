"""The module card next to a code folder."""

from pathlib import Path

from expects import contain, equal, expect
from mamba import description, it

from cdd_guidance.practices.clean_engineering.model.module_context_files import ModuleContext

_EXAMPLES = Path(__file__).resolve().parent / "python" / "_examples"


def _card(example: str, version: str) -> ModuleContext:
    return ModuleContext(_EXAMPLES / example / version)


with description("the module card of a code folder"):
    with it("should be missing for a folder with no card"):
        expect(_card("missing-module-context", "faulty").exists()).to(equal(False))

    with it("should read as empty for a folder with no card"):
        expect(_card("missing-module-context", "faulty").read()).to(equal(""))

    with it("should find a Modules heading"):
        expect(_card("language-modules-one-section", "faulty").has_modules_heading()).to(equal(True))

    with it("should find no Modules heading once it is repaired"):
        expect(_card("language-modules-one-section", "repaired").has_modules_heading()).to(equal(False))

    with it("should name the model detail written into it"):
        expect(" ".join(_card("modules-not-model-blocks", "faulty").model_blocks())).to(contain("Live instance"))

    with it("should name no model detail once it is repaired"):
        expect(_card("modules-not-model-blocks", "repaired").model_blocks()).to(equal([]))
