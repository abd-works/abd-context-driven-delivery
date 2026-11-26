"""The session board as tools an agent calls (cdd MCP), through the MCP server, organised by story.

A behavior the board app shares across its tiers keeps its sentence here, in `app/tests/kanban/**/*.spec.shared.ts`."""
import json
import re
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

from expects import be_false, be_true, contain, equal, expect, have_key, raise_error, start_with
from mamba import after, before, context, description, it

from harness.installation.repository_toolsets import RepositoryToolsets

RepositoryToolsets(Path(__file__).resolve().parents[2]).ensure_import_path()

from harness.agent_tools.agent_tools import ToolsetReference, AgentToolSet  # noqa: E402
from harness.catalog_generator.catalog_practice import CatalogSkills  # noqa: E402
from harness.installation.files import CommandInstallation  # noqa: E402
from harness.installation.ide_layout import IdeLayout  # noqa: E402
from harness.installation.install_target import InstallTarget  # noqa: E402
from harness.installation.data_class import DataClass  # noqa: E402
from harness.installation.json_file import JsonFileUnreadable  # noqa: E402
from space.kanban.backlog_item import BacklogItem  # noqa: E402
from space.kanban.board import Stage  # noqa: E402
from space.kanban.card_name import NAME_LENGTH_LIMIT, BacklogItemTakenError, TicketNameTakenError, TitleNamesNothingError, TitleTooLongError  # noqa: E402
from harness.graph.violation import Violation  # noqa: E402
from space.kanban.report import ReportRule, ViolationNotInReportError  # noqa: E402
from space.kanban.session_board_examples import saved_graph, saved_practice  # noqa: E402
from harness.graph.edge import Edge  # noqa: E402
from harness.graph.saved_graph import SavedGraph, SavedNode  # noqa: E402
from space.kanban.story_test import progress_in  # noqa: E402
from space.kanban.ticket import NoReportToAcceptInError, Ticket  # noqa: E402
from space.session.session import MainStaysOpenError  # noqa: E402
from space.session.practices.practice_session_output import LastFormatLeftOut  # noqa: E402
from space.kanban.board import FolderOutsideRepositoryError, NotAStageError  # noqa: E402
from space.kanban.ticket_tree import NotAChildError, ParentMovesWithChildrenError  # noqa: E402
from space.kanban.ticket_choices import FormatNotOfferedError as TicketFormatNotOfferedError  # noqa: E402
from space.session.practices.practice_session_output import FidelityNotInPractice, FormatNotOfferedError as SessionFormatNotOfferedError  # noqa: E402
from space.kanban.board_practices import PracticeNotFoundError  # noqa: E402
from space.session import Sessions  # noqa: E402
from space.session.session import NotAPatternError, UnknownPracticeError  # noqa: E402

from space.kanban.board_tools_examples import CHECKED_GRAPH, DISCOVERY_DONE, JUDGED_REPORT, ProjectTools, STORY_MAP_GRAPH, WHOLE_STORIES_GRAPH, column_of, next_action_of, reports_of, session_file_of, ticket_names_in, ticket_of, violation_counts_of  # noqa: E402
from space.session.spec_support.throwaway_project import OPEN_PROJECTS


# A context whose examples only look at what its tools answered reads them once, in a ``before.all``, on a project of
# its own (``ProjectTools.answer_of``), built as the context's ``before.each`` would build it.
def pet_visits(project: ProjectTools) -> None:
    """A ticket done in Discovery and a backlog item."""
    project.ticket("pet-visits", *DISCOVERY_DONE, title="Pet visits")
    project.backlog_item("returns.md", "Returns and refunds")


def cut_off_loyalty_points(project: ProjectTools) -> Path:
    """A ticket loyalty-points whose session.json is cut off half way; answers that file."""
    cut_off = project.ticket("loyalty-points", title="Loyalty points") / "session.json"
    cut_off.write_text('{"name": "loyalty-points", "title": "Loyal', encoding="utf-8")
    return cut_off


def pet_visits_reports(project: ProjectTools) -> None:
    """pet-visits with an earlier and a latest clean engineering modules report, the latest with its graph."""
    pet_visits(project)
    reports = project.sessions / "pet-visits" / "validation-reports"
    reports.mkdir()
    (reports / "clean-engineering-modules-20261030T173000.md").write_text("earlier\n", encoding="utf-8")
    (reports / "clean-engineering-modules-20261031T041200.md").write_text("# Graph rule validation\n", encoding="utf-8")
    (reports / "clean-engineering-modules-20261031T041200.json").write_text(json.dumps(CHECKED_GRAPH), encoding="utf-8")


def modules_report(project: ProjectTools) -> dict:
    return project.call("fidelity-progress.report", ticket="pet-visits", fidelity="clean-engineering-modules")


# A report as validate now saves it: each rule's heading and where its text is kept, never the text, with its graph hits
# and the judgment the validating agent appended.
SAVED_MODULES_REPORT = """# Graph rule validation

## Summary

**Total graph violations:** 2

## Rules

### `domain-nouns-only`

Rule text: [clean_engineering/clean_engineering.md:127](clean_engineering.md#L127)

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [docs/map.md](docs/map.md#L12): Story ``: Name the story with a verb

## Judgment — `docs/map.md`

### `one-way-deps` — Fail
- map.md:4 `pets`: pets imports visits, which imports pets.
"""


def whole_modules_graph() -> dict:
    """The whole graph a validate of the modules checked: the node its hits are on, another node with facts and no hit,
    and the edge between them."""
    practice = saved_practice("clean_engineering", "node-1", "docs/map.md", 12, ("domain-nouns-only", "Name the story with a verb"), ("domain-nouns-only", "Name the epic with a verb"))
    practice.nodes.append(SavedNode({"node_id": "node-2", "name": "visits", "type": "Module", "practice": "clean_engineering", "file": "docs/other.md", "line": 3, "end_line": 9, "stage": "", "facts": {"members": ["Visit", "Vet"]}}))
    practice.edges.append(Edge.from_record({"kind": "depends_on", "parent": "node-1", "child": "node-2"}))
    practice.root_facts = {"classes": ["Visit", "Vet"]}
    return saved_graph(practice)


def modules_report_on(graph: dict) -> dict:
    """The report of pet-visits' modules fidelity, saved as validate saves it, with graph beside it."""
    def read(project: ProjectTools) -> dict:
        pet_visits_reports(project)
        reports = project.sessions / "pet-visits" / "validation-reports"
        (reports / "clean-engineering-modules-20261031T041200.md").write_text(SAVED_MODULES_REPORT, encoding="utf-8")
        (reports / "clean-engineering-modules-20261031T041200.json").write_text(json.dumps(graph), encoding="utf-8")
        return modules_report(project)
    return ProjectTools.answer_of(read)


def sign_up(project: ProjectTools, *log_lines: str) -> None:
    """A ticket called sign-up whose session log holds log_lines."""
    project.ticket("sign-up", *log_lines, title="Sign up")


def sign_up_board(*log_lines: str, then=lambda project: None) -> dict:
    """board.show on a project of its own holding sign-up, its log holding log_lines, after then has written to it."""
    def shown(project: ProjectTools) -> dict:
        sign_up(project, *log_lines)
        then(project)
        return project.call("board.show")

    return ProjectTools.answer_of(shown)


def story_map_written(project: ProjectTools) -> None:
    (project.root / ".context").mkdir(exist_ok=True)
    (project.root / ".context" / "story-map.md").write_text("# Story Map\n", encoding="utf-8")


def judged(project: ProjectTools) -> None:
    project.report("sign-up", "stories-story-map-20261031T041200")
    (project.sessions / "sign-up" / "validation-reports" / "stories-story-map-20261031T041200.md").write_text(JUDGED_REPORT, encoding="utf-8")


STORY_MAP_PASSED = (
    "2026-10-31T01:00:00Z generate /work stories story_map markdown stories no-chat",
    "2026-10-31T01:00:01Z validate Stories story_map no-chat",
)
STORY_MAP_VIOLATED = (
    "2026-10-31T01:00:00Z generate /work stories story_map markdown stories no-chat",
    "2026-10-31T01:00:01Z validate Stories story_map graph-rule verb-noun-format map.md:12 no-chat",
)
SCENARIOS_VIOLATED = ("2026-10-31T01:00:01Z validate Stories scenarios graph-rule verb-noun-format map.md:12 no-chat",)


def a_dozen_tickets_overview(project: ProjectTools) -> dict:
    """board.overview from ticket-0's own chat, on a project of twelve tickets done in Discovery."""
    for number in range(12):
        project.ticket(f"ticket-{number}", *DISCOVERY_DONE, title=f"Ticket {number}")
    # The chat bar of ticket-0's own chat, which works on ticket-0.
    project.call("sessions.switch", name="ticket-0", create=True)
    return project.call("board.overview")


def moves(project: ProjectTools, *directions: str) -> list[dict]:
    """pet-visits moved in each of directions in turn, next or previous: each move's answer."""
    pet_visits(project)
    return [project.call(f"ticket.move_{direction}", ticket="pet-visits") for direction in directions]


