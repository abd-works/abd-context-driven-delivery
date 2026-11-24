"""ClaudeMarketplace - the Claude Code plugin marketplace a cdd home publishes: the ``cdd`` plugin, which declares the cdd
server for every chat, and the mods of the code the server runs, each a *PublishedPlugin*."""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import TYPE_CHECKING, Any

from harness.installation.ide_layout import IdeLayout
from harness.installation.install_lock import InstallLock
from harness.installation.json_file import JsonFile, JsonFileUnreadable

if TYPE_CHECKING:
    from harness.mcp.cdd_home import CddHome

CLAUDE_MARKETPLACE = "cdd-home"
CLAUDE_PLUGIN = "cdd"
CLAUDE_PLUGIN_DESCRIPTION = "Connects every Claude Code chat to the one cdd server, starting it when a chat starts"
# How long the chat-start hook may take to start a server that was not running: a cold start imports every toolset.
SERVER_START_SECONDS = 90
# How much of a content hash a plugin version carries: enough that two different contents never share a version.
VERSION_HASH_CHARS = 12
# The parts of a mod Claude Code loads; its tests and the rest of its folder stay in the checkout.
MOD_PARTS = (".claude-plugin", "hooks", "types")
# The file a mod keeps beside its ``.claude-plugin`` folder to be published from the code the server runs.
MOD_DECLARATION = "cdd-mod.json"
# How deep under a checkout a mod's folder sits, such as ``tools/prompt_queue`` or ``harness/chat-ui/pane``.
_MOD_DEPTHS = ("*/*", "*/*/*")
# Claude Code, the IDE whose plugins the marketplace publishes.
_CLAUDE_CODE = IdeLayout("Claude")


class PublishedMod:
    """A mod a checkout's code declares for the cdd home to publish: a folder holding ``.claude-plugin/plugin.json``
    and ``cdd-mod.json`` beside it, which names the plugin, the files of the checkout it carries besides its own
    (``extras``: where each goes in the plugin, and the file in the checkout it is copied from), and the file the
    install command its Run install runs is written to, for a mod that runs one. The mod declares itself in the code, so
    the framework names no folder of a module built on it, and a pinned server publishes the mods its own code
    declares."""

    def __init__(self, declaration: Path, code: Path) -> None:
        self.folder = declaration.parent
        self._code = code
        self._declared = JsonFile(declaration).read()

    @property
    def name(self) -> str:
        return str(self._declared.get("plugin") or self.folder.name)

    @property
    def extras(self) -> dict[Path, Path]:
        """Each file the mod carries besides its own: where it goes in the plugin, and the checkout file it comes from."""
        return {Path(target): self._code / source for target, source in dict(self._declared.get("extras") or {}).items()}

    @property
    def install_command_file(self) -> str:
        """The file in the mod its Run install reads the install command from; empty for a mod that runs no install."""
        return str(self._declared.get("install_command") or "")


class PublishedMods:
    """The mods the code at code declares, each a *PublishedMod*, found by their ``cdd-mod.json``."""

    def __init__(self, code: Path) -> None:
        self.code = Path(code)

    @property
    def every(self) -> list[PublishedMod]:
        found = [declaration for depth in _MOD_DEPTHS for declaration in self.code.glob(f"{depth}/{MOD_DECLARATION}")]
        mods = [PublishedMod(declaration, self.code) for declaration in sorted(found)]
        return [mod for mod in mods if (mod.folder / ".claude-plugin" / "plugin.json").is_file()]


