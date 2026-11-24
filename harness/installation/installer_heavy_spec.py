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

from harness.mcp.claude_plugins import ClaudePlugins, PluginInstall
from harness.agent_tools.agent_tools import InstalledName, ToolsetReference
from harness.installation.installer import Installer, ToolsetInstallFailed


class _Published:
    """A plugin the cdd home's marketplace publishes, at the version it publishes it at, from its folder."""

    def __init__(self, name: str, version: str) -> None:
        self.name = name
        self.version = version
        self.installed_name = f"{name}@cdd-home"
        self.folder = Path(tempfile.gettempdir()) / "cdd-home" / "claude-plugins" / name
        self.marketplace = type("Marketplace", (), {"folder": self.folder.parent, "mod_folder": lambda _self, plugin: plugin.folder})()


_BOARD = _Published("cdd-board", "0.6.3-abc")
_CDD = _Published("cdd", "1.0.0-abc")
_QUEUE = _Published("prompt-queue", "0.1.0-abc")


class _ScriptedClaude(ClaudePlugins):
    """The plugin installer over a throwaway Claude Code settings folder, with a claude command that records each call and
    lists what the spec says."""

    # A folder the person's settings named already, which an install keeps.
    OWN_FOLDER = str(Path("own") / "chat-ui" / "pane")

    def __init__(self, listed: str) -> None:
        self.claude_folder = Path(tempfile.mkdtemp(prefix="cdd-claude-settings-"))
        self.home_folder = Path(tempfile.mkdtemp(prefix="cdd-home-"))
        super().__init__(CddHome(self.home_folder), claude_folder=self.claude_folder)
        for plugin in (_BOARD, _CDD, _QUEUE):
            plugin.folder.mkdir(parents=True, exist_ok=True)
        self.listed = listed
        self.calls: list[tuple[str, ...]] = []
        self.cli: str | None = "claude"
        self.plugins_installed: dict[str, str] = {}
        self.watch_folders(self.OWN_FOLDER)

    def watch_folders(self, *folders: str) -> None:
        settings = self.claude_folder / "settings.json"
        named = json.loads(settings.read_text(encoding="utf-8")) if settings.is_file() else {}
        current = [f for f in named.get("env", {}).get("CLAUDE_CODE_PLUGIN_DIRS", "").split(os.pathsep) if f]
        named.setdefault("env", {})["CLAUDE_CODE_PLUGIN_DIRS"] = os.pathsep.join([*current, *folders])
        settings.write_text(json.dumps(named), encoding="utf-8")

    def chat_folder(self, name: str) -> Path:
        return self.home_folder / "chat-plugins" / name

    @property
    def watched_folders(self) -> list[str]:
        named = json.loads((self.claude_folder / "settings.json").read_text(encoding="utf-8"))
        return [f for f in named["env"]["CLAUDE_CODE_PLUGIN_DIRS"].split(os.pathsep) if f]

    @property
    def installed(self) -> dict[str, str]:
        return self.plugins_installed

    @property
    def claude_cli(self) -> str | None:
        return self.cli

    def run(self, claude: str, *args: str) -> str:
        self.calls.append(args)
        return self.listed
from harness.installation.repository_toolsets import RepositoryToolsets

RepositoryToolsets(_REPO_ROOT).ensure_import_path()

from expects import be_true, contain, equal, expect, have_key, raise_error, start_with
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
from harness.hooks.hooks import Hook, hook
from harness.mcp.cdd_home import CddHome
from harness.mcp.mcp_server import McpInstallation, ProjectToolsets
from harness.mcp.mcp_daemon import McpDaemon
from harness.mcp.spec_support import ThrowawayMachine
from harness.installation.ide_layout import IdeLayout
from harness.installation.install_target import InstallTarget
from harness.installation.files import Skill
from harness.installation.install_diagnostics import InstallDiagnosis
from harness.installation.installer import SERVER_CHANNELS, InstallChannels, InstallRun




def _server_publishing(installation: McpInstallation) -> ProjectToolsets:
    """A server publishing the operations an install recorded, as the cdd server publishes them."""
    server = ProjectToolsets()
    for tool in installation.mcp_operations:
        server.enroll(tool)
    return server


class HookDecoration:
    def unknown_event(self) -> None:
        @hook("notAnEvent")
        def handler(self, payload: dict) -> dict:
            return {}

    def omitted_event(self) -> None:
        @hook
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


def _recorded_diagnosis(installer: Installer) -> InstallDiagnosis:
    """The diagnosis of the folder installer installs into, recorded in its diagnostics as an install records it."""
    diagnosis = installer.diagnosis_of(*_folder_channels(installer))
    installer.diagnostics.record(diagnosis)
    return diagnosis


def _folder_channels(installer: Installer) -> tuple:
    """The channels of an install not run, reading the folder as an earlier install left it."""
    channels = InstallChannels(installer, SERVER_CHANNELS.kinds)
    return channels, channels.published


def _last_logged_install(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))["installs"][-1]


