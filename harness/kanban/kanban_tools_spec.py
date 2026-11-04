"""The session board as tools an agent calls (cdd MCP), through the MCP server, organised by story.

A behavior the board app shares across its tiers keeps its sentence here, in `app/tests/kanban/**/*.spec.shared.ts`."""
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from expects import be_false, be_true, contain, equal, expect, have_key, match, raise_error, start_with
from mamba import after, before, context, description, it

from harness.installation.installer import Installer

Installer(repo=Path(__file__).resolve().parents[2]).ensure_import_path()

from harness.kanban.data import BacklogItemData, ColumnData, ReportRuleData, TicketData, ViolationData, WorkspaceData  # noqa: E402
from harness.kanban.ticket import FidelityNotFoundError  # noqa: E402
from harness.mcp.mcp_server import McpServer  # noqa: E402
from space.session import Session  # noqa: E402

TOOLSETS = ("harness.kanban.board:Board", "harness.kanban.ticket:Ticket", "harness.kanban.backlog_item:BacklogItem")
STAGE_COLUMNS = {"Discovery": 1, "Specification": 2, "Implementation": 3}

DISCOVERY_DONE = [
    line
    for practice, practice_class, fidelity in (
        ("stories", "Stories", "story_map"), ("ddd", "Ddd", "bounded_context"), ("ux", "Ux", "ia"),
        ("clean_engineering", "CleanEngineering", "modules"), ("bdd", "Bdd", "behavior"),
    )
    for line in (
        f"2026-10-31T01:00:00Z generate /work {practice} {fidelity} markdown {practice} no-chat",
        f"2026-10-31T01:00:01Z validate {practice_class} {fidelity} no-chat",
        f"2026-10-31T01:00:02Z review /work {practice} {fidelity} markdown {practice} no-chat",
    )
]
CHECKED_GRAPH = {
    "practices": {
        "clean_engineering": {
            "nodes": [["node-1", "", "Story", "clean_engineering", "docs/map.md", 12, 12]],
            "rules": [["domain-nouns-only", "node-1", "Name the story with a verb"], ["domain-nouns-only", "node-1", "Name the epic with a verb"]],
        },
        "stories": {
            "nodes": [["node-2", "", "Story", "stories", "docs/other.md", 3, 3]],
            "rules": [["actor-named-in-step", "node-2", "Name the actor"]],
        },
    },
}
STORY_MAP_GRAPH = {
    "practices": {
        "stories": {
            "nodes": [["node-1", "", "Story", "stories", "docs/map.md", 12, 12]],
            "rules": [["verb-noun-format", "node-1", "Name the story with a verb"], ["verb-noun-format", "node-1", "Name the epic with a verb"]],
        },
    },
}
# A report as validate saves it, with the judgment the validating agent added: a rule the graph already hit, a failed rule
# with two findings, and a rule an older report marked Warn.
JUDGED_REPORT = """# Graph rule validation

## Judgment — `docs/map.md`

| Rule | Verdict |
|---|---|
| verb-noun-format | **Fail** (graph rule) |

### `verb-noun-format` — Fail
Graph rule: the story at line 12 opens with a noun.

### `do-not-invent-requirements` — Fail
- map.md:7 `Open Board`: no source names the board command.
- map.md:9 `Close Board`: invented.

### `story-name-captures-system-mechanic` — Warn
- map.md:3 `Do Stuff` does not say what it does.

### Passes
Everything else.
"""

# One hit each on a story map rule and a scenarios rule.
WHOLE_STORIES_GRAPH = {
    "practices": {
        "stories": {
            "nodes": [["node-1", "", "Story", "stories", "docs/map.md", 12, 12]],
            "rules": [
                ["verb-noun-format", "node-1", "Name the story with a verb"],
                ["plain-english-gwt-steps", "node-1", "Write the step in plain English"],
            ],
        },
    },
}


class ProjectTools:
    """A project with a sessions folder, and the board's tools called through the MCP server."""

    def __init__(self) -> None:
        self.root = Path(tempfile.mkdtemp(prefix="kanban-tools-"))
        self.sessions = self.root / ".sessions"
        self.sessions.mkdir()
        (self.root / ".git").mkdir()
        os.environ["CDD_PROJECT"] = str(self.root)
        self.server = McpServer(project=self.root)
        self.server.start(TOOLSETS)

    def ticket(self, name: str, *log_lines: str, **fields) -> Path:
        folder = self.sessions / name
        folder.mkdir()
        (folder / "session.json").write_text(json.dumps({"name": name, **fields}), encoding="utf-8")
        (folder / "session.log").write_text("".join(f"{line}\n" for line in log_lines), encoding="utf-8")
        return folder

    def report(self, ticket: str, name: str, graph: dict | None = None) -> None:
        reports = self.sessions / ticket / "validation-reports"
        reports.mkdir(exist_ok=True)
        (reports / f"{name}.md").write_text("# Graph rule validation\n", encoding="utf-8")
        if graph:
            (reports / f"{name}.json").write_text(json.dumps(graph), encoding="utf-8")

    def backlog_item(self, file_name: str, heading: str) -> None:
        folder = self.sessions / "_backlog"
        folder.mkdir(exist_ok=True)
        (folder / file_name).write_text(f"# {heading}\n\nAn idea.\n", encoding="utf-8")

    def call(self, tool: str, **arguments):
        result = self.server.invoke_tool(tool, arguments)
        return json.loads(json.dumps(result, default=lambda value: value.to_json()))

    def column(self, name: str) -> dict:
        return next(column for column in self.call("board.show")["columns"] if column["name"] == name)

    def tickets_in(self, name: str) -> list:
        column = self.column(name)
        return [ticket["name"] for key in ("in_progress", "done", "tickets") for ticket in column.get(key, [])]

    def ticket_json(self, name: str) -> dict:
        columns = self.call("board.show")["columns"]
        return next(ticket for column in columns for key in ("in_progress", "done", "tickets")
                    for ticket in column.get(key, []) if ticket["name"] == name)