class PublishedPlugin:
    """One plugin of the marketplace, by its name: the one owner of ``{name}/.claude-plugin/plugin.json``, its manifest,
    which says its version and description. A mod is published from its folder in the code the server runs
    (`publish_from`): its parts, without their tests, and the files it carries besides; its version gains a hash of the
    mod's files, because Claude Code keeps a plugin it has already seen at the same version, so a changed mod needs a
    new one."""

    def __init__(self, marketplace: ClaudeMarketplace, name: str) -> None:
        self.marketplace = marketplace
        self.name = name
        self.folder = marketplace.folder / name
        self._manifest = JsonFile(self.folder / ".claude-plugin" / "plugin.json")

    @property
    def is_published(self) -> bool:
        return self._manifest.exists()

    @property
    def manifest(self) -> dict[str, Any]:
        """The plugin's manifest; empty when it is not published, or is being written."""
        try:
            return self._manifest.read()
        except JsonFileUnreadable:
            return {}

    @property
    def version(self) -> str:
        """The version the marketplace publishes the plugin at; empty when it publishes none."""
        return str(self.manifest.get("version", ""))

    @property
    def description(self) -> str:
        return str(self.manifest.get("description", ""))

    @property
    def installed_name(self) -> str:
        """The plugin as Claude Code names it once installed: ``{name}@cdd-home``."""
        return f"{self.name}@{CLAUDE_MARKETPLACE}"

    def write_manifest(self, manifest: dict[str, Any]) -> Path:
        return self._manifest.write(manifest)

    def publish_from(self, mod: PublishedMod) -> None:
        """Copy mod's parts and the files it carries besides into this plugin, then version it from the mod's files."""
        # A file the running app holds open can survive the delete on Windows, so the copy writes over what is left.
        shutil.rmtree(self.folder, ignore_errors=True)
        for part in MOD_PARTS:
            if (mod.folder / part).is_dir():
                shutil.copytree(mod.folder / part, self.folder / part, ignore=shutil.ignore_patterns("*.test.*"), dirs_exist_ok=True)
        for target, source in mod.extras.items():
            if source.is_file():
                (self.folder / target).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, self.folder / target)
        manifest = self.manifest
        # The source is hashed, not the copy: with the board folder watched, Claude Code writes type files into the copy
        # while it is read, and a file it renames away mid-read failed the install.
        manifest["version"] = f"{manifest.get('version', '0.0.0')}-{self._content_hash(mod.folder)}"
        self.write_manifest(manifest)

    def _content_hash(self, folder: Path) -> str:
        digest = hashlib.sha256()
        for path in sorted(item for item in folder.rglob("*") if item.is_file()):
            digest.update(path.relative_to(folder).as_posix().encode("utf-8"))
            digest.update(path.read_bytes())
        return digest.hexdigest()[:VERSION_HASH_CHARS]


