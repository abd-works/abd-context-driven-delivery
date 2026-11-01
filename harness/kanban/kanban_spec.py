"""The session kanban board (model: harness/kanban/.context/kanban-model.md)."""
import json
import os
import tempfile
from pathlib import Path

from expects import be_none, be_true, contain, equal, expect
from mamba import after, before, context, description, it

from harness.installation.installer import Installer

Installer(repo=Path(__file__).resolve().parents[2]).ensure_import_path()

from bdd.bdd import Bdd  # noqa: E402
from ddd.ddd import Ddd  # noqa: E402
from generate.generate import Generate  # noqa: E402
from harness.kanban.board import Board, Card  # noqa: E402
from harness.kanban.ticket import Ticket  # noqa: E402
from review.review import Review  # noqa: E402
from stories.stories import Stories  # noqa: E402
from ux.ux import Ux  # noqa: E402
from validate.validate import Validate  # noqa: E402


class SessionsFolder:
    """A temporary `.sessions/` folder: work sessions with their logs, closed sessions, backlog items."""

    def __init__(self) -> None:
        self.project = Path(tempfile.mkdtemp(prefix="kanban-sessions-"))
        self.root = self.project / ".sessions"
        self.root.mkdir()
        os.environ["CDD_PROJECT"] = str(self.project)

    def session(self, name: str, *log_lines: str, closed: bool = False, **fields) -> Path:
        folder = self.root / ("closed" if closed else "") / name
        folder.mkdir(parents=True)
        (folder / "session.json").write_text(json.dumps({"name": name, **fields}), encoding="utf-8")
        stamped = [f"2026-10-31T0{index % 10}:00:00Z {line}" for index, line in enumerate(log_lines)]
        (folder / "session.log").write_text("".join(f"{line}\n" for line in stamped), encoding="utf-8")
        return folder

    def folder(self, name: str) -> Path:
        folder = self.root / name
        folder.mkdir(parents=True, exist_ok=True)
        return folder

    def backlog_item(self, file_name: str, heading: str) -> Path:
        path = self.folder("_backlog") / file_name
        path.write_text(f"# {heading}\n\nAn idea.\n", encoding="utf-8")
        return path

    def current(self, name: str) -> None:
        (self.root / "session.json").write_text(json.dumps({"session": name}), encoding="utf-8")


def names(items) -> list:
    return [item.name for item in items]


