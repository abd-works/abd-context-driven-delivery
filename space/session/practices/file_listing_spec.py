"""Which of a session's files a page lists (model: space/session/.context/module-context.md, FileListing)."""
from types import SimpleNamespace

from expects import equal, expect
from mamba import before, context, description, it

from space.session.practices.file_listing import FileListing
from space.session.files.file_manager import FileEntry
from space.session.practices.practice_session_output import Publication

STORY_MAP = "stories-story-map"
MODEL = "ddd-bounded-context"


def selection(fidelities: list[str], formats: list[list[str]] | None = None, *, is_stage_chosen: bool = True, practices: tuple[bool, ...] = (True,)):
    """A guidance selection as the listing reads it: the fidelities it covers, the format groups selected, whether stages
    were chosen, and whether each practice is selected."""
    groups = [SimpleNamespace(formats=group, is_selected=True) for group in formats or []]
    return SimpleNamespace(fidelities=fidelities, formats=groups, is_stage_chosen=is_stage_chosen, practices=[SimpleNamespace(is_selected=on) for on in practices])


def board(path: str) -> FileEntry:
    """A whiteboard file published to its board's address."""
    return FileEntry(path, True).linked(Publication("https://claude.ai/artifact/board", "whiteboard"))


with description("a listing of a session's files") as self:
    with context("for the fidelities the selection covers, with no format selected"):
        with before.each:
            self.listing = FileListing(selection([STORY_MAP]), [], is_repository=True)

        with it("should list every file of a fidelity listed"):
            expect(self.listing.of_fidelity(STORY_MAP, "markdown", FileEntry(".context/story-map.md", True)).is_listed).to(equal(True))

        with it("should leave out a file of a fidelity not listed"):
            expect(self.listing.of_fidelity(MODEL, "markdown", FileEntry(".context/context-map.md", True)).is_listed).to(equal(False))

    # A board published from the story map opens in Claude, so it shows whatever formats are chosen; requested
    # 2026-11-18: "first of all where is whiteboard link" while only markdown and drawio were chosen.
    with context("with markdown and drawio selected"):
        with before.each:
            self.listing = FileListing(selection([STORY_MAP], [["markdown"], ["drawio"]]), [], is_repository=True)

        with it("should list a published whiteboard"):
            expect(self.listing.of_fidelity(STORY_MAP, "whiteboard", board(".context/story-map.version-2.whiteboard")).is_listed).to(equal(True))

        with it("should leave out a code file"):
            expect(self.listing.of_fidelity(STORY_MAP, "python", FileEntry("src/story_map.py", True)).is_listed).to(equal(False))

    # A diagram is a draw.io file and a Claude Whiteboard board, so the diagram filter shows a board not yet published
    # too; requested 2026-11-20: "whiteboard isn't a separate format, there's only a button for 'diagram'".
    with context("with the diagram group selected"):
        with it("should list the whiteboard beside the draw.io file, and not the markdown"):
            listing = FileListing(selection([STORY_MAP], [["drawio", "whiteboard"]]), [], is_repository=True)
            shown = [listing.of_fidelity(STORY_MAP, format, FileEntry(f".context/story-map.{format}", True)).is_listed for format in ("markdown", "drawio", "whiteboard")]
            expect(shown).to(equal([False, True, True]))

    with context("before anyone chose stages"):
        with it("should list the fidelities the link names that the selection covers"):
            listing = FileListing(selection([STORY_MAP, MODEL], is_stage_chosen=False), [MODEL, "ux-ia"], is_repository=True)
            expect(listing.listed).to(equal([MODEL]))

    with context("for a file under the root that no fidelity declares"):
        with it("should leave it out while a practice is selected"):
            expect(FileListing(selection([STORY_MAP]), [], is_repository=True).of_root(FileEntry("notes/plain.txt", True)).is_listed).to(equal(False))

        with it("should list it while no practice is selected"):
            expect(FileListing(selection([STORY_MAP], practices=(False,)), [], is_repository=True).of_root(FileEntry("notes/plain.txt", True)).is_listed).to(equal(True))

    with context("in a git repository"):
        with it("should say a file is the session's own work exactly when the branch changed it"):
            listing = FileListing(selection([STORY_MAP]), [], is_repository=True)
            expect([listing.of_root(FileEntry("a.md", True, changed)).is_session_work for changed in (True, False)]).to(equal([True, False]))

    with context("in a folder that is no git repository"):
        with it("should say a file a fidelity holds that is there is the session's own work, and a file of none is not"):
            listing = FileListing(selection([STORY_MAP]), [], is_repository=False)
            held = FileEntry(".context/story-map.md", True).belonging_to([STORY_MAP])
            expect([listing.of_root(held).is_session_work, listing.of_root(FileEntry("notes/plain.txt", True)).is_session_work]).to(equal([True, False]))
