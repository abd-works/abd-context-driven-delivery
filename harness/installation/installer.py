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

    ToolsetReference,
    agent_instructions,
    agent_tool,
    agent_toolset,
    tool_subject,
)
from harness.annotations.annotation import annotation_kinds, noCatalog
from harness.installation.destination import ChannelServer, Installation, RegisteredChannel
from harness.installation.install_target import is_temporary
from harness.installation.files import CommandInstallation, FileInstallation, RulesInstallation, SkillInstallation, command
from harness.installation.ide_layout import IdeLayout
from harness.installation.install_diagnostics import Deployed, InstallDiagnosis
from harness.installation.install_lock import InstallLock
from harness.installation.install_target import InstallTarget
from harness.installation.install_record import InstallRecord, LastInstall
from harness.installation.language_adapter import LanguageAdapters
from harness.installation.project_guidelines import PROJECT_GUIDELINES
from harness.installation.repository_toolsets import RepositoryToolsets
from harness.markdown import markdown
from harness.markdown.front_matter import FrontMatter

# Where this checkout keeps the IDE and folder it last installed into; each folder keeps the record of its own files.
_LAST_INSTALL = Path(__file__).resolve().parent / InstallRecord.NAME

_Channel = TypeVar("_Channel", bound=RegisteredChannel)


class ToolsetInstallFailed(Exception):
    """Publishing one toolset failed; the install stops so no IDE folder is left with part of a toolset."""

    def __init__(self, toolset: ToolsetReference | AgentToolSet, cause: Exception) -> None:
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
    """The installations of one install, made once and used for every member of every toolset: one installation of each
    file channel (skills, commands, rules), one of each channel registered with the Installer, and the language
    adapters. Each keeps the files it writes in the install record."""

    def __init__(self, installer: Installer, registered: Iterable[type[RegisteredChannel]]) -> None:
        target, record, repository = installer.target, installer.record, installer.toolsets
        # The toolsets the install deployed, by their references.
        self.deployed: list[str] = []
        self.registered = [kind.create(target, record, repository) for kind in registered]
        self.language_adapters = LanguageAdapters(target, record, repository)
        self.rules = RulesInstallation(target, record, repository)
        self.files: list[FileInstallation] = [SkillInstallation(target, record, repository), CommandInstallation(target, record, repository), self.rules]
        # The toolsets the registered channels publish into every install, such as the hooks that start the cdd server.
        self.toolsets: list[AgentToolSet] = [ToolsetReference.of(toolset).made() for channel in self.registered for toolset in channel.toolsets]

    def of(self, kind: type[_Channel]) -> _Channel:
        """The install's installation of kind, such as its *McpInstallation*."""
        for installation in self.registered:
            if isinstance(installation, kind):
                return installation
        raise LookupError(f"no {kind.__name__} is registered with the Installer in this process")

    def for_tool(self, tool: AgentTool) -> list[Installation]:
        """Every installation tool is written through: each registered channel that takes it, then each file channel
        install publishes it to."""
        return [
            *(channel for channel in self.registered if channel.accepts(tool)),
            *(installation for installation in self.files if tool.is_published_to(installation.destination)),
        ]

    @property
    def servers(self) -> list[ChannelServer]:
        """The server each registered channel points the IDE at; the hook channel holds none."""
        return [channel.server for channel in self.registered if channel.server is not None]

    @property
    def published(self) -> dict[str, list[str]]:
        """What each registered channel published in this install, by its channel, such as the MCP operations it
        enrolled."""
        return {channel.destination.channel: channel.published for channel in self.registered}


class ServerChannels:
    """The kinds of registered channel every install publishes through, beside its file channels: harness/mcp and
    harness/hooks each register theirs when they are imported (``SERVER_CHANNELS.register(kind)``), so this module
    never imports them and a new channel is one more registration. The process keeps one."""

    def __init__(self) -> None:
        self._kinds: list[type[RegisteredChannel]] = []

    def register(self, kind: type[RegisteredChannel]) -> None:
        """Have every install publish through an installation of kind too, and start the server it points at."""
        if kind not in self._kinds:
            self._kinds.append(kind)

    @property
    def kinds(self) -> list[type[RegisteredChannel]]:
        """Each kind registered, in the order it registered; an install with none stops with *ServersNotRegistered*."""
        if not self._kinds:
            raise ServersNotRegistered()
        return list(self._kinds)


