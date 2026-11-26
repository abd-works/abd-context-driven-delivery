"""Which of a session's files a page lists (model: space/session/.context/module-context.md, FileListing)."""
from types import SimpleNamespace

from expects import equal, expect
from mamba import before, context, description, it

from space.session.practices.file_listing import FileListing
from space.session.files.file_manager import FileEntry
from space.session.practices.practice_session_output import Publication
from space.session.session_paths import SessionPaths

STORY_MAP = "stories-story-map"
MODEL = "ddd-bounded-context"
CODE = "clean-engineering-code"
SESSION = "checkout-flow"


def selection(fidelities: list[str], formats: list[list[str]] | None = None, *, is_stage_chosen: bool = True, practices: tuple[bool, ...] = (True,), of_practices: list[str] | None = None, offered: dict[str, list[list[str]]] | None = None):
    """A guidance selection as the listing reads it: the fidelities it covers, the format groups selected, whether stages
    were chosen, whether each practice is selected, the fidelities of the practices selected in every stage (those it
    covers when none are given), and the format groups selected that a fidelity it does not cover offers, by slug. Each
    group is labelled by its first format."""
    groups = [SimpleNamespace(label=group[0], formats=group, is_selected=True) for group in formats or []]
    offered_groups = {slug: [SimpleNamespace(label=group[0], formats=group, is_selected=True) for group in each] for slug, each in (offered or {}).items()}
    return SimpleNamespace(
        fidelities=fidelities,
        formats=groups,
        is_stage_chosen=is_stage_chosen,
        practices=[SimpleNamespace(is_selected=on) for on in practices],
        fidelities_of_practices=fidelities if of_practices is None else of_practices,
        format_groups_with=lambda slugs: [*groups, *(group for slug in slugs for group in offered_groups.get(slug, []))],
    )


def listing_of(selection, linked: list[str] | None = None, *, is_repository: bool = True) -> FileListing:
    """A listing for the session checkout-flow, whose sketch is checkout-flow-sketch.md in a .context folder."""
    return FileListing(selection, linked or [], is_repository, SessionPaths(SimpleNamespace(name=SESSION)))


def board(path: str) -> FileEntry:
    """A whiteboard file published to its board's address."""
    return FileEntry(path, True).linked(Publication("https://claude.ai/artifact/board", "whiteboard"))


