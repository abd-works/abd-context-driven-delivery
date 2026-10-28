"""A class model rendered to code keeps every body it can, in every language, through one render."""

import sys
from pathlib import Path

from expects import be_true, contain, equal, expect
from mamba import before, context, description, it

_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import cdd_guidance.practices  # noqa: F401
from harness.agent_tools.agent_tools import AgentToolSet
from cdd_guidance.practices.clean_engineering.model.code_body import CodeBody, CodeLanguage

_TOOLSET = "cdd_guidance.practices.clean_engineering.clean_engineering:CleanEngineering"

_CART_PYTHON = '''\
from __future__ import annotations

from decimal import Decimal


class Cart:
    """A shopper's cart."""

    items: list

    def __init__(self, items: list) -> None:
        self.items = items

    def total(self) -> Decimal:
        """The sum of the item prices."""
        # an empty cart totals zero
        return sum((item.price for item in self.items), Decimal("0"))

    def add(self, item: object) -> None:
        self.items.append(item)
'''

_CART_TYPESCRIPT = """\
class Cart {
  items: Item[];

  constructor(items: Item[]) {
    this.items = items;
  }

  total(): number {
    // an empty cart totals zero
    return this.items.reduce((sum, item) => sum + item.price, 0);
  }
}
"""

_CART_MARKDOWN = """\
# Shop

*Shop* is the cart module.

## Cart

*Cart* holds line items.

Cart(items: list)
------
items: list
----
total(): Decimal
empty(): None
"""

_PYTHON_TOTAL = 'return sum((item.price for item in self.items), Decimal("0"))'
_TYPESCRIPT_TOTAL = "return this.items.reduce((sum, item) => sum + item.price, 0);"


def _render(target: str, content: str, source: str, previous: str = "") -> str:
    toolset = type(AgentToolSet.instantiate(_TOOLSET))(fidelity="model")
    return toolset.render(format=target, content=content, source=source, previous=previous)["content"]


def _bodies(language: str, text: str) -> dict:
    from cdd_guidance.practices.clean_engineering.clean_engineering import CleanEngineering

    adapter = CleanEngineering(fidelity="model")._live_adapter(language)
    model = adapter.parse(text)
    return {
        f"{oclass.name}.{operation.name}": operation.body.text
        for oclass in model.classes
        for operation in oclass.operations
    }


with description("an operation body"):
    with context("that was read from python"):
        with before.each:
            self.body = CodeBody("self.items.append(item)", CodeLanguage.named("python"))

        with context("that is written back in python"):
            with it("should keep the statements as read"):
                expect(self.body.lines_in(CodeLanguage.named("python"), "        ", "raise NotImplementedError")).to(
                    equal(["        self.items.append(item)"])
                )

        with context("that is written in typescript"):
            with before.each:
                typescript = CodeLanguage.named("typescript")
                self.lines = self.body.lines_in(typescript, "    ", typescript.unfinished)

            with it("should keep the python statements commented out under a note naming python"):
                expect(self.lines[:2]).to(equal(["    // python body to translate:", "    // self.items.append(item)"]))

            with it("should end with the line that fails until the body is written"):
                expect(self.lines[-1]).to(equal(f"    {CodeLanguage.named('typescript').unfinished}"))

    with context("that is only a placeholder"):
        with it("should be empty"):
            expect(CodeBody("...", CodeLanguage.named("python")).is_empty).to(be_true)

    with context("that is empty"):
        with it("should write only the line that marks it still to write"):
            expect(CodeBody("", None).lines_in(CodeLanguage.named("java"), "    ", "// BDD: SIGNATURE")).to(
                equal(["    // BDD: SIGNATURE"])
            )

    with context("that is kept against the previous file's body"):
        with before.each:
            self.python = CodeLanguage.named("python")
            self.previous = CodeBody("return 1", self.python)

        with context("with a model body in the target language"):
            with it("should keep the model body"):
                newer = CodeBody("return 2", self.python)
                expect(newer.in_language_of(self.previous, self.python).text).to(equal("return 2"))

        with context("with a model body from another language"):
            with it("should keep the previous file's body"):
                other = CodeBody("return 2;", CodeLanguage.named("typescript"))
                expect(other.in_language_of(self.previous, self.python).text).to(equal("return 1"))


with description("a class model rendered to code"):
    with context("that was read from a python file"):
        with context("that is rendered back to python"):
            with before.each:
                self.rendered = _render("python", _CART_PYTHON, "python")

            with it("should keep each operation's statements"):
                expect(self.rendered).to(contain(f"        {_PYTHON_TOTAL}"))

            with it("should keep the comments inside an operation"):
                expect(self.rendered).to(contain("        # an empty cart totals zero"))

            with it("should keep the imports above the first class"):
                expect(self.rendered).to(contain("from decimal import Decimal"))

            with it("should read back the same bodies"):
                expect(_bodies("python", self.rendered)).to(equal(_bodies("python", _CART_PYTHON)))

            with it("should render the same text again"):
                expect(_render("python", self.rendered, "python")).to(equal(self.rendered))

        with context("that is rendered to typescript"):
            with before.each:
                self.rendered = _render("typescript", _CART_PYTHON, "python")

            with it("should carry each python body as a commented note inside its operation"):
                expect(self.rendered).to(contain(f"    // {_PYTHON_TOTAL}"))

            with it("should make each operation fail until it is written"):
                expect(self.rendered).to(contain(f"    {CodeLanguage.named('typescript').unfinished}"))

    with context("that was read from a typescript file"):
        with context("that is rendered back to typescript"):
            with before.each:
                self.rendered = _render("typescript", _CART_TYPESCRIPT, "typescript")

            with it("should keep each method's statements"):
                expect(self.rendered).to(contain(f"    {_TYPESCRIPT_TOTAL}"))

            with it("should read back the same bodies"):
                expect(_bodies("typescript", self.rendered)).to(equal(_bodies("typescript", _CART_TYPESCRIPT)))

        with context("that is rendered to java"):
            with it("should carry each typescript body as a commented note inside its method"):
                expect(_render("java", _CART_TYPESCRIPT, "typescript")).to(contain(f"        // {_TYPESCRIPT_TOTAL}"))

    with context("that was read from markdown"):
        with context("that is rendered to python with the previous python file"):
            with before.each:
                self.rendered = _render("python", _CART_MARKDOWN, "markdown", previous=_CART_PYTHON)

            with it("should keep the previous file's body for an operation the model still has"):
                expect(self.rendered).to(contain(f"        {_PYTHON_TOTAL}"))

            with it("should make an operation new to the model fail until it is written"):
                expect(self.rendered).to(contain("    def empty(self) -> None:\n        raise NotImplementedError"))

        with context("that is rendered to each code language"):
            with it("should make every operation fail until it is written, in each language"):
                languages = ("python", "typescript", "javascript", "java")
                unfinished = [
                    CodeLanguage.named(language).unfinished in _render(language, _CART_MARKDOWN, "markdown")
                    for language in languages
                ]
                expect(unfinished).to(equal([True] * len(languages)))
