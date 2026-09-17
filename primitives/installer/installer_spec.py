"""Installer BDD — annotations, install tree, MCP, hooks, and deploy fixtures."""
import json
import shutil
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("practices", "primitives", "utilities", "actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be_true, contain, equal, expect, have_key, raise_error
from mamba import after, before, context, description, it

from primitives.guidance.fixtures.agentic_ops.agentic_ops import (
    SampleAgenticOps,
    SampleMcpOps,
)
from primitives.guidance.fixtures.agentic_ops.hook_ops import SampleHookOps
from primitives.guidance.fixtures.sample_tool.sample_tool_host import (
    SampleGuidance,
    SampleMcpGuidance,
    SampleMcpPractice,
    SamplePracticeGuidance,
    SamplePracticeWithFidelities,
)
from primitives.installer import Installer
from primitives.hooks.hooks import hook
from primitives.mcp.mcp_server import McpServer
from agent_bdd.spec_helpers import repo_root_from
from primitives.agent_tools.agent_tools import AgentToolSet

CAR = "practices.car.car:Car"
CAR_SKILL = ".cursor/skills/context_tools/car/car/SKILL.md"
CAR_ROAD_STORY = ".cursor/skills/context_tools/car/car-road-story/SKILL.md"
TRAVEL_TO = ".cursor/skills/actions/travel-to/SKILL.md"
CAR_START = ".cursor/skills/context_tools/car/car-start/SKILL.md"
CAR_INSPECT = ".cursor/skills/actions/car-inspect/SKILL.md"


def stage_invoke_commands(repo_root: Path) -> None:
    car = AgentToolSet.instantiate(CAR)
    car.load_fidelities_from_markdown()
    car_story = AgentToolSet.instantiate("car_story.car_story:CarStory")
    Installer("Cursor", path=repo_root / ".cursor").install([car, car_story])


with description("an operation annotated as a Cursor hook"):

    with context("that names a documented Cursor event"):
        with it("should store that event on the member"):
            for event in sorted(hook.EVENTS):

                @hook(event)
                def handler(self, payload: dict) -> dict:
                    return {}

                expect(handler._hook).to(equal(True))
                expect(handler._hook_name).to(equal(event))

    with context("that names an unknown event"):
        with it("should raise ValueError"):
            def bad_decoration():
                @hook("notAnEvent")
                def handler(self, payload: dict) -> dict:
                    return {}

            expect(bad_decoration).to(raise_error(ValueError))

    with context("that omits the event"):
        with it("should raise ValueError"):
            def bare_hook():
                @hook
                def handler(self, payload: dict) -> dict:
                    return {}

            expect(bare_hook).to(raise_error(ValueError))

    with context("that is marked always"):
        with it("should store always on the member"):
            @hook("preToolUse", always=True)
            def handler(self, payload: dict) -> dict:
                return {}

            expect(handler._hook_always).to(equal(True))


# --- installation_spec.py ---
def _skill_names(tree: Path) -> set[str]:
    return {path.parent.name for path in tree.joinpath("skills").glob("*/SKILL.md")}


def _command_names(tree: Path) -> set[str]:
    folder = tree / "commands"
    if not folder.is_dir():
        return set()
    return {path.stem for path in folder.glob("*.md")}


with description("a bare agentic toolset registered for deploy") as self:
    with before.each:
        self._tmp = tempfile.mkdtemp()
        self.tree = Path(self._tmp)
        self.installer = Installer(ide="Cursor", path=self.tree)
        self.installer.install([SampleAgenticOps()])

    with after.each:
        shutil.rmtree(self._tmp, ignore_errors=True)

    with context("with a Cursor deploy output tree"):
        with it("should write one skill file per agent-instructions operation marked for skill"):
            expect(_skill_names(self.tree)).to(contain("generate"))

        with it("should write one command file per agent-instructions operation marked for command"):
            expect(_command_names(self.tree)).to(contain("sketch"))

        with it(
            "should write a skill or command for an agent-tool operation only when that operation is also marked skill or command"
        ):
            expect(_skill_names(self.tree)).to(contain("listed"))
            ping = list(self.tree.rglob("*ping*"))
            expect(ping).to(equal([]))

        with it("should not write a context guidance skill or fidelity commands"):
            expect(_skill_names(self.tree)).not_to(contain("sample_tool"))
            expect(_command_names(self.tree)).not_to(contain("sample-ops-behavior"))

    with context("with a deploy output tree"):
        with it(
            "should render skill and command bodies from the tool docstring"
        ):
            skill_text = (self.tree / "skills" / "generate" / "SKILL.md").read_text(encoding="utf-8")
            command_text = (self.tree / "commands" / "sketch.md").read_text(encoding="utf-8")
            tool = SampleAgenticOps()
            generate_body = tool.tools["generate"].docstring
            sketch_body = tool.tools["sketch"].docstring
            expect(skill_text).to(contain(generate_body))
            expect(command_text).to(contain(sketch_body))
            expect(generate_body).to(contain("compound generate instructions"))


with description("a bare agentic toolset with mcp-published operations registered for deploy") as self:
    with before.each:
        self._tmp = tempfile.mkdtemp()
        self.tree = Path(self._tmp)
        self.installer = Installer(ide="Cursor", path=self.tree)
        self.mcp = self.installer.install([SampleMcpOps()])

    with after.each:
        shutil.rmtree(self._tmp, ignore_errors=True)

    with context("with a deployed skill file for an mcp-published agent-instructions operation"):
        with it("should still write the skill file so there is a slash command"):
            expect((self.tree / "skills" / "generate" / "SKILL.md").is_file()).to(equal(True))

        with it("should put the tool docstring at the top of the file"):
            text = (self.tree / "skills" / "generate" / "SKILL.md").read_text(encoding="utf-8")
            expect(text).to(contain("full generate instructions that must not appear"))

        with it("should place one MCP invoke tail after the docstring"):
            text = (self.tree / "skills" / "generate" / "SKILL.md").read_text(encoding="utf-8")
            expect(text).to(contain("Use MCP tool:"))

        with it(
            "should name the tool as the toolset slug and operation with the method parameter signature in backticks"
        ):
            text = (self.tree / "skills" / "generate" / "SKILL.md").read_text(encoding="utf-8")
            expect(text).to(contain("`sample-mcp.generate"))

        with it("should not append the CLI tools.ps1 invoke fence"):
            text = (self.tree / "skills" / "generate" / "SKILL.md").read_text(encoding="utf-8")
            expect(text).not_to(contain("tools.ps1"))

    with context("with a deployed command file for an mcp-published command operation"):
        with it("should write the tool docstring plus MCP invoke tail"):
            text = (self.tree / "commands" / "sketch.md").read_text(encoding="utf-8")
            expect(text).to(contain("Use MCP tool:"))
            expect(text).to(contain("full sketch instructions that must not appear"))

    with context("with a deploy output tree for tools whose members are annotated mcp"):
        with it("should record each mcp-published operation for server enrollment"):
            names = [op.mcp_name for op in self.mcp.mcp_operations]
            expect(names).to(contain("sample-mcp.generate"))
            expect(names).to(contain("sample-mcp.sketch"))

        with it("should not bind tool handlers during deploy"):
            server_bound = getattr(self.mcp, "_bound", False)
            expect(server_bound).to(equal(False))


with description("context guidance registered for deploy") as self:
    with before.each:
        self._tmp = tempfile.mkdtemp()
        self.tree = Path(self._tmp)
        self.tool = SampleGuidance(format="markdown")
        self.installer = Installer(ide="Cursor", path=self.tree)
        self.installer.install([self.tool])

    with after.each:
        shutil.rmtree(self._tmp, ignore_errors=True)

    with context("with a Cursor deploy output tree"):
        with it("should write a skill file whose body is the instructions docstring"):
            skill = self.tree / "skills" / "sample-tool" / "SKILL.md"
            expect(skill.is_file()).to(equal(True))
            expect(skill.read_text(encoding="utf-8")).to(contain("context"))

        with it("should write one rules file per rule slug"):
            rule = self.tree / "rules" / "sample-rule-one.mdc"
            expect(rule.is_file()).to(equal(True))
            expect(rule.read_text(encoding="utf-8")).to(contain("sample rule one"))


with description("context guidance with mcp-published guidance registered for deploy") as self:
    with before.each:
        self._tmp = tempfile.mkdtemp()
        self.tree = Path(self._tmp)
        self.installer = Installer(ide="Cursor", path=self.tree)
        self.mcp = self.installer.install([SampleMcpGuidance(format="markdown")])

    with after.each:
        shutil.rmtree(self._tmp, ignore_errors=True)

    with context("with a deployed practice skill when guidance is mcp-published"):
        with it("should write the instructions docstring plus MCP invoke tail"):
            text = (self.tree / "skills" / "sample-tool" / "SKILL.md").read_text(encoding="utf-8")
            expect(text).to(contain("Use MCP tool:"))
            expect(text).to(contain("context"))
            expect(text).not_to(contain("active format template body for sample tool"))

    with context("with a deploy output tree for tools whose members are annotated mcp"):
        with it("should record each mcp-published operation for server enrollment"):
            names = [op.mcp_name for op in self.mcp.mcp_operations]
            expect(names).to(contain("sample-tool.instructions"))

        with it("should not bind tool handlers during deploy"):
            expect(getattr(self.mcp, "_bound", False)).to(equal(False))


with description("a context tool module with shared contexts format registered for deploy") as self:
    with before.each:
        self._tmp = tempfile.mkdtemp()
        self.tree = Path(self._tmp)
        self.tool = SamplePracticeGuidance(format="markdown")
        self.installer = Installer(ide="Cursor", path=self.tree)
        self.installer.install([self.tool])

    with after.each:
        shutil.rmtree(self._tmp, ignore_errors=True)

    with context("with a Cursor deploy output tree"):
        with it("should write a skill file whose body is the instructions docstring"):
            text = (self.tree / "skills" / "sample-tool" / "SKILL.md").read_text(encoding="utf-8")
            expect(text).to(contain("context"))

        with it("should write one practice guidance rules file per practice guidance rule slug"):
            expect((self.tree / "rules" / "sample-rule-one.mdc").is_file()).to(equal(True))


with description("a context tool module with fidelity sections registered for deploy") as self:
    with before.each:
        self._tmp = tempfile.mkdtemp()
        self.tree = Path(self._tmp)
        self.tool = SamplePracticeWithFidelities(format="markdown")
        Installer(ide="Cursor", path=self.tree).install([self.tool])

    with after.each:
        shutil.rmtree(self._tmp, ignore_errors=True)

    with context("with a Cursor deploy output tree"):
        with it("should write one fidelity command file per fidelity whose body is the instructions docstring"):
            sketch = (self.tree / "commands" / "sample-tool-sketch.md").read_text(encoding="utf-8")
            expect(sketch).to(contain("context"))

        with it("should write one fidelity rules file per fidelity rule slug"):
            expect((self.tree / "rules" / "sketch-rule.mdc").is_file()).to(equal(True))


with description("a context tool module with fidelities and assembly registered for deploy") as self:
    with before.each:
        self._tmp = tempfile.mkdtemp()
        self.tree = Path(self._tmp)
        self.tool = SamplePracticeWithFidelities(format="markdown")
        Installer(ide="Cursor", path=self.tree).install([self.tool])

    with after.each:
        shutil.rmtree(self._tmp, ignore_errors=True)

    with context("with a Cursor deploy output tree"):
        with it("should emit the practice skill, practice rules, fidelity commands, and fidelity rules in one pass"):
            expect((self.tree / "skills" / "sample-tool" / "SKILL.md").is_file()).to(equal(True))
            expect((self.tree / "rules" / "sample-rule-one.mdc").is_file()).to(equal(True))
            expect((self.tree / "commands" / "sample-tool-sketch.md").is_file()).to(equal(True))
            expect((self.tree / "rules" / "spec-rule.mdc").is_file()).to(equal(True))


with description("practice guidance that has been deployed") as self:
    with before.each:
        self._tmp = tempfile.mkdtemp()
        self.tree = Path(self._tmp)
        Installer(ide="Cursor", path=self.tree).install(
            [SamplePracticeGuidance(format="markdown")]
        )

    with after.each:
        shutil.rmtree(self._tmp, ignore_errors=True)

    with context("with members that are not annotated mcp"):
        with context("with deployed skill command and rules bodies"):
            with it("should not append a YAML CLI invoke fence"):
                skill = (self.tree / "skills" / "sample-tool" / "SKILL.md").read_text(encoding="utf-8")
                rule = (self.tree / "rules" / "sample-rule-one.mdc").read_text(encoding="utf-8")
                for text in (skill, rule):
                    expect(text).not_to(contain("tools.ps1"))
                    expect(text).not_to(contain("toolset:"))


with description("practice guidance that has been deployed for VS Code") as self:
    with before.each:
        self._tmp = tempfile.mkdtemp()
        self.tree = Path(self._tmp)
        Installer(ide="VS Code", path=self.tree).install(
            [SamplePracticeWithFidelities(format="markdown")]
        )

    with after.each:
        shutil.rmtree(self._tmp, ignore_errors=True)

    with context("with a VS Code deploy output tree"):
        with it("should write fidelity command files under github prompts not under cursor commands"):
            expect((self.tree / "prompts" / "sample-tool-sketch.md").is_file()).to(equal(True))


_REPO = repo_root_from(__file__, parents=2)


with description("harness deploy for car invoke BDD"):
    with context("after install"):
        with it("should write the car context tool skill"):
            stage_invoke_commands(_REPO)
            skill = _REPO / CAR_SKILL
            expect(skill.is_file()).to(be_true)
            body = skill.read_text(encoding="utf-8")
            expect("AskQuestion" in body).to(be_true)
            expect("@car-road_story" in body or "road_story" in body).to(be_true)
            expect("tools.ps1" in body).to(equal(False))
            expect("toolset:" in body).to(equal(False))

        with it("should write fidelity and action command prompts"):
            stage_invoke_commands(_REPO)
            expect((_REPO / CAR_ROAD_STORY).is_file()).to(be_true)
            expect((_REPO / TRAVEL_TO).is_file()).to(be_true)
            expect((_REPO / CAR_START).is_file()).to(be_true)
            expect((_REPO / CAR_INSPECT).is_file()).to(be_true)

        with it("should not embed YAML CLI invoke fences in deployed command bodies"):
            stage_invoke_commands(_REPO)
            for path in (CAR_ROAD_STORY, TRAVEL_TO, CAR_START, CAR_INSPECT):
                text = (_REPO / path).read_text(encoding="utf-8")
                expect("tools.ps1" in text).to(equal(False))
                expect("toolset:" in text).to(equal(False))


# --- mcp_server_spec.py ---
with description("an MCP manifest file") as self:
    with context("that has been written by a deploy whose walked members are annotated mcp"):
        with before.each:
            self._tmp = tempfile.mkdtemp()
            self.tree = Path(self._tmp)
            Installer(ide="Cursor", path=self.tree).install([SampleMcpOps()])

        with after.each:
            shutil.rmtree(self._tmp, ignore_errors=True)

        with it("should list stdio server command and comma-separated toolset refs for walked classes"):
            text = (self.tree / "mcp.json").read_text(encoding="utf-8")
            expect(text).to(contain("python"))
            expect(text).to(contain("--toolsets"))
            expect(text).to(contain("SampleMcpOps"))

    with context("that has been written by a deploy with no mcp-published members"):
        with before.each:
            self._tmp = tempfile.mkdtemp()
            self.tree = Path(self._tmp)
            Installer(ide="Cursor", path=self.tree).install([SampleAgenticOps()])

        with after.each:
            shutil.rmtree(self._tmp, ignore_errors=True)

        with it("should omit the MCP manifest file"):
            expect((self.tree / "mcp.json").exists()).to(equal(False))


with description("a bare agentic toolset with an agent-tool operation annotated for mcp") as self:
    with before.each:
        self._tmp = tempfile.mkdtemp()
        self.tree = Path(self._tmp)
        self.tool = SampleMcpOps()
        self.installer = Installer(ide="Cursor", path=self.tree)
        self.mcp = self.installer.install([self.tool])
        self.server = McpServer()
        self.server.bind_from(self.mcp)

    with after.each:
        shutil.rmtree(self._tmp, ignore_errors=True)

    with context("that has been deployed"):
        with context("with an MCP server started from manifest toolset refs written during that deploy"):
            with it("should enroll that operation as a prompt under the mcp name for generate"):
                expect("sample-mcp.generate" in self.server.prompts).to(equal(True))

            with it("should enroll from mcp operations recorded at deploy not from a second annotation scan on the class"):
                expect(len(self.mcp.mcp_operations) > 0).to(equal(True))

            with context("with a prompts call for that enrolled mcp name"):
                with it("should return the orchestration result from that operation"):
                    result = self.server.invoke_prompt("sample-mcp.generate")
                    expect(str(result)).to(contain("full generate instructions"))


with description("context guidance with guidance annotated for mcp") as self:
    with before.each:
        self._tmp = tempfile.mkdtemp()
        self.installer = Installer(ide="Cursor", path=self._tmp)
        self.tool = SampleMcpGuidance(format="markdown")
        self.mcp = self.installer.install([self.tool])
        self.server = McpServer()
        self.server.bind_from(self.mcp)

    with after.each:
        shutil.rmtree(self._tmp, ignore_errors=True)

    with context("that has been deployed"):
        with context("with an MCP server started from manifest toolset refs written during that deploy"):
            with context("with a prompts call for that enrolled mcp name"):
                with it("should return the same compound instructions string the read path assembles"):
                    result = self.server.invoke_prompt("sample-tool.instructions")
                    expect(result).to(equal(self.tool.instructions))


with description("practice guidance with guidance annotated for mcp") as self:
    with before.each:
        self._tmp = tempfile.mkdtemp()
        self.installer = Installer(ide="Cursor", path=self._tmp)
        self.tool = SampleMcpPractice(format="markdown")
        self.mcp = self.installer.install([self.tool])
        self.server = McpServer()
        self.server.bind_from(self.mcp)

    with after.each:
        shutil.rmtree(self._tmp, ignore_errors=True)

    with context("that has been deployed"):
        with context("with an MCP server started from manifest toolset refs written during that deploy"):
            with context("with a prompts call for the practice skill enrolled mcp name"):
                with it("should return practice guidance instructions as the prompt source"):
                    result = self.server.invoke_prompt("sample-tool.instructions")
                    expect(result).to(equal(self.tool.instructions))


with description("fidelity guidance with guidance annotated for mcp") as self:
    with before.each:
        self._tmp = tempfile.mkdtemp()
        self.installer = Installer(ide="Cursor", path=self._tmp)
        self.tool = SampleMcpPractice(format="markdown")
        self.mcp = self.installer.install([self.tool])
        self.server = McpServer()
        self.server.bind_from(self.mcp)

    with after.each:
        shutil.rmtree(self._tmp, ignore_errors=True)

    with context("that has been deployed"):
        with context("with an MCP server started from manifest toolset refs written during that deploy"):
            with context("with a prompts call for that fidelity enrolled mcp name"):
                with it("should return fidelity guidance instructions as the prompt source"):
                    names = list(self.server.prompts)
                    expect(any("instructions" in n for n in names)).to(equal(True))


# --- hook_installation_spec.py ---
with description("a Cursor hooks config") as self:
    with context("that has been deployed with hook sources in the walk"):
        with before.each:
            self._tmp = tempfile.mkdtemp()
            self.tree = Path(self._tmp)
            Installer(ide="Cursor", path=self.tree).install([SampleHookOps()])

        with after.each:
            shutil.rmtree(self._tmp, ignore_errors=True)

        with it("should write hooks.json dispatch for each registered hook event"):
            data = json.loads((self.tree / "hooks.json").read_text(encoding="utf-8"))
            expect(data["version"]).to(equal(1))
            expect(data["hooks"]).to(have_key("stop"))
            command = data["hooks"]["stop"][0]["command"]
            expect(command).to(contain("primitives/hooks/dispatch.py"))

        with it("should write hook skill files for hook-published operations"):
            expect((self.tree / "skills" / "hook-auto_turn" / "SKILL.md").is_file()).to(
                equal(True)
            )

        with it("should write handler refs for dispatch"):
            data = json.loads((self.tree / "hook-handlers.json").read_text(encoding="utf-8"))
            expect(data["handlers"][0]["event"]).to(equal("stop"))
            expect(data["handlers"][0]["operation"]).to(equal("auto_turn"))

    with context("that has been partially deployed with no hook sources emitted"):
        with before.each:
            self._tmp = tempfile.mkdtemp()
            self.tree = Path(self._tmp)
            prior = self.tree / "hooks.json"
            prior.write_text(
                '{"version": 1, "hooks": {"stop": [{"command": "keep-me"}]}}\n',
                encoding="utf-8",
            )
            Installer(ide="Cursor", path=self.tree).install([SampleAgenticOps()])

        with after.each:
            shutil.rmtree(self._tmp, ignore_errors=True)

        with it("should leave hooks manifest unchanged from a prior full deploy"):
            text = (self.tree / "hooks.json").read_text(encoding="utf-8")
            expect(text).to(contain("keep-me"))


with description("the installer toolset installing itself") as self:
    with before.each:
        self._tmp = tempfile.mkdtemp()
        self.tree = Path(self._tmp)
        self.mcp = Installer(ide="Cursor", path=self.tree).install(
            [Installer(ide="Cursor", path=self.tree)]
        )

    with after.each:
        shutil.rmtree(self._tmp, ignore_errors=True)

    with it("should write an install skill that names the MCP tool"):
        text = (self.tree / "skills" / "install" / "SKILL.md").read_text(encoding="utf-8")
        expect(text).to(contain("Use MCP tool:"))
        expect(text).to(contain("installer.install"))

    with it("should record install as an MCP operation"):
        names = [op.mcp_name for op in self.mcp.mcp_operations]
        expect(names).to(contain("installer.install"))
