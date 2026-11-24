"""ClaudePlugins - has Claude Code load the plugins a cdd home's marketplace publishes from their folders, never its cache."""
from __future__ import annotations

import json
import os
if os.name == "nt":
    import _winapi
import re
import shutil
import subprocess
import sys
from pathlib import Path

from harness.installation.ide_layout import IdeLayout
from harness.installation.json_file import JsonFile, JsonFileUnreadable
from harness.mcp.cdd_home import CddHome
from harness.mcp.claude_marketplace import PublishedPlugin

# The cdd home's folder of fixed folders Claude Code loads the plugins from, each leading to the approved lane's copy.
CHAT_PLUGINS = "chat-plugins"
# Each claude plugin command clones or reads a marketplace; a slow disk or network can take this long.
_CLAUDE_COMMAND_TIMEOUT_SECONDS = 120


class PluginInstall:
    """What installing one plugin came to: ``watched`` (Claude Code loads it from its published folder already),
    ``watched from now on: restart the Claude app to load it`` (the install named its folder just now, which Claude Code
    reads when it starts), or ``cached copy still loaded: no claude command to uninstall it`` (a copy in Claude Code's
    cache that the install could not remove)."""

    WATCHED = "watched"
    NEWLY_WATCHED = "watched from now on: restart the Claude app to load it"
    CACHED = "cached copy still loaded: no claude command to uninstall it"

    def __init__(self, state: str) -> None:
        self.state = state

    def __str__(self) -> str:
        return self.state

    def __eq__(self, other: object) -> bool:
        return isinstance(other, PluginInstall) and other.state == self.state

    def __hash__(self) -> int:
        return hash(self.state)


