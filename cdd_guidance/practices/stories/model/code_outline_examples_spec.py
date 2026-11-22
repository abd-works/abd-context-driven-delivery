"""Mamba spec: a scenarios file with a Scenario Outline and example tables, rendered to code and back.

The code a render writes is valid in its language, holds each example's row, and names no example data its scenarios
file does not hold."""

import ast
import re

from expects import be_empty, be_true, contain, equal, expect
from mamba import before, context, description, it

from cdd_guidance.practices.stories.model.markdown.nodes import MarkdownStory, MarkdownStoryModel
from cdd_guidance.practices.stories.model.python.python_story_model import PythonStoryModel
from cdd_guidance.practices.stories.model.typescript.typescript_story_model import TypeScriptStoryModel

_SCENARIOS = """## Story: Change Cart Line Quantity

### Examples

#### cart

| cart | example | lines | total |
| --- | --- | --- | --- |
| cart | cart with Tiny Tales | 1 x Tiny Tales | 5 |

### Background

*Given* the Bookshop sells Tiny Tales

### Behaviors

#### Scenario Outline: Cart total follows the quantity

*Given* the Customer has ++Cart++ ++cart with Tiny Tales++
*When* the Customer changes the ++Cart Line++ of Tiny Tales to <quantity> copies
*Then* the Cart total is <total>

#### Examples

| scenario | quantity | total |
| --- | --- | --- |
| one copy | 1 | 5 |
| two copies | 2 | 10 |
"""

_IMPORTED_NAMES = re.compile(r"^(?:from examples import (?P<python>.+)|import \{(?P<typescript>[^}]+)\} from \"\./examples\";?)$", re.M)


def _rendered(format: type) -> dict:
    """The files the scenarios render to in format, a code format's story model, by path."""
    return format(tests_root="tests").render(MarkdownStoryModel().parse(_SCENARIOS))


def _story_test(files: dict) -> str:
    return next(text for path, text in files.items() if "_story.test." in path)


def _imported_examples(text: str) -> list:
    found = _IMPORTED_NAMES.search(text)
    return [name.strip() for name in (found.group("python") or found.group("typescript")).split(",")] if found else []


def _markdown_back_from(format: type) -> str:
    """The story's section of a scenarios file, written from the story read back from format's code."""
    story = format(tests_root="tests").parse(_rendered(format)).descendants.stories()[0]
    return MarkdownStory.copy_of(story).document_text()


def _outline_back_from(format: type):
    """The outline as markdown reads it after a trip through format."""
    return MarkdownStoryModel().parse(_markdown_back_from(format)).descendants.stories()[0].scenarios[0]


with description("a scenarios file with a Scenario Outline whose rows sit under an Examples heading") as self:
    with context("that is read from markdown"):
        with before.each:
            self.outline = MarkdownStoryModel().parse(_SCENARIOS).descendants.stories()[0].scenarios[0]

        with it("should name each row by its scenario column"):
            expect(list(self.outline.examples)).to(equal(["one copy", "two copies"]))

    with context("that is rendered to Python"):
        with before.each:
            self.python = _story_test(_rendered(PythonStoryModel))

        with it("should be Python that parses"):
            expect(ast.parse(self.python) is not None).to(be_true)

        with it("should import no example whose name is no Python name"):
            expect([name for name in _imported_examples(self.python) if not name.isidentifier()]).to(be_empty)

        with it("should hold each row's values"):
            expect(self.python).to(contain('"two copies": {"scenario": "two copies", "quantity": "2", "total": "10"}'))

        with context("and read back into markdown"):
            with before.each:
                self.back = _outline_back_from(PythonStoryModel)

            with it("should still be a Scenario Outline"):
                expect(self.back.is_outline).to(be_true)

            with it("should hold each row under the columns it was written with"):
                expect(self.back.examples.table()).to(equal([
                    {"example": "one copy", "scenario": "one copy", "quantity": "1", "total": "5"},
                    {"example": "two copies", "scenario": "two copies", "quantity": "2", "total": "10"},
                ]))

    with context("that is rendered to TypeScript"):
        with before.each:
            self.files = _rendered(TypeScriptStoryModel)
            self.typescript = _story_test(self.files)

        with it("should import no example whose name is no TypeScript name"):
            expect([name for name in _imported_examples(self.typescript) if not re.fullmatch(r"[A-Za-z_$][\w$]*", name)]).to(be_empty)

        with it("should import the background helper its story calls"):
            expect(self.typescript).to(contain('import { background, scenario, story } from "tests/story-test";'))

        with it("should write no examples file holding data the scenarios file does not name"):
            expect([path for path in self.files if "/examples/" in path]).to(be_empty)

        with context("and read back into markdown"):
            with before.each:
                self.back = _outline_back_from(TypeScriptStoryModel)

            with it("should still be a Scenario Outline"):
                expect(self.back.is_outline).to(be_true)

            with it("should hold each row's values"):
                expect(self.back.examples["two copies"].cells()).to(equal({"scenario": "two copies", "quantity": "2", "total": "10"}))


with description("a scenarios file whose story shares a table of examples under a group heading") as self:
    with context("that is rendered to Python and read back into markdown"):
        with before.each:
            self.back = _markdown_back_from(PythonStoryModel)

        with it("should write the table under its group with the columns it was written with"):
            expect(self.back).to(contain("#### cart\n\n| cart | example | lines | total |\n| --- | --- | --- | --- |\n| cart | cart with Tiny Tales | 1 x Tiny Tales | 5 |\n"))
