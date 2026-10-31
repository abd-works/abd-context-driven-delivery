"""The session kanban board (model: harness/kanban/kanban-model.md)."""
import json
import tempfile
from pathlib import Path

from expects import be_none, be_true, contain, equal, expect, raise_error
from mamba import before, context, description, it

from harness.installation.installer import Installer

Installer(repo=Path(__file__).resolve().parents[2]).ensure_import_path()

from bdd.bdd import Bdd  # noqa: E402
from ddd.ddd import Ddd  # noqa: E402
from generate.generate import Generate  # noqa: E402
from harness.kanban.board import Board  # noqa: E402
from harness.kanban.ticket import StageNotDone  # noqa: E402
from review.review import Review  # noqa: E402
from stories.stories import Stories  # noqa: E402
from ux.ux import Ux  # noqa: E402
from validate.validate import Validate  # noqa: E402


class SessionsFolder:
    """A temporary `.sessions/` folder: work sessions with their logs, closed sessions, backlog items."""

    def __init__(self) -> None:
        self.root = Path(tempfile.mkdtemp(prefix="kanban-sessions-"))

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

    with context("with a sessions folder of work sessions, closed sessions, default, backlog items, and archived sessions"):
        # sessions_folder holds pet-visits/, sign-up/, closed/browse-pets/, default/,
        #   _backlog/returns-and-refunds.md, _archive/old-spike/

        with it("should show every work session as a ticket"):
            # board.tickets
            #   -> Ticket(sessions_folder / "pet-visits", board)
            #   -> Ticket(sessions_folder / "sign-up", board)
            #   -> Ticket(sessions_folder / "closed" / "browse-pets", board)
            #   <- [pet-visits, sign-up, browse-pets]
            pass  # BDD: SIGNATURE

        with it("should leave default off the board"):
            # board.tickets
            #   <- no ticket named default
            pass  # BDD: SIGNATURE

        with it("should show each backlog item in the Backlog column"):
            # backlog.items
            #   -> board.backlog_items
            #       -> BacklogItem(sessions_folder / "_backlog" / "returns-and-refunds.md", board)
            #   <- [returns-and-refunds]
            pass  # BDD: SIGNATURE

        with it("should leave archived sessions off the board"):
            # board.tickets
            #   <- no ticket named old-spike
            pass  # BDD: SIGNATURE

        with it("should show closed sessions in Complete"):
            # complete.tickets
            #   -> board.tickets
            #   -> ticket.column  for each ticket
            #   <- [browse-pets]
            pass  # BDD: SIGNATURE

        with it("should name the ticket of the current session as active"):
            # board.active
            #   -> board.tickets
            #   <- pet-visits, the session named in .sessions/session.json
            pass  # BDD: SIGNATURE

        with it("should list every column with its tickets or items"):
            # board.to_json()
            #   -> backlog.items
            #   -> column.tickets  for each Stage and Complete
            #   -> ticket.column, ticket.is_done, ticket.next  for each ticket
            #   <- {"columns": [...], "active": "pet-visits"}
            pass  # BDD: SIGNATURE

with description("a backlog item") as self:
    with context("that a person has added to the backlog folder"):
        # .sessions/_backlog/returns-and-refunds.md
        # item = board.backlog_items[0]

        with context("that has been started"):
            # ticket = item.start("feature")

            with it("should open a ticket in Discovery"):
                # item.start("feature")
                #   -> board.new_ticket("Returns and refunds", "feature", None)
                #   <- ticket
                # ticket.column
                #   <- Discovery
                pass  # BDD: SIGNATURE

            with it("should name the item's file in the new ticket's session log"):
                # item.start("feature")
                #   -> board.new_ticket("Returns and refunds", "feature", None)
                # ticket reads session.log
                #   <- a line naming .sessions/_backlog/returns-and-refunds.md
                pass  # BDD: SIGNATURE