SERVER_CHANNELS = ServerChannels()


class InstallRun:
    """One install of toolsets into an installer's IDE folder, every toolset the repository defines when none are named:
    it writes every channel's files (`publish`), tidies the folder and saves the install record, stands each channel's
    server up and starts it (`stand_up`), then diagnoses what it deployed and records the diagnosis (`diagnosis`).
    replace wipes the previous install first; a run that adds to the last install removes none of it."""

    def __init__(self, installer: Installer, toolsets: Iterable[ToolsetReference | AgentToolSet] | None, replace: bool) -> None:
        self._installer = installer
        self._toolsets = toolsets
        self._replace = replace
        self.channels = InstallChannels(installer, SERVER_CHANNELS.kinds)
        self.diagnosis: InstallDiagnosis | None = None

    def run(self) -> InstallChannels:
        """Install, holding the folder's lock, so a second install into the folder waits for it."""
        installer = self._installer
        with installer.lock.held():
            if self._replace:
                installer.clean()
            else:
                installer.last_install.hand_over_to(installer.record)
                installer.record.keep_existing()
            installer.toolsets.ensure_import_path()
            self.publish()
            self._save_installed_files()
            self.stand_up()
            self._diagnose()
        return self.channels

    def publish(self) -> None:
        """Write every channel's files for the run's toolsets, the Installer, and the toolsets the registered channels
        publish, then the language adapters, the agents, and the standing rules, and what a registered channel writes
        once every tool is recorded. A run of every toolset the repository defines, in place of the last install,
        leaves the adapters' folder holding nothing else."""
        installer = self._installer
        items = installer.repository_toolsets() if self._toolsets is None else list(self._toolsets)
        self._install_all(items)
        for toolset in (installer, *self.channels.toolsets):
            self._install_toolset(toolset)
        self.channels.language_adapters.write_all(whole=self._replace and self._toolsets is None)
        self._install_agents()
        self._install_standing_rules()
        for channel in self.channels.registered:
            channel.write_once_recorded()

    def stand_up(self) -> None:
        """Stand up each channel's server over what was installed, to check it loads, then start the servers. A run
        inside one of those servers, as an install through MCP runs inside the cdd server, starts none: they are already
        running, and starting them again would reload every toolset in the middle of a request."""
        for server in self.channels.servers:
            notice = server.stand_up().notice
            if notice:
                print(notice, file=sys.stderr)
        if not is_temporary(self._installer.path) and not any(server.runs_this_process for server in self.channels.servers):
            print(", ".join(self.ensure_running()), file=sys.stderr)

    def ensure_running(self) -> list[str]:
        """Start the server behind every channel the install wrote; one line for each thing started, saying how it runs."""
        return [line for server in self.channels.servers for line in server.ensure_running()]

    def _diagnose(self) -> None:
        """Diagnose what the run deployed against the last install, record it, and print a red report."""
        installer = self._installer
        self.diagnosis = installer.diagnosis_of(self.channels, self.channels.published)
        installer.diagnostics.record(self.diagnosis)
        if self.diagnosis.is_red:
            print(installer.red_report(self.diagnosis), file=sys.stderr)

    def _save_installed_files(self) -> None:
        """Tidy the folder this run wrote into and save its record."""
        installer = self._installer
        if self._replace:
            # Only after a full wipe and republish do the enrolled MCP names hold the whole catalog; a partial install
            # must not delete skills for toolsets not in this run.
            self._remove_skills_naming_missing_mcp()
        installer.record.prune_empty_skill_folders()
        installer.record.save()
        installer.last_install.remember(installer.target)

    def _install_all(self, toolsets: Iterable[ToolsetReference | AgentToolSet]) -> None:
        for item in toolsets:
            try:
                toolset = item.made()
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
        deployed = str(toolset.reference)
        if deployed not in channels.deployed:
            channels.deployed.append(deployed)
        for tool in toolset.tools.values():
            for installation in channels.for_tool(tool):
                installation.install(tool)
        channels.language_adapters.record(toolset)

    def _install_agents(self) -> None:
        """Copy cdd_guidance/agents into the IDE agents folder, each named as its front matter names it. The source
        stays on cdd_guidance. An agent kept in a folder of its own kind, such as exploratory-testing/tester.md, is
        installed flat under its front matter's name, since an IDE reads agents from one folder."""
        installer = self._installer
        source = installer.toolsets.agents_folder
        if not source.is_dir():
            return
        for path in sorted(source.rglob("*.md")):
            if ".context" in path.relative_to(source).parts:
                continue
            front_matter = FrontMatter.of_file(path)
            dest = installer.path / "agents" / f"{front_matter.fields.get('name') or path.stem}.md"
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(front_matter.text, encoding="utf-8")
            installer.record.track(dest)

    def _install_standing_rules(self) -> None:
        """Install cdd_guidance/rules as always-on rules in the IDE rules folder."""
        source = self._installer.toolsets.standing_rules_folder
        if not source.is_dir():
            return
        for path in sorted([*source.glob("*.md"), *source.glob("*.mdc")]):
            self.channels.rules.write_standing_rule(path)

    def _remove_skills_naming_missing_mcp(self) -> list[str]:
        """Drop skill files that name an MCP tool this install did not enroll.

        Orphan skills from a prior API (for example ``branch.create`` after the
        tool became ``repo.new_branch``) survive ``clean`` when they were never
        tracked. Agents then thrash searching for a tool that cannot exist.
        Skills without an MCP invoke line are left alone (hand-authored orphans).
        """
        skills = self._installer.path / "skills"
        answering = annotation_kinds.answering_calls
        if not skills.is_dir() or answering is None:
            return []
        enrolled = set(self.channels.published.get(answering.channel, []))
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
        installer.record.prune_empty_parents(skill)
        installer.record.forget(relative)
        return relative


