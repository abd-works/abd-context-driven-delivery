"""A workspace story map reads scenario files once while attaching them."""

from pathlib import Path
import tempfile

from expects import contain, equal, expect, have_len
from mamba import before, context, description, it

from cdd_guidance.practices.stories.model.markdown.nodes import MarkdownScenario, MarkdownStoryModel


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
            original = MarkdownScenario.from_workspace.__func__

            def counting(cls, root, *args, **kwargs):
                calls.append(Path(root))
                return original(cls, root, *args, **kwargs)

            MarkdownScenario.from_workspace = classmethod(counting)
            try:
                MarkdownStoryModel.from_workspace(self.root)
            finally:
                MarkdownScenario.from_workspace = classmethod(original)
            expect(calls).to(have_len(1))

        with it("should report each scenario file while reading"):
            reported = []
            MarkdownStoryModel.from_workspace(self.root, on_file=reported.append)
            expect(reported).to(contain("stories/place-order.md"))
