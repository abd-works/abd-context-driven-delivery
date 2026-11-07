"""``~/.cdd/``: the one place the cdd server runs from, whichever checkout ran the install."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

from harness.process.git import Git, RepoConnectError

CDD_HOME_ENV = "CDD_HOME"
CLAUDE_MARKETPLACE = "cdd-home"
CLAUDE_PLUGIN = "cdd"
CLAUDE_PLUGIN_DESCRIPTION = "Connects every Claude Code chat to the one cdd server, naming the chat's folder as its project"
# The cdd-board mod is published from the code the server runs, so every chat's mod matches the server it talks to.
BOARD_PLUGIN = "cdd-board"
BOARD_MOD_FOLDER = Path("harness") / "chat-ui" / "pane"
BOARD_MOD_PARTS = (".claude-plugin", "hooks", "types")
# A commit without the server cannot serve chats, so pinning one would leave every chat without cdd.
SERVER_MODULE = "harness/mcp/mcp_daemon.py"
# The folders under a checkout that hold importable packages, beside the checkout root itself.
IMPORT_FOLDERS = (
    "tools",
    "cdd_guidance/practices",
    "cdd_guidance/actions",
    "cdd_guidance/patterns",
    "cdd_guidance/builders",
)


class RuntimeNotInstalled(Exception):
    """``~/.cdd/runtime.json`` names no checkout, so there is no code to serve."""

    def __init__(self, home: Path) -> None:
        super().__init__(f"cdd is not installed in {home}: run python scripts/install.py from a CDD checkout")
        self.home = home


class PinFailed(Exception):
    """git could not copy the checkout's commit into the pinned runtime."""

    def __init__(self, checkout: Path, detail: str) -> None:
        super().__init__(f"could not pin the cdd runtime to {checkout}: {detail}")
        self.checkout = checkout


class RuntimeRecordUnreadable(Exception):
    """``~/.cdd/runtime.json`` exists but is not readable JSON, so which checkout the server runs is unknown. cdd stops
    rather than read it as not installed, which would pin a new runtime over it."""

    def __init__(self, path: Path, cause: BaseException) -> None:
        super().__init__(f"{path} is not readable JSON ({cause}); fix or remove it, then install again")
        self.path = path
        self.cause = cause


