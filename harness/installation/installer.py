"""Installer: install every toolset a repository defines into one IDE folder, through every destination."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable, TypeVar

from harness.agent_tools.agent_tools import (
    AgentTool,
    InvokeLine,
    AgentToolSet,
    InstallDestination,
    ToolsetConfiguration,
    ToolsetReference,
    agent_instructions,
    agent_tool,
    agent_toolset,
    tool_subject,
)
from harness.installation.destination import Installation, ServerInstallation, is_temporary, noCatalog
from harness.installation.files import FileChannel, FileInstallation, command
from harness.installation.ide_layout import IdeLayout
from harness.installation.install_diagnostics import InstallDiagnostics
from harness.installation.install_record import InstallRecord
from harness.installation.language_adapter import LanguageAdapterInstallation
from harness.installation.repository_toolsets import RepositoryToolsets
from harness.markdown import markdown
from harness.markdown.front_matter import FrontMatter

# The record of the last install into a project's own IDE folder; an install into a temporary folder keeps its record
# in that folder, so a spec's install never replaces the person's.
_SHARED_RECORD = Path(__file__).resolve().parent / InstallRecord.NAME

_Server = TypeVar("_Server", bound=ServerInstallation)


class ToolsetInstallFailed(Exception):
    """Publishing one toolset failed; the install stops so no IDE folder is left with part of a toolset."""

    def __init__(self, toolset: ToolsetConfiguration | ToolsetReference, cause: Exception) -> None:
        super().__init__(f"install failed for {toolset}: {type(cause).__name__}: {cause}")
        self.toolset = toolset
        self.cause = cause


class ServersNotRegistered(LookupError):
    """An install ran in a process where no server installation registered with the Installer, so it would write no
    MCP entry and no hooks. harness/mcp and harness/hooks register theirs when they are imported."""

    def __init__(self) -> None:
        super().__init__(
            "no server installation is registered with the Installer in this process: import harness.mcp.mcp_server "
            "and harness.hooks before installing"
        )


class InstallChannels:
    """The installations of one install run, made once and used for every member of every toolset: a file installation
    for each file channel, with and without MCP, the writer of the standing rules, the language adapters, and one
    installation of each server channel registered with the Installer. Each tracks the files it writes in the install
    record."""

    def __init__(self, installer: Installer, servers: Iterable[type[ServerInstallation]], *, installing: bool = False) -> None:
        layout, path, repo = installer.layout, installer.path, installer.repo
        # Whether these are the installations of an install that is running, rather than ones made to read a folder
        # an earlier install wrote; and the toolsets the install deployed, by their references.
        self.installing = installing
        self.deployed: list[str] = []
        self.servers = [kind(layout, path, repo=repo) for kind in servers]
        self.language_adapters = LanguageAdapterInstallation(layout, path, repo=repo)
        self._files = {
            (destination, mcp_mode): FileInstallation(layout, path, FileChannel(destination, mcp_mode), repo=repo)
            for destination in FileInstallation.CHANNELS
            for mcp_mode in (False, True)
        }
        self.standing_rules = FileInstallation(layout, path, FileChannel(InstallDestination.RULE), repo=repo)
        for installation in (*self.servers, self.language_adapters, *self._files.values(), self.standing_rules):
            installation.track_writes_with(lambda written: installer.record.track(written, installer.path))
        # The toolsets the server channels publish into every install, such as the hooks that start the cdd server.
        self.toolsets: list[Any] = [AgentToolSet.instantiate(toolset) for server in self.servers for toolset in server.toolsets]

    def of(self, kind: type[_Server]) -> _Server:
        """The run's installation of kind, such as its *McpInstallation*."""
        for installation in self.servers:
            if isinstance(installation, kind):
                return installation
        raise LookupError(f"no {kind.__name__} is registered with the Installer in this process")

    def for_tool(self, tool: AgentTool) -> list[Installation]:
        """Every installation tool is written through: each server channel that takes it, then each file channel its
        annotations name, written for MCP when the tool is also published there."""
        destinations = tool.destinations
        mcp_mode = InstallDestination.MCP in destinations
        files = [self._files[(destination, mcp_mode)] for destination in FileInstallation.CHANNELS if destination in destinations]
        return [*(server for server in self.servers if server.accepts(tool)), *files]

    @property
    def published(self) -> dict[str, list[str]]:
        """What each server channel published in this run, by its channel, such as the MCP operations it enrolled."""
        return {server.channel: server.published for server in self.servers}