@noCatalog
@agent_toolset
class Installer:
    """Publish every annotated member of the toolsets a repository defines into one IDE folder, through the installation
    of each channel its annotations name, then start the servers the installed files point at.

    Each install is one *InstallRun*, kept as ``last_run``. The MCP and hook channels are registered channels:
    harness/mcp and harness/hooks register their installation with ``SERVER_CHANNELS`` when they are imported, so this
    module never imports them."""

    def __init__(self, target: InstallTarget, toolsets: RepositoryToolsets, last_install: LastInstall) -> None:
        self.target = target
        """The IDE folder it installs into, with that IDE's layout."""
        self.record = InstallRecord(target)
        """The files the last install into that folder wrote, kept in the folder, read and written by the install and
        the clean."""
        self.last_install = last_install
        """The IDE and folder the checkout last installed into, where an install that names neither goes."""
        self.lock = InstallLock(target.path)
        """The folder's lock: one install or clean in it at a time."""
        self.toolsets = toolsets
        """The toolsets of the repository it installs."""
        self.diagnostics = target.diagnostics
        """The install's ``diagnostics.json``, kept in the folder it installs into."""
        self.last_run: InstallRun | None = None
        """The install this installer ran last; none before its first."""

    @classmethod
    def create(cls, ide: str | None = None, path: str | Path | None = None, *, repo: str | Path, dev_lane: bool = False) -> Installer:
        """The installer of repo into path for ide; with neither named, into the IDE folder it last installed into,
        else repo's own folder for the default IDE. An IDE name that is none CDD installs into is refused with
        *UnknownIde*, and a path that is empty, a file, or in a folder that does not exist with *NotAnInstallFolder*. dev_lane points the chats of a project other than repo at the dev lane's cdd
        server, which they otherwise reach on the stable lane."""
        root = Path(repo).resolve()
        last_install = LastInstall(_LAST_INSTALL)
        last_ide, last_folder = (last_install.ide, last_install.folder) if ide is None and path is None else (None, None)
        layout = IdeLayout(ide or last_ide or IdeLayout.DEFAULT_IDE)
        target = InstallTarget(layout, path, dev_lane) if path is not None else InstallTarget.from_last_install(layout, last_folder, root, dev_lane)
        return cls(target, RepositoryToolsets(root), last_install)

    @classmethod
    @tool_subject
    def load(cls, *, project: Path | str) -> Installer:
        """The installer of project, the folder the call names, into the IDE folder it last installed into."""
        return cls.create(repo=project)

    @property
    def repo(self) -> Path:
        """The repository it installs."""
        return self.toolsets.root

    @property
    def layout(self) -> IdeLayout:
        return self.target.layout

    @property
    def path(self) -> Path:
        """The IDE folder it installs into."""
        return self.target.path

    @property
    def ide(self) -> str:
        return self.target.layout.ide


    @command(name="clean")
    @agent_tool
    def clean(self) -> list[str]:
        """Remove files from the previous install on this IDE path."""
        if not self.path.is_dir():
            return []
        with self.lock.held():
            self.last_install.hand_over_to(self.record)
            removed = self.record.remove_installed()
            self.record.prune_empty_skill_folders()
        return removed

    @command(name="install")
    @agent_tool
    def install(
        self,
        toolsets: Iterable[ToolsetReference | AgentToolSet] | None = None,
        replace: bool = True,
    ) -> InstallChannels:
        """Install CDD into ``.cursor`` (or ``.claude`` with ``--ide Claude``) — skills, commands, rules, MCP, and hooks. ``replace`` wipes the previous install first.

        Installer-only refresh (``/install`` and ``/clean`` without walking the catalog): ``python scripts/install.py --self`` from this repo — not MCP.

        Before you run it, write these steps in the chat as a checklist. Then, as each one completes, write ``✓`` and the step in the chat with what the output said for it, so the person follows the install as it goes:

        1. Install every toolset: skills, commands, rules, MCP, and hooks (the line ``mcp: …, cdd plugin: …, board: …``).
        2. Check the cdd server runs, moved onto this commit when it ran an older one (``mcp: running (pid …)``, or ``cdd server: …``).
        3. Read ``diagnostics.json`` in the install folder (latest ``diagnose_install`` report) and paste the full summary: color, channel deltas, cdd server, hooks registered.

        When a step fails, write ``✗`` and the step with its error, stop, and follow "When install fails" in ``harness/installation/installer.md``."""
        self.last_run = InstallRun(self, toolsets, replace)
        return self.last_run.run()

    def install_self(self) -> InstallChannels:
        """Deploy only the Installer toolset — ``/install``, ``/clean`` — and the toolsets the registered channels publish
        into every install, such as the hooks that start the cdd server. It adds to the last install and removes none
        of it: a refresh of two commands must not take every skill and rule away."""
        return self.install([], replace=False)

    def write_language_adapters(self) -> list[Path]:
        """Write the TypeScript language adapters from the repository's toolsets as they are now, and nothing else. A
        page built against adapters an earlier install wrote reads the data the server sent then, so a field added since,
        such as a backlog item's children, is missing from it and the page fails; switching the server's code writes
        them first, then rebuilds its pages."""
        self.toolsets.ensure_import_path()
        adapters = LanguageAdapters(self.target, self.record, self.toolsets)
        channel_toolsets = [ToolsetReference.of(toolset) for channel in SERVER_CHANNELS.kinds for toolset in channel.toolsets]
        for item in [*self.repository_toolsets(), *channel_toolsets]:
            toolset = item.made()
            for each in (toolset, *toolset.child_toolsets()):
                adapters.record(each)
        return adapters.write_all(whole=True)

    def repository_toolsets(self) -> list[ToolsetReference]:
        """The reference to every toolset the repository defines, with the guidelines of the project it installs into
        chosen as that project's ``.context/config.json`` says: a pattern it disables is left out, and each pattern it
        keeps in its own guidelines folder is published as a shipped one is. One whose module cannot be imported stops
        the install, named after the toolset, with its cause."""
        classes = self.toolsets.classes()
        for unloadable in self.toolsets.unloadable:
            raise ToolsetInstallFailed(unloadable.reference, unloadable.cause) from unloadable.cause
        chosen = PROJECT_GUIDELINES.of(self.target.project).toolsets(classes)
        return [ToolsetReference.of(toolset_class) for toolset_class in chosen]

    def diagnosis_of(self, channels: InstallChannels, published: dict[str, list[str]]) -> InstallDiagnosis:
        """What channels deployed, with what each registered channel published, against the last install recorded, and
        the status each registered channel reports."""
        deployed = Deployed.of_folder(self.target, channels.deployed, published)
        status = [line for channel in channels.registered for line in channel.status()]
        return InstallDiagnosis(deployed, deployed.changes_since(self.diagnostics.last_deployed()), status)

    def red_report(self, diagnosis: InstallDiagnosis) -> str:
        """A red diagnosis's report, marked and followed by how to diagnose the install."""
        return f"!\n{diagnosis.report}\n{self.diagnose_instructions()}"

    @command(name="install-latest")
    @agent_tool
    def install_latest(self) -> int:
        """Merge the latest release (origin's newest v* tag, not the tip of main) and reinstall CDD on it, restarting every
        server, so this chat and the apps run the latest released code.

        Before you run it, put these seven steps in your task list (in Claude Code, the plan the app shows under your message) and write them in the chat as a checklist:

        1. Fetch origin's tags and merge the latest release into this checkout. A fetch or merge that fails or conflicts, or an origin with no release tag, stops here, before anything is stopped: tell the person and wait.
        2. Stop every app's server.
        3. Restart the cdd server on this checkout's commit: its lane (stable from main, dev from a ticket's worktree) serves the release just merged, and the chats point at that lane, so the chat bar's version shows it.
        4. Install every toolset: skills, commands, rules, MCP, and hooks. This is the long step, about a minute.
        5. Ping the cdd server.
        6. Reconnect this chat: when the cdd server reads failed, reconnect it, or ask the person to run ``/reload-plugins``.
        7. Read ``diagnostics.json`` in the install folder (latest ``diagnose_install`` report) and paste the summary: color, channel deltas, cdd server.

        Run the command in the background and watch its output as it runs, rather than waiting for it to end, so the person sees each step finish as it happens. The script writes ``▶ n/7 <step>`` as a step starts and ``✓ n/7 <step>: <result>`` as it is done. On each ``✓`` line, mark that step done in your task list and write the same line in the chat; on a ``✗ n/7`` line, write it, stop, and follow "When install fails" in ``harness/installation/installer.md``. Steps 6 and 7 are yours: mark and write each the same way once you have done it.

        Other chats share the cdd server, so message their sessions before you run it."""
        script = self.repo / "scripts" / "install-latest.py"
        return subprocess.run([sys.executable, str(script)], cwd=self.repo, check=False).returncode

    @agent_instructions
    def diagnose_install(self) -> str:
        """Compare this install with the last diagnostics.json entry and report counts, or what changed."""
        diagnosis = self._last_diagnosis()
        return self.red_report(diagnosis) if diagnosis.is_red else diagnosis.report

    def _last_diagnosis(self) -> InstallDiagnosis:
        """The diagnosis of the last run, or, before this installer ran one, of the folder an earlier install wrote: a
        channel whose names live outside the folder, such as MCP, names what the last install recorded."""
        if self.last_run is not None:
            return self.diagnosis_of(self.last_run.channels, self.last_run.channels.published)
        channels = InstallChannels(self, SERVER_CHANNELS.kinds)
        published = {name: names or self.diagnostics.installed_items(name) for name, names in channels.published.items()}
        return self.diagnosis_of(channels, published)

    @markdown("diagnose_install")
    def _diagnose_install_section(self) -> str:
        """The Diagnose Install section of installer.md."""

    @agent_instructions
    def diagnose_instructions(self) -> str:
        """How to diagnose an install whose deployed counts do not match."""
        return str(self._diagnose_install_section).strip()


__all__ = ["InstallChannels", "InstallRun", "Installer", "SERVER_CHANNELS", "ServersNotRegistered", "ToolsetInstallFailed"]
