"""``~/.cdd/``: the one place the cdd server runs from, whichever checkout ran the install."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

CDD_HOME_ENV = "CDD_HOME"
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
            self._git(source, "init", "--quiet", str(target))
        self._git(source, "-C", str(target), "fetch", "--quiet", "--no-tags", str(source), "HEAD")
        self._git(source, "-C", str(target), "checkout", "--quiet", "--force", "--detach", "FETCH_HEAD")
        commit = self._git(source, "-C", str(target), "rev-parse", "HEAD")
        if not (target / SERVER_MODULE).is_file():
            raise PinFailed(source, f"commit {commit[:8]} has no {SERVER_MODULE}; commit the one-server code before pinning")
        self._mirror_origin(source, target)
        self._save_runtime(target, self.PINNED, commit=commit)
        return commit

    def _mirror_origin(self, source: Path, target: Path) -> None:
        """Give the pinned copy the checkout's ``origin``: tools that cite the repository, such as the catalog, read it."""
        found = subprocess.run(["git", "remote", "get-url", "origin"], cwd=source, capture_output=True, text=True)
        if found.returncode != 0:
            return
        url = found.stdout.strip()
        has_origin = subprocess.run(["git", "remote", "get-url", "origin"], cwd=target, capture_output=True, text=True).returncode == 0
        self._git(target, "remote", "set-url" if has_origin else "add", "origin", url)

    def serve_from(self, checkout: Path | str) -> None:
        """Run the server on ``checkout`` as it is on disk, so a ``cdd.restart`` picks up its edits."""
        self._save_runtime(Path(checkout).resolve(), self.CHECKOUT)

    def _git(self, checkout: Path, *arguments: str) -> str:
        # Some fixtures nest deeper than Windows' default path limit, and the pinned copy needs every file.
        done = subprocess.run(["git", "-c", "core.longpaths=true", *arguments], cwd=checkout, capture_output=True, text=True)
        if done.returncode != 0:
            raise PinFailed(checkout, done.stderr.strip() or done.stdout.strip())
        return done.stdout.strip()

    def _save_runtime(self, source: Path, mode: str, *, commit: str = "") -> None:
        self.folder.mkdir(parents=True, exist_ok=True)
        runtime = {"source": str(source), "mode": mode, "python": self.python}
        if commit:
            runtime["commit"] = commit
        (self.folder / "runtime.json").write_text(json.dumps(runtime, indent=2) + "\n", encoding="utf-8")

    def _runtime(self) -> dict[str, str]:
        path = self.folder / "runtime.json"
        if not path.is_file():
            return {}
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
        return {str(key): str(value) for key, value in data.items()} if isinstance(data, dict) else {}
