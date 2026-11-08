"""The session kanban board (model: space/kanban/.context/kanban-model.md)."""
import json
import os
import tempfile
from pathlib import Path

from expects import be, be_none, be_true, contain, equal, expect
from mamba import after, before, context, description, it

from harness.installation.repository_toolsets import RepositoryToolsets

RepositoryToolsets(Path(__file__).resolve().parents[2]).ensure_import_path()

from cdd_guidance.practices.bdd.bdd import Bdd  # noqa: E402
from cdd_guidance.practices.ddd.ddd import Ddd  # noqa: E402
from cdd_guidance.practices.stories.stories import Stories  # noqa: E402
from cdd_guidance.practices.ux.ux import Ux  # noqa: E402
from harness.guidance.guidance import FidelityGuidance  # noqa: E402
from harness.installation.data_class import data_of  # noqa: E402
from space.kanban.board import Board, Card, ColumnNotFoundError, Help  # noqa: E402
from space.kanban.ticket import Ticket  # noqa: E402
from space.repo.repo import Repo  # noqa: E402


class SessionsFolder:
    """A temporary `.sessions/` folder: work sessions with their logs, closed sessions, backlog items."""

    def __init__(self) -> None:
        self.project = Path(tempfile.mkdtemp(prefix="kanban-sessions-"))
        self.root = self.project / ".sessions"
        self.root.mkdir()
        os.environ["CDD_PROJECT"] = str(self.project)

    def session(self, name: str, *log_lines: str, closed: bool = False, **fields) -> Path:
        folder = self.root / ("_complete" if closed else "") / name
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

    with context("loaded for a tool call"):
        with it("should work on the one repository its sessions hold"):
            board = Board.load(SessionsFolder().project)
            expect(board.repo).to(be(board.sessions.repo))

    # (S) Board App --> Display Board
    with context("with Stories, DDD, and UX chosen"):
        with before.each:
            self.board = Board(Repo(SessionsFolder().project), [Stories(), Ddd(), Ux()])
            self.discovery = self.board.column("Discovery")

        with it("should have the columns Backlog, Discovery, Specification, Implementation, and Complete, in that order"):
            expect(names(self.board.columns)).to(equal(["Backlog", "Discovery", "Specification", "Implementation", "Complete"]))

        with it("should have story_map, bounded_context, and ia as Discovery's work required"):
            expect([fidelity.name for fidelity in self.discovery.work_required]).to(equal(["story_map", "bounded_context", "ia"]))

        with it("should give every stage Generate, Validate, and Review, in that order"):
            expect([self.board.column(name).steps for name in ("Discovery", "Specification", "Implementation")]).to(equal([["generate", "validate", "review"]] * 3))

    with context("with BDD chosen"):
        with before.each:
            self.board = Board(Repo(SessionsFolder().project), [Bdd()])

        with it("should have behavior as Discovery's work required"):
            expect([fidelity.name for fidelity in self.board.column("Discovery").work_required]).to(equal(["behavior"]))

        with it("should have realization as Specification's work required"):
            expect([fidelity.name for fidelity in self.board.column("Specification").work_required]).to(equal(["realization"]))

        with it("should refuse a column it does not have, naming it"):
            try:
                self.board.column("Icebox")
                refused = None
            except ColumnNotFoundError as error:
                refused = error.column
            expect(refused).to(equal("Icebox"))

    with context("that has been loaded with no practices given"):
        with before.each:
            self.board = Board.load(SessionsFolder().project)

        with it("should choose every practice"):
            expect([type(practice).__name__ for practice in self.board.practices]).to(equal(["Stories", "Ddd", "Ux", "CleanEngineering", "Bdd"]))

        with it("should choose the practice classes their packages define, loaded once under one name"):
            expect([type(practice) for practice in self.board.practices[:3]]).to(equal([Stories, Ddd, Ux]))

        with it("should share its practices with every other board loaded in the process, since they do not change between calls"):
            expect(Board.load(SessionsFolder().project).practices[0]).to(be(self.board.practices[0]))

    # (S) Person --> Open Board
    with context("of a project named by a folder inside its checkout"):
        with before.each:
            self.checkout = SessionsFolder().project
            (self.checkout / ".git").mkdir(exist_ok=True)
            inside = self.checkout / "src" / "visits"
            inside.mkdir(parents=True)
            self.inside = inside

        with it("should show the board of the whole checkout, where sessions keep their folders"):
            expect(Board.load(self.inside).repo.root).to(equal(self.checkout.resolve()))

    with context("of a project named by a folder in a ticket's worktree"):
        with before.each:
            self.checkout = SessionsFolder().project
            worktree_git = self.checkout / ".git" / "worktrees" / "pet-visits"
            worktree_git.mkdir(parents=True)
            (worktree_git / "commondir").write_text("../..\n", encoding="utf-8")
            self.worktree = Path(tempfile.mkdtemp(prefix="kanban-worktree-"))
            (self.worktree / ".git").write_text(f"gitdir: {worktree_git}\n", encoding="utf-8")
            (self.worktree / "docs").mkdir()

        with it("should show the board of the project's main checkout, where every ticket's session lives"):
            expect(Board.load(self.worktree / "docs").repo.root).to(equal(self.checkout.resolve()))

    with context("with no session saved as open"):
        with it("should have no active ticket, since main is not on the board"):
            expect(Board(Repo(SessionsFolder().project), [Stories()]).active).to(be_none)

    # (S) Board App --> Display Ticket Card, Display Backlog Items As Tickets
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
            self.board = Board(Repo(sessions.project), [Stories(), Ddd(), Ux()])

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

        with it("should offer the tickets in a stage to switch to, neither backlog items nor closed tickets"):
            expect(names(self.board.open_tickets)).to(equal(["pet-visits", "sign-up"]))

        with it("should show tickets and backlog items alike as the board's cards"):
            expect([card.title for card in self.board.cards]).to(equal(["Pet visits", "Sign up", "Browse pets", "Returns and refunds"]))

        with it("should count both a ticket and a backlog item as a card"):
            expect(all(isinstance(card, Card) for card in self.board.cards)).to(be_true)

        with it("should give each card one column"):
            expect([card.column.name for card in self.board.cards]).to(equal(["Discovery", "Discovery", "Complete", "Backlog"]))

        with it("should list every column with its tickets or items"):
            expect([column["name"] for column in data_of(self.board)["columns"]]).to(equal(["Backlog", "Discovery", "Specification", "Implementation", "Complete"]))

        with it("should send each column's kind"):
            expect([column["kind"] for column in data_of(self.board)["columns"]]).to(equal(["backlog", "stage", "stage", "stage", "complete"]))

        with it("should read its tickets once for every column"):
            expect(self.board.column("Discovery").cards[0]).to(be(self.board.tickets[0]))

        with context("that has opened a ticket since it read them"):
            with before.each:
                self.board.tickets
                self.board.open_ticket("Gift cards", "feature", "", "")

            with it("should read the tickets again"):
                expect(names(self.board.tickets)).to(contain("gift-cards"))

        with it("should send each card's title and last activity, whether a ticket or a backlog item"):
            sent = [data_of(card) for card in self.board.cards]
            expect([(bool(card["title"]), "last_activity" in card) for card in sent]).to(equal([(True, True)] * 4))

    # (S) Person --> Open Help
    with context("with help open on a fidelity the catalog has no page for"):
        with before.each:
            stories = Stories()
            self.help = Help(stories, FidelityGuidance("unpublished", "discovery"), None)

        with it("should link to its practice's page on the forge"):
            expect(self.help.href).to(equal("https://forge.abdworks.net/abd-context-driven-delivery/context-tools/stories.html"))

    # (S) Person --> Set WIP Limit
    with context("with something else the sessions share saved in the board's file"):
        with before.each:
            self.sessions = SessionsFolder()
            (self.sessions.root / "_board.json").write_text(json.dumps({"pinned": ["pet-visits"]}), encoding="utf-8")
            self.board = Board(Repo(self.sessions.project), [Stories()])

        with context("that a person sets a stage's limit"):
            with before.each:
                self.board.column("Discovery").set_wip_limit(5)

            with it("should keep what else the board's file holds"):
                saved = json.loads((self.sessions.root / "_board.json").read_text(encoding="utf-8"))
                expect(saved).to(equal({"pinned": ["pet-visits"], "wip_limits": {"Discovery": 5}}))

