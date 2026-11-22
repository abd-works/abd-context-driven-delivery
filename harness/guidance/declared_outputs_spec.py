"""BDD spec — the file a fidelity's declared outputs name for a render of one of its files into another format."""
from expects import equal, expect
from mamba import before, context, description, it

from pathlib import Path

from harness.guidance.declared_outputs import DeclaredFile, DeclaredOutputs, RenderPlace
from harness.markdown.format import Format

_STORY_MAP = {
    "markdown": ".context/story-map.md",
    "drawio": ".context/story-map.drawio",
    "whiteboard": ".context/story-map.whiteboard",
    "thin_slice": [".context/thin-slice.md", ".context/thin-slice.drawio", ".context/thin-slice.whiteboard"],
}
_SCENARIOS = {
    "python": "story_tests/{epic}/{sub-epic}/{story}/{story_snake}_story.test.py",
    "markdown": "story_tests/{epic}/{sub-epic}/{story_snake}_story.test.md",
    "realization": ".context/{scope}-scenario-realization.md",
}
_MODULES = {
    "markdown": "{module}/.context/module-context.md",
    "drawio": ".context/modules.drawio",
}
_CLASS_MODEL = {
    "python": "{module}/",
    "markdown": "{module}/.context/{module}-model.md",
    "drawio": "{module}/.context/{module}-model.drawio",
}


def _declared(outputs: dict) -> DeclaredOutputs:
    """The declared outputs of a fidelity: every example asks only what the outputs themselves say."""
    return DeclaredOutputs(outputs)


with description("the file a fidelity declares for a render of one of its files") as self:
    with context("with a main file and a second output named for what it holds, each declared in every format"):
        with before.each:
            self.declared = _declared(_STORY_MAP)

        with it("should name the main file's drawing for the main file"):
            expect(self.declared.file_name_beside(".context/story-map.md", "drawio")).to(equal("story-map.drawio"))

        with it("should name the second output's own drawing for the second output's markdown"):
            expect(self.declared.file_name_beside(".context/thin-slice.md", "drawio")).to(equal("thin-slice.drawio"))

        with it("should name the second output's own whiteboard for the second output's markdown"):
            expect(self.declared.file_name_beside(".context/thin-slice.md", "whiteboard")).to(equal("thin-slice.whiteboard"))

        with it("should name the second output's own markdown for the second output's drawing"):
            expect(self.declared.file_name_beside(".context/thin-slice.drawio", "markdown")).to(equal("thin-slice.md"))

    with context("with an output named for what it holds that is declared in one format only"):
        with before.each:
            self.declared = _declared(_SCENARIOS)

        with it("should name no file of the fidelity's other outputs for it in another format"):
            expect(self.declared.file_name_beside(".context/checkout-scenario-realization.md", "python")).to(equal(""))

    with context("with a drawing declared under the folder each source file starts in"):
        with before.each:
            self.declared = _declared(_CLASS_MODEL)

        with it("should place the drawing in the source's own folder, named for the source's module"):
            placed = self.declared.file_beside("C:/work/src/ordering/.context/ordering-model.md", "drawio")
            expect(placed).to(equal("C:/work/src/ordering/.context/ordering-model.drawio"))

    with context("with one drawing declared for the project and a markdown file declared for each module"):
        with before.each:
            self.declared = _declared(_MODULES)

        with it("should place the drawing from the fidelity's root, not in the first module's folder"):
            expect(self.declared.file_beside("src/catalogue/.context/module-context.md", "drawio")).to(equal(".context/modules.drawio"))

        with it("should name no one markdown file for the project's drawing, which holds every module"):
            expect(self.declared.file_beside(".context/modules.drawio", "markdown")).to(equal(""))

    with context("with a main file kept in a folder below the root"):
        with before.each:
            self.declared = _declared(_STORY_MAP)

        with it("should place the drawing in that same folder"):
            expect(self.declared.file_beside("docs/.context/story-map.md", "drawio")).to(equal("docs/.context/story-map.drawio"))

    with context("with a source that is none of the fidelity's files"):
        with before.each:
            self.declared = _declared(_STORY_MAP)

        with it("should place no file for it"):
            expect(self.declared.file_beside(".context/returns.md", "drawio")).to(equal(""))