with description("a board") as self:
    with after.each:
        os.environ.pop("CDD_PROJECT", None)

    # (S) Board Pane --> Display Board
    with context("with Stories, DDD, and UX chosen"):
        with before.each:
            self.board = Board(SessionsFolder().root, [Stories(), Ddd(), Ux()])
            self.discovery = self.board.column("Discovery")

        with it("should have the columns Backlog, Discovery, Specification, Implementation, and Complete, in that order"):
            expect(names(self.board.columns)).to(equal(["Backlog", "Discovery", "Specification", "Implementation", "Complete"]))

        with it("should have story_map, bounded_context, and ia as Discovery's work required"):
            expect([fidelity.name for fidelity in self.discovery.work_required]).to(equal(["story_map", "bounded_context", "ia"]))

        with it("should give every stage Generate, Validate, and Review, in that order"):
            expect([self.board.column(name).actions for name in ("Discovery", "Specification", "Implementation")]).to(equal([[Generate, Validate, Review]] * 3))

    with context("with BDD chosen"):
        with before.each:
            self.board = Board(SessionsFolder().root, [Bdd()])

        with it("should have behavior as Discovery's work required"):
            expect([fidelity.name for fidelity in self.board.column("Discovery").work_required]).to(equal(["behavior"]))

        with it("should have realization as Specification's work required"):
            expect([fidelity.name for fidelity in self.board.column("Specification").work_required]).to(equal(["realization"]))

    with context("that has been loaded with no practices given"):
        with before.each:
            self.board = Board.load(SessionsFolder().root)

        with it("should choose every practice"):
            expect([type(practice).__name__ for practice in self.board.practices]).to(equal(["Stories", "Ddd", "Ux", "CleanEngineering", "Bdd"]))

    # (S) Board Pane --> Display Ticket Card, Display Backlog Items As Tickets
    with context("with a sessions folder of work sessions, closed sessions, default, backlog items, and archived sessions"):
        with before.each:
            sessions = SessionsFolder()
            sessions.session("pet-visits", title="Pet visits")
            sessions.session("sign-up", title="Sign up")
            sessions.session("browse-pets", closed=True, title="Browse pets")
            sessions.folder("main")
            sessions.backlog_item("returns-and-refunds.md", "Returns and refunds")
            sessions.folder("_archive/old-spike")
            sessions.current("pet-visits")
            self.board = Board(sessions.root, [Stories(), Ddd(), Ux()])

        with it("should show every work session as a ticket"):
            expect(names(self.board.tickets)).to(equal(["pet-visits", "sign-up", "browse-pets"]))

        with it("should leave main off the board"):
            expect(names(self.board.tickets)).not_to(contain("main"))

        with it("should show each backlog item in the Backlog column"):
            expect([card.title for card in self.board.column("Backlog").cards]).to(equal(["Returns and refunds"]))

        with it("should leave archived sessions off the board"):
            expect(names(self.board.tickets)).not_to(contain("old-spike"))

        with it("should show closed sessions in Complete"):
            expect(names(self.board.column("Complete").cards)).to(equal(["browse-pets"]))

        with it("should name the ticket of the current session as active"):
            expect(self.board.active.name).to(equal("pet-visits"))

        with it("should show tickets and backlog items alike as the board's cards"):
            expect([card.title for card in self.board.cards]).to(equal(["Pet visits", "Sign up", "Browse pets", "Returns and refunds"]))

        with it("should count both a ticket and a backlog item as a card"):
            expect(all(isinstance(card, Card) for card in self.board.cards)).to(be_true)

        with it("should give each card one column"):
            expect([card.column.name for card in self.board.cards]).to(equal(["Discovery", "Discovery", "Complete", "Backlog"]))

        with it("should list every column with its tickets or items"):
            expect([column["name"] for column in self.board.to_json()["columns"]]).to(equal(["Backlog", "Discovery", "Specification", "Implementation", "Complete"]))

with description("a backlog item") as self:
    with after.each:
        os.environ.pop("CDD_PROJECT", None)

    # (S) Person --> Add Backlog Item, Start Backlog Item
    with context("that a person has added to the backlog folder"):
        with before.each:
            self.sessions = SessionsFolder()
            self.item_path = self.sessions.backlog_item("returns-and-refunds.md", "Returns and refunds")
            self.board = Board(self.sessions.root, [Stories(), Ddd(), Ux()])

        with it("should be in the Backlog"):
            expect(self.board.backlog_items[0].column.name).to(equal("Backlog"))

        with context("that a person has moved on"):
            with before.each:
                self.moved = self.board.backlog_items[0].move_next()

            with it("should open its ticket in Discovery"):
                expect((self.moved.name, self.moved.column.name)).to(equal(("returns-and-refunds", "Discovery")))

        with context("that a person has moved back"):
            with before.each:
                self.moved = self.board.backlog_items[0].move_previous()

            with it("should stay in the Backlog"):
                expect(self.moved.column.name).to(equal("Backlog"))

        with context("that has been started"):
            with before.each:
                self.ticket = self.board.backlog_items[0].start("feature")

            with it("should open a ticket in Discovery"):
                expect(self.board.ticket("returns-and-refunds").column.name).to(equal("Discovery"))

            with it("should name the item's file in the new ticket's session log"):
                log = self.sessions.root / "returns-and-refunds" / "session.log"
                expect(log.read_text(encoding="utf-8")).to(contain(str(self.item_path)))

