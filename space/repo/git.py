"""Git - runs the git command line in one folder, with a time limit that suits the command."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

_COMMAND_TIMEOUT_SECONDS = 10
# Push, fetch, and pull wait on the network. Checkout, merge, and worktree rewrite the working
# tree, and stopping one partway leaves a half-switched checkout with a stale index.lock.
_LONG_COMMAND_TIMEOUT_SECONDS = 180
_LONG_COMMANDS = frozenset({"push", "fetch", "pull", "checkout", "merge", "worktree"})
# Where Git for Windows installs git when it is not on the PATH, such as under the cdd server.
_WINDOWS_GIT_INSTALLS = (Path(r"C:\Program Files\Git\cmd\git.exe"), Path(r"C:\Program Files\Git\bin\git.exe"))


class RepoConnectError(RuntimeError):
    """Raised when git cannot be run, or a git command fails, in a clone."""


class Git:
    """The git command line, run in one folder. Every repository operation goes through ``run``, so the time limits,
    the stopping of a git that hangs, and the error a failure raises are the same for all of them."""

    def __init__(self, folder: Path | str) -> None:
        self.folder = Path(folder)

    def run(self, *args: str, env: dict[str, str] | None = None, timeout: float | None = None) -> str:
        """Run git with args and answer its output. ``env`` adds variables to git's environment; ``timeout`` overrides
        the limit the command gets by default."""
        limit = timeout or (_LONG_COMMAND_TIMEOUT_SECONDS if args and args[0] in _LONG_COMMANDS else _COMMAND_TIMEOUT_SECONDS)
        command = f"git {' '.join(args)}"
        try:
            code, stdout, stderr = self._run_process([self._executable(), "-c", "core.longpaths=true", "-C", str(self.folder), *args], limit, env)
        except subprocess.TimeoutExpired as exc:
            raise RepoConnectError(f"Cannot connect git: {command} exceeded {limit} seconds in {self.folder}.") from exc
        except OSError as exc:
            raise RepoConnectError(f"Cannot connect git: {exc}.") from exc
        if code != 0:
            raise RepoConnectError(f"Cannot connect git: {command} failed in {self.folder}: {(stderr or stdout or '').strip()}.")
        return (stdout or "").strip()

    def succeeds(self, *args: str) -> bool:
        """Whether git with args succeeds, such as ``show-ref --verify`` for a ref that may not exist."""
        try:
            self.run(*args)
        except RepoConnectError:
            return False
        return True

    @staticmethod
    def _executable() -> str:
        found = shutil.which("git") or next((str(path) for path in _WINDOWS_GIT_INSTALLS if path.is_file()), None)
        if not found:
            raise RepoConnectError("Cannot connect git: `git` is not available.")
        return found

    def _run_process(self, argv: list[str], timeout: float, env: dict[str, str] | None = None) -> tuple[int, str, str]:
        process = subprocess.Popen(
            argv,
            env={**os.environ, **env} if env else None,
            # Under the MCP stdio host, an inherited stdin pipe can hang git on Windows.
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            # The cdd server runs without a console, so on Windows each git it starts would open a window of its own.
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        try:
            stdout, stderr = process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            self._kill_process_tree(process)
            process.communicate()
            raise
        return process.returncode, stdout, stderr

    @staticmethod
    def _kill_process_tree(process: subprocess.Popen) -> None:
        # Git for Windows' cmd\git.exe is a launcher; killing only the launcher leaves the real
        # git holding the output pipes, so communicate() would block long past the timeout.
        if os.name == "nt":
            subprocess.run(["taskkill", "/T", "/F", "/PID", str(process.pid)], stdin=subprocess.DEVNULL, capture_output=True, check=False)
            return
        process.kill()
