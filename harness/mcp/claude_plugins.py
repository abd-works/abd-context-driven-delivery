"""ClaudePlugins - installs the plugins a cdd home's marketplace publishes into Claude Code through its own command line."""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from harness.installation.ide_layout import IdeLayout
from harness.installation.json_file import JsonFile, JsonFileUnreadable
from harness.mcp.cdd_home import CddHome
from harness.mcp.claude_marketplace import CLAUDE_MARKETPLACE, PublishedPlugin

# Each claude plugin command clones or reads a marketplace; a slow disk or network can take this long.
_CLAUDE_COMMAND_TIMEOUT_SECONDS = 120


class PluginInstall:
    """What installing one plugin came to: ``installed`` (it is at the published version, or installing put it there),
    ``watched`` (Claude Code loads its folder and reloads it as it changes, so it needs no install), or ``missing``
    (no claude command, or the install did not take)."""

    INSTALLED = "installed"
    WATCHED = "watched"
    MISSING = "missing"

    def __init__(self, state: str) -> None:
        self.state = state

    def __str__(self) -> str:
        return self.state

    def __eq__(self, other: object) -> bool:
        return isinstance(other, PluginInstall) and other.state == self.state

    def __hash__(self) -> int:
        return hash(self.state)


class ClaudePlugins:
    """The plugins ``~/.cdd/`` publishes for Claude Code, installed at user level with the ``claude`` command: the
    ``cdd`` plugin, which declares the cdd server for every chat, and the mods of the code the server runs. Each claude
    command takes seconds, so one runs only for what is missing, old, or installed from a checkout. A plugin is a
    convenience on top of the install, so a miss is printed, never raised."""

    # A plugin installed from a checkout's own marketplace runs that branch's code, not the server's.
    CHECKOUT_MARKETPLACE = "abd-works"

    def __init__(self, home: CddHome | None = None) -> None:
        self._home = home if home is not None else CddHome()
        self._claude = IdeLayout("Claude")

    def install(self, plugin: PublishedPlugin) -> PluginInstall:
        """Install plugin from the cdd home's marketplace, or update it when what it publishes changed. A plugin whose
        folder Claude Code watches, named in ``CLAUDE_CODE_PLUGIN_DIRS``, needs no install: every chat reloads it as
        the folder is written, and installing it too would load it twice. A copy installed from a checkout's own
        marketplace is replaced."""
        if self.is_watched(plugin):
            return PluginInstall(PluginInstall.WATCHED)
        installed = self.installed
        from_checkout = f"{plugin.name}@{self.CHECKOUT_MARKETPLACE}"
        if from_checkout not in installed and installed.get(plugin.installed_name) == plugin.version:
            return PluginInstall(PluginInstall.INSTALLED)
        claude = self.claude_cli
        if claude is None:
            print(
                f"{plugin.installed_name} not installed: no claude command found. Run: claude plugin marketplace add "
                f"{plugin.marketplace.folder}",
                file=sys.stderr,
            )
            return PluginInstall(PluginInstall.MISSING)
        if from_checkout in installed:
            self.run(claude, "plugin", "uninstall", from_checkout, "--scope", "user")
            self.run(claude, "plugin", "marketplace", "remove", self.CHECKOUT_MARKETPLACE)
        return self._install(claude, plugin)

    @property
    def installed(self) -> dict[str, str]:
        """Each plugin Claude Code has installed, with its version, from its own record of them."""
        record = JsonFile(self._claude.user_settings_folder / "plugins" / "installed_plugins.json")
        try:
            plugins = record.read().get("plugins", {})
        except JsonFileUnreadable:
            # A record Claude Code is writing: nothing reads as installed, and the install runs again.
            return {}
        return {name: str((entries or [{}])[0].get("version", "")) for name, entries in plugins.items()}

    def is_watched(self, plugin: PublishedPlugin) -> bool:
        """Whether the user's Claude Code settings name plugin's folder in ``CLAUDE_CODE_PLUGIN_DIRS``, which every chat
        loads it from and reloads it from when the folder changes: a served checkout's mod folder, else the copy."""
        try:
            env = JsonFile(self._claude.user_settings_folder / "settings.json").read().get("env", {})
        except JsonFileUnreadable:
            return False
        watched = plugin.marketplace.mod_folder(plugin).resolve()
        folders = str(env.get("CLAUDE_CODE_PLUGIN_DIRS", "")).split(os.pathsep)
        return any(folder.strip() and Path(folder.strip()).expanduser().resolve() == watched for folder in folders)

    @property
    def claude_cli(self) -> str | None:
        """The desktop app's newest Claude Code, else the one on PATH, which can be too old for the plugin."""
        found = [path for folder in self._desktop_claude_code_folders() for path in folder.glob("*/*/claude.exe")]
        versions = [path for path in found if re.fullmatch(r"[\d.]+", path.parent.parent.name)]
        if versions:
            return str(max(versions, key=lambda path: [int(part) for part in path.parent.parent.name.split(".")]))
        return shutil.which("claude")

    def run(self, claude: str, *args: str) -> str:
        """What one claude command prints; the failure's text when it cannot run."""
        try:
            run = subprocess.run(
                [claude, *args], capture_output=True, text=True, encoding="utf-8", timeout=_CLAUDE_COMMAND_TIMEOUT_SECONDS
            )
        except (OSError, subprocess.SubprocessError) as error:
            return str(error)
        return run.stdout + run.stderr

    # Adding a marketplace Claude Code already has reads nothing new, and an update compares against the listing it last
    # read, so the marketplace is read again before the update, or a newly published board stays uninstalled.
    def _install(self, claude: str, plugin: PublishedPlugin) -> PluginInstall:
        named = plugin.installed_name
        self.run(claude, "plugin", "marketplace", "add", str(plugin.marketplace.folder))
        self.run(claude, "plugin", "marketplace", "update", CLAUDE_MARKETPLACE)
        self.run(claude, "plugin", "install", named, "--scope", "user")
        self.run(claude, "plugin", "update", named, "--scope", "user")
        if named in self.run(claude, "plugin", "list"):
            return PluginInstall(PluginInstall.INSTALLED)
        print(f"{named} not installed: claude plugin install did not take", file=sys.stderr)
        return PluginInstall(PluginInstall.MISSING)

    def _desktop_claude_code_folders(self) -> list[Path]:
        """Where the desktop app keeps its Claude Code: under `%APPDATA%\\Claude`, or under each profile in
        `%LOCALAPPDATA%\\Claude-Data`. Neither is on PATH, so without these the plugin never installs."""
        roaming = Path(os.environ.get("APPDATA") or Path.home()) / "Claude" / "claude-code"
        local = Path(os.environ.get("LOCALAPPDATA") or Path.home())
        return [roaming, *local.glob("Claude-Data/*/claude-code")]
