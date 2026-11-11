"""The session board as tools an agent calls (cdd MCP), through the MCP server, organised by story.

A behavior the board app shares across its tiers keeps its sentence here, in `app/tests/kanban/**/*.spec.shared.ts`."""
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import patch

from expects import be_false, be_true, contain, equal, expect, have_key, match, raise_error, start_with
from mamba import after, before, context, description, it

from harness.installation.repository_toolsets import RepositoryToolsets

RepositoryToolsets(Path(__file__).resolve().parents[2]).ensure_import_path()

from harness.catalog_generator.catalog_practice import CatalogPractice  # noqa: E402
from harness.installation.data_class import DataClass  # noqa: E402
from space.kanban.backlog_item import BacklogItem  # noqa: E402
from space.kanban.board import Stage  # noqa: E402
from harness.graph.violation import Violation  # noqa: E402
from space.kanban.report import ReportRule  # noqa: E402
from space.kanban.session_board_examples import saved_graph, saved_practice  # noqa: E402
from space.kanban.story_test import progress_in  # noqa: E402
from space.kanban.ticket import Ticket  # noqa: E402
from space.repo.repo import Branch  # noqa: E402
from space.kanban.board import FidelityNotFoundError, NotAStageError  # noqa: E402
from space.session.sessions import PracticeNotFoundError  # noqa: E402
from space.session.file_manager import PathOutsideRootsError  # noqa: E402
from space.session import Sessions  # noqa: E402
from space.session.session import UnknownPracticeError  # noqa: E402

from space.kanban.board_tools_examples import CHECKED_GRAPH, DISCOVERY_DONE, JUDGED_REPORT, ProjectTools, STORY_MAP_GRAPH, WHOLE_STORIES_GRAPH, next_action_of, reports_of, session_file_of, violation_counts_of  # noqa: E402