def _skill_tool(name: str):
    @Skill
    def _fn(self):
        return None

    return type("Tool", (), {"name": name, "deploy_name": name, "is_published_to": lambda self, destination: destination is Skill, "callable": _fn})()


def _own_skill_tool(installed: InstalledName):
    """A toolset's own instructions skill, on a toolset that installs it as installed says."""
    tool = _skill_tool("instructions")
    tool.toolset = type("Toolset", (), {"tools": {"instructions": tool}, "installed_as": lambda self, _tool: installed})()
    return tool


# (E) Install CDD Tools
# (E) Install Agent Toolset
with description("an agent toolset") as self:
    with before.all:
        self.machine = ThrowawayMachine()
        self.machine.enter()

    with after.all:
        self.machine.leave()

    with context("with operations annotated for installation"):
        # (S) Installer --> Generate skills and commands from Agent Toolset
        with context("that are annotated as skills and commands"):
            with before.each:
                self._tmp = tempfile.mkdtemp()
                self.tree = Path(self._tmp)
                self.installer = Installer.create(ide="Cursor", path=self.tree, repo=_REPO_ROOT)
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
                    self.installer = Installer.create(ide="Cursor", path=self.tree, repo=_REPO_ROOT)
                    self.mcp = self.installer.install([SampleMcpOps()]).of(McpInstallation)

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

                # (S) Installer --> Configure and Start MCP Host Session
                with context("with the MCP host stood up"):
                    with it("should list the built-in health-check tool"):
                        expect(self.mcp.server.stood_up.tools).to(contain("cdd.ping"))

                with it("should return that operation's instructions when the installed tool is invoked"):
                    server = _server_publishing(self.mcp)
                    result = server.invoke("sample-mcp.generate")
                    expect(result).to(equal("full generate instructions that must not appear in the slash file"))

                # (S) Installer --> Configure and Start MCP Host Session
                with context("with mcp.json on the tree"):
                    with it("should name the one cdd server by its URL, with no command or toolsets to start"):
                        server = json.loads((self.tree / "mcp.json").read_text(encoding="utf-8"))["mcpServers"]["cdd"]
                        expect(server["url"]).to(equal(McpDaemon(CddHome()).url))
                        expect(sorted(server)).to(equal(["headers", "url"]))

                    with it("should publish the server as cdd"):
                        data = json.loads((self.tree / "mcp.json").read_text(encoding="utf-8"))
                        expect(data["mcpServers"]).to(have_key("cdd"))

                with context("with an MCP server publishing the operations that install recorded"):
                    with before.each:
                        self.server = _server_publishing(self.mcp)

                    with it("should enroll that operation as a prompt under the mcp name for generate"):
                        expect("sample-mcp.generate" in self.server.prompts).to(equal(True))

            # (S) Installer --> Register Agent Toolsets as Cursor hooks
            with context("that are annotated as Cursor hooks"):
                with before.each:
                    self._branch_tmp = tempfile.mkdtemp()
                    self.tree = Path(self._branch_tmp)
                    self.installer = Installer.create(ide="Cursor", path=self.tree, repo=_REPO_ROOT)
                    self.run = self.installer.install([SampleHookOps()])

                with after.each:
                    shutil.rmtree(self._branch_tmp, ignore_errors=True)

                with context("with hooks.json and hook-handlers.json on the tree"):
                    with it("should write hooks.json dispatch for each registered hook event"):
                        data = json.loads((self.tree / "hooks.json").read_text(encoding="utf-8"))
                        expect(data["version"]).to(equal(1))
                        expect(data["hooks"]).to(have_key("stop"))
                        command = data["hooks"]["stop"][0]["command"]
                        expect(command.replace("\\", "/")).to(contain("harness/hooks/hook_daemon.py"))

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

            with context("that are not annotated as Cursor hooks and a hooks manifest is already on the IDE path"):
                with before.each:
                    self._branch_tmp = tempfile.mkdtemp()
                    self.tree = Path(self._branch_tmp)
                    prior = self.tree / "hooks.json"
                    prior.write_text(
                        '{"version": 1, "hooks": {"stop": [{"command": "keep-me"}]}}\n',
                        encoding="utf-8",
                    )
                    Installer.create(ide="Cursor", path=self.tree, repo=_REPO_ROOT).install([SampleAgenticOps()])

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
            self.installer = Installer.create(ide="Cursor", path=self.tree, repo=_REPO_ROOT)
            self.mcp = self.installer.install([self.tool]).of(McpInstallation)

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

            with it("should return the instructions the property assembles when the installed tool is invoked"):
                server = _server_publishing(self.mcp)
                result = server.invoke("sample-tool.instructions")
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
                    self.installer = Installer.create(ide="Cursor", path=self.tree, repo=_REPO_ROOT)
                    self.installer.install([SampleAgenticOps()])
                    self.orphan = self.tree / "skills" / "stale-orphan" / "SKILL.md"
                    self.orphan.parent.mkdir(parents=True, exist_ok=True)
                    self.orphan.write_text("orphan", encoding="utf-8")

                with after.each:
                    shutil.rmtree(self._tmp, ignore_errors=True)

                # (S) Installer --> Clean previously installed skills
                with context("that has been cleansed"):
                    with before.each:
                        self.removed = Installer.create(ide="Cursor", path=self.tree, repo=_REPO_ROOT).clean()

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
                    Installer.create(ide="Cursor", path=self.tree, repo=_REPO_ROOT).install([SampleMcpOps()])

                with after.each:
                    shutil.rmtree(self._tmp, ignore_errors=True)

                # (S) Installer --> Cleanse previously installed MCP tools
                with context("that has been cleansed"):
                    with before.each:
                        Installer.create(ide="Cursor", path=self.tree, repo=_REPO_ROOT).clean()

                    with it("should keep the MCP manifest so Cursor stays connected to the cdd server"):
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
                    Installer.create(ide="Cursor", path=self.cursor, repo=_REPO_ROOT).install([SampleMcpOps()])

                with after.each:
                    shutil.rmtree(self._tmp, ignore_errors=True)
                    if self._user_mcp_before is None:
                        if self._user_mcp.is_file():
                            self._user_mcp.unlink()
                    else:
                        self._user_mcp.write_text(self._user_mcp_before, encoding="utf-8")

                with it("should name the project root on every request from the project mcp.json"):
                    data = json.loads((self.cursor / "mcp.json").read_text(encoding="utf-8"))
                    expect(data["mcpServers"]["cdd"]["headers"]).to(equal({"X-CDD-Project": str(self.project.resolve())}))

                with it("should leave the user Cursor mcp.json unchanged"):
                    data = json.loads(self._user_mcp.read_text(encoding="utf-8"))
                    expect(data["mcpServers"]["cdd"]["command"]).to(equal("python"))

            # (S) Installer --> Generate Installer Skill
            with context("with the installer toolset as the only deploy subject"):
                with before.each:
                    self._tmp = tempfile.mkdtemp()
                    self.tree = Path(self._tmp)
                    self.mcp = Installer.create(ide="Cursor", path=self.tree, repo=_REPO_ROOT).install(
                        [Installer.create(ide="Cursor", path=self.tree, repo=_REPO_ROOT)]
                    ).of(McpInstallation)

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
                        Installer.create(ide="Cursor", path=tree, repo=_REPO_ROOT).install_self()
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
                            Installer.create(ide="Cursor", path=tree, repo=_REPO_ROOT).install(
                                [ToolsetReference.parsed("no.such.module:Nope")]
                            )

                        expect(run).to(raise_error(ToolsetInstallFailed))
                    finally:
                        shutil.rmtree(tree, ignore_errors=True)

            # (S) Installer --> Diagnose the finished install
            with context("with a previous install on the diagnostics log"):
                with before.each:
                    self._branch_tmp = tempfile.mkdtemp()
                    self.tree = Path(self._branch_tmp)
                    self.installer = Installer.create(ide="Cursor", path=self.tree, repo=_REPO_ROOT)
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
                        expect(report).to(contain("cdd server:"))
                        expect(report).not_to(contain("hook server:"))
                        expect(report).to(contain("hooks registered (events):"))

                    with it("should mark the install green"):
                        expect(self.installer.diagnose_install()).to(contain("green"))

                    with it("should record install channels in the diagnosis"):
                        expect(_recorded_diagnosis(self.installer).report).to(contain("skill 1 -> 1 (delta 0)"))

                    with it("should append this install to the diagnostics log"):
                        _recorded_diagnosis(self.installer)
                        expect(len(json.loads(self.log.read_text(encoding="utf-8"))["installs"])).to(
                            equal(2)
                        )

                    with it("should record the latest skill count on that install"):
                        _recorded_diagnosis(self.installer)
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
                        _recorded_diagnosis(self.installer)
                        names = [item["name"] for item in _last_logged_install(self.log)["diagnostics"]]
                        expect(names).to(contain("diagnose_install"))

            with context("whose install standup has finished on the IDE path"):
                with before.each:
                    self.machine = ThrowawayMachine()
                    self.machine.enter()

                with after.each:
                    self.machine.leave()

                with it("should leave the cdd server answering"):
                    installer = Installer.create(ide="Cursor", path=_REPO_ROOT / ".cursor", repo=_REPO_ROOT)
                    expect(InstallRun(installer, [], replace=False).ensure_running()[0]).to(start_with("mcp: running"))

                with it("should start no hook server, which the hook command starts on the first event"):
                    installer = Installer.create(ide="Cursor", path=_REPO_ROOT / ".cursor", repo=_REPO_ROOT)
                    expect([line for line in InstallRun(installer, [], replace=False).ensure_running() if line.startswith("hook")]).to(equal([]))

            with context("that resolves deploy imports and toolsets from the repo catalog"):
                with before.each:
                    self.repo = Path(__file__).resolve().parents[2]
                    RepositoryToolsets(self.repo).ensure_import_path()

                with it("should not collect toolsets under examples folders"):
                    refs = [str(reference) for reference in RepositoryToolsets(self.repo).references()]
                    expect(any("examples" in ref.replace("\\", "/") for ref in refs)).to(equal(False))
                    expect(any("car_story" in ref for ref in refs)).to(equal(False))

                with it("should collect deployable toolsets under harness and patterns"):
                    refs = [str(reference) for reference in RepositoryToolsets(self.repo).references()]
                    expect(refs).to(contain("cdd_guidance.patterns.lern_domain_driven.lern_domain_driven:LernDomainDriven"))
                    expect(refs).to(contain("cdd_guidance.patterns.mern_domain_driven.mern_domain_driven:MernDomainDriven"))
                    expect(refs).to(contain("harness.graph.graph:Graph"))
                    expect(refs).to(contain("harness.guidance.guidance:Guidance"))
                    expect(refs).not_to(contain("harness.guidance.guidance:PracticeGuidance"))
                    expect(refs).not_to(contain("harness.guidance.guidance:FidelityGuidance"))

                with it("should put catalog folders on sys.path so short catalog imports resolve"):
                    import harness.agent_tools as agent_tools
                    import harness.guidance_actions as guidance_actions

                    toolsets = RepositoryToolsets(self.repo)
                    expect("agent_toolset" in dir(agent_tools)).to(equal(True))
                    expect(guidance_actions.GuidanceAction.__name__).to(equal("GuidanceAction"))
                    expect(toolsets.pythonpath()).to(contain("actions"))
                    expect(toolsets.pythonpath()).to(contain("patterns"))
                    expect(toolsets.pythonpath()).not_to(contain(str(self.repo / "harness" / "installation") + os.sep))
                    expect(toolsets.pythonpath().split(os.pathsep)).not_to(
                        contain(str(self.repo / "harness"))
                    )

                with it("should not record a temp install path in the shared install state"):
                    shared = Path(__file__).resolve().parent / ".install-state.json"
                    before = shared.read_text(encoding="utf-8") if shared.is_file() else ""
                    tmp = tempfile.mkdtemp()
                    try:
                        Installer.create(ide="Cursor", path=tmp, repo=self.repo).install([])
                        after = shared.read_text(encoding="utf-8") if shared.is_file() else ""
                        expect(after).to(equal(before))
                        expect(
                            Installer.create(path=tmp, repo=self.repo).record.path.parent
                        ).to(equal(Path(tmp)))
                    finally:
                        shutil.rmtree(tmp, ignore_errors=True)

