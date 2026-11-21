"""``~/.cdd/``: the one place the cdd server runs from, whichever checkout ran the install."""
from __future__ import annotations

import functools
import os
import sys
from pathlib import Path

from harness.installation.json_file import JsonFile, JsonFileUnreadable
from harness.installation.repository_toolsets import RepositoryToolsets
from harness.git.git import Git, RepoConnectError
from harness.mcp.claude_marketplace import ClaudeMarketplace
from harness.mcp.mcp_address import DEV_LANE_FOLDER
from harness.process.process import PythonInterpreter

CDD_HOME_ENV = "CDD_HOME"
# A commit without the server cannot serve chats, so pinning one would leave every chat without cdd.
SERVER_MODULE = "harness/mcp/mcp_daemon.py"
# What a linked worktree's ``.git`` file starts with, before the path of its folder in the main checkout's ``.git``.
GITDIR_PREFIX = "gitdir:"
# What git's ``HEAD`` file starts with when a branch is out; a detached checkout holds a bare commit instead.
BRANCH_REF_PREFIX = "ref: refs/heads/"


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
    """The user's cdd folder: which checkout the one server runs, the Python it runs on, and the server's address and
    files. The Claude Code marketplace it publishes is its own object (`marketplace`).

    The server runs from a pinned copy of a commit, so installing from a worktree never changes the code every chat
    talks to. ``serve_from`` points it at a live checkout instead, for working on CDD itself."""

    PINNED = "pinned"
    CHECKOUT = "checkout"

    def __init__(self, folder: Path | str | None = None) -> None:
        named = folder or os.environ.get(CDD_HOME_ENV) or Path.home() / ".cdd"
        self.folder = Path(named).resolve()
        self._pinned = Git(self.pinned_checkout)
        # Which checkout the server runs, in which mode, on which Python.
        self._runtime_file = JsonFile(self.folder / "runtime.json", RuntimeRecordUnreadable)
        # Where the running server publishes its address and pid, for tools that look for it without calling it.
        self.state_file = JsonFile(self.folder / "server.json", ServerStateUnreadable)
        # The Claude Code marketplace this home publishes: the cdd plugin and the mods of the code the server runs.
        self.marketplace = ClaudeMarketplace(self.folder / "claude-plugins", self)

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
    def stable_lane(self) -> CddHome:
        """The stable lane's home: this one, or the one a dev lane's home sits in."""
        return CddHome(self.folder.parent) if self.is_dev_lane else self

    @property
    def dev_lane(self) -> CddHome:
        """The dev lane's home inside this stable lane's home."""
        return CddHome(self.folder / DEV_LANE_FOLDER)

    @property
    def runtime_record(self) -> Path:
        """Which checkout the server runs, in which mode, on which Python."""
        return self._runtime_file.path

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
        self.marketplace.publish_mods(self.source)
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
        self.marketplace.publish_mods(self.source)

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
