"""Installer: install every toolset a repository defines into one IDE folder, through every destination."""
from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Any, Iterable

from harness.agent_tools.agent_tools import AgentTool, InstallDestination, agent_instructions, agent_tool, agent_toolset, tool_subject
from harness.hooks.hooks import HookInstallation, hook
from harness.installation.destination import Installation, noCatalog
from harness.installation.files import FileInstallation, command
from harness.installation.ide_layout import IdeLayout
from harness.installation.language_adapter import LanguageAdapterInstallation
from harness.installation.repository_toolsets import RepositoryToolsets
from harness.installer.claude_plugins import ClaudePlugins
from harness.installer.install_diagnostics import InstallDiagnostics
from harness.installer.install_record import InstallRecord
from harness.markdown import markdown

if TYPE_CHECKING:
    from harness.hooks.hook_server import HookPayload
    from harness.mcp.mcp_server import McpInstallation

# The checkout this installer's code runs from. The cdd server is installed into ``~/.cdd`` from it, whichever
# project's hook asks for the server.
_CDD_CHECKOUT = Path(__file__).resolve().parents[2]
# The record of the last install into a project's own IDE folder; an install into a temporary folder keeps its record
# in that folder, so a spec's install never replaces the person's.
_SHARED_RECORD = Path(__file__).resolve().parent / InstallRecord.NAME


class ToolsetInstallFailed(Exception):
    """Publishing one toolset failed; the install stops so no IDE folder is left with part of a toolset."""

    def __init__(self, toolset: Any, cause: Exception) -> None:
        super().__init__(f"install failed for {toolset}: {type(cause).__name__}: {cause}")
        self.toolset = toolset
        self.cause = cause


class HookServerNotRunning(Exception):
    """The install finished but the checkout's hook daemon does not answer, so hooks would not run."""

    def __init__(self, repo: Path) -> None:
        super().__init__(f"install failed: the hook server of {repo} is not running")
        self.repo = repo


class _InstallChannels:
    """The MCP, hook, and language adapter installations of one install run, each tracking the files it writes in
    the install record."""

    def __init__(self, installer: Installer) -> None:
        from harness.mcp.mcp_server import McpInstallation

        self.mcp: McpInstallation = McpInstallation(installer.ide, installer.path, repo=installer.repo)
        self.hook = HookInstallation(installer.ide, installer.path, repo=installer.repo)
        self.language_adapters = LanguageAdapterInstallation(installer.ide, installer.path, repo=installer.repo)
        for installation in (self.mcp, self.hook, self.language_adapters):
            installer.track(installation)