with description("the board tools") as self:
    with before.each:
        self.project = ProjectTools()

    with after.each:
        OPEN_PROJECTS.close_all()
        patch.stopall()

    # (E) See Work On Session Board
    with context("with a project whose sessions folder holds a ticket and a backlog item"):
        with before.each:
            self.project.ticket("pet-visits", *DISCOVERY_DONE, title="Pet visits")
            self.project.backlog_item("returns.md", "Returns and refunds")

        with before.all:
            self.board = ProjectTools.answer_of(lambda project: (pet_visits(project), project.call("board.show"))[1])

        # (S) Board App --> Display Board: a command names the formats chosen for an action that takes them, so no page
        # asks which actions do.
        with it("should name the formats chosen in the commands of an action that takes them"):
            column = column_of(self.board, "Discovery")
            ticket = next(ticket for ticket in [*column["in_progress"], *column["done"]] if ticket["name"] == "pet-visits")
            expect((" format=" in ticket["progress"][0]["commands"]["generate"], " format=" in ticket["progress"][0]["commands"]["validate"])).to(equal((True, False)))

        # (S) Person --> Choose Session Root
        with context("with folders in the repository"):
            with before.each:
                for folder in ("src/visits", "src/billing", "node_modules/left-pad", ".git/objects"):
                    (self.project.root / folder).mkdir(parents=True, exist_ok=True)

            with it("should leave out installed packages and hidden folders"):
                expect([folder for folder in self.project.call("board.folders") if folder in ("node_modules", ".git")]).to(equal([]))

            with context("that a person has chosen as a ticket's workpath"):
                with before.each:
                    self.chosen = self.project.call("session.choose_workpath", session=session_file_of("pet-visits"), path="src/visits")

                # Kept from the repository's top, so it can never name a folder in another checkout of the repository.
                with it("should keep the folder as the session's work folder"):
                    saved = json.loads((self.project.sessions / "pet-visits" / "session.json").read_text(encoding="utf-8"))
                    expect(saved["workpath"]).to(equal("src/visits"))

            with context("that a person has chosen as one practice's root"):
                with before.each:
                    self.chosen = self.project.call("practice-session-output.choose_root", session=session_file_of("pet-visits"), practice="stories", path="src/visits")

                with it("should write that practice's files there"):
                    files = self.project.call("fidelity-progress.files", ticket="pet-visits", fidelity="stories-story-map")["markdown"]
                    expect(files[0]["path"]).to(start_with("src/visits/"))

                with context("and then a new workpath for the ticket"):
                    with before.each:
                        self.moved = self.project.call("session.choose_workpath", session=session_file_of("pet-visits"), path="src")

                    with it("should keep that practice writing to the folder chosen for it"):
                        expect(self.moved["practices"]["stories"]["root"]).to(equal("src/visits"))

        # (S) Person --> Set Stage WIP Limit
        with it("should give every stage a limit of 3 tickets until a person sets one"):
            expect(column_of(self.board, "Discovery")["wip_limit"]).to(equal(3))

        with context("that sets a stage's limit below the tickets it holds"):
            with before.each:
                (self.project.sessions / "_board.json").unlink(missing_ok=True)
                self.limited = self.project.call("stage.set_wip_limit", stage="Discovery", limit=0)

            with it("should show the stage over its limit"):
                expect(self.limited["is_over_limit"]).to(be_true)

            with it("should count every ticket in the stage but main, which draws no card"):
                shown = [ticket for ticket in [*self.limited["in_progress"], *self.limited["done"]] if ticket["name"] != "main"]
                expect(self.limited["ticket_count"]).to(equal(len(shown)))

        with context("that sets a WIP limit on a column that is not a stage"):
            with it("should refuse it, naming the column"):
                expect(lambda: self.project.call("stage.set_wip_limit", stage="Backlog", limit=2)).to(raise_error(NotAStageError))

        # Validate saves only a graph's violations and the nodes they are on beside a report, and points at each rule's
        # text instead of copying it; the board shows the report as it did when both were saved whole.
        with context("with a report saved with its rules pointed at and only its violations' part of the graph"):
            with before.all:
                whole = whole_modules_graph()
                self.from_whole = modules_report_on(whole)
                self.from_kept = modules_report_on(SavedGraph.from_document(whole).violated.document)

            with it("should show every violation on its node, at its file and line, as the whole graph shows it"):
                expect(self.from_kept["rules"]).to(equal(self.from_whole["rules"]))

            with it("should describe each rule from its practice"):
                rule = next(rule["rule"] for rule in self.from_kept["rules"] if rule["rule"]["slug"] == "domain-nouns-only")
                expect(rule["body"]).to(start_with("Name modules after domain concepts"))

            with it("should list the judgment's findings beside the graph's hits"):
                judged = next(rule for rule in self.from_kept["rules"] if rule["rule"]["slug"] == "one-way-deps")
                expect((judged["violations"][0]["location"], judged["violations"][0]["line"])).to(equal(("docs/map.md", 4)))

        # (S) Person --> Open Validation Report
        with context("with validation reports saved for a fidelity"):
            with before.all:
                self.ticket, self.report = ProjectTools.answer_of(lambda project: (pet_visits_reports(project), project.ticket_json("pet-visits"), modules_report(project))[1:])

            with it("should show that fidelity's latest report"):
                latest = ".sessions/pet-visits/validation-reports/clean-engineering-modules-20261031T041200.md"
                expect(reports_of(self.ticket)).to(equal({"clean-engineering-modules": latest}))

            # (S) Person --> Fix Report Violations
            with it("should list each rule the report names with its violations"):
                report = self.report
                expect(report["rules"][0]["violations"][0]["message"]).to(equal("Name the story with a verb"))

            with it("should give a violation the line it failed on"):
                report = self.report
                expect(report["rules"][0]["violations"][0]["location"] + ":" + str(report["rules"][0]["violations"][0]["line"])).to(equal("docs/map.md:12"))

            with it("should show no source for a file that is not in the repository"):
                report = self.report
                expect(report["rules"][0]["violations"][0]["source"]).to(equal([]))

            # A graph names each file from the session's root, which can be a folder of the project with its own docs/map.md.
            with context("with a session whose root is a folder of the project"):
                with before.all:
                    def rooted(project: ProjectTools) -> dict:
                        pet_visits_reports(project)
                        session = project.sessions / "pet-visits" / "session.json"
                        root = project.root / "harness" / "pets"
                        session.write_text(json.dumps({**json.loads(session.read_text(encoding="utf-8")), "workpath": str(root)}), encoding="utf-8")
                        (root / "docs").mkdir(parents=True)
                        (root / "docs" / "map.md").write_text("".join(f"pets line {number}\n" for number in range(1, 21)), encoding="utf-8")
                        (project.root / "docs").mkdir()
                        (project.root / "docs" / "map.md").write_text("".join(f"project line {number}\n" for number in range(1, 21)), encoding="utf-8")
                        return modules_report(project)

                    self.report = ProjectTools.answer_of(rooted)

                with it("should name the violation's file from the project's root"):
                    report = self.report
                    expect(report["rules"][0]["violations"][0]["location"]).to(equal("harness/pets/docs/map.md"))

                with it("should show the source lines of the file in the session's root"):
                    report = self.report
                    expect(report["rules"][0]["violations"][0]["source"][0]["text"]).to(equal("pets line 10"))

            with it("should return exactly the fields a Violation marks as its data"):
                report = self.report
                expect(set(report["rules"][0]["violations"][0])).to(equal(set(DataClass(Violation).fields)))

            with it("should return exactly the fields a ReportRule marks as its data"):
                report = self.report
                expect(set(report["rules"][0])).to(equal(set(DataClass(ReportRule).fields)))

            with it("should count the violations of each rule"):
                report = self.report
                expect((report["rules"][0]["rule"]["slug"], report["rules"][0]["count"])).to(equal(("domain-nouns-only", 2)))

            with it("should send how many violations it names in all"):
                report = self.report
                expect(report["violation_count"]).to(equal(2))

            with it("should leave out the violations of other practices in the saved graph"):
                report = self.report
                expect([rule["rule"]["slug"] for rule in report["rules"]]).to(equal(["domain-nouns-only"]))

            with it("should say the report has its saved graph"):
                report = self.report
                expect(report["has_saved_graph"]).to(equal(True))

        with context("with a validation report on a rule the practice describes"):
            with before.each:
                self.project.report("pet-visits", "stories-story-map-20261031T041200", STORY_MAP_GRAPH)

            with it("should show the text of each rule under its name"):
                report = self.project.call("fidelity-progress.report", ticket="pet-visits", fidelity="stories-story-map")
                expect(report["rules"][0]["rule"]["body"]).to(contain("verb"))

            with it("should refuse to accept a violation the report does not list, naming it and the report"):
                accepting = lambda: self.project.call(
                    "fidelity-progress.accept_violation", ticket="pet-visits", fidelity="stories-story-map",
                    rule="verb-noun-format", message="No such finding.", location="docs/elsewhere.md",
                )
                expect(accepting).to(raise_error(ViolationNotInReportError, contain("verb-noun-format", "stories-story-map-20261031T041200")))

            # The agent that ran validate adds its judgment to the report, and the report panel must agree with it.
            with context("with the judgment of the agent that validated it"):
                with before.each:
                    (self.project.root / "docs").mkdir()
                    (self.project.root / "docs" / "map.md").write_text("".join(f"line {number}\n" for number in range(1, 21)), encoding="utf-8")
                    report = self.project.sessions / "pet-visits" / "validation-reports" / "stories-story-map-20261031T041200.md"
                    report.write_text(JUDGED_REPORT, encoding="utf-8")

                # Validate saves a report before the agent writes its judgment, so a run that never got judged must not
                # hide the result of the one before it.
                with context("with a later validate whose report has no judgment and no saved graph yet"):
                    with before.each:
                        self.project.report("pet-visits", "stories-story-map-20261031T050000")

                    with it("should still show the judged report"):
                        report = self.project.call("fidelity-progress.report", ticket="pet-visits", fidelity="stories-story-map")
                        expect(report["path"]).to(equal(".sessions/pet-visits/validation-reports/stories-story-map-20261031T041200.md"))

                    # A judgment is a result even when validate saved no graph beside the report.
                    with context("that its agent has judged since"):
                        with before.each:
                            later = self.project.sessions / "pet-visits" / "validation-reports" / "stories-story-map-20261031T050000.md"
                            later.write_text(JUDGED_REPORT, encoding="utf-8")

                        with it("should show the later judged report"):
                            report = self.project.call("fidelity-progress.report", ticket="pet-visits", fidelity="stories-story-map")
                            expect(report["path"]).to(equal(".sessions/pet-visits/validation-reports/stories-story-map-20261031T050000.md"))

                with it("should list each rule the judgment fails after the graph's rules, once each"):
                    report = self.project.call("fidelity-progress.report", ticket="pet-visits", fidelity="stories-story-map")
                    expect([rule["rule"]["slug"] for rule in report["rules"]]).to(equal(["verb-noun-format", "do-not-invent-requirements", "story-name-captures-system-mechanic"]))

                with it("should count each finding of a judged rule in every judged file"):
                    report = self.project.call("fidelity-progress.report", ticket="pet-visits", fidelity="stories-story-map")
                    expect(report["rules"][1]["count"]).to(equal(3))

                with it("should not read the passing rules listed after a judged rule as its findings"):
                    report = self.project.call("fidelity-progress.report", ticket="pet-visits", fidelity="stories-story-map")
                    expect(report["rules"][2]["count"]).to(equal(1))

                with it("should give a judged finding the judged file and its line"):
                    finding = self.project.call("fidelity-progress.report", ticket="pet-visits", fidelity="stories-story-map")["rules"][1]["violations"][0]
                    expect((finding["location"], finding["line"])).to(equal(("docs/map.md", 7)))

                with it("should show the source lines around a judged finding"):
                    finding = self.project.call("fidelity-progress.report", ticket="pet-visits", fidelity="stories-story-map")["rules"][1]["violations"][0]
                    expect(finding["source"][0]["text"]).to(equal("line 5"))

                with it("should give a finding that names no line its message"):
                    finding = self.project.call("fidelity-progress.report", ticket="pet-visits", fidelity="stories-story-map")["rules"][2]["violations"][0]
                    expect(finding["message"]).to(equal("`Do Stuff` does not say what it does."))

        with context("with no validation report of the fidelity"):
            with it("should refuse to accept a violation, naming the fidelity and the violation asked for"):
                accepting = lambda: self.project.call(
                    "fidelity-progress.accept_violation", ticket="pet-visits", fidelity="stories-story-map",
                    rule="verb-noun-format", message="`Do Stuff` does not say what it does.", location="docs/map.md",
                )
                expect(accepting).to(raise_error(NoReportToAcceptInError, contain("stories-story-map", "verb-noun-format", "docs/map.md")))

        # A saved graph keeps the hits of a scanner deleted after it was saved.
        with context("with a validation report on a rule no scanner checks any more"):
            with before.each:
                deleted = saved_graph(saved_practice("stories", "node-1", "docs/map.md", 12, ("evidence-distinguishes-observed-inferred-and-intended", "Label the evidence")))
                self.project.report("pet-visits", "stories-story-map-20261031T041200", deleted)

            with it("should leave that rule's hits out of the report"):
                report = self.project.call("fidelity-progress.report", ticket="pet-visits", fidelity="stories-story-map")
                expect(report["rules"]).to(equal([]))

        # A rule that requires a judge lists candidates: places to read, which nothing has decided are wrong.
        with context("with a validation report whose graph holds a candidate of a rule that requires a judge"):
            with before.each:
                listed = saved_graph(saved_practice("stories", "node-1", "docs/map.md", 12, ("verb-noun-format", "`Press The Mark` may name a gesture"), requires_judge=True))
                self.project.report("pet-visits", "stories-story-map-20261031T041200", listed)
                self.candidates = self.project.call("fidelity-progress.report", ticket="pet-visits", fidelity="stories-story-map")

            with it("should show the candidate under its rule as a candidate"):
                expect(self.candidates["rules"][0]["violations"][0]["severity"]).to(equal("candidate"))

            with it("should count the rule's candidates"):
                expect(self.candidates["rules"][0]["candidate_count"]).to(equal(1))

            with it("should count no violation"):
                expect(self.candidates["violation_count"]).to(equal(0))

            with it("should count the candidate apart from the violations"):
                expect(self.candidates["candidate_count"]).to(equal(1))

            # The judge has then read the candidates, so its findings are the rule's violations.
            with context("that the judgment fails on the same rule"):
                with before.each:
                    (self.project.root / "docs").mkdir()
                    (self.project.root / "docs" / "map.md").write_text("".join(f"line {number}\n" for number in range(1, 21)), encoding="utf-8")
                    report = self.project.sessions / "pet-visits" / "validation-reports" / "stories-story-map-20261031T041200.md"
                    report.write_text("# Graph rule validation\n\n## Judgment — `docs/map.md`\n\n### `verb-noun-format` — Fail\n- map.md:12 `Press The Mark`: names the gesture, not what the person means to do.\n", encoding="utf-8")
                    self.judged = self.project.call("fidelity-progress.report", ticket="pet-visits", fidelity="stories-story-map")

                with it("should show the judge's finding in place of the candidate"):
                    expect([violation["severity"] for violation in self.judged["rules"][0]["violations"]]).to(equal(["error"]))

                with it("should count the finding as a violation"):
                    expect(self.judged["violation_count"]).to(equal(1))

        # (S) Board App --> Display Board
        # The board is read once, on a project of the context's own, and the examples that look at it read what came
        # back: a read in each example's setup ran over the unit tier's budget for one example.
        with context("with another ticket whose session.json is cut off half way"):
            with before.all:
                self.shown = ProjectTools.answer_of(lambda project: (pet_visits(project), cut_off_loyalty_points(project), project.call("board.show"))[2])

            with before.each:
                self.cut_off = cut_off_loyalty_points(self.project)

            with it("should still show the tickets whose files read"):
                expect(ticket_names_in(self.shown, "Discovery")).to(contain("pet-visits"))

            with it("should leave the ticket it cannot read off its columns"):
                expect([name for column in self.shown["columns"] for name in ticket_names_in(self.shown, column["name"])]).not_to(contain("loyalty-points"))

            with it("should say which session file could not be read"):
                expect([unread["file"] for unread in self.shown["unreadable"]]).to(equal([".sessions/loyalty-points/session.json"]))

            with it("should say why it could not be read"):
                expect(self.shown["unreadable"][0]["error"]).to(contain("not a readable JSON object"))

            with it("should refuse a change to that ticket, leaving its file as it was"):
                expect(lambda: self.project.call("ticket.tag", ticket="loyalty-points", word="urgent")).to(raise_error(JsonFileUnreadable))
                expect(self.cut_off.read_text(encoding="utf-8")).to(equal('{"name": "loyalty-points", "title": "Loyal'))

        # (S) Person --> Edit Ticket Text, Tag Ticket: main is the default session, which the page offers neither for.
        with context("that edits the text of main, the default session"):
            with it("should refuse it, naming main"):
                expect(lambda: self.project.call("ticket.edit_text", ticket="main", text="Everything else.")).to(raise_error(MainStaysOpenError))

        with context("that tags main, the default session"):
            with it("should refuse it, naming main"):
                expect(lambda: self.project.call("ticket.tag", ticket="main", word="urgent")).to(raise_error(MainStaysOpenError))

        # (S) Person --> Split Ticket Into Child Tickets
        with context("that adds a child whose title makes the name of a ticket already there"):
            with it("should refuse it, naming that ticket"):
                expect(lambda: self.project.call("ticket.add_child", ticket="pet-visits", title="PET VISITS")).to(raise_error(TicketNameTakenError, contain("pet-visits")))

            with it("should refuse a child whose title gives no name"):
                expect(lambda: self.project.call("ticket.add_child", ticket="pet-visits", title="日本語")).to(raise_error(TitleNamesNothingError))

        with context("that overlays a pattern nobody registered on a ticket's graph"):
            with it("should refuse it, naming the pattern and the patterns there are"):
                choosing = lambda: self.project.call("ticket.choose_overlays", ticket="pet-visits", overlays=["no_such_pattern"])
                expect(choosing).to(raise_error(NotAPatternError, contain("no_such_pattern", "lern_domain_driven")))

        with context("that pulls out a ticket that has no parent"):
            with it("should refuse it, naming the ticket"):
                expect(lambda: self.project.call("ticket.pull_out", ticket="pet-visits")).to(raise_error(NotAChildError, contain("pet-visits")))

        with context("that moves a ticket split into children on its own"):
            with it("should refuse it, naming the parent"):
                self.project.call("ticket.add_child", ticket="pet-visits", title="Pet photos")
                expect(lambda: self.project.call("ticket.move_next", ticket="pet-visits")).to(raise_error(ParentMovesWithChildrenError, contain("pet-visits")))

        with context("that adds a child to a ticket"):
            with before.each:
                self.child = self.project.call("ticket.add_child", ticket="pet-visits", title="Book a visit")

            with it("should name the child after its title, under its parent"):
                expect((self.child["name"], self.child["session"]["parent"])).to(equal(("book-a-visit", "pet-visits")))

        # (E) Tickets
        # (S) Person --> Open Ticket Session
        with context("that opens a new ticket"):
            with before.each:
                self.opened = self.project.call("ticket.create", title="Loyalty points", scope="feature")

            with it("should return the new ticket in Discovery"):
                expect((self.opened["name"], self.opened["column"]["name"])).to(equal(("loyalty-points", "Discovery")))

        with context("that opens a ticket on a folder in the repository"):
            with before.each:
                self.project.call("ticket.create", title="Pet records", scope="feature", path="harness/pets")

            with it("should save that folder as the session's workpath"):
                fields = json.loads((self.project.sessions / "pet-records" / "session.json").read_text(encoding="utf-8"))
                expect(fields["workpath"]).to(equal("harness/pets"))

        # The chat bar's folder picker sends the folder in full; it is kept from the repository's top all the same.
        with context("that opens a ticket on a folder of the repository named in full"):
            with before.each:
                self.project.call("ticket.create", title="Pet records", scope="feature", path=str(self.project.root / "harness" / "pets"))

            with it("should save that folder from the repository's top as the session's workpath"):
                fields = json.loads((self.project.sessions / "pet-records" / "session.json").read_text(encoding="utf-8"))
                expect(fields["workpath"]).to(equal("harness/pets"))

        with context("that opens a ticket on a folder outside the repository"):
            with it("should refuse it, naming the folder"):
                outside = str(self.project.root.parent)
                expect(lambda: self.project.call("ticket.create", title="Pet records", scope="feature", path=outside)).to(raise_error(FolderOutsideRepositoryError, contain(outside.replace("\\", "\\\\"))))

        with context("that opens a ticket with no folder"):
            with before.each:
                self.project.call("ticket.create", title="Pet records", scope="feature")

            with it("should save no workpath, so the session works on the repository"):
                fields = json.loads((self.project.sessions / "pet-records" / "session.json").read_text(encoding="utf-8"))
                expect("workpath" in fields).to(equal(False))

        with context("that opens a ticket whose title has no letter a to z and no digit"):
            with it("should refuse an empty title"):
                expect(lambda: self.project.call("ticket.create", title="   ")).to(raise_error(TitleNamesNothingError))

            with it("should refuse a title in another script"):
                expect(lambda: self.project.call("ticket.create", title="日本語")).to(raise_error(TitleNamesNothingError))

            with it("should write no session into the sessions folder itself"):
                expect(lambda: self.project.call("ticket.create", title="日本語")).to(raise_error(TitleNamesNothingError))
                expect((self.project.sessions / "session.json").exists()).to(be_false)

        with context("that opens a ticket whose title makes the name of a ticket already there"):
            with it("should refuse it, naming that ticket"):
                expect(lambda: self.project.call("ticket.create", title="PET VISITS")).to(raise_error(TicketNameTakenError, contain("pet-visits")))

            with it("should keep that ticket's title"):
                expect(lambda: self.project.call("ticket.create", title="PET VISITS")).to(raise_error(TicketNameTakenError))
                fields = json.loads((self.project.sessions / "pet-visits" / "session.json").read_text(encoding="utf-8"))
                expect(fields["title"]).to(equal("Pet visits"))

            with it("should refuse a ticket titled main"):
                expect(lambda: self.project.call("ticket.create", title="main")).to(raise_error(TicketNameTakenError))

        with context("that opens a ticket whose title makes a name longer than a folder and a branch can be"):
            with before.each:
                self.long_title = "A very long title that goes on and on about the bookshop and its many needs"

            with it("should refuse it, naming the limit"):
                expect(lambda: self.project.call("ticket.create", title=self.long_title)).to(raise_error(TitleTooLongError, contain(str(NAME_LENGTH_LIMIT))))

            with it("should make no session folder"):
                expect(lambda: self.project.call("ticket.create", title=self.long_title)).to(raise_error(TitleTooLongError))
                expect([folder.name for folder in self.project.sessions.iterdir() if folder.name.startswith("a-very")]).to(equal([]))

        # (S) Person --> Split Ticket Into Child Tickets
        with context("that opens a ticket split from another"):
            with before.each:
                self.opened = self.project.call("ticket.create", title="Book a visit", scope="story", parent="pet-visits")

            with it("should name the ticket it was split from"):
                expect(self.opened["session"]["parent"]).to(equal("pet-visits"))

        # (S) Person --> Add Backlog Item
        with context("that adds a backlog item"):
            with before.each:
                self.added = self.project.call("backlog-item.create", title="Gift cards", text="Sell gift cards.")

            with it("should show the item in the Backlog with its text"):
                expect((self.added["title"], self.added["text"])).to(equal(("Gift cards", "Sell gift cards.")))

            with it("should write the title and text to one markdown file"):
                file = self.project.sessions / "_backlog" / "gift-cards.md"
                expect(file.read_text(encoding="utf-8")).to(equal("# Gift cards\n\nSell gift cards.\n"))

            with context("and then an item whose title makes the same file name"):
                with it("should refuse it, naming the file that keeps the first idea"):
                    expect(lambda: self.project.call("backlog-item.create", title="Gift cards", text="A second idea.")).to(raise_error(BacklogItemTakenError, contain("gift-cards.md")))

                with it("should keep the first idea's text"):
                    expect(lambda: self.project.call("backlog-item.create", title="Gift cards", text="A second idea.")).to(raise_error(BacklogItemTakenError))
                    file = self.project.sessions / "_backlog" / "gift-cards.md"
                    expect(file.read_text(encoding="utf-8")).to(equal("# Gift cards\n\nSell gift cards.\n"))

        with context("that adds a backlog item whose title has no letter a to z and no digit"):
            with it("should refuse it"):
                expect(lambda: self.project.call("backlog-item.create", title="", text="idea")).to(raise_error(TitleNamesNothingError))

            with it("should write no file without a name"):
                expect(lambda: self.project.call("backlog-item.create", title="日本語", text="idea")).to(raise_error(TitleNamesNothingError))
                expect((self.project.sessions / "_backlog" / ".md").exists()).to(be_false)

        with context("that starts a backlog item whose title makes the name of a ticket already there"):
            with before.each:
                self.project.backlog_item("pet-visits.md", "Pet visits")

            with it("should refuse it, naming that ticket"):
                expect(lambda: self.project.call("backlog-item.start", backlog_item="Pet visits")).to(raise_error(TicketNameTakenError, contain("pet-visits")))

            with it("should keep the idea in the Backlog"):
                expect(lambda: self.project.call("backlog-item.start", backlog_item="Pet visits")).to(raise_error(TicketNameTakenError))
                expect((self.project.sessions / "_backlog" / "pet-visits.md").is_file()).to(be_true)

        # (S) Person --> Add Backlog Item, Start Backlog Item
        with context("that starts a backlog item"):
            with before.all:
                def started(project: ProjectTools) -> tuple[dict, dict]:
                    pet_visits(project)
                    return project.call("backlog-item.start", backlog_item="Returns and refunds", scope="feature"), project.call("board.show")

                self.started, self.board = ProjectTools.answer_of(started)

            with it("should return the new ticket in Discovery"):
                expect((self.started["name"], self.started["column"]["name"])).to(equal(("returns-and-refunds", "Discovery")))

            with it("should take the item off the Backlog"):
                expect(column_of(self.board, "Backlog")["items"]).to(equal([]))

        # (S) Person --> Move Ticket, a ticket that is done in Discovery
        with context("that moves a ticket to the next column"):
            with before.all:
                self.moved = ProjectTools.answer_of(lambda project: moves(project, "next"))[-1]

            with it("should show the ticket in the next stage"):
                expect(self.moved["column"]["name"]).to(equal("Specification"))

            with it("should show the ticket in progress there"):
                expect(self.moved["is_done"]).to(be_false)

            # (S) Person --> Mark Ticket Done In Stage
            with context("with that stage's work not done"):
                with context("and on to the column after"):
                    with context("and past Hardening, the last stage"):
                        with before.all:
                            self.moved, self.moved_again = ProjectTools.answer_of(lambda project: moves(project, *["next"] * 9))[-2:]

                        with it("should close the ticket"):
                            expect(self.moved["column"]["name"]).to(equal("Complete"))

                        with it("should leave a ticket in Complete where it is on another move forward"):
                            expect(self.moved_again["column"]["name"]).to(equal("Complete"))

                        with context("and back again"):
                            with before.all:
                                self.moved = ProjectTools.answer_of(lambda project: moves(project, *["next"] * 8, "previous"))[-1]

                            with it("should reopen the ticket in Hardening"):
                                expect(self.moved["column"]["name"]).to(equal("Hardening"))

                with context("and back from Done"):
                    with before.all:
                        self.moved = ProjectTools.answer_of(lambda project: moves(project, "next", "next", "previous"))[-1]

                    with it("should show the ticket in progress in that stage"):
                        expect((self.moved["column"]["name"], self.moved["is_done"])).to(equal(("Specification", False)))

            with context("and back to the previous column"):
                with before.all:
                    self.moved = ProjectTools.answer_of(lambda project: moves(project, "next", "previous"))[-1]

                with it("should show the ticket in Discovery"):
                    expect(self.moved["column"]["name"]).to(equal("Discovery"))

        # (S) Person --> Choose Ticket Practices
        with context("that turns off a practice the session does not know"):
            with it("should refuse it, naming the practice"):
                try:
                    self.project.call("practice-session-output.enable", session=session_file_of("pet-visits"), practice="astrology", is_enabled=False)
                    refused = None
                except UnknownPracticeError as error:
                    refused = error.practice
                expect(refused).to(equal("astrology"))

        # The board app names and colours each practice from these, and finds a fidelity's practice among its slugs.
        with it("should name and colour every practice the board shows"):
            stories = self.board["practices"][0]
            expect((stories["key"], stories["short_name"], stories["colour"])).to(equal(("stories", "Stories", "#6BCB77")))

        # The board sends each fidelity once: in its own list, with its practice, which a tile finds it by.
        with it("should name each fidelity's practice beside the fidelity"):
            shown = next(entry for entry in self.board["fidelities"] if entry["fidelity"]["slug"] == "stories-story-map")
            expect(shown["practice"]).to(equal({"key": "stories"}))

        with it("should send no second list of a practice's fidelities"):
            stories = self.board["practices"][0]
            expect(stories).not_to(have_key("fidelities"))

        # (S) Person --> Open Help
        # The catalog's view of the board's practices names their pages and skills; the process makes it once for the
        # checkout, though every call makes a new board.
        with context("that is asked for its help and shown several times"):
            with before.all:
                def helped(project: ProjectTools) -> tuple[list[dict], int]:
                    pet_visits(project)
                    with patch.object(CatalogSkills, "__init__", autospec=True, side_effect=CatalogSkills.__init__) as made:
                        helps = [project.call("board.help", practice="stories"), project.call("board.help", practice="ux")]
                        project.call("board.show")
                        project.call("fidelity-progress.help", ticket="pet-visits", fidelity="stories-story-map")
                    return helps, made.call_count

                self.helps, self.made = ProjectTools.answer_of(helped)

            with it("should make the skill install its catalog pages are named with once"):
                expect(self.made).to(equal(1))

            with it("should still link each practice's own page"):
                expect([help["href"].rsplit("/", 1)[-1] for help in self.helps]).to(equal(["stories.html", "ux.html"]))

        with context("that opens help on a practice the board does not have"):
            with it("should refuse it, naming the practice"):
                try:
                    self.project.call("board.help", practice="astrology")
                    refused = None
                except PracticeNotFoundError as error:
                    refused = (error.practice, error.within)
                expect(refused).to(equal(("astrology", "the board")))

        # (E) Review Fidelity Outputs
        # (S) Person --> List Ticket Files
        with context("with a work folder outside the repository"):
            with before.each:
                self.outside = Path(tempfile.mkdtemp())
                (self.outside / "src").mkdir()
                (self.outside / "src" / "visits_spec.py").write_text("", encoding="utf-8")
                (self.project.sessions / "pet-visits" / "session.json").write_text(json.dumps({"name": "pet-visits", "workpath": str(self.outside)}), encoding="utf-8")

            with after.each:
                shutil.rmtree(self.outside)

            # (S) Person --> View Fidelity Files
            with it("should list the files a pattern finds there"):
                files = self.project.call("fidelity-progress.files", ticket="pet-visits", fidelity="bdd-behavior")["python"]
                expect(files).to(equal([{"path": (self.outside / "src" / "visits_spec.py").as_posix(), "exists": True, "is_changed": False, "link": "", "published_kind": "", "published_name": "", "format": "python", "fidelities": [], "is_listed": True, "is_session_work": False, "hidden_by_formats": []}]))

            # (S) Person --> View Fidelity Files, a path that names its module
            with it("should list the files a named part of the path finds there, in folders at any depth"):
                model = self.outside / "src" / "visits" / ".context" / "visits-model.md"
                model.parent.mkdir(parents=True)
                model.write_text("# Visits\n", encoding="utf-8")
                files = self.project.call("fidelity-progress.files", ticket="pet-visits", fidelity="clean-engineering-model")["markdown"]
                expect(files).to(equal([{"path": model.as_posix(), "exists": True, "is_changed": False, "link": "", "published_kind": "", "published_name": "", "format": "markdown", "fidelities": [], "is_listed": True, "is_session_work": False, "hidden_by_formats": []}]))

        with context("with a fidelity's markdown generated"):
            with before.all:
                def generated(project: ProjectTools) -> None:
                    docs = project.root / "docs" / ".context"
                    docs.mkdir(parents=True)
                    (docs / "story-map.md").write_text("# Story map\n", encoding="utf-8")
                    fields = {"outputs": {"stories": {"root": "docs", "story_map": {"markdown": "story-map.md"}}}}
                    (project.sessions / "pet-visits" / "session.json").write_text(json.dumps({"name": "pet-visits", **fields}), encoding="utf-8")

                self.generated = generated
                self.ticket = ProjectTools.answer_of(lambda project: (pet_visits(project), generated(project), project.ticket_json("pet-visits"))[2])

            with before.each:
                self.generated(self.project)

            with it("should list the file with whether it exists"):
                files = self.project.call("fidelity-progress.files", ticket="pet-visits", fidelity="stories-story-map")["markdown"]
                expect(files).to(equal([{"path": "docs/.context/story-map.md", "exists": True, "is_changed": False, "link": "", "published_kind": "", "published_name": "", "format": "markdown", "fidelities": [], "is_listed": True, "is_session_work": False, "hidden_by_formats": []}]))

            # (S) Person --> View Fidelity Files: the page opens tabs in the order Python sends the formats.
            with it("should send the formats in the order files are shown, markdown before code, and the diagram last"):
                files = self.project.call("fidelity-progress.files", ticket="pet-visits", fidelity="clean-engineering-model")
                expect(list(files)).to(equal(["markdown", "python", "typescript", "javascript", "drawio", "whiteboard"]))

            # One fidelity object per session: the progress's fidelity is the one an action on the ticket's session works with.
            with it("should give each progress the fidelity its ticket's session holds"):
                ticket = Ticket.load("pet-visits", project=self.project.root)
                expect(ticket.work.progress_of("stories-story-map").fidelity is ticket.session.practices["stories"].fidelities["story_map"]).to(be_true)

            with it("should give the board the ticket's session.json"):
                expect(self.ticket["session"]["session_file"]).to(equal(".sessions/pet-visits/session.json"))

            # (S) Person --> View Fidelity Files
            with it("should return no text for a file that is gone, such as one deleted since the board listed it"):
                opened = self.project.call("session.read_file", session=session_file_of("pet-visits"), path="docs/.context/gone.md")
                expect((opened["path"], opened["text"], opened["version"], opened["language"])).to(equal(("docs/.context/gone.md", "", "", "markdown")))

            # A practice root is a folder of the project, which a page may name by its whole path.
            with it("should return the text of a file named by its whole path under a practice root"):
                worktree = self.project.root / "kanban-worktree"
                worktree.mkdir(exist_ok=True)
                (worktree / "story-map.md").write_text("# Worktree map\n", encoding="utf-8")
                self.project.call("practice-session-output.choose_root", session=session_file_of("pet-visits"), practice="stories", path=str(worktree))
                opened = self.project.call("session.read_file", session=session_file_of("pet-visits"), path=(worktree / "story-map.md").as_posix())
                expect(opened["text"]).to(equal("# Worktree map\n"))

    # (S) Person --> Move Ticket, a ticket just started in Discovery
    with context("with a ticket in Discovery"):
        with before.all:
            self.ticket = ticket_of(sign_up_board(), "sign-up")

        with before.each:
            self.project.ticket("sign-up", title="Sign up")

        with context("that moves the ticket back out of Discovery"):
            with before.all:
                def moved_back(project: ProjectTools) -> tuple[dict, dict]:
                    sign_up(project)
                    return project.call("ticket.move_previous", ticket="sign-up"), project.call("board.show")

                self.moved, self.board = ProjectTools.answer_of(moved_back)

            with it("should show an item in the Backlog with the ticket's title"):
                expect(self.moved["title"]).to(equal("Sign up"))

            with it("should give the item's path from the project"):
                expect(self.moved["path"]).to(start_with(".sessions/"))

            # The page says a ticket moved back by finding the item that holds it, never by matching titles.
            with it("should name the ticket the item holds"):
                expect(self.moved["ticket"]).to(equal("sign-up"))

            with it("should take the ticket off the board's stages"):
                expect(ticket_names_in(self.board, "Discovery")).to(equal(["main"]))

            # (S) Person --> Add Backlog Item, Start Backlog Item
            with context("that starts the item again"):
                with before.all:
                    def started_again(project: ProjectTools) -> tuple[str, bool]:
                        sign_up(project)
                        project.call("ticket.move_previous", ticket="sign-up")
                        started = project.call("backlog-item.start", backlog_item="Sign up")
                        return started["name"], (project.sessions / "sign-up" / "session.json").is_file()

                    self.started_again = ProjectTools.answer_of(started_again)

                with it("should bring the ticket back with its work"):
                    expect(self.started_again).to(equal(("sign-up", True)))

        # (S) Person --> Send Next Fidelity Action
        with it("should allow only the actions that need no output before anything is generated"):
            expect(progress_in(self.ticket, "stories-story-map")["allowed_actions"]).to(equal(["partition", "generate", "iterate", "sketch", "document"]))

        # The board's Run sends render only once there is output to convert; Python says so, not the page.
        with it("should not allow Render before anything is generated"):
            expect(progress_in(self.ticket, "stories-story-map")["allowed_actions"]).not_to(contain("render"))

        # The Files app lists many fidelities' files in one call, sharing one look at what the branch changed.
        with it("should answer each fidelity's files by slug and format in one call"):
            files = self.project.call("ticket.fidelity_files", ticket="sign-up", fidelities=["stories-story-map", "ddd-bounded-context"])
            expect(sorted(files)).to(equal(["ddd-bounded-context", "stories-story-map"]))

        # The Files app's All session files: every file under the root, each saying which fidelities it belongs to, so the
        # stage and practice buttons narrow it, and its format, so the format buttons do.
        with context("with a story map and a file of no fidelity under its root"):
            with before.all:
                def root_files(project: ProjectTools) -> dict[str, dict]:
                    sign_up(project)
                    story_map = project.call("ticket.fidelity_files", ticket="sign-up", fidelities=["stories-story-map"])["stories-story-map"]["markdown"][0]["path"]
                    written = {
                        story_map: "text\n",
                        "notes/plain.txt": "text\n",
                        ".context/sign-up-sketch.md": "# Stories\n",
                        "src/orders/chat_bar.py": "class ChatBar:\n    pass\n",
                        "src/carts/cart.py": "@aggregate_root\nclass Cart:\n    pass\n",
                        "src/carts/carts.py": "class CartRepository:\n    pass\n",
                        "lib/billing/billing.py": "class Billing:\n    pass\n",
                        "old/design-canvas/version-1/project/canvas.json": "{}\n",
                        "old/design-canvas/versions.json": '{"version-1": "https://claude.ai/artifact/old-canvas"}\n',
                        "notes/flow.whiteboard": '{"board": "https://claude.ai/artifact/flow-board", "title": "Flow", "elements": {}}\n',
                    }
                    for path, text in written.items():
                        (project.root / path).parent.mkdir(parents=True, exist_ok=True)
                        (project.root / path).write_text(text, encoding="utf-8")
                    entries = project.call("ticket.root_files", ticket="sign-up", linked=["stories-story-map"])
                    return {entry["path"]: entry for entry in entries if entry["path"] in written}

                self.root_files = ProjectTools.answer_of(root_files)

            with it("should name the fidelities the story map belongs to"):
                expect([entry["fidelities"] for path, entry in self.root_files.items() if entry["format"] == "markdown" and not path.endswith("-sketch.md")]).to(equal([["stories-story-map"]]))

            with it("should name no fidelity for a file none declares"):
                expect(self.root_files["notes/plain.txt"]["fidelities"]).to(equal([]))

            # The Files app lists what Python says it lists: the page restates no rule of the selection. This session
            # chose code alone among the format groups, and its link names the story map.
            with it("should leave out the story map, in a format the session did not choose"):
                expect([self.root_files[path]["is_listed"] for path in self.root_files if self.root_files[path]["fidelities"] == ["stories-story-map"]]).to(equal([False]))

            with it("should leave out a file of no fidelity while the session works on practices"):
                expect(self.root_files["notes/plain.txt"]["is_listed"]).to(equal(False))

            # A folder that is no git repository has no branch to change a file, so its own work is what a fidelity holds.
            with it("should say a file a fidelity holds is the session's own work in a folder that is no repository"):
                expect([self.root_files[".context/sign-up-sketch.md"]["is_session_work"], self.root_files["notes/plain.txt"]["is_session_work"]]).to(equal([True, False]))

            # Reported 2026-11-18 (Nov 18 demo): the Files app opened without the sketch just written, as no fidelity
            # declares it, so a practice selected hid it.
            with it("should name the session's fidelities for its sketch, which holds a section for each practice"):
                expect(self.root_files[".context/sign-up-sketch.md"]["fidelities"]).to(contain("stories-story-map", "ux-ia"))

            # Requested 2026-11-16: a design canvas and a whiteboard open where they are published, wherever they lie.
            with it("should list a design canvas the root holds at the link it is published at"):
                expect(self.root_files["old/design-canvas/version-1/project/canvas.json"]["link"]).to(equal("https://claude.ai/artifact/old-canvas"))

            with it("should list a whiteboard file at its board's address"):
                expect(self.root_files["notes/flow.whiteboard"]["link"]).to(equal("https://claude.ai/artifact/flow-board"))

            with context("with code the session did not change"):
                with it("should name Clean Engineering code for it"):
                    expect(self.root_files["src/orders/chat_bar.py"]["fidelities"]).to(contain("clean-engineering-code"))

                with it("should name no DDD fidelity for code declaring no building block"):
                    expect([slug for slug in self.root_files["src/orders/chat_bar.py"]["fidelities"] if slug.startswith("ddd-")]).to(equal([]))

                with it("should name DDD tactics for code declaring a building block in a domain"):
                    expect(self.root_files["src/carts/carts.py"]["fidelities"]).to(contain("ddd-tactics"))

                with it("should name no DDD fidelity for code that only fits a DDD file pattern"):
                    expect([slug for slug in self.root_files["lib/billing/billing.py"]["fidelities"] if slug.startswith("ddd-")]).to(equal([]))

        with context("with a fidelity whose patterns find no file"):
            with it("should list no file for it, a pattern being no file"):
                def acceptance_tests(project: ProjectTools) -> dict:
                    sign_up(project)
                    return project.call("ticket.fidelity_files", ticket="sign-up", fidelities=["stories-acceptance-tests"])["stories-acceptance-tests"]

                listed = ProjectTools.answer_of(acceptance_tests)
                expect([entry["path"] for entries in listed.values() for entry in entries]).to(equal([]))

        # (S) Person --> Choose Action And Formats
        with context("with an action bar opened on its story map"):
            with before.each:
                self.chips = self.project.call("ticket.format_choices", ticket="sign-up", fidelities=["stories-story-map"])

            with it("should offer a chip for each group of formats the story map writes, diagram first"):
                expect([chip["label"] for chip in self.chips]).to(equal(["diagram", "markdown"]))

            # Requested 2026-11-16: the thin slice is a file the story map writes, not a format a person picks.
            with it("should offer no thin_slice chip"):
                expect([chip["label"] for chip in self.chips if chip["label"] == "thin_slice"]).to(equal([]))

            with it("should refuse thin_slice as a format of the story map"):
                expect(lambda: self.project.call("fidelity-session-output.choose_format", session=session_file_of("sign-up"), practice="stories", fidelity="story_map", format="thin_slice", is_chosen=True)).to(raise_error(SessionFormatNotOfferedError, contain("does not write thin_slice")))

            with it("should take the story map by the slug the guidance names it by, as well as by its name"):
                chosen = self.project.call("fidelity-session-output.choose_format", session=session_file_of("sign-up"), practice="stories", fidelity="stories-story-map", format="markdown", is_chosen=True)
                expect(chosen["name"]).to(equal("story_map"))

            with it("should refuse a fidelity the practice does not have, naming the ones it has"):
                expect(lambda: self.project.call("fidelity-session-output.choose_format", session=session_file_of("sign-up"), practice="stories", fidelity="ux-ia", format="markdown", is_chosen=True)).to(
                    raise_error(FidelityNotInPractice, contain("stories has no fidelity named ux-ia; it has story_map")))

            with it("should show the chip of its default format chosen until a person chooses"):
                expect([chip["label"] for chip in self.chips if chip["is_chosen"]]).to(equal(["markdown"]))

            with context("that turns the diagram chip on"):
                with before.all:
                    def diagram_on(project: ProjectTools) -> tuple[list, dict]:
                        sign_up(project)
                        chips = project.call("ticket.choose_formats", ticket="sign-up", fidelities=["stories-story-map"], label="diagram", is_chosen=True)
                        output = project.call("fidelity-session-output.choose_format", session=session_file_of("sign-up"), practice="stories", fidelity="story_map", format="markdown", is_chosen=True)
                        return chips, output

                    self.diagram_on, self.markdown_kept = ProjectTools.answer_of(diagram_on)

                with it("should show both chips chosen"):
                    expect([chip["label"] for chip in self.diagram_on if chip["is_chosen"]]).to(equal(["diagram", "markdown"]))

                # Requested 2026-11-20: "whiteboard isn't a separate format, there's only a button for 'diagram'".
                with it("should keep markdown and both diagram formats chosen for the story map in the session, in the order chosen"):
                    expect(self.markdown_kept["chosen_formats"]).to(equal(["markdown", "drawio", "whiteboard"]))

            with context("whose session kept only drawio of its diagram"):
                with before.all:
                    def drawio_only(project: ProjectTools) -> tuple[list, dict]:
                        sign_up(project)
                        project.call("fidelity-session-output.choose_format", session=session_file_of("sign-up"), practice="stories", fidelity="story_map", format="drawio", is_chosen=True)
                        shown = project.call("ticket.format_choices", ticket="sign-up", fidelities=["stories-story-map"])
                        project.call("ticket.choose_formats", ticket="sign-up", fidelities=["stories-story-map"], label="diagram", is_chosen=True)
                        output = project.call("fidelity-session-output.choose_format", session=session_file_of("sign-up"), practice="stories", fidelity="story_map", format="markdown", is_chosen=True)
                        return shown, output

                    self.drawio_shown, self.drawio_turned_on = ProjectTools.answer_of(drawio_only)

                with it("should show the diagram chip not chosen, since its whiteboard is not"):
                    expect([chip["label"] for chip in self.drawio_shown if chip["is_chosen"]]).to(equal(["markdown"]))

                with context("that turns the diagram chip on"):
                    with it("should choose the whiteboard as well"):
                        expect(self.drawio_turned_on["chosen_formats"]).to(equal(["markdown", "drawio", "whiteboard"]))

            with context("in a project whose defaults draw every diagram in drawio and whiteboard"):
                with before.all:
                    def drawn_both_ways(project: ProjectTools) -> tuple[list, list, list]:
                        from harness.installation.context_config import ContextConfig

                        sign_up(project)
                        ContextConfig(project.root).update(default_formats={"*": ["default", "drawio", "whiteboard"]})
                        shown = project.call("ticket.format_choices", ticket="sign-up", fidelities=["stories-story-map"])
                        off = project.call("ticket.choose_formats", ticket="sign-up", fidelities=["stories-story-map"], label="diagram", is_chosen=False)
                        on = project.call("ticket.choose_formats", ticket="sign-up", fidelities=["stories-story-map"], label="diagram", is_chosen=True)
                        return shown, off, on

                    self.both_shown, self.both_off, self.both_on = ProjectTools.answer_of(drawn_both_ways)

                with it("should show the diagram chip chosen, standing for both formats"):
                    diagram = next(chip for chip in self.both_shown if chip["label"] == "diagram")
                    expect((diagram["is_chosen"], diagram["formats"])).to(equal((True, ["drawio", "whiteboard"])))

                with context("that turns the diagram chip off"):
                    with it("should leave out both of its formats, keeping only markdown chosen"):
                        expect([chip["label"] for chip in self.both_off if chip["is_chosen"]]).to(equal(["markdown"]))

                    with context("and on again"):
                        with it("should choose both of its formats again"):
                            diagram = next(chip for chip in self.both_on if chip["label"] == "diagram")
                            expect((diagram["is_chosen"], diagram["formats"])).to(equal((True, ["drawio", "whiteboard"])))

            with context("that turns the markdown chip off"):
                with before.all:
                    def markdown_off(project: ProjectTools) -> list:
                        sign_up(project)
                        return project.call("ticket.choose_formats", ticket="sign-up", fidelities=["stories-story-map"], label="markdown", is_chosen=False)

                    self.markdown_off = lambda: ProjectTools.answer_of(markdown_off)

                # widget-13, answered 2026-11-23: a fidelity keeps at least one format chosen.
                with it("should refuse it, markdown being the only format chosen"):
                    expect(self.markdown_off).to(raise_error(LastFormatLeftOut, contain("markdown is the only format chosen")))

            with it("should refuse a chip label the story map does not offer, naming the labels it offers"):
                expect(lambda: self.project.call("ticket.choose_formats", ticket="sign-up", fidelities=["stories-story-map"], label="drawio", is_chosen=True)).to(
                    raise_error(TicketFormatNotOfferedError, contain("offers diagram, markdown"))
                )

            with it("should refuse a format the story map does not write"):
                expect(lambda: self.project.call("fidelity-session-output.choose_format", session=session_file_of("sign-up"), practice="stories", fidelity="story_map", format="python", is_chosen=True)).to(raise_error(SessionFormatNotOfferedError, contain("does not write python")))

        # Requested 2026-11-16: the realization is a file the scenarios write, not a format a person picks.
        with context("with an action bar opened on its scenarios"):
            with before.each:
                self.chips = self.project.call("ticket.format_choices", ticket="sign-up", fidelities=["stories-scenarios"])

            with it("should offer no realization chip"):
                expect([chip["label"] for chip in self.chips]).to(equal(["markdown", "code"]))

        with context("with an action bar opened on its UX mockup"):
            with before.each:
                self.chips = self.project.call("ticket.format_choices", ticket="sign-up", fidelities=["ux-mockup"])

            with it("should offer the diagram, the code, and the design canvas as a chip of its own after the code"):
                expect([chip["label"] for chip in self.chips]).to(equal(["diagram", "code", "canvas"]))

            with it("should send the drawing and the whiteboard for the diagram chip"):
                expect(sorted(next(chip["formats"] for chip in self.chips if chip["label"] == "diagram"))).to(equal(["drawio", "whiteboard"]))

            with it("should send the claude_design format for the canvas chip"):
                expect(next(chip["formats"] for chip in self.chips if chip["label"] == "canvas")).to(equal(["claude_design"]))

            with it("should show the canvas unchosen, since the mockup defaults to html"):
                expect([chip["label"] for chip in self.chips if chip["is_chosen"]]).to(equal(["code"]))

        with context("with an action bar opened on its UX mockup, a canvas written in the UX root"):
            with before.each:
                # A session working in a folder of its own counts every file there as its work.
                (self.project.root / "app").mkdir()
                session_file = self.project.sessions / "sign-up" / "session.json"
                session = json.loads(session_file.read_text(encoding="utf-8"))
                session_file.write_text(json.dumps({**session, "workpath": str(self.project.root / "app")}), encoding="utf-8")
                self.project.call("practice-session-output.choose_root", session=session_file_of("sign-up"), practice="ux", path="app/ux")
                canvas = self.project.root / "app" / "ux" / "design-canvas" / "version-1" / "project" / "canvas.json"
                canvas.parent.mkdir(parents=True)
                canvas.write_text("{}", encoding="utf-8")
                chips = self.project.call("ticket.format_choices", ticket="sign-up", fidelities=["ux-mockup"])
                self.canvas = next(chip for chip in chips if chip["label"] == "canvas")

            with it("should count the canvas as made"):
                expect(self.canvas["made"]).to(equal(1))

        # r3-gizmo-05: with six views on disk the front-end code's code chip said none was made, since it counted the
        # IA's and the mockup's files a person reviews for it rather than the views it writes.
        with context("with an action bar opened on its UX front-end code, a view written in the UX root"):
            with before.each:
                (self.project.root / "app").mkdir()
                session_file = self.project.sessions / "sign-up" / "session.json"
                session = json.loads(session_file.read_text(encoding="utf-8"))
                session_file.write_text(json.dumps({**session, "workpath": str(self.project.root / "app")}), encoding="utf-8")
                self.project.call("practice-session-output.choose_root", session=session_file_of("sign-up"), practice="ux", path="app/ux")
                view = self.project.root / "app" / "ux" / "src" / "CheckoutView.tsx"
                view.parent.mkdir(parents=True)
                view.write_text("export function CheckoutView() {}\n", encoding="utf-8")
                self.chips = self.project.call("ticket.format_choices", ticket="sign-up", fidelities=["ux-front-end-code"])
                self.root_files = {entry["path"]: entry for entry in self.project.call("ticket.root_files", ticket="sign-up")}

            with it("should name the front-end code among the fidelities whose file the view is"):
                expect(self.root_files["app/ux/src/CheckoutView.tsx"]["fidelities"]).to(contain("ux-front-end-code"))

            with it("should offer the code chip alone"):
                expect([chip["label"] for chip in self.chips]).to(equal(["code"]))

            with it("should count the view as made"):
                expect(self.chips[0]["made"]).to(equal(1))

        with context("with an action bar opened on its story map and its bounded context, the story map's markdown written"):
            with before.each:
                (self.project.root / ".context").mkdir(exist_ok=True)
                (self.project.root / ".context" / "story-map.md").write_text("# Story Map\n", encoding="utf-8")
                chips = self.project.call("ticket.format_choices", ticket="sign-up", fidelities=["stories-story-map", "ddd-bounded-context"])
                self.markdown = next(chip for chip in chips if chip["label"] == "markdown")
                self.chips_named = lambda label: [chip for chip in chips if chip["label"] == label and chip["is_chosen"]]

            with it("should count the fidelities that offer the markdown chip"):
                expect(self.markdown["offered"]).to(equal(2))

            with it("should count the fidelities that have a file in it already"):
                expect(self.markdown["made"]).to(equal(1))

            with it("should show chosen while every fidelity it covers keeps the format chosen"):
                expect(self.markdown["is_chosen"]).to(be_true)

            with it("should show the code chip unchosen, since no fidelity here defaults to code"):
                expect(self.chips_named("code")).to(equal([]))

            with it("should send each fidelity's own format for the chip"):
                expect(self.markdown["formats"]).to(equal(["markdown"]))

        with context("with an action bar opened on its story map, its markdown written"):
            with before.each:
                (self.project.root / ".context").mkdir(exist_ok=True)
                (self.project.root / ".context" / "story-map.md").write_text("# Story Map\n", encoding="utf-8")
                chips = self.project.call("ticket.format_choices", ticket="sign-up", fidelities=["stories-story-map"])
                self.markdown = next(chip for chip in chips if chip["label"] == "markdown")

            with it("should keep a chip chosen once its file is written"):
                expect(self.markdown["is_chosen"]).to(be_true)

        # A person can write a fidelity's file by hand, and checking it should not wait for a generate.
        with context("whose story map is already written, with nothing recorded"):
            with before.all:
                self.ticket = ticket_of(sign_up_board(then=story_map_written), "sign-up")

            with it("should allow Validate and Render on that file"):
                expect(progress_in(self.ticket, "stories-story-map")["allowed_actions"]).to(equal(["partition", "generate", "validate", "iterate", "sketch", "render", "document"]))

            with it("should still name generate as the next action"):
                expect(progress_in(self.ticket, "stories-story-map")["next_action"]).to(equal("generate"))

    # (S) Person --> Send Next Fidelity Action
    with context("with a ticket whose story map has passed validate"):
        with before.all:
            self.ticket = ticket_of(sign_up_board(*STORY_MAP_PASSED), "sign-up")

        # A story map generated and validated without violations is done.
        with it("should name generate on the next fidelity as the next action"):
            expect(next_action_of(self.ticket)).to(equal("generate"))

        # (S) Person --> Invoke Next Fidelity Action
        with it("should name each fidelity's own next action"):
            ticket = self.ticket
            expect((progress_in(ticket, "stories-story-map")["next_action"], progress_in(ticket, "stories-scenarios")["next_action"])).to(equal(("", "generate")))

        # The validating agent adds its judgment to the report after validate has logged its graph's result.
        with context("with a report whose judgment fails rules the graph passed"):
            with before.all:
                self.ticket = ticket_of(sign_up_board(*STORY_MAP_PASSED, then=judged), "sign-up")

            with it("should name validate as the next action"):
                expect(next_action_of(self.ticket)).to(equal("validate"))

            with it("should count each finding of the judgment"):
                expect(violation_counts_of(self.ticket)).to(equal({"stories-story-map": 5}))

    # (S) Person --> Send Next Fidelity Action
    with context("with a ticket whose next fidelity has violations"):
        # (S) Person --> Open Validation Report
        with context("with that fidelity's report saved with its graph"):
            with before.all:
                self.ticket = ticket_of(sign_up_board(*STORY_MAP_VIOLATED, then=lambda project: project.report("sign-up", "stories-story-map-20261031T041200", STORY_MAP_GRAPH)), "sign-up")

            with it("should count the violations of the fidelity on its ticket"):
                expect(violation_counts_of(self.ticket)).to(equal({"stories-story-map": 2}))

        with context("with that fidelity's report saved without its graph"):
            with before.all:
                self.ticket = ticket_of(sign_up_board(*STORY_MAP_VIOLATED, then=lambda project: project.report("sign-up", "stories-story-map-20261031T041200")), "sign-up")

            with it("should leave a fidelity with no saved graph uncounted"):
                expect(violation_counts_of(self.ticket)).to(equal({}))

    # (S) Person --> Open Validation Report
    with context("with violations left on two fidelities"):
        with before.each:
            self.project.ticket(
                "sign-up",
                "2026-10-31T01:00:00Z validate Stories story_map graph-rule verb-noun-format map.md:12 no-chat",
                "2026-10-31T01:00:01Z validate CleanEngineering modules graph-rule verb-noun-format map.md:12 no-chat",
                title="Sign up",
            )
            self.project.report("sign-up", "stories-story-map-20261031T041200", STORY_MAP_GRAPH)
            reports = self.project.sessions / "sign-up" / "validation-reports"
            (reports / "clean-engineering-modules-20261031T041200.md").write_text("# Graph rule validation\n", encoding="utf-8")
            (reports / "clean-engineering-modules-20261031T041200.json").write_text(json.dumps(CHECKED_GRAPH), encoding="utf-8")

        with it("should list the rules of every fidelity with violations"):
            rules = self.project.call("ticket.violations", ticket="sign-up")["rules"]
            expect([rule["fidelity"]["slug"] for rule in rules]).to(equal(["stories-story-map", "clean-engineering-modules"]))

        with it("should name the fidelity a rule was broken on"):
            report = self.project.call("fidelity-progress.report", ticket="sign-up", fidelity="stories-story-map")
            expect(report["rules"][0]["fidelity"]["slug"]).to(equal("stories-story-map"))

        # (S) Person --> Display Violations Of File Or Folder: the Files app's file menu shows the rules broken in one
        # file or folder, read from the same reports.
        with context("that are asked for in one file"):
            with it("should list only the violations in that file"):
                rules = self.project.call("ticket.violations_of", ticket="sign-up", path="docs/map.md")["rules"]
                expect({violation["location"] for rule in rules for violation in rule["violations"]}).to(equal({"docs/map.md"}))

        with context("that are asked for in a folder"):
            with it("should list the violations of every file in it, here every violation the ticket has"):
                in_folder = self.project.call("ticket.violations_of", ticket="sign-up", path="docs")["rules"]
                expect(in_folder).to(equal(self.project.call("ticket.violations", ticket="sign-up")["rules"]))

        with context("that are asked for in a folder holding none of them"):
            with it("should list no rule"):
                expect(self.project.call("ticket.violations_of", ticket="sign-up", path="src")["rules"]).to(equal([]))

        with context("that are asked for in a folder whose name only starts as another's"):
            with it("should list no violation of the other folder"):
                expect(self.project.call("ticket.violations_of", ticket="sign-up", path="doc")["rules"]).to(equal([]))

    # A ticket's card sits in one stage, so its violations are those of that stage's practices.
    with context("with violations left on a fidelity of a later stage"):
        with before.each:
            self.project.ticket(
                "sign-up",
                "2026-10-31T01:00:00Z validate Stories story_map graph-rule verb-noun-format map.md:12 no-chat",
                "2026-10-31T01:00:01Z validate Stories scenarios graph-rule plain-english-gwt-steps map.md:12 no-chat",
                "2026-10-31T01:00:02Z move Discovery no-chat",
                title="Sign up",
            )
            self.project.report("sign-up", "stories-story-map-20261031T041200", STORY_MAP_GRAPH)
            reports = self.project.sessions / "sign-up" / "validation-reports"
            (reports / "stories-scenarios-20261031T050000.md").write_text("# Graph rule validation\n", encoding="utf-8")
            (reports / "stories-scenarios-20261031T050000.json").write_text(json.dumps(WHOLE_STORIES_GRAPH), encoding="utf-8")

        with it("should list only the rules of the fidelities in the ticket's stage"):
            rules = self.project.call("ticket.violations", ticket="sign-up")["rules"]
            expect({rule["fidelity"]["slug"] for rule in rules}).to(equal({"stories-story-map"}))

    with context("with violations two fidelities of one practice share in their saved graphs"):
        with before.each:
            self.project.ticket(
                "sign-up",
                "2026-10-31T01:00:00Z validate Stories story_map graph-rule verb-noun-format map.md:12 no-chat",
                "2026-10-31T01:00:01Z validate Stories scenarios graph-rule verb-noun-format map.md:12 no-chat",
                "2026-10-31T01:00:02Z move Discovery no-chat",
                title="Sign up",
            )
            self.project.report("sign-up", "stories-story-map-20261031T041200", STORY_MAP_GRAPH)
            reports = self.project.sessions / "sign-up" / "validation-reports"
            (reports / "stories-scenarios-20261031T041200.md").write_text("# Graph rule validation\n", encoding="utf-8")
            (reports / "stories-scenarios-20261031T041200.json").write_text(json.dumps(STORY_MAP_GRAPH), encoding="utf-8")

        with it("should list a rule two fidelities share once"):
            rules = self.project.call("ticket.violations", ticket="sign-up")["rules"]
            expect([rule["fidelity"]["slug"] for rule in rules]).to(equal(["stories-story-map"]))

    # A saved graph holds the hits of every rule of its practice, but a report answers for its own fidelity.
    with context("with a scenarios report whose saved graph holds every stories rule's hits"):
        with before.all:
            def scenarios_read(newer_story_map: bool) -> tuple[dict, dict]:
                def read(project: ProjectTools) -> tuple[dict, dict]:
                    sign_up(project, *SCENARIOS_VIOLATED)
                    project.report("sign-up", "stories-scenarios-20261031T041200", WHOLE_STORIES_GRAPH)
                    if newer_story_map:
                        reports = project.sessions / "sign-up" / "validation-reports"
                        (reports / "stories-story-map-20261031T050000.md").write_text("# Graph rule validation\n", encoding="utf-8")
                    report = project.call("fidelity-progress.report", ticket="sign-up", fidelity="stories-scenarios")
                    return report, project.ticket_json("sign-up")

                return ProjectTools.answer_of(read)

            self.scenarios_read = scenarios_read
            self.report, self.ticket = scenarios_read(False)

        with it("should list the scenarios rules and the story map rules"):
            expect([rule["rule"]["slug"] for rule in self.report["rules"]]).to(equal(["verb-noun-format", "plain-english-gwt-steps"]))

        with it("should count the same rules on the ticket"):
            expect(violation_counts_of(self.ticket)).to(equal({"stories-scenarios": 2}))

        with context("with a story map report newer than the scenarios report"):
            with before.all:
                self.report, self.ticket = self.scenarios_read(True)

            with it("should leave the story map rules to the story map report"):
                expect([rule["rule"]["slug"] for rule in self.report["rules"]]).to(equal(["plain-english-gwt-steps"]))

            with it("should count only the rules the scenarios report answers for"):
                expect(violation_counts_of(self.ticket)).to(equal({"stories-scenarios": 1}))

    with context("with a session open in the project"):
        with before.all:
            def logged(project: ProjectTools) -> str:
                Sessions(project.root).switch("pet-visits", project.root, create=True)
                project.call("board.show")
                return (project.sessions / "pet-visits" / "session.log").read_text(encoding="utf-8")

            self.logged = ProjectTools.answer_of(logged)

        with it("should leave the board read out of the session log"):
            expect(self.logged).not_to(contain("board.show"))

    # The chat bar reads the board every turn through MCP, whose answers are cut off past their size limit, so it reads
    # board.overview: the active ticket whole and every other ticket by its name and column.
    with context("with the chat bar's overview of the board"):
        with before.all:
            self.overview = ProjectTools.answer_of(a_dozen_tickets_overview)

        with it("should send the active ticket whole, with its progress"):
            expect((self.overview["active"]["name"], len(self.overview["active"]["progress"]) > 0)).to(equal(("ticket-0", True)))

        with it("should name every open ticket in its column"):
            named = {ticket["name"] for column in self.overview["columns"] for ticket in column["tickets"]}
            expect(named).to(equal({"main", *(f"ticket-{number}" for number in range(12))}))

        with it("should send each ticket of a column by its name alone"):
            expect({tuple(ticket) for column in self.overview["columns"] for ticket in column["tickets"]}).to(equal({("name",)}))

        with it("should send each stage's work required by slug alone"):
            discovery = next(column for column in self.overview["columns"] if column["name"] == "Discovery")
            expect(discovery["work_required"][0]).to(equal({"slug": "stories-story-map"}))

        with it("should send each practice's colour and editor under its key"):
            expect(sorted(self.overview["practices"][0])).to(equal(["colour", "editor", "practice", "short_name"]))

        with it("should stay well inside an MCP answer with a dozen tickets"):
            expect(len(json.dumps(self.overview)) < 40_000).to(be_true)

        # Each child sent whole carries its own progress and its own children, so a ticket two levels of children deep
        # tripled the answer past the chat bar's size limit.
        with context("that has children two levels deep"):
            with before.all:
                def with_children(project: ProjectTools) -> dict:
                    a_dozen_tickets_overview(project)
                    project.ticket("child-1", *DISCOVERY_DONE, title="Child 1", parent="ticket-0")
                    project.ticket("grandchild-1", *DISCOVERY_DONE, title="Grandchild 1", parent="child-1")
                    return project.call("board.overview")

                self.overview = ProjectTools.answer_of(with_children)

            with it("should send the active ticket's children by name alone"):
                expect(self.overview["active"]["children"]).to(equal([{"name": "child-1"}]))

            with it("should stay as small as a ticket with no children"):
                expect(len(json.dumps(self.overview)) < 40_000).to(be_true)

        # A ticket's idea file can run to tens of thousands of characters, as a plan does; sent in the overview, it took
        # the chat bar's answer past MCP's size limit, and the bar never draws it.
        with context("with an active ticket whose idea file is long"):
            with before.all:
                def with_long_text(project: ProjectTools) -> dict:
                    a_dozen_tickets_overview(project)
                    (project.sessions / "ticket-0" / "ticket-0.md").write_text("# Ticket 0\n\n" + "A plan line.\n" * 5_000, encoding="utf-8")
                    return project.call("board.overview")

                self.overview = ProjectTools.answer_of(with_long_text)

            with it("should leave the ticket's text out"):
                expect(self.overview["active"]["text"]).to(equal(""))

            with it("should stay as small as a ticket with no text"):
                expect(len(json.dumps(self.overview)) < 40_000).to(be_true)

        # A move answers with the ticket it moved; sent with a plan's idea file, that answer went past MCP's size limit,
        # so the agent that moved the ticket could not read what came of it. ticket.show still sends the text.
        with context("with a ticket whose idea file is long, moved"):
            with before.all:
                def moved_with_long_text(project: ProjectTools) -> list[dict]:
                    pet_visits(project)
                    (project.sessions / "pet-visits" / "pet-visits.md").write_text("# Pet visits\n\n" + "A plan line.\n" * 5_000, encoding="utf-8")
                    return [project.call("ticket.move_to", ticket="pet-visits", stage="Specification"), project.call("ticket.move_next", ticket="pet-visits")]

                self.moved_to, self.moved_next = ProjectTools.answer_of(moved_with_long_text)

            with it("should leave the text out of move_to's answer"):
                expect(self.moved_to["text"]).to(equal(""))

            with it("should leave the text out of move_next's answer"):
                expect(self.moved_next["text"]).to(equal(""))

        # (S) Person --> Show Backlog Items In Session List: the session list offers the Backlog's items to start, a
        # parent's children under it, from the overview it reads every turn, so each item goes by its title alone.
        with context("that holds backlog items, one a parent of two"):
            with before.all:
                def with_backlog(project: ProjectTools) -> dict:
                    project.backlog_item("payment-retry.md", "Payment retry")
                    (project.sessions / "_backlog" / "checkout-flow").mkdir()
                    project.backlog_item("checkout-flow/checkout-flow.md", "Checkout flow")
                    project.backlog_item("checkout-flow/address-form.md", "Address form")
                    project.backlog_item("checkout-flow/card-form.md", "Card form")
                    return project.call("board.overview")

                self.backlog = column_of(ProjectTools.answer_of(with_backlog), "Backlog")

            with it("should send the Backlog's own items by title, each with its children by title"):
                expect(sorted(self.backlog["items"], key=lambda item: item["title"])).to(equal([
                    {"title": "Checkout flow", "children": [{"title": "Address form"}, {"title": "Card form"}]},
                    {"title": "Payment retry", "children": []},
                ]))

            with it("should send no items in a stage"):
                expect(column_of(self.overview, "Discovery")["items"]).to(equal([]))

    with context("that are published through the cdd server"):
        with it("should name each tool after its object"):
            names = set(self.project.server.tools)
            expect(names).to(equal({
                "board.show", "board.overview", "board.help", "board.folders", "board.set_sends_fixes_directly", "board.save_again", "stage.set_wip_limit",
                "ticket.create", "ticket.activate", "ticket.branch", "ticket.work_branch", "ticket.close_choices", "ticket.fidelity_files", "ticket.root_files", "ticket.format_choices", "ticket.choose_formats", "ticket.overlay_choices", "ticket.choose_overlays", "ticket.move_next", "ticket.move_previous", "ticket.move_to", "ticket.close", "ticket.archive", "ticket.violations", "ticket.violations_of", "ticket.assign_chat",
                "ticket.edit_text", "ticket.tag", "ticket.delete", "ticket.add_child", "ticket.pull_out", "ticket.reassign_parent", "ticket.move_before",
                "fidelity-progress.report", "fidelity-progress.accept_violation", "fidelity-progress.reopen_violation", "fidelity-progress.files", "fidelity-progress.help",
                "sessions.current", "sessions.switch", "session.close", "session.append_log", "session.mark_loop", "session.read_loop",
                "session.choose_workpath", "session.folder_files", "session.workpath_files", "session.all_files", "session.delete_file", "session.read_file", "session.write_file", "session.check_changed_artifact", "session.file", "session.graph_trees", "session.graph_branch", "session.graph_fix_prompt", "session.graph_filter_choices", "session.graph_node_ranges", "session.graph_members", "session.add_to_chat_context", "session.show",
                "session.guidance_selection", "session.toggle_guidance", "session.guidance_selection_after", "session.record_test_tier",
                "session.write_handoff", "session.read_handoff_format", "session.read_cdr_format", "session.list_cdrs", "session.write_cdr",
                "practice-session-output.enable", "practice-session-output.choose_root", "practice-session-output.add_root", "practice-session-output.use_default_root", "fidelity-session-output.choose_root", "fidelity-session-output.add_root", "fidelity-session-output.propose_roots", "fidelity-session-output.choose_format",
                "backlog-item.create", "backlog-item.start", "backlog-item.start_under", "backlog-item.edit_text", "backlog-item.move_before",
                "backlog-item.move_after", "backlog-item.nest_under", "backlog-item.leave_parent", "backlog-item.delete",
            }))

        # A person adds an idea from the chat with /backlog, as the + on the board's Backlog column does.
        with it("should install adding a backlog item as the backlog slash command"):
            installed = tempfile.mkdtemp()
            CommandInstallation.into(InstallTarget(IdeLayout("Claude"), installed)).install(ToolsetReference.of(BacklogItem).made().tools["create"])
            expect([file.name for file in Path(installed).rglob("*.md")]).to(equal(["backlog.md"]))

        # An agent that opens a ticket must work in the ticket's own worktree, not in the chat that opened it.
        with it("should tell an agent opening a ticket to activate it and work in a chat in its worktree"):
            for tool in ("ticket.create", "backlog-item.start"):
                described = self.project.server.tools[tool].description
                expect(described).to(contain("Then run ticket.activate"))
                expect(described).to(contain("start_session with cwd set to the ticket's worktree"))

        with it("should take the ticket's name on every ticket tool that acts on one"):
            schema = self.project.server.tools["ticket.move_next"].callable
            expect(list(__import__("inspect").signature(schema).parameters)).to(equal(["ticket"]))

    # The shapes in data.py are the only agreement between the two languages: the language adapter is written from them.
    with context("whose JSON is compared with the shapes in data.py"):
        with before.all:
            def shown(project: ProjectTools) -> tuple[dict, dict]:
                project.ticket("pet-visits", title="Pet visits")
                project.backlog_item("returns.md", "Returns and refunds")
                board = project.call("board.show")
                project.call("sessions.switch", name="pet-visits", create=True)
                return board, project.call("board.show")["active"]

            self.board, self.active = ProjectTools.answer_of(shown)

        with it("should return exactly the fields a Ticket marks as its data"):
            expect(set(ticket_of(self.board, "pet-visits"))).to(equal(set(DataClass(Ticket).fields)))

        with it("should send a Ticket's progress as one FidelityProgress per fidelity, each naming its fidelity"):
            expect([progress["fidelity"]["slug"] for progress in ticket_of(self.board, "pet-visits")["progress"]][:2]).to(equal(["stories-story-map", "ddd-bounded-context"]))

        with it("should send a Ticket's column by its name alone, since the column sends the ticket"):
            expect(ticket_of(self.board, "pet-visits")["column"]).to(equal({"name": "Discovery"}))

        # board.show is read every turn by the chat bar through MCP, whose answers are cut off past their size limit, so
        # a fidelity's guidance text, which its help call reads, is never repeated in it.
        with it("should send each fidelity a Stage requires by its slug alone"):
            expect(column_of(self.board, "Discovery")["work_required"][0]).to(equal({"slug": "stories-story-map"}))

        with it("should send each fidelity a Ticket's progress is on by its slug alone"):
            expect(ticket_of(self.board, "pet-visits")["progress"][0]["fidelity"]).to(equal({"slug": "stories-story-map"}))

        with it("should send a Ticket's next fidelity by its ticket and slug alone, since its progress sends it"):
            expect(ticket_of(self.board, "pet-visits")["next"]).to(equal({"ticket": {"name": "pet-visits"}, "fidelity": {"slug": "stories-story-map"}}))

        with it("should send the board's active ticket whole, so the chat bar never finds it again by its name"):
            active = self.active
            expect((active["name"], "progress" in active)).to(equal(("pet-visits", True)))

        with it("should return exactly the fields a BacklogItem marks as its data"):
            expect(set(column_of(self.board, "Backlog")["items"][0])).to(equal(set(DataClass(BacklogItem).fields)))

        with it("should return exactly the fields a Stage marks as its data"):
            expect(set(column_of(self.board, "Discovery"))).to(equal(set(DataClass(Stage).fields)))

    with context("whose signatures are compared with the board app's shared behaviors"):
        with it("should state every shared behavior here under the same sentence"):
            spec = Path(__file__).read_text(encoding="utf-8")
            signatures = set(re.findall(r'with it\("(should [^"]+)"\)', spec))
            shared_files = (Path(__file__).parent / "app" / "tests" / "kanban").rglob("*.spec.shared.ts")
            shared = {sentence for path in shared_files for sentence in re.findall(r"\bit\('(should .+?)',", path.read_text(encoding="utf-8"))}
            only_on_the_page = {"should leave a stage holding fewer tickets than its limit within it"}
            expect(sorted(shared - signatures - only_on_the_page)).to(equal([]))
