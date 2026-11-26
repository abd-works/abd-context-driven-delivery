"""Mamba spec for the links a rendered story map gives each story: the file that writes its scenarios, in every layout a
project keeps them in. A story's own file is found by its name; a file holding several stories, a sub-epic's markdown,
a story test or a shared story file in code, is found by the story it names, and a markdown one is linked at the
story's heading."""

import tempfile
from pathlib import Path

from expects import contain, equal, expect
from mamba import after, before, description, it

from cdd_guidance.practices.stories.model.drawio.nodes import DrawIOStoryMap
from cdd_guidance.practices.stories.model.fixtures.scenario_layouts import (
    MAP,
    MAP_TEXT,
    ONE_STORY_PER_FILE,
    PYTHON_ONLY,
    SUB_EPIC_FILE_HOLDING_BOTH,
    TYPESCRIPT_ONLY,
)
from cdd_guidance.practices.stories.model.markdown.links import StoryMapLinks
from cdd_guidance.practices.stories.model.markdown.nodes import MarkdownStoryMap
from harness.guidance.practice_formats import Written


class _Project:
    """A project written in one layout, its story map read from its markdown."""

    def __init__(self, files: dict[str, str]) -> None:
        self._folder = tempfile.TemporaryDirectory()
        self.root = Path(self._folder.name)
        (self.root / ".git").mkdir()
        for name, text in {MAP: MAP_TEXT, **files}.items():
            (self.root / name).parent.mkdir(parents=True, exist_ok=True)
            (self.root / name).write_text(text, encoding="utf-8")
        self.story_map = MarkdownStoryMap().parse(MAP_TEXT)
        self.links = StoryMapLinks(self.story_map, self.root / ".context")

    def link_of(self, name: str) -> str:
        return self.links.story_file(next(story for story in self.story_map.descendants.stories() if story.name == name))

    def drawn(self) -> str:
        return DrawIOStoryMap().render(self.story_map, Written(folder=self.root / ".context"))

    def close(self) -> None:
        self._folder.cleanup()


with description("the story files a rendered story map links each story to") as self:
    with before.all:
        self.layouts = {
            "one story per file": _Project(ONE_STORY_PER_FILE),
            "a sub-epic file": _Project(SUB_EPIC_FILE_HOLDING_BOTH),
            "Python alone": _Project(PYTHON_ONLY),
            "a TypeScript shared story file": _Project(TYPESCRIPT_ONLY),
        }

    with after.all:
        for layout in self.layouts.values():
            layout.close()

    with it("should link a story to its own file, named after it"):
        expect(self.layouts["one story per file"].link_of("Pay For Order")).to(equal("../story_tests/check-out/pay/pay-for-order/pay_for_order_story.test.md"))

    with it("should link each story a sub-epic's markdown file holds to its heading there"):
        expect([self.layouts["a sub-epic file"].link_of(name) for name in ("Pay For Order", "Cancel Order")]).to(equal([
            "../story_tests/check-out/pay/pay_story.test.md#story-pay-for-order",
            "../story_tests/check-out/pay/pay_story.test.md#story-cancel-order",
        ]))

    with it("should link each story a story test in Python holds to that story test"):
        expect(self.layouts["Python alone"].link_of("Cancel Order")).to(equal("../story_tests/check-out/pay/pay_story.test.py"))

    with it("should link each story a shared story file in TypeScript holds to that file"):
        expect(self.layouts["a TypeScript shared story file"].link_of("Cancel Order")).to(equal("../story_tests/check-out/pay/pay.story.shared.ts"))

    with it("should draw a story a sub-epic's markdown file holds linked to its heading there"):
        expect(self.layouts["a sub-epic file"].drawn()).to(contain('link="../story_tests/check-out/pay/pay_story.test.md#story-cancel-order"'))
