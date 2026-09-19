"""Installer BDD — annotations, install tree, MCP, hooks, and deploy fixtures."""
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("practices", "harness", "tools", "actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be_true, contain, equal, expect, have_key, raise_error
from mamba import after, before, context, description, it

from installation.installer import Installer
from harness.guidance.fixtures.agentic_ops.agentic_ops import (
    SampleAgenticOps,
    SampleMcpOps,
)
from harness.guidance.fixtures.agentic_ops.hook_ops import SampleHookOps
from harness.guidance.fixtures.sample_tool.sample_tool_host import (
    SampleGuidance,
    SampleMcpGuidance,
    SampleMcpPractice,
    SamplePracticeGuidance,
    SamplePracticeWithFidelities,
)
from installation.hooks.hooks import Hook
from installation.hooks.prompt_log.prompt_log import PromptLog
from installation.mcp.mcp_server import McpServer
from agent_bdd.spec_helpers import repo_root_from
from harness.agent_tools.agent_tools import AgentToolSet

CAR = "practices.car.car:Car"
CAR_SKILL = ".cursor/skills/context_tools/car/car/SKILL.md"
CAR_ROAD_STORY = ".cursor/skills/context_tools/car/car-road-story/SKILL.md"
TRAVEL_TO = ".cursor/skills/actions/travel-to/SKILL.md"
CAR_START = ".cursor/skills/context_tools/car/car-start/SKILL.md"
CAR_INSPECT = ".cursor/skills/actions/car-inspect/SKILL.md"


def stage_invoke_commands(repo_root: Path) -> None:
    car = AgentToolSet.instantiate(CAR)
    car.load_fidelities_from_markdown()
    car_story = AgentToolSet.instantiate("actions.examples.car_story.car_story:CarStory")
    Installer("Cursor", path=repo_root / ".cursor").install([car, car_story])


with description("an operation annotated as a Cursor hook"):

    with context("that names a documented Cursor event"):
        with it("should store that event on the member"):
            for event in sorted(Hook.EVENTS):

                @Hook(event)
                def handler(self, payload: dict) -> dict:
                    return {}

                expect(handler._hook).to(equal(True))
                expect(handler._hook_name).to(equal(event))

    with context("that names an unknown event"):
        with it("should raise ValueError"):
            def bad_decoration():
                @Hook("notAnEvent")
                def handler(self, payload: dict) -> dict:
                    return {}

            expect(bad_decoration).to(raise_error(ValueError))

    with context("that omits the event"):
        with it("should raise ValueError"):
            def bare_hook():
                @Hook
                def handler(self, payload: dict) -> dict:
                    return {}

            expect(bare_hook).to(raise_error(ValueError))

# --- installation_spec.py ---
def _skill_names(tree: Path) -> set[str]:
    return {path.parent.name for path in tree.joinpath("skills").glob("*/SKILL.md")}


def _command_names(tree: Path) -> set[str]:
    folder = tree / "commands"
    if not folder.is_dir():
        return set()
    return {path.stem for path in folder.glob("*.md")}


def _skill_path(tree: Path, operation: str) -> Path | None:
    matches = list(tree.rglob(f"{operation}/SKILL.md"))
    return matches[0] if matches else None


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

        with it("should diagnose that the MCP host answers ping"):
            expect(self.mcp.diagnosis["ping"]).to(equal("pong"))


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
        with it("should write a skill file whose body is the overview"):
            skill = self.tree / "skills" / "sample-tool" / "SKILL.md"
            expect(skill.is_file()).to(equal(True))
            expect(skill.read_text(encoding="utf-8")).to(contain("sample preamble"))

        with it("should write one rules file whose body is the rules section markdown"):
            rule = self.tree / "rules" / "sample-tool.mdc"
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
        with it("should write the overview plus MCP invoke tail"):
            text = (self.tree / "skills" / "sample-tool" / "SKILL.md").read_text(encoding="utf-8")
            expect(text).to(contain("Use MCP tool:"))
            expect(text).to(contain("sample preamble"))
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
        with it("should write a skill file whose body is the overview"):
            text = (self.tree / "skills" / "sample-tool" / "SKILL.md").read_text(encoding="utf-8")
            expect(text).to(contain("sample preamble"))

        with it("should write one practice guidance rules file whose body is the shared rules section"):
            expect((self.tree / "rules" / "sample-tool.mdc").is_file()).to(equal(True))
            expect((self.tree / "rules" / "sample-tool.mdc").read_text(encoding="utf-8")).to(
                contain("sample rule one")
            )


with description("a context tool module with fidelity sections registered for deploy") as self:
    with before.each:
        self._tmp = tempfile.mkdtemp()
        self.tree = Path(self._tmp)
        self.tool = SamplePracticeWithFidelities(format="markdown")
        Installer(ide="Cursor", path=self.tree).install([self.tool])

    with after.each:
        shutil.rmtree(self._tmp, ignore_errors=True)

    with context("with a Cursor deploy output tree"):
        with it("should write one fidelity command file per fidelity whose body is the overview"):
            sketch = (self.tree / "commands" / "sample-tool-sketch.md").read_text(encoding="utf-8")
            expect(sketch).to(contain("sketch guidance body only"))

        with it("should list each fidelity MCP signature and a one-liner on the practice skill"):
            text = (self.tree / "skills" / "sample-tool" / "SKILL.md").read_text(encoding="utf-8")
            expect(text).to(contain("sample preamble"))
            expect(text).to(contain("sketch"))
            expect(text).to(contain("Use MCP tool:"))
            expect(text).to(contain("sample-tool-sketch()"))
            expect(text).not_to(contain("sketch guidance body only"))

        with it("should write one fidelity rules file whose body is that fidelity's rules section"):
            sketch_rules = self.tree / "rules" / "sample-tool-sketch.mdc"
            expect(sketch_rules.is_file()).to(equal(True))
            expect(sketch_rules.read_text(encoding="utf-8")).to(contain("sketch rule body"))


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
            expect((self.tree / "rules" / "sample-tool.mdc").is_file()).to(equal(True))
            expect((self.tree / "commands" / "sample-tool-sketch.md").is_file()).to(equal(True))
            expect((self.tree / "rules" / "sample-tool-spec.mdc").is_file()).to(equal(True))


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
                rule = (self.tree / "rules" / "sample-tool.mdc").read_text(encoding="utf-8")
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


_REPO = repo_root_from(__file__, parents=1)


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
            expect(text).to(contain("PYTHONPATH"))

        with it("should name the stdio server after the checkout so another folder named cdd does not hide it"):
            from installation.mcp.mcp_server import McpHost

            data = json.loads((self.tree / "mcp.json").read_text(encoding="utf-8"))
            expect(data["mcpServers"]).to(have_key(McpHost.server_key(_REPO_ROOT)))

    with context("that has been written by a deploy with no mcp-published members"):
        with before.each:
            self._tmp = tempfile.mkdtemp()
            self.tree = Path(self._tmp)
            Installer(ide="Cursor", path=self.tree).install([SampleAgenticOps()])

        with after.each:
            shutil.rmtree(self._tmp, ignore_errors=True)

        with it("should omit the MCP manifest file"):
            expect((self.tree / "mcp.json").exists()).to(equal(False))


with description("an installer that has finished writing the IDE path") as self:
    with before.each:
        self._tmp = tempfile.mkdtemp()
        self.tree = Path(self._tmp)
        self.installer = Installer(ide="Cursor", path=self.tree)

    with after.each:
        shutil.rmtree(self._tmp, ignore_errors=True)

    with context("with mcp-published operations installed"):
        with before.each:
            self.mcp = self.installer.install([SampleMcpOps()])

        with it("should diagnose that the MCP host answers ping"):
            expect(self.mcp.diagnosis["ping"]).to(equal("pong"))

        with it("should list the built-in health-check tool"):
            expect(self.mcp.diagnosis["tools"]).to(contain("cdd.ping"))

        with it("should diagnose that the hook server answers ping"):
            expect(self.installer._hook.diagnosis["ping"]).to(equal("pong"))

    with context("with no mcp-published members installed"):
        with before.each:
            self.mcp = self.installer.install([SampleAgenticOps()])

        with it("should diagnose that the MCP host answers ping"):
            expect(self.mcp.diagnosis["ping"]).to(equal("pong"))

        with it("should diagnose that the hook server answers ping"):
            expect(self.installer._hook.diagnosis["ping"]).to(equal("pong"))

    with context("with hook operations installed"):
        with before.each:
            self.mcp = self.installer.install([SampleHookOps()])

        with it("should diagnose that the hook server answers ping"):
            expect(self.installer._hook.diagnosis["ping"]).to(equal("pong"))

        with it("should list the installed hook event"):
            expect(self.installer._hook.diagnosis["events"]).to(contain("stop"))


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


with description("an MCP server") as self:
    with context("that has started from practice guidance toolset refs"):
        with before.each:
            self.server = McpServer(repo=_REPO_ROOT)
            self.server.start(
                (
                    "practices.stories.stories:Stories",
                    "harness.guidance.guidance:FidelityGuidance",
                )
            )

        with it("should enroll nested fidelity instructions under the fidelity slug"):
            expect("stories-scenarios" in self.server.prompts).to(equal(True))


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
            expect(command).to(contain("installation/hooks/hook_server.py"))

        with it("should write the skill file for the skill-annotated operation"):
            skill_files = [
                path
                for path in self.tree.rglob("SKILL.md")
                if not path.parent.name.startswith("hook-")
            ]
            expect(len(skill_files) > 0).to(equal(True))

        with it("should write handler refs for dispatch"):
            data = json.loads((self.tree / "hook-handlers.json").read_text(encoding="utf-8"))
            expect(data["handlers"][0]["event"]).to(equal("stop"))
            expect(data["handlers"][0]["operation"]).to(equal("auto_turn"))

    with context("that has been deployed with the prompt log hook toolset"):
        with before.each:
            self._tmp = tempfile.mkdtemp()
            self.tree = Path(self._tmp)
            Installer(ide="Cursor", path=self.tree).install([PromptLog()])

        with after.each:
            shutil.rmtree(self._tmp, ignore_errors=True)

        with it("should write hooks.json dispatch for beforeSubmitPrompt"):
            data = json.loads((self.tree / "hooks.json").read_text(encoding="utf-8"))
            expect(data["hooks"]).to(have_key("beforeSubmitPrompt"))

        with it("should not write a skill file for a hook-only operation"):
            hook_skills = list((self.tree / "skills").glob("hook-*/SKILL.md"))
            expect(hook_skills).to(equal([]))

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


with description("an installer that recorded files from a prior install") as self:
    with before.each:
        self._tmp = tempfile.mkdtemp()
        self.tree = Path(self._tmp)
        self.installer = Installer(ide="Cursor", path=self.tree)
        self.installer.install([SampleAgenticOps()])
        self.orphan = self.tree / "skills" / "stale-orphan" / "SKILL.md"
        self.orphan.parent.mkdir(parents=True, exist_ok=True)
        self.orphan.write_text("orphan", encoding="utf-8")

    with after.each:
        shutil.rmtree(self._tmp, ignore_errors=True)

    with context("whose clean operation runs directly"):
        with it("should remove only files recorded in install state"):
            prior_skill = _skill_path(self.tree, "generate")
            expect(prior_skill is not None).to(equal(True))
            removed = Installer(ide="Cursor", path=self.tree).clean()
            expect(len(removed) > 0).to(be_true)
            expect(prior_skill.is_file()).to(equal(False))
            expect(self.orphan.is_file()).to(equal(True))

    with context("that runs install again for a different toolset"):
        with before.each:
            self.installer.install([SampleGuidance(format="markdown")])

        with it("should remove tracked files from the prior install before writing"):
            expect(_skill_path(self.tree, "generate") is None).to(equal(True))
            expect(_skill_path(self.tree, "sample_tool") is not None).to(equal(True))

        with it("should leave untracked orphans in place"):
            expect(self.orphan.is_file()).to(equal(True))


with description("an installer that recorded an MCP host from a prior install") as self:
    with before.each:
        self._tmp = tempfile.mkdtemp()
        self.tree = Path(self._tmp)
        Installer(ide="Cursor", path=self.tree).install([SampleMcpOps()])

    with after.each:
        shutil.rmtree(self._tmp, ignore_errors=True)

    with context("whose clean operation runs directly"):
        with it("should keep the MCP manifest so Cursor can respawn the host"):
            Installer(ide="Cursor", path=self.tree).clean()
            expect((self.tree / "mcp.json").is_file()).to(equal(True))


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

    with it("should record install and clean as MCP operations"):
        names = [op.mcp_name for op in self.mcp.mcp_operations]
        expect(names).to(contain("installer.install"))
        expect(names).to(contain("installer.clean"))


with description("the installer import path") as self:
    with before.each:
        self.repo = Path(__file__).resolve().parents[1]
        Installer.ensure_import_path(self.repo)

    with it("should put catalog folders on sys.path so short catalog imports resolve"):
        import agent_tools
        import guidance_actions

        expect("agent_toolset" in dir(agent_tools)).to(equal(True))
        expect(guidance_actions.GuidanceAction.__name__).to(equal("GuidanceAction"))
        expect(Installer.pythonpath(self.repo)).to(contain("actions"))
        expect(Installer.pythonpath(self.repo)).not_to(contain(str(self.repo / "installation") + os.sep))

    with it("should not collect toolsets under examples folders"):
        refs = Installer(ide="Cursor", path=self.repo / ".cursor", repo=self.repo).collect_toolsets()
        expect(any("examples" in ref.replace("\\", "/") for ref in refs)).to(equal(False))
        expect(any("car_story" in ref for ref in refs)).to(equal(False))


def _skill_tool(name: str):
    def _fn(self):
        return None

    _fn._skill = True
    return type("Tool", (), {"name": name, "deploy_name": name, "install_to_skill": True, "callable": _fn})()


with description("markdown skill paths for a kit with several skill operations"):
    with it("should write each skill as a peer folder named for the operation"):
        from installation.harness_files.harness_files import MarkdownInstallation

        writer = MarkdownInstallation("Cursor", Path("."), "skill")
        tools = {"validate": _skill_tool("validate"), "createRule": _skill_tool("createRule")}
        toolset = type("Kit", (), {"install_folder": Path("actions/validate"), "tools": tools})()
        expect(
            writer.relative_path("skill", toolset, tools["validate"].callable, "validate").as_posix()
        ).to(equal("skills/actions/validate/validate/SKILL.md"))
        expect(
            writer.relative_path("skill", toolset, tools["createRule"].callable, "createRule").as_posix()
        ).to(equal("skills/actions/validate/create-rule/SKILL.md"))

    with it("should keep a single matching operation at the kit folder"):
        from installation.harness_files.harness_files import MarkdownInstallation

        writer = MarkdownInstallation("Cursor", Path("."), "skill")
        tools = {"generate": _skill_tool("generate")}
        toolset = type("Kit", (), {"install_folder": Path("actions/generate"), "tools": tools})()
        expect(
            writer.relative_path("skill", toolset, tools["generate"].callable, "generate").as_posix()
        ).to(equal("skills/actions/generate/SKILL.md"))

    with it("should name a single unmatched operation for the operation not the kit folder"):
        from installation.harness_files.harness_files import MarkdownInstallation

        writer = MarkdownInstallation("Cursor", Path("."), "skill")
        tools = {"grill": _skill_tool("grill")}
        toolset = type("Kit", (), {"install_folder": Path("actions/grill_context"), "tools": tools})()
        expect(
            writer.relative_path("skill", toolset, tools["grill"].callable, "grill").as_posix()
        ).to(equal("skills/actions/grill_context/grill/SKILL.md"))


with description("markdown skill paths for a fidelity nested under a practice"):
    with it("should keep the practice folder and name the leaf practice-fidelity"):
        from installation.harness_files.harness_files import MarkdownInstallation

        writer = MarkdownInstallation("Cursor", Path("."), "skill")
        tools = {"instructions": _skill_tool("instructions")}
        practice = type("Practice", (), {"slug": "stories"})()
        toolset = type(
            "Fidelity",
            (),
            {
                "install_folder": Path("practices/stories/scenarios"),
                "tools": tools,
                "practice_guidance": practice,
                "slug": "stories-scenarios",
            },
        )()
        expect(
            writer.relative_path(
                "skill", toolset, tools["instructions"].callable, "instructions"
            ).as_posix()
        ).to(equal("skills/practices/stories/stories-scenarios/SKILL.md"))


def _write_skill_tool(name: str, overview: str):
    def _fn(self):
        return overview

    _fn.__name__ = name
    _fn._skill = True
    host = type(
        "Host",
        (),
        {
            "install_folder": Path("sample-tool"),
            "overview": overview,
            name: overview,
            "tools": {},
        },
    )()
    return type(
        "Tool",
        (),
        {
            "kind": "instructions",
            "name": name,
            "deploy_name": name,
            "callable": _fn,
            "toolset": host,
            "docstring": overview,
        },
    )()


with description("markdown skill front matter") as self:
    with before.each:
        self._tmp = tempfile.mkdtemp()
        self.tree = Path(self._tmp)

    with after.each:
        shutil.rmtree(self._tmp, ignore_errors=True)

    with it("should put the skill folder name and overview in YAML front matter"):
        from installation.harness_files.harness_files import MarkdownInstallation

        writer = MarkdownInstallation("Cursor", self.tree, "skill")
        writer.write(_write_skill_tool("instructions", "sample preamble"))
        text = (self.tree / "skills" / "sample-tool" / "SKILL.md").read_text(encoding="utf-8")
        front = text.split("---", 2)[1]
        expect(text.startswith("---\n")).to(equal(True))
        expect(front).to(contain("name: sample-tool"))
        expect(front).to(contain("description:"))
        expect(front).to(contain("sample preamble"))
        expect(text).to(contain("sample preamble"))

    with it("should keep the MCP invoke tail out of the skill description"):
        from installation.harness_files.harness_files import MarkdownInstallation

        overview = "sample preamble"
        writer = MarkdownInstallation("Cursor", self.tree, "skill")
        text = writer._skill_front_matter(
            "sample-tool",
            writer._skill_overview(
                type("Host", (), {"overview": overview})(),
                [overview, "Use MCP tool: `sample-tool.instructions()`"],
            ),
        )
        expect(text).to(contain("sample preamble"))
        expect(text).not_to(contain("Use MCP tool:"))


with description("markdown rules front matter"):
    with it("should copy alwaysApply and globs from rules.appliesTo"):
        from installation.harness_files.harness_files import MarkdownInstallation
        from actions.scan.rule import AppliesTo, RulesCollection

        host = type(
            "Host",
            (),
            {"rules": RulesCollection(applies_to=AppliesTo(always_apply=False, globs="**/*spec.py"))},
        )()
        writer = MarkdownInstallation("Cursor", Path("."), "rules")
        text = writer._rules_front_matter(
            "Whenever you write specs. Follow these rules.\n\n- **a** — b",
            host,
        )
        expect(text).to(contain("alwaysApply: false"))
        expect(text).to(contain("globs: **/*spec.py"))
        expect(text).to(contain("Whenever you write specs"))