with description("a ticket") as self:
    # board = Board(sessions_folder, [stories, ddd, ux])

    with context("that has just been started"):
        # ticket = board.new_ticket("Pet visits", "feature", pawplace)

        with it("should be in Discovery, in progress"):
            # ticket.column
            #   -> ticket reads session.log  (no action lines)
            #   <- Discovery
            # ticket.is_done
            #   <- False
            pass  # BDD: SIGNATURE

        with it("should keep its title, scope, and lineage"):
            # ticket.title, ticket.scope, ticket.lineage
            #   <- "Pet visits", "feature", pawplace
            pass  # BDD: SIGNATURE

        with it("should name Generate on story_map as next"):
            # ticket.next
            #   -> ticket.progress
            #       -> discovery.work_required
            #       -> FidelityProgress(stories story_map, discovery, [])
            #   <- stories story_map, remaining [Generate, Validate, Review]
            pass  # BDD: SIGNATURE

    with context("with its first logged work on a Specification fidelity"):
        # session.log: generate <paths> ux mockup html

        with it("should be in Specification"):
            # ticket.column
            #   -> ticket reads session.log
            #   -> fidelity.stage  for ux mockup
            #   <- Specification
            pass  # BDD: SIGNATURE

    with context("with a fidelity generated"):
        # session.log: generate <paths> stories story_map markdown

        with it("should show Generate done and Validate and Review remaining for that fidelity"):
            # ticket.progress
            #   -> ticket reads session.log
            #   -> FidelityProgress(stories story_map, discovery, [Generate])
            # progress.remaining_actions
            #   -> discovery.actions
            #   <- [Validate, Review]
            pass  # BDD: SIGNATURE

        with context("with log lines whose paths hold spaces and commas"):
            # session.log: generate C:\My Work, D:\other files stories story_map markdown

            with it("should still find the practice and fidelity by name"):
                # ticket.progress
                #   -> ticket reads session.log
                #   <- stories story_map has Generate done
                pass  # BDD: SIGNATURE

        with context("that has a validate naming graph-rule violations"):
            # session.log: validate Stories story_map graph-rule actor-named-in-step map.md:12

            with it("should still need Validate for that fidelity"):
                # progress.remaining_actions
                #   -> ticket reads session.log
                #   <- [Validate, Review]
                pass  # BDD: SIGNATURE

        with context("that has a validate with no violations"):
            # session.log: validate Stories story_map no-chat

            with it("should show Validate done for that fidelity"):
                # progress.done_actions
                #   -> ticket reads session.log
                #   <- [Generate, Validate]
                pass  # BDD: SIGNATURE

            with it("should match the practice's class name in the validate line to its folder name"):
                # ticket.progress
                #   -> ticket reads session.log  (Stories in validate lines, stories in action lines)
                #   <- one FidelityProgress for stories story_map
                pass  # BDD: SIGNATURE

            with context("that has been reviewed"):
                # session.log: review stories story_map

                with it("should show the fidelity done"):
                    # progress.is_done
                    #   -> progress.remaining_actions
                    #       -> discovery.actions
                    #   <- True
                    pass  # BDD: SIGNATURE

        with context("that was reviewed before its validate passed"):
            # session.log: review stories story_map, then validate Stories story_map graph-rule ...

            with it("should not count the review"):
                # progress.done_actions
                #   -> ticket reads session.log
                #   <- [Generate]
                pass  # BDD: SIGNATURE

    with context("with every required fidelity in its stage done"):
        # session.log: generate, validate, review for story_map, bounded_context, ia

        with it("should be done, waiting in its stage's done part"):
            # ticket.is_done
            #   -> ticket.progress
            #       -> progress.is_done  for each Discovery fidelity
            #   <- True
            # discovery.done
            #   <- includes the ticket
            pass  # BDD: SIGNATURE

        with it("should have no next"):
            # ticket.next
            #   <- None
            pass  # BDD: SIGNATURE

        with context("that has been pulled"):
            # ticket.pull()

            with it("should be in the next stage"):
                # ticket.pull()
                #   -> ticket.is_done
                #   -> discovery.next_stage
                #   <- Specification
                # ticket.column
                #   <- Specification
                pass  # BDD: SIGNATURE

            with it("should write the stage it entered to its session log"):
                # ticket.pull()
                #   -> ticket session.log
                #   <- line: pull Specification
                pass  # BDD: SIGNATURE

        with context("in Implementation"):
            # session.log: pull Specification, pull Implementation, and every Implementation fidelity done

            with it("should refuse to be pulled past Implementation"):
                # ticket.pull()
                #   -> ticket.is_done
                #   -> implementation.next_stage
                #       <- None
                #   <- StageNotDone
                pass  # BDD: SIGNATURE

    with context("with its stage not done"):
        # session.log: generate stories story_map only

        with it("should refuse to be pulled"):
            # ticket.pull()
            #   -> ticket.is_done
            #       <- False
            #   <- StageNotDone
            pass  # BDD: SIGNATURE

        with it("should stay in its stage"):
            # ticket.column
            #   <- Discovery
            pass  # BDD: SIGNATURE

    with context("that has been closed"):
        # ticket.close()

        with it("should be in Complete"):
            # ticket.column
            #   <- Complete
            pass  # BDD: SIGNATURE

        with it("should have its folder in closed"):
            # ticket.close()
            #   <- Ticket at .sessions/closed/pet-visits
            pass  # BDD: SIGNATURE

    with context("that has been archived"):
        # ticket.archive()

        with it("should be off the board"):
            # board.tickets
            #   <- no ticket named pet-visits
            pass  # BDD: SIGNATURE

        with it("should have its folder in the archive"):
            # ticket.archive()
            #   <- Ticket at .sessions/_archive/pet-visits
            pass  # BDD: SIGNATURE