class ClaudePlugins:
    """The plugins ``~/.cdd/`` publishes for Claude Code: the ``cdd`` plugin, which declares the cdd server for every
    chat, and the mods of the code the server runs. Claude Code loads each from its published folder, named in
    ``CLAUDE_CODE_PLUGIN_DIRS`` in its user settings, never from a copy in its own plugin cache: a cached copy keeps the
    version it was installed at, so a mod published afterwards, such as the queue bar gaining Flush, never reaches the
    chats. A cached copy the install finds is uninstalled with the ``claude`` command. A plugin is a convenience on top
    of the install, so a miss is printed, never raised."""

    # A plugin installed from a checkout's own marketplace, whose listing goes when its plugin does.
    CHECKOUT_MARKETPLACE = "abd-works"
    WATCHED_FOLDERS = "CLAUDE_CODE_PLUGIN_DIRS"

    def __init__(self, home: CddHome | None = None, claude_folder: Path | None = None) -> None:
        self._home = home if home is not None else CddHome()
        self._claude_folder = claude_folder if claude_folder is not None else IdeLayout("Claude").user_settings_folder

    def install(self, plugin: PublishedPlugin) -> PluginInstall:
        """Have Claude Code load plugin from the lane the person approved, never a cached copy: the cdd home's fixed
        folder for the plugin (``chat-plugins/{name}``) leads to the folder the plugin is published from, the settings
        name that fixed folder in place of any other folder of the same plugin, and every cached copy is uninstalled.
        The fixed folder never moves, so a repin onto another lane and a reload of the plugins reach every chat; only
        the first time the settings name it does Claude Code need restarting, since it reads them when it starts."""
        chat_folder = self._lead_to(plugin.marketplace.mod_folder(plugin), plugin.name)
        newly_watched = self._watch(chat_folder, plugin.name)
        cached = [name for name in self.installed if name.split("@")[0] == plugin.name]
        if cached and not self._uninstall(cached):
            print(f"{plugin.name}: a cached copy is still installed and no claude command was found to uninstall it", file=sys.stderr)
            return PluginInstall(PluginInstall.CACHED)
        return PluginInstall(PluginInstall.NEWLY_WATCHED if newly_watched else PluginInstall.WATCHED)

    @property
    def installed(self) -> dict[str, str]:
        """Each plugin Claude Code has a copy of in its cache, with its version, from its own record of them."""
        record = JsonFile(self._claude_folder / "plugins" / "installed_plugins.json")
        try:
            plugins = record.read().get("plugins", {})
        except JsonFileUnreadable:
            # A record Claude Code is writing reads as empty; the next install looks again.
            return {}
        return {name: str((entries or [{}])[0].get("version", "")) for name, entries in plugins.items()}

    def _watch(self, folder: Path, name: str) -> bool:
        """Name folder in ``CLAUDE_CODE_PLUGIN_DIRS``, dropping any other published folder of the plugin called name,
        which would load it twice; answer whether the settings changed."""
        settings = JsonFile(self._claude_folder / "settings.json")
        try:
            named = settings.read()
        except JsonFileUnreadable:
            named = {}
        env = named.setdefault("env", {})
        current = [entry.strip() for entry in str(env.get(self.WATCHED_FOLDERS, "")).split(os.pathsep) if entry.strip()]
        wanted = str(Path(folder))
        kept = [entry for entry in current if not self._another_copy(Path(entry), name, wanted)]
        if wanted not in kept:
            kept.append(wanted)
        if kept == current:
            return False
        env[self.WATCHED_FOLDERS] = os.pathsep.join(kept)
        self._claude_folder.mkdir(parents=True, exist_ok=True)
        (self._claude_folder / "settings.json").write_text(json.dumps(named, indent=2), encoding="utf-8")
        return True

    def _lead_to(self, published: Path, name: str) -> Path:
        """The cdd home's fixed folder for the plugin called name, made to lead to published: a directory junction on
        Windows, which needs no special rights, else a symbolic link. A link leading elsewhere is replaced."""
        link = self._home.folder / CHAT_PLUGINS / name
        target = Path(published).resolve()
        if link.is_symlink() or link.is_junction():
            if link.resolve() == target:
                return link
            os.unlink(link) if link.is_symlink() else os.rmdir(link)
        link.parent.mkdir(parents=True, exist_ok=True)
        if os.name == "nt":
            _winapi.CreateJunction(str(target), str(link))
        else:
            link.symlink_to(target, target_is_directory=True)
        return link

    def _another_copy(self, entry: Path, name: str, wanted: str) -> bool:
        """Whether entry is another folder of the plugin called name, which would load it twice: a published one, in a
        ``claude-plugins`` folder, another home's fixed one, in a ``chat-plugins`` folder, or any folder whose manifest
        names the plugin, such as a served checkout's own mod folder an older install named."""
        if str(entry) == wanted:
            return False
        return (entry.name == name and entry.parent.name in ("claude-plugins", CHAT_PLUGINS)) or self._plugin_named(entry) == name

    def _plugin_named(self, folder: Path) -> str:
        """The name the plugin in folder gives itself in its manifest; empty when folder holds no plugin it can read."""
        try:
            return str(JsonFile(folder / ".claude-plugin" / "plugin.json").read().get("name", ""))
        except JsonFileUnreadable:
            return ""

    def _uninstall(self, cached: list[str]) -> bool:
        """Uninstall each cached copy, and the listing of a checkout's own marketplace with its copy; answer whether a
        claude command ran them."""
        claude = self.claude_cli
        if claude is None:
            return False
        for name in cached:
            self.run(claude, "plugin", "uninstall", name, "--scope", "user")
            if name.endswith(f"@{self.CHECKOUT_MARKETPLACE}"):
                self.run(claude, "plugin", "marketplace", "remove", self.CHECKOUT_MARKETPLACE)
        return True

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

    def _desktop_claude_code_folders(self) -> list[Path]:
        """Where the desktop app keeps its Claude Code: under `%APPDATA%\\Claude`, or under each profile in
        `%LOCALAPPDATA%\\Claude-Data`. Neither is on PATH, so without these the plugin never installs."""
        roaming = Path(os.environ.get("APPDATA") or Path.home()) / "Claude" / "claude-code"
        local = Path(os.environ.get("LOCALAPPDATA") or Path.home())
        return [roaming, *local.glob("Claude-Data/*/claude-code")]
