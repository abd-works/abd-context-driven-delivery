"""BDD specs for the settings block at the top of a template or example file."""
from expects import equal, expect
from mamba import context, description, it

from harness.markdown.front_matter import FrontMatter


with description("a file's settings block"):
    with context("written as a yaml block"):
        with it("should give the settings between its fences"):
            expect(FrontMatter("---\nfidelity: model\n---\n# Model\n").settings).to(equal("fidelity: model"))

        with it("should give the text after it as the content"):
            expect(FrontMatter("---\nfidelity: model\n---\n\n# Model\n").content).to(equal("# Model\n"))

        with it("should give each setting by its name, without quotes"):
            expect(FrontMatter("---\ndescription: \"Rules\"\nalwaysApply: true\n---\nBody\n").fields).to(
                equal({"description": "Rules", "alwaysApply": "true"})
            )

    with context("written as comment lines in a code template"):
        with it("should give the settings without their comment marks"):
            expect(FrontMatter("# ---\n# format: python\n# ---\nclass Model: ...\n").settings).to(equal("format: python"))

    with context("whose fences hold a markdown heading"):
        with it("should leave the text whole, since the fences are horizontal rules"):
            text = "---\n## Domain terms\n---\nBody\n"
            expect(FrontMatter(text).content).to(equal(text))

    with context("that is missing"):
        with it("should give no settings"):
            expect(FrontMatter("# Model\n").settings).to(equal(""))
