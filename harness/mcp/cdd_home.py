"""``~/.cdd/``: the one place the cdd server runs from, whichever checkout ran the install."""
from __future__ import annotations

import functools
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

from harness.installation.ide_layout import IdeLayout
from harness.installation.json_file import JsonFile, JsonFileUnreadable
from harness.installation.repository_toolsets import RepositoryToolsets
from harness.git.git import Git, RepoConnectError
from harness.mcp.mcp_address import DEV_LANE_FOLDER
from harness.process.process import PythonInterpreter

CDD_HOME_ENV = "CDD_HOME"
CLAUDE_MARKETPLACE = "cdd-home"
CLAUDE_PLUGIN = "cdd"
CLAUDE_PLUGIN_DESCRIPTION = "Connects every Claude Code chat to the one cdd server, starting it when a chat starts"
# How long the chat-start hook may take to start a server that was not running: a cold start imports every toolset.
SERVER_START_SECONDS = 90
# How much of a content hash a plugin version carries: enough that two different contents never share a version.
VERSION_HASH_CHARS = 12
# The cdd-board mod is published from the code the server runs, so every chat's mod matches the server it talks to.
BOARD_PLUGIN = "cdd-board"
BOARD_MOD_FOLDER = Path("harness") / "chat-ui" / "pane"
# The prompt queue is a mod beside the chat bar, published the same way, so every chat can queue prompts.
QUEUE_PLUGIN = "prompt-queue"
QUEUE_MOD_FOLDER = Path("tools") / "prompt_queue"
# The parts of a mod Claude Code loads; its tests and the rest of its folder stay in the checkout.
MOD_PARTS = (".claude-plugin", "hooks", "types")
# The chat bar opens a diagram in the draw.io viewer, so the viewer is published inside the mod: a chat in any project
# finds it there, not only one in a CDD checkout. It is copied as a file; the harness does not import it.
DRAWIO_VIEWER = Path("tools") / "drawio_viewer" / "drawio_viewer.py"
BOARD_DRAWIO_VIEWER = Path("drawio-viewer") / "drawio_viewer.py"
# A commit without the server cannot serve chats, so pinning one would leave every chat without cdd.
SERVER_MODULE = "harness/mcp/mcp_daemon.py"
# What a linked worktree's ``.git`` file starts with, before the path of its folder in the main checkout's ``.git``.
GITDIR_PREFIX = "gitdir:"
# What git's ``HEAD`` file starts with when a branch is out; a detached checkout holds a bare commit instead.
BRANCH_REF_PREFIX = "ref: refs/heads/"
# Claude Code, the IDE whose plugins this home publishes.
_CLAUDE_CODE = IdeLayout("Claude")


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


class RuntimeRecordUnreadable(JsonFileUnreadable):
    """``~/.cdd/runtime.json`` exists but is not readable JSON, so which checkout the server runs is unknown. cdd stops
    rather than read it as not installed, which would pin a new runtime over it."""

    def message(self, path: Path, cause: Exception) -> str:
        return f"{path} is not readable JSON ({cause}); fix or remove it, then install again"


class ServerStateUnreadable(JsonFileUnreadable):
    """The file where the cdd server publishes its address and pid exists but is not readable JSON."""

    def message(self, path: Path, cause: Exception) -> str:
        return f"{path} is not readable JSON ({cause}); remove it and the server writes it again when it starts"


