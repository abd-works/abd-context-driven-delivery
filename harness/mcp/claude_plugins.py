"""ClaudePlugins - installs the cdd and cdd-board plugins into Claude Code through its own command line."""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from harness.installation.ide_layout import IdeLayout
from harness.installation.json_file import JsonFile, JsonFileUnreadable
from harness.mcp.cdd_home import BOARD_PLUGIN, CLAUDE_MARKETPLACE, CLAUDE_PLUGIN, CddHome

# Each claude plugin command clones or reads a marketplace; a slow disk or network can take this long.
_CLAUDE_COMMAND_TIMEOUT_SECONDS = 120


class ClaudePlugins:
    """The plugins ``~/.cdd/`` publishes for Claude Code, installed at user level with the ``claude`` command. The
    ``cdd`` plugin declares the cdd server for every chat; the ``cdd-board`` plugin is the session board. Each claude
    command takes seconds, so one runs only for what is missing, old, or installed from a checkout."""

    BOARD = f"{BOARD_PLUGIN}@{CLAUDE_MARKETPLACE}"
    CDD = f"{CLAUDE_PLUGIN}@{CLAUDE_MARKETPLACE}"
    # A board mod installed from a checkout's own marketplace runs that branch's code, not the server's.
    CHECKOUT_BOARD = f"{BOARD_PLUGIN}@abd-works"
    CHECKOUT_MARKETPLACE = "abd-works"

    def __init__(self, home: CddHome | None = None) -> None:
        self._home = home if home is not None else CddHome()
        self._claude = IdeLayout("Claude")

    def install_board(self) -> str:
        """Install the board mod from the code the server runs. The board is a convenience on top of the install, so a
        miss is printed, never raised."""
        installed = self.installed
        from_checkout = self.CHECKOUT_BOARD in installed
        if not from_checkout and installed.get(self.BOARD) == self.published_board_version:
            return "installed"
        claude = self.claude_cli
        if claude is None:
            print(f"{self.BOARD} not installed: no claude command found", file=sys.stderr)
            return "missing"
        if from_checkout:
            self.run(claude, "plugin", "uninstall", self.CHECKOUT_BOARD, "--scope", "user")
            self.run(claude, "plugin", "marketplace", "remove", self.CHECKOUT_MARKETPLACE)
        return self._install(claude, self.BOARD)

    def install_cdd(self) -> str:
        """Install the ``cdd`` plugin. Without it Claude Code has no cdd at all, so a miss is printed with the command
        to run by hand. Claude Code reads it from its folder, so one already installed needs no claude command."""
        if self.CDD in self.installed:
            return "installed"
        claude = self.claude_cli
        if claude is None:
            print(
                f"{self.CDD} not installed: no claude command found. Run: claude plugin marketplace add "
                f"{self._home.claude_plugins}",
                file=sys.stderr,
            )
            return "missing"
        return self._install(claude, self.CDD)

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

    @property
    def published_board_version(self) -> str:
        manifest = JsonFile(self._home.claude_plugins / BOARD_PLUGIN / ".claude-plugin" / "plugin.json")
        try:
            return str(manifest.read().get("version", ""))
        except JsonFileUnreadable:
            return ""

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

    def _install(self, claude: str, plugin: str) -> str:
        self.run(claude, "plugin", "marketplace", "add", str(self._home.claude_plugins))
        self.run(claude, "plugin", "install", plugin, "--scope", "user")
        self.run(claude, "plugin", "update", plugin, "--scope", "user")
        if plugin in self.run(claude, "plugin", "list"):
            return "installed"
        print(f"{plugin} not installed: claude plugin install did not take", file=sys.stderr)
        return "missing"

    def _desktop_claude_code_folders(self) -> list[Path]:
        """Where the desktop app keeps its Claude Code: under `%APPDATA%\\Claude`, or under each profile in
        `%LOCALAPPDATA%\\Claude-Data`. Neither is on PATH, so without these the plugin never installs."""
        roaming = Path(os.environ.get("APPDATA") or Path.home()) / "Claude" / "claude-code"
        local = Path(os.environ.get("LOCALAPPDATA") or Path.home())
        return [roaming, *local.glob("Claude-Data/*/claude-code")]
