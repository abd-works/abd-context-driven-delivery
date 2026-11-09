"""A workspace story map reads scenario files once while attaching them."""

from pathlib import Path
import tempfile

from expects import be, contain, equal, expect, have_len
from mamba import before, context, description, it

from cdd_guidance.practices.stories.model.markdown.nodes import MarkdownScenario, MarkdownStoryModel
from cdd_guidance.practices.stories.model.source_location import SourceLocation


def _stories(model):
    found = []

    def walk(epic):
        found.extend(epic.stories)
        for child in epic.epics:
            walk(child)

    for epic in model.epics:
        walk(epic)
    return found


with description("a markdown story map loaded from a workspace") as self:
    with context("that has several stories and one scenario file"):
        with before.each:
            self.folder = tempfile.TemporaryDirectory()
            root = Path(self.folder.name)
            (root / "story-map.md").write_text(
                "\n".join(
                    [
                        "(E) Place Order",
                        "    (E) Submit Order",
                        "        (S) Customer --> Place Order",
                        "        (S) Customer --> Cancel Order",
                        "        (S) Customer --> Refund Order",
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            stories = root / "stories"
            stories.mkdir()
            (stories / "place-order.md").write_text(
                "\n".join(
                    [
                        "## Story: Place Order",
                        "",
                        "### Scenario: Happy path",
                        "*Given* a cart",
                        "*When* the customer checks out",
                        "*Then* the order is placed",
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            self.root = root

        with it("should attach the scenario to the story it names"):
            loaded = MarkdownStoryModel.from_workspace(self.root)
            named = {story.name: story for story in _stories(loaded)}
            expect(named["Place Order"].scenarios[0].name).to(equal("Happy path"))

        with it("should read scenario files once for every story"):
            calls = []
            original = MarkdownScenario.sections_in.__func__

            def counting(cls, root, *args, **kwargs):
                calls.append(Path(root))
                return original(cls, root, *args, **kwargs)

            MarkdownScenario.sections_in = classmethod(counting)
            try:
                MarkdownStoryModel.from_workspace(self.root)
            finally:
                MarkdownScenario.sections_in = classmethod(original)
            expect(calls).to(have_len(1))

        with it("should report each scenario file while reading"):
            reported = []
            MarkdownStoryModel.from_workspace(self.root, on_file=reported.append)
            expect(reported).to(contain("stories/place-order.md"))

        with it("should give the story the scenario file's section names a scenario its story as its parent"):
            loaded = MarkdownStoryModel.from_workspace(self.root)
            named = {story.name: story for story in _stories(loaded)}
            expect(named["Place Order"].scenarios[0].parent).to(be(named["Place Order"]))

    with context("whose stories are written as headings"):
        with before.each:
            self.folder = tempfile.TemporaryDirectory()
            root = Path(self.folder.name)
            (root / "story-map.md").write_text(
                "\n".join(["# Shop", "", "## Checkout", "", "### Pay By Card", "", "## Story: Refund Order", ""]),
                encoding="utf-8",
            )
            loaded = MarkdownStoryModel.from_workspace(root)
            self.named = {story.name: story for story in _stories(loaded)}
            self.loaded = loaded

        with it("should give the epic the line it was read on"):
            expect(self.loaded.epics[0].source).to(equal(SourceLocation("story-map.md", 1)))

        with it("should give the sub-epic the line it was read on"):
            expect(self.loaded.epics[0].epics[0].source).to(equal(SourceLocation("story-map.md", 3)))

        with it("should give a story written as a heading under a sub-epic the line it was read on"):
            expect(self.named["Pay By Card"].source).to(equal(SourceLocation("story-map.md", 5)))

        with it("should give a story written as a Story heading the line it was read on"):
            expect(self.named["Refund Order"].source).to(equal(SourceLocation("story-map.md", 7)))

    with context("whose thin slicing sits only in a folder a scan never enters"):
        with before.each:
            self.folder = tempfile.TemporaryDirectory()
            root = Path(self.folder.name)
            (root / "story-map.md").write_text("(E) Shop\n    (S) Customer --> Pay By Card\n", encoding="utf-8")
            vendored = root / "node_modules" / "kit"
            vendored.mkdir(parents=True)
            (vendored / "thin-slicing.md").write_text(
                "### Increment 1: Pay\n**Stories:**\n- Pay By Card\n", encoding="utf-8"
            )
            self.loaded = MarkdownStoryModel.from_workspace(root)

        with it("should read no increments"):
            expect(self.loaded.increments).to(have_len(0))

    with context("whose thin slicing names its stories"):
        with before.each:
            self.folder = tempfile.TemporaryDirectory()
            root = Path(self.folder.name)
            (root / "story-map.md").write_text("(E) Shop\n    (S) Customer --> Pay By Card\n", encoding="utf-8")
            (root / "thin-slicing.md").write_text(
                "### Increment 1: Pay\n**Stories:**\n- Pay By Card\n- Refund Order\n", encoding="utf-8"
            )
            self.loaded = MarkdownStoryModel.from_workspace(root)

        with it("should deliver the map's own story each name gives"):
            expect(self.loaded.increments[0].stories[0]).to(be(_stories(self.loaded)[0]))

        with it("should leave out a name the map has no story for"):
            expect(self.loaded.increments[0].stories).to(have_len(1))