with description("a backlog item") as self:
    with after.each:
        os.environ.pop("CDD_PROJECT", None)

    # (S) Person --> Add Backlog Item, Start Backlog Item
    with context("that a person has added to the backlog folder"):
        with before.each:
            self.sessions = SessionsFolder()
            self.item_path = self.sessions.backlog_item("returns-and-refunds.md", "Returns and refunds")
            self.board = Board(Repo(self.sessions.project), [Stories(), Ddd(), Ux()])

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
                self.written = self.item_path.read_text(encoding="utf-8")
                self.ticket = self.board.backlog_items[0].start("feature")

            with it("should keep the item's file, text and all, in the new ticket's session folder"):
                kept = self.sessions.root / "returns-and-refunds" / "returns-and-refunds.md"
                expect(kept.read_text(encoding="utf-8")).to(equal(self.written))

            with it("should open a ticket in Discovery"):
                expect(self.board.ticket("returns-and-refunds").column.name).to(equal("Discovery"))

            with it("should name the item's file in the new ticket's session log"):
                log = self.sessions.root / "returns-and-refunds" / "session.log"
                expect(log.read_text(encoding="utf-8")).to(contain(str(self.item_path)))

    # (S) Board App --> Display Backlog Items As Tickets
    with context("that is kept as a folder holding a file of its own name"):
        with before.each:
            self.sessions = SessionsFolder()
            folder = self.sessions.folder("_backlog/gift-cards")
            (folder / "gift-cards.md").write_text("# Gift cards\n\nSell them at the till.\n", encoding="utf-8")
            (folder / "session.log").write_text("2026-10-31T01:00:00Z generate /work stories story_map markdown stories no-chat\n", encoding="utf-8")
            (folder / "session.json").write_text(json.dumps({"name": "gift-cards", "title": "Gift cards"}), encoding="utf-8")
            self.board = Board(Repo(self.sessions.project), [Stories(), Ddd(), Ux()])

        with it("should be in the Backlog under the heading of that file"):
            expect([item.title for item in self.board.backlog_items]).to(equal(["Gift cards"]))

        with it("should show the text of that file"):
            expect(self.board.backlog_items[0].text).to(equal("Sell them at the till."))

        with context("that has been started"):
            with before.each:
                self.ticket = self.board.backlog_items[0].start("feature")

            with it("should bring its ticket back with the history in its session log"):
                log = self.sessions.root / "gift-cards" / "session.log"
                expect(log.read_text(encoding="utf-8")).to(contain("generate /work stories story_map"))

            with it("should keep its file in the ticket's session folder"):
                expect((self.sessions.root / "gift-cards" / "gift-cards.md").read_text(encoding="utf-8")).to(contain("Sell them at the till."))

    # (S) Person --> Drag Ticket To A Stage
    with context("that a ticket became when a person dragged it into the Backlog from a later stage"):
        with before.each:
            self.sessions = SessionsFolder()
            folder = self.sessions.session("pet-visits", "move Specification", title="Pet visits")
            (folder / "pet-visits.md").write_text("# Pet visits\n\nBook a vet visit online.\n", encoding="utf-8")
            board = Board(Repo(self.sessions.project), [Stories(), Ddd(), Ux()])
            board.ticket("pet-visits").move_to("Backlog")
            self.board = Board(Repo(self.sessions.project), [Stories(), Ddd(), Ux()])

        with it("should be in the Backlog"):
            expect([item.title for item in self.board.backlog_items]).to(equal(["Pet visits"]))

        with it("should keep the ticket's whole folder, its history included"):
            expect((self.sessions.root / "_backlog" / "pet-visits" / "session.log").read_text(encoding="utf-8")).to(contain("move Specification"))

        with it("should show the ticket's own idea file as its text"):
            expect(self.board.backlog_items[0].text).to(equal("Book a vet visit online."))

        with it("should be off the stages"):
            expect(names(self.board.tickets)).to(equal([]))

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
    return sessions.root, Board(Repo(sessions.project), [Stories(), Ddd(), Ux()])


