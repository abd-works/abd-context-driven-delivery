"""The module card next to a code folder."""

import tempfile
from pathlib import Path

from expects import be_false, be_true, contain, equal, expect
from mamba import after, before, context, description, it

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

    with context("read once and then changed on disk"):
        with before.each:
            self.folder = tempfile.TemporaryDirectory()
            card = Path(self.folder.name) / ".context" / "module-context.md"
            card.parent.mkdir()
            card.write_text("# Cart\n\n**Seam (terms):** Cart\n\n## Order : Cart\n", encoding="utf-8")
            self.card = ModuleContext(Path(self.folder.name))
            self.card.read()
            card.write_text("# Cart\n", encoding="utf-8")

        with after.each:
            self.folder.cleanup()

        with it("should answer from the text it read"):
            expect(self.card.names_seam()).to(be_true)

        with it("should find the heading that writes a class with its base"):
            expect(self.card.writes_child_parent_headings()).to(be_true)

        with it("should find no inheritance written in prose"):
            expect(self.card.says_is_a_type_of()).to(be_false)