class ServerChannels:
    """The kinds of server installation every install publishes through, beside its file channels: harness/mcp and
    harness/hooks each register theirs when they are imported (``SERVER_CHANNELS.register(kind)``), so this module
    never imports them and a new server channel is one more registration. The process keeps one."""

    def __init__(self) -> None:
        self._kinds: list[type[ServerInstallation]] = []

    def register(self, kind: type[ServerInstallation]) -> None:
        """Have every install publish through an installation of kind too, and start the server it points at."""
        if kind not in self._kinds:
            self._kinds.append(kind)

    @property
    def kinds(self) -> list[type[ServerInstallation]]:
        """Each kind registered, in the order it registered; an install with none stops with *ServersNotRegistered*."""
        if not self._kinds:
            raise ServersNotRegistered()
        return list(self._kinds)


SERVER_CHANNELS = ServerChannels()


class Deployment:
    """One installer's publishing of the repository's toolsets into its IDE folder: a run writes every channel's files,
    tidies the folder and saves the install record, stands each server up and starts it, then diagnoses what it wrote.
    The installer holds one (``installer.deployment``), made with it, and its published tools run through it."""

    def __init__(self, installer: Installer) -> None:
        self._installer = installer
        self._channels: InstallChannels | None = None
        self.diagnosis: list[str] = []

    @property
    def channels(self) -> InstallChannels:
        """The installations of the last run, or of a run not yet made, to read a folder an earlier install wrote."""
        if self._channels is None:
            self._channels = InstallChannels(self._installer, SERVER_CHANNELS.kinds)
        return self._channels

    def run(self, toolsets: Iterable[ToolsetConfiguration] | None, replace: bool) -> InstallChannels:
        """Publish toolsets, every toolset the repository defines when none are named; replace wipes the previous
        install first."""
        installer = self._installer
        if replace:
            installer.clean()
        else:
            installer.record.keep_existing(installer.path)
        installer.toolsets.ensure_import_path()
        items = self._repository_toolsets() if toolsets is None else list(toolsets)
        channels = self._channels = InstallChannels(installer, SERVER_CHANNELS.kinds, installing=True)
        self._publish_every_toolset(items, channels)
        self._save_installed_files(replace)
        self._standup_channels()
        self._report_diagnosis()
        return channels

    def install_self(self, *, replace: bool = False) -> InstallChannels:
        """Deploy only the Installer toolset — ``/install``, ``/clean`` — and the toolsets the server channels publish
        into every install, such as the hooks that start the cdd server."""
        return self.run([], replace=replace)

    def _publish_every_toolset(self, items: list[ToolsetConfiguration], channels: InstallChannels) -> None:
        """Write every channel's files for items, the Installer, and the toolsets the server channels publish, then the
        language adapters, the agents, and the standing rules."""
        self._install_all(items)
        for toolset in (self._installer, *channels.toolsets):
            self._install_toolset(toolset)
        channels.language_adapters.write_all()
        self._install_agents()
        self._install_standing_rules()

    def _save_installed_files(self, replace: bool) -> None:
        """Tidy the folder this run wrote into and save its record."""
        installer = self._installer
        if replace:
            # Only after a full wipe and republish do the enrolled MCP names hold the whole catalog; a partial install
            # must not delete skills for toolsets not in this run.
            self._remove_skills_naming_missing_mcp()
        installer.record.prune_empty_skill_folders(installer.path)
        installer.record.save(installer.ide, installer.path)

    def _report_diagnosis(self) -> None:
        """Diagnose the finished install, printing each red report."""
        self.diagnosis = self.diagnose_after_install()
        for report in self.diagnosis:
            if report.startswith("!"):
                print(report, file=sys.stderr)

    def write_language_adapters(self) -> list[Path]:
        """Write the TypeScript language adapters from the repository's toolsets as they are now, and nothing else. A
        page built against adapters an earlier install wrote reads the data the server sent then, so a field added since,
        such as a backlog item's children, is missing from it and the page fails; switching the server's code writes
        them first, then rebuilds its pages."""
        installer = self._installer
        installer.toolsets.ensure_import_path()
        adapters = LanguageAdapterInstallation(installer.layout, installer.path, repo=installer.repo)
        server_toolsets = [toolset for server in SERVER_CHANNELS.kinds for toolset in server.toolsets]
        for item in [*self._repository_toolsets(), *server_toolsets]:
            toolset = AgentToolSet.instantiate(item)
            for each in (toolset, *toolset.child_toolsets()):
                adapters.record(each)
        return adapters.write_all()

    def _repository_toolsets(self) -> list[type]:
        """The class of every toolset the repository defines; one whose module cannot be imported stops the install,
        named after the toolset, with its cause."""
        toolsets = self._installer.toolsets
        classes = toolsets.classes()
        for unloadable in toolsets.unloadable:
            raise ToolsetInstallFailed(unloadable.reference, unloadable.cause) from unloadable.cause
        return classes

    def _install_all(self, toolsets: Iterable[ToolsetConfiguration]) -> None:
        for item in toolsets:
            try:
                toolset = AgentToolSet.instantiate(item)
                self._install_toolset(toolset)
                for child in toolset.child_toolsets():
                    self._install_toolset(child)
            except ToolsetInstallFailed:
                raise
            # Any failure while publishing a toolset stops the install, named after the toolset, with its cause.
            except Exception as error:  # noqa: BLE001
                raise ToolsetInstallFailed(item, error) from error

    def _install_toolset(self, toolset: AgentToolSet) -> None:
        channels = self.channels
        if toolset.registration_name not in channels.deployed:
            channels.deployed.append(toolset.registration_name)
        for tool in toolset.tools.values():
            for installation in channels.for_tool(tool):
                installation.install(tool)
        channels.language_adapters.record(toolset)

    def _install_agents(self) -> None:
        """Copy cdd_guidance/agents into the IDE agents folder, each named as its front matter names it. The source
        stays on cdd_guidance."""
        installer = self._installer
        source = installer.toolsets.agents_folder
        if not source.is_dir():
            return
        for path in sorted(source.glob("*.md")):
            front_matter = FrontMatter.of_file(path)
            dest = installer.path / "agents" / f"{front_matter.fields.get('name') or path.stem}.md"
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(front_matter.text, encoding="utf-8")
            installer.record.track(dest, installer.path)

    def _install_standing_rules(self) -> None:
        """Install cdd_guidance/rules as always-on rules in the IDE rules folder."""
        source = self._installer.toolsets.standing_rules_folder
        if not source.is_dir():
            return
        rules = self.channels.standing_rules
        for path in sorted([*source.glob("*.md"), *source.glob("*.mdc")]):
            rules.write_standing_rule(path)

    def _remove_skills_naming_missing_mcp(self) -> list[str]:
        """Drop skill files that name an MCP tool this install did not enroll.

        Orphan skills from a prior API (for example ``branch.create`` after the
        tool became ``repo.new_branch``) survive ``clean`` when they were never
        tracked. Agents then thrash searching for a tool that cannot exist.
        Skills without an MCP invoke line are left alone (hand-authored orphans).
        """
        skills = self._installer.path / "skills"
        if not skills.is_dir():
            return []
        enrolled = set(self.channels.published.get(InstallDestination.MCP, []))
        return [self._remove_skill(path) for path in skills.rglob("SKILL.md") if self._names_missing_mcp(path, enrolled)]

    def _names_missing_mcp(self, skill: Path, enrolled: set[str]) -> bool:
        """Whether the skill file names an MCP tool, and one of them is not among the enrolled names."""
        names = InvokeLine(skill.read_text(encoding="utf-8")).names
        return bool(names) and not all(name in enrolled for name in names)

    def _remove_skill(self, skill: Path) -> str:
        """Delete the skill file and forget it in the record; answer its path from the IDE folder."""
        installer = self._installer
        relative = skill.resolve().relative_to(installer.path.resolve()).as_posix()
        skill.unlink()
        installer.record.prune_empty_parents(skill, installer.path)
        installer.record.forget(relative)
        return relative

    def _standup_channels(self) -> None:
        """Stand up each server over what was installed, to check it loads, then start the servers. An install that
        runs inside one of those servers, as an install through MCP runs inside the cdd server, starts none: they are
        already running, and starting them again would reload every toolset in the middle of a request."""
        for server in self.channels.servers:
            server.standup()
            self._print_channel_notice(server.diagnose())
        if not is_temporary(self._installer.path) and not self._runs_inside_a_server():
            self.ensure_runtimes()

    def ensure_runtimes(self) -> dict[str, str]:
        """Start the server behind every channel the install wrote; fail if one stays down."""
        status: dict[str, str] = {}
        for server in self.channels.servers:
            status.update(server.ensure_running())
        print(", ".join(f"{name}: {value}" for name, value in status.items()), file=sys.stderr)
        return status

    def _runs_inside_a_server(self) -> bool:
        return any(server.serves_this_process() for server in self.channels.servers)

    def _print_channel_notice(self, diagnosis: dict[str, Any]) -> None:
        notice = diagnosis.get("notice") or ""
        if notice:
            print(notice, file=sys.stderr)

    def diagnose_after_install(self) -> list[str]:
        """Record install-channel diagnostics only; guidance probes use ``/guidance-diagnostics``."""
        report = self._installer.diagnose_install()
        self._installer.diagnostics.record_run(self.channels, report)
        return [report]


