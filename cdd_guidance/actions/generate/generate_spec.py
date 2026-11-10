"""BDD spec — Generate runs validate, including the active fidelity's rules."""
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

from expects import contain, equal, expect
from mamba import after, before, context, description, it

from cdd_guidance.actions.generate.generate import Generate
from harness.agent_tools.agent_tools import AgentInstructions
from harness.agent_tools.tool_call import ToolCall
from harness.guidance.fixtures.sample_tool.sample_tool_host import (
    SamplePracticeGuidance,
)
from harness.mcp.mcp_server import McpServer
from space.session import Sessions
from space.session.throwaway_project import ThrowawayProject


def _made_for(project):
    """A generate made for a call on project, working in the session open there."""
    return Generate().for_call(ToolCall({}, project))


def _expanded_generate(action, arguments):
    return AgentInstructions.for_callable(Generate.generate, action).expand(
        arguments
    )


def _logged_verbs(project):
    log = project / ".sessions" / "alpha" / "session.log"
    return [line.split(" ")[1] for line in log.read_text(encoding="utf-8").splitlines() if len(line.split(" ")) > 1]


def _generate_line(project):
    log = project / ".sessions" / "alpha" / "session.log"
    lines = log.read_text(encoding="utf-8").splitlines()
    return next((line for line in lines if line.split(" ")[1:2] == ["generate"]), "")


