import json

from mamba import description, it
from expects import equal, expect

from harness.markdown.format import Format


with description("a format") as self:
    with description("named by its short name"):
        with it("should go by its own name"):
            expect(Format("md").name).to(equal("markdown"))

        with it("should ignore case"):
            expect(Format("PY").name).to(equal("python"))

    with description("read from a file's extension"):
        with it("should be the format that extension belongs to"):
            expect(Format.from_extension(".ts").name).to(equal("typescript"))

    with description("that is a code format"):
        with it("should say it is code"):
            expect(Format("java").is_code).to(equal(True))

        with it("should keep its templates in the folder of its short name"):
            expect(Format("javascript").template_folder).to(equal("js"))

        with it("should end its templates with its extension"):
            expect(Format("python").template_extension).to(equal(".py"))

        with it("should be picked in the code group"):
            expect(Format("python").group).to(equal("code"))

    with description("that is a diagram format"):
        with it("should not say it is code"):
            expect(Format("drawio").is_code).to(equal(False))

        with it("should have no template extension, so its template is found by name"):
            expect(Format("drawio").template_extension).to(equal(""))

        with it("should still name its file extension"):
            expect(Format("drawio").extension).to(equal(".drawio"))

        with it("should be picked in the diagram group, which comes first"):
            expect((Format("drawio").group, Format("drawio").group_order)).to(equal(("diagram", 0)))

    with description("among a fidelity's files"):
        with it("should show markdown, then code, then diagrams"):
            names = sorted(["drawio", "python", "markdown"], key=lambda name: Format(name).file_order)
            expect(names).to(equal(["markdown", "python", "drawio"]))

        with it("should show a format in no group after them"):
            expect(Format("sub").file_order).to(equal(3))

    with description("that is in no group"):
        with it("should be a group of its own, after the others"):
            expect((Format("sub").group, Format("sub").group_order)).to(equal(("sub", 3)))

    with description("that was not given"):
        with it("should have no name"):
            expect(Format(None).name).to(equal(""))

    with description("held by its owner"):
        with it("should compare equal to its own name"):
            expect(Format("md")).to(equal("markdown"))

        with it("should be written to JSON as its own name"):
            expect(json.dumps({"format": Format("py")})).to(equal('{"format": "python"}'))

        with it("should stay the same format when made again from itself"):
            expect(Format(Format("ts")).is_code).to(equal(True))
