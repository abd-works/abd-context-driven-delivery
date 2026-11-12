"""Where story maps and story files sit: one locator walks a folder for both, entering the folders documents are kept
in and none a scan never enters, so the map search and the story-file search find the same files."""

import tempfile
from pathlib import Path

from expects import equal, expect
from mamba import after, before, context, description, it

from cdd_guidance.practices.stories.model.story_map_files import StoryMapFiles

_MAP = "# Story Map\n"
_STORY = "# Submit Order\n"


def _write(root: Path, relative: str, text: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _named(root: Path, paths: list) -> list:
    return [path.relative_to(root.resolve()).as_posix() for path in paths]


with description("the story files of a folder"):
    with before.each:
        self.folder = tempfile.TemporaryDirectory()
        self.root = Path(self.folder.name)
        _write(self.root, "shop/.context/story-map.md", _MAP)
        _write(self.root, "node_modules/kit/story-map.md", _MAP)
        _write(self.root, ".venv/lib/story-map.md", _MAP)
        _write(self.root, "shop/tests/place-order/submit_order_story.test.md", _STORY)
        _write(self.root, "node_modules/kit/tests/vendored_story.test.md", _STORY)

    with after.each:
        self.folder.cleanup()

    with it("should find a story map kept in a folder's .context"):
        expect(_named(self.root, StoryMapFiles(self.root).markdown_below())).to(equal(["shop/.context/story-map.md"]))

    with it("should find each story's own file, outside the folders a scan never enters"):
        expect(_named(self.root, StoryMapFiles(self.root).story_files_below())).to(
            equal(["shop/tests/place-order/submit_order_story.test.md"])
        )


with description("the thin slicing of a folder"):
    with before.each:
        self.folder = tempfile.TemporaryDirectory()
        self.root = Path(self.folder.name)

    with after.each:
        self.folder.cleanup()

    with context("that sits only in a folder a scan never enters"):
        with before.each:
            _write(self.root, "node_modules/kit/thin-slicing.md", _MAP)
            _write(self.root, ".venv/lib/thin-slicing.md", _MAP)

        with it("should find none"):
            expect(StoryMapFiles(self.root).thin_slicing()).to(equal(None))

    with context("that is kept in a folder's .context"):
        with before.each:
            _write(self.root, "node_modules/kit/thin-slicing.md", _MAP)
            _write(self.root, "shop/.context/thin-slicing.md", _MAP)

        with it("should find the one in .context"):
            expect(_named(self.root, [StoryMapFiles(self.root).thin_slicing()])).to(equal(["shop/.context/thin-slicing.md"]))

    with context("that sits beside the map and below it"):
        with before.each:
            _write(self.root, "thin-slicing.md", _MAP)
            _write(self.root, "shop/thin-slicing.md", _MAP)

        with it("should find the one in the folder itself"):
            expect(_named(self.root, [StoryMapFiles(self.root).thin_slicing()])).to(equal(["thin-slicing.md"]))


with description("the nearest story map of a folder"):
    with before.each:
        self.folder = tempfile.TemporaryDirectory()
        self.root = Path(self.folder.name)
        _write(self.root, "story-map.md", _MAP)
        (self.root / "project" / "tests" / "place-order").mkdir(parents=True)

    with after.each:
        self.folder.cleanup()

    with context("with no story map in the project the search stops at"):
        with it("should find none above the project"):
            files = StoryMapFiles(self.root / "project" / "tests" / "place-order", top=self.root / "project")
            expect(files.nearest()).to(equal(None))

    with context("with a story map in the project"):
        with before.each:
            _write(self.root, "project/.context/story-map.md", _MAP)

        with it("should find the project's map"):
            files = StoryMapFiles(self.root / "project" / "tests" / "place-order", top=self.root / "project")
            expect(_named(self.root, [files.nearest()])).to(equal(["project/.context/story-map.md"]))

    with context("with no top named and a story map above a folder that sits in no git checkout"):
        with before.each:
            _write(self.root, ".context/story-map.md", _MAP)
            (self.root / "loose").mkdir()

        with it("should search the folder alone, not the folders above it"):
            expect(StoryMapFiles(self.root / "loose").nearest()).to(equal(None))

    with context("with no top named and a story map at the root of the git checkout the folder sits in"):
        with before.each:
            _write(self.root, "checkout/.context/story-map.md", _MAP)
            (self.root / "checkout" / ".git").mkdir()
            (self.root / "checkout" / "work").mkdir()

        with it("should find the checkout's map"):
            found = StoryMapFiles(self.root / "checkout" / "work").nearest()
            expect(_named(self.root, [found])).to(equal(["checkout/.context/story-map.md"]))