with description("the board tools") as self:
    with before.each:
        self.project = ProjectTools()

    with after.each:
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

        with it("should say which of a stage's actions take the formats an action bar picks"):
            expect(self.project.column("Specification")["actions_with_formats"]).to(equal(["generate", "render"]))

        with it("should name the project the board belongs to"):
            expect(self.project.call("board.show")["project"]).to(equal(self.project.root.name))

        # (S) Board App --> Display Backlog Items As Tickets
        with it("should say when a backlog item last changed"):
            expect(self.project.column("Backlog")["items"][0]["last_activity"]).to(match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"))

        with it("should give a backlog item its text"):
            expect(self.project.column("Backlog")["items"][0]["text"]).to(equal("An idea."))

        # (S) Person --> Choose Session Root
        with it("should say a ticket works on the whole repository until a person chooses a workpath"):
            expect(self.project.ticket_json("pet-visits")["session"]["workpath"]).to(equal(""))

        with context("with folders in the repository"):
            with before.each:
                for folder in ("src/visits", "src/billing", "node_modules/left-pad", ".git/objects"):
                    (self.project.root / folder).mkdir(parents=True, exist_ok=True)

            with it("should list the folders at the top of the repository a workpath can be chosen from"):
                expect(self.project.call("board.folders")).to(contain("src"))

            with it("should leave out installed packages and hidden folders"):
                expect([folder for folder in self.project.call("board.folders") if folder in ("node_modules", ".git")]).to(equal([]))

            with it("should list the folders inside one, as paths from the project"):
                expect(self.project.call("board.folders", path="src")).to(equal(["src/billing", "src/visits"]))

            with context("that a person has chosen as a ticket's workpath"):
                with before.each:
                    self.chosen = self.project.call("session.choose_workpath", session=session_file_of("pet-visits"), path="src/visits")

                with it("should show the folder as the ticket's workpath"):
                    expect(self.chosen["workpath"]).to(equal("src/visits"))

                with it("should keep the folder as the session's work folder"):
                    saved = json.loads((self.project.sessions / "pet-visits" / "session.json").read_text(encoding="utf-8"))
                    expect(Path(saved["workpath"])).to(equal((self.project.root / "src" / "visits").resolve()))

            with context("that a person has chosen as one practice's root"):
                with before.each:
                    self.chosen = self.project.call("practice-session-output.choose_root", session=session_file_of("pet-visits"), practice="stories", path="src/visits")

                with it("should show the folder as that practice's root, chosen by a person"):
                    expect((self.chosen["root"], self.chosen["is_root_chosen"])).to(equal(("src/visits", True)))

                with it("should write that practice's files there"):
                    files = self.project.call("fidelity-progress.files", ticket="pet-visits", fidelity="stories-story-map")["markdown"]
                    expect(files[0]["path"]).to(start_with("src/visits/"))

                with it("should leave every other practice on its default root"):
                    expect(self.project.ticket_json("pet-visits")["session"]["practices"]["bdd"]["is_root_chosen"]).to(be_false)

                with context("and then a new workpath for the ticket"):
                    with before.each:
                        self.moved = self.project.call("session.choose_workpath", session=session_file_of("pet-visits"), path="src")

                    with it("should keep that practice writing to the folder chosen for it"):
                        expect(self.moved["practices"]["stories"]["root"]).to(equal("src/visits"))

                with context("and then back to its default"):
                    with before.each:
                        self.reset = self.project.call("practice-session-output.use_default_root", session=session_file_of("pet-visits"), practice="stories")

                    with it("should show the practice on its default root again"):
                        expect(self.reset["is_root_chosen"]).to(be_false)

            with context("that a person has chosen as the ticket's workpath, with no practice root chosen"):
                with before.each:
                    self.chosen = self.project.call("session.choose_workpath", session=session_file_of("pet-visits"), path="src/visits")

                with it("should put each practice's default practice root under the ticket's workpath"):
                    expect(self.chosen["practices"]["stories"]["root"]).to(start_with("src/visits"))

            with context("that a person has started a backlog item in a folder"):
                with before.each:
                    self.started = self.project.call("backlog-item.start", backlog_item="Returns and refunds", path="src/billing")

                with it("should open its ticket with that folder as its workpath"):
                    expect(self.started["session"]["workpath"]).to(equal("src/billing"))

        # (S) Person --> Set Stage WIP Limit
        with it("should give every stage a limit of 3 tickets until a person sets one"):
            expect(self.project.column("Discovery")["wip_limit"]).to(equal(3))

        with context("that sets a stage's limit below the tickets it holds"):
            with before.each:
                (self.project.sessions / "_board.json").unlink(missing_ok=True)
                self.limited = self.project.call("stage.set_wip_limit", stage="Discovery", limit=0)

            with it("should show the stage over its limit"):
                expect(self.limited["is_over_limit"]).to(be_true)

            with it("should keep the limit for the next read of the board"):
                expect(self.project.column("Discovery")["wip_limit"]).to(equal(0))

        with context("that sets a WIP limit on a column that is not a stage"):
            with it("should refuse it, naming the column"):
                expect(lambda: self.project.call("stage.set_wip_limit", stage="Backlog", limit=2)).to(raise_error(NotAStageError))

        # (S) Board App --> Display Latest Handoff
        with it("should show no handoff for a ticket that has none"):
            expect(self.project.ticket_json("pet-visits")["session"]["handoff"]).to(equal(""))

        with context("with handoffs written for the ticket"):
            with before.each:
                session = self.project.sessions / "pet-visits"
                (session / "handoff-20261030T1730.md").write_text("earlier\n", encoding="utf-8")
                (session / "handoff-20261031T0412.md").write_text("latest\n", encoding="utf-8")

            with it("should show the latest handoff"):
                expect(self.project.ticket_json("pet-visits")["session"]["handoff"]).to(equal(".sessions/pet-visits/handoff-20261031T0412.md"))

        # (S) Person --> Open Validation Report
        with it("should show no report for a fidelity that has none"):
            expect(reports_of(self.project.ticket_json("pet-visits"))).to(equal({}))

        with context("with validation reports saved for a fidelity"):
            with before.each:
                reports = self.project.sessions / "pet-visits" / "validation-reports"
                reports.mkdir()
                (reports / "clean-engineering-modules-20261030T173000.md").write_text("earlier\n", encoding="utf-8")
                (reports / "clean-engineering-modules-20261031T041200.md").write_text("# Graph rule validation\n", encoding="utf-8")
                (reports / "clean-engineering-modules-20261031T041200.json").write_text(json.dumps(CHECKED_GRAPH), encoding="utf-8")

            with it("should show that fidelity's latest report"):
                latest = ".sessions/pet-visits/validation-reports/clean-engineering-modules-20261031T041200.md"
                expect(reports_of(self.project.ticket_json("pet-visits"))).to(equal({"clean-engineering-modules": latest}))

            # (S) Person --> Fix Report Violations
            with it("should list each rule the report names with its violations"):
                report = self.project.call("fidelity-progress.report", ticket="pet-visits", fidelity="clean-engineering-modules")
                expect(report["rules"][0]["violations"][0]["message"]).to(equal("Name the story with a verb"))

            with it("should give a violation the line it failed on"):
                report = self.project.call("fidelity-progress.report", ticket="pet-visits", fidelity="clean-engineering-modules")
                expect(report["rules"][0]["violations"][0]["location"] + ":" + str(report["rules"][0]["violations"][0]["line"])).to(equal("docs/map.md:12"))

            with it("should show no source for a file that is not in the repository"):
                report = self.project.call("fidelity-progress.report", ticket="pet-visits", fidelity="clean-engineering-modules")
                expect(report["rules"][0]["violations"][0]["source"]).to(equal([]))

            with context("with the file a violation names in the repository"):
                with before.each:
                    docs = self.project.root / "docs"
                    docs.mkdir()
                    (docs / "map.md").write_text("".join(f"line {number}\n" for number in range(1, 21)), encoding="utf-8")

                with it("should show the source lines around a violation"):
                    report = self.project.call("fidelity-progress.report", ticket="pet-visits", fidelity="clean-engineering-modules")
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
                    report = self.project.call("fidelity-progress.report", ticket="pet-visits", fidelity="clean-engineering-modules")
                    expect(report["rules"][0]["violations"][0]["location"]).to(equal("harness/pets/docs/map.md"))

                with it("should show the source lines of the file in the session's root"):
                    report = self.project.call("fidelity-progress.report", ticket="pet-visits", fidelity="clean-engineering-modules")
                    expect(report["rules"][0]["violations"][0]["source"][0]["text"]).to(equal("pets line 10"))

            with it("should return exactly the fields a Violation marks as its data"):
                report = self.project.call("fidelity-progress.report", ticket="pet-visits", fidelity="clean-engineering-modules")
                expect(set(report["rules"][0]["violations"][0])).to(equal(set(DataClass(Violation).fields)))

            with it("should return exactly the fields a ReportRule marks as its data"):
                report = self.project.call("fidelity-progress.report", ticket="pet-visits", fidelity="clean-engineering-modules")
                expect(set(report["rules"][0])).to(equal(set(DataClass(ReportRule).fields)))

            with it("should count the violations of each rule"):
                report = self.project.call("fidelity-progress.report", ticket="pet-visits", fidelity="clean-engineering-modules")
                expect((report["rules"][0]["rule"]["slug"], report["rules"][0]["count"])).to(equal(("domain-nouns-only", 2)))

            with it("should send how many violations it names in all"):
                report = self.project.call("fidelity-progress.report", ticket="pet-visits", fidelity="clean-engineering-modules")
                expect(report["violation_count"]).to(equal(2))

            with it("should leave out the violations of other practices in the saved graph"):
                report = self.project.call("fidelity-progress.report", ticket="pet-visits", fidelity="clean-engineering-modules")
                expect([rule["rule"]["slug"] for rule in report["rules"]]).to(equal(["domain-nouns-only"]))

            with it("should say the report has its saved graph"):
                report = self.project.call("fidelity-progress.report", ticket="pet-visits", fidelity="clean-engineering-modules")
                expect(report["has_saved_graph"]).to(equal(True))

        with context("with a validation report saved without its graph"):
            with before.each:
                reports = self.project.sessions / "pet-visits" / "validation-reports"
                reports.mkdir()
                (reports / "clean-engineering-modules-20261030T173000.md").write_text("### verb-noun-format: 1 violation(s)\n", encoding="utf-8")

            with it("should say a report has no saved graph"):
                report = self.project.call("fidelity-progress.report", ticket="pet-visits", fidelity="clean-engineering-modules")
                expect((report["has_saved_graph"], report["rules"])).to(equal((False, [])))

            with it("should still return the report's text"):
                report = self.project.call("fidelity-progress.report", ticket="pet-visits", fidelity="clean-engineering-modules")
                expect(report["text"]).to(contain("verb-noun-format"))

        with context("with a validation report on a rule the practice describes"):
            with before.each:
                self.project.report("pet-visits", "stories-story-map-20261031T041200", STORY_MAP_GRAPH)

            with it("should show the text of each rule under its name"):
                report = self.project.call("fidelity-progress.report", ticket="pet-visits", fidelity="stories-story-map")
                expect(report["rules"][0]["rule"]["body"]).to(contain("verb"))

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

        # A saved graph keeps the hits of a scanner deleted after it was saved.
        with context("with a validation report on a rule no scanner checks any more"):
            with before.each:
                deleted = saved_graph(saved_practice("stories", "node-1", "docs/map.md", 12, ("evidence-distinguishes-observed-inferred-and-intended", "Label the evidence")))
                self.project.report("pet-visits", "stories-story-map-20261031T041200", deleted)

            with it("should leave that rule's hits out of the report"):
                report = self.project.call("fidelity-progress.report", ticket="pet-visits", fidelity="stories-story-map")
                expect(report["rules"]).to(equal([]))

        # (E) Tickets
        # (S) Person --> Open Ticket Session
        with context("that opens a new ticket"):
            with before.each:
                self.opened = self.project.call("ticket.create", title="Loyalty points", scope="feature")

            with it("should return the new ticket in Discovery"):
                expect((self.opened["name"], self.opened["column"]["name"])).to(equal(("loyalty-points", "Discovery")))

            with it("should leave the current session as it is"):
                expect(self.project.call("board.show")["active"]["name"]).to(equal("main"))

        with context("that opens a ticket on a folder in the repository"):
            with before.each:
                self.project.call("ticket.create", title="Pet records", scope="feature", path="harness/pets")

            with it("should save that folder as the session's workpath"):
                fields = json.loads((self.project.sessions / "pet-records" / "session.json").read_text(encoding="utf-8"))
                expect(fields["workpath"]).to(equal(str((self.project.root / "harness" / "pets").resolve())))

        with context("that opens a ticket with no folder"):
            with before.each:
                self.project.call("ticket.create", title="Pet records", scope="feature")

            with it("should save no workpath, so the session works on the repository"):
                fields = json.loads((self.project.sessions / "pet-records" / "session.json").read_text(encoding="utf-8"))
                expect("workpath" in fields).to(equal(False))

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

        # (S) Person --> Add Backlog Item, Start Backlog Item
        with context("that starts a backlog item"):
            with before.each:
                self.started = self.project.call("backlog-item.start", backlog_item="Returns and refunds", scope="feature")

            with it("should return the new ticket in Discovery"):
                expect((self.started["name"], self.started["column"]["name"])).to(equal(("returns-and-refunds", "Discovery")))

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
                Sessions(self.project.root).switch("pet-visits")
                self.project.call("ticket.close", ticket="pet-visits")

            with it("should make main the active ticket"):
                expect(self.project.call("board.show")["active"]["name"]).to(equal("main"))

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
                expect((self.moved["column"]["name"], self.moved["is_done"])).to(equal(("Implementation", True)))

        # (S) Person --> Move Ticket, a ticket that is done in Discovery
        with context("that moves a ticket to the next column"):
            with before.each:
                self.moved = self.project.call("ticket.move_next", ticket="pet-visits")

            with it("should show the ticket in the next stage"):
                expect(self.moved["column"]["name"]).to(equal("Specification"))

            with it("should show the ticket in progress there"):
                expect(self.moved["is_done"]).to(be_false)

            # (S) Person --> Mark Ticket Done In Stage
            with context("with that stage's work not done"):
                with before.each:
                    self.moved = self.project.call("ticket.move_next", ticket="pet-visits")

                with it("should show the ticket in that stage's Done all the same"):
                    expect((self.moved["column"]["name"], self.moved["is_done"])).to(equal(("Specification", True)))

                with context("and on to the column after"):
                    with before.each:
                        self.project.call("ticket.move_next", ticket="pet-visits")
                        self.project.call("ticket.move_next", ticket="pet-visits")
                        self.moved = self.project.call("ticket.move_next", ticket="pet-visits")

                    with context("and past Implementation"):
                        with before.each:
                            self.moved = self.project.call("ticket.move_next", ticket="pet-visits")

                        with it("should close the ticket"):
                            expect(self.moved["column"]["name"]).to(equal("Complete"))

                        with it("should leave a ticket in Complete where it is on another move forward"):
                            expect(self.project.call("ticket.move_next", ticket="pet-visits")["column"]["name"]).to(equal("Complete"))

                        with context("and back again"):
                            with before.each:
                                self.moved = self.project.call("ticket.move_previous", ticket="pet-visits")

                            with it("should reopen the ticket in Implementation"):
                                expect(self.moved["column"]["name"]).to(equal("Implementation"))

                with context("and back from Done"):
                    with before.each:
                        self.moved = self.project.call("ticket.move_previous", ticket="pet-visits")

                    with it("should show the ticket in progress in that stage"):
                        expect((self.moved["column"]["name"], self.moved["is_done"])).to(equal(("Specification", False)))

            with context("and back to the previous column"):
                with before.each:
                    self.moved = self.project.call("ticket.move_previous", ticket="pet-visits")

                with it("should show the ticket in Discovery"):
                    expect(self.moved["column"]["name"]).to(equal("Discovery"))

                with it("should show the ticket in Discovery's Done"):
                    expect(self.moved["is_done"]).to(be_true)

        # (S) Person --> Choose Ticket Practices
        with context("that turns a practice off for a ticket"):
            with before.each:
                self.chosen = self.project.call("practice-session-output.enable", session=session_file_of("pet-visits"), practice="ux", is_enabled=False)

            with it("should show the practice off for that ticket"):
                expect(self.chosen["enabled"]).to(be_false)

            with it("should save the choice to the ticket's session.json"):
                fields = json.loads((self.project.sessions / "pet-visits" / "session.json").read_text(encoding="utf-8"))
                expect(fields["practices"]).to(equal({"ux": {"enabled": False}}))

        with context("that turns off a practice the session does not know"):
            with it("should refuse it, naming the practice"):
                try:
                    self.project.call("practice-session-output.enable", session=session_file_of("pet-visits"), practice="astrology", is_enabled=False)
                    refused = None
                except UnknownPracticeError as error:
                    refused = error.practice
                expect(refused).to(equal("astrology"))

        # (S) Board App --> Display Fidelity Progress
        with it("should show each fidelity's Generate and Validate"):
            actions = progress_in(self.project.ticket_json("pet-visits"), "stories-story-map")["actions"]
            expect(actions).to(equal({"generate": "done", "validate": "done"}))

        # The board app names and colours each practice from these, and finds a fidelity's practice among its slugs.
        with it("should name and colour every practice the board shows"):
            stories = self.project.call("board.show")["practices"][0]
            expect((stories["key"], stories["short_name"], stories["colour"])).to(equal(("stories", "Stories", "#6BCB77")))

        # The board sends each fidelity once: in its own list, with its practice, which a tile finds it by.
        with it("should name each fidelity's practice beside the fidelity"):
            shown = next(entry for entry in self.project.call("board.show")["fidelities"] if entry["fidelity"]["slug"] == "stories-story-map")
            expect(shown["practice"]).to(equal({"key": "stories"}))

        with it("should send no second list of a practice's fidelities"):
            stories = self.project.call("board.show")["practices"][0]
            expect(stories).not_to(have_key("fidelities"))

        # (S) Person --> Open Help
        with context("that opens help on a fidelity"):
            with before.each:
                self.help = self.project.call("fidelity-progress.help", ticket="pet-visits", fidelity="stories-story-map")

            with it("should show the fidelity's rules, as the fidelity sends them"):
                expect([rule["slug"] for rule in self.help["fidelity"]["rules"]]).to(contain("verb-noun-format"))

            with it("should show the fidelity's own overview, as the fidelity sends it"):
                expect(self.help["fidelity"]["overview"]).to(contain("Scope the solution"))

            with it("should name the stage a fidelity belongs to"):
                expect(self.help["stage"]["name"]).to(equal("Discovery"))

            with it("should link to the fidelity's page on the forge"):
                expect(self.help["href"]).to(equal("https://forge.abdworks.net/abd-context-driven-delivery/fidelities/stories-story_map.html"))

        with context("that opens help on a practice"):
            with before.each:
                self.help = self.project.call("board.help", practice="stories")

            with it("should show the practice's shared rules, as the practice sends them"):
                expect([rule["slug"] for rule in self.help["practice"]["rules"]]).to(contain("do-not-invent-requirements"))

            with it("should name no fidelity on a practice's help"):
                expect((self.help["fidelity"], self.help["stage"])).to(equal((None, None)))

        # The catalog's view of the board's practices names their pages and skills; the process makes it once for the
        # checkout, though every call makes a new board.
        with context("that is asked for its help and shown several times"):
            with before.each:
                with patch.object(CatalogPractice, "skill_install", wraps=CatalogPractice.skill_install) as made:
                    self.helps = [self.project.call("board.help", practice="stories"), self.project.call("board.help", practice="ux")]
                    self.project.call("board.show")
                    self.project.call("fidelity-progress.help", ticket="pet-visits", fidelity="stories-story-map")
                self.made = made.call_count

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
                expect(files).to(equal([{"path": (self.outside / "src" / "visits_spec.py").as_posix(), "exists": True}]))

            # (S) Person --> View Fidelity Files, a path that names its module
            with it("should list the files a named part of the path finds there, in folders at any depth"):
                model = self.outside / "src" / "visits" / ".context" / "visits-model.md"
                model.parent.mkdir(parents=True)
                model.write_text("# Visits\n", encoding="utf-8")
                files = self.project.call("fidelity-progress.files", ticket="pet-visits", fidelity="clean-engineering-model")["markdown"]
                expect(files).to(equal([{"path": model.as_posix(), "exists": True}]))

        with context("with a fidelity's markdown generated"):
            with before.each:
                docs = self.project.root / "docs" / ".context"
                docs.mkdir(parents=True)
                (docs / "story-map.md").write_text("# Story map\n", encoding="utf-8")
                fields = {"outputs": {"stories": {"root": "docs", "story_map": {"markdown": "story-map.md"}}}}
                (self.project.sessions / "pet-visits" / "session.json").write_text(json.dumps({"name": "pet-visits", **fields}), encoding="utf-8")

            with it("should list the file with whether it exists"):
                files = self.project.call("fidelity-progress.files", ticket="pet-visits", fidelity="stories-story-map")["markdown"]
                expect(files).to(equal([{"path": "docs/.context/story-map.md", "exists": True}]))

            with it("should list only that fidelity's formats"):
                files = self.project.call("fidelity-progress.files", ticket="pet-visits", fidelity="stories-story-map")
                expect(sorted(files)).to(equal(["drawio", "markdown"]))

            # (S) Person --> View Fidelity Files: the page opens tabs in the order Python sends the formats.
            with it("should send the formats in the order files are shown, markdown before code"):
                files = self.project.call("fidelity-progress.files", ticket="pet-visits", fidelity="clean-engineering-model")
                expect(list(files)).to(equal(["markdown", "python", "typescript"]))

            # One fidelity object per session: the progress's fidelity is the one an action on the ticket's session works with.
            with it("should give each progress the fidelity its ticket's session holds"):
                ticket = Ticket.load("pet-visits", project=self.project.root)
                expect(ticket.work.progress_of("stories-story-map").fidelity is ticket.session.practices["stories"].fidelities["story_map"]).to(be_true)

            with it("should give the board the ticket's session.json"):
                expect(self.project.ticket_json("pet-visits")["session"]["session_file"]).to(equal(".sessions/pet-visits/session.json"))

            # (S) Person --> View Fidelity Files
            with it("should return the file's text"):
                opened = self.project.call("session.read_file", session=session_file_of("pet-visits"), path="docs/.context/story-map.md")
                expect(opened["text"]).to(equal("# Story map\n"))

            with it("should return no text for a file that is gone, such as one deleted since the board listed it"):
                opened = self.project.call("session.read_file", session=session_file_of("pet-visits"), path="docs/.context/gone.md")
                expect(opened).to(equal({"path": "docs/.context/gone.md", "text": ""}))

            with it("should refuse a file outside the repository"):
                expect(lambda: self.project.call("session.read_file", session=session_file_of("pet-visits"), path="../elsewhere.md")).to(raise_error(PathOutsideRootsError))

            # A ticket's worktree sits beside the repository, so its practices write outside it.
            with it("should return the text of a file under a practice root outside the repository, such as the ticket's worktree"):
                worktree = Path(tempfile.mkdtemp(prefix="kanban-worktree-"))
                (worktree / "story-map.md").write_text("# Worktree map\n", encoding="utf-8")
                self.project.call("practice-session-output.choose_root", session=session_file_of("pet-visits"), practice="stories", path=str(worktree))
                opened = self.project.call("session.read_file", session=session_file_of("pet-visits"), path=(worktree / "story-map.md").as_posix())
                expect(opened["text"]).to(equal("# Worktree map\n"))

        # (S) Person --> List Ticket Files, the session folder
        with context("with files in its session folder"):
            with before.each:
                (self.project.sessions / "pet-visits" / "notes").mkdir()
                (self.project.sessions / "pet-visits" / "notes" / "idea.md").write_text("# Idea\n", encoding="utf-8")

            with it("should list every file in the session folder"):
                files = self.project.call("session.folder_files", session=session_file_of("pet-visits"))
                expect(files).to(contain({"path": ".sessions/pet-visits/notes/idea.md", "exists": True}))

            with it("should list the files from the project"):
                files = self.project.call("session.folder_files", session=session_file_of("pet-visits"))
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

            # The page says a ticket moved back by finding the item that holds it, never by matching titles.
            with it("should name the ticket the item holds"):
                expect(self.moved["ticket"]).to(equal("sign-up"))

            with it("should take the ticket off the board's stages"):
                expect(self.project.tickets_in("Discovery")).to(equal(["main"]))

            # (S) Person --> Add Backlog Item, Start Backlog Item
            with context("that starts the item again"):
                with before.each:
                    self.started = self.project.call("backlog-item.start", backlog_item="Sign up")

                with it("should bring the ticket back with its work"):
                    expect((self.started["name"], (self.project.sessions / "sign-up" / "session.json").is_file())).to(equal(("sign-up", True)))

        # (S) Person --> Send Next Fidelity Action
        with it("should name generate as the next action"):
            expect(next_action_of(self.project.ticket_json("sign-up"))).to(equal("generate"))

        with it("should allow only the actions that need no output before anything is generated"):
            expect(progress_in(self.project.ticket_json("sign-up"), "stories-story-map")["allowed_actions"]).to(equal(["generate", "iterate", "sketch", "document"]))

        # The board's Run sends render only once there is output to convert; Python says so, not the page.
        with it("should not allow Render before anything is generated"):
            expect(progress_in(self.project.ticket_json("sign-up"), "stories-story-map")["allowed_actions"]).not_to(contain("render"))

        # (S) Person --> Choose Action And Formats
        with context("with an action bar opened on its story map"):
            with before.each:
                self.chips = self.project.call("ticket.format_choices", ticket="sign-up", fidelities=["stories-story-map"])

            with it("should offer a chip for each group of formats the story map writes, diagram first"):
                expect([chip["label"] for chip in self.chips]).to(equal(["diagram", "markdown"]))

            with it("should open with the chip of its default format picked"):
                expect([chip["label"] for chip in self.chips if chip["starts_picked"]]).to(equal(["markdown"]))

        with context("with an action bar opened on its UX mockup"):
            with before.each:
                self.chips = self.project.call("ticket.format_choices", ticket="sign-up", fidelities=["ux-mockup"])

            with it("should offer the design canvas as a chip of its own, after the code"):
                expect([chip["label"] for chip in self.chips]).to(equal(["code", "canvas"]))

            with it("should send the claude_design format for the canvas chip"):
                expect(next(chip["formats"] for chip in self.chips if chip["label"] == "canvas")).to(equal(["claude_design"]))

            with it("should open with the canvas unpicked, since the mockup defaults to html"):
                expect([chip["label"] for chip in self.chips if chip["starts_picked"]]).to(equal(["code"]))

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

        with context("with an action bar opened on its story map and its bounded context, the story map's markdown written"):
            with before.each:
                (self.project.root / ".context").mkdir(exist_ok=True)
                (self.project.root / ".context" / "story-map.md").write_text("# Story Map\n", encoding="utf-8")
                chips = self.project.call("ticket.format_choices", ticket="sign-up", fidelities=["stories-story-map", "ddd-bounded-context"])
                self.markdown = next(chip for chip in chips if chip["label"] == "markdown")
                self.chips_named = lambda label: [chip for chip in chips if chip["label"] == label and chip["starts_picked"]]

            with it("should count the fidelities that offer the markdown chip"):
                expect(self.markdown["offered"]).to(equal(2))

            with it("should count the fidelities that have a file in it already"):
                expect(self.markdown["made"]).to(equal(1))

            # B6: the bounded context still has no markdown of its own, so a stage Run writes its default format.
            with it("should open picked while a fidelity whose default it holds has not made it"):
                expect(self.markdown["starts_picked"]).to(be_true)

            with it("should open the code chip unpicked, since no fidelity here defaults to code"):
                expect(self.chips_named("code")).to(equal([]))

            with it("should send each fidelity's own format for the chip"):
                expect(self.markdown["formats"]).to(equal(["markdown"]))

        with context("with an action bar opened on its story map, its markdown written"):
            with before.each:
                (self.project.root / ".context").mkdir(exist_ok=True)
                (self.project.root / ".context" / "story-map.md").write_text("# Story Map\n", encoding="utf-8")
                chips = self.project.call("ticket.format_choices", ticket="sign-up", fidelities=["stories-story-map"])
                self.markdown = next(chip for chip in chips if chip["label"] == "markdown")

            with it("should open with a chip every fidelity has made left unpicked"):
                expect(self.markdown["starts_picked"]).to(be_false)

        # A person can write a fidelity's file by hand, and checking it should not wait for a generate.
        with context("whose story map is already written, with nothing recorded"):
            with before.each:
                (self.project.root / ".context").mkdir(exist_ok=True)
                (self.project.root / ".context" / "story-map.md").write_text("# Story Map\n", encoding="utf-8")

            with it("should allow Validate and Render on that file"):
                expect(progress_in(self.project.ticket_json("sign-up"), "stories-story-map")["allowed_actions"]).to(equal(["generate", "validate", "iterate", "sketch", "render", "document"]))

            with it("should still name generate as the next action"):
                expect(progress_in(self.project.ticket_json("sign-up"), "stories-story-map")["next_action"]).to(equal("generate"))

    # (S) Person --> Send Next Fidelity Action
    with context("with a ticket whose story map has passed validate"):
        with before.each:
            self.project.ticket(
                "sign-up",
                "2026-10-31T01:00:00Z generate /work stories story_map markdown stories no-chat",
                "2026-10-31T01:00:01Z validate Stories story_map no-chat",
                title="Sign up",
            )

        # A story map generated and validated without violations is done.
        with it("should name generate on the next fidelity as the next action"):
            expect(next_action_of(self.project.ticket_json("sign-up"))).to(equal("generate"))

        # (S) Person --> Invoke Next Fidelity Action
        with it("should name each fidelity's own next action"):
            ticket = self.project.ticket_json("sign-up")
            expect((progress_in(ticket, "stories-story-map")["next_action"], progress_in(ticket, "stories-scenarios")["next_action"])).to(equal(("", "generate")))

        # The validating agent adds its judgment to the report after validate has logged its graph's result.
        with context("with a report whose judgment fails rules the graph passed"):
            with before.each:
                self.project.report("sign-up", "stories-story-map-20261031T041200")
                (self.project.sessions / "sign-up" / "validation-reports" / "stories-story-map-20261031T041200.md").write_text(JUDGED_REPORT, encoding="utf-8")

            with it("should name validate as the next action"):
                expect(next_action_of(self.project.ticket_json("sign-up"))).to(equal("validate"))

            with it("should count each finding of the judgment"):
                expect(violation_counts_of(self.project.ticket_json("sign-up"))).to(equal({"stories-story-map": 5}))

    # (S) Person --> Send Next Fidelity Action
    with context("with a ticket whose next fidelity has violations"):
        with before.each:
            self.project.ticket(
                "sign-up",
                "2026-10-31T01:00:00Z generate /work stories story_map markdown stories no-chat",
                "2026-10-31T01:00:01Z validate Stories story_map graph-rule verb-noun-format map.md:12 no-chat",
                title="Sign up",
            )

        with it("should name validate as the next action"):
            expect(next_action_of(self.project.ticket_json("sign-up"))).to(equal("validate"))

        with it("should allow Validate again on the same output"):
            expect(progress_in(self.project.ticket_json("sign-up"), "stories-story-map")["allowed_actions"]).to(equal(["generate", "validate", "iterate", "sketch", "render", "document"]))

        with it("should name validate as that fidelity's own next action"):
            expect(progress_in(self.project.ticket_json("sign-up"), "stories-story-map")["next_action"]).to(equal("validate"))

        # (S) Person --> Open Validation Report
        with context("with that fidelity's report saved with its graph"):
            with before.each:
                self.project.report("sign-up", "stories-story-map-20261031T041200", STORY_MAP_GRAPH)

            with it("should count the violations of the fidelity on its ticket"):
                expect(violation_counts_of(self.project.ticket_json("sign-up"))).to(equal({"stories-story-map": 2}))

        with context("with that fidelity's report saved without its graph"):
            with before.each:
                self.project.report("sign-up", "stories-story-map-20261031T041200")

            with it("should leave a fidelity with no saved graph uncounted"):
                expect(violation_counts_of(self.project.ticket_json("sign-up"))).to(equal({}))

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

        with it("should give the folder of the reports for every fidelity"):
            expect(self.project.call("ticket.violations", ticket="sign-up")["path"]).to(equal(".sessions/sign-up/validation-reports"))

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
        with before.each:
            self.project.ticket(
                "sign-up",
                "2026-10-31T01:00:01Z validate Stories scenarios graph-rule verb-noun-format map.md:12 no-chat",
                title="Sign up",
            )
            self.project.report("sign-up", "stories-scenarios-20261031T041200", WHOLE_STORIES_GRAPH)

        with it("should list the scenarios rules and the story map rules"):
            report = self.project.call("fidelity-progress.report", ticket="sign-up", fidelity="stories-scenarios")
            expect([rule["rule"]["slug"] for rule in report["rules"]]).to(equal(["verb-noun-format", "plain-english-gwt-steps"]))

        with it("should count the same rules on the ticket"):
            expect(violation_counts_of(self.project.ticket_json("sign-up"))).to(equal({"stories-scenarios": 2}))

        with context("with a story map report newer than the scenarios report"):
            with before.each:
                reports = self.project.sessions / "sign-up" / "validation-reports"
                (reports / "stories-story-map-20261031T050000.md").write_text("# Graph rule validation\n", encoding="utf-8")

            with it("should leave the story map rules to the story map report"):
                report = self.project.call("fidelity-progress.report", ticket="sign-up", fidelity="stories-scenarios")
                expect([rule["rule"]["slug"] for rule in report["rules"]]).to(equal(["plain-english-gwt-steps"]))

            with it("should count only the rules the scenarios report answers for"):
                expect(violation_counts_of(self.project.ticket_json("sign-up"))).to(equal({"stories-scenarios": 1}))

    with context("with a session open in the project"):
        with before.each:
            Sessions(self.project.root).switch("pet-visits", self.project.root)
            self.log = self.project.sessions / "pet-visits" / "session.log"
            self.project.call("board.show")

        with it("should leave the board read out of the session log"):
            expect(self.log.read_text(encoding="utf-8")).not_to(contain("board.show"))

    # The chat bar reads the board every turn through MCP, whose answers are cut off past their size limit, so it reads
    # board.overview: the active ticket whole and every other ticket by its name and column.
    with context("with the chat bar's overview of the board"):
        with before.each:
            for number in range(12):
                self.project.ticket(f"ticket-{number}", *DISCOVERY_DONE, title=f"Ticket {number}")
            # The chat bar of ticket-0's own chat, which works on ticket-0.
            self.project.call("sessions.switch", name="ticket-0")
            self.overview = self.project.call("board.overview")

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

        with it("should send each practice's colour under its key"):
            expect(sorted(self.overview["practices"][0])).to(equal(["colour", "practice", "short_name"]))

        with it("should stay well inside an MCP answer with a dozen tickets"):
            expect(len(json.dumps(self.overview)) < 40_000).to(be_true)

    with context("that are published through the cdd server"):
        with it("should name each tool after its object"):
            names = set(self.project.server.tools)
            expect(names).to(equal({
                "board.show", "board.overview", "board.help", "board.folders", "board.set_sends_fixes_directly", "stage.set_wip_limit",
                "ticket.create", "ticket.activate", "ticket.branch", "ticket.work_branch", "ticket.close_choices", "ticket.format_choices", "ticket.overlay_choices", "ticket.choose_overlays", "ticket.move_next", "ticket.move_previous", "ticket.move_to", "ticket.close", "ticket.archive", "ticket.violations", "ticket.assign_chat",
                "ticket.edit_text", "ticket.tag", "ticket.delete", "ticket.add_child", "ticket.pull_out", "ticket.reassign_parent", "ticket.move_before",
                "fidelity-progress.report", "fidelity-progress.files", "fidelity-progress.help",
                "sessions.current", "sessions.switch", "session.close", "session.append_log", "session.mark_loop", "session.read_loop",
                "session.choose_workpath", "session.folder_files", "session.read_file",
                "session.write_handoff", "session.read_handoff_format", "session.read_cdr_format", "session.list_cdrs", "session.write_cdr",
                "practice-session-output.enable", "practice-session-output.choose_root", "practice-session-output.use_default_root",
                "backlog-item.create", "backlog-item.start", "backlog-item.edit_text", "backlog-item.move_before",
            }))

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
        with before.each:
            self.project.ticket("pet-visits", title="Pet visits")
            self.project.backlog_item("returns.md", "Returns and refunds")

        with it("should return exactly the fields a Ticket marks as its data"):
            expect(set(self.project.ticket_json("pet-visits"))).to(equal(set(DataClass(Ticket).fields)))

        with it("should send a Ticket's progress as one FidelityProgress per fidelity, each naming its fidelity"):
            expect([progress["fidelity"]["slug"] for progress in self.project.ticket_json("pet-visits")["progress"]][:2]).to(equal(["stories-story-map", "ddd-bounded-context"]))

        with it("should send a Ticket's column by its name alone, since the column sends the ticket"):
            expect(self.project.ticket_json("pet-visits")["column"]).to(equal({"name": "Discovery"}))

        # board.show is read every turn by the chat bar through MCP, whose answers are cut off past their size limit, so
        # a fidelity's guidance text, which its help call reads, is never repeated in it.
        with it("should send each fidelity a Stage requires by its slug alone"):
            expect(self.project.column("Discovery")["work_required"][0]).to(equal({"slug": "stories-story-map"}))

        with it("should send each fidelity a Ticket's progress is on by its slug alone"):
            expect(self.project.ticket_json("pet-visits")["progress"][0]["fidelity"]).to(equal({"slug": "stories-story-map"}))

        with it("should send a Ticket's next fidelity by its ticket and slug alone, since its progress sends it"):
            expect(self.project.ticket_json("pet-visits")["next"]).to(equal({"ticket": {"name": "pet-visits"}, "fidelity": {"slug": "stories-story-map"}}))

        with it("should send the board's active ticket whole, so the chat bar never finds it again by its name"):
            self.project.call("sessions.switch", name="pet-visits")
            active = self.project.call("board.show")["active"]
            expect((active["name"], "progress" in active)).to(equal(("pet-visits", True)))

        with it("should return exactly the fields a Branch marks as its data"):
            subprocess.run(["git", "init", "-q", "-b", "main"], cwd=self.project.root, check=False)
            branch = self.project.call("ticket.branch", ticket="pet-visits")
            expect(set(branch)).to(equal(set(DataClass(Branch).fields)))

        with it("should return exactly the fields a BacklogItem marks as its data"):
            expect(set(self.project.column("Backlog")["items"][0])).to(equal(set(DataClass(BacklogItem).fields)))

        with it("should return exactly the fields a Stage marks as its data"):
            expect(set(self.project.column("Discovery"))).to(equal(set(DataClass(Stage).fields)))

    with context("whose signatures are compared with the board app's shared behaviors"):
        with it("should state every shared behavior here under the same sentence"):
            spec = Path(__file__).read_text(encoding="utf-8")
            signatures = set(re.findall(r'with it\("(should [^"]+)"\)', spec))
            shared_files = (Path(__file__).parent / "app" / "tests" / "kanban").rglob("*.spec.shared.ts")
            shared = {sentence for path in shared_files for sentence in re.findall(r"\bit\('(should .+?)',", path.read_text(encoding="utf-8"))}
            only_on_the_page = {"should leave a stage holding fewer tickets than its limit within it"}
            expect(sorted(shared - signatures - only_on_the_page)).to(equal([]))