class CddHome:
    """The user's cdd folder: which checkout the one server runs, the Python it runs on, and the server's address.

    The server runs from a pinned copy of a commit, so installing from a worktree never changes the code every chat
    talks to. ``serve_from`` points it at a live checkout instead, for working on CDD itself."""

    PINNED = "pinned"
    CHECKOUT = "checkout"

    def __init__(self, folder: Path | str | None = None) -> None:
        named = folder or os.environ.get(CDD_HOME_ENV) or Path.home() / ".cdd"
        self.folder = Path(named).resolve()

    @property
    def state_path(self) -> Path:
        """Where the running server publishes its address and pid."""
        return self.folder / "server.json"

    @property
    def log_path(self) -> Path:
        return self.folder / "server.log"

    @property
    def connect_script(self) -> Path:
        """The command an IDE runs before it connects: it starts the server when none answers and names the project."""
        return self.folder / "connect.py"

    @property
    def claude_plugins(self) -> Path:
        """The local marketplace holding the ``cdd`` plugin, which declares the cdd server for every Claude Code chat."""
        return self.folder / "claude-plugins"

    def write_claude_plugin(self, server: dict[str, object]) -> list[Path]:
        """Write the ``cdd`` plugin and its marketplace. A server a plugin declares gets ``${CLAUDE_PROJECT_DIR}`` filled
        in with the chat's folder, which a user-level entry never sees. Returns the files written."""
        plugin = self.claude_plugins / CLAUDE_PLUGIN
        files = {
            plugin / ".claude-plugin" / "plugin.json": {"name": CLAUDE_PLUGIN, "version": "1.0.0", "description": CLAUDE_PLUGIN_DESCRIPTION},
            plugin / ".mcp.json": {"mcpServers": {"cdd": server}},
        }
        for path, content in files.items():
            self._write_json(path, content)
        if self.is_installed:
            self.write_board_plugin()
        return [self._write_marketplace(), *files]

    def write_board_plugin(self) -> None:
        """Publish the cdd-board mod from the code the server runs. Its version gains a hash of the mod's files:
        Claude Code keeps a plugin it has already seen at the same version, so a changed mod needs a new one."""
        source = self.source / BOARD_MOD_FOLDER
        if not (source / ".claude-plugin" / "plugin.json").is_file():
            return
        target = self.claude_plugins / BOARD_PLUGIN
        shutil.rmtree(target, ignore_errors=True)
        for part in BOARD_MOD_PARTS:
            if (source / part).is_dir():
                shutil.copytree(source / part, target / part, ignore=shutil.ignore_patterns("*.test.*"))
        manifest_path = target / ".claude-plugin" / "plugin.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["version"] = f"{manifest.get('version', '0.0.0')}-{self._content_hash(target)}"
        self._write_json(manifest_path, manifest)
        self._write_marketplace()

    def _content_hash(self, folder: Path) -> str:
        digest = hashlib.sha256()
        for path in sorted(item for item in folder.rglob("*") if item.is_file()):
            digest.update(path.relative_to(folder).as_posix().encode("utf-8"))
            digest.update(path.read_bytes())
        return digest.hexdigest()[:12]

    def _write_marketplace(self) -> Path:
        """List every plugin published here; a marketplace naming a missing folder fails to load."""
        plugins = []
        for name in (CLAUDE_PLUGIN, BOARD_PLUGIN):
            manifest = self.claude_plugins / name / ".claude-plugin" / "plugin.json"
            if manifest.is_file():
                description = json.loads(manifest.read_text(encoding="utf-8")).get("description", "")
                plugins.append({"name": name, "source": f"./{name}", "description": description})
        path = self.claude_plugins / ".claude-plugin" / "marketplace.json"
        self._write_json(path, {"name": CLAUDE_MARKETPLACE, "owner": {"name": "cdd"}, "plugins": plugins})
        return path

    def _write_json(self, path: Path, content: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(content, indent=2) + "\n", encoding="utf-8")

    @property
    def runtime_record(self) -> Path:
        """Which checkout the server runs, in which mode, on which Python."""
        return self.folder / "runtime.json"

    @property
    def pinned_checkout(self) -> Path:
        return self.folder / "runtime"

    @property
    def is_installed(self) -> bool:
        return bool(self._runtime().get("source"))

    @property
    def source(self) -> Path:
        """The checkout whose code the server runs."""
        named = self._runtime().get("source")
        if not named:
            raise RuntimeNotInstalled(self.folder)
        return Path(named)

    @property
    def mode(self) -> str:
        return self._runtime().get("mode", "")

    @property
    def python(self) -> str:
        return self._runtime().get("python") or sys.executable

    @property
    def server_environment(self) -> dict[str, str]:
        """What the server process needs to import the source checkout's packages and keep bytecode out of it."""
        root = self.source
        entries = [str(root), *(str(root / name) for name in IMPORT_FOLDERS if (root / name).is_dir())]
        return {
            "PYTHONPATH": os.pathsep.join(entries),
            "PYTHONPYCACHEPREFIX": str(self.folder / ".pycache"),
            "PYTHONIOENCODING": "utf-8",
            CDD_HOME_ENV: str(self.folder),
        }

    def install(self, checkout: Path | str, connect_script: Path | str) -> None:
        """First install: pin the runtime to ``checkout``'s commit. Later installs leave the serving code alone."""
        self.folder.mkdir(parents=True, exist_ok=True)
        script = Path(connect_script).read_text(encoding="utf-8")
        if not self.connect_script.is_file() or self.connect_script.read_text(encoding="utf-8") != script:
            self.connect_script.write_text(script, encoding="utf-8")
        if not self.is_installed:
            self.pin(checkout)

    def pin(self, checkout: Path | str) -> str:
        """Copy ``checkout``'s current commit into ``runtime/`` and serve it. Returns the commit."""
        source = Path(checkout).resolve()
        target = self.pinned_checkout
        if not (target / ".git").exists():
            self._git(source, source, "init", "--quiet", str(target))
        self._git(source, target, "fetch", "--quiet", "--no-tags", str(source), "HEAD")
        self._git(source, target, "checkout", "--quiet", "--force", "--detach", "FETCH_HEAD")
        commit = self._git(source, target, "rev-parse", "HEAD")
        if not (target / SERVER_MODULE).is_file():
            raise PinFailed(source, f"commit {commit[:8]} has no {SERVER_MODULE}; commit the one-server code before pinning")
        self._mirror_origin(source, target)
        self._save_runtime(target, self.PINNED, commit=commit)
        self.write_board_plugin()
        return commit

    def _mirror_origin(self, source: Path, target: Path) -> None:
        """Give the pinned copy the checkout's ``origin``: tools that cite the repository, such as the catalog, read it."""
        if not Git(source).succeeds("remote", "get-url", "origin"):
            return
        url = self._git(source, source, "remote", "get-url", "origin")
        has_origin = Git(target).succeeds("remote", "get-url", "origin")
        self._git(source, target, "remote", "set-url" if has_origin else "add", "origin", url)

    def serve_from(self, checkout: Path | str) -> None:
        """Run the server on ``checkout`` as it is on disk, so a ``cdd.restart`` picks up its edits."""
        self._save_runtime(Path(checkout).resolve(), self.CHECKOUT)
        self.write_board_plugin()

    def _git(self, checkout: Path, folder: Path, *arguments: str) -> str:
        """Run git in folder while pinning checkout; a failure is the pin's failure."""
        try:
            return Git(folder).run(*arguments)
        except RepoConnectError as failure:
            raise PinFailed(checkout, str(failure)) from failure

    def _save_runtime(self, source: Path, mode: str, *, commit: str = "") -> None:
        runtime = {"source": str(source), "mode": mode, "python": self.python}
        if commit:
            runtime["commit"] = commit
        self._write_json(self.runtime_record, runtime)

    def _runtime(self) -> dict[str, str]:
        path = self.runtime_record
        if not path.is_file():
            return {}
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as unreadable:
            raise RuntimeRecordUnreadable(path, unreadable) from unreadable
        return {str(key): str(value) for key, value in data.items()} if isinstance(data, dict) else {}