class ClaudeMarketplace:
    """The local Claude Code marketplace a cdd home publishes, its ``claude-plugins`` folder: the ``cdd`` plugin
    (`publish_cdd_plugin`), and the mods of the code the server runs (`publish_mods`), listed in its
    ``marketplace.json``. One install publishes into it at a time: installs from the main checkout and a ticket's
    worktree at the same moment both replace the same mod folders, and one would fail on a file the other had just
    removed."""

    # The file in a published mod naming the command its Run install runs.
    INSTALL_COMMAND = "install.json"

    def __init__(self, folder: Path, home: CddHome) -> None:
        self.folder = folder
        self._home = home
        # One install publishes this home's mods at a time; a second waits for it.
        self._publishing = InstallLock(home.folder)

    def plugin(self, name: str) -> PublishedPlugin:
        return PublishedPlugin(self, name)

    @property
    def cdd_plugin(self) -> PublishedPlugin:
        """The ``cdd`` plugin, which declares the cdd server for every chat."""
        return self.plugin(CLAUDE_PLUGIN)

    @property
    def mods(self) -> list[PublishedPlugin]:
        """The plugins of the mods the code the server runs declares."""
        return [self.plugin(mod.name) for mod in PublishedMods(self._home.source).every] if self._home.is_installed else []

    def mod_folder(self, plugin: PublishedPlugin) -> Path:
        """The folder Claude Code loads plugin from when it watches it: a served checkout's own mod folder, so an edit
        there reloads in every chat with no install, else the copy published here."""
        if self._home.is_installed and self._home.mode == self._home.CHECKOUT:
            served = next((mod.folder for mod in PublishedMods(self._home.source).every if mod.name == plugin.name), None)
            if served is not None:
                return served
        return plugin.folder

    @property
    def install_command(self) -> list[str]:
        """What a mod's Run install runs, with the chat's folder added: the served checkout's install script on the
        Python the server runs on. The mod runs it itself because the server may be what is broken."""
        home = self._home
        return [str(home.interpreter.executable), str(home.source / "scripts" / "install.py"), "--ide", _CLAUDE_CODE.ide, "--from-chat"]

    def publish_cdd_plugin(self, server: dict[str, object]) -> list[Path]:
        """Write the ``cdd`` plugin and the listing: the server every chat connects to, and the hook that starts it when a
        chat starts. Its version gains a hash of both: Claude Code keeps a plugin it has already seen at the same version,
        so a changed one needs a new one. The mods of the code the server runs are published with it. Returns the files
        written."""
        plugin = self.cdd_plugin
        declared = {_CLAUDE_CODE.mcp_servers_key: {"cdd": server}}
        command = f'"{self._home.interpreter.windowless}" "{self._home.connect_script}" --start'
        hooks = {"hooks": {"SessionStart": [{"hooks": [{"type": "command", "command": command, "timeout": SERVER_START_SECONDS}]}]}}
        version = f"1.0.0-{hashlib.sha256(json.dumps([declared, hooks], sort_keys=True).encode('utf-8')).hexdigest()[:VERSION_HASH_CHARS]}"
        written = [
            plugin.write_manifest({"name": CLAUDE_PLUGIN, "version": version, "description": CLAUDE_PLUGIN_DESCRIPTION}),
            JsonFile(plugin.folder / ".mcp.json").write(declared),
            JsonFile(plugin.folder / "hooks" / "hooks.json").write(hooks),
        ]
        if self._home.is_installed:
            self.publish_mods(self._home.source)
        return [self._write_listing(), *written]

    def publish_mods(self, code: Path) -> None:
        """Publish the mods code declares, then list every plugin here. A mod that runs an install gets the command it
        runs, read from its own folder since it runs while the server is broken; a checkout served from disk gets the
        file in its own mod folder too."""
        with self._publishing.held():
            for mod in PublishedMods(code).every:
                plugin = self.plugin(mod.name)
                plugin.publish_from(mod)
                if mod.install_command_file:
                    self._write_install_command(plugin, mod, code)
            self._write_listing()

    def _write_install_command(self, plugin: PublishedPlugin, mod: PublishedMod, code: Path) -> None:
        """Give a mod that runs an install the command it runs, in its published folder, and in its own mod folder too
        when the checkout it was published from is the one served from disk."""
        JsonFile(plugin.folder / mod.install_command_file).write({"command": self.install_command})
        if self._home.mode == self._home.CHECKOUT and Path(code).resolve() == self._home.source.resolve():
            JsonFile(mod.folder / mod.install_command_file).write({"command": self.install_command})

    def publish_mods_for_chats(self, is_dev_lane_running: bool) -> None:
        """Publish this lane's mods when its server restarts, then the mods every chat installs, which come from the
        stable lane's marketplace: a dev lane's own, and, on the stable lane, the dev lane's after its own while the dev
        lane's server runs, so a restart of either server leaves the feature's mods in the chats."""
        self.publish_mods(self._home.source)
        if self._home.is_dev_lane or is_dev_lane_running:
            stable = self._home.stable_lane
            stable.marketplace.publish_mods(stable.dev_lane.source)

    def _write_listing(self) -> Path:
        """List every plugin published here, the cdd plugin first; a marketplace naming a missing folder fails to load."""
        folders = sorted(folder for folder in self.folder.iterdir() if folder.is_dir()) if self.folder.is_dir() else []
        published = [plugin for plugin in (self.plugin(folder.name) for folder in folders) if plugin.is_published]
        published.sort(key=lambda plugin: (plugin.name != CLAUDE_PLUGIN, plugin.name))
        plugins = [{"name": plugin.name, "source": f"./{plugin.name}", "description": plugin.description} for plugin in published]
        return JsonFile(self.folder / ".claude-plugin" / "marketplace.json").write(
            {"name": CLAUDE_MARKETPLACE, "owner": {"name": "cdd"}, "plugins": plugins}
        )