with description("a generate action on practice guidance") as self:
    with before.each:
        self.throwaway = ThrowawayProject()
        self.action = Generate()

    with after.each:
        self.throwaway.close()

    # Satisfy names this step after asking for validate; a step that expands to nothing leaves the agent no fixes to apply.
    with context("whose fixes step is expanded"):
        with it("should tell the agent to apply the fixes the latest validate report names"):
            fixes = AgentInstructions.for_callable(Generate.generate_fixes_from_validate, self.action).expand({})
            expect(fixes.instructions).to(contain("Apply the fixes the latest validate report names"))

    with context("with a fidelity active"):
        with it("should include that fidelity's rules in the generate instructions"):
            guidance = SamplePracticeGuidance(format="markdown", fidelity="sketch")
            expanded = _expanded_generate(self.action, {"guidance": [guidance]})
            prose = expanded.instructions
            expect(prose).to(contain("sample-rule-one"))
            expect(prose).to(contain("sketch-rule"))
            expect(prose).not_to(contain("spec-rule"))
            expect(
                prose.index("sketch-rule") < prose.index("call validate with this same guidance")
            ).to(equal(True))

        with it("should list validate as a tool to call after the artifact is written"):
            guidance = SamplePracticeGuidance(format="markdown", fidelity="sketch")
            expanded = _expanded_generate(self.action, {"guidance": [guidance]})
            expect("validate" in expanded.tools).to(equal(True))
            expect(expanded.instructions).to(contain("call validate with this same guidance"))

    with context("with no named session on the project"):
        with before.each:
            self.project = Path(tempfile.mkdtemp(prefix="cdd-generate-"))
            (self.project / ".git").mkdir()
            self.action = _made_for(self.project)

        with after.each:
            shutil.rmtree(self.project, ignore_errors=True)

        with it("should say where each format of the artifact is saved in the main session"):
            prose = _expanded_generate(self.action, {"guidance": ["stories-story-map"]}).instructions
            expect(prose).to(contain(f"{self.project.resolve().as_posix()}/.context/story-map.md"))

    with context("with a session open"):
        with before.each:
            self.project = Path(tempfile.mkdtemp(prefix="cdd-generate-"))
            (self.project / ".git").mkdir()
            sessions = Sessions(self.project)
            sessions.open(sessions.create("alpha", self.project))
            self.action = _made_for(self.project)

        with after.each:
            shutil.rmtree(self.project, ignore_errors=True)

        with it("should say where each format of the artifact is saved"):
            prose = _expanded_generate(self.action, {"guidance": ["stories-story-map"]}).instructions
            expect(prose).to(contain(f"{self.project.resolve().as_posix()}/.context/story-map.md"))

        with context("that generates a fidelity in a format its earlier fidelity has no file in, but another format it has"):
            with before.each:
                (self.project / ".context").mkdir(exist_ok=True)
                (self.project / ".context" / "story-map.drawio").write_text("<mxfile/>\n", encoding="utf-8")
                self.prose = _expanded_generate(self.action, {"guidance": "stories-scenarios format=markdown"}).instructions

            with it("should render the earlier fidelity into that format first"):
                expect(self.prose).to(contain("render the earlier fidelity stories-story-map into markdown"))

            with it("should render it from the earlier fidelity's file in the format it has"):
                expect(self.prose).to(contain("source drawio, and paths .context/story-map.drawio"))

        with context("that generates a fidelity in a format its earlier fidelity already has a file in"):
            with before.each:
                (self.project / ".context").mkdir(exist_ok=True)
                (self.project / ".context" / "story-map.drawio").write_text("<mxfile/>\n", encoding="utf-8")
                (self.project / ".context" / "story-map.md").write_text("# Story map\n", encoding="utf-8")
                self.prose = _expanded_generate(self.action, {"guidance": "stories-scenarios format=markdown"}).instructions

            with it("should render nothing first"):
                expect(self.prose).not_to(contain("render the earlier fidelity"))

        with context("that an MCP call names a guidance slug"):
            with before.each:
                self.action.generate(guidance="stories-story-map")

            with it("should log a generate line that names the practice and fidelity"):
                expect(_generate_line(self.project)).to(contain(" stories story_map "))

            # Generate only names the rules to follow; nothing has been checked, so the board must not count a validate.
            with it("should log no validate line"):
                expect(_logged_verbs(self.project)).not_to(contain("validate"))

            with it("should save no validation report"):
                expect((self.project / ".sessions" / "alpha" / "validation-reports").exists()).to(equal(False))

        # An agent acting on a command needs the session's folders, or it guesses where paths start and where files go.
        with context("that an agent runs it as an MCP command"):
            with before.each:
                server = McpServer(project=self.project)
                server.start(("cdd_guidance.actions.generate.generate:Generate",))
                self.reply = server.invoke_prompt("generate.generate", {"guidance": "stories-story-map"})

            with it("should name the session's session.json"):
                expect(self.reply).to(contain((self.project / ".sessions" / "alpha" / "session.json").resolve().as_posix()))

            with it("should say paths are named from the project's root"):
                expect(self.reply).to(contain(f"Name paths from the project's root, {self.project.resolve().as_posix()}, or absolute."))

            with it("should give the session.json the session works from"):
                expect(self.reply).to(contain('"name": "alpha"'))

            with it("should say where the listed practice writes"):
                expect(self.reply).to(contain(f"- stories: {self.project.resolve().as_posix()}/tests"))

        with context("that a command names the session it is for"):
            with before.each:
                other = self.project / ".sessions" / "beta"
                other.mkdir(parents=True)
                (self.project / "src").mkdir(exist_ok=True)
                (other / "session.json").write_text('{"name": "beta", "workpath": "' + (self.project / "src").as_posix() + '"}', encoding="utf-8")
                server = McpServer(project=self.project)
                server.start(("cdd_guidance.actions.generate.generate:Generate",))
                self.reply = server.invoke_prompt("generate.generate", {"guidance": "stories-story-map session=.sessions/beta/session.json"})

            with it("should describe that session, not the one open"):
                expect(self.reply).to(contain((self.project / ".sessions" / "beta" / "session.json").resolve().as_posix()))

            with it("should name that session's root"):
                expect(self.reply).to(contain(f"The session's root is {(self.project / 'src').resolve().as_posix()}"))

            # The output paths must come from the named session too, or the agent writes the artifact under the open session's root.
            with it("should save each format under that session's root"):
                expect(self.reply).to(contain(f"{(self.project / 'src').resolve().as_posix()}/.context/story-map.md"))

        with context("that the same cdd server has already generated once"):
            with before.each:
                server = McpServer(project=self.project)
                server.start(("cdd_guidance.actions.generate.generate:Generate",))
                server.invoke_prompt("generate.generate", {"guidance": "stories-story-map"})
                server.invoke_prompt("generate.generate", {"guidance": "stories-scenarios"})

            with it("should log a generate line for each call"):
                expect(_logged_verbs(self.project).count("generate")).to(equal(2))

        with context("that an MCP call names a guidance slug and its format in one string"):
            with before.each:
                self.action.generate(guidance="ux-ia format=drawio")

            with it("should log a generate line that names the practice, fidelity, and format"):
                expect(_generate_line(self.project)).to(contain(" ux ia drawio "))

    with context("with Bdd listed"):
        with it("should run generate using the practice default generate_output"):
            self.action.generate(["bdd"])
