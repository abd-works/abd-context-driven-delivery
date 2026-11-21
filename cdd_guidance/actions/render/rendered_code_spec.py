"""Specs for where a render to code is saved: one file for each piece of the rendered code, at the path the fidelity
declares for it, keeping a code file that is already there and differs. The Render action that calls it is in
render_spec.py."""
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import contain, equal, expect, raise_error
from mamba import before, context, description, it

from cdd_guidance.actions.render.rendered_code import RenderedCode, RenderHasNoDeclaredPlace
from cdd_guidance.actions.render.reshaped_code import RenderWouldLoseContent
from harness.guidance.practice_formats import Reshaped
from harness.markdown.format import Format

AGGREGATE_FILE = "{bounded_context}/{aggregate}/{aggregate}.py"
# A domain model rendered to Python: one text, each aggregate under a banner naming its bounded context and itself.
MODEL_CODE = """\
from __future__ import annotations

# === Ordering | custom · Cart ===


class Cart:
    pass

# === Ordering | custom · Order Line ===


class OrderLine:
    pass
"""
CART_FILE = "from __future__ import annotations\n\n# === Ordering | custom · Cart ===\n\n\nclass Cart:\n    pass\n"
VIEW_CODE = "export function CartView() {}\n"


def _saved(root: Path, result: dict) -> list[str]:
    return [Path(path).relative_to(root).as_posix() for path in result["paths"]]


