"""BDD spec — Validate action."""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("cdd_guidance/practices", "tools", "cdd_guidance/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

import shutil
import tempfile

from expects import contain, equal, expect, raise_error
from mamba import after, before, context, description, it

from harness.agent_tools.agent_tools import AgentInstructions
from space.session import Session
from space.session.throwaway_project import ThrowawayProject
from harness.guidance.fixtures.sample_tool.sample_tool_host import (
    SamplePracticeGuidance,
)
from validate.graph_json_reader import violations_from_graph_json_files
from validate.validate import PathsNotFoundError, Validate


_SAMPLE = _REPO_ROOT / "harness" / "graph" / "_examples" / "input"
_STORY_FOLDER = "tests/onboard-a-customer/authenticate-user"
_ENTITY_ROOT_FILE = "src/account-credentials/account-credentials.ts"
_STORY_FILE = f"{_STORY_FOLDER}/authenticate_user.story.shared.ts"
_SPEC_FILE = f"{_STORY_FOLDER}/authenticate_user.story.server.spec.ts"

# Five parameters, over the three limit-operation-parameters allows.
_OVER_LIMIT = "export class {name} {{\n  place(a: string, b: string, c: string, d: string, e: string): void {{}}\n}}\n"
# "Board Stuff" opens with a noun, which verb-noun-format rejects.
_STORY_MAP = "# (E) Move Work On Board\n\n## (E) Display Board\n\n### (S) Person --> Open Board\n\n### (S) Person --> Board Stuff\n"
# The scenarios of the story map's Open Board story, in the file a story's heading links to.
_EMPTY_DRAWIO = '<mxfile><diagram name="Story Map"><mxGraphModel><root><mxCell id="0" /></root></mxGraphModel></diagram></mxfile>\n'
_OPEN_BOARD_SCENARIOS ="""from story_test import given, scenario, story, then, when

# Epic: Move Work On Board
# Sub-epic: Display Board
# Map: ../../story-map.md#s-person----open-board

# Story: Open Board
# Actor: Person
with story("Open Board"):
    with scenario("Open the board"):
        with given("the board is closed"):
            pass
        with when("the Person opens the board"):
            pass
        with then("the board shows its columns"):
            pass
"""


def _write(root: Path, relative: str, text: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _expanded_validate(action, arguments):
    return AgentInstructions.for_callable(Validate.validate, action).expand(
        {}, arguments
    ).instructions


with description("a validate action on practice guidance") as self:
    with before.each:
        self.project = ThrowawayProject()
        self.guidance = SamplePracticeGuidance(format="markdown")
        self.action = Validate()

    with after.each:
        self.project.close()

    with context("with no rule passed"):
        with it("should document graph JSON in validate instructions"):
            prose = _expanded_validate(self.action, {"guidance": [self.guidance]})
            expect(prose).to(contain("graph_return_nodes"))

        with it("should return validate instructions for every rule in one shot"):
            report = self.action.validate(guidance=[self.guidance])
            expect(report).to(contain("sample-rule-one"))

    with context("with one rule passed"):
        with it("should return validate instructions for that rule only"):
            rule = self.guidance.rules.entries["sample-rule-one"]
            report = self.action.validate(guidance=[self.guidance], rule=rule)
            expect(report).to(contain("sample-rule-one"))

    with context("with a fidelity active"):
        with it("should pass that fidelity's rules with the shared rules"):
            guidance = SamplePracticeGuidance(format="markdown", fidelity="sketch")
            report = self.action.validate(guidance=[guidance])
            expect(report).to(contain("sample-rule-one"))
            expect(report).to(contain("sketch-rule"))
            expect(report).not_to(contain("spec-rule"))

    with context("with stories practice guidance"):
        with it("should load the shared rules collection from the whole practice slug"):
            report = self.action.validate(guidance=["stories"])
            expect(report).to(contain("vocabulary-traces-to-domain-source"))

        with it("should load shared and fidelity rules when the fidelity slug is scenarios"):
            report = self.action.validate(guidance=["scenarios"])
            expect(report).to(contain("vocabulary-traces-to-domain-source"))
            expect(report).to(contain("gwt-steps-trace-to-domain-operations"))

    with context("with ddd and stories guidance"):
        with it("should return shared and active-fidelity rules from each practice"):
            report = self.action.validate(guidance=["ddd", "stories"])
            expect(report).to(contain("ubiquitous-language-everywhere"))
            expect(report).to(contain("experts-words-preferred"))
            expect(report).to(contain("do-not-invent-requirements"))
            expect(report).to(contain("verb-noun-format"))

    with context("with graph JSON paths"):
        with it("should append a graph-rule report from summary JSON and still include AI rules"):
            fixture = Path(__file__).with_name("fixtures") / "sample-graph-violations.json"
            report = self.action.validate(
                guidance=[self.guidance],
                graph=str(fixture),
            )
            expect(report).to(contain("Graph rule validation"))
            expect(report).to(contain("limit-operation-parameters"))
            expect(report).to(contain("**[graph rule]**"))
            expect(report).to(contain("sample-rule-one"))
            expect(report).not_to(contain("vscode://"))
            expect(report).not_to(contain("file://"))
            expect(report).to(contain("#L10"))
            expect(report).to(contain("[src/example.ts]("))
            expect(report).not_to(contain("[src\\example.ts]"))

        with it("should return the graph-rule report when the MCP prompt expands validate"):
            fixture = Path(__file__).with_name("fixtures") / "sample-graph-violations.json"
            prose = _expanded_validate(
                self.action,
                {"guidance": [self.guidance], "graph": str(fixture)},
            )
            expect(prose).to(contain("limit-operation-parameters"))
            expect(prose).to(contain("[src/example.ts]("))
            expect(prose).to(contain("sample-rule-one"))

    with context("with the saved graph"):
        with before.each:
            self.folder = Path(__file__).with_name("fixtures") / "saved-graph"
            self.session = Path(tempfile.mkdtemp(prefix="cdd-validate-session-"))
            self.action._validate_workspace = lambda: self.folder
            self.action._project_checkout = lambda: self.folder
            self.action._session_path = lambda: self.session

        with after.each:
            shutil.rmtree(self.session, ignore_errors=True)

        with it("should report the guidance practice's graph hits from graph.json when graph is true"):
            prose = _expanded_validate(self.action, {"guidance": ["ddd-tactics"], "graph": True})
            expect(prose).to(contain("load-with-identity-in-hand"))
            expect(prose).to(contain("[src/orders/order.ts]("))
            expect(prose).not_to(contain("sampleOp"))

        with it("should read a saved graph document passed as the graph path"):
            report = self.action.validate(
                guidance=["clean-engineering-code"],
                graph=str(self.folder / ".context" / "graph.json"),
            )
            expect(report).to(contain("sampleOp"))
            expect(report).not_to(contain("OrderRepository"))

    with context("with the edited files"):
        with before.each:
            self.folder = Path(tempfile.mkdtemp(prefix="cdd-validate-"))
            _write(self.folder, "src/orders/order.ts", _OVER_LIMIT.format(name="Order"))
            _write(self.folder, "src/billing/invoice.ts", _OVER_LIMIT.format(name="Invoice"))
            self.session = Path(tempfile.mkdtemp(prefix="cdd-validate-session-"))
            self.action._validate_workspace = lambda: self.folder
            self.action._project_checkout = lambda: self.folder
            self.action._session_path = lambda: self.session

        with after.each:
            shutil.rmtree(self.folder, ignore_errors=True)
            shutil.rmtree(self.session, ignore_errors=True)

        with it("should report the rule violations in those files as they are now"):
            report = self.action.validate(guidance=["clean-engineering-code"], paths=["src/orders/order.ts"])
            expect(report).to(contain("limit-operation-parameters"))
            expect(report).to(contain("[src/orders/order.ts]("))

        with it("should leave files outside the edited paths out of the report"):
            report = self.action.validate(guidance=["clean-engineering-code"], paths=["src/orders/order.ts"])
            expect(report).not_to(contain("src/billing/invoice.ts"))

        with it("should not write the workspace graph"):
            self.action.validate(guidance=["clean-engineering-code"], paths=["src/orders/order.ts"])
            expect((self.folder / ".context" / "graph.json").exists()).to(equal(False))

    with context("with an edited story map markdown file"):
        with before.each:
            self.folder = Path(tempfile.mkdtemp(prefix="cdd-validate-"))
            _write(self.folder, "board/.context/story-map.md", _STORY_MAP)
            self.session = Path(tempfile.mkdtemp(prefix="cdd-validate-session-"))
            self.action._validate_workspace = lambda: self.folder
            self.action._project_checkout = lambda: self.folder
            self.action._session_path = lambda: self.session

        with after.each:
            shutil.rmtree(self.folder, ignore_errors=True)
            shutil.rmtree(self.session, ignore_errors=True)

        with it("should report the story map's rule violations at the story map's path"):
            report = self.action.validate(guidance=["stories-story-map"], paths=["board/.context/story-map.md"])
            expect(report).to(contain("[board/.context/story-map.md]("))

        with it("should report the verb-noun-format violation on the story that breaks it"):
            report = self.action.validate(guidance=["stories-story-map"], paths=["board/.context/story-map.md"])
            expect(report).to(contain("Board Stuff"))

        # The session board lists the agent's judgment beside the graph's hits only when it is written in this shape.
        with it("should tell the agent to write its judgment under the judged file, one heading per failed rule"):
            report = self.action.validate(guidance=["stories-story-map"], paths=["board/.context/story-map.md"])
            expect(report).to(contain("## Judgment — `harness/kanban/.context/story-map.md`\n\n   ### `rule-slug` — Fail\n   - story-map.md:86"))

        # The board opens a finding's file in this project, so a path anywhere else cannot be opened.
        with it("should tell the agent to name the judged file by its path from the project's root"):
            report = self.action.validate(guidance=["stories-story-map"], paths=["board/.context/story-map.md"])
            expect(report).to(contain("as a path from the project's root"))

        # The board opens each finding at one line, so a range or a second place would be lost.
        with it("should tell the agent to give each finding one file and one line"):
            report = self.action.validate(guidance=["stories-story-map"], paths=["board/.context/story-map.md"])
            expect(report).to(contain("a finding at two places is two bullets"))

        # The session board reads a fidelity's latest validate line, so a second, clean line would hide the violations.
        with context("that has been validated"):
            with before.each:
                self.action.validate(guidance=["stories-story-map"], paths=["board/.context/story-map.md"])
                log = Path(Session.current().session_path) / "session.log"
                self.validate_lines = [line for line in log.read_text(encoding="utf-8").splitlines() if " validate " in line]

            with it("should write one validate line"):
                expect(len(self.validate_lines)).to(equal(1))

            with it("should name its violations on that line"):
                expect(self.validate_lines[-1]).to(contain(" graph-rule "))

        # A board command names its ticket's session, which need not be the session open in the chat that runs it.
        with context("in a session the command names that is not the open one"):
            with before.each:
                self.other = self.folder / ".sessions" / "pet-visits"
                self.other.mkdir(parents=True)
                (self.other / "session.json").write_text(f'{{"workpath": "{(self.folder / "board").as_posix()}"}}', encoding="utf-8")
                self.action = Validate()
                self.report = self.action.validate(guidance=f"stories-story-map session={(self.other / 'session.json').as_posix()}", paths=[(self.folder / "board/.context/story-map.md").as_posix()])

            with it("should check the named session's files"):
                expect(self.report).to(contain("Epic `Move Work On Board`"))

            with it("should save the report in the named session"):
                expect([path.suffix for path in (self.other / "validation-reports").iterdir()]).to(contain(".md"))

        # The session board validates with no paths, and a report saved without its graph lists no violations to fix.
        with context("that the story map fidelity declares as its output"):
            with before.each:
                declared = {"markdown": [str(self.folder / "board/.context/story-map.md")], "drawio": [str(self.folder / "board/.context/story-map.drawio")]}
                self.action._fidelity_outputs = lambda item: declared

            with context("that is validated with no paths named"):
                with before.each:
                    self.report = self.action.validate(guidance=["stories-story-map"])

                with it("should report the violations in the declared output"):
                    expect(self.report).to(contain("Board Stuff"))

                with it("should save the graph it checked beside the report"):
                    expect([path.suffix for path in (self.session / "validation-reports").iterdir()]).to(contain(".json"))

            # The drawio mirrors the markdown, so judging both reports every finding twice.
            with context("with its drawio beside it"):
                with before.each:
                    _write(self.folder, "board/.context/story-map.drawio", _EMPTY_DRAWIO)

                with it("should judge only the markdown the fidelity writes by default"):
                    report = self.action.validate(guidance=["stories-story-map"], paths=["board/.context/story-map.md", "board/.context/story-map.drawio"])
                    expect(report).to(contain("Judge only the checked format's files (markdown: "))

                with it("should judge only the format the guidance names"):
                    expect(self.action.validate(guidance="stories-story-map format=drawio")).to(contain("Judge only the checked format's files (drawio: "))

                with context("that the latest generate wrote"):
                    with before.each:
                        self.log = Path(Session.current().session_path) / "session.log"
                        self.logged = self.log.read_text(encoding="utf-8") if self.log.is_file() else ""
                        self.log.write_text(self.logged + "2026-11-05T00:00:00Z generate /work stories story_map drawio stories no-chat\n", encoding="utf-8")

                    with after.each:
                        self.log.write_text(self.logged, encoding="utf-8")

                    with it("should judge only the drawio"):
                        expect(self.action.validate(guidance=["stories-story-map"])).to(contain("Judge only the checked format's files (drawio: "))

            # A story's scenarios sit in files beside the story map, and a story read without them has none.
            with context("with the scenario file of its story beside it"):
                with before.each:
                    _write(self.folder, "board/.context/display-board/open-board/open_board_story.test.py", _OPEN_BOARD_SCENARIOS)

                with it("should read the story's scenarios from the file beside the declared output"):
                    expect(self.action.validate(guidance=["stories-story-map"])).not_to(contain("'Open Board': 0 scenarios"))

        # An agent works from the project's checkout, so every path it sees starts there, not at the session's root.
        with context("in a session whose root is a folder of the project"):
            with before.each:
                self.action._validate_workspace = lambda: self.folder / "board"

            with it("should read a path named from the project's root"):
                report = self.action.validate(guidance=["stories-story-map"], paths=["board/.context/story-map.md"])
                expect(report).to(contain("Board Stuff"))

            with it("should report the violation at its path from the session's root"):
                report = self.action.validate(guidance=["stories-story-map"], paths=["board/.context/story-map.md"])
                expect(report).to(contain("[.context/story-map.md]("))

            with it("should read an absolute path"):
                report = self.action.validate(guidance=["stories-story-map"], paths=[str(self.folder / "board/.context/story-map.md")])
                expect(report).to(contain("Board Stuff"))

        # A graph built from nothing reports no violations, which reads as a clean validate.
        with context("that is named by a path that is not there"):
            with it("should refuse, naming the path and the root it was read from"):
                expect(lambda: self.action.validate(guidance=["stories-story-map"], paths=["board/.context/missing.md"])).to(
                    raise_error(PathsNotFoundError, contain(f"board/.context/missing.md, read from {self.folder}"))
                )

            with it("should save no report"):
                try:
                    self.action.validate(guidance=["stories-story-map"], paths=["board/.context/missing.md"])
                except PathsNotFoundError:
                    pass
                expect((self.session / "validation-reports").exists()).to(equal(False))

    with context("with edited files of a working copy that every graph practice reads"):
        with before.each:
            self.session = Path(tempfile.mkdtemp(prefix="cdd-validate-session-"))
            self.action._validate_workspace = lambda: _SAMPLE
            self.action._project_checkout = lambda: _SAMPLE
            self.action._session_path = lambda: self.session

        with after.each:
            shutil.rmtree(self.session, ignore_errors=True)

        with it("should report the private-method-naming violation on the edited entity root"):
            report = self.action.validate(guidance=["ddd-tactics"], paths=[_ENTITY_ROOT_FILE])
            expect(report).to(contain("private-method-naming"))
            expect(report).to(contain(f"[{_ENTITY_ROOT_FILE}]("))

        with it("should report the verb-noun-format violation on the edited story"):
            report = self.action.validate(guidance=["stories-scenarios"], paths=[_STORY_FILE])
            expect(report).to(contain("verb-noun-format"))
            expect(report).to(contain(f"[{_STORY_FILE}]("))

        with it("should report the framework-syntax violation on the edited spec"):
            report = self.action.validate(guidance=["bdd-development"], paths=[_SPEC_FILE])
            expect(report).to(contain("framework-syntax"))
            expect(report).to(contain(f"[{_SPEC_FILE}]("))

        with it("should report only the violations of the guidance's own practice"):
            report = self.action.validate(guidance=["bdd-development"], paths=[_SPEC_FILE, _STORY_FILE])
            expect(report).not_to(contain("verb-noun-format"))

        with it("should write the edited graph beside the session"):
            self.action.validate(guidance=["ddd-tactics"], paths=[_ENTITY_ROOT_FILE])
            expect((self.session / "edited-graph.json").is_file()).to(equal(True))

        with it("should save the report in the session's reports folder, named after the fidelity and date"):
            self.action.validate(guidance=["ddd-tactics"], paths=[_ENTITY_ROOT_FILE])
            saved = next((self.session / "validation-reports").glob("ddd-tactics-*.md"))
            expect(saved.read_text(encoding="utf-8")).to(contain("private-method-naming"))

        with it("should save a report for each listed guidance"):
            self.action.validate(guidance=["ddd-tactics", "stories-scenarios"], paths=[_ENTITY_ROOT_FILE])
            saved = list((self.session / "validation-reports").glob("stories-scenarios-*.md"))
            expect(len(saved)).to(equal(1))

        with it("should save the graph it checked beside the report, under the same name"):
            self.action.validate(guidance=["ddd-tactics"], paths=[_ENTITY_ROOT_FILE])
            report = next((self.session / "validation-reports").glob("ddd-tactics-*.md"))
            expect(report.with_suffix(".json").is_file()).to(equal(True))

        with it("should keep the rule hits on the nodes of the saved graph"):
            self.action.validate(guidance=["ddd-tactics"], paths=[_ENTITY_ROOT_FILE])
            saved = next((self.session / "validation-reports").glob("ddd-tactics-*.json"))
            slugs = [item["rule_slug"] for item in violations_from_graph_json_files([saved], ["ddd"])]
            expect(slugs).to(contain("private-method-naming"))

        with it("should leave an earlier report's saved graph as it was"):
            folder = self.session / "validation-reports"
            folder.mkdir()
            earlier = folder / "ddd-tactics-20200101T000000.json"
            earlier.write_text("[]", encoding="utf-8")
            self.action.validate(guidance=["ddd-tactics"], paths=[_ENTITY_ROOT_FILE])
            expect(earlier.read_text(encoding="utf-8")).to(equal("[]"))

        with it("should say where the report is saved"):
            report = self.action.validate(guidance=["ddd-tactics"], paths=[_ENTITY_ROOT_FILE])
            saved = next((self.session / "validation-reports").glob("ddd-tactics-*.md"))
            expect(report).to(contain(str(saved)))


with description("two validate calls running at once on one action") as self:
    with before.each:
        import threading

        from validate.validate import Validate

        action = Validate()
        self.wrong = []

        def validate_repeatedly(slug, own_rule, other_rule):
            for _ in range(4):
                report = action.validate(slug)
                if own_rule not in report or other_rule in report:
                    self.wrong.append(slug)

        calls = [
            threading.Thread(target=validate_repeatedly, args=("stories-story-map", "verb-noun-format", "hide-inner-details")),
            threading.Thread(target=validate_repeatedly, args=("clean-engineering-model", "hide-inner-details", "verb-noun-format")),
        ]
        for call in calls:
            call.start()
        for call in calls:
            call.join()

    with it("should check each call against the rules of its own guidance"):
        expect(self.wrong).to(equal([]))