# (E) Install CDD Tools
# (E) Install Practice Guidance Class
with description("a practice guidance class") as self:
    with before.all:
        self.machine = ThrowawayMachine()
        self.machine.enter()

    with after.all:
        self.machine.leave()

    # (S) Installer --> Deploy Practice guidance instructions
    with context("with instructions"):
        with before.each:
            self._tmp = tempfile.mkdtemp()
            self.tree = Path(self._tmp)
            self.tool = SamplePracticeGuidance(format="markdown")
            self.installer = Installer.create(ide="Cursor", path=self.tree, repo=_REPO_ROOT)
            self.mcp = self.installer.install([self.tool]).of(McpInstallation)

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
            from harness.installation.files import SkillInstallation

            overview = "sample preamble"
            writer = SkillInstallation.into(InstallTarget(IdeLayout("Cursor"), self.tree))
            tool = type("Tool", (), {"toolset": type("Host", (), {"overview": overview})()})()
            text = writer.front_matter(
                tool, Path("skills") / "sample-tool" / "SKILL.md", [overview, "Use MCP tool: `sample-tool.instructions()`"], ""
            )
            expect(text).to(contain("sample preamble"))
            expect(text).not_to(contain("Use MCP tool:"))

        with context("with an overview that opens with its heading and closes with a rule"):
            with before.each:
                from harness.installation.files import CommandInstallation, RulesInstallation, SkillInstallation

                overview = "## Overview\n\nsample preamble\n\nsecond paragraph\n\n---"
                writer = SkillInstallation.into(InstallTarget(IdeLayout("Cursor"), self.tree))
                self.description = writer._skill_overview(type("Host", (), {"overview": overview})(), [overview])

            with it("should describe the skill with the opening paragraph alone"):
                expect(self.description).to(equal("sample preamble"))

        with context("with guidance that links a shared reference file and names a rule file"):
            with before.each:
                from harness.installation.files import RulesInstallation

                self.text = "See [tools](../../references/language-tools.md); follow `practices/ddd/ddd-model.mdc`."
                self.dest = self.tree / "rules" / "practices" / "ddd" / "ddd-model.md"
                self.writer = RulesInstallation.into(InstallTarget(IdeLayout("Claude"), self.tree), RepositoryToolsets(_REPO_ROOT))

            with it("should copy the shared file into the IDE references folder"):
                self.writer._with_installed_references(self.text, self.dest)
                expect((self.tree / "references" / "language-tools.md").is_file()).to(be_true)

            with it("should link the shared file from where the guidance is installed"):
                text = self.writer._with_installed_references(self.text, self.dest)
                expect(text).to(contain("](../../../references/language-tools.md)"))

            with it("should name the rule file with the IDE's extension"):
                text = self.writer._with_installed_references(self.text, self.dest)
                expect(text).to(contain("`practices/ddd/ddd-model.md`"))

        with context("with an always-on rule in cdd_guidance/rules"):
            with before.each:
                self.source = self.tree / "source" / "coding.mdc"
                self.source.parent.mkdir(parents=True)
                self.source.write_text(
                    '---\ndescription: "Coding rules"\nalwaysApply: true\nglobs: "**/*.py"\n---\n\nKeep seams small.\n',
                    encoding="utf-8",
                )

            with context("installed for Claude Code"):
                with before.each:
                    from harness.installation.files import RulesInstallation

                    RulesInstallation.into(InstallTarget(IdeLayout("Claude"), self.tree), RepositoryToolsets(_REPO_ROOT)).write_standing_rule(self.source)
                    self.text = (self.tree / "rules" / "coding.md").read_text(encoding="utf-8")

                with it("should load in every session, with no paths"):
                    expect(self.text).not_to(contain("paths:"))

                with it("should keep the rule's description and body"):
                    expect(self.text).to(equal('---\ndescription: "Coding rules"\n---\n\nKeep seams small.\n'))

            with context("installed for Cursor"):
                with it("should keep the source front matter as an .mdc rule"):
                    from harness.installation.files import CommandInstallation, RulesInstallation, SkillInstallation

                    RulesInstallation.into(InstallTarget(IdeLayout("Cursor"), self.tree), RepositoryToolsets(_REPO_ROOT)).write_standing_rule(self.source)
                    text = (self.tree / "rules" / "coding.mdc").read_text(encoding="utf-8")
                    expect(text).to(equal(self.source.read_text(encoding="utf-8")))

        with it("should not append a YAML CLI invoke fence to the skill body"):
            skill = InstalledTree(self.tree).skill_path("sample-tool").read_text(encoding="utf-8")
            expect(skill).not_to(contain("tools.ps1"))
            expect(skill).not_to(contain("toolset:"))

        with it("should return the instructions the property assembles when the installed tool is invoked"):
            server = _server_publishing(self.mcp)
            result = server.invoke("sample-tool.instructions")
            expect(result).to(equal(self.tool.instructions))

        with context("with an underscored practice module path"):
            with it("should kebab-case the practice folder to match fidelity skill names"):
                from harness.installation.files import SkillInstallation

                writer = SkillInstallation.into(InstallTarget(IdeLayout("Cursor"), Path(".")))
                tool = _own_skill_tool(InstalledName(Path("cdd_guidance/practices/sample_tool"), is_own=True))
                expect(writer.relative_path(tool).as_posix()).to(equal("skills/practices/sample-tool/SKILL.md"))

    # (S) Installer --> Deploy Practice guidance rules
    with context("with rules"):
        with before.each:
            self._tmp = tempfile.mkdtemp()
            self.tree = Path(self._tmp)
            self.tool = SamplePracticeGuidance(format="markdown")
            self.installer = Installer.create(ide="Cursor", path=self.tree, repo=_REPO_ROOT)
            self.mcp = self.installer.install([self.tool]).of(McpInstallation)

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
                Installer.create(ide="Cursor", path=self.tree, repo=_REPO_ROOT).install(
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
                from harness.agent_tools.agent_tools import ToolsetReference

                Car = ToolsetReference.parsed("cdd_guidance.practices._examples.car.car:Car").toolset_class
                from cdd_guidance.actions._examples.car_story.car_story import CarStory

                self._branch_tmp = tempfile.mkdtemp()
                self._car_tree = Path(self._branch_tmp)
                Installer.create(ide="Cursor", path=self._car_tree, repo=_REPO_ROOT).install(
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
            self.mcp = Installer.create(ide="Cursor", path=self.tree, repo=_REPO_ROOT).install([self.tool]).of(McpInstallation)

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

        with context("with an underscored module path and fidelity folders under it"):
            with it("should keep the practice folder and name the leaf practice-fidelity"):
                from harness.installation.files import SkillInstallation

                writer = SkillInstallation.into(InstallTarget(IdeLayout("Cursor"), Path(".")))
                installed = InstalledName(Path("cdd_guidance/practices/sample_tool"), "sample-tool-sketch", is_own=True)
                expect(
                    writer.relative_path(_own_skill_tool(installed)).as_posix()
                ).to(equal("skills/practices/sample-tool/sample-tool-sketch/SKILL.md"))

            with it("should kebab-case the practice parent so it matches the fidelity leaf"):
                from harness.installation.files import SkillInstallation

                writer = SkillInstallation.into(InstallTarget(IdeLayout("Cursor"), Path(".")))
                installed = InstalledName(Path("cdd_guidance/practices/sample_tool"), "sample-tool-spec", is_own=True)
                expect(
                    writer.relative_path(_own_skill_tool(installed)).as_posix()
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
                server = _server_publishing(self.mcp)
                sketch = self.tool.fidelities.entries["sketch"]
                result = server.invoke("sample-tool-sketch")
                expect(result).to(equal(sketch.instructions))

            with context("from stories"):
                with before.each:
                    from cdd_guidance.practices.stories.stories import Stories

                    self._branch_tmp = tempfile.mkdtemp()
                    self.tree = Path(self._branch_tmp)
                    self.tool = Stories()
                    self.mcp = Installer.create(ide="Cursor", path=self.tree, repo=_REPO_ROOT).install(
                        [self.tool]
                    ).of(McpInstallation)
                    self.server = _server_publishing(self.mcp)

                with after.each:
                    shutil.rmtree(self._branch_tmp, ignore_errors=True)

                with it("should enroll nested fidelity instructions under the fidelity slug"):
                    expect("stories-scenarios" in self.server.prompts).to(equal(True))

                with it("should return that fidelity's instructions when the installed tool is invoked"):
                    scenarios = self.tool.fidelities.entries["scenarios"]
                    result = self.server.invoke("stories-scenarios")
                    expect(result).to(equal(scenarios.instructions))

            with context("that has been installed for VS Code"):
                with before.each:
                    self._branch_tmp = tempfile.mkdtemp()
                    self.tree = Path(self._branch_tmp)
                    Installer.create(ide="VS Code", path=self.tree, repo=_REPO_ROOT).install(
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
    with before.all:
        self.machine = ThrowawayMachine()
        self.machine.enter()

    with after.all:
        self.machine.leave()

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
                    self.mcp = Installer.create(ide="Cursor", path=self.tree, repo=_REPO_ROOT).install(
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
                    ).of(McpInstallation)

                with after.each:
                    tmp = getattr(self, "_tmp", None)
                    if tmp:
                        shutil.rmtree(tmp, ignore_errors=True)

                with it("should write a skill file for each operation annotated as a skill"):
                    expect(InstalledTree(self.tree).skill_names()).to(
                        equal(
                            {
                                "answer-board-comment",
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

                with it("should keep a single matching operation at the toolset folder"):
                    expect(
                        (self.tree / "skills" / "actions" / "generate" / "SKILL.md").is_file()
                    ).to(equal(True))

                with it("should name a single unmatched operation for the operation not the toolset folder"):
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
                    self.mcp = Installer.create(ide="Cursor", path=self.tree, repo=_REPO_ROOT).install(
                        [Improvement()]
                    ).of(McpInstallation)

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
                    self.mcp = Installer.create(ide="Cursor", path=self.tree, repo=_REPO_ROOT).install(
                        [Generate()]
                    ).of(McpInstallation)

                with after.each:
                    tmp = getattr(self, "_tmp", None)
                    if tmp:
                        shutil.rmtree(tmp, ignore_errors=True)

                with it("should record that operation"):
                    expect([op.mcp_name for op in self.mcp.mcp_operations]).to(
                        equal(["generate.generate"])
                    )

                with it("should return that operation's instructions when the installed tool is invoked"):
                    server = _server_publishing(self.mcp)
                    result = server.invoke("generate.generate")
                    expect(str(result)).to(contain("Write artifacts for each listed guidance"))

            # (S) Installer --> Install Lifecycle actions as several tools
            with context("with several MCP operations"):
                with before.each:
                    from cdd_guidance.actions.improvement.improvement import Improvement
                    from cdd_guidance.actions.validate.validate import Validate

                    self._tmp = tempfile.mkdtemp()
                    self.tree = Path(self._tmp)
                    self.mcp = Installer.create(ide="Cursor", path=self.tree, repo=_REPO_ROOT).install(
                        [Improvement(), Validate()]
                    ).of(McpInstallation)

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
                    expect("validate.create_rule" in names).to(equal(False))

with description("guidance agents"):
    with before.all:
        self.machine = ThrowawayMachine()
        self.machine.enter()

    with after.all:
        self.machine.leave()

    with it("should install the agents from cdd_guidance/agents"):
        tree = Path(tempfile.mkdtemp())
        try:
            InstallRun(Installer.create(ide="Cursor", path=tree, repo=_REPO_ROOT), [], replace=False)._install_agents()
            installed = sorted(path.name for path in (tree / "agents").glob("*.md"))
            expect(installed).to(equal([
                "context.md", "discoverer.md", "exploratory-testing-supervisor.md", "exploratory-testing-tester.md",
                "implementation.md", "specification.md",
            ]))
            expect((tree / "agents" / "discoverer.md").read_text(encoding="utf-8")).to(contain("name: discoverer"))
            expect(((_REPO_ROOT / "cdd_guidance" / "agents" / "discovery.md").is_file())).to(equal(True))
        finally:
            shutil.rmtree(tree, ignore_errors=True)

with description("an operation annotated as a Cursor hook"):
    with before.all:
        self.machine = ThrowawayMachine()
        self.machine.enter()

    with after.all:
        self.machine.leave()


    with context("that names a documented Cursor event"):
        with it("should store that event on the member"):
            for event in sorted(Hook.EVENTS):

                @hook(event)
                def handler(self, payload: dict) -> dict:
                    return {}

                expect(Hook.annotates(handler)).to(equal(True))
                expect(Hook.recorded_on(handler).name).to(equal(event))

    with context("that names an unknown event"):
        with it("should raise ValueError"):
            expect(HookDecoration().unknown_event).to(raise_error(ValueError))

    with context("that omits the event"):
        with it("should raise ValueError"):
            expect(HookDecoration().omitted_event).to(raise_error(ValueError))

# (S) Installer --> Install for Claude Code
with description("toolsets installed for Claude Code") as self:
    with before.all:
        self.machine = ThrowawayMachine()
        self.machine.enter()

    with after.all:
        self.machine.leave()

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
        Installer.create(ide="Claude", path=self.tree, repo=_REPO_ROOT).install(
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
        expect(servers["cdd"]["headers"]).to(equal({"X-CDD-Project": str(self.project.resolve())}))
        expect((self.tree / "mcp.json").exists()).to(equal(False))

    # Claude Code loads a plugin it installed from a copy in its own cache, which a later publish never reaches, so a chat
    # kept a queue bar with no Flush after the mod gained one. Every cdd plugin is loaded from its published folder instead.
    with context("installing a cdd plugin"):
        with before.each:
            self.plugins = _ScriptedClaude(listed="")

        with after.each:
            shutil.rmtree(self.plugins.claude_folder, ignore_errors=True)
            shutil.rmtree(self.plugins.home_folder, ignore_errors=True)

        with context("that Claude Code does not load yet"):
            with before.each:
                self.answer = str(self.plugins.install(_QUEUE))

            # The folder Claude Code watches never changes, so a repin and a reload of the plugins reach every chat.
            with it("should name the cdd home's fixed folder for it in CLAUDE_CODE_PLUGIN_DIRS"):
                expect(self.plugins.watched_folders).to(contain(str(self.plugins.chat_folder("prompt-queue"))))

            with it("should have the fixed folder lead to its published folder"):
                expect(self.plugins.chat_folder("prompt-queue").resolve()).to(equal(_QUEUE.folder.resolve()))

            with it("should keep the folders the settings named already"):
                expect(self.plugins.watched_folders).to(contain(_ScriptedClaude.OWN_FOLDER))

            # Claude Code reads CLAUDE_CODE_PLUGIN_DIRS when it starts, so a chat open now loads the folder only after a restart.
            with it("should say Claude must restart to load it"):
                expect(self.answer).to(equal(PluginInstall.NEWLY_WATCHED))

            with it("should run no claude command"):
                expect(self.plugins.calls).to(equal([]))

        with context("that Claude Code loads from its folder already"):
            with before.each:
                self.plugins.install(_QUEUE)
                self.answer = str(self.plugins.install(_QUEUE))

            with it("should say it is watched"):
                expect(self.answer).to(equal(PluginInstall.WATCHED))

            with it("should name its folder once"):
                expect(self.plugins.watched_folders.count(str(self.plugins.chat_folder("prompt-queue")))).to(equal(1))

        # A repin moves the plugin to the lane the person approved: the fixed folder follows, and the settings stay as they are.
        with context("that the approved lane publishes from another folder"):
            with before.each:
                self.plugins.install(_QUEUE)
                self.moved = _Published("prompt-queue", "0.1.0-dev")
                self.moved.folder = Path(tempfile.gettempdir()) / "cdd-home" / "dev" / "claude-plugins" / "prompt-queue"
                self.moved.folder.mkdir(parents=True, exist_ok=True)
                self.answer = str(self.plugins.install(self.moved))

            with it("should have the fixed folder lead to the approved lane's folder"):
                expect(self.plugins.chat_folder("prompt-queue").resolve()).to(equal(self.moved.folder.resolve()))

            with it("should say it is watched, so a reload of the plugins loads it"):
                expect(self.answer).to(equal(PluginInstall.WATCHED))

        # A lane's or an older home's copy of the same plugin, named too, would load the plugin twice.
        with context("that the settings name from another published folder"):
            with before.each:
                self.plugins.watch_folders(str(Path("elsewhere") / "claude-plugins" / "prompt-queue"))
                self.plugins.install(_QUEUE)

            with it("should name only its own published folder"):
                expect([f for f in self.plugins.watched_folders if f.endswith("prompt-queue")]).to(equal([str(self.plugins.chat_folder("prompt-queue"))]))

        # A served checkout's own mod folder, named by an older install, holds the plugin under another folder name, so
        # Claude Code loaded it twice: once from there and once from the fixed folder.
        with context("that the settings name a checkout's own folder of it"):
            with before.each:
                self.checkout_folder = self.plugins.home_folder / "checkout" / "tools" / "prompt_queue"
                (self.checkout_folder / ".claude-plugin").mkdir(parents=True)
                (self.checkout_folder / ".claude-plugin" / "plugin.json").write_text(json.dumps({"name": "prompt-queue"}), encoding="utf-8")
                self.plugins.watch_folders(str(self.checkout_folder))
                self.plugins.install(_QUEUE)

            with it("should name only the fixed folder for it"):
                expect(self.plugins.watched_folders).not_to(contain(str(self.checkout_folder)))

        with context("that Claude Code has a cached copy of"):
            with before.each:
                self.plugins.plugins_installed = {"prompt-queue@cdd-home": "0.1.0-old", "cdd-board@cdd-home": "0.6.3-abc"}
                self.answer = str(self.plugins.install(_QUEUE))

            with it("should uninstall the cached copy"):
                expect(self.plugins.calls).to(contain(("plugin", "uninstall", "prompt-queue@cdd-home", "--scope", "user")))

            with it("should leave other plugins' copies alone"):
                expect([c for c in self.plugins.calls if "cdd-board@cdd-home" in c]).to(equal([]))

            with it("should still name its fixed folder"):
                expect(self.plugins.watched_folders).to(contain(str(self.plugins.chat_folder("prompt-queue"))))

        # A mod installed from a checkout's own marketplace runs that branch's code, not the server's.
        with context("that is installed from a checkout's own marketplace"):
            with it("should uninstall it and remove that marketplace"):
                self.plugins.plugins_installed = {"cdd-board@abd-works": "0.6.3"}
                self.plugins.install(_BOARD)
                expect(self.plugins.calls).to(equal([
                    ("plugin", "uninstall", "cdd-board@abd-works", "--scope", "user"),
                    ("plugin", "marketplace", "remove", "abd-works"),
                ]))

        with context("with a cached copy and no claude command"):
            with it("should say the cached copy is still there"):
                self.plugins.plugins_installed = {"cdd@cdd-home": "1.0.0"}
                self.plugins.cli = None
                expect(str(self.plugins.install(_CDD))).to(equal(PluginInstall.CACHED))

    with context("finding Claude Code in the desktop app"):
        with before.each:
            self.local = Path(tempfile.mkdtemp(prefix="cdd-local-app-data-"))
            self.saved = {name: os.environ.get(name) for name in ("APPDATA", "LOCALAPPDATA")}
            os.environ["APPDATA"] = str(self.local / "Roaming")
            os.environ["LOCALAPPDATA"] = str(self.local)
            for version in ("2.1.200", "2.1.309"):
                found = self.local / "Claude-Data" / "claude_profile" / "claude-code" / version / "build" / "claude.exe"
                found.parent.mkdir(parents=True)
                found.write_text("", encoding="utf-8")

        with after.each:
            for name, value in self.saved.items():
                if value is None:
                    os.environ.pop(name, None)
                else:
                    os.environ[name] = value
            shutil.rmtree(self.local, ignore_errors=True)

        with context("that keeps it under a profile in its local data folder"):
            with it("should use the newest version there"):
                expected = self.local / "Claude-Data" / "claude_profile" / "claude-code" / "2.1.309" / "build" / "claude.exe"
                expect(ClaudePlugins().claude_cli).to(equal(str(expected)))

    with it("should install no hooks and leave the project's settings.json alone"):
        expect(self.settings).to(equal({"permissions": {"allow": ["Bash(ls)"]}}))
        expect((self.tree / "hooks.json").exists()).to(equal(False))
        expect((self.tree / "hook-handlers.json").exists()).to(equal(False))

    with context("with rules scoped by globs"):
        with it("should list each glob under paths"):
            from harness.installation.files import RulesInstallation

            text = RulesInstallation.into(InstallTarget(IdeLayout("Claude"), Path(".")))._claude_rules_front_matter(
                "d", "**/*.py, **/*.ts"
            )
            expect(text).to(equal('---\ndescription: "d"\npaths:\n  - "**/*.py"\n  - "**/*.ts"\n---\n\n'))


with description("Repo branch commands installed into Cursor") as self:
    with before.all:
        self.machine = ThrowawayMachine()
        self.machine.enter()

    with after.all:
        self.machine.leave()

    with before.each:
        self._tmp = tempfile.mkdtemp()
        self.tree = Path(self._tmp)
        self.mcp = Installer.create(ide="Cursor", path=self.tree, repo=_REPO_ROOT).install(
            [ToolsetReference.parsed("space.repo.repo:Repo")]
        ).of(McpInstallation)

    with after.each:
        shutil.rmtree(self._tmp, ignore_errors=True)

    with it("should write push naming repo.push_commit"):
        path = self.tree / "commands" / "space" / "repo" / "push.md"
        expect(path.read_text(encoding="utf-8")).to(contain("repo.push_commit"))

    with it("should not write the retired new-branch command"):
        path = self.tree / "commands" / "space" / "repo" / "new-branch.md"
        expect(path.is_file()).to(equal(False))

    with it("should enroll repo.push_commit on the MCP channel"):
        names = [op.mcp_name for op in self.mcp.mcp_operations]
        expect(names).to(contain("repo.push_commit"))