@noCatalog
@agent_toolset
class Installer:
    """Publish every annotated member of the toolsets a repository defines into one IDE folder, through the installation
    of each channel its annotations name, then start the hook server and the cdd server the install points at."""

    TOOLSET_REF = "harness.installer.installer:Installer"
    _SKILL_MCP_NAME = re.compile(r"Use MCP tool:\s*`([A-Za-z0-9_.-]+)")

    def __init__(self, ide: str | None = None, path: str | Path | None = None, *, repo: str | Path) -> None:
        self.repo = Path(repo).resolve()
        last = InstallRecord(_SHARED_RECORD).saved if ide is None and path is None else {}
        self.ide = ide or last.get("ide") or IdeLayout.DEFAULT_IDE
        self.layout = IdeLayout(self.ide)
        self.path = Path(path) if path is not None else self._last_or_default_folder(last.get("path"))
        self.record = InstallRecord(self.path / InstallRecord.NAME if self._is_temporary(self.path) else _SHARED_RECORD)
        self.diagnostics = InstallDiagnostics(self.path, self.layout)
        self.claude_plugins = ClaudePlugins()
        self.toolsets = RepositoryToolsets(self.repo)
        self._channels: _InstallChannels | None = None
        self._deployed_toolsets: list[str] = []
        self.diagnosis: list[str] = []

    @classmethod
    @tool_subject
    def load(cls, *, project: Path | str) -> Installer:
        """The installer of project, the folder the call names, into the IDE folder it last installed into."""
        return cls(repo=project)

    def track(self, installation: Installation) -> None:
        """Have installation add each file it writes to the install record."""
        installation.track_writes_with(lambda written: self.record.track(written, self.path))

    def installations_for(self, tool: AgentTool) -> list[Installation]:
        channels = self._channels_of_run()
        destinations = tool.destinations
        mcp_mode = InstallDestination.MCP in destinations
        installations: list[Installation] = [channels.mcp] if mcp_mode else []
        for destination in (InstallDestination.SKILL, InstallDestination.COMMAND, InstallDestination.RULE):
            if destination in destinations:
                files = FileInstallation(self.ide, self.path, destination, mcp_mode=mcp_mode, repo=self.repo)
                self.track(files)
                installations.append(files)
        if InstallDestination.HOOK in destinations and self.layout.runs_hooks:
            installations.append(channels.hook)
        return installations

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

        When install finishes, read ``.cursor/diagnostics.json`` (latest ``diagnose_install`` report) and paste the full summary: color, channel deltas, cdd server, hook server, hooks registered."""
        return self._install_run(toolsets, replace)

    def install_self(self, *, replace: bool = False) -> Any:
        """Deploy only this Installer toolset — ``/install``, ``/clean``, and MCP-host hooks."""
        return self._install_run([], replace=replace)

    def _install_run(self, toolsets: Iterable[Any] | None, replace: bool) -> McpInstallation:
        if replace:
            self.clean()
        else:
            self.record.keep_existing(self.path)
        self.toolsets.ensure_import_path()
        self._channels = _InstallChannels(self)
        self._install_all(self.toolsets.collect() if toolsets is None else toolsets)
        self._install_toolset(self.TOOLSET_REF, self)
        self._channels.language_adapters.write_all()
        self._install_agents()
        self._install_standing_rules()
        if replace:
            # Only after a full wipe and republish do the enrolled MCP names hold the whole catalog; a partial install
            # must not delete skills for toolsets not in this run.
            self._remove_skills_naming_missing_mcp()
        self.record.prune_empty_skill_folders(self.path)
        self.record.save(self.ide, self.path)
        self._standup_channels()
        self.diagnosis = self.diagnose_after_install()
        for report in self.diagnosis:
            if report.startswith("!"):
                print(report, file=sys.stderr)
        return self._channels.mcp

    def _install_all(self, toolsets: Iterable[Any]) -> None:
        from harness.agent_tools.agent_tools import AgentToolSet

        for item in toolsets:
            try:
                toolset = AgentToolSet.instantiate(item)
                self._install_toolset(item, toolset)
                for child in toolset.child_toolsets():
                    self._install_toolset(item, child)
            except ToolsetInstallFailed:
                raise
            # Any failure while publishing a toolset stops the install, named after the toolset, with its cause.
            except Exception as error:  # noqa: BLE001
                raise ToolsetInstallFailed(item, error) from error

    def _install_toolset(self, item: Any, toolset: Any) -> None:
        self._remember_toolset(item, toolset)
        for tool in toolset.tools.values():
            for installation in self.installations_for(tool):
                installation.install(tool)
        self._channels_of_run().language_adapters.record(toolset)

    def _remember_toolset(self, item: Any, toolset: Any) -> None:
        ref = item if isinstance(item, str) else f"{type(toolset).__module__}:{type(toolset).__name__}"
        if ref not in self._deployed_toolsets:
            self._deployed_toolsets.append(ref)

    def _channels_of_run(self) -> _InstallChannels:
        if self._channels is None:
            self._channels = _InstallChannels(self)
        return self._channels

    def _install_agents(self) -> None:
        """Copy cdd_guidance/agents into the IDE agents folder. The source stays on cdd_guidance."""
        source = self.repo / "cdd_guidance" / "agents"
        if not source.is_dir():
            return
        for path in sorted(source.glob("*.md")):
            dest = self.path / "agents" / f"{self._agent_name(path)}.md"
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
            self.record.track(dest, self.path)

    def _agent_name(self, path: Path) -> str:
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---"):
            return path.stem
        for line in text.splitlines()[1:]:
            if line.strip() == "---":
                break
            if line.startswith("name:") and line.split(":", 1)[1].strip():
                return line.split(":", 1)[1].strip()
        return path.stem

    def _install_standing_rules(self) -> None:
        """Install cdd_guidance/rules as always-on rules in the IDE rules folder."""
        source = self.repo / "cdd_guidance" / "rules"
        if not source.is_dir():
            return
        rules = FileInstallation(self.ide, self.path, "rules", repo=self.repo)
        self.track(rules)
        for path in sorted([*source.glob("*.md"), *source.glob("*.mdc")]):
            rules.write_standing_rule(path)

    def _remove_skills_naming_missing_mcp(self) -> list[str]:
        """Drop skill files that name an MCP tool this install did not enroll.

        Orphan skills from a prior API (for example ``branch.create`` after the
        tool became ``repo.new_branch``) survive ``clean`` when they were never
        tracked. Agents then thrash searching for a tool that cannot exist.
        Skills without an MCP invoke line are left alone (hand-authored orphans).
        """
        skills = self.path / "skills"
        if not skills.is_dir():
            return []
        enrolled = set(self._mcp_names())
        removed: list[str] = []
        for path in skills.rglob("SKILL.md"):
            names = self._SKILL_MCP_NAME.findall(path.read_text(encoding="utf-8"))
            if not names or all(name in enrolled for name in names):
                continue
            relative = path.resolve().relative_to(self.path.resolve()).as_posix()
            path.unlink()
            removed.append(relative)
            self.record.prune_empty_parents(path, self.path)
            self.record.forget(relative)
        return removed

    def _standup_channels(self) -> None:
        # Installing via MCP runs inside the cdd server itself. A second McpHost.from_repo() reloads every toolset
        # mid-request, and the server is already running, so neither runs then.
        channels = self._channels_of_run()
        in_mcp_host = self._mcp_host_is_this_process()
        if not in_mcp_host:
            channels.mcp.standup()
            self._print_channel_notice(channels.mcp.diagnose())
        channels.hook.standup()
        self._print_channel_notice(channels.hook.diagnose())
        if not self._is_temporary(self.path) and not in_mcp_host:
            self.ensure_runtimes()

    def ensure_runtimes(self) -> dict[str, Any]:
        """Start the hook daemon and the cdd server; fail if either stays down."""
        if not self.layout.runs_hooks:
            return {
                "hook": "not installed",
                "mcp": self.ensure_mcp_server(),
                "cdd plugin": self.claude_plugins.install_cdd(),
                "board": self.claude_plugins.install_board(),
            }
        hook_pid = self._ensure_hook_server()
        mcp = self.ensure_mcp_server()
        print(f"hook server pid={hook_pid} cdd server={mcp}", file=sys.stderr)
        return {"hook": "running", "mcp": mcp}

    def ensure_mcp_server(self) -> str:
        """Start the one cdd server when none answers. Cursor and VS Code connect to its URL and cannot start it."""
        return self._channels_of_run().mcp.ensure_server()

    def _ensure_hook_server(self) -> int | None:
        from harness.hooks.hook_daemon import HookDaemon

        daemon = HookDaemon(self.repo)
        daemon.ensure()
        address = daemon.live_address()
        if address is None:
            raise HookServerNotRunning(self.repo)
        return address.pid

    def _print_channel_notice(self, diagnosis: dict[str, Any]) -> None:
        notice = diagnosis.get("notice") or ""
        if notice:
            print(notice, file=sys.stderr)

    def diagnose_after_install(self) -> list[str]:
        """Record install-channel diagnostics only; guidance probes use ``/guidance-diagnostics``."""
        report = self.diagnose_install()
        color = next((line for line in report.splitlines() if line in {"green", "yellow", "red"}), "green")
        self.diagnostics.record_install(self._deployed_channels(), report, color)
        return [report]

    @agent_instructions
    def diagnose_install(self) -> str:
        """Compare this install with the last diagnostics.json entry and report counts, or what changed."""
        color, compared = self.diagnostics.compared(self._deployed_channels())
        body = f"{compared}\n{self._runtime_status_report()}"
        if color != "red":
            return f"{color}\n{body}"
        return f"!\n{color}\n{body}\n{self.diagnose_instructions()}"

    def _deployed_channels(self) -> dict[str, list[str]]:
        return self.diagnostics.channels_in_folder(self._deployed_toolsets, self._mcp_names())

    def _mcp_names(self) -> list[str]:
        """The MCP operations this run enrolled; outside a run, the ones the last install recorded."""
        if self._channels is None:
            return self.diagnostics.installed_items("mcp")
        return sorted(str(tool.mcp_name) for tool in self._channels.mcp.mcp_operations)

    def _mcp_host_is_this_process(self) -> bool:
        return self._channels_of_run().mcp.server_runs_this_process()

    def _runtime_status_report(self) -> str:
        from harness.hooks.hook_daemon import HookDaemon

        mcp = "running" if self._channels_of_run().mcp.server_is_running() else "not running"
        address = HookDaemon(self.repo).live_address()
        hook = f"running (pid {address.pid})" if address is not None else "not running"
        hooks = HookInstallation(self.ide, self.path)
        events, operations = hooks.registered_events, hooks.registered_operations
        return "\n".join(
            [
                f"cdd server: {mcp}",
                f"hook server: {hook}",
                f"hooks registered (events): {', '.join(events) or 'none'}",
                f"hook handlers (operations): {', '.join(operations) or 'none'}",
            ]
        )

    def _last_or_default_folder(self, last: str | None) -> Path:
        if last and Path(last).exists() and not self._is_temporary(Path(last)):
            return Path(last)
        return self.repo / self.layout.folder_name

    def _is_temporary(self, folder: Path) -> bool:
        temp = Path(tempfile.gettempdir()).resolve()
        resolved = folder.resolve()
        return resolved == temp or temp in resolved.parents

    @markdown("install")
    def install_instructions(self) -> str:
        """Install instructions."""

    @markdown("clean")
    def clean_instructions(self) -> str:
        """Clean instructions."""

    @markdown("diagnose_install")
    def diagnose_install_instructions(self) -> str:
        """Diagnose-install instructions."""

    @markdown("ensure_runtimes")
    def runtime_instructions(self) -> str:
        """Runtime instructions."""

    @agent_instructions
    def diagnose_instructions(self) -> str:
        """How to diagnose an install whose deployed counts do not match."""
        return str(self.diagnose_install_instructions).strip()

    @hook("sessionStart")
    def ensure_mcp_server_on_session_start(self, payload: HookPayload) -> str:
        """Start the cdd server when a chat starts; the hook server's toolset holds no project, so this builds the
        installer of the checkout the server is installed from."""
        return Installer(repo=_CDD_CHECKOUT).ensure_mcp_server()

    @hook("afterAgentResponse")
    def ensure_mcp_server_after_agent_response(self, payload: HookPayload) -> str:
        return Installer(repo=_CDD_CHECKOUT).ensure_mcp_server()


__all__ = ["Installer"]
