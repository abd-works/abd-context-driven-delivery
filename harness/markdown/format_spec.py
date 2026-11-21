import json
from pathlib import Path

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

    with description("whose files carry an ending before their extension"):
        with it("should name a file that carries the ending"):
            expect(Format("sketch").names(Path("orders-sketch.md"))).to(equal(True))

        with it("should not name a file without the ending"):
            expect(Format("sketch").names(Path("orders.md"))).to(equal(False))

    with description("whose files carry no ending"):
        with it("should name no file by an ending"):
            expect(Format("markdown").names(Path("orders.md"))).to(equal(False))

    with description("that is a code format"):
        with it("should say it is code"):
            expect(Format("javascript").is_code).to(equal(True))

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

    with description("that is a Claude Whiteboard board"):
        with it("should be picked in the diagram group, beside drawio"):
            expect((Format("whiteboard").group, Format("whiteboard").is_code)).to(equal(("diagram", False)))

        with it("should name its file extension"):
            expect(Format("whiteboard").extension).to(equal(".whiteboard"))

    with description("that is a Claude Design canvas"):
        with it("should be picked in the canvas group, after the code"):
            expect((Format("claude_design").group, Format("claude_design").group_order)).to(equal(("canvas", 3)))

    with description("among a fidelity's files"):
        with it("should show markdown, then code, then diagrams, then the canvas"):
            names = sorted(["claude_design", "drawio", "python", "markdown"], key=lambda name: Format(name).file_order)
            expect(names).to(equal(["markdown", "python", "drawio", "claude_design"]))

        with it("should show a format in no group after them"):
            expect(Format("sub").file_order).to(equal(4))

    with description("that is in no group"):
        with it("should be a group of its own, after the others"):
            expect((Format("sub").group, Format("sub").group_order)).to(equal(("sub", 4)))

    # Requested 2026-11-16: thin_slice and realization are files a fidelity writes, not formats a person picks.
    with description("that is a fidelity output named for what it holds, such as thin_slice"):
        with it("should not be offered for a person to pick"):
            expect([Format("thin_slice").is_offered, Format("realization").is_offered]).to(equal([False, False]))

    with description("that is in a group a person picks by"):
        with it("should be offered for a person to pick"):
            expect([Format(name).is_offered for name in ("markdown", "drawio", "whiteboard", "python", "html", "claude_design")]).to(equal([True] * 6))

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

    with description("naming the file it was read from"):
        with it("should be a sketch file's name without its sketch ending"):
            expect(Format("sketch").stem_of(Path("work/orders-sketch.md"))).to(equal("orders"))

        with it("should be any other file's own name without its extension"):
            expect(Format("markdown").stem_of(Path("work/orders-sketch.md"))).to(equal("orders-sketch"))