class CddHome:
    """The user's cdd folder: which checkout the one server runs, the Python it runs on, and the server's address.

    The server runs from a pinned copy of a commit, so installing from a worktree never changes the code every chat
    talks to. ``serve_from`` points it at a live checkout instead, for working on CDD itself."""

    PINNED = "pinned"
    CHECKOUT = "checkout"
    # The file in the published board mod naming the command its Run install runs.
    INSTALL_COMMAND = "install.json"

    def __init__(self, folder: Path | str | None = None) -> None:
        named = folder or os.environ.get(CDD_HOME_ENV) or Path.home() / ".cdd"
        self.folder = Path(named).resolve()
        self._pinned = Git(self.pinned_checkout)
        # Which checkout the server runs, in which mode, on which Python.
        self._runtime_file = JsonFile(self.folder / "runtime.json", RuntimeRecordUnreadable)
        # Where the running server publishes its address and pid, for tools that look for it without calling it.
        self.state_file = JsonFile(self.folder / "server.json", ServerStateUnreadable)

    @property
    def is_dev_lane(self) -> bool:
        """Whether this is the dev lane's home, whose server serves a feature branch beside the stable lane's."""
        return self.folder.name == DEV_LANE_FOLDER

    @property
    def state_path(self) -> Path:
        """Where the running server publishes its address and pid."""
        return self.state_file.path

    @property
    def log_path(self) -> Path:
        return self.folder / "server.log"

    @property
    def connect_script(self) -> Path:
        """The command an IDE runs before it connects: it starts the server when none answers and names the project."""
        return self.folder / "connect.py"

    @property
    def _start_command(self) -> str:
        """What the cdd plugin runs when a chat starts: the connect script, starting the server when none answers. It
        prints nothing, so it runs without a console window."""
        return f'"{self.interpreter.windowless}" "{self.connect_script}" --start'

    @property
    def claude_plugins(self) -> Path:
        """The local marketplace holding the ``cdd`` plugin, which declares the cdd server for every Claude Code chat."""
        return self.folder / "claude-plugins"

    def write_claude_plugin(self, server: dict[str, object]) -> list[Path]:
        """Write the ``cdd`` plugin and its marketplace: the server every chat connects to, and the hook that starts it
        when a chat starts. Its version gains a hash of both: Claude Code keeps a plugin it has already seen at the same
        version, so a changed one needs a new one. Returns the files written."""
        plugin = self.claude_plugins / CLAUDE_PLUGIN
        declared = {_CLAUDE_CODE.mcp_servers_key: {"cdd": server}}
        hooks = {"hooks": {"SessionStart": [{"hooks": [{"type": "command", "command": self._start_command, "timeout": SERVER_START_SECONDS}]}]}}
        version = f"1.0.0-{hashlib.sha256(json.dumps([declared, hooks], sort_keys=True).encode('utf-8')).hexdigest()[:VERSION_HASH_CHARS]}"
        files = {
            plugin / ".claude-plugin" / "plugin.json": {"name": CLAUDE_PLUGIN, "version": version, "description": CLAUDE_PLUGIN_DESCRIPTION},
            plugin / ".mcp.json": declared,
            plugin / "hooks" / "hooks.json": hooks,
        }
        for path, content in files.items():
            JsonFile(path).write(content)
        if self.is_installed:
            self.write_mod_plugins()
        return [self._write_marketplace(), *files]

    def write_mod_plugins(self) -> None:
        """Publish the mods from the code the server runs."""
        self._publish_mods(self.source)

    def publish_mods_of(self, lane: CddHome) -> None:
        """Publish the mods of the code lane's server runs into this home's marketplace. Every chat installs its mods
        from the stable lane's home, so a dev lane's install publishes there too, or the person keeps the stable lane's
        mods while the feature changes them."""
        self._publish_mods(lane.source)

    def _publish_mods(self, code: Path) -> None:
        """Publish the mods of code: the cdd-board mod, with the draw.io viewer its chat bar opens diagrams in and the
        install command it runs, and the prompt queue mod; then list them in the marketplace."""
        board = self._publish_mod(code, BOARD_MOD_FOLDER, BOARD_PLUGIN)
        if board is not None:
            self._add_board_extras(code, board)
        self._publish_mod(code, QUEUE_MOD_FOLDER, QUEUE_PLUGIN)
        self._write_marketplace()

    def _publish_mod(self, code: Path, folder: Path, name: str) -> Path | None:
        """Copy the mod in folder of code to the plugin called name; none when the code has no such mod. Its version
        gains a hash of the mod's files: Claude Code keeps a plugin it has already seen at the same version, so a
        changed mod needs a new one."""
        source = code / folder
        if not (source / ".claude-plugin" / "plugin.json").is_file():
            return None
        target = self.claude_plugins / name
        self._copy_mod(source, target)
        manifest_file = JsonFile(target / ".claude-plugin" / "plugin.json")
        manifest = manifest_file.read()
        # The source is hashed, not the copy: with the board folder watched, Claude Code writes type files into the copy
        # while it is read, and a file it renames away mid-read failed the install.
        manifest["version"] = f"{manifest.get('version', '0.0.0')}-{self._content_hash(source)}"
        manifest_file.write(manifest)
        return target

    def _add_board_extras(self, code: Path, target: Path) -> None:
        """The install command the chat bar runs, read from its own folder since it runs while the server is broken, and
        the draw.io viewer it opens diagrams in."""
        JsonFile(target / self.INSTALL_COMMAND).write({"command": self.install_command})
        if self.mode == self.CHECKOUT:
            JsonFile(self.source / BOARD_MOD_FOLDER / self.INSTALL_COMMAND).write({"command": self.install_command})
        if (code / DRAWIO_VIEWER).is_file():
            (target / BOARD_DRAWIO_VIEWER).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(code / DRAWIO_VIEWER, target / BOARD_DRAWIO_VIEWER)

    def _copy_mod(self, source: Path, target: Path) -> None:
        """Copy the mod's parts, without their tests."""
        # A file the running app holds open can survive the delete on Windows, so the copy writes over what is left.
        shutil.rmtree(target, ignore_errors=True)
        for part in MOD_PARTS:
            if (source / part).is_dir():
                shutil.copytree(source / part, target / part, ignore=shutil.ignore_patterns("*.test.*"), dirs_exist_ok=True)

    def _content_hash(self, folder: Path) -> str:
        digest = hashlib.sha256()
        for path in sorted(item for item in folder.rglob("*") if item.is_file()):
            digest.update(path.relative_to(folder).as_posix().encode("utf-8"))
            digest.update(path.read_bytes())
        return digest.hexdigest()[:VERSION_HASH_CHARS]

    def _write_marketplace(self) -> Path:
        """List every plugin published here; a marketplace naming a missing folder fails to load."""
        plugins = []
        for name in (CLAUDE_PLUGIN, BOARD_PLUGIN, QUEUE_PLUGIN):
            manifest = JsonFile(self.claude_plugins / name / ".claude-plugin" / "plugin.json")
            if manifest.exists():
                description = manifest.read().get("description", "")
                plugins.append({"name": name, "source": f"./{name}", "description": description})
        marketplace = JsonFile(self.claude_plugins / ".claude-plugin" / "marketplace.json")
        return marketplace.write({"name": CLAUDE_MARKETPLACE, "owner": {"name": "cdd"}, "plugins": plugins})

    @property
    def board_folder(self) -> Path:
        """The folder Claude Code loads the board mod from: a served checkout's own mod folder, so an edit there reloads
        in every chat with no install, else the copy published here."""
        if self.mode == self.CHECKOUT:
            return self.source / BOARD_MOD_FOLDER
        return self.claude_plugins / BOARD_PLUGIN

    @property
    def runtime_record(self) -> Path:
        """Which checkout the server runs, in which mode, on which Python."""
        return self._runtime_file.path

    @property
    def pinned_checkout(self) -> Path:
        return self.folder / "runtime"

    def take_language_adapters(self, written: Path, ide_folder: str) -> Path:
        """Copy the language adapters an install wrote, the folder written, into the pinned runtime under its IDE folder
        ide_folder, in place of any an earlier pin left. The apps this home's server launches run from the runtime and
        import the CDD domain through those adapters, which git never copies there. A server started from the runtime
        keeps its folders open on Windows, so they outlive the removal empty and the copy writes into them. Answers
        where they went."""
        target = self.pinned_checkout / ide_folder / "language-adapters"
        shutil.rmtree(target, ignore_errors=True)
        shutil.copytree(written, target, dirs_exist_ok=True)
        return target

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
    def served_branch(self) -> str:
        """The branch the served code came from, so a chat can tell which feature it runs against; empty when the
        served checkout had no branch out."""
        return self._runtime().get("branch", "")

    @property
    def served_worktree(self) -> Path | None:
        """The checkout the served code came from: for a pinned runtime the worktree it was pinned from, not the copy."""
        named = self._runtime().get("worktree")
        return Path(named) if named else None

    def is_pinned_to(self, checkout: Path | str) -> bool:
        """True when the pinned runtime serves ``checkout``'s current commit."""
        source = Path(checkout).resolve()
        return self._runtime().get("commit", "") == self._git(source, Git(source), "rev-parse", "HEAD")

    @functools.cached_property
    def interpreter(self) -> PythonInterpreter:
        """The Python the server runs on: the one the first install recorded, else the one running this install."""
        return PythonInterpreter(self._runtime().get("python") or sys.executable)

    @property
    def install_command(self) -> list[str]:
        """What the board mod's Run install runs, with the chat's folder added: the served checkout's install script on
        the Python the server runs on. The mod runs it itself because the server may be what is broken."""
        return [str(self.interpreter.executable), str(self.source / "scripts" / "install.py"), "--ide", _CLAUDE_CODE.ide, "--from-chat"]

    @property
    def server_environment(self) -> dict[str, str]:
        """What the server process needs to import the source checkout's packages and keep bytecode out of it: the
        checkout's toolsets say both, as they do for the hook daemon."""
        toolsets = RepositoryToolsets(self.source)
        return {
            "PYTHONPATH": toolsets.pythonpath(),
            "PYTHONPYCACHEPREFIX": toolsets.pycache_prefix(),
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
        source_git = Git(source)
        target = self.pinned_checkout
        if not (target / ".git").exists():
            self._git(source, source_git, "init", "--quiet", str(target))
        self._git(source, self._pinned, "fetch", "--quiet", "--no-tags", str(source), "HEAD")
        self._git(source, self._pinned, "checkout", "--quiet", "--force", "--detach", "FETCH_HEAD")
        commit = self._git(source, self._pinned, "rev-parse", "HEAD")
        if not (target / SERVER_MODULE).is_file():
            raise PinFailed(source, f"commit {commit[:8]} has no {SERVER_MODULE}; commit the one-server code before pinning")
        self._mirror_origin(source, source_git)
        self._save_runtime(source, self.PINNED, commit=commit)
        self.write_mod_plugins()
        return commit

    def _mirror_origin(self, source: Path, source_git: Git) -> None:
        """Give the pinned copy the checkout's ``origin``: tools that cite the repository, such as the catalog, read it."""
        if not source_git.succeeds("remote", "get-url", "origin"):
            return
        url = self._git(source, source_git, "remote", "get-url", "origin")
        has_origin = self._pinned.succeeds("remote", "get-url", "origin")
        self._git(source, self._pinned, "remote", "set-url" if has_origin else "add", "origin", url)

    def serve_current(self, checkout: Path | str) -> None:
        """Serve ``checkout``'s current code the way the server already serves it: as it is on disk for a person working
        on CDD itself, who chose that, else pinned to its current commit."""
        if self.is_installed and self.mode == self.CHECKOUT:
            self.serve_from(checkout)
            return
        self.pin(checkout)

    def serve_from(self, checkout: Path | str) -> None:
        """Run the server on ``checkout`` as it is on disk, so a ``cdd.restart`` picks up its edits."""
        self._save_runtime(Path(checkout).resolve(), self.CHECKOUT)
        self.write_mod_plugins()

    def _branch_of(self, checkout: Path) -> str:
        """The branch the checkout has out; none for a detached checkout or a folder that is not a git checkout. It reads
        git's ``HEAD`` file rather than running git, because serving a checkout from disk runs on every install."""
        git_folder = checkout / ".git"
        if git_folder.is_file():
            git_folder = checkout / git_folder.read_text(encoding="utf-8").removeprefix(GITDIR_PREFIX).strip()
        head = git_folder / "HEAD"
        if not head.is_file():
            return ""
        named = head.read_text(encoding="utf-8").strip()
        if not named.startswith(BRANCH_REF_PREFIX):
            return ""
        return named.removeprefix(BRANCH_REF_PREFIX)

    def _git(self, checkout: Path, git: Git, *arguments: str) -> str:
        """Run git while pinning checkout; a failure is the pin's failure."""
        try:
            return git.run(*arguments)
        except RepoConnectError as failure:
            raise PinFailed(checkout, str(failure)) from failure

    def _save_runtime(self, served_from: Path, mode: str, commit: str = "") -> None:
        """Record the code the server runs: a pinned commit runs from the copy in ``runtime/``, a checkout from disk runs
        where it is; either way the record names the worktree it came from and that worktree's branch."""
        source = self.pinned_checkout if mode == self.PINNED else served_from
        runtime = {"source": str(source), "mode": mode, "python": str(self.interpreter.executable), "worktree": str(served_from)}
        if commit:
            runtime["commit"] = commit
        branch = self._branch_of(served_from)
        if branch:
            runtime["branch"] = branch
        self._runtime_file.write(runtime)

    def _runtime(self) -> dict[str, str]:
        return {str(key): str(value) for key, value in self._runtime_file.read().items()}
