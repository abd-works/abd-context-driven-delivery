"""Installer BDD — annotations, install tree, MCP, hooks, and deploy fixtures."""
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from harness.installation.installer import Installer

Installer(repo=_REPO_ROOT).ensure_import_path()

from expects import be_true, contain, equal, expect, have_key, raise_error
from mamba import after, before, context, description, it
from harness.guidance.fixtures.agentic_ops.agentic_ops import (
    SampleAgenticOps,
    SampleMcpOps,
)
from harness.guidance.fixtures.agentic_ops.hook_ops import SampleHookOps
from harness.guidance.fixtures.sample_tool.sample_tool_host import (
    SampleGuidance,
    SamplePracticeGuidance,
    SamplePracticeWithFidelities,
)
from harness.hooks.hooks import Hook
from harness.mcp.mcp_server import McpServer




class HookDecoration:
    def unknown_event(self) -> None:
        @Hook("notAnEvent")
        def handler(self, payload: dict) -> dict:
            return {}

    def omitted_event(self) -> None:
        @Hook
        def handler(self, payload: dict) -> dict:
            return {}


class InstalledTree:
    def __init__(self, tree: Path) -> None:
        self.tree = tree

    def skill_names(self) -> set[str]:
        skills = self.tree / "skills"
        if not skills.is_dir():
            return set()
        return {path.parent.name for path in skills.rglob("SKILL.md")}

    def command_names(self) -> set[str]:
        folder = self.tree / "commands"
        if not folder.is_dir():
            return set()
        return {path.stem for path in folder.rglob("*.md")}

    def name_keys(self, name: str) -> set[str]:
        return {name, name.replace("-", "_"), name.replace("_", "-")}

    def skill_path(self, operation: str) -> Path | None:
        wanted = self.name_keys(operation)
        for path in self.tree.rglob("SKILL.md"):
            if path.parent.name in wanted:
                return path
        return None

    def command_path(self, stem: str) -> Path | None:
        folder = self.tree / "commands"
        if not folder.is_dir():
            return None
        wanted = self.name_keys(stem)
        for path in folder.rglob("*.md"):
            if path.stem in wanted:
                return path
        return None

    def rule_path(self, name: str) -> Path | None:
        folder = self.tree / "rules"
        if not folder.is_dir():
            return None
        wanted = self.name_keys(name)
        for path in folder.rglob("*"):
            if path.is_file() and path.name in wanted:
                return path
        return None

    def prompt_path(self, stem: str) -> Path | None:
        folder = self.tree / "prompts"
        if not folder.is_dir():
            return None
        wanted = self.name_keys(stem)
        for path in folder.rglob("*.md"):
            if path.stem in wanted:
                return path
        return None


