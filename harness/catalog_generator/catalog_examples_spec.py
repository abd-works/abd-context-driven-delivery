"""BDD specs for the example files the catalog shows for a fidelity."""
import tempfile
from pathlib import Path
from types import SimpleNamespace

from expects import contain, equal, expect
from mamba import before, context, description, it

from harness.catalog_generator.catalog_examples import CatalogFidelity, ExampleMarkdown

_PNG = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489"
    "0000000a49444154789c63000100000500010d0a2db40000000049454e44ae426082"
)


def _fidelity(name: str, files: dict) -> SimpleNamespace:
    folder = Path(tempfile.mkdtemp())
    examples = folder / "catalog-examples"
    examples.mkdir()
    for file_name, content in files.items():
        if isinstance(content, bytes):
            (examples / file_name).write_bytes(content)
        else:
            (examples / file_name).write_text(content, encoding="utf-8")
    return SimpleNamespace(name=name, overview="", section="", practice_guidance=SimpleNamespace(module_dir=folder))


with description("a fidelity's catalog examples"):
    with context("with a png named for the fidelity"):
        with before.all:
            self.html = CatalogFidelity(_fidelity("story_map", {"story_map.png": _PNG})).examples_html

        with it("should show it as an image embedded in the page"):
            expect("data:image/png;base64," in self.html).to(equal(True))

        with it("should not show it as source text"):
            expect("<pre>" in self.html).to(equal(False))

    with context("with a file named for the fidelity in kebab spelling"):
        with it("should show it on the fidelity page"):
            fidelity = _fidelity("bounded_context", {"bounded-context.md": "# Bounded context\n"})
            expect(CatalogFidelity(fidelity).examples_html).to(contain("bounded-context.md"))

    with context("with a diagram and the markdown it was drawn from"):
        with before.all:
            files = {"story_map.drawio": "<mxfile/>", "story_map.md": "# Map\n"}
            self.fidelity = CatalogFidelity(_fidelity("story_map", files))

        with it("should show in the approach panel only files the fidelity page shows"):
            expect(set(self.fidelity.panel_example_files) <= set(self.fidelity.example_files)).to(equal(True))

        with it("should show the diagram in the approach panel"):
            expect([path.name for path in self.fidelity.panel_example_files]).to(equal(["story_map.drawio"]))

    with context("with an overview that opens with a paragraph"):
        with it("should give that paragraph as its opening"):
            fidelity = _fidelity("story_map", {})
            fidelity.overview = "#### Overview\n\nScope the solution.\nKeep it small.\n\nMore later."
            expect(CatalogFidelity(fidelity).opening).to(equal("Scope the solution.\nKeep it small."))


with description("a markdown example"):
    with context("that holds a horizontal rule mid-document"):
        with before.all:
            self.html = ExampleMarkdown(
                "---\n"
                "## fidelity: [specification]\n"
                "format: md\n"
                "\n"
                "# Story Scenarios\n"
                "\n"
                "### Domain terms\n"
                "\n"
                "- `Offer` — qualifies products\n"
                "\n"
                "---\n"
                "\n"
                "## Behaviors\n"
                "\n"
                "#### Scenario: User sees an offer\n"
                "\n"
                "*Given* a `Client`\n"
                "  *When* the rep opens **offers available** on `[ client dashboard ]` *(*`Offer`*.scan)*\n"
                "  *Then* the rep sees `[ offer panel ]`\n"
            ).html

        with it("should keep the content before the rule"):
            expect("Domain terms" in self.html).to(equal(True))

        with it("should keep the content after the rule"):
            expect("Scenario: User sees an offer" in self.html).to(equal(True))

        with it("should write an operation's parentheses as code"):
            expect("(`Offer`.scan)" in self.html or "<code>Offer</code>.scan" in self.html).to(equal(True))

    with context("that marks domain terms"):
        with before.all:
            self.html = ExampleMarkdown(
                "#### Scenario: Example\n\n*Given* ++`Client`++ holds ++Already held++\n  *When* ++`Offer`++.scan runs\n"
            ).html

        with it("should unwrap the markers"):
            expect("++" in self.html).to(equal(False))

        with it("should keep a backticked term as code"):
            expect("<code>Client</code>" in self.html).to(equal(True))

        with it("should make a plain term bold"):
            expect("<strong>Already held</strong>" in self.html).to(equal(True))