@noCatalog
@agent_toolset
class Installer:
    """Publish every annotated member of the toolsets a repository defines into one IDE folder, through the installation
    of each channel its annotations name, then start the servers the installed files point at.

    The files of skills, commands, rules, and language adapters are written by its *Deployment* (``deployment``). The
    MCP and hook channels each point the IDE at a server, and harness/mcp and harness/hooks register their installation
    with ``SERVER_CHANNELS`` when they are imported, so this module never imports them."""

    def __init__(self, ide: str | None = None, path: str | Path | None = None, *, repo: str | Path) -> None:
        self.repo = Path(repo).resolve()
        last = InstallRecord(_SHARED_RECORD).saved if ide is None and path is None else {}
        self.ide = ide or last.get("ide") or IdeLayout.DEFAULT_IDE
        self.layout = IdeLayout(self.ide)
        self.path = Path(path) if path is not None else self._last_or_default_folder(last.get("path"))
        self.record = InstallRecord(self.path / InstallRecord.NAME if is_temporary(self.path) else _SHARED_RECORD)
        self.diagnostics = InstallDiagnostics(self.path, self.layout)
        self.toolsets = RepositoryToolsets(self.repo)
        self.deployment = Deployment(self)

    @classmethod
    @tool_subject
    def load(cls, *, project: Path | str) -> Installer:
        """The installer of project, the folder the call names, into the IDE folder it last installed into."""
        return cls(repo=project)

    @command(name="clean")
    @agent_tool
    def clean(self) -> list[str]:
        """Remove files from the previous install on this IDE path."""
        removed = self.record.remove_installed(self.path)
        self.record.prune_empty_skill_folders(self.path)
        return removed

    @command(name="install")
    @agent_tool
    def install(
        self,
        toolsets: Iterable[Any] | None = None,
        replace: bool = True,
    ) -> Any:
        """Install CDD into ``.cursor`` (or ``.claude`` with ``--ide Claude``) — skills, commands, rules, MCP, and hooks. ``replace`` wipes the previous install first.

        Installer-only refresh (``/install`` and ``/clean`` without walking the catalog): ``python scripts/install.py --self`` from this repo — not MCP.

        Before you run it, write these steps in the chat as a checklist. Then, as each one completes, write ``✓`` and the step in the chat with what the output said for it, so the person follows the install as it goes:

        1. Install every toolset: skills, commands, rules, MCP, and hooks (the line ``hook: …, mcp: …, cdd plugin: …, board: …``).
        2. Check the cdd server runs, moved onto this commit when it ran an older one (``mcp: running (pid …)``, or ``cdd server: …``).
        3. Read ``diagnostics.json`` in the install folder (latest ``diagnose_install`` report) and paste the full summary: color, channel deltas, cdd server, hook server, hooks registered.

        When a step fails, write ``✗`` and the step with its error, stop, and follow "When install fails" in ``harness/installation/installer.md``."""
        return self.deployment.run(toolsets, replace)

    @command(name="install-latest")
    @agent_tool
    def install_latest(self) -> int:
        """Pull origin main and reinstall CDD on it, restarting every server, so this chat and the apps run the latest code.

        Before you run it, put these seven steps in your task list (in Claude Code, the plan the app shows under your message) and write them in the chat as a checklist:

        1. Pull origin main into this checkout. A pull that fails or conflicts stops here, before anything is stopped: tell the person and wait.
        2. Stop every app's server and the hook server.
        3. Restart the cdd server.
        4. Install every toolset: skills, commands, rules, MCP, and hooks. This is the long step, about a minute.
        5. Ping the cdd server.
        6. Reconnect this chat: when the cdd server reads failed, reconnect it, or ask the person to run ``/reload-plugins``.
        7. Read ``diagnostics.json`` in the install folder (latest ``diagnose_install`` report) and paste the summary: color, channel deltas, cdd server, hook server.

        Run the command in the background and watch its output as it runs, rather than waiting for it to end, so the person sees each step finish as it happens. The script writes ``▶ n/7 <step>`` as a step starts and ``✓ n/7 <step>: <result>`` as it is done. On each ``✓`` line, mark that step done in your task list and write the same line in the chat; on a ``✗ n/7`` line, write it, stop, and follow "When install fails" in ``harness/installation/installer.md``. Steps 6 and 7 are yours: mark and write each the same way once you have done it.

        Other chats share the cdd server, so message their sessions before you run it."""
        script = self.repo / "scripts" / "install-latest.py"
        return subprocess.run([sys.executable, str(script)], cwd=self.repo, check=False).returncode

    @agent_instructions
    def diagnose_install(self) -> str:
        """Compare this install with the last diagnostics.json entry and report counts, or what changed."""
        color, body = self.diagnostics.diagnosed(self.deployment.channels)
        return f"{color}\n{body}" if color != "red" else f"!\n{color}\n{body}\n{self.diagnose_instructions()}"

    def _last_or_default_folder(self, last: str | None) -> Path:
        if last and Path(last).exists() and not is_temporary(Path(last)):
            return Path(last)
        return self.repo / self.layout.folder_name

    @markdown("diagnose_install")
    def _diagnose_install_section(self) -> str:
        """The Diagnose Install section of installer.md."""

    @agent_instructions
    def diagnose_instructions(self) -> str:
        """How to diagnose an install whose deployed counts do not match."""
        return str(self._diagnose_install_section).strip()


__all__ = ["Installer"]