GENERATE_STORY_MAP = "generate /work, /work/docs stories story_map markdown stories no-chat"
VALIDATE_STORY_MAP_WITH_VIOLATIONS = "validate Stories story_map graph-rule actor-named-in-step map.md:12 no-chat"
VALIDATE_STORY_MAP = "validate Stories story_map no-chat"
REVIEW_STORY_MAP = "review /work stories story_map markdown stories no-chat"


def every_action(practice: str, practice_class: str, fidelity: str) -> list:
    return [
        f"generate /work {practice} {fidelity} markdown {practice} no-chat",
        f"validate {practice_class} {fidelity} no-chat",
        f"review /work {practice} {fidelity} markdown {practice} no-chat",
    ]


DISCOVERY_DONE = every_action("stories", "Stories", "story_map") + every_action("ddd", "Ddd", "bounded_context") + every_action("ux", "Ux", "ia")


def board_with(lines: list):
    sessions = SessionsFolder()
    sessions.session("pawplace", title="PawPlace")
    sessions.session("pet-visits", *lines, title="Pet visits", scope="feature", parent="pawplace")
    return sessions.root, Board(sessions.root, [Stories(), Ddd(), Ux()])


def ticket_with(lines: list):
    return board_with(lines)[1].ticket("pet-visits")


def story_map(ticket):
    return next(progress for progress in ticket.progress if progress.slug == "stories-story_map")


