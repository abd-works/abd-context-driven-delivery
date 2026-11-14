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
import threading
from datetime import datetime, timezone

from expects import contain, equal, expect, raise_error, start_with
from mamba import after, before, context, description, it

from harness.agent_tools.agent_tools import AgentInstructions
from harness.agent_tools.tool_call import ToolCall
from space.session.throwaway_project import ThrowawayProject
from harness.guidance.fixtures.sample_tool.sample_tool_host import (
    SamplePracticeGuidance,
)
import space.session.practice_session_output as session_output_module
from harness.graph.saved_graph import SavedGraph
from cdd_guidance.actions.validate.checked_graph import CheckedGraph
from space.session.session_files import NamedPathNotFoundError
from cdd_guidance.actions.validate.validate import Validate
from cdd_guidance.actions.validate.validate_examples import ENTITY_ROOT_FILE, SPEC_FILE, STORY_FILE, SampleWorkingCopy, working_in
import cdd_guidance.practices  # noqa: F401 - registers the practices with the practice catalogue
import cdd_guidance.actions  # noqa: F401 - registers the actions with the action catalogue



# Five parameters, over the three limit-operation-parameters allows.
_OVER_LIMIT = "export class {name} {{\n  place(a: string, b: string, c: string, d: string, e: string): void {{}}\n}}\n"
# "Boarding Stuff" opens with a gerund, which verb-noun-format rejects. A word missing from the verb list passes, so the fixture needs an opening the rule flags.
_STORY_MAP = "# (E) Move Work On Board\n\n## (E) Display Board\n\n### (S) Person --> Open Board\n\n### (S) Person --> Boarding Stuff\n"
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


class _ClockAtOneSecond(datetime):
    """The clock a report's name is dated by, stopped, so two calls fall in the same second."""

    @classmethod
    def now(cls, tz=None):
        return datetime(2026, 11, 7, 3, 43, 43, tzinfo=timezone.utc)


class _StoryMapFolder:
    """A folder holding the story map, in a throwaway project whose main session a validate checks it in, made to work
    in root, a folder of it. declared makes the story map fidelity declare the story map, and its drawio, as its output;
    drawio writes that drawio."""

    _MAP = "board/.context/story-map.md"

    def __init__(self, root: str = "", declared: bool = False, drawio: bool = False) -> None:
        self.project = ThrowawayProject()
        self.folder = Path(tempfile.mkdtemp(prefix="cdd-validate-"))
        _write(self.folder, self._MAP, _STORY_MAP)
        if drawio:
            _write(self.folder, "board/.context/story-map.drawio", _EMPTY_DRAWIO)
        self.action = Validate(session=working_in(self.project, self.folder, self.folder / root))
        self.session = Path(self.action.session.session_path)
        if declared:
            outputs = {"markdown": [str(self.folder / self._MAP)], "drawio": [str(self.folder / "board/.context/story-map.drawio")]}
            self.action.session.practice("stories").guidance.fidelities.entries["story_map"].output_paths = lambda: outputs

    def validate(self, guidance: str = "stories-story-map", paths: list[str] | None = None) -> str:
        return self.action.validate(guidance=[guidance], paths=paths or [self._MAP])

    def validate_lines(self) -> list[str]:
        log = self.session / "session.log"
        return [line for line in log.read_text(encoding="utf-8").splitlines() if " validate " in line]

    def close(self) -> None:
        self.project.close()
        shutil.rmtree(self.folder, ignore_errors=True)


def _expanded_validate(action, arguments):
    return AgentInstructions.for_callable(Validate.validate, action).expand(
        arguments
    ).instructions


