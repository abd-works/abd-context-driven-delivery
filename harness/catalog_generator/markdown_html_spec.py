"""BDD specs for markdown written as catalog HTML."""
from pathlib import Path

from expects import equal, expect
from mamba import context, description, it

from harness.catalog_generator.markdown_html import MarkdownHtml

_REPO_ROOT = Path(__file__).resolve().parents[2]


with description("markdown written as catalog HTML"):
    with context("with trailing double spaces in a paragraph"):
        with it("should break the line there"):
            expect("<br>" in MarkdownHtml("*When* one step  \n*Then* another step").html).to(equal(True))

        with it("should write the emphasis as HTML"):
            expect("*When*" in MarkdownHtml("*When* one step  \n*Then* another step").html).to(equal(False))

    with context("with the scenarios catalog example"):
        with it("should put its scenario steps on separate lines"):
            source = (
                _REPO_ROOT / "cdd_guidance" / "practices" / "stories" / "catalog-examples" / "scenarios.md"
            ).read_text(encoding="utf-8")
            expect(MarkdownHtml(source.split("---", 2)[-1]).html.count("<br>") > 5).to(equal(True))

    with context("with a yaml settings fence"):
        with it("should leave the settings out"):
            expect(MarkdownHtml("Intro\n\n```yaml\nstage: discovery\n```\n").html).to(equal("<p>Intro</p>"))

    with context("with a code fence left open at the end"):
        with it("should show the code"):
            expect(MarkdownHtml("```python\nx = 1\n").html).to(equal("<pre><code>x = 1\n</code></pre>"))

    with context("with a pipe table"):
        with it("should leave the table out by default"):
            expect(MarkdownHtml("| a | b |\n| - | - |\n| 1 | 2 |\n").html).to(equal(""))

        with it("should write the table when tables are asked for"):
            html = MarkdownHtml("| a | b |\n| - | - |\n| 1 | 2 |\n", include_tables=True).html
            expect("<td>1</td>" in html).to(equal(True))

    with context("with a link whose label is code"):
        with it("should keep the code inside the link"):
            expect(MarkdownHtml("See [`guide`](a.md).").html).to(equal('<p>See <a href="a.md"><code>guide</code></a>.</p>'))

    with context("with a Guidance section"):
        with it("should mark the section's body for its accent colour"):
            html = MarkdownHtml("## Guidance\n\n**Lead** in.\n\n## Rules\n\nA rule.").guidance_html
            expect('<h2>Guidance</h2><div class="fidelity-guidance-body">' in html).to(equal(True))