with description("the code formats a fidelity writes as a folder for each module") as self:
    with context("with a folder declared for one code format, alone and beside the file a render writes"):
        with before.each:
            self.declared = _declared({"python": "{module}/", "typescript": ["{module}/", "{module}/{module}.ts"], "markdown": "{module}/.context/{module}-model.md"})

        with it("should name each code format that declares a folder"):
            expect(self.declared.code_folders()).to(equal(["python", "typescript"]))

    with context("with a file declared for each code format and no folder"):
        with it("should name none"):
            expect(_declared({"python": "{bounded_context}/{aggregate}/{aggregate}.py"}).code_folders()).to(equal([]))


with description("a declared file") as self:
    with it("should name the folders it names outright before its first named part"):
        expect(DeclaredFile("story_tests/{epic}/{sub-epic}/{story}/x.py").fixed_folder).to(equal("story_tests"))

    with it("should name its own folder when nothing in it is filled in"):
        expect(DeclaredFile(".context/story-map.md").fixed_folder).to(equal(".context"))

    with it("should name a declared folder itself"):
        expect(DeclaredFile("docs/maps/").fixed_folder).to(equal("docs/maps"))

    with it("should read a source's own name off the wildcard of its file name"):
        expect(DeclaredFile("**/*View.tsx").own_name_of(Path("src/CartView.tsx"))).to(equal("Cart"))

    with it("should read a source's own name off its one named part"):
        expect(DeclaredFile(".context/{scope}-bdd-realization.md").own_name_of(Path(".context/bookshop-bdd-realization.md"))).to(equal("bookshop"))

    with it("should read no name off a file name that does not say where the name ends"):
        expect(DeclaredFile("**/*spec.ts").own_name_of(Path("cart.spec.ts"))).to(equal(None))

    with it("should fill its named parts with names in the order they come"):
        expect(DeclaredFile("{bounded_context}/{aggregate}/{aggregate}.py").filled_with(["ordering", "cart"])).to(equal("ordering/cart/cart.py"))

    with it("should fill nothing when the names are too few"):
        expect(DeclaredFile("{bounded_context}/{aggregate}/{aggregate}.py").filled_with(["ordering"])).to(equal(""))


with description("where a fidelity's declared paths place a render") as self:
    with before.each:
        self.placement = DeclaredOutputs({
            "python": ["{bounded_context}/{aggregate}/{aggregate}.py", "{module}/"],
            "typescript": ["{bounded_context}/{aggregate}/{aggregate}.ts", "**/*View.tsx"],
            "javascript": ["**/*View.jsx"],
            "markdown": [".context/{scope}-bdd-realization.md"],
        }).placement

    with it("should place a section of code by the names its banner gives"):
        expect(self.placement.section_place(["ordering", "cart"], Format("python"))).to(equal(RenderPlace("ordering/cart/cart.py")))

    with it("should place one of the fidelity's own files as the same file in the other language, where its path starts"):
        place = self.placement.counterpart_of(Path("/work/catalogue/book/book.ts"), Format("python"))
        expect(place).to(equal(RenderPlace("/work/catalogue/book/book.py", from_root=False)))

    with it("should place code from a view beside it, named for the view"):
        expect(self.placement.beside_source(Path("/work/src/CartView.tsx"), Format("javascript"))).to(equal(RenderPlace("/work/src/CartView.jsx", from_root=False)))

    with it("should place a document of a scope at the declared path that names one"):
        expect(self.placement.place_for_scope("bookshop", Format("markdown"))).to(equal(RenderPlace(".context/bookshop-bdd-realization.md")))

    with it("should place a render of a file no declaration names under that file's own name"):
        expect(self.placement.beside_itself(Path("design/cart-sketch.md"), Format("sketch"), Format("markdown"))).to(equal(Path("design/cart.md")))