with description("a ticket") as self:
    with after.each:
        os.environ.pop("CDD_PROJECT", None)

    # (S) Person --> Open Ticket Session
    with context("that has just been started"):
        with before.each:
            SessionsFolder()
            Ticket.new("PawPlace", "initiative")
            self.ticket = Ticket.new("Pet visits", "feature", "pawplace")

        with it("should be in Discovery, in progress"):
            expect((self.ticket.column.name, self.ticket.is_done)).to(equal(("Discovery", False)))

        with it("should keep its title, scope, and lineage"):
            expect((self.ticket.title, self.ticket.scope, self.ticket.lineage.name)).to(equal(("Pet visits", "feature", "pawplace")))

        with it("should name Generate on story_map as next"):
            expect((self.ticket.next.slug, self.ticket.next.remaining_actions[0])).to(equal(("stories-story_map", Generate)))

    # (S) Board Pane --> Display Ticket Card, Place Ticket In Column
    with context("with its first logged work on a Specification fidelity"):
        with it("should be in Specification"):
            ticket = ticket_with(["generate /work/ux ux mockup html ux no-chat"])
            expect(ticket.column.name).to(equal("Specification"))

    # (S) Board Pane --> Display Fidelity Progress; (S) Person --> Generate Fidelity Output, Validate Fidelity, Review Fidelity
    with context("with a fidelity generated"):
        with before.each:
            self.lines = [GENERATE_STORY_MAP]

        with it("should show Generate done and Validate and Review remaining for that fidelity"):
            expect(story_map(ticket_with(self.lines)).remaining_actions).to(equal([Validate, Review]))

        with context("with log lines whose paths hold spaces and commas"):
            with it("should still find the practice and fidelity by name"):
                ticket = ticket_with(["generate C:\\My Work, D:\\other files stories story_map markdown stories no-chat"])
                expect(story_map(ticket).done_actions).to(equal([Generate]))

        with context("that has a validate naming graph-rule violations"):
            with before.each:
                self.lines.append(VALIDATE_STORY_MAP_WITH_VIOLATIONS)

            with it("should still need Validate for that fidelity"):
                expect(story_map(ticket_with(self.lines)).remaining_actions).to(equal([Validate, Review]))

        with context("that has a validate with no violations"):
            with before.each:
                self.lines.append(VALIDATE_STORY_MAP)

            with it("should show Validate done for that fidelity"):
                expect(story_map(ticket_with(self.lines)).done_actions).to(equal([Generate, Validate]))

            with it("should match the practice's class name in the validate line to its folder name"):
                expect([progress.slug for progress in ticket_with(self.lines).progress if progress.done_actions]).to(equal(["stories-story_map"]))

            with context("that has been reviewed"):
                with before.each:
                    self.lines.append(REVIEW_STORY_MAP)

                with it("should show the fidelity done"):
                    expect(story_map(ticket_with(self.lines)).is_done).to(be_true)

        with context("that was reviewed before its validate passed"):
            with before.each:
                self.lines += [REVIEW_STORY_MAP, VALIDATE_STORY_MAP]

            with it("should not count the review"):
                expect(story_map(ticket_with(self.lines)).done_actions).to(equal([Generate, Validate]))

    # (S) Person --> Review Fidelity, Complete Stage Work; (S) Person --> Move Ticket
    with context("with every required fidelity in its stage done"):
        with before.each:
            self.root, self.board = board_with(DISCOVERY_DONE)
            self.ticket = self.board.ticket("pet-visits")

        with it("should be done, waiting in its stage's done part"):
            expect(names(self.board.column("Discovery").done)).to(equal(["pet-visits"]))

        with it("should have no next"):
            expect(self.ticket.next).to(be_none)

        with context("that a person has moved on"):
            with before.each:
                self.ticket.move_next()

            with it("should be in the next stage"):
                expect(self.ticket.column.name).to(equal("Specification"))

            with it("should write the stage it entered to its session log"):
                log = (self.root / "pet-visits" / "session.log").read_text(encoding="utf-8")
                expect(log.splitlines()[-1]).to(contain("move Specification"))

    with context("with a session log written before moves were named move"):
        with before.each:
            self.ticket = ticket_with(["pull Specification", "done Specification"])

        with it("should still be in the stage the log names"):
            expect(self.ticket.column.name).to(equal("Specification"))

        with it("should still be marked done there"):
            expect(self.ticket.is_done).to(be_true)

    # (S) Person --> Mark Ticket Done In Stage
    with context("with its stage not done"):
        with before.each:
            self.ticket = ticket_with([GENERATE_STORY_MAP])

        with it("should stay in its stage"):
            expect(self.ticket.column.name).to(equal("Discovery"))

        with context("that a person has moved on"):
            with before.each:
                self.ticket.move_next()

            with it("should be done in its stage, in the same column"):
                expect((self.ticket.column.name, self.ticket.is_done)).to(equal(("Discovery", True)))

            with it("should have no next"):
                expect(self.ticket.next).to(be_none)

    # (S) Person --> Choose Ticket Practices
    with context("with every practice but Stories turned off"):
        with before.each:
            self.ticket = ticket_with(every_action("stories", "Stories", "story_map"))
            self.ticket.enable_practice("ddd", False)
            self.ticket.enable_practice("ux", False)

        with it("should be done with the one practice it works on"):
            expect(self.ticket.is_done).to(be_true)

    # (S) Person --> Close Active Session
    with context("that has been closed"):
        with before.each:
            self.root, board = board_with([GENERATE_STORY_MAP])
            self.closed = board.ticket("pet-visits").close()

        with it("should be in Complete"):
            expect(self.closed.column.name).to(equal("Complete"))

        with it("should have its folder in closed"):
            expect((self.root / "closed" / "pet-visits" / "session.log").is_file()).to(be_true)

    # (S) Person --> Archive Ticket
    with context("that has been archived"):
        with before.each:
            self.root, self.board = board_with([GENERATE_STORY_MAP])
            self.board.ticket("pet-visits").archive()

        with it("should be off the board"):
            expect(names(self.board.tickets)).not_to(contain("pet-visits"))

        with it("should have its folder in the archive"):
            expect((self.root / "_archive" / "pet-visits" / "session.log").is_file()).to(be_true)