def _write_install_log(path: Path, skills: list[str]) -> None:
    path.write_text(
        json.dumps(
            {
                "installs": [
                    {
                        "color": "green",
                        "skill": {"count": len(skills), "items": skills},
                        "diagnostics": [],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )


def _last_logged_install(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))["installs"][-1]


def _skill_tool(name: str):
    def _fn(self):
        return None

    _fn._skill = True
    return type("Tool", (), {"name": name, "deploy_name": name, "install_to_skill": True, "callable": _fn})()


# (E) Install CDD Tools
# (E) Install Agent Toolset
with description("an agent toolset") as self:
    with context("with operations annotated for installation"):
        # (S) Installer --> Generate skills and commands from Agent Toolset
        with context("that are annotated as skills and commands"):
            with before.each:
                self._tmp = tempfile.mkdtemp()
                self.tree = Path(self._tmp)
                self.installer = Installer(ide="Cursor", path=self.tree)
                self.installer.install([SampleAgenticOps()])

            with after.each:
                shutil.rmtree(self._tmp, ignore_errors=True)

            with context("with operations that are annotated as skills"):
                with it("should write a skill file for each of them"):
                    names = InstalledTree(self.tree).skill_names()
                    expect(names).to(contain("generate"))
                    expect(names).to(contain("listed"))

                with it("should write the operation's instructions on the skill"):
                    skill_text = InstalledTree(self.tree).skill_path("generate").read_text(encoding="utf-8")
                    expect(skill_text).to(contain(SampleAgenticOps().tools["generate"].docstring))

            with context("with operations that are annotated as commands"):
                with it("should write a command file for each of them"):
                    expect(InstalledTree(self.tree).command_names()).to(contain("sketch"))

                with it("should write the operation's instructions on the command"):
                    command_text = InstalledTree(self.tree).command_path("sketch").read_text(encoding="utf-8")
                    assembled = SampleAgenticOps().tools["sketch"].docstring
                    expect(command_text).to(contain(assembled))
                    expect(command_text).not_to(contain("Shell tool"))

            with context("with operations that are not annotated"):
                with it("should not write a skill or command"):
                    expect(list(self.tree.rglob("*ping*"))).to(equal([]))

            with it("should not write a Guidance or practice guidance skill or fidelity commands"):
                expect(InstalledTree(self.tree).skill_names()).not_to(contain("sample-tool"))
                expect(InstalledTree(self.tree).command_names()).not_to(contain("sample-ops-behavior"))

            with it("should not write an MCP manifest"):
                expect((self.tree / "mcp.json").exists()).to(equal(False))

            with context("also annotated for MCP"):
                with before.each:
                    self._branch_tmp = tempfile.mkdtemp()
                    self.tree = Path(self._branch_tmp)
                    self.installer = Installer(ide="Cursor", path=self.tree)
                    self.mcp = self.installer.install([SampleMcpOps()])

                with after.each:
                    shutil.rmtree(self._branch_tmp, ignore_errors=True)

                # (S) Installer --> Generate Skills and Commands With MCP Calls
                with context("with a skill file for an operation annotated for MCP"):
                    with it("should still write the skill file so there is a slash command"):
                        expect(InstalledTree(self.tree).skill_path("generate").is_file()).to(equal(True))

                    with it("should put the tool docstring at the top of the file"):
                        text = InstalledTree(self.tree).skill_path("generate").read_text(encoding="utf-8")
                        expect(text).to(contain("full generate instructions that must not appear"))

                    with it("should place one MCP invoke tail after the docstring"):
                        text = InstalledTree(self.tree).skill_path("generate").read_text(encoding="utf-8")
                        expect(text).to(contain("Use MCP tool:"))

                    with it(
                        "should name the tool as the toolset slug and operation with the method parameter signature in backticks"
                    ):
                        text = InstalledTree(self.tree).skill_path("generate").read_text(encoding="utf-8")
                        expect(text).to(contain("`sample-mcp.generate"))

                    with it("should write the tool docstring plus MCP invoke tail on the command file"):
                        text = InstalledTree(self.tree).command_path("sketch").read_text(encoding="utf-8")
                        expect(text).to(contain("Use MCP tool:"))
                        expect(text).to(contain("full sketch instructions that must not appear"))

                # (S) Installer --> Enroll Agent Toolset as MCP Tools
                with context("with mcp operations recorded at install"):
                    with it("should record each mcp-published operation for server enrollment"):
                        names = [op.mcp_name for op in self.mcp.mcp_operations]
                        expect(names).to(contain("sample-mcp.generate"))
                        expect(names).to(contain("sample-mcp.sketch"))

                    with it("should not bind tool handlers during deploy"):
                        server_bound = getattr(self.mcp, "_bound", False)
                        expect(server_bound).to(equal(False))

                # (S) Installer --> Configure and Start MCP Host Session
                with context("with the MCP host stood up"):
                    with it("should diagnose that the MCP host answers ping"):
                        expect(self.mcp.diagnosis["ping"]).to(equal("pong"))

                    with it("should list the built-in health-check tool"):
                        expect(self.mcp.diagnosis["tools"]).to(contain("cdd.ping"))

                with it("should return that operation's instructions when the installed tool is invoked"):
                    server = McpServer()
                    server.bind_from(self.mcp)
                    result = server.invoke_prompt("sample-mcp.generate")
                    expect(result).to(equal("full generate instructions that must not appear in the slash file"))

                # (S) Installer --> Configure and Start MCP Host Session
                with context("with mcp.json on the tree"):
                    with it("should list a stdio host that discovers toolsets from the workspace"):
                        text = (self.tree / "mcp.json").read_text(encoding="utf-8")
                        expect(text).to(contain("python"))
                        expect(text).to(contain("start_host.py"))
                        expect(text).not_to(contain("--toolsets"))
                        expect(text).to(contain("PYTHONPATH"))

                    with it("should publish the stdio server as cdd"):
                        data = json.loads((self.tree / "mcp.json").read_text(encoding="utf-8"))
                        expect(data["mcpServers"]).to(have_key("cdd"))

                with context("with an MCP server started from manifest toolset refs written during that install"):
                    with before.each:
                        self.server = McpServer()
                        self.server.bind_from(self.mcp)

                    with it("should enroll that operation as a prompt under the mcp name for generate"):
                        expect("sample-mcp.generate" in self.server.prompts).to(equal(True))

                    with it(
                        "should enroll from mcp operations recorded at deploy not from a second annotation scan on the class"
                    ):
                        expect(len(self.mcp.mcp_operations) > 0).to(equal(True))

            # (S) Installer --> Register Agent Toolsets as Cursor hooks
            with context("that are annotated as Cursor hooks"):
                with before.each:
                    self._branch_tmp = tempfile.mkdtemp()
                    self.tree = Path(self._branch_tmp)
                    self.installer = Installer(ide="Cursor", path=self.tree)
                    self.mcp = self.installer.install([SampleHookOps()])

                with after.each:
                    shutil.rmtree(self._branch_tmp, ignore_errors=True)

                with context("with hooks.json and hook-handlers.json on the tree"):
                    with it("should write hooks.json dispatch for each registered hook event"):
                        data = json.loads((self.tree / "hooks.json").read_text(encoding="utf-8"))
                        expect(data["version"]).to(equal(1))
                        expect(data["hooks"]).to(have_key("stop"))
                        command = data["hooks"]["stop"][0]["command"]
                        expect(command.replace("\\", "/")).to(contain("harness/hooks/hook_server.py"))

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

                with context("with the hook host stood up"):
                    with it("should diagnose that the hook server answers ping"):
                        expect(self.installer._hook.diagnosis["ping"]).to(equal("pong"))

                    with it("should list the installed hook event"):
                        expect(self.installer._hook.diagnosis["events"]).to(contain("stop"))

            with context("that are not annotated as Cursor hooks and a hooks manifest is already on the IDE path"):
                with before.each:
                    self._branch_tmp = tempfile.mkdtemp()
                    self.tree = Path(self._branch_tmp)
                    prior = self.tree / "hooks.json"
                    prior.write_text(
                        '{"version": 1, "hooks": {"stop": [{"command": "keep-me"}]}}\n',
                        encoding="utf-8",
                    )
                    Installer(ide="Cursor", path=self.tree).install([SampleAgenticOps()])

                with after.each:
                    shutil.rmtree(self._branch_tmp, ignore_errors=True)

                with it("should leave hooks manifest unchanged from a prior full deploy"):
                    text = (self.tree / "hooks.json").read_text(encoding="utf-8")
                    expect(text).to(contain("keep-me"))


    with context("that is a Guidance toolset"):
        with before.each:
            self._tmp = tempfile.mkdtemp()
            self.tree = Path(self._tmp)
            self.tool = SampleGuidance(format="markdown")
            self.installer = Installer(ide="Cursor", path=self.tree)
            self.mcp = self.installer.install([self.tool])

        with after.each:
            shutil.rmtree(self._tmp, ignore_errors=True)

        # (S) Installer --> Deploy Guidance Instructions
        with context("with instructions"):
            with it("should write a skill file whose body is the overview"):
                skill = InstalledTree(self.tree).skill_path("sample-tool")
                expect(skill.is_file()).to(equal(True))
                expect(skill.read_text(encoding="utf-8")).to(contain("sample preamble"))

            with it("should write the overview plus an MCP invoke tail on the skill"):
                text = InstalledTree(self.tree).skill_path("sample-tool").read_text(encoding="utf-8")
                expect(text).to(contain("Use MCP tool:"))
                expect(text).to(contain("sample preamble"))
                expect(text).not_to(contain("active format template body for sample tool"))

            with it("should record the instructions property for MCP enrollment"):
                names = [op.mcp_name for op in self.mcp.mcp_operations]
                expect(names).to(contain("sample-tool.instructions"))

            with it("should not bind tool handlers during install"):
                expect(getattr(self.mcp, "_bound", False)).to(equal(False))

            with it("should return the instructions the property assembles when the installed tool is invoked"):
                server = McpServer()
                server.bind_from(self.mcp)
                result = server.invoke_prompt("sample-tool.instructions")
                expect(result).to(equal(self.tool.instructions))


        # (S) Installer --> Deploy Guidance Rules
        with context("with rules"):
            with it("should write a rules file from the rules property"):
                rule = InstalledTree(self.tree).rule_path("sample-tool.mdc")
                expect(rule.is_file()).to(equal(True))
                expect(rule.read_text(encoding="utf-8")).to(contain("sample rule one"))

    with context("that has been installed"):
        with context("to a path"):
            with context("that has a prior publish of agent skills and commands on the IDE path"):
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

                # (S) Installer --> Clean previously installed skills
                with context("that has been cleansed"):
                    with before.each:
                        self.removed = Installer(ide="Cursor", path=self.tree).clean()

                    with it("should remove the published skill"):
                        expect(len(self.removed) > 0).to(be_true)
                        expect(InstalledTree(self.tree).skill_path("generate") is None).to(equal(True))

                    with it("should leave the file that was never published"):
                        expect(self.orphan.is_file()).to(equal(True))

                # (S) Installer --> Install While preserving skills from prior installed Skills
                with context("that has been published again without removing the prior skills"):
                    with before.each:
                        self.installer.install(
                            [SamplePracticeWithFidelities(format="markdown")],
                            replace=False,
                        )

                    with it("should keep the skill from the prior publish"):
                        expect(InstalledTree(self.tree).skill_path("generate").is_file()).to(equal(True))

                    with it("should publish the new skill"):
                        expect(InstalledTree(self.tree).skill_path("sample-tool").is_file()).to(equal(True))

                    with it("should leave the file that was never published"):
                        expect(self.orphan.is_file()).to(equal(True))

                # (S) Installer --> Install While preserving skills from other sources
                with context("that has been published again in place of the prior skills"):
                    with before.each:
                        self.installer.install([SamplePracticeWithFidelities(format="markdown")])

                    with it("should remove the skill from the prior publish"):
                        expect(InstalledTree(self.tree).skill_path("generate") is None).to(equal(True))

                    with it("should publish the new skill"):
                        expect(InstalledTree(self.tree).skill_path("sample-tool").is_file()).to(equal(True))

                    with it("should leave the file that was never published"):
                        expect(self.orphan.is_file()).to(equal(True))

                # (S) Installer --> Remove orphan skills that name missing MCP tools
                with context("that has an orphan skill naming an MCP tool the install does not enroll"):
                    with before.each:
                        self.stale = (
                            self.tree / "skills" / "space" / "branch" / "branch-create" / "SKILL.md"
                        )
                        self.stale.parent.mkdir(parents=True, exist_ok=True)
                        self.stale.write_text(
                            "Use MCP tool: `branch.create(name: 'str')`\n",
                            encoding="utf-8",
                        )
                        self.installer.install(
                            [SamplePracticeWithFidelities(format="markdown")],
                            replace=True,
                        )

                    with it("should remove the skill that names the missing MCP tool"):
                        expect(self.stale.is_file()).to(equal(False))

                    with it("should leave the hand-authored orphan without an MCP invoke line"):
                        expect(self.orphan.is_file()).to(equal(True))

            with context("that has a prior publish of MCP tools on the IDE path"):
                with before.each:
                    self._tmp = tempfile.mkdtemp()
                    self.tree = Path(self._tmp)
                    Installer(ide="Cursor", path=self.tree).install([SampleMcpOps()])

                with after.each:
                    shutil.rmtree(self._tmp, ignore_errors=True)

                # (S) Installer --> Cleanse previously installed MCP tools
                with context("that has been cleansed"):
                    with before.each:
                        Installer(ide="Cursor", path=self.tree).clean()

                    with it("should keep the MCP manifest so Cursor can respawn the host"):
                        expect((self.tree / "mcp.json").is_file()).to(equal(True))

            # (S) Installer --> Install MCP to User Project Specific Location
            with context("with a project .cursor folder and a user Cursor mcp.json that already names cdd"):
                with before.each:
                    self._user_mcp = Path.home() / ".cursor" / "mcp.json"
                    self._user_mcp_before = (
                        self._user_mcp.read_text(encoding="utf-8") if self._user_mcp.is_file() else None
                    )
                    self._user_mcp.parent.mkdir(parents=True, exist_ok=True)
                    self._user_mcp.write_text(
                        json.dumps(
                            {
                                "mcpServers": {
                                    "cdd": {
                                        "type": "stdio",
                                        "command": "python",
                                        "args": [
                                            "-u",
                                            str(
                                                _REPO_ROOT
                                                / "harness"
                                                / "mcp"
                                                / "scripts"
                                                / "start_host.py"
                                            ),
                                        ],
                                    }
                                }
                            },
                            indent=2,
                        )
                        + "\n",
                        encoding="utf-8",
                    )
                    self._tmp = tempfile.mkdtemp()
                    self.project = Path(self._tmp)
                    self.cursor = self.project / ".cursor"
                    self.cursor.mkdir()
                    Installer(ide="Cursor", path=self.cursor, repo=_REPO_ROOT).install([SampleMcpOps()])

                with after.each:
                    shutil.rmtree(self._tmp, ignore_errors=True)
                    if self._user_mcp_before is None:
                        if self._user_mcp.is_file():
                            self._user_mcp.unlink()
                    else:
                        self._user_mcp.write_text(self._user_mcp_before, encoding="utf-8")

                with it("should set cwd and CDD_PROJECT to the project root on project mcp.json"):
                    data = json.loads((self.cursor / "mcp.json").read_text(encoding="utf-8"))
                    server = data["mcpServers"]["cdd"]
                    expect(server["cwd"]).to(equal(str(self.project)))
                    expect(server["env"]["CDD_PROJECT"]).to(equal(str(self.project)))

                with it("should leave the user Cursor mcp.json unchanged"):
                    data = json.loads(self._user_mcp.read_text(encoding="utf-8"))
                    expect(data["mcpServers"]["cdd"]["command"]).to(equal("python"))

            # (S) Installer --> Generate Installer Skill
            with context("with the installer toolset as the only deploy subject"):
                with before.each:
                    self._tmp = tempfile.mkdtemp()
                    self.tree = Path(self._tmp)
                    self.mcp = Installer(ide="Cursor", path=self.tree).install(
                        [Installer(ide="Cursor", path=self.tree)]
                    )

                with after.each:
                    shutil.rmtree(self._tmp, ignore_errors=True)

                with it("should write an install slash command that runs Python not MCP"):
                    path = InstalledTree(self.tree).command_path("install")
                    expect(path is not None).to(equal(True))
                    text = path.read_text(encoding="utf-8")
                    expect(text).not_to(contain("Use MCP tool:"))
                    expect(text).not_to(contain("installer.install"))
                    expect(text).to(contain("Shell tool"))
                    expect(text).to(contain("scripts/install.py"))
                    expect(text).to(contain("--self"))
                    expect(InstalledTree(self.tree).skill_path("install")).to(equal(None))

                with it("should write a clean slash command with a shell invoke tail"):
                    path = InstalledTree(self.tree).command_path("clean")
                    expect(path is not None).to(equal(True))
                    text = path.read_text(encoding="utf-8")
                    expect(text).to(contain("Shell tool"))
                    expect(text).to(contain("python -c"))
                    expect(text).to(contain(".clean()"))

                with it("should not enroll install or clean as MCP operations"):
                    names = [op.mcp_name for op in self.mcp.mcp_operations]
                    expect(names).not_to(contain("installer.install"))
                    expect(names).not_to(contain("installer.clean"))

                with it("should install only itself via install_self"):
                    tree = Path(tempfile.mkdtemp())
                    try:
                        Installer(ide="Cursor", path=tree, repo=_REPO_ROOT).install_self()
                        path = InstalledTree(tree).command_path("install")
                        expect(path is not None).to(equal(True))
                        expect(path.read_text(encoding="utf-8")).to(contain("scripts/install.py"))
                    finally:
                        shutil.rmtree(tree, ignore_errors=True)

                with it("should enroll a session start hook that respawns the MCP host"):
                    handlers = json.loads((self.tree / "hook-handlers.json").read_text(encoding="utf-8"))
                    events = [item["event"] for item in handlers.get("handlers") or []]
                    expect(events).to(contain("sessionStart"))
                    expect(events).to(contain("afterAgentResponse"))

            # (S) Installer --> Raise Error on Install Failure
            with context("that is given a toolset reference that cannot be instantiated"):
                with it("should raise instead of skipping the toolset"):
                    tree = Path(tempfile.mkdtemp())
                    try:

                        def run():
                            Installer(ide="Cursor", path=tree, repo=_REPO_ROOT).install(
                                ["no.such.module:Nope"]
                            )

                        expect(run).to(raise_error(RuntimeError, "install failed for no.such.module:Nope"))
                    finally:
                        shutil.rmtree(tree, ignore_errors=True)

            # (S) Installer --> Diagnose the finished install
            with context("with a previous install on the diagnostics log"):
                with before.each:
                    self._branch_tmp = tempfile.mkdtemp()
                    self.tree = Path(self._branch_tmp)
                    self.installer = Installer(ide="Cursor", path=self.tree, repo=_REPO_ROOT)
                    self.log = self.tree / "diagnostics.json"

                with after.each:
                    shutil.rmtree(self._branch_tmp, ignore_errors=True)

                with context("that matches the last install"):
                    with before.each:
                        skill = self.tree / "skills" / "generate"
                        skill.mkdir(parents=True)
                        (skill / "SKILL.md").write_text("skill\n", encoding="utf-8")
                        _write_install_log(self.log, ["generate"])

                    with it("should return the counts of what is installed"):
                        report = self.installer.diagnose_install()
                        expect(report).to(contain("installed"))
                        expect(report).to(contain("skill 1 -> 1 (delta 0)"))
                        expect(report).to(contain("mcp host:"))
                        expect(report).to(contain("hook server:"))
                        expect(report).to(contain("hooks registered (events):"))

                    with it("should mark the install green"):
                        expect(self.installer.diagnose_install()).to(contain("green"))

                    with it("should record install channels via diagnose_after_install"):
                        reports = self.installer.diagnose_after_install()
                        expect(any("skill 1 -> 1 (delta 0)" in report for report in reports)).to(
                            equal(True)
                        )

                    with it("should append this install to the diagnostics log"):
                        self.installer.diagnose_after_install()
                        expect(len(json.loads(self.log.read_text(encoding="utf-8"))["installs"])).to(
                            equal(2)
                        )

                    with it("should record the latest skill count on that install"):
                        self.installer.diagnose_after_install()
                        expect(_last_logged_install(self.log)["skill"]["count"]).to(equal(1))

                with context("that has a yellow surface change"):
                    with before.each:
                        for name in ("keep-a", "keep-b", "listed"):
                            folder = self.tree / "skills" / name
                            folder.mkdir(parents=True)
                            (folder / "SKILL.md").write_text("skill\n", encoding="utf-8")
                        _write_install_log(
                            self.log, ["keep-a", "keep-b", "generate", "stale"]
                        )

                    with it("should list every new and deleted item"):
                        report = self.installer.diagnose_install()
                        expect(report).to(contain("new skill: listed"))
                        expect(report).to(contain("deleted skill: generate"))

                    with it("should mark the install yellow"):
                        expect(self.installer.diagnose_install()).to(contain("yellow"))

                with context("that has a majority surface change"):
                    with before.each:
                        skill = self.tree / "skills" / "listed"
                        skill.mkdir(parents=True)
                        (skill / "SKILL.md").write_text("skill\n", encoding="utf-8")
                        _write_install_log(
                            self.log, ["one", "two", "three", "four", "five", "six"]
                        )

                    with it("should show the delta and how to diagnose it"):
                        report = self.installer.diagnose_install()
                        expect(report.startswith("!")).to(equal(True))
                        expect(report).to(contain("skill 6 -> 1 (delta -5)"))

                    with it("should mark the install red"):
                        expect(self.installer.diagnose_install()).to(contain("red"))

                    with it("should log diagnose_install on the install"):
                        self.installer.diagnose_after_install()
                        names = [item["name"] for item in _last_logged_install(self.log)["diagnostics"]]
                        expect(names).to(contain("diagnose_install"))

            with context("whose install standup has finished on the IDE path"):
                with it("should leave hook and mcp hosts answering"):
                    installer = Installer(ide="Cursor", path=_REPO_ROOT / ".cursor", repo=_REPO_ROOT)
                    status = installer.ensure_runtimes()
                    expect(status["hook"]).to(equal("running"))
                    expect(status["mcp"]).to(equal("running"))

            with context("that resolves deploy imports and toolsets from the repo catalog"):
                with before.each:
                    self.repo = Path(__file__).resolve().parents[2]
                    Installer(repo=self.repo).ensure_import_path()

                with it("should not collect toolsets under examples folders"):
                    refs = Installer(
                        ide="Cursor", path=self.repo / ".cursor", repo=self.repo
                    ).collect_toolsets()
                    expect(any("examples" in ref.replace("\\", "/") for ref in refs)).to(equal(False))
                    expect(any("car_story" in ref for ref in refs)).to(equal(False))

                with it("should collect deployable toolsets under harness and patterns"):
                    refs = Installer(
                        ide="Cursor", path=self.repo / ".cursor", repo=self.repo
                    ).collect_toolsets()
                    expect(refs).not_to(contain("_retired.transformers.transformers:Transformers"))
                    expect(refs).to(contain("cdd_guidance.patterns.lern_domain_driven.lern_domain_driven:LernDomainDriven"))
                    expect(refs).to(contain("cdd_guidance.patterns.mern_domain_driven.mern_domain_driven:MernDomainDriven"))
                    expect(refs).to(contain("harness.graph.graph:Graph"))
                    expect(refs).to(contain("harness.guidance.guidance:Guidance"))
                    expect(refs).not_to(contain("harness.guidance.guidance:PracticeGuidance"))
                    expect(refs).not_to(contain("harness.guidance.guidance:FidelityGuidance"))

                with it("should put catalog folders on sys.path so short catalog imports resolve"):
                    import harness.agent_tools as agent_tools
                    import harness.guidance_actions as guidance_actions

                    installer = Installer(repo=self.repo)
                    expect("agent_toolset" in dir(agent_tools)).to(equal(True))
                    expect(guidance_actions.GuidanceAction.__name__).to(equal("GuidanceAction"))
                    expect(installer.pythonpath()).to(contain("actions"))
                    expect(installer.pythonpath()).to(contain("patterns"))
                    expect(installer.pythonpath()).not_to(contain(str(self.repo / "harness" / "installation") + os.sep))
                    expect(installer.pythonpath().split(os.pathsep)).not_to(
                        contain(str(self.repo / "harness"))
                    )

                with it("should not record a temp install path in the shared install state"):
                    shared = Path(__file__).resolve().parent / ".install-state.json"
                    before = shared.read_text(encoding="utf-8") if shared.is_file() else ""
                    tmp = tempfile.mkdtemp()
                    try:
                        Installer(ide="Cursor", path=tmp, repo=self.repo).install([])
                        after = shared.read_text(encoding="utf-8") if shared.is_file() else ""
                        expect(after).to(equal(before))
                        expect(
                            Installer(path=tmp, repo=self.repo)._is_ephemeral_install_path(tmp)
                        ).to(equal(True))
                    finally:
                        shutil.rmtree(tmp, ignore_errors=True)

# (E) Install CDD Tools
# (E) Install Practice Guidance Class
with description("a practice guidance class") as self:
    # (S) Installer --> Deploy Practice guidance instructions
    with context("with instructions"):
        with before.each:
            self._tmp = tempfile.mkdtemp()
            self.tree = Path(self._tmp)
            self.tool = SamplePracticeGuidance(format="markdown")
            self.installer = Installer(ide="Cursor", path=self.tree)
            self.mcp = self.installer.install([self.tool])

        with after.each:
            shutil.rmtree(self._tmp, ignore_errors=True)

        with it("should write a skill file whose body is the overview"):
            text = InstalledTree(self.tree).skill_path("sample-tool").read_text(encoding="utf-8")
            expect(text).to(contain("sample preamble"))

        with it("should put the skill folder name and overview in YAML front matter"):
            text = InstalledTree(self.tree).skill_path("sample-tool").read_text(encoding="utf-8")
            front = text.split("---", 2)[1]
            expect(text.startswith("---\n")).to(equal(True))
            expect(front).to(contain("name: sample-tool"))
            expect(front).to(contain("description:"))
            expect(front).to(contain("sample preamble"))

        with it("should keep the MCP invoke tail out of the skill description"):
            from harness.installation.files import FileInstallation

            overview = "sample preamble"
            writer = FileInstallation("Cursor", self.tree, "skill")
            text = writer._skill_front_matter(
                "sample-tool",
                writer._skill_overview(
                    type("Host", (), {"overview": overview})(),
                    [overview, "Use MCP tool: `sample-tool.instructions()`"],
                ),
            )
            expect(text).to(contain("sample preamble"))
            expect(text).not_to(contain("Use MCP tool:"))

        with it("should not append a YAML CLI invoke fence to the skill body"):
            skill = InstalledTree(self.tree).skill_path("sample-tool").read_text(encoding="utf-8")
            expect(skill).not_to(contain("tools.ps1"))
            expect(skill).not_to(contain("toolset:"))

        with it("should return the instructions the property assembles when the installed tool is invoked"):
            server = McpServer()
            server.bind_from(self.mcp)
            result = server.invoke_prompt("sample-tool.instructions")
            expect(result).to(equal(self.tool.instructions))

        with context("with an underscored practice module path"):
            with it("should kebab-case the practice folder to match fidelity skill names"):
                from harness.installation.files import FileInstallation

                writer = FileInstallation("Cursor", Path("."), "skill")
                tools = {"instructions": _skill_tool("instructions")}
                toolset = type(
                    "Practice",
                    (),
                    {"install_folder": Path("cdd_guidance/practices/sample_tool"), "tools": tools},
                )()
                expect(
                    writer.relative_path(
                        "skill", toolset, tools["instructions"].callable, "instructions"
                    ).as_posix()
                ).to(equal("skills/practices/sample-tool/SKILL.md"))

    # (S) Installer --> Deploy Practice guidance rules
    with context("with rules"):
        with before.each:
            self._tmp = tempfile.mkdtemp()
            self.tree = Path(self._tmp)
            self.tool = SamplePracticeGuidance(format="markdown")
            self.installer = Installer(ide="Cursor", path=self.tree)
            self.mcp = self.installer.install([self.tool])

        with after.each:
            tmp = getattr(self, "_tmp", None)
            if tmp:
                shutil.rmtree(tmp, ignore_errors=True)

        with it("should write a rules file from the rules property"):
            expect(InstalledTree(self.tree).rule_path("sample-tool.mdc").is_file()).to(equal(True))
            expect(InstalledTree(self.tree).rule_path("sample-tool.mdc").read_text(encoding="utf-8")).to(
                contain("sample rule one")
            )

        with it("should copy alwaysApply and globs from the rules property onto the rules file"):
            text = InstalledTree(self.tree).rule_path("sample-tool.mdc").read_text(encoding="utf-8")
            expect(text).to(contain("alwaysApply: false"))
            expect(text).to(contain("globs: **/*sample*"))

        with it("should not append a YAML CLI invoke fence to the rules body"):
            rule = InstalledTree(self.tree).rule_path("sample-tool.mdc").read_text(encoding="utf-8")
            expect(rule).not_to(contain("tools.ps1"))
            expect(rule).not_to(contain("toolset:"))

        with context("that do not enroll inject_rules when the hook is disabled on the operation"):
            with before.each:
                from cdd_guidance.practices.bdd.bdd import Bdd
                from cdd_guidance.practices.clean_engineering.clean_engineering import CleanEngineering

                self._branch_tmp = tempfile.mkdtemp()
                self.tree = Path(self._branch_tmp)
                Installer(ide="Cursor", path=self.tree, repo=_REPO_ROOT).install(
                    [Bdd(), CleanEngineering()]
                )
                handlers_path = self.tree / "hook-handlers.json"
                self.handlers = (
                    json.loads(handlers_path.read_text(encoding="utf-8"))
                    if handlers_path.is_file()
                    else {"handlers": []}
                )
                self.inject_refs = [
                    item["ref"]
                    for item in self.handlers.get("handlers") or []
                    if item.get("operation") == "inject_rules"
                    and item.get("event") == "postToolUse"
                ]

            with after.each:
                branch = getattr(self, "_branch_tmp", None)
                if branch:
                    shutil.rmtree(branch, ignore_errors=True)

            with it("should not write a Bdd inject_rules handler"):
                expect(self.inject_refs.count("cdd_guidance.practices.bdd.bdd:Bdd")).to(equal(0))

            with it("should not write a CleanEngineering inject_rules handler"):
                expect(
                    self.inject_refs.count(
                        "cdd_guidance.practices.clean_engineering.clean_engineering:CleanEngineering"
                    )
                ).to(equal(0))

        with context("that do not inject"):
            with before.each:
                from harness.agent_tools.agent_tools import AgentToolSet

                Car = AgentToolSet._load("cdd_guidance.practices._examples.car.car:Car")
                from cdd_guidance.actions._examples.car_story.car_story import CarStory

                self._branch_tmp = tempfile.mkdtemp()
                self._car_tree = Path(self._branch_tmp)
                Installer(ide="Cursor", path=self._car_tree, repo=_REPO_ROOT).install(
                    [Car(), CarStory()]
                )

            with after.each:
                branch = getattr(self, "_branch_tmp", None)
                if branch:
                    shutil.rmtree(branch, ignore_errors=True)

            with it("should not write inject_rules handlers for Car or CarStory"):
                dest = self._car_tree / "hook-handlers.json"
                if dest.is_file():
                    refs = [
                        item.get("ref", "")
                        for item in json.loads(dest.read_text(encoding="utf-8")).get("handlers")
                        or []
                    ]
                else:
                    refs = []
                expect(any("car:Car" in ref for ref in refs)).to(equal(False))
                expect(any("CarStory" in ref for ref in refs)).to(equal(False))

    # (S) Installer --> Deploy Practice guidance fidelities
    with context("with fidelities"):
        with before.each:
            self._tmp = tempfile.mkdtemp()
            self.tree = Path(self._tmp)
            self.tool = SamplePracticeWithFidelities(format="markdown")
            self.mcp = Installer(ide="Cursor", path=self.tree).install([self.tool])

        with after.each:
            shutil.rmtree(self._tmp, ignore_errors=True)

        with it("should write practice and fidelity skill folders in kebab-case not underscored slugs"):
            names = InstalledTree(self.tree).skill_names()
            expect(names).to(contain("sample-tool"))
            expect(names).to(contain("sample-tool-sketch"))
            expect("sample_tool" in names).to(equal(False))
            expect(InstalledTree(self.tree).skill_path("sample-tool").is_file()).to(equal(True))

        with it("should emit the practice skill, practice rules, fidelity skills, and fidelity rules in one pass"):
            expect(InstalledTree(self.tree).skill_path("sample-tool").is_file()).to(equal(True))
            expect(InstalledTree(self.tree).rule_path("sample-tool.mdc").is_file()).to(equal(True))
            expect(InstalledTree(self.tree).skill_path("sample-tool-sketch").is_file()).to(equal(True))
            expect(InstalledTree(self.tree).command_path("sample-tool-sketch")).to(equal(None))
            expect(InstalledTree(self.tree).rule_path("sample-tool-spec.mdc").is_file()).to(equal(True))

        with context("with a leftover underscored practice skill folder beside the installed tree"):
            with before.each:
                kebab_dir = InstalledTree(self.tree).skill_path("sample-tool").parent
                self.leftover = kebab_dir.parent / "sample_tool"
                self.leftover.mkdir(parents=True, exist_ok=True)
                (self.leftover / "SKILL.md").write_text("stale\n", encoding="utf-8")
                Installer(ide="Cursor", path=self.tree).install(
                    [SamplePracticeWithFidelities(format="markdown")]
                )

            with it("should remove the leftover underscored folder"):
                expect(self.leftover.exists()).to(equal(False))

            with it("should keep the kebab-case practice skill"):
                expect(InstalledTree(self.tree).skill_path("sample-tool").is_file()).to(equal(True))

        with context("with an underscored module path and fidelity folders under it"):
            with it("should keep the practice folder and name the leaf practice-fidelity"):
                from harness.installation.files import FileInstallation

                writer = FileInstallation("Cursor", Path("."), "skill")
                tools = {"instructions": _skill_tool("instructions")}
                practice = type("Practice", (), {"slug": "sample-tool"})()
                toolset = type(
                    "Fidelity",
                    (),
                    {
                        "install_folder": Path("cdd_guidance/practices/sample_tool/sketch"),
                        "tools": tools,
                        "practice_guidance": practice,
                        "slug": "sample-tool-sketch",
                    },
                )()
                expect(
                    writer.relative_path(
                        "skill", toolset, tools["instructions"].callable, "instructions"
                    ).as_posix()
                ).to(equal("skills/practices/sample-tool/sample-tool-sketch/SKILL.md"))

            with it("should kebab-case the practice parent so it matches the fidelity leaf"):
                from harness.installation.files import FileInstallation

                writer = FileInstallation("Cursor", Path("."), "skill")
                tools = {"instructions": _skill_tool("instructions")}
                practice = type("Practice", (), {"slug": "sample-tool"})()
                toolset = type(
                    "Fidelity",
                    (),
                    {
                        "install_folder": Path("cdd_guidance/practices/sample_tool/spec"),
                        "tools": tools,
                        "practice_guidance": practice,
                        "slug": "sample-tool-spec",
                    },
                )()
                expect(
                    writer.relative_path(
                        "skill", toolset, tools["instructions"].callable, "instructions"
                    ).as_posix()
                ).to(equal("skills/practices/sample-tool/sample-tool-spec/SKILL.md"))

        # (S) Installer --> Deploy Practice guidance fidelity instructions
        with context("that have instructions"):
            with it("should write one fidelity skill file per fidelity"):
                sketch = InstalledTree(self.tree).skill_path("sample-tool-sketch")
                expect(sketch.is_file()).to(equal(True))
                expect(sketch.read_text(encoding="utf-8")).to(contain("sample-tool-sketch()"))

            with it("should leave each fidelity off the command list"):
                expect(InstalledTree(self.tree).command_path("sample-tool-sketch")).to(equal(None))

            with it("should list each fidelity MCP signature and a one-liner on the practice skill"):
                text = InstalledTree(self.tree).skill_path("sample-tool").read_text(encoding="utf-8")
                expect(text).to(contain("sample preamble"))
                expect(text).to(contain("sketch"))
                expect(text).to(contain("Use MCP tool:"))
                expect(text).to(contain("sample-tool-sketch()"))
                expect(text).not_to(contain("sketch guidance body only"))

            with it("should return that fidelity's instructions when the installed tool is invoked"):
                server = McpServer()
                server.bind_from(self.mcp)
                sketch = self.tool.fidelities.entries["sketch"]
                result = server.invoke_prompt("sample-tool-sketch")
                expect(result).to(equal(sketch.instructions))

            with context("from stories"):
                with before.each:
                    from cdd_guidance.practices.stories.stories import Stories

                    self._branch_tmp = tempfile.mkdtemp()
                    self.tree = Path(self._branch_tmp)
                    self.tool = Stories()
                    self.mcp = Installer(ide="Cursor", path=self.tree, repo=_REPO_ROOT).install(
                        [self.tool]
                    )
                    self.server = McpServer()
                    self.server.bind_from(self.mcp)

                with after.each:
                    shutil.rmtree(self._branch_tmp, ignore_errors=True)

                with it("should enroll nested fidelity instructions under the fidelity slug"):
                    expect("stories-scenarios" in self.server.prompts).to(equal(True))

                with it("should return that fidelity's instructions when the installed tool is invoked"):
                    scenarios = self.tool.fidelities.entries["scenarios"]
                    result = self.server.invoke_prompt("stories-scenarios")
                    expect(result).to(equal(scenarios.instructions))

            with context("that has been installed for VS Code"):
                with before.each:
                    self._branch_tmp = tempfile.mkdtemp()
                    self.tree = Path(self._branch_tmp)
                    Installer(ide="VS Code", path=self.tree).install(
                        [SamplePracticeWithFidelities(format="markdown")]
                    )

                with after.each:
                    shutil.rmtree(self._branch_tmp, ignore_errors=True)

                with it("should leave each fidelity out of github prompts"):
                    expect(InstalledTree(self.tree).prompt_path("sample-tool-sketch")).to(equal(None))

        # (S) Installer --> Deploy Practice guidance fidelity rules
        with context("that have rules"):
            with it("should write one fidelity rules file whose body is that fidelity's rules section"):
                sketch_rules = InstalledTree(self.tree).rule_path("sample-tool-sketch.mdc")
                expect(sketch_rules.is_file()).to(equal(True))
                expect(sketch_rules.read_text(encoding="utf-8")).to(contain("sketch rule body"))

            with it("should leave alwaysApply off and omit globs on a fidelity rules file"):
                text = InstalledTree(self.tree).rule_path("sample-tool-sketch.mdc").read_text(encoding="utf-8")
                expect(text).to(contain("alwaysApply: false"))
                expect(text).not_to(contain("globs:"))

# (E) Install CDD Tools
# (E) Install Action Classes
# (S) Installer --> Install Lifecycle actions
with description("lifecycle actions annotated for installation") as self:
    with context("that has been installed to Cursor"):
        with context("with operations annotated as skills"):
            with context("with only a single skill operation"):
                with before.each:
                    from cdd_guidance.actions.document.document import Document
                    from cdd_guidance.actions.generate.generate import Generate
                    from cdd_guidance.actions.grill_context.grill_context import GrillContext
                    from cdd_guidance.actions.iterate.iterate import Iterate
                    from cdd_guidance.actions.partition.partition import Partition
                    from cdd_guidance.actions.render.render import Render
                    from cdd_guidance.actions.satisfy.satisfy import Satisfy
                    from cdd_guidance.actions.sketch.sketch import Sketch

                    self._tmp = tempfile.mkdtemp()
                    self.tree = Path(self._tmp)
                    self.mcp = Installer(ide="Cursor", path=self.tree, repo=_REPO_ROOT).install(
                        [
                            Document(),
                            Generate(),
                            GrillContext(),
                            Iterate(),
                            Partition(),
                            Render(),
                            Satisfy(),
                            Sketch(),
                        ]
                    )

                with after.each:
                    tmp = getattr(self, "_tmp", None)
                    if tmp:
                        shutil.rmtree(tmp, ignore_errors=True)

                with it("should write a skill file for each operation annotated as a skill"):
                    expect(InstalledTree(self.tree).skill_names()).to(
                        equal(
                            {
                                "document",
                                "generate",
                                "grill",
                                "iterate",
                                "partition",
                                "render",
                                "satisfy",
                                "sketch",
                            }
                        )
                    )

                with it("should keep a single matching operation at the kit folder"):
                    expect(
                        (self.tree / "skills" / "actions" / "generate" / "SKILL.md").is_file()
                    ).to(equal(True))

                with it("should name a single unmatched operation for the operation not the kit folder"):
                    expect(
                        (
                            self.tree / "skills" / "actions" / "grill-context" / "grill" / "SKILL.md"
                        ).is_file()
                    ).to(equal(True))

            # (S) Installer --> Install Lifecycle actions as several tools
            with context("with several skill operations"):
                with before.each:
                    from cdd_guidance.actions.improvement.improvement import Improvement

                    self._tmp = tempfile.mkdtemp()
                    self.tree = Path(self._tmp)
                    self.mcp = Installer(ide="Cursor", path=self.tree, repo=_REPO_ROOT).install(
                        [Improvement()]
                    )

                with after.each:
                    tmp = getattr(self, "_tmp", None)
                    if tmp:
                        shutil.rmtree(tmp, ignore_errors=True)

                with it("should write each skill as a peer folder named for the operation"):
                    root = self.tree / "skills" / "actions" / "improvement"
                    expect(
                        sorted(path.relative_to(root).as_posix() for path in root.rglob("SKILL.md"))
                    ).to(equal(["repair/SKILL.md", "verify-fix/SKILL.md"]))

        with context("with operations annotated for MCP"):
            with context("with only a single MCP operation"):
                with before.each:
                    from cdd_guidance.actions.generate.generate import Generate

                    self._tmp = tempfile.mkdtemp()
                    self.tree = Path(self._tmp)
                    self.mcp = Installer(ide="Cursor", path=self.tree, repo=_REPO_ROOT).install(
                        [Generate()]
                    )

                with after.each:
                    tmp = getattr(self, "_tmp", None)
                    if tmp:
                        shutil.rmtree(tmp, ignore_errors=True)

                with it("should record that operation"):
                    expect([op.mcp_name for op in self.mcp.mcp_operations]).to(
                        equal(["generate.generate"])
                    )

                with it("should return that operation's instructions when the installed tool is invoked"):
                    server = McpServer()
                    server.bind_from(self.mcp)
                    result = server.invoke_prompt("generate.generate")
                    expect(str(result)).to(contain("Write artifacts for each listed guidance"))

            # (S) Installer --> Install Lifecycle actions as several tools
            with context("with several MCP operations"):
                with before.each:
                    from cdd_guidance.actions.improvement.improvement import Improvement
                    from cdd_guidance.actions.validate.validate import Validate

                    self._tmp = tempfile.mkdtemp()
                    self.tree = Path(self._tmp)
                    self.mcp = Installer(ide="Cursor", path=self.tree, repo=_REPO_ROOT).install(
                        [Improvement(), Validate()]
                    )

                with after.each:
                    tmp = getattr(self, "_tmp", None)
                    if tmp:
                        shutil.rmtree(tmp, ignore_errors=True)

                with it("should record each operation annotated for MCP"):
                    expect(sorted(op.mcp_name for op in self.mcp.mcp_operations)).to(
                        equal(
                            [
                                "improvement.repair",
                                "improvement.verify_fix",
                                "validate.validate",
                            ]
                        )
                    )

                with it("should not publish an operation annotated not to deploy"):
                    names = [op.mcp_name for op in self.mcp.mcp_operations]
                    expect("validate.createRule" in names).to(equal(False))

with description("guidance agents"):
    with it("should install the agents from cdd_guidance/agents"):
        tree = Path(tempfile.mkdtemp())
        try:
            Installer(ide="Cursor", path=tree, repo=_REPO_ROOT)._install_agents()
            installed = sorted(path.name for path in (tree / "agents").glob("*.md"))
            expect(installed).to(equal(["context.md", "discoverer.md", "implementation.md", "specification.md"]))
            expect((tree / "agents" / "discoverer.md").read_text(encoding="utf-8")).to(contain("name: discoverer"))
            expect(((_REPO_ROOT / "cdd_guidance" / "agents" / "discovery.md").is_file())).to(equal(True))
        finally:
            shutil.rmtree(tree, ignore_errors=True)

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
            expect(HookDecoration().unknown_event).to(raise_error(ValueError))

    with context("that omits the event"):
        with it("should raise ValueError"):
            expect(HookDecoration().omitted_event).to(raise_error(ValueError))

# (S) Installer --> Install for Claude Code
with description("toolsets installed for Claude Code") as self:
    with before.each:
        self._branch_tmp = tempfile.mkdtemp()
        self.project = Path(self._branch_tmp)
        self.tree = self.project / ".claude"
        self.tree.mkdir()
        (self.project / ".mcp.json").write_text(
            json.dumps({"mcpServers": {"other": {"command": "other"}}}), encoding="utf-8"
        )
        (self.tree / "settings.json").write_text(
            json.dumps({"permissions": {"allow": ["Bash(ls)"]}}), encoding="utf-8"
        )
        Installer(ide="Claude", path=self.tree, repo=_REPO_ROOT).install(
            [SamplePracticeWithFidelities(format="markdown"), SampleMcpOps(), SampleHookOps()]
        )
        self.settings = json.loads((self.tree / "settings.json").read_text(encoding="utf-8"))

    with after.each:
        shutil.rmtree(self._branch_tmp, ignore_errors=True)

    with it("should place every skill one folder under skills, named by its whole path"):
        for path in (self.tree / "skills").rglob("SKILL.md"):
            expect(path.parent.parent).to(equal(self.tree / "skills"))
            expect(path.read_text(encoding="utf-8")).to(contain(f"name: {path.parent.name}\n"))
        expect(InstalledTree(self.tree).skill_path("harness-guidance-fixtures-sample-tool-sample-tool-sketch")).not_to(
            equal(None)
        )

    with it("should write rules as markdown, not mdc"):
        expect(InstalledTree(self.tree).rule_path("sample-tool-sketch.md")).not_to(equal(None))
        expect(list((self.tree / "rules").rglob("*.mdc"))).to(equal([]))

    with it("should add the cdd server to the project .mcp.json and keep the project's own servers"):
        servers = json.loads((self.project / ".mcp.json").read_text(encoding="utf-8"))["mcpServers"]
        expect(servers).to(have_key("other"))
        expect(servers["cdd"]).not_to(have_key("cwd"))
        expect(servers["cdd"]["env"]["CDD_IDE_PATH"]).to(equal(str(self.tree.resolve())))
        expect((self.tree / "mcp.json").exists()).to(equal(False))

    with it("should install no hooks and leave the project's settings.json alone"):
        expect(self.settings).to(equal({"permissions": {"allow": ["Bash(ls)"]}}))
        expect((self.tree / "hooks.json").exists()).to(equal(False))
        expect((self.tree / "hook-handlers.json").exists()).to(equal(False))

    with context("with rules scoped by globs"):
        with it("should list each glob under paths"):
            from harness.installation.files import FileInstallation

            text = FileInstallation("Claude", Path("."), "rules")._claude_rules_front_matter(
                "d", "**/*.py, **/*.ts"
            )
            expect(text).to(equal('---\ndescription: "d"\npaths:\n  - "**/*.py"\n  - "**/*.ts"\n---\n\n'))


with description("Repo branch commands installed into Cursor") as self:
    with before.each:
        self._tmp = tempfile.mkdtemp()
        self.tree = Path(self._tmp)
        self.mcp = Installer(ide="Cursor", path=self.tree, repo=_REPO_ROOT).install(
            ["space.repo.repo:Repo"]
        )

    with after.each:
        shutil.rmtree(self._tmp, ignore_errors=True)

    with it("should write switch-branch naming repo.switch_branch"):
        path = self.tree / "commands" / "space" / "repo" / "switch-branch.md"
        expect(path.read_text(encoding="utf-8")).to(contain("repo.switch_branch"))

    with it("should not write the retired new-branch command"):
        path = self.tree / "commands" / "space" / "repo" / "new-branch.md"
        expect(path.is_file()).to(equal(False))

    with it("should enroll repo.switch_branch on the MCP channel"):
        names = [op.mcp_name for op in self.mcp.mcp_operations]
        expect(names).to(contain("repo.switch_branch"))
