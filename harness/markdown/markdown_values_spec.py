"""Specs for the values an owner's code holds and its markdown names by a marker: the markdown is filled from them as it
is read, so a number a check holds is typed in the code alone."""
import tempfile
from pathlib import Path

from expects import equal, expect
from mamba import before, context, description, it

from harness.markdown.markdown import Markdown, MarkdownScope


class _Cart:
    """An owner of markdown, as small as one can be."""


with description("markdown whose owner holds a value its text names by a marker") as self:
    with before.each:
        self.folder = Path(tempfile.mkdtemp(prefix="markdown-values-"))
        (self.folder / "cart.md").write_text("## Overview\n\nA cart holds {{cart.most_lines}} lines, and {{ticket}} names it.\n", encoding="utf-8")

    with context("read in a scope that holds the value"):
        with it("should write the value in the marker's place"):
            scope = MarkdownScope(self.folder, "cart", values=(("cart.most_lines", "9"),))
            expect(Markdown(_Cart(), "overview", scope).extract()).to(equal("## Overview\n\nA cart holds 9 lines, and {{ticket}} names it."))

        with it("should leave a marker the owner holds no value for, which an instruction fills from its call"):
            scope = MarkdownScope(self.folder, "cart", values=(("cart.most_lines", "9"),))
            expect("{{ticket}}" in Markdown(_Cart(), "overview", scope).extract()).to(equal(True))

    with context("read in a scope that holds no value"):
        with it("should read the text as written"):
            expect("{{cart.most_lines}}" in Markdown(_Cart(), "overview", MarkdownScope(self.folder, "cart")).extract()).to(equal(True))