with description("the board tools") as self:
    with before.each:
        Session.forget_current()
        self.project = ProjectTools()

    with after.each:
        Session.forget_current()
        os.environ.pop("CDD_PROJECT", None)

    # (E) See Work On Session Board
    with context("with a project whose sessions folder holds a ticket and a backlog item"):
        with before.each:
            self.project.ticket("pet-visits", *DISCOVERY_DONE, title="Pet visits")
            self.project.backlog_item("returns.md", "Returns and refunds")

        # (S) Board App --> Display Board
        with it("should return every column of the board"):
            columns = [column["name"] for column in self.project.call("board.show")["columns"]]
            expect(columns).to(equal(["Backlog", "Discovery", "Specification", "Implementation", "Complete"]))

        with it("should name the project the board belongs to"):
            expect(self.project.call("board.show")["project"]).to(equal(self.project.root.name))

        # (S) Board App --> Display Backlog Items As Tickets
        with it("should say when a backlog item last changed"):
            expect(self.project.column("Backlog")["items"][0]["last_activity"]).to(match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"))

        with it("should give a backlog item its text"):
            expect(self.project.column("Backlog")["items"][0]["text"]).to(equal("An idea."))

        # (S) Person --> Choose Session Root
        with it("should say a ticket works on the whole repository until a person chooses a root"):
            expect(self.project.ticket_json("pet-visits")["root"]).to(equal(""))

        with context("with folders in the repository"):
            with before.each:
                for folder in ("src/visits", "src/billing", "node_modules/left-pad", ".git/objects"):
                    (self.project.root / folder).mkdir(parents=True, exist_ok=True)

            with it("should list the folders at the top of the repository a root can be chosen from"):
                expect(self.project.call("board.folders")).to(contain("src"))

            with it("should leave out installed packages and hidden folders"):
                expect([folder for folder in self.project.call("board.folders") if folder in ("node_modules", ".git")]).to(equal([]))

            with it("should list the folders inside one, as paths from the project"):
                expect(self.project.call("board.folders", path="src")).to(equal(["src/billing", "src/visits"]))

            with context("that a person has chosen as a ticket's root"):
                with before.each:
                    self.chosen = self.project.call("ticket.choose_root", ticket="pet-visits", path="src/visits")

                with it("should show the folder as the ticket's root"):
                    expect(self.chosen["root"]).to(equal("src/visits"))

                with it("should keep the folder as the session's work folder"):
                    saved = json.loads((self.project.sessions / "pet-visits" / "session.json").read_text(encoding="utf-8"))
                    expect(Path(saved["workpath"])).to(equal((self.project.root / "src" / "visits").resolve()))

            with context("that a person has chosen as one practice's root"):
                with before.each:
                    self.chosen = self.project.call("ticket.choose_practice_root", ticket="pet-visits", practice="stories", path="src/visits")

                with it("should show the folder as that practice's root, chosen by a person"):
                    expect(self.chosen["practice_roots"]["stories"]).to(equal({"root": "src/visits", "is_chosen": True}))

                with it("should write that practice's files there"):
                    files = self.project.call("ticket.files", ticket="pet-visits", fidelities=["stories-story_map"])["stories-story_map"]["markdown"]
                    expect(files[0]["path"]).to(start_with("src/visits/"))

                with it("should leave every other practice on its default root"):
                    expect(self.chosen["practice_roots"]["bdd"]["is_chosen"]).to(be_false)

                with context("and then a new root for the ticket"):
                    with before.each:
                        self.moved = self.project.call("ticket.choose_root", ticket="pet-visits", path="src")

                    with it("should keep that practice writing to the folder chosen for it"):
                        expect(self.moved["practice_roots"]["stories"]["root"]).to(equal("src/visits"))

                with context("and then back to its default"):
                    with before.each:
                        self.reset = self.project.call("ticket.use_default_practice_root", ticket="pet-visits", practice="stories")

                    with it("should show the practice on its default root again"):
                        expect(self.reset["practice_roots"]["stories"]["is_chosen"]).to(be_false)

            with context("that a person has chosen as the ticket's root, with no practice root chosen"):
                with before.each:
                    self.chosen = self.project.call("ticket.choose_root", ticket="pet-visits", path="src/visits")

                with it("should put each practice's default root under the ticket's root"):
                    expect(self.chosen["practice_roots"]["stories"]["root"]).to(start_with("src/visits"))

            with context("that a person has started a backlog item in a folder"):
                with before.each:
                    self.started = self.project.call("backlog-item.start", backlog_item="Returns and refunds", path="src/billing")

                with it("should open its ticket with that folder as its root"):
                    expect(self.started["root"]).to(equal("src/billing"))

        # (S) Person --> Set Stage WIP Limit
        with it("should give every stage a limit of 3 tickets until a person sets one"):
            expect(self.project.column("Discovery")["wip_limit"]).to(equal(3))

        with context("that sets a stage's limit below the tickets it holds"):
            with before.each:
                (self.project.sessions / "_board.json").unlink(missing_ok=True)
                self.limited = self.project.call("board.set_wip_limit", stage="Discovery", limit=0)

            with it("should show the stage over its limit"):
                discovery = next(column for column in self.limited["columns"] if column["name"] == "Discovery")
                expect(discovery["is_over_limit"]).to(be_true)

        # (S) Board App --> Display Latest Handoff
        with it("should show no handoff for a ticket that has none"):
            expect(self.project.ticket_json("pet-visits")["handoff"]).to(equal(""))

        with context("with handoffs written for the ticket"):
            with before.each:
                session = self.project.sessions / "pet-visits"
                (session / "handoff-20261030T1730.md").write_text("earlier\n", encoding="utf-8")
                (session / "handoff-20261031T0412.md").write_text("latest\n", encoding="utf-8")

            with it("should show the latest handoff"):
                expect(self.project.ticket_json("pet-visits")["handoff"]).to(equal(".sessions/pet-visits/handoff-20261031T0412.md"))

        # (S) Person --> Open Validation Report
        with it("should show no report for a fidelity that has none"):
            expect(self.project.ticket_json("pet-visits")["reports"]).to(equal({}))

        with context("with validation reports saved for a fidelity"):
            with before.each:
                reports = self.project.sessions / "pet-visits" / "validation-reports"
                reports.mkdir()
                (reports / "clean-engineering-modules-20261030T173000.md").write_text("earlier\n", encoding="utf-8")
                (reports / "clean-engineering-modules-20261031T041200.md").write_text("# Graph rule validation\n", encoding="utf-8")
                (reports / "clean-engineering-modules-20261031T041200.json").write_text(json.dumps(CHECKED_GRAPH), encoding="utf-8")

            with it("should show that fidelity's latest report"):
                latest = ".sessions/pet-visits/validation-reports/clean-engineering-modules-20261031T041200.md"
                expect(self.project.ticket_json("pet-visits")["reports"]).to(equal({"clean_engineering-modules": latest}))

            # (S) Person --> Fix Report Violations
            with it("should list each rule the report names with its violations"):
                report = self.project.call("ticket.report", ticket="pet-visits", fidelity="clean_engineering-modules")
                expect(report["rules"][0]["violations"][0]["message"]).to(equal("Name the story with a verb"))

            with it("should give a violation the line it failed on"):
                report = self.project.call("ticket.report", ticket="pet-visits", fidelity="clean_engineering-modules")
                expect(report["rules"][0]["violations"][0]["location"] + ":" + str(report["rules"][0]["violations"][0]["line"])).to(equal("docs/map.md:12"))

            with it("should show no source for a file that is not in the repository"):
                report = self.project.call("ticket.report", ticket="pet-visits", fidelity="clean_engineering-modules")
                expect(report["rules"][0]["violations"][0]["source"]).to(equal([]))

            with context("with the file a violation names in the repository"):
                with before.each:
                    docs = self.project.root / "docs"
                    docs.mkdir()
                    (docs / "map.md").write_text("".join(f"line {number}\n" for number in range(1, 21)), encoding="utf-8")

                with it("should show the source lines around a violation"):
                    report = self.project.call("ticket.report", ticket="pet-visits", fidelity="clean_engineering-modules")
                    source = report["rules"][0]["violations"][0]["source"]
                    expect((source[0], source[-1])).to(equal(({"number": 10, "text": "line 10"}, {"number": 16, "text": "line 16"})))

            # A graph names each file from the session's root, which can be a folder of the project with its own docs/map.md.
            with context("with a session whose root is a folder of the project"):
                with before.each:
                    session = self.project.sessions / "pet-visits" / "session.json"
                    root = self.project.root / "harness" / "pets"
                    session.write_text(json.dumps({**json.loads(session.read_text(encoding="utf-8")), "workpath": str(root)}), encoding="utf-8")
                    (root / "docs").mkdir(parents=True)
                    (root / "docs" / "map.md").write_text("".join(f"pets line {number}\n" for number in range(1, 21)), encoding="utf-8")
                    (self.project.root / "docs").mkdir()
                    (self.project.root / "docs" / "map.md").write_text("".join(f"project line {number}\n" for number in range(1, 21)), encoding="utf-8")

                with it("should name the violation's file from the project's root"):
                    report = self.project.call("ticket.report", ticket="pet-visits", fidelity="clean_engineering-modules")
                    expect(report["rules"][0]["violations"][0]["location"]).to(equal("harness/pets/docs/map.md"))

                with it("should show the source lines of the file in the session's root"):
                    report = self.project.call("ticket.report", ticket="pet-visits", fidelity="clean_engineering-modules")
                    expect(report["rules"][0]["violations"][0]["source"][0]["text"]).to(equal("pets line 10"))

            with it("should return exactly the fields ViolationData names"):
                report = self.project.call("ticket.report", ticket="pet-visits", fidelity="clean_engineering-modules")
                expect(set(report["rules"][0]["violations"][0])).to(equal(set(ViolationData.__annotations__)))

            with it("should return exactly the fields ReportRuleData names"):
                report = self.project.call("ticket.report", ticket="pet-visits", fidelity="clean_engineering-modules")
                expect(set(report["rules"][0])).to(equal(set(ReportRuleData.__annotations__)))

            with it("should count the violations of each rule"):
                report = self.project.call("ticket.report", ticket="pet-visits", fidelity="clean_engineering-modules")
                expect((report["rules"][0]["name"], report["rules"][0]["count"])).to(equal(("domain-nouns-only", 2)))

            with it("should leave out the violations of other practices in the saved graph"):
                report = self.project.call("ticket.report", ticket="pet-visits", fidelity="clean_engineering-modules")
                expect([rule["name"] for rule in report["rules"]]).to(equal(["domain-nouns-only"]))

            with it("should say the report has its saved graph"):
                report = self.project.call("ticket.report", ticket="pet-visits", fidelity="clean_engineering-modules")
                expect(report["has_saved_graph"]).to(equal(True))

        with context("with a validation report saved without its graph"):
            with before.each:
                reports = self.project.sessions / "pet-visits" / "validation-reports"
                reports.mkdir()
                (reports / "clean-engineering-modules-20261030T173000.md").write_text("### verb-noun-format: 1 violation(s)\n", encoding="utf-8")

            with it("should say a report has no saved graph"):
                report = self.project.call("ticket.report", ticket="pet-visits", fidelity="clean_engineering-modules")
                expect((report["has_saved_graph"], report["rules"])).to(equal((False, [])))

            with it("should still return the report's text"):
                report = self.project.call("ticket.report", ticket="pet-visits", fidelity="clean_engineering-modules")
                expect(report["text"]).to(contain("verb-noun-format"))

        with context("with a validation report on a rule the practice describes"):
            with before.each:
                self.project.report("pet-visits", "stories-story-map-20261031T041200", STORY_MAP_GRAPH)

            with it("should show the text of each rule under its name"):
                report = self.project.call("ticket.report", ticket="pet-visits", fidelity="stories-story_map")
                expect(report["rules"][0]["description"]).to(contain("verb"))

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
                        report = self.project.call("ticket.report", ticket="pet-visits", fidelity="stories-story_map")
                        expect(report["path"]).to(equal(".sessions/pet-visits/validation-reports/stories-story-map-20261031T041200.md"))

                with it("should list each rule the judgment fails after the graph's rules, once each"):
                    report = self.project.call("ticket.report", ticket="pet-visits", fidelity="stories-story_map")
                    expect([rule["name"] for rule in report["rules"]]).to(equal(["verb-noun-format", "do-not-invent-requirements", "story-name-captures-system-mechanic"]))

                with it("should count each finding of a judged rule"):
                    report = self.project.call("ticket.report", ticket="pet-visits", fidelity="stories-story_map")
                    expect(report["rules"][1]["count"]).to(equal(2))

                with it("should give a judged finding the judged file and its line"):
                    finding = self.project.call("ticket.report", ticket="pet-visits", fidelity="stories-story_map")["rules"][1]["violations"][0]
                    expect((finding["location"], finding["line"])).to(equal(("docs/map.md", 7)))

                with it("should show the source lines around a judged finding"):
                    finding = self.project.call("ticket.report", ticket="pet-visits", fidelity="stories-story_map")["rules"][1]["violations"][0]
                    expect(finding["source"][0]["text"]).to(equal("line 5"))

                with it("should list a rule an older report warns on as failing, since a warning is a Fail"):
                    finding = self.project.call("ticket.report", ticket="pet-visits", fidelity="stories-story_map")["rules"][2]["violations"][0]
                    expect(finding["message"]).to(equal("`Do Stuff` does not say what it does."))

        # A saved graph keeps the hits of a scanner deleted after it was saved.
        with context("with a validation report on a rule no scanner checks any more"):
            with before.each:
                deleted = {"practices": {"stories": {"nodes": [], "rules": [["evidence-distinguishes-observed-inferred-and-intended", "node-1", "Label the evidence"]]}}}
                self.project.report("pet-visits", "stories-story-map-20261031T041200", deleted)

            with it("should leave that rule's hits out of the report"):
                report = self.project.call("ticket.report", ticket="pet-visits", fidelity="stories-story_map")
                expect(report["rules"]).to(equal([]))

        # (E) Tickets
        # (S) Person --> Open Ticket Session
        with context("that opens a new ticket"):
            with before.each:
                self.opened = self.project.call("ticket.new", title="Loyalty points", scope="feature")

            with it("should return the new ticket in Discovery"):
                expect((self.opened["name"], self.opened["column"])).to(equal(("loyalty-points", "Discovery")))

            with it("should leave the current session as it is"):
                expect(self.project.call("board.show")["active"]).to(equal(None))

        with context("that opens a ticket on a folder in the repository"):
            with before.each:
                self.project.call("ticket.new", title="Pet records", scope="feature", path="harness/pets")

            with it("should save that folder as the session's workpath"):
                fields = json.loads((self.project.sessions / "pet-records" / "session.json").read_text(encoding="utf-8"))
                expect(fields["workpath"]).to(equal(str((self.project.root / "harness" / "pets").resolve())))

        with context("that opens a ticket with no folder"):
            with before.each:
                self.project.call("ticket.new", title="Pet records", scope="feature")

            with it("should leave the session working on the repository"):
                fields = json.loads((self.project.sessions / "pet-records" / "session.json").read_text(encoding="utf-8"))
                expect(fields["workpath"]).to(equal(str(self.project.root.resolve())))

        # (S) Person --> Split Ticket Into Child Tickets
        with context("that opens a ticket split from another"):
            with before.each:
                self.opened = self.project.call("ticket.new", title="Book a visit", scope="story", parent="pet-visits")

            with it("should name the ticket it was split from"):
                expect(self.opened["parent"]).to(equal("pet-visits"))

        # (S) Person --> Add Backlog Item
        with context("that adds a backlog item"):
            with before.each:
                self.added = self.project.call("backlog-item.add", title="Gift cards", text="Sell gift cards.")

            with it("should show the item in the Backlog with its text"):
                expect((self.added["title"], self.added["text"])).to(equal(("Gift cards", "Sell gift cards.")))

            with it("should write the title and text to one markdown file"):
                file = self.project.sessions / "_backlog" / "gift-cards.md"
                expect(file.read_text(encoding="utf-8")).to(equal("# Gift cards\n\nSell gift cards.\n"))

        # (S) Person --> Add Backlog Item, Start Backlog Item
        with context("that starts a backlog item"):
            with before.each:
                self.started = self.project.call("backlog-item.start", backlog_item="Returns and refunds", scope="feature")

            with it("should return the new ticket in Discovery"):
                expect((self.started["name"], self.started["column"])).to(equal(("returns-and-refunds", "Discovery")))

            with it("should take the item off the Backlog"):
                expect(self.project.column("Backlog")["items"]).to(equal([]))

        # (S) Person --> Close Active Session
        with context("that closes a ticket"):
            with before.each:
                self.project.call("ticket.close", ticket="pet-visits")

            with it("should show the ticket in Complete"):
                expect(self.project.tickets_in("Complete")).to(contain("pet-visits"))

        with context("that closes the active ticket"):
            with before.each:
                Session.switch("pet-visits", repo_path=self.project.root)
                self.project.call("ticket.close", ticket="pet-visits")

            with it("should leave no ticket active"):
                expect(self.project.call("board.show")["active"]).to(equal(None))

        # (S) Person --> Archive Ticket
        with context("that archives a ticket"):
            with before.each:
                self.project.call("ticket.archive", ticket="pet-visits")

            with it("should leave the ticket off the board"):
                expect(json.dumps(self.project.call("board.show"))).not_to(contain("pet-visits"))

        # (S) Person --> Drag Ticket To A Stage
        with context("that drags a ticket into a later stage's Done"):
            with before.each:
                self.moved = self.project.call("ticket.move_to", ticket="pet-visits", stage="Implementation", done=True)

            with it("should show the ticket in that stage's Done"):
                expect((self.moved["column"], self.moved["is_done"])).to(equal(("Implementation", True)))

        # (S) Person --> Move Ticket, a ticket that is done in Discovery
        with context("that moves a ticket to the next column"):
            with before.each:
                self.moved = self.project.call("ticket.move_next", ticket="pet-visits")

            with it("should show the ticket in the next stage"):
                expect(self.moved["column"]).to(equal("Specification"))

            with it("should show the ticket in progress there"):
                expect(self.moved["is_done"]).to(be_false)

            # (S) Person --> Mark Ticket Done In Stage
            with context("with that stage's work not done"):
                with before.each:
                    self.moved = self.project.call("ticket.move_next", ticket="pet-visits")

                with it("should show the ticket in that stage's Done all the same"):
                    expect((self.moved["column"], self.moved["is_done"])).to(equal(("Specification", True)))

                with context("and on to the column after"):
                    with before.each:
                        self.project.call("ticket.move_next", ticket="pet-visits")
                        self.project.call("ticket.move_next", ticket="pet-visits")
                        self.moved = self.project.call("ticket.move_next", ticket="pet-visits")

                    with context("and past Implementation"):
                        with before.each:
                            self.moved = self.project.call("ticket.move_next", ticket="pet-visits")

                        with it("should close the ticket"):
                            expect(self.moved["column"]).to(equal("Complete"))

                        with it("should leave a ticket in Complete where it is on another move forward"):
                            expect(self.project.call("ticket.move_next", ticket="pet-visits")["column"]).to(equal("Complete"))

                        with context("and back again"):
                            with before.each:
                                self.moved = self.project.call("ticket.move_previous", ticket="pet-visits")

                            with it("should reopen the ticket in Implementation"):
                                expect(self.moved["column"]).to(equal("Implementation"))

                with context("and back from Done"):
                    with before.each:
                        self.moved = self.project.call("ticket.move_previous", ticket="pet-visits")

                    with it("should show the ticket in progress in that stage"):
                        expect((self.moved["column"], self.moved["is_done"])).to(equal(("Specification", False)))

            with context("and back to the previous column"):
                with before.each:
                    self.moved = self.project.call("ticket.move_previous", ticket="pet-visits")

                with it("should show the ticket in Discovery"):
                    expect(self.moved["column"]).to(equal("Discovery"))

                with it("should show the ticket in Discovery's Done"):
                    expect(self.moved["is_done"]).to(be_true)

        # (S) Person --> Choose Ticket Practices
        with context("that turns a practice off for a ticket"):
            with before.each:
                self.chosen = self.project.call("ticket.enable_practice", ticket="pet-visits", practice="ux", is_enabled=False)

            with it("should show the practice off for that ticket"):
                expect(self.chosen["practices"]["ux"]).to(be_false)

            with it("should save the choice to the ticket's session.json"):
                fields = json.loads((self.project.sessions / "pet-visits" / "session.json").read_text(encoding="utf-8"))
                expect(fields["practices"]).to(equal({"ux": {"enabled": False}}))

        # (S) Person --> Choose Action And Formats
        with it("should give each fidelity its default format"):
            expect(self.project.column("Discovery")["default_formats"]["stories-story_map"]).to(equal("markdown"))

        # (S) Board App --> Display Fidelity Progress
        with it("should show each fidelity's Generate, Validate, and Review"):
            actions = self.project.ticket_json("pet-visits")["actions"]["stories-story_map"]
            expect(actions).to(equal({"generate": "done", "validate": "done", "review": "done"}))

        # (S) Person --> Open Help
        with context("that opens help on a fidelity"):
            with before.each:
                self.help = self.project.call("board.help", practice="stories", fidelity="story_map")

            with it("should show the fidelity's rules"):
                expect([rule["slug"] for rule in self.help["rules"]]).to(contain("verb-noun-format"))

            with it("should name the stage a fidelity belongs to"):
                expect(self.help["stage"]).to(equal("Discovery"))

            with it("should link to the fidelity's page on the forge"):
                expect(self.help["href"]).to(equal("https://forge.abdworks.net/abd-context-driven-delivery/fidelities/stories-story_map.html"))

        with context("that opens help on a practice"):
            with before.each:
                self.help = self.project.call("board.help", practice="stories")

            with it("should show the practice's shared rules"):
                expect([rule["slug"] for rule in self.help["rules"]]).to(contain("do-not-invent-requirements"))

            with it("should name no fidelity on a practice's help"):
                expect((self.help["fidelity"], self.help["stage"])).to(equal(("", "")))

        # (E) Review
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
                files = self.project.call("ticket.files", ticket="pet-visits", fidelities=["bdd-behavior"])["bdd-behavior"]["python"]
                expect(files).to(equal([{"path": (self.outside / "src" / "visits_spec.py").as_posix(), "exists": True}]))

            # (S) Person --> View Fidelity Files, a path that names its module
            with it("should list the files a named part of the path finds there, in folders at any depth"):
                model = self.outside / "src" / "visits" / ".context" / "visits-model.md"
                model.parent.mkdir(parents=True)
                model.write_text("# Visits\n", encoding="utf-8")
                files = self.project.call("ticket.files", ticket="pet-visits", fidelities=["clean_engineering-model"])["clean_engineering-model"]["markdown"]
                expect(files).to(equal([{"path": model.as_posix(), "exists": True}]))

        with context("with a fidelity's markdown generated"):
            with before.each:
                docs = self.project.root / "docs" / ".context"
                docs.mkdir(parents=True)
                (docs / "story-map.md").write_text("# Story map\n", encoding="utf-8")
                fields = {"outputs": {"stories": {"root": "docs", "story_map": {"markdown": "story-map.md"}}}}
                (self.project.sessions / "pet-visits" / "session.json").write_text(json.dumps({"name": "pet-visits", **fields}), encoding="utf-8")

            with it("should list the file with whether it exists"):
                files = self.project.call("ticket.files", ticket="pet-visits", fidelities=["stories-story_map"])["stories-story_map"]["markdown"]
                expect(files).to(equal([{"path": "docs/.context/story-map.md", "exists": True}]))

            with it("should list only the fidelities asked for"):
                files = self.project.call("ticket.files", ticket="pet-visits", fidelities=["stories-story_map"])
                expect(list(files)).to(equal(["stories-story_map"]))

            # (S) Person --> Generate Fidelity Output
            with it("should render the earlier fidelity into the new format first"):
                commands = self.project.call("ticket.generate_commands", ticket="pet-visits", fidelities=["stories-scenarios"], formats=["drawio"])
                expect(commands[0]).to(equal("/actions-render stories-story-map format=drawio source=markdown session=.sessions/pet-visits/session.json"))

            # A command runs in whichever chat it is sent to, so it names the ticket's session for the agent to work in.
            with it("should name the ticket's session in the generate command"):
                commands = self.project.call("ticket.generate_commands", ticket="pet-visits", fidelities=["stories-scenarios"], formats=["drawio"])
                expect(commands[-1]).to(equal("/actions-generate stories-scenarios format=drawio session=.sessions/pet-visits/session.json"))

            with it("should give the board the ticket's session.json"):
                expect(self.project.ticket_json("pet-visits")["session_file"]).to(equal(".sessions/pet-visits/session.json"))

            # (S) Person --> View Fidelity Files
            with it("should return the file's text"):
                opened = self.project.call("ticket.read_file", ticket="pet-visits", path="docs/.context/story-map.md")
                expect(opened["text"]).to(equal("# Story map\n"))

        # (S) Person --> List Ticket Files, the session folder
        with context("with files in its session folder"):
            with before.each:
                (self.project.sessions / "pet-visits" / "notes").mkdir()
                (self.project.sessions / "pet-visits" / "notes" / "idea.md").write_text("# Idea\n", encoding="utf-8")

            with it("should list every file in the session folder"):
                files = self.project.call("ticket.session_files", ticket="pet-visits")
                expect(files).to(contain({"path": ".sessions/pet-visits/notes/idea.md", "exists": True}))

            with it("should list the files from the project"):
                files = self.project.call("ticket.session_files", ticket="pet-visits")
                expect(all(entry["path"].startswith(".sessions/pet-visits/") for entry in files)).to(be_true)

    # (S) Person --> Move Ticket, a ticket just started in Discovery
    with context("with a ticket in Discovery"):
        with before.each:
            self.project.ticket("sign-up", title="Sign up")

        with context("that moves the ticket back out of Discovery"):
            with before.each:
                self.moved = self.project.call("ticket.move_previous", ticket="sign-up")

            with it("should show an item in the Backlog with the ticket's title"):
                expect(self.moved["title"]).to(equal("Sign up"))

            with it("should give the item's path from the project"):
                expect(self.moved["path"]).to(start_with(".sessions/"))

            with it("should take the ticket off the board's stages"):
                expect(self.project.tickets_in("Discovery")).to(equal([]))

            # (S) Person --> Add Backlog Item, Start Backlog Item
            with context("that starts the item again"):
                with before.each:
                    self.started = self.project.call("backlog-item.start", backlog_item="Sign up")

                with it("should bring the ticket back with its work"):
                    expect((self.started["name"], (self.project.sessions / "sign-up" / "session.json").is_file())).to(equal(("sign-up", True)))

        # (S) Person --> Send Next Fidelity Action
        with it("should name generate as the next action"):
            expect(self.project.ticket_json("sign-up")["next_action"]).to(equal("generate"))

        with it("should allow only Generate before anything is generated"):
            expect(self.project.ticket_json("sign-up")["allowed_actions"]["stories-story_map"]).to(equal(["generate"]))

    # (S) Person --> Review Fidelity
    with context("with a ticket whose story map has passed validate"):
        with before.each:
            self.project.ticket(
                "sign-up",
                "2026-10-31T01:00:00Z generate /work stories story_map markdown stories no-chat",
                "2026-10-31T01:00:01Z validate Stories story_map no-chat",
                title="Sign up",
            )

        with it("should name review as the next action"):
            expect(self.project.ticket_json("sign-up")["next_action"]).to(equal("review"))

        # The validating agent adds its judgment to the report after validate has logged its graph's result.
        with context("with a report whose judgment fails rules the graph passed"):
            with before.each:
                self.project.report("sign-up", "stories-story-map-20261031T041200")
                (self.project.sessions / "sign-up" / "validation-reports" / "stories-story-map-20261031T041200.md").write_text(JUDGED_REPORT, encoding="utf-8")

            with it("should name satisfy as the next action"):
                expect(self.project.ticket_json("sign-up")["next_action"]).to(equal("satisfy"))

            with it("should count each finding of the judgment"):
                expect(self.project.ticket_json("sign-up")["violation_counts"]).to(equal({"stories-story_map": 4}))

        with context("that a person has finished reviewing"):
            with before.each:
                self.reviewed = self.project.call("ticket.finish_review", ticket="sign-up", fidelities=["stories-story_map"])

            with it("should show the fidelity's review done"):
                expect(self.reviewed["actions"]["stories-story_map"]["review"]).to(equal("done"))

            with it("should write the review to the session log"):
                log = (self.project.sessions / "sign-up" / "session.log").read_text(encoding="utf-8")
                expect(log.splitlines()[-1]).to(match(r" review Stories story_map$"))

        with context("that a person names a fidelity the ticket does not have"):
            with it("should refuse it, naming the fidelity"):
                expect(lambda: self.project.call("ticket.finish_review", ticket="sign-up", fidelities=["stories-nothing"])).to(raise_error(FidelityNotFoundError))

            with context("among fidelities it does have"):
                with before.each:
                    try:
                        self.project.call("ticket.finish_review", ticket="sign-up", fidelities=["stories-story_map", "stories-nothing"])
                    except FidelityNotFoundError:
                        pass

                with it("should write no review for the others named with it"):
                    expect(self.project.ticket_json("sign-up")["actions"]["stories-story_map"]["review"]).to(equal("to_do"))

    # (S) Person --> Send Next Fidelity Action
    with context("with a ticket whose next fidelity has violations"):
        with before.each:
            self.project.ticket(
                "sign-up",
                "2026-10-31T01:00:00Z generate /work stories story_map markdown stories no-chat",
                "2026-10-31T01:00:01Z validate Stories story_map graph-rule verb-noun-format map.md:12 no-chat",
                title="Sign up",
            )

        with it("should name satisfy as the next action"):
            expect(self.project.ticket_json("sign-up")["next_action"]).to(equal("satisfy"))

        with it("should allow Validate and Review again on the same output"):
            expect(self.project.ticket_json("sign-up")["allowed_actions"]["stories-story_map"]).to(equal(["generate", "validate", "review"]))

        # (S) Person --> Open Validation Report
        with context("with that fidelity's report saved with its graph"):
            with before.each:
                self.project.report("sign-up", "stories-story-map-20261031T041200", STORY_MAP_GRAPH)

            with it("should count the violations of the fidelity on its ticket"):
                expect(self.project.ticket_json("sign-up")["violation_counts"]).to(equal({"stories-story_map": 2}))

        with context("with that fidelity's report saved without its graph"):
            with before.each:
                self.project.report("sign-up", "stories-story-map-20261031T041200")

            with it("should leave a fidelity with no saved graph uncounted"):
                expect(self.project.ticket_json("sign-up")["violation_counts"]).to(equal({}))

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
            expect([rule["fidelity"] for rule in rules]).to(equal(["stories-story_map", "clean_engineering-modules"]))

        with it("should name the fidelity a rule was broken on"):
            report = self.project.call("ticket.report", ticket="sign-up", fidelity="stories-story_map")
            expect(report["rules"][0]["fidelity"]).to(equal("stories-story_map"))

        with it("should give the folder of the reports for every fidelity"):
            expect(self.project.call("ticket.violations", ticket="sign-up")["path"]).to(equal(".sessions/sign-up/validation-reports"))

    # A ticket's card sits in one stage, so its violations are those of that stage's practices.
    with context("with violations left on a fidelity of a later stage"):
        with before.each:
            self.project.ticket(
                "sign-up",
                "2026-10-31T01:00:00Z validate Stories story_map graph-rule verb-noun-format map.md:12 no-chat",
                "2026-10-31T01:00:01Z validate Stories scenarios graph-rule plain-english-gwt-steps map.md:12 no-chat",
                title="Sign up",
            )
            self.project.report("sign-up", "stories-story-map-20261031T041200", STORY_MAP_GRAPH)
            reports = self.project.sessions / "sign-up" / "validation-reports"
            (reports / "stories-scenarios-20261031T050000.md").write_text("# Graph rule validation\n", encoding="utf-8")
            (reports / "stories-scenarios-20261031T050000.json").write_text(json.dumps(WHOLE_STORIES_GRAPH), encoding="utf-8")

        with it("should list only the rules of the fidelities in the ticket's stage"):
            rules = self.project.call("ticket.violations", ticket="sign-up")["rules"]
            expect({rule["fidelity"] for rule in rules}).to(equal({"stories-story_map"}))

    with context("with violations two fidelities of one practice share in their saved graphs"):
        with before.each:
            self.project.ticket(
                "sign-up",
                "2026-10-31T01:00:00Z validate Stories story_map graph-rule verb-noun-format map.md:12 no-chat",
                "2026-10-31T01:00:01Z validate Stories scenarios graph-rule verb-noun-format map.md:12 no-chat",
                title="Sign up",
            )
            self.project.report("sign-up", "stories-story-map-20261031T041200", STORY_MAP_GRAPH)
            reports = self.project.sessions / "sign-up" / "validation-reports"
            (reports / "stories-scenarios-20261031T041200.md").write_text("# Graph rule validation\n", encoding="utf-8")
            (reports / "stories-scenarios-20261031T041200.json").write_text(json.dumps(STORY_MAP_GRAPH), encoding="utf-8")

        with it("should list a rule two fidelities share once"):
            rules = self.project.call("ticket.violations", ticket="sign-up")["rules"]
            expect([rule["fidelity"] for rule in rules]).to(equal(["stories-story_map"]))

    # A saved graph holds the hits of every rule of its practice, but a report answers for its own fidelity.
    with context("with a scenarios report whose saved graph holds every stories rule's hits"):
        with before.each:
            self.project.ticket(
                "sign-up",
                "2026-10-31T01:00:01Z validate Stories scenarios graph-rule verb-noun-format map.md:12 no-chat",
                title="Sign up",
            )
            self.project.report("sign-up", "stories-scenarios-20261031T041200", WHOLE_STORIES_GRAPH)

        with it("should list the scenarios rules and the story map rules"):
            report = self.project.call("ticket.report", ticket="sign-up", fidelity="stories-scenarios")
            expect([rule["name"] for rule in report["rules"]]).to(equal(["verb-noun-format", "plain-english-gwt-steps"]))

        with it("should count the same rules on the ticket"):
            expect(self.project.ticket_json("sign-up")["violation_counts"]).to(equal({"stories-scenarios": 2}))

        with context("with a story map report newer than the scenarios report"):
            with before.each:
                reports = self.project.sessions / "sign-up" / "validation-reports"
                (reports / "stories-story-map-20261031T050000.md").write_text("# Graph rule validation\n", encoding="utf-8")

            with it("should leave the story map rules to the story map report"):
                report = self.project.call("ticket.report", ticket="sign-up", fidelity="stories-scenarios")
                expect([rule["name"] for rule in report["rules"]]).to(equal(["plain-english-gwt-steps"]))

            with it("should count only the rules the scenarios report answers for"):
                expect(self.project.ticket_json("sign-up")["violation_counts"]).to(equal({"stories-scenarios": 1}))

    # (S) Person --> Activate Ticket
    with context("with a git repository and two tickets"):
        with before.each:
            subprocess.run(["git", "init", "-q", "-b", "main"], cwd=self.project.root, check=False)
            (self.project.root / ".git" / "HEAD").is_file()
            subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "start"], cwd=self.project.root, check=True)
            self.project.ticket("pet-visits", title="Pet visits")
            self.project.ticket("sign-up", title="Sign up")

        with context("that activates a ticket"):
            with before.each:
                self.project.call("ticket.activate", ticket="sign-up")

            with it("should make the chosen ticket the current session"):
                expect(self.project.call("board.show")["active"]).to(equal("sign-up"))

        with context("that activates a ticket with a new branch"):
            with before.each:
                self.project.call("ticket.activate", ticket="sign-up", opening=["branch"])

            with it("should create the ticket's branch when a ticket that has none is activated"):
                expect(self.project.call("ticket.workspace", ticket="sign-up")["has_branch"]).to(be_true)

        with it("should say a ticket has no branch yet"):
            expect(self.project.call("ticket.workspace", ticket="sign-up")["has_branch"]).to(be_false)

        with context("with the active ticket on no branch of its own"):
            with before.each:
                Session.switch("pet-visits", repo_path=self.project.root)
                (self.project.root / "work.txt").write_text("work\n", encoding="utf-8")

            with it("should say the ticket being left has no branch yet"):
                expect(self.project.call("ticket.workspace", ticket="sign-up")["leaving_has_branch"]).to(be_false)

            with it("should commit nothing on a ticket that has no branch"):
                self.project.call("ticket.activate", ticket="sign-up", leaving=["commit", "push", "merge"])
                count = subprocess.run(["git", "rev-list", "--count", "HEAD"], cwd=self.project.root, check=True, capture_output=True, text=True)
                expect(count.stdout.strip()).to(equal("1"))

            with it("should leave the branch checked out as it was"):
                self.project.call("ticket.close", ticket="pet-visits", leaving=["commit", "merge"])
                branch = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=self.project.root, check=True, capture_output=True, text=True)
                expect(branch.stdout.strip()).to(equal("main"))

        with context("with the active ticket on its own branch"):
            with before.each:
                subprocess.run(["git", "checkout", "-q", "-b", "pet-visits"], cwd=self.project.root, check=True)
                subprocess.run(["git", "config", "user.name", "t"], cwd=self.project.root, check=True)
                subprocess.run(["git", "config", "user.email", "t@t"], cwd=self.project.root, check=True)
                Session.switch("pet-visits", repo_path=self.project.root)
                (self.project.root / "work.txt").write_text("work\n", encoding="utf-8")

            with it("should say the ticket being left is on its branch"):
                expect(self.project.call("ticket.workspace", ticket="sign-up")["leaving_has_branch"]).to(be_true)

            with it("should commit the branch the ticket being left is on"):
                self.project.call("ticket.activate", ticket="sign-up", leaving=["commit"])
                count = subprocess.run(["git", "rev-list", "--count", "pet-visits"], cwd=self.project.root, check=True, capture_output=True, text=True)
                expect(count.stdout.strip()).to(equal("2"))

        with context("with specs in the repository and one changed on the ticket's branch"):
            with before.each:
                (self.project.root / "src").mkdir()
                (self.project.root / "src" / "theirs_spec.py").write_text("", encoding="utf-8")
                subprocess.run(["git", "add", "src"], cwd=self.project.root, check=True)
                subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "spec"], cwd=self.project.root, check=True)
                subprocess.run(["git", "checkout", "-q", "-b", "pet-visits"], cwd=self.project.root, check=True)
                (self.project.root / "src" / "mine_spec.py").write_text("", encoding="utf-8")

            with it("should list only the files the ticket's branch changed"):
                files = self.project.call("ticket.files", ticket="pet-visits", fidelities=["bdd-behavior"])["bdd-behavior"]["python"]
                expect(files).to(equal([{"path": "src/mine_spec.py", "exists": True}]))

        with context("with the active ticket's branch not checked out"):
            with before.each:
                subprocess.run(["git", "branch", "pet-visits"], cwd=self.project.root, check=True)
                Session.switch("pet-visits", repo_path=self.project.root)
                (self.project.root / "work.txt").write_text("work\n", encoding="utf-8")

            with it("should commit nothing on a branch that is not checked out"):
                self.project.call("ticket.activate", ticket="sign-up", leaving=["commit"])
                count = subprocess.run(["git", "rev-list", "--count", "HEAD"], cwd=self.project.root, check=True, capture_output=True, text=True)
                expect(count.stdout.strip()).to(equal("1"))

    with context("with a session open in the project"):
        with before.each:
            Session.new("pet-visits", self.project.root, self.project.root)
            self.log = self.project.sessions / "pet-visits" / "session.log"
            self.project.call("board.show")

        with it("should leave the board read out of the session log"):
            expect(self.log.read_text(encoding="utf-8")).not_to(contain("board.show"))

    with context("that are published through the cdd server"):
        with it("should name each tool after its object"):
            names = set(self.project.server.tools)
            expect(names).to(equal({
                "board.show", "board.set_wip_limit", "board.help", "board.folders",
                "ticket.new", "ticket.move_next", "ticket.move_previous", "ticket.move_to", "ticket.close", "ticket.archive", "ticket.activate", "ticket.finish_review", "ticket.choose_root", "ticket.choose_practice_root", "ticket.use_default_practice_root",
                "ticket.workspace", "ticket.enable_practice", "ticket.files", "ticket.session_files", "ticket.read_file", "ticket.report", "ticket.violations", "ticket.generate_commands",
                "backlog-item.add", "backlog-item.start",
            }))

        with it("should take the ticket's name on every ticket tool that acts on one"):
            schema = self.project.server.tools["ticket.move_next"].callable
            expect(list(__import__("inspect").signature(schema).parameters)).to(equal(["ticket"]))

    # The shapes in data.py are the only agreement between the two languages: the language adapter is written from them.
    with context("whose JSON is compared with the shapes in data.py"):
        with before.each:
            self.project.ticket("pet-visits", title="Pet visits")
            self.project.backlog_item("returns.md", "Returns and refunds")

        with it("should return exactly the fields TicketData names"):
            expect(set(self.project.ticket_json("pet-visits"))).to(equal(set(TicketData.__annotations__)))

        with it("should return exactly the fields WorkspaceData names"):
            subprocess.run(["git", "init", "-q", "-b", "main"], cwd=self.project.root, check=False)
            workspace = self.project.call("ticket.workspace", ticket="pet-visits")
            expect(set(workspace)).to(equal(set(WorkspaceData.__annotations__)))

        with it("should return exactly the fields BacklogItemData names"):
            expect(set(self.project.column("Backlog")["items"][0])).to(equal(set(BacklogItemData.__annotations__)))

        with it("should return only the fields ColumnData names on a stage"):
            expect(set(self.project.column("Discovery")) - set(ColumnData.__annotations__)).to(equal(set()))

    with context("whose signatures are compared with the board app's shared behaviors"):
        with it("should state every shared behavior here under the same sentence"):
            spec = Path(__file__).read_text(encoding="utf-8")
            signatures = set(re.findall(r'with it\("(should [^"]+)"\)', spec))
            shared_files = (Path(__file__).parent / "app" / "tests" / "kanban").rglob("*.spec.shared.ts")
            shared = {sentence for path in shared_files for sentence in re.findall(r"\bit\('(should .+?)',", path.read_text(encoding="utf-8"))}
            only_on_the_page = {"should leave a stage holding fewer tickets than its limit within it"}
            expect(sorted(shared - signatures - only_on_the_page)).to(equal([]))