with description("a render to code that is saved") as self:
    with before.each:
        self.root = Path(tempfile.mkdtemp(prefix="cdd-rendered-code-"))

    with context("with one text holding a section for each aggregate"):
        with before.each:
            self.code = RenderedCode(self.root, [AGGREGATE_FILE], Format("python"))

        with it("should save a file for each aggregate at the path the fidelity declares"):
            result = self.code.save({"format": "python", "content": MODEL_CODE})
            expect(_saved(self.root, result)).to(equal(["ordering/cart/cart.py", "ordering/order_line/order_line.py"]))

        with it("should write each file with the text's opening lines and its own section"):
            self.code.save({"format": "python", "content": MODEL_CODE})
            expect((self.root / "ordering/cart/cart.py").read_text(encoding="utf-8")).to(equal(CART_FILE))

        with it("should answer no content for an agent to save"):
            expect("content" in self.code.save({"format": "python", "content": MODEL_CODE})).to(equal(False))

        with context("that a person filled a file of with code, rendered again"):
            with before.each:
                self.code.save({"format": "python", "content": MODEL_CODE})
                self.cart = self.root / "ordering/cart/cart.py"
                self.cart.write_text("class Cart:\n    def total(self):\n        return 5\n", encoding="utf-8")
                self.result = self.code.save({"format": "python", "content": MODEL_CODE})

            with it("should keep the code the person wrote"):
                expect(self.cart.read_text(encoding="utf-8")).to(contain("return 5"))

            with it("should name every file as holding the render"):
                expect(_saved(self.root, self.result)).to(equal(["ordering/cart/cart.py", "ordering/order_line/order_line.py"]))

            with it("should name total, which the model does not hold, as waiting to be migrated in that file"):
                expect([(Path(each["file"]).name, each["kept"], each["may_have_replaced_it"]) for each in self.result["migrate"]]).to(equal([("cart.py", "Cart.total", [])]))

        with context("that a file of holds a class the section does not, rendered with the class in it"):
            with before.each:
                self.code.save({"format": "python", "content": MODEL_CODE})
                self.cart = self.root / "ordering/cart/cart.py"
                self.cart.write_text("class Cart:\n    def old_total(self):\n        return 5\n", encoding="utf-8")
                rendered = MODEL_CODE.replace("class Cart:\n    pass", "class Cart:\n    def total(self):\n        raise NotImplementedError")
                self.result = self.code.save({"format": "python", "content": rendered})

            with it("should list the added operation as what may have replaced the one kept"):
                expect([(each["kept"], each["may_have_replaced_it"]) for each in self.result["migrate"]]).to(equal([("Cart.old_total", ["Cart.total"])]))

        with context("that a file of holds an operation of, whose opening line the section changed"):
            with before.each:
                self.code.save({"format": "python", "content": MODEL_CODE})
                self.cart = self.root / "ordering/cart/cart.py"
                self.cart.write_text("class Cart:" + chr(10) + "    def total(self):" + chr(10) + "        return 5" + chr(10), encoding="utf-8")
                rendered = MODEL_CODE.replace("class Cart:" + chr(10) + "    pass", "class Cart:" + chr(10) + "    def total(self, tax: int) -> int:" + chr(10) + "        raise NotImplementedError")
                self.result = self.code.save({"format": "python", "content": rendered})

            with it("should list the operation as one whose signature in the model now differs, with the model's"):
                listed = [(Path(each["file"]).name, each["signature_differs"], each["model_has"]) for each in self.result["migrate"]]
                expect(listed).to(equal([("cart.py", "Cart.total", "def total(self, tax: int) -> int:")]))

        with context("that is rendered again unchanged"):
            with it("should name every file as saved and nothing to migrate"):
                self.code.save({"format": "python", "content": MODEL_CODE})
                result = self.code.save({"format": "python", "content": MODEL_CODE})
                expect((len(result["paths"]), result["migrate"])).to(equal((2, [])))

        with context("whose format writes onto the existing text itself and drops a line the file held"):
            with before.each:
                lossy = lambda rendered, existing: Reshaped(rendered, [], [])
                self.code = RenderedCode(self.root, [AGGREGATE_FILE], Format("python"), reshape=lossy)
                self.code.save({"format": "python", "content": MODEL_CODE})
                self.cart = self.root / "ordering/cart/cart.py"
                self.written = "class Cart:\n    def total(self):\n        return 5\n"
                self.cart.write_text(self.written, encoding="utf-8")
                self.save = lambda: self.code.save({"format": "python", "content": MODEL_CODE})

            with it("should fail, naming the line the render would lose"):
                expect(self.save).to(raise_error(RenderWouldLoseContent, contain("return 5")))

            with it("should leave the file as it was"):
                try:
                    self.save()
                except RenderWouldLoseContent:
                    pass
                expect(self.cart.read_text(encoding="utf-8")).to(equal(self.written))

    with context("with a section whose names do not fill the declared path"):
        with it("should refuse, naming the section and the declared path, and save nothing"):
            code = RenderedCode(self.root, ["{module}/"], Format("python"))
            save = lambda: code.save({"format": "python", "content": "# === Ordering ===\n\nclass Cart:\n    pass\n"})
            expect(save).to(raise_error(RenderHasNoDeclaredPlace, contain("Ordering", "{module}/")))

    with context("with a file for each name it answers"):
        with it("should save each one the fidelity declares, under its root"):
            code = RenderedCode(self.root, ["story_tests/{epic}/{story}/{story_snake}_story.test.py"], Format("python"))
            result = code.save({"format": "python", "content": {"story_tests/fill-cart/add-book/add_book_story.test.py": "with story('Add Book'):\n    pass\n"}})
            expect(_saved(self.root, result)).to(equal(["story_tests/fill-cart/add-book/add_book_story.test.py"]))

        with context("that names a file the fidelity does not declare"):
            with before.each:
                self.code = RenderedCode(self.root, ["story_tests/{epic}/{story}/{story_snake}_story.test.py"], Format("python"))
                self.content = {"story_tests/fill-cart/add-book/add_book_story.test.py": "pass\n", "tests/fill-cart/add_books_story.test.py": "pass\n"}

            with it("should refuse, naming the file"):
                expect(lambda: self.code.save({"format": "python", "content": self.content})).to(raise_error(RenderHasNoDeclaredPlace, contain("tests/fill-cart/add_books_story.test.py")))

            with it("should save none of the files"):
                try:
                    self.code.save({"format": "python", "content": self.content})
                except RenderHasNoDeclaredPlace:
                    pass
                expect((self.root / "story_tests").exists()).to(equal(False))

    with context("with one text rendered from one source file"):
        with before.each:
            self.source = self.root / "bookshop" / "src" / "CartView.tsx"
            self.source.parent.mkdir(parents=True)
            self.source.write_text("export function CartView(): void {}\n", encoding="utf-8")

        with it("should save it beside the source, under the name the fidelity declares for the format"):
            code = RenderedCode(self.root, ["**/*View.jsx"], Format("javascript"), self.source, ["**/*View.tsx", "**/*View.jsx"])
            expect(_saved(self.root, code.save({"format": "javascript", "content": VIEW_CODE}))).to(equal(["bookshop/src/CartView.jsx"]))

        with context("whose declared path does not say how the source's name joins it"):
            with it("should refuse, naming the declared path"):
                spec = self.root / "cart_spec.py"
                spec.write_text("pass\n", encoding="utf-8")
                code = RenderedCode(self.root, ["**/*spec.ts"], Format("typescript"), spec, ["**/*_spec.py", "**/*spec.ts"])
                expect(lambda: code.save({"format": "typescript", "content": "describe()\n"})).to(raise_error(RenderHasNoDeclaredPlace, contain("**/*spec.ts")))

        with context("that is a Python spec, for a fidelity that declares how a TypeScript spec is named"):
            with it("should carry the spec's own name across: cart_spec.py is saved as cart.spec.ts"):
                spec = self.root / "cart_spec.py"
                spec.write_text("pass\n", encoding="utf-8")
                code = RenderedCode(self.root, ["**/*.spec.ts"], Format("typescript"), spec, ["**/*_spec.py", "**/*.spec.ts"])
                expect(_saved(self.root, code.save({"format": "typescript", "content": "describe()\n"}))).to(equal(["cart.spec.ts"]))

        with context("that is a document in a .context folder, named for its scope"):
            with it("should save the code in the folder the .context sits in, named for that scope"):
                document = self.root / "src" / "ordering" / ".context" / "ordering-bdd-realization.md"
                document.parent.mkdir(parents=True)
                document.write_text("# Ordering\n", encoding="utf-8")
                code = RenderedCode(self.root, ["**/*_spec.py"], Format("python"), document, [".context/{scope}-bdd-realization.md", "**/*_spec.py"])
                expect(_saved(self.root, code.save({"format": "python", "content": "pass\n"}))).to(equal(["src/ordering/ordering_spec.py"]))

        with context("that is an aggregate's code, for a fidelity that declares a file for each aggregate"):
            with it("should save the code as the same aggregate's file in the other language"):
                book = self.root / "catalogue" / "book" / "book.ts"
                book.parent.mkdir(parents=True)
                book.write_text("class Book {}\n", encoding="utf-8")
                declared = ["{bounded_context}/{aggregate}/{aggregate}.py", "{bounded_context}/{aggregate}/{aggregate}.ts"]
                code = RenderedCode(self.root, declared[:1], Format("python"), book, declared)
                expect(_saved(self.root, code.save({"format": "python", "content": "class Book:\n    pass\n"}))).to(equal(["catalogue/book/book.py"]))

        with context("that is a sketch, whose one section carries a name the sketch does not write"):
            with it("should name the code for the sketch and save it beside the sketch, as the fidelity declares a module's file"):
                sketch = self.root / "design" / "cart-sketch.md"
                sketch.parent.mkdir(parents=True)
                sketch.write_text("Cart\n  owner\n", encoding="utf-8")
                code = RenderedCode(self.root, ["{module}/", "{module}/{module}.py"], Format("python"), sketch, ["{module}/{module}.py"], "cart")
                result = code.save({"format": "python", "content": "# === KnowledgeGraph ===\n\nclass Cart:\n    pass\n"})
                expect(_saved(self.root, result)).to(equal(["design/cart/cart.py"]))

        with context("that no declared path of the fidelity names"):
            with it("should refuse, naming the source"):
                notes = self.root / "notes.md"
                notes.write_text("# Notes\n", encoding="utf-8")
                code = RenderedCode(self.root, ["**/*View.jsx"], Format("javascript"), notes, ["**/*View.tsx", "**/*View.jsx"])
                expect(lambda: code.save({"format": "javascript", "content": VIEW_CODE})).to(raise_error(RenderHasNoDeclaredPlace, contain("notes.md")))