with description("a validate action on practice guidance") as self:
    with before.each:
        self.project = ThrowawayProject()
        self.guidance = SamplePracticeGuidance(format="markdown")
        self.action = Validate(session=ToolCall(project=self.project.root).session)

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
            self.action = Validate(session=working_in(self.project, self.folder, self.folder))
            self.session = Path(self.action.session.session_path)
            # A session's graph is the one created for it in its own folder, so the fixture's graph is put there.
            self.session.mkdir(parents=True, exist_ok=True)
            shutil.copy(self.folder / ".context" / "graph.json", self.session / "graph.json")

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

    with context("with a clean-engineering-violations.json left in the session and no saved graph"):
        with before.each:
            self.folder = Path(tempfile.mkdtemp(prefix="cdd-validate-"))
            self.action = Validate(session=working_in(self.project, self.folder, self.folder))
            self.session = Path(self.action.session.session_path)
            self.session.mkdir(parents=True, exist_ok=True)
            shutil.copy(Path(__file__).with_name("fixtures") / "sample-graph-violations.json", self.session / "clean-engineering-violations.json")

        with after.each:
            shutil.rmtree(self.folder, ignore_errors=True)

        with it("should not report that file's hits when graph is true"):
            report = self.action.validate(guidance=["clean-engineering-code"], graph=True)
            expect(report).not_to(contain("sampleOp"))

    # Each validate below builds a graph, so each context makes its files and validates once, in before.all, and its
    # examples read what that left; a context whose examples change what the next would see makes files of its own.
    with context("with the edited files"):
        with before.all:
            self.edited_project = ThrowawayProject()
            self.edited = Path(tempfile.mkdtemp(prefix="cdd-validate-"))
            _write(self.edited, "src/orders/order.ts", _OVER_LIMIT.format(name="Order"))
            _write(self.edited, "src/billing/invoice.ts", _OVER_LIMIT.format(name="Invoice"))
            action = Validate(session=working_in(self.edited_project, self.edited, self.edited))
            self.edited_report = action.validate(guidance=["clean-engineering-code"], paths=["src/orders/order.ts"])

        with after.all:
            self.edited_project.close()
            shutil.rmtree(self.edited, ignore_errors=True)

        with it("should report the rule violations in those files as they are now"):
            expect(self.edited_report).to(contain("limit-operation-parameters"))
            expect(self.edited_report).to(contain("[src/orders/order.ts]("))

        with it("should leave files outside the edited paths out of the report"):
            expect(self.edited_report).not_to(contain("src/billing/invoice.ts"))

        with it("should not write the workspace graph"):
            expect((self.edited / ".context" / "graph.json").exists()).to(equal(False))

    with context("with an edited story map markdown file"):
        with before.all:
            self.map = _StoryMapFolder()
            self.map_report = self.map.validate()

        with after.all:
            self.map.close()

        with it("should report the story map's rule violations at the story map's path"):
            expect(self.map_report).to(contain("[board/.context/story-map.md]("))

        with it("should report the verb-noun-format violation on the story that breaks it"):
            expect(self.map_report).to(contain("Boarding Stuff"))

        # The session board lists the agent's judgment beside the graph's hits only when it is written in this shape.
        with it("should tell the agent to write its judgment under the judged file, one heading per failed rule"):
            expect(self.map_report).to(contain("## Judgment — `harness/.context/stories/story-map.md`\n\n   ### `rule-slug` — Fail\n   - story-map.md:86"))

        # The board opens a finding's file in this project, so a path anywhere else cannot be opened.
        with it("should tell the agent to name the judged file by its path from the project's root"):
            expect(self.map_report).to(contain("as a path from the project's root"))

        # The board opens each finding at one line, so a range or a second place would be lost.
        with it("should tell the agent to give each finding one file and one line"):
            expect(self.map_report).to(contain("a finding at two places is two bullets"))

        # The session board reads a fidelity's latest validate line, so a second, clean line would hide the violations.
        with context("that has been validated"):
            with before.all:
                self.validated = _StoryMapFolder()
                self.validated.validate()
                self.validate_lines = self.validated.validate_lines()

            with after.all:
                self.validated.close()

            with it("should write one validate line"):
                expect(len(self.validate_lines)).to(equal(1))

            with it("should name its violations on that line"):
                expect(self.validate_lines[-1]).to(contain(" graph-rule "))

        # The line names the fidelity worked at, which the log reads from that fidelity's own session output.
        with context("that has been validated at a fidelity after the first"):
            with before.all:
                self.later = _StoryMapFolder()
                self.later.validate("stories-scenarios")

            with after.all:
                self.later.close()

            with it("should name that fidelity on its validate line"):
                expect(self.later.validate_lines()[-1]).to(contain(" validate Stories scenarios"))

        # A board command names its ticket's session, which need not be the session open in the chat that runs it.
        with context("in a session the command names that is not the open one"):
            with before.all:
                self.named = _StoryMapFolder()
                folder = self.named.folder
                self.other = folder / ".sessions" / "pet-visits"
                self.other.mkdir(parents=True)
                (self.other / "session.json").write_text(f'{{"workpath": "{(folder / "board").as_posix()}"}}', encoding="utf-8")
                guidance = f"stories-story-map session={(self.other / 'session.json').as_posix()}"
                action = Validate().for_call(ToolCall({"guidance": guidance}, folder))
                self.named_report = action.validate(guidance=guidance, paths=[(folder / "board/.context/story-map.md").as_posix()])

            with after.all:
                self.named.close()

            with it("should check the named session's files"):
                expect(self.named_report).to(contain("Epic `Move Work On Board`"))

            with it("should save the report in the named session"):
                expect([path.suffix for path in (self.other / "validation-reports").iterdir()]).to(contain(".md"))

        # The session board validates with no paths, and a report saved without its graph lists no violations to fix.
        with context("that the story map fidelity declares as its output"):
            with context("that is validated with no paths named"):
                with before.all:
                    self.declared = _StoryMapFolder(declared=True)
                    self.declared_report = self.declared.action.validate(guidance=["stories-story-map"])

                with after.all:
                    self.declared.close()

                with it("should report the violations in the declared output"):
                    expect(self.declared_report).to(contain("Boarding Stuff"))

                with it("should save the graph it checked beside the report"):
                    expect([path.suffix for path in (self.declared.session / "validation-reports").iterdir()]).to(contain(".json"))

            # The drawio mirrors the markdown, so judging both reports every finding twice. A call naming a format leaves
            # it as the fidelity's last used, so each call below checks a story map of its own.
            with context("with its drawio beside it"):
                with context("that is validated on both its files"):
                    with before.all:
                        self.both = _StoryMapFolder(declared=True, drawio=True)
                        self.both_report = self.both.validate(paths=["board/.context/story-map.md", "board/.context/story-map.drawio"])

                    with after.all:
                        self.both.close()

                    with it("should judge only the markdown the fidelity writes by default"):
                        expect(self.both_report).to(contain("Judge only the checked format's files (markdown: "))

                with context("that is validated on a markdown file the call names"):
                    with before.all:
                        self.elsewhere = _StoryMapFolder(declared=True, drawio=True)
                        _write(self.elsewhere.folder, "elsewhere/story-map.md", "# (E) Board Elsewhere\n")
                        self.elsewhere_report = self.elsewhere.validate(paths=["elsewhere/story-map.md"])

                    with after.all:
                        self.elsewhere.close()

                    with it("should judge the markdown file the call names, not the fidelity's declared one"):
                        expect(self.elsewhere_report).to(contain("Judge only the checked format's files (markdown: elsewhere/story-map.md)"))

                with context("that is validated in the format the guidance names"):
                    with before.all:
                        self.named_format = _StoryMapFolder(declared=True, drawio=True)
                        self.named_format_report = self.named_format.action.validate(guidance="stories-story-map format=drawio")

                    with after.all:
                        self.named_format.close()

                    with it("should judge only the format the guidance names"):
                        expect(self.named_format_report).to(contain("Judge only the checked format's files (drawio: "))

                with context("that the latest generate wrote"):
                    with before.all:
                        from harness.guidance_actions import GuidanceAction

                        self.generated = _StoryMapFolder(declared=True, drawio=True)
                        action = GuidanceAction(session=self.generated.action.session)
                        action._work_on("stories-story-map format=drawio")
                        action.run(lambda item: None, action="generate")
                        self.generated_report = self.generated.action.validate(guidance=["stories-story-map"])

                    with after.all:
                        self.generated.close()

                    with it("should judge only the drawio"):
                        expect(self.generated_report).to(contain("Judge only the checked format's files (drawio: "))

                # Each call has an action of its own, so a call checking the drawio must not change which files a call
                # checking the markdown, in the same session, leaves out of its report.
                with context("while another call checks the drawio"):
                    with before.all:
                        self.racing = _StoryMapFolder(declared=True, drawio=True)
                        validate = self.racing.action
                        resolve = CheckedGraph.check_beside
                        markdown_call_waiting = threading.Event()
                        drawio_call_done = threading.Event()

                        def resolve_after_the_drawio_call(checked_graph, reports):
                            if threading.current_thread() is markdown_call:
                                markdown_call_waiting.set()
                                drawio_call_done.wait(60)
                            return resolve(checked_graph, reports)

                        def check_the_markdown():
                            self.racing_report = validate.validate(guidance=["stories-story-map"], paths=["board/.context/story-map.md"])

                        CheckedGraph.check_beside = resolve_after_the_drawio_call
                        try:
                            markdown_call = threading.Thread(target=check_the_markdown)
                            markdown_call.start()
                            markdown_call_waiting.wait(60)
                            validate.made_for(validate.session).validate(guidance="stories-story-map format=drawio")
                            drawio_call_done.set()
                            markdown_call.join()
                        finally:
                            CheckedGraph.check_beside = resolve

                    with after.all:
                        self.racing.close()

                    with it("should report the violations in the markdown it checks"):
                        expect(self.racing_report).to(contain("Boarding Stuff"))

            # A story's scenarios sit in files beside the story map, and a story read without them has none.
            with context("with the scenario file of its story beside it"):
                with before.all:
                    self.with_scenarios = _StoryMapFolder(declared=True)
                    _write(self.with_scenarios.folder, "board/.context/display-board/open-board/open_board_story.test.py", _OPEN_BOARD_SCENARIOS)
                    self.with_scenarios_report = self.with_scenarios.action.validate(guidance=["stories-story-map"])

                with after.all:
                    self.with_scenarios.close()

                with it("should read the story's scenarios from the file beside the declared output"):
                    expect(self.with_scenarios_report).not_to(contain("'Open Board': 0 scenarios"))

        # An agent works from the project's checkout, so every path it sees starts there, not at the session's root.
        with context("in a session whose root is a folder of the project"):
            with before.all:
                self.rooted = _StoryMapFolder(root="board")
                self.rooted_report = self.rooted.validate()
                self.rooted_absolute_report = self.rooted.validate(paths=[str(self.rooted.folder / "board/.context/story-map.md")])

            with after.all:
                self.rooted.close()

            with it("should read a path named from the project's root"):
                expect(self.rooted_report).to(contain("Boarding Stuff"))

            with it("should report the violation at its path from the session's root"):
                expect(self.rooted_report).to(contain("[.context/story-map.md]("))

            with it("should read an absolute path"):
                expect(self.rooted_absolute_report).to(contain("Boarding Stuff"))

            # The graph reads only under the session's root, so a file of the project outside it would be checked as
            # nothing.
            with context("that is named a file of the project outside the session's root"):
                with before.all:
                    (self.rooted.folder / "outside.md").write_text("# Outside\n", encoding="utf-8")

                with it("should refuse it, naming the session's root"):
                    expect(lambda: self.rooted.validate(paths=["outside.md"])).to(
                        raise_error(NamedPathNotFoundError, contain(f"under the session's root {(self.rooted.folder / 'board').resolve()} at outside.md"))
                    )

        # A graph built from nothing reports no violations, which reads as a clean validate.
        with context("that is named by a path that is not there"):
            with before.all:
                self.missing = _StoryMapFolder()

            with after.all:
                self.missing.close()

            with it("should refuse, naming the path and the root it was read from"):
                expect(lambda: self.missing.validate(paths=["board/.context/missing.md"])).to(
                    raise_error(NamedPathNotFoundError, contain(f"board/.context/missing.md, read from {self.missing.folder}"))
                )

            with it("should save no report"):
                try:
                    self.missing.validate(paths=["board/.context/missing.md"])
                except NamedPathNotFoundError:
                    pass
                expect((self.missing.session / "validation-reports").exists()).to(equal(False))

    # The sample's graph takes seconds to build, so one working copy is validated in before.all, once for each call the
    # examples read, and each example reads the report, and the report files, its own call left.
    with context("with edited files of a working copy that every graph practice reads"):
        with before.all:
            self.sample_project = ThrowawayProject()
            sample = SampleWorkingCopy(self.sample_project)
            self.sample_session = sample.session
            reports = self.sample_session / "validation-reports"
            reports.mkdir(parents=True)
            self.earlier = reports / "ddd-tactics-20200101T000000.json"
            self.earlier.write_text("[]", encoding="utf-8")

            def validated(guidance: list[str], paths: list[str]) -> tuple[str, list[Path]]:
                """The report of one validate of the working copy, and the report files that validate saved."""
                before_call = set(reports.iterdir())
                report = sample.action.validate(guidance=guidance, paths=paths)
                return report, sorted(set(reports.iterdir()) - before_call)

            self.sample_validated = validated
            self.entity_root_report, saved = validated(["ddd-tactics"], [ENTITY_ROOT_FILE])
            self.entity_root_saved = next(path for path in saved if path.suffix == ".md")
            self.story_report, _ = validated(["stories-scenarios"], [STORY_FILE])
            self.spec_report, _ = validated(["bdd-development"], [SPEC_FILE])
            self.spec_and_story_report, _ = validated(["bdd-development"], [SPEC_FILE, STORY_FILE])
            self.code_report, _ = validated(["clean-engineering-code"], [ENTITY_ROOT_FILE])
            _, self.two_guidance_saved = validated(["ddd-tactics", "stories-scenarios"], [ENTITY_ROOT_FILE])

        with after.all:
            self.sample_project.close()

        with it("should report the private-method-naming violation on the edited entity root"):
            expect(self.entity_root_report).to(contain("private-method-naming"))
            expect(self.entity_root_report).to(contain(f"[{ENTITY_ROOT_FILE}]("))

        with it("should report the verb-noun-format violation on the edited story"):
            expect(self.story_report).to(contain("verb-noun-format"))
            expect(self.story_report).to(contain(f"[{STORY_FILE}]("))

        with it("should report the observable-behavior violation on the edited spec"):
            expect(self.spec_report).to(contain("observable-behavior"))
            expect(self.spec_report).to(contain(f"[{SPEC_FILE}]("))

        with it("should report only the violations of the guidance's own practice"):
            expect(self.spec_and_story_report).not_to(contain("verb-noun-format"))

        # A rule over a whole practice compares the files a validate names with every file the session's graph holds, so
        # two validates of one file found other hits as other chats loaded other files; the report names those files.
        with context("after another validate refreshed other files into the session's graph"):
            with before.all:
                self.sample_validated(["bdd-development"], [SPEC_FILE])
                self.held_report, _ = self.sample_validated(["ddd-tactics"], [ENTITY_ROOT_FILE])

            with it("should name the folders of the files the graph held beside those it checked"):
                expect(self.held_report).to(contain("The session's graph also held"))
                expect(self.held_report).to(contain(f"- `{'/'.join(Path(SPEC_FILE).parent.parts[:2])}`"))

        # Calls running at once would each read the graph the last one wrote.
        with it("should write no graph that every call in the session shares"):
            expect((self.sample_session / "edited-graph.json").exists()).to(equal(False))

        with it("should name the graph it checked, beside the report, in the report"):
            expect(self.entity_root_report).to(contain(str(self.entity_root_saved.with_suffix(".json"))))

        # At the code and model fidelities the rules are about the object model the code holds, which validate builds as a graph.
        with it("should tell the judge to judge the graph it built at a code fidelity"):
            expect(self.code_report).to(contain("Judge the graph validate built from the checked format's files"))

        with it("should name what the judge reads in the graph"):
            expect(self.code_report).to(contain("its classes, operations, parameters, properties, relationships, and dependencies"))

        with it("should save the report in the session's reports folder, named after the fidelity and date"):
            expect(self.entity_root_saved.name).to(start_with("ddd-tactics-"))
            expect(self.entity_root_saved.read_text(encoding="utf-8")).to(contain("private-method-naming"))

        with it("should save a report for each listed guidance"):
            saved = [path for path in self.two_guidance_saved if path.name.startswith("stories-scenarios-") and path.suffix == ".md"]
            expect(len(saved)).to(equal(1))

        with it("should save the graph it checked beside the report, under the same name"):
            expect(self.entity_root_saved.with_suffix(".json").is_file()).to(equal(True))

        with it("should keep the rule hits on the nodes of the saved graph"):
            slugs = [violation.rule for violation in SavedGraph.from_file(self.entity_root_saved.with_suffix(".json")).violations(["ddd"])]
            expect(slugs).to(contain("private-method-naming"))

        with it("should leave an earlier report's saved graph as it was"):
            expect(self.earlier.read_text(encoding="utf-8")).to(equal("[]"))

        with it("should say where the report is saved"):
            expect(self.entity_root_report).to(contain(str(self.entity_root_saved)))

        # A report's name is dated to the second, so a second call in that second would write over the first's report.
        with context("that is validated twice in the same second"):
            with before.all:
                clock = session_output_module.datetime
                session_output_module.datetime = _ClockAtOneSecond
                try:
                    _, first = self.sample_validated(["ddd-tactics"], [ENTITY_ROOT_FILE])
                    _, second = self.sample_validated(["ddd-tactics"], [ENTITY_ROOT_FILE])
                finally:
                    session_output_module.datetime = clock
                self.same_second_reports = sorted(path for path in first + second if path.suffix == ".md")

            with it("should save a report for each call"):
                expect(len(self.same_second_reports)).to(equal(2))

            with it("should save each call's graph beside its own report"):
                expect([report.with_suffix(".json").is_file() for report in self.same_second_reports]).to(equal([True, True]))


with description("two validate calls running at once on one cdd server") as self:
    with after.each:
        ThrowawayProject.close_all()

    # Actions log to the open session, so each example works on its own project rather than this repository's.
    with before.each:
        project = ThrowawayProject().root
        served = Validate()
        self.wrong = []

        def validate_repeatedly(slug, own_rule, other_rule):
            for _ in range(4):
                report = served.for_call(ToolCall({"guidance": slug}, project)).validate(slug)
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
