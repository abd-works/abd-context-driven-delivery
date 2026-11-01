"""The session board as tools an agent calls (cdd MCP), through the MCP server, organised by story.

Each signature here has a test of the same name in `pane/hooks/register.test.tsx`."""
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

from expects import be_false, be_true, contain, equal, expect, have_key, match
from mamba import after, before, context, description, it

from harness.installation.installer import Installer

Installer(repo=Path(__file__).resolve().parents[2]).ensure_import_path()

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
            "rules": [["verb-noun-format", "node-1", "Name the story with a verb"], ["verb-noun-format", "node-1", "Name the epic with a verb"]],
        },
        "stories": {
            "nodes": [["node-2", "", "Story", "stories", "docs/other.md", 3, 3]],
            "rules": [["actor-named-in-step", "node-2", "Name the actor"]],
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
        Session._current = None
        self.project = ProjectTools()

    with after.each:
        Session._current = None
        os.environ.pop("CDD_PROJECT", None)

    # (E) Display Board And Details For Repo
    with context("with a project whose sessions folder holds a ticket and a backlog item"):
        with before.each:
            self.project.ticket("pet-visits", *DISCOVERY_DONE, title="Pet visits")
            self.project.backlog_item("returns.md", "Returns and refunds")

        # (S) Board Pane --> Display Board
        with it("should return every column of the board"):
            columns = [column["name"] for column in self.project.call("board.show")["columns"]]
            expect(columns).to(equal(["Backlog", "Discovery", "Specification", "Implementation", "Complete"]))

        with it("should name the project the board belongs to"):
            expect(self.project.call("board.show")["project"]).to(equal(self.project.root.name))

        # (S) Board Pane --> Display Backlog Items As Tickets
        with it("should say when a backlog item last changed"):
            expect(self.project.column("Backlog")["items"][0]["last_activity"]).to(match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"))

        with it("should give a backlog item its text"):
            expect(self.project.column("Backlog")["items"][0]["text"]).to(equal("An idea."))

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

        # (S) Board Pane --> Display Latest Handoff
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
                expect(report["rules"][0]["violations"][0]).to(equal({"location": "docs/map.md", "message": "Name the story with a verb"}))

            with it("should count the violations of each rule"):
                report = self.project.call("ticket.report", ticket="pet-visits", fidelity="clean_engineering-modules")
                expect((report["rules"][0]["name"], report["rules"][0]["count"])).to(equal(("verb-noun-format", 2)))

            with it("should leave out the violations of other practices in the saved graph"):
                report = self.project.call("ticket.report", ticket="pet-visits", fidelity="clean_engineering-modules")
                expect([rule["name"] for rule in report["rules"]]).to(equal(["verb-noun-format"]))

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

        # (S) Board Pane --> Display Fidelity Progress
        with it("should show each fidelity's Generate, Validate, and Review"):
            actions = self.project.ticket_json("pet-visits")["actions"]["stories-story_map"]
            expect(actions).to(equal({"generate": "done", "validate": "done", "review": "done"}))

        # (S) Person --> Open Help
        with context("that opens help on a fidelity"):
            with before.each:
                self.help = self.project.call("board.help", practice="stories", fidelity="story_map")

            with it("should show the fidelity's rules"):
                expect([rule["slug"] for rule in self.help["rules"]]).to(contain("verb-noun-format"))

            with it("should link to the fidelity's page on the forge"):
                expect(self.help["href"]).to(equal("https://forge.abdworks.net/abd-context-driven-delivery/fidelities/stories-story_map.html"))

        with context("that opens help on a practice"):
            with before.each:
                self.help = self.project.call("board.help", practice="stories")

            with it("should show the practice's shared rules"):
                expect([rule["slug"] for rule in self.help["rules"]]).to(contain("do-not-invent-requirements"))

        # (E) Review
        # (S) Person --> List Ticket Files
        with context("with a fidelity's markdown generated"):
            with before.each:
                docs = self.project.root / "docs"
                docs.mkdir()
                (docs / "story-map.md").write_text("# Story map\n", encoding="utf-8")
                fields = {"outputs": {"stories": {"root": "docs", "story_map": {"markdown": "story-map.md"}}}}
                (self.project.sessions / "pet-visits" / "session.json").write_text(json.dumps({"name": "pet-visits", **fields}), encoding="utf-8")

            with it("should list the file with whether it exists"):
                files = self.project.call("ticket.files", ticket="pet-visits")["stories-story_map"]["markdown"]
                expect(files).to(equal([{"path": "docs/story-map.md", "exists": True}]))

            # (S) Person --> Generate Fidelity Output
            with it("should render the earlier fidelity into the new format first"):
                commands = self.project.call("ticket.generate_commands", ticket="pet-visits", fidelities=["stories-scenarios"], formats=["drawio"])
                expect(commands[0]).to(equal("/actions-render stories-story-map format=drawio source=markdown"))

            # (S) Person --> View Files
            with it("should return the file's text"):
                opened = self.project.call("ticket.read_file", ticket="pet-visits", path="docs/story-map.md")
                expect(opened["text"]).to(equal("# Story map\n"))

    # (S) Person --> Move Ticket, a ticket just started in Discovery
    with context("with a ticket in Discovery"):
        with before.each:
            self.project.ticket("sign-up", title="Sign up")

        with context("that moves the ticket back out of Discovery"):
            with before.each:
                self.moved = self.project.call("ticket.move_previous", ticket="sign-up")

            with it("should show an item in the Backlog with the ticket's title"):
                expect(self.moved["title"]).to(equal("Sign up"))

            with it("should take the ticket off the board's stages"):
                expect(self.project.tickets_in("Discovery")).to(equal([]))

            # (S) Person --> Add Backlog Item, Start Backlog Item
            with context("that starts the item again"):
                with before.each:
                    self.started = self.project.call("backlog-item.start", backlog_item="Sign up")

                with it("should bring the ticket back with its work"):
                    expect((self.started["name"], (self.project.sessions / "sign-up" / "session.json").is_file())).to(equal(("sign-up", True)))

        # (S) Person --> Run Next Step
        with it("should name generate as the next action"):
            expect(self.project.ticket_json("sign-up")["next_action"]).to(equal("generate"))

        with it("should allow only Generate before anything is generated"):
            expect(self.project.ticket_json("sign-up")["allowed_actions"]["stories-story_map"]).to(equal(["generate"]))

    # (S) Person --> Run Next Step
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

        with it("should not allow Review until Validate is clean"):
            expect(self.project.ticket_json("sign-up")["allowed_actions"]["stories-story_map"]).not_to(contain("review"))

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
                "board.show", "board.set_wip_limit", "board.help",
                "ticket.new", "ticket.move_next", "ticket.move_previous", "ticket.close", "ticket.archive", "ticket.activate",
                "ticket.workspace", "ticket.enable_practice", "ticket.files", "ticket.read_file", "ticket.report", "ticket.generate_commands",
                "backlog-item.add", "backlog-item.start",
            }))

        with it("should take the ticket's name on every ticket tool that acts on one"):
            schema = self.project.server.tools["ticket.move_next"].callable
            expect(list(__import__("inspect").signature(schema).parameters)).to(equal(["ticket"]))

    # The contract in pane/types/index.d.ts is the only agreement between the two languages.
    with context("whose JSON is compared with the mod's contract"):
        with before.each:
            self.project.ticket("pet-visits", title="Pet visits")
            self.project.backlog_item("returns.md", "Returns and refunds")
            self.contract = (Path(__file__).parent / "pane" / "types" / "index.d.ts").read_text(encoding="utf-8")

        with it("should return exactly the fields TicketJson names"):
            declared = self.contract[self.contract.index("export type TicketJson = {"):].split("\n}")[0]
            expect(set(self.project.ticket_json("pet-visits"))).to(equal(set(re.findall(r"^  (\w+)\??:", declared, re.M))))

        with it("should return exactly the fields BacklogItemJson names"):
            declared = self.contract[self.contract.index("export type BacklogItemJson"):].split("\n")[0]
            expect(set(self.project.column("Backlog")["items"][0])).to(equal(set(re.findall(r"(\w+): string", declared))))

        with it("should return only the fields ColumnJson names on a stage"):
            declared = self.contract[self.contract.index("export type ColumnJson = {"):].split("\n}")[0]
            expect(set(self.project.column("Discovery")) - set(re.findall(r"^  (\w+)\??:", declared, re.M))).to(equal(set()))

    with context("whose signatures are compared with the plugin tests"):
        with it("should give every tool behaviour the same signature in the plugin tests"):
            spec = Path(__file__).read_text(encoding="utf-8")
            plugin = (Path(__file__).parent / "pane" / "hooks" / "register.test.tsx").read_text(encoding="utf-8").replace(chr(92) + "'", "'")
            signatures = set(re.findall(r'with it\("(should [^"]+)"\)', spec))
            front_end = set(re.findall(r"test\('(should .+?)', async", plugin))
            shared_only_in_python = {
                "should give every tool behaviour the same signature in the plugin tests",
                "should return exactly the fields TicketJson names",
                "should return exactly the fields BacklogItemJson names",
                "should return only the fields ColumnJson names on a stage",
                "should name each tool after its object",
                "should take the ticket's name on every ticket tool that acts on one",
                "should leave the board read out of the session log",
                "should save the choice to the ticket's session.json",
                "should save that folder as the session's workpath",
                "should leave the session working on the repository",
                "should write the title and text to one markdown file",
                "should say a ticket has no branch yet",
                "should count the violations of each rule",
                "should leave out the violations of other practices in the saved graph",
                "should say the report has its saved graph",
                "should still return the report's text",
                "should leave the current session as it is",
            }
            expect(sorted(signatures - shared_only_in_python - front_end)).to(equal([]))