def ticket_with(lines: list):
    return board_with(lines)[1].ticket("pet-visits")


def story_map(ticket):
    return next(progress for progress in ticket.progress if progress.fidelity.slug == "stories-story-map")


with description("a ticket") as self:
    with after.each:
        os.environ.pop("CDD_PROJECT", None)

    # (S) Person --> Open Ticket Session
    with context("that has just been started"):
        with before.each:
            project = SessionsFolder().project
            Ticket.create("PawPlace", "initiative", project=project)
            self.ticket = Ticket.create("Pet visits", "feature", "pawplace", project=project)

        with it("should be in Discovery, in progress"):
            expect((self.ticket.column.name, self.ticket.is_done)).to(equal(("Discovery", False)))

        with it("should keep its title, scope, and parent"):
            expect((self.ticket.title, self.ticket.session.scope, self.ticket.session.parent)).to(equal(("Pet visits", "feature", "pawplace")))

        with it("should name Generate on story_map as next"):
            expect((self.ticket.next_fidelity.fidelity.slug, self.ticket.next_fidelity.remaining_actions[0])).to(equal(("stories-story-map", "generate")))

        with it("should tell the agent the ticket, its stage, its next guidance, and the steps each fidelity goes through"):
            expect(self.ticket.agent_context).to(equal(
                'CDD session board: you are working on ticket pet-visits ("Pet visits"), in Discovery. Its next guidance is stories-story-map. '
                "Each fidelity goes through generate, validate, then review, which a person records on the board."
            ))

        with it("should offer its own branch and worktree on opening it, each chosen"):
            expect(self.ticket.open_choices().choices).to(equal(["branch", "worktree"]))

        with it("should command an action on its next fidelity in its own session, naming no format so the fidelity's kept format holds"):
            expect(self.ticket.next_fidelity.commands["generate"]).to(equal("/actions-generate stories-story-map session=.sessions/pet-visits/session.json"))

        with it("should command every action its stage offers"):
            expect(list(self.ticket.next_fidelity.commands)).to(equal(["generate", "validate", "review", "iterate", "sketch", "render", "document"]))

    # (S) Board App --> Display Ticket Card, Place Ticket In Column
    with context("with its first logged work on a Specification fidelity"):
        with it("should be in Specification"):
            ticket = ticket_with(["generate /work/ux ux mockup html ux no-chat"])
            expect(ticket.column.name).to(equal("Specification"))

    # (S) Board App --> Display Fidelity Progress; (S) Person --> Generate Fidelity Output, Validate Fidelity, Review Fidelity
    with context("with a fidelity generated"):
        with before.each:
            self.lines = [GENERATE_STORY_MAP]

        with it("should show Generate done and Validate and Review remaining for that fidelity"):
            expect(story_map(ticket_with(self.lines)).remaining_actions).to(equal(["validate", "review"]))

        with context("by the generate tool"):
            with it("should show Generate done"):
                expect(story_map(ticket_with(["tool generate.generate", GENERATE_STORY_MAP])).done_actions).to(equal(["generate"]))

        # Building the Sketch, Grill, or Iterate prompt expands a generate inside it, which wrote a generate line
        # although the agent had written nothing yet.
        with context("only in a line another tool's call wrote"):
            with it("should leave Generate to do"):
                expect(story_map(ticket_with(["tool sketch.sketch", GENERATE_STORY_MAP])).done_actions).to(equal([]))

            with it("should leave Generate to do however many lines that call wrote"):
                expect(story_map(ticket_with(["tool iterate.iterate", "iterate /work no-chat", GENERATE_STORY_MAP])).done_actions).to(equal([]))

        with context("by the generate tool after another tool's call"):
            with it("should show Generate done"):
                lines = ["tool sketch.sketch", GENERATE_STORY_MAP, "tool generate.generate", GENERATE_STORY_MAP]
                expect(story_map(ticket_with(lines)).done_actions).to(equal(["generate"]))

        with context("with log lines whose paths hold spaces and commas"):
            with it("should still find the practice and fidelity by name"):
                ticket = ticket_with(["generate C:\\My Work, D:\\other files stories story_map markdown stories no-chat"])
                expect(story_map(ticket).done_actions).to(equal(["generate"]))

        with context("that has a validate naming graph-rule violations"):
            with before.each:
                self.lines.append(VALIDATE_STORY_MAP_WITH_VIOLATIONS)

            with it("should still need Validate for that fidelity"):
                expect(story_map(ticket_with(self.lines)).remaining_actions).to(equal(["validate", "review"]))

        with context("that has a validate with no violations"):
            with before.each:
                self.lines.append(VALIDATE_STORY_MAP)

            with it("should show Validate done for that fidelity"):
                expect(story_map(ticket_with(self.lines)).done_actions).to(equal(["generate", "validate"]))

            with it("should match the practice's class name in the validate line to its folder name"):
                expect([progress.fidelity.slug for progress in ticket_with(self.lines).progress if progress.done_actions]).to(equal(["stories-story-map"]))

            with context("that has been reviewed"):
                with before.each:
                    self.lines.append(REVIEW_STORY_MAP)

                with it("should show the fidelity done"):
                    expect(story_map(ticket_with(self.lines)).is_done).to(be_true)

            # (S) Person --> Send Action To Stage Practices: a stage head's bar shows the stage's work taken together.
            with it("should show Validate in progress across Discovery while one of its fidelities is validated"):
                ticket = ticket_with(self.lines)
                expect(data_of(ticket.work_in(ticket.column).action_states)["validate"]).to(equal("in_progress"))

            with it("should show Generate done across Discovery only once every fidelity is generated"):
                ticket = ticket_with(self.lines)
                expect(data_of(ticket.work_in(ticket.column).action_states)["generate"]).to(equal("in_progress"))

            with it("should allow across Discovery only the actions every fidelity allows"):
                ticket = ticket_with(self.lines)
                expect(ticket.work_in(ticket.column).allowed_actions).not_to(contain("validate"))

        with context("that was reviewed before its validate passed"):
            with before.each:
                self.lines += [REVIEW_STORY_MAP, VALIDATE_STORY_MAP]

            with it("should not count the review"):
                expect(story_map(ticket_with(self.lines)).done_actions).to(equal(["generate", "validate"]))

        # A person who clicks Review has reviewed the output, whatever its validate found.
        with context("that was reviewed after a validate that found violations"):
            with before.each:
                self.lines += [VALIDATE_STORY_MAP_WITH_VIOLATIONS, REVIEW_STORY_MAP]

            with it("should count the review"):
                expect(story_map(ticket_with(self.lines)).done_actions).to(equal(["generate", "review"]))

    # (S) Person --> Review Fidelity, Complete Stage Work; (S) Person --> Move Ticket
    with context("with every required fidelity in its stage done"):
        with before.each:
            self.root, self.board = board_with(DISCOVERY_DONE)
            self.ticket = self.board.ticket("pet-visits")

        with it("should be done, waiting in its stage's done part"):
            expect(names(self.board.column("Discovery").done)).to(equal(["pet-visits"]))

        with it("should have no next"):
            expect(self.ticket.next_fidelity).to(be_none)

        with context("that a person has moved on"):
            with before.each:
                self.ticket.move_next()

            with it("should be in the next stage"):
                expect(self.ticket.column.name).to(equal("Specification"))

            with it("should write the stage it entered to its session log"):
                log = (self.root / "pet-visits" / "session.log").read_text(encoding="utf-8")
                expect(log.splitlines()[-1]).to(contain("move Specification"))

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
                expect(self.ticket.next_fidelity).to(be_none)

    # (S) Person --> Send Next Fidelity Action
    with context("that a person has moved on with an earlier stage's fidelity still to review"):
        with before.each:
            self.ticket = ticket_with([GENERATE_STORY_MAP, VALIDATE_STORY_MAP])
            self.ticket.move_to("Specification")

        with it("should name Review on that fidelity as next"):
            expect((self.ticket.next_fidelity.fidelity.slug, self.ticket.next_fidelity.next_action)).to(equal(("stories-story-map", "review")))

    # (S) Person --> Drag Ticket To A Stage
    with context("that a person has dragged into a later stage's done part"):
        with before.each:
            self.ticket = ticket_with([GENERATE_STORY_MAP])
            self.ticket.move_to("Implementation", done=True)

        with it("should be done in that stage"):
            expect((self.ticket.column.name, self.ticket.is_done)).to(equal(("Implementation", True)))

    with context("that a person has dragged back into its own stage's in progress part"):
        with before.each:
            self.root, board = board_with(DISCOVERY_DONE)
            self.ticket = board.ticket("pet-visits")
            self.ticket.move_to("Discovery")

        with it("should be in progress in that stage"):
            expect((self.ticket.column.name, self.ticket.is_done)).to(equal(("Discovery", False)))

    with context("that a person has dragged out of Complete"):
        with before.each:
            self.root, board = board_with([GENERATE_STORY_MAP])
            self.moved = board.ticket("pet-visits").close().move_to("Specification")

        with it("should be open again, in progress in that stage"):
            expect((self.moved.column.name, self.moved.is_done)).to(equal(("Specification", False)))

    # (S) Person --> Choose Ticket Practices
    with context("with every practice but Stories turned off"):
        with before.each:
            self.ticket = ticket_with(every_action("stories", "Stories", "story_map"))
            self.ticket.session.practice("ddd").enable(False)
            self.ticket.session.practice("ux").enable(False)

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
            expect((self.root / "_complete" / "pet-visits" / "session.log").is_file()).to(be_true)

    # (S) Person --> Archive Ticket
    with context("that has been archived"):
        with before.each:
            self.root, self.board = board_with([GENERATE_STORY_MAP])
            self.board.ticket("pet-visits").archive()

        with it("should be off the board"):
            expect(names(self.board.tickets)).not_to(contain("pet-visits"))

        with it("should have its folder in the archive"):
            expect((self.root / "_archive" / "pet-visits" / "session.log").is_file()).to(be_true)