with description("a listing of a session's files") as self:
    with context("for the fidelities the selection covers, with no format selected"):
        with before.each:
            self.listing = listing_of(selection([STORY_MAP]), is_repository=True)

        with it("should list every file of a fidelity listed"):
            expect(self.listing.of_fidelity(STORY_MAP, "markdown", FileEntry(".context/story-map.md", True)).is_listed).to(equal(True))

        with it("should leave out a file of a fidelity not listed"):
            expect(self.listing.of_fidelity(MODEL, "markdown", FileEntry(".context/context-map.md", True)).is_listed).to(equal(False))

    # A board published from the story map opens in Claude, so it shows whatever formats are chosen; requested
    # 2026-11-18: "first of all where is whiteboard link" while only markdown and drawio were chosen.
    with context("with markdown and drawio selected"):
        with before.each:
            self.listing = listing_of(selection([STORY_MAP], [["markdown"], ["drawio"]]), is_repository=True)

        with it("should list a published whiteboard"):
            expect(self.listing.of_fidelity(STORY_MAP, "whiteboard", board(".context/story-map.version-2.whiteboard")).is_listed).to(equal(True))

        with it("should leave out a code file"):
            expect(self.listing.of_fidelity(STORY_MAP, "python", FileEntry("src/story_map.py", True)).is_listed).to(equal(False))

    # A diagram is a draw.io file and a Claude Whiteboard board, so the diagram filter shows a board not yet published
    # too; requested 2026-11-20: "whiteboard isn't a separate format, there's only a button for 'diagram'".
    with context("with the diagram group selected"):
        with it("should list the whiteboard beside the draw.io file, and not the markdown"):
            listing = listing_of(selection([STORY_MAP], [["drawio", "whiteboard"]]), is_repository=True)
            shown = [listing.of_fidelity(STORY_MAP, format, FileEntry(f".context/story-map.{format}", True)).is_listed for format in ("markdown", "drawio", "whiteboard")]
            expect(shown).to(equal([False, True, True]))

    # The Files app says why it lists nothing when the formats chosen leave out every file of the fidelities listed;
    # Python says which formats leave each file out, and the page only words it (release-1-2-fixes report, section 7,
    # item 13).
    with context("with markdown selected and a draw.io file of a fidelity listed"):
        with before.each:
            self.listing = listing_of(selection([STORY_MAP], [["markdown"]]), is_repository=True)

        with it("should say the markdown format chosen leaves it out"):
            expect(self.listing.of_fidelity(STORY_MAP, "drawio", FileEntry(".context/story-map.drawio", True)).hidden_by_formats).to(equal(["markdown"]))

        with it("should say no format leaves out a markdown file it lists"):
            expect(self.listing.of_fidelity(STORY_MAP, "markdown", FileEntry(".context/story-map.md", True)).hidden_by_formats).to(equal([]))

        with it("should say no format leaves out a file of a fidelity not listed, which no format would show"):
            expect(self.listing.of_fidelity(MODEL, "drawio", FileEntry(".context/context-map.drawio", True)).hidden_by_formats).to(equal([]))

        with it("should say the markdown format chosen leaves out the draw.io file under the root"):
            held = FileEntry(".context/story-map.drawio", True).belonging_to([STORY_MAP])
            expect(self.listing.of_root(held).hidden_by_formats).to(equal(["markdown"]))

    with context("before anyone chose stages"):
        with it("should list the fidelities the link names that the selection covers"):
            listing = listing_of(selection([STORY_MAP, MODEL], is_stage_chosen=False), [MODEL, "ux-ia"], is_repository=True)
            expect(listing.listed).to(equal([MODEL]))

        # The selection shows the stage the session's ticket stands in until someone chooses, but a link that names a
        # fidelity of another stage, such as the Files app opened on a ticket's code, still lists it.
        with context("with a link naming a fidelity of a stage other than the ticket's"):
            with before.each:
                self.listing = listing_of(
                    selection([STORY_MAP], [["markdown"]], is_stage_chosen=False, of_practices=[STORY_MAP, CODE], offered={CODE: [["python"]]}),
                    [CODE],
                    is_repository=True,
                )

            with it("should list that fidelity while its practice is selected"):
                expect(self.listing.listed).to(equal([CODE]))

            with it("should list its files in the formats selected that it offers"):
                expect(self.listing.of_fidelity(CODE, "python", FileEntry("app/checkout/order.py", True)).is_listed).to(equal(True))

    # A design canvas opens in Claude at its link, so All session files lists it whatever formats are chosen, as the
    # fidelity's own list does; requested 2026-11-16: a design canvas opens where it is published, wherever it lies.
    with context("for a design canvas under the root, published to its link, with only code selected"):
        with it("should list it"):
            listing = listing_of(selection(["ux-mockup"], [["python"]]), is_repository=True)
            canvas = FileEntry("ux/design-canvas/version-1/project/canvas.json", True).belonging_to(["ux-mockup"]).linked(Publication("https://claude.ai/artifact/canvas", "design canvas"))
            expect(listing.of_root(canvas).is_listed).to(equal(True))

    with context("for a file under the root that no fidelity declares"):
        with it("should leave it out while a practice is selected"):
            expect(listing_of(selection([STORY_MAP]), is_repository=True).of_root(FileEntry("notes/plain.txt", True)).is_listed).to(equal(False))

        with it("should list it while no practice is selected"):
            expect(listing_of(selection([STORY_MAP], practices=(False,)), [], is_repository=True).of_root(FileEntry("notes/plain.txt", True)).is_listed).to(equal(True))

    # The sketch action writes one file for every practice, which no fidelity declares, and the person reviews it next;
    # reported 2026-11-18 (Nov 18 demo, "bug 1"): the Files app opened from the chat bar without the sketch just written.
    with context("for the session's sketch under the root, while a practice is selected"):
        with it("should list it"):
            listing = listing_of(selection([STORY_MAP]), is_repository=True)
            expect(listing.of_root(FileEntry(f".context/{SESSION}-sketch.md", True, True)).is_listed).to(equal(True))

        with it("should list it whatever formats are selected"):
            listing = listing_of(selection([STORY_MAP], [["drawio"]]), is_repository=True)
            expect(listing.of_root(FileEntry(f".context/{SESSION}-sketch.md", True, True)).is_listed).to(equal(True))

        with it("should leave out another session's sketch"):
            listing = listing_of(selection([STORY_MAP]), is_repository=True)
            expect(listing.of_root(FileEntry(".context/other-sketch.md", True, True)).is_listed).to(equal(False))

    with context("in a git repository"):
        with it("should say a file is the session's own work exactly when the branch changed it"):
            listing = listing_of(selection([STORY_MAP]), is_repository=True)
            expect([listing.of_root(FileEntry("a.md", True, changed)).is_session_work for changed in (True, False)]).to(equal([True, False]))

    with context("in a folder that is no git repository"):
        with it("should say a file a fidelity holds that is there is the session's own work, and a file of none is not"):
            listing = listing_of(selection([STORY_MAP]), is_repository=False)
            held = FileEntry(".context/story-map.md", True).belonging_to([STORY_MAP])
            expect([listing.of_root(held).is_session_work, listing.of_root(FileEntry("notes/plain.txt", True)).is_session_work]).to(equal([True, False]))
