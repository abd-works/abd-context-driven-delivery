"""Local repository domain model: the clone, its branches, worktrees, commits, and work sessions."""

from __future__ import annotations

import logging
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from harness.agent_tools import agent_instructions, agent_tool, agent_toolset
from harness.agent_tools.agent_tools import tool_subject
from harness.hooks.running_process import RunningProcess
from harness.installation.destination import data_field, language_adapter
from harness.installation.files import command
from harness.mcp.mcp_server import mcp
from space.repo.latest_release import LatestRelease
from space.work_state import WorkState, project_checkout

BACKLOG_FOLDER = "_backlog"
BOARD_FILE = "_board.json"

if TYPE_CHECKING:
    from space.session.session import Session
    from tools.file_manager.file_manager import FileManager

logger = logging.getLogger(__name__)


class RepoConnectError(RuntimeError):
    """Raised when the clone cannot be used as a repository."""


_COMMAND_TIMEOUT_SECONDS = 10
# Push, fetch, and pull wait on the network. Checkout, merge, and worktree rewrite the working
# tree, and stopping one partway leaves a half-switched checkout with a stale index.lock.
_LONG_COMMAND_TIMEOUT_SECONDS = 180
_LONG_COMMANDS = frozenset({"push", "fetch", "pull", "checkout", "merge", "worktree"})


class BranchNameRequiredError(ValueError):
    """Raised when a branch command has no name and none is saved in ``.sessions/session.json``."""

    def __init__(self) -> None:
        super().__init__(
            "branch name is required: pass name, or switch to a branch first so "
            "it is saved in .sessions/session.json"
        )


class DefaultBranchError(ValueError):
    """Raised when a branch or worktree command is aimed at the default branch."""

    def __init__(self, operation: str, default: str) -> None:
        super().__init__(f"cannot {operation} the default branch {default!r}")


class BranchInWorktreeError(RuntimeError):
    """Raised when the branch to close is still checked out in a linked worktree."""

    def __init__(self, branch: str, path: Path) -> None:
        super().__init__(
            f"branch {branch!r} is checked out in the worktree at {path}; "
            "close that worktree first"
        )


class NoOpenWorktreeError(RuntimeError):
    """Raised when close-worktree runs with no worktree saved in ``.sessions/session.json``."""

    def __init__(self) -> None:
        super().__init__("no open worktree: .sessions/session.json has no worktree")


class DirtyBranchSwitchError(RuntimeError):
    """Raised when checkout would move a dirty tree onto another branch."""

    def __init__(self, current: str, wanted: str) -> None:
        self.current = current
        self.wanted = wanted
        super().__init__(
            f"Working tree has uncommitted changes on {current!r}; "
            f"not switching to {wanted!r}. Ask whether to bring this work onto "
            f"the session branch, or create a continuation branch "
            f"(e.g. {wanted}-2)."
        )


class Commit:
    """One git commit. Its data is its sha, subject, full message, and the trailers the message carries, which is what
    an MCP tool that makes a commit answers with."""

    def __init__(self, sha: str, message: str) -> None:
        self._sha = sha
        self._message = message

    @classmethod
    def format(cls, subject: str, trailers: dict[str, str] | None = None) -> str:
        lines = [subject.strip()]
        for key, value in (trailers or {}).items():
            text = (value or "").strip()
            if text:
                lines.append(f"{key}: {text}")
        return "\n".join(lines)

    @classmethod
    def from_message(cls, sha: str, message: str) -> Commit:
        return cls(sha=sha, message=message)

    @property
    @data_field
    def sha(self) -> str:
        return self._sha

    @property
    @data_field
    def subject(self) -> str:
        lines = (self.message or "").splitlines()
        return lines[0].strip() if lines else ""

    @property
    @data_field
    def message(self) -> str:
        return self._message

    @property
    @data_field
    def data(self) -> dict[str, str]:
        """The trailers: each ``Key: value`` line after the subject."""
        lines = (self.message or "").splitlines()
        if not lines:
            return {}
        data: dict[str, str] = {}
        for line in lines[1:]:
            if ": " not in line:
                continue
            key, value = line.split(": ", 1)
            data[key.strip()] = value.strip()
        return data

    @classmethod
    def note_text(cls, fields: dict[str, str]) -> str:
        return "\n".join(f"{key}: {value}" for key, value in fields.items())

    def note_payload(self) -> dict[str, str]:
        out: dict[str, str] = {}
        for line in (self.message or "").splitlines():
            if ": " not in line:
                continue
            key, value = line.split(": ", 1)
            out[key.strip()] = value
        return out


@dataclass
class CliAgents:
    """The doer and judge CLI agents working on a branch. Their status and process ids are kept on the branch's
    ``cli-agent/{branch}`` annotated tag."""

    status: str = "closed"
    doer: str = ""
    doer_pid: int = 0
    judge: str = ""
    judge_pid: int = 0

    @property
    def open(self) -> bool:
        return self.status == "open" and RunningProcess(self.doer_pid).alive

    def message(self) -> str:
        return Commit.note_text(
            {
                "status": self.status,
                "doer": self.doer,
                "doer_pid": str(self.doer_pid or ""),
                "judge": self.judge,
                "judge_pid": str(self.judge_pid or ""),
            }
        )

    @classmethod
    def from_message(cls, text: str) -> CliAgents:
        data = Commit(sha="", message=text).note_payload()
        return cls(
            status=(data.get("status") or "closed").strip() or "closed",
            doer=(data.get("doer") or "").strip(),
            doer_pid=_process_id(data.get("doer_pid")),
            judge=(data.get("judge") or "").strip(),
            judge_pid=_process_id(data.get("judge_pid")),
        )


def _process_id(raw: str | None) -> int:
    text = (raw or "").strip()
    return int(text) if text.isdigit() else 0


@language_adapter(language="typescript")
@agent_toolset
class Repo:
    """Local git clone: its branches, worktrees, commits, and work sessions."""

    def __init__(self, root: str | Path = ".", *, memory: bool = False) -> None:
        self.root = Path(root).resolve()
        self.default_branch = "main"
        self._memory = memory
        if memory:
            self._init_memory_state()

    @classmethod
    @tool_subject
    def current(cls) -> Repo:
        """The clone of the project the running call names. One cdd server answers every chat, so each call reads its
        project from the request and acts on that project's clone, never on a clone named by an earlier call."""
        return cls(project_checkout())

    @property
    def in_memory(self) -> bool:
        return self._memory

    def find_root(self) -> Path | None:
        current = self.root
        if current.is_file():
            current = current.parent
        for candidate in (current, *current.parents):
            if (candidate / ".git").exists():
                return candidate
        return None

    @property
    def is_clone(self) -> bool:
        """Whether git works here: a .git folder holding a HEAD, or the .git file of a linked worktree. A .git folder with
        nothing in it only marks a project's root."""
        root = self.find_root()
        if root is None:
            return False
        marker = root / ".git"
        return marker.is_file() or (marker / "HEAD").is_file()

    @classmethod
    def open(cls, start: str | Path) -> Repo:
        root = cls(start).find_root()
        if root is None:
            raise RepoConnectError(f"not a git clone: {start!r}")
        return cls(root)

    @classmethod
    def memory(cls, root: str | Path = ".") -> Repo:
        return cls(root, memory=True)

    @classmethod
    def git(cls, root: str | Path, *args: str, env: dict[str, str] | None = None, timeout: float | None = None) -> str:
        """Run git in ``root``. ``env`` adds variables to git's environment; ``timeout`` overrides the default limit."""
        found = shutil.which("git")
        if not found:
            for candidate in (
                Path(r"C:\Program Files\Git\cmd\git.exe"),
                Path(r"C:\Program Files\Git\bin\git.exe"),
            ):
                if candidate.is_file():
                    found = str(candidate)
                    break
        if not found:
            raise RepoConnectError("Cannot connect git: `git` is not available.")
        timeout = timeout or (
            _LONG_COMMAND_TIMEOUT_SECONDS
            if args and args[0] in _LONG_COMMANDS
            else _COMMAND_TIMEOUT_SECONDS
        )
        try:
            returncode, stdout, stderr = cls._run_git_process(
                [found, "-c", "core.longpaths=true", "-C", str(root), *args], timeout, env
            )
        except subprocess.TimeoutExpired as exc:
            raise RepoConnectError(
                f"Cannot connect git: git {' '.join(args)} exceeded "
                f"{timeout} seconds in {root}."
            ) from exc
        except OSError as exc:
            raise RepoConnectError(f"Cannot connect git: {exc}.") from exc
        if returncode != 0:
            err = (stderr or stdout or "").strip()
            raise RepoConnectError(
                f"Cannot connect git: git {' '.join(args)} failed in {root}: "
                f"{err}."
            )
        return (stdout or "").strip()

    @classmethod
    def _run_git_process(cls, argv: list[str], timeout: float, env: dict[str, str] | None = None) -> tuple[int, str, str]:
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
            cls._kill_process_tree(process)
            process.communicate()
            raise
        return process.returncode, stdout, stderr

    @classmethod
    def _kill_process_tree(cls, process: subprocess.Popen) -> None:
        # Git for Windows' cmd\git.exe is a launcher; killing only the launcher leaves the real
        # git holding the output pipes, so communicate() would block long past the timeout.
        if os.name == "nt":
            subprocess.run(
                ["taskkill", "/T", "/F", "/PID", str(process.pid)],
                stdin=subprocess.DEVNULL,
                capture_output=True,
                check=False,
            )
            return
        process.kill()

    def _git(self, *args: str) -> str:
        return type(self).git(self.root, *args)

    def _init_memory_state(self) -> None:
        self._branch_names: set[str] = {"main"}
        self._branch = "main"
        self._commit = "sha-init"
        self._commits: list[tuple[list[str], str]] = []
        self._pushes: list[str] = []
        self._deleted: list[str] = []
        self._dirty = False
        self._worktrees: list[Worktree] = [Worktree(self.root, self.branch_named("main"))]
        self._fetches: list[str] = []
        self._pulls: list[str] = []
        self._stash = False
        self._annotated_tags: dict[str, str] = {}

    def branch_named(self, name: str) -> Branch:
        return Branch(self, name)

    def has_branch(self, name: str) -> bool:
        if self._memory:
            return name in self._branch_names
        return bool(self._git("branch", "--list", name).strip())

    @property
    def sessions_folder(self) -> Path:
        """The `.sessions` folder that holds this repository's work sessions and what they share on the board."""
        return WorkState(self.root).sessions_folder

    @property
    def backlog_folder(self) -> Path:
        """Where sessions wait before work starts, and where a session moved back is held."""
        return self.sessions_folder / BACKLOG_FOLDER

    @property
    def board_file(self) -> Path:
        """The file that holds what this repository's sessions share on the board."""
        return self.sessions_folder / BOARD_FILE

    def sessions(self) -> list[Session]:
        """This repository's work sessions, open ones first then closed: not main, and not the folders the sessions share."""
        from space.session.session import Session

        return [Session.load(folder, self.root) for folder in self._work_session_folders()]

    @property
    def current_session(self) -> Session:
        """The session saved as open in ``.sessions/session.json``; main, which works on the whole repository, when none
        is named. Read without becoming the current session."""
        from space.session.session import MAIN_SESSION_NAME, Session

        name = WorkState(self.root).session or MAIN_SESSION_NAME
        return Session.load(self.session_folder(name), self.root)

    def work_session(self, name: str) -> Session | None:
        """This repository's work session called name, open before closed; none when it has none. Only that session's
        folder is read, so a tool that names one session does not load every other."""
        from space.session.session import COMPLETE_FOLDER, MAIN_SESSION_NAME, Session

        if not name or name == MAIN_SESSION_NAME or name.startswith("_"):
            return None
        sessions = self.sessions_folder
        folder = next((folder for folder in (sessions / name, sessions / COMPLETE_FOLDER / name) if folder.is_dir()), None)
        return Session.load(folder, self.root) if folder is not None else None

    def session_folder(self, name: str) -> Path:
        """The folder of the session called name. A ticket on the board lives in the main checkout's ``.sessions``, so
        a chat in the ticket's linked worktree logs there too and the board shows its work. Each checkout keeps its own
        main session."""
        from space.session.session import MAIN_SESSION_NAME

        preferred = self.sessions_folder / name
        candidates = [preferred]
        if name != MAIN_SESSION_NAME:
            candidates.insert(0, Repo(self.primary_root()).sessions_folder / name)
        return next((folder for folder in candidates if (folder / "session.json").is_file()), preferred)

    def _work_session_folders(self) -> list[Path]:
        from space.session.session import COMPLETE_FOLDER, MAIN_SESSION_NAME

        sessions = self.sessions_folder
        if not sessions.is_dir():
            return []
        skipped = {COMPLETE_FOLDER, MAIN_SESSION_NAME}
        # Folders whose names start with `_` are the ones the sessions share, such as the backlog.
        open_folders = [folder for folder in sorted(sessions.iterdir()) if folder.is_dir() and folder.name not in skipped and not folder.name.startswith("_")]
        closed = sessions / COMPLETE_FOLDER
        closed_folders = sorted(folder for folder in closed.iterdir() if folder.is_dir()) if closed.is_dir() else []
        return open_folders + closed_folders

    @property
    def file_manager(self) -> FileManager:
        """Lists, finds, and reads the files anywhere in this repository."""
        from tools.file_manager.file_manager import FileManager

        return FileManager(self.root, (self.root,))

    def path_from_top(self, path: Path | str) -> str:
        """path as written from the repository's top, empty for the top itself, or as it is when it lies outside the
        repository, where a session may work."""
        given = Path(path)
        if not given.is_relative_to(self.root):
            return given.as_posix()
        relative = given.relative_to(self.root).as_posix()
        return "" if relative == "." else relative

    def files_changed_on(self, branch: str) -> list[str]:
        """Paths from the repository root that ``branch`` changed since it left the default branch, with uncommitted changes when it is checked out."""
        if not self.has_branch(branch):
            return []
        committed = self._git("diff", "--name-only", f"{self.default_branch}...{branch}").splitlines()
        if self.current_branch != branch:
            return committed
        uncommitted = self._git("status", "--porcelain", "--untracked-files=all", "--no-renames").splitlines()
        return [*committed, *(line[3:].strip('"') for line in uncommitted)]

    def cli_agent_tag_name(self, branch: str) -> str:
        slug = (branch or "").strip() or "HEAD"
        return f"cli-agent/{slug}"

    def read_cli_agent_tag(self, branch: str) -> CliAgents:
        return CliAgents.from_message(
            self.read_annotated_tag(self.cli_agent_tag_name(branch))
        )

    def write_annotated_tag(self, name: str, message: str, target: str = "HEAD") -> None:
        """Tag ``target`` (a branch, commit, or ``HEAD``) as ``name`` with ``message``, replacing an earlier tag of
        that name."""
        name = (name or "").strip()
        if not name:
            raise ValueError("annotated tag requires a name")
        if self._memory:
            self._annotated_tags[name] = message
            return
        self._git("tag", "-f", "-a", name, "-m", message, target)

    def read_annotated_tag(self, name: str) -> str:
        name = (name or "").strip()
        if not name:
            return ""
        if self._memory:
            return self._annotated_tags.get(name, "")
        try:
            return self._git("tag", "-l", "--format=%(contents)", name)
        except RepoConnectError:
            return ""

    def list_annotated_tags(self, prefix: str = "") -> dict[str, str]:
        prefix = prefix or ""
        if self._memory:
            return {
                name: text
                for name, text in self._annotated_tags.items()
                if name.startswith(prefix)
            }
        try:
            listing = self._git("tag", "-l", f"{prefix}*") if prefix else self._git("tag", "-l")
        except RepoConnectError:
            return {}
        return {
            name: self.read_annotated_tag(name)
            for name in listing.splitlines()
            if name.strip()
        }

    @property
    def current_branch(self) -> str:
        if self._memory:
            return self._branch
        return self._git("rev-parse", "--abbrev-ref", "HEAD")

    @current_branch.setter
    def current_branch(self, name: str) -> None:
        if self.is_dirty() and name != self.current_branch:
            raise DirtyBranchSwitchError(self.current_branch, name)
        if self._memory:
            if name not in self._branch_names:
                raise RepoConnectError(f"unknown branch {name}")
            self._branch = name
            return
        self._git( "checkout", name)

    @property
    def current_commit(self) -> str:
        if self._memory:
            return self._commit
        return self._git("rev-parse", "HEAD")

    def is_dirty(
        self, path: str | Path | None = None, *, untracked: bool = True
    ) -> bool:
        if self._memory:
            return self._dirty
        args = [
            "status",
            "--porcelain",
            "--untracked-files=normal" if untracked else "--untracked-files=no",
        ]
        if path is not None:
            args.extend(["--", self._rel(path)])
        return any(
            not self._is_runtime_log(line)
            for line in self._git(*args).splitlines()
            if line.strip()
        )

    @staticmethod
    def _is_runtime_log(porcelain_line: str) -> bool:
        raw = porcelain_line[3:] if len(porcelain_line) >= 3 else porcelain_line
        name = raw.split(" -> ")[-1].replace("\\", "/").strip()
        return Path(name).name == "events.log"

    def mark_dirty(self, dirty: bool = True) -> None:
        if not self._memory:
            raise RuntimeError("mark_dirty is only supported on Repo.memory()")
        self._dirty = dirty

    def create_branch(self, name: str) -> None:
        if self._memory:
            self._branch_names.add(name)
            return
        self._git("branch", name)

    def checkout_or_create(self, name: str) -> str:
        if self.current_branch == name:
            return name
        if self.is_dirty():
            raise DirtyBranchSwitchError(self.current_branch, name)
        if self._memory:
            self._branch_names.add(name)
            self._branch = name
            return name
        existing = self._git( "branch", "--list", name)
        if existing:
            self._git( "checkout", name)
        else:
            self._git( "checkout", "-b", name)
        return name

    def commit(
        self, paths: list[str], message: str, *, untracked: bool = False
    ) -> str:
        if not paths:
            raise ValueError("commit requires at least one path")
        if self._memory:
            self._commits.append((list(paths), message))
            self._commit = f"commit-{len(self._commits)}"
            self._dirty = False
            return self._commit
        merge_in_progress = (self.root / ".git" / "MERGE_HEAD").is_file()
        if merge_in_progress:
            add_flag = "-A" if untracked else "-u"
            self._git("add", add_flag)
            staged = self._git("diff", "--cached", "--name-only")
            if not staged:
                return self.current_commit
            self._git("commit", "-m", message)
            return self.current_commit
        rels = [self._rel(path) for path in paths]
        add_flag = "-A" if untracked else "-u"
        self._git("add", add_flag, "--", *rels)
        staged = self._git("diff", "--cached", "--name-only", "--", *rels)
        if not staged:
            return self.current_commit
        self._git("commit", "-m", message, "--", *rels)
        return self.current_commit

    def push_upstream(self) -> None:
        if self._memory:
            self._pushes.append(self.current_branch)
            return
        self._git( "push", "-u", "origin", self.current_branch)

    def has_unpushed_commits(self) -> bool:
        if self._memory:
            return False
        try:
            count = self._git("rev-list", "@{upstream}..HEAD", "--count").strip()
            return int(count or "0") > 0
        except RepoConnectError:
            return False

    def needs_push(self) -> bool:
        """True when the current branch has no upstream yet or is ahead of it."""
        if self._memory:
            return True
        if not self._ref_exists(f"refs/remotes/origin/{self.current_branch}"):
            return True
        return self.has_unpushed_commits()

    def checkout_from_default(self, name: str) -> str:
        """Check out ``name``; a missing branch starts from origin's copy, else from the default branch."""
        if self._memory:
            self._branch_names.add(name)
            self._branch = name
            return name
        if self._ref_exists(f"refs/heads/{name}"):
            self._git("checkout", name)
            return name
        self._git("checkout", "-b", name, self._branch_start_point(name))
        return name

    def delete_branch(self, name: str) -> None:
        """Delete merged branch ``name`` here and on origin."""
        if self._memory:
            self._branch_names.discard(name)
            self._deleted.append(name)
            return
        self._git("branch", "-d", name)
        if self._ref_exists(f"refs/remotes/origin/{name}"):
            self._git("push", "origin", "--delete", name)

    def _branch_start_point(self, name: str) -> str:
        if self._ref_exists(f"refs/remotes/origin/{name}"):
            return f"origin/{name}"
        return self._worktree_start_point() or self.default_branch

    def list_worktrees(self) -> list[Worktree]:
        if self._memory:
            return list(self._worktrees)
        trees: list[Worktree] = []
        path = ""
        branch = ""
        for line in self._git("worktree", "list", "--porcelain").splitlines():
            path, branch, trees = self._accumulate_worktree_line(
                line, path, branch, trees
            )
        return self._flush_worktree(
            self._listed_worktree(path, branch), trees
        )

    def _accumulate_worktree_line(
        self,
        line: str,
        path: str,
        branch: str,
        trees: list[Worktree],
    ) -> tuple[str, str, list[Worktree]]:
        if line.startswith("worktree "):
            return (
                line[len("worktree ") :],
                "",
                self._flush_worktree(
                    self._listed_worktree(path, branch), trees
                ),
            )
        if line.startswith("branch "):
            return path, self._branch_from_porcelain(line), trees
        if line == "":
            return (
                "",
                "",
                self._flush_worktree(
                    self._listed_worktree(path, branch), trees
                ),
            )
        return path, branch, trees

    def _branch_from_porcelain(self, line: str) -> str:
        ref = line[len("branch ") :]
        if ref.startswith("refs/heads/"):
            return ref[len("refs/heads/") :]
        return ref

    def _listed_worktree(self, path: str, branch_name: str) -> Worktree | None:
        if not path:
            return None
        return Worktree.from_checkout(Path(path), branch_name)

    def _flush_worktree(
        self, tree: Worktree | None, trees: list[Worktree]
    ) -> list[Worktree]:
        if tree is None:
            return trees
        return trees + [tree]

    def add_worktree(self, path: str | Path, branch: Branch) -> Worktree:
        """Check ``branch`` out in a new worktree at ``path``; the worktree that already has it, when one does."""
        existing = branch.worktree
        if existing is not None:
            return existing
        dest = Path(path)
        if self._memory:
            self._branch_names.add(branch.name)
            added = Worktree(dest, branch)
            self._worktrees.append(added)
            return added
        dest.parent.mkdir(parents=True, exist_ok=True)
        if self._ref_exists(f"refs/heads/{branch.name}"):
            self._git("worktree", "add", str(dest), branch.name)
        else:
            self._git("worktree", "add", "-b", branch.name, str(dest), self._branch_start_point(branch.name))
        return Worktree.from_checkout(dest, branch.name)

    def remove_worktree(self, worktree: Worktree) -> None:
        dest = worktree.path
        if self._memory:
            self._worktrees = [tree for tree in self._worktrees if tree.path != dest]
            return
        try:
            self._git("worktree", "remove", "--force", str(dest))
        except RepoConnectError as exc:
            logger.info("worktree remove failed; forcing directory delete: %s", exc)
            self._force_remove_directory_windows(dest)
        if dest.exists():
            shutil.rmtree(dest, ignore_errors=True)
        if dest.exists():
            self._force_remove_directory_windows(dest)
        if dest.exists():
            return
        try:
            self._git("worktree", "prune")
        except RepoConnectError as exc:
            logger.info("worktree prune failed: %s", exc)

    def _force_remove_directory_windows(self, path: Path) -> bool:
        """Last resort when git/shutil cannot delete a locked checkout (Windows only)."""
        if os.name != "nt":
            return False
        target = path.resolve()
        if not target.exists():
            return True
        user = os.environ.get("USERNAME", "").strip()
        if not user:
            return False
        self._take_windows_ownership(target, user)
        self._rmtree_logged(target)
        if target.exists():
            self._powershell_remove_item(target)
        return not target.exists()

    def _take_windows_ownership(self, target: Path, user: str) -> None:
        for args in (
            ("takeown", "/f", str(target), "/r", "/d", "y"),
            ("icacls", str(target), "/grant", f"{user}:(F)", "/t"),
        ):
            try:
                subprocess.run(list(args), capture_output=True, check=False)
            except OSError as exc:
                logger.info("windows ownership command failed: %s", exc)

    def _rmtree_logged(self, target: Path) -> None:
        try:
            shutil.rmtree(target, ignore_errors=True)
        except OSError as exc:
            logger.info("rmtree failed for %s: %s", target, exc)

    def _powershell_remove_item(self, target: Path) -> None:
        try:
            subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-NonInteractive",
                    "-Command",
                    (
                        f'Remove-Item -LiteralPath "{target}" '
                        "-Recurse -Force -ErrorAction SilentlyContinue"
                    ),
                ],
                capture_output=True,
                check=False,
            )
        except OSError as exc:
            logger.info("powershell Remove-Item failed for %s: %s", target, exc)

    def fetch(self) -> None:
        if self._memory:
            self._fetches.append("origin")
            return
        self._git("fetch", "origin")

    def pull(self) -> None:
        if self._memory:
            self._pulls.append(self.current_branch)
            return
        self._git("pull", "--ff-only")

    def fetch_pull(self) -> None:
        self.fetch()
        self.pull()

    def merge_from(self, other: str, message: str = "") -> str:
        """Merge *other* into the current branch without checking *other* out."""
        if not other or other == self.current_branch:
            return self.current_commit
        if self._memory:
            text = message or f"merge {other} into {self.current_branch}"
            self._commits.append(([], text))
            self._commit = f"merge-{other}-into-{self.current_branch}"
            return self._commit
        if message:
            self._git("merge", other, "-m", message)
        else:
            self._git("merge", other, "--no-edit")
        return self.current_commit

    def push_to(self, branch: str) -> None:
        if self._memory:
            self._pushes.append(branch)
            return
        self._git("push", "origin", f"HEAD:{branch}")

    def has_stash(self) -> bool:
        if self._memory:
            return self._stash
        return bool(self._git("stash", "list"))

    def clear_stash(self) -> None:
        """Drop every stash entry. Session close must not leave worktrees for stash."""
        if self._memory:
            self._stash = False
            return
        if not self.has_stash():
            return
        self._git("stash", "clear")

    def is_linked_worktree(self) -> bool:
        return (self.root / ".git").is_file()

    @property
    def checkout_folder(self) -> Path:
        """The checkout holding this folder; the folder itself when it is in none."""
        return self.find_root() or self.root

    def primary_root(self) -> Path:
        """The repository's main checkout. A linked worktree's ``.git`` is a file naming its git folder, whose
        ``commondir`` leads back to the main checkout's ``.git``; any other checkout is its own main checkout."""
        if self._memory:
            return self.root
        checkout = self.checkout_folder
        marker = checkout / ".git"
        if not marker.is_file():
            return checkout
        worktree_git = (checkout / marker.read_text(encoding="utf-8").split("gitdir:", 1)[-1].strip()).resolve()
        common = worktree_git / "commondir"
        if not common.is_file():
            return checkout
        return (worktree_git / common.read_text(encoding="utf-8").strip()).resolve().parent

    def _ref_exists(self, ref: str) -> bool:
        try:
            self._git("show-ref", "--verify", "--quiet", ref)
            return True
        except RepoConnectError:
            return False

    def _worktree_start_point(self) -> str:
        for candidate in (
            f"origin/{self.default_branch}",
            "origin/main",
            "origin/master",
        ):
            try:
                self._git("rev-parse", "--verify", candidate)
                return candidate
            except RepoConnectError:
                continue
        return ""

    def merge_branch(self, source: str, into: str = "main", message: str = "") -> str:
        if self.is_dirty(untracked=False):
            raise DirtyBranchSwitchError(self.current_branch, into)
        if self._memory:
            if source not in self._branch_names:
                self._branch_names.add(source)
            self._branch = into
            text = message or f"merge {source} into {into}"
            self._commits.append(([], text))
            self._commit = f"merge-{source}-into-{into}"
            return self._commit
        target = self.branch_named(into).worktree
        merge_root = Path(target.path) if target is not None else Path(self.root)
        if target is None and self.current_branch != into:
            self._git("checkout", into)
            merge_root = Path(self.root)
        merge_git = type(self)
        if message:
            merge_git.git(merge_root, "merge", source, "-m", message)
        else:
            merge_git.git(merge_root, "merge", source, "--no-edit")
        return merge_git.git(merge_root, "rev-parse", "HEAD")

    def _last_commit_message(self) -> str:
        if self._memory:
            if not self._commits:
                return ""
            return self._commits[-1][1]
        return self._git("log", "-1", "--pretty=%B")

    def _rel(self, path: str | Path) -> str:
        resolved = Path(path).resolve()
        try:
            return str(resolved.relative_to(self.root)).replace("\\", "/")
        except ValueError:
            return str(resolved).replace("\\", "/")

    @property
    def commits(self) -> list[tuple[list[str], str]]:
        if not self._memory:
            raise RuntimeError("commits is only available on Repo.memory()")
        return self._commits

    @property
    def pushes(self) -> list[str]:
        if not self._memory:
            raise RuntimeError("pushes is only available on Repo.memory()")
        return self._pushes

    @property
    def _branches(self) -> set[str]:
        if not self._memory:
            raise RuntimeError("_branches is only available on Repo.memory()")
        return self._branch_names

    def _agent_repo(self) -> Repo:
        """The checkout repo tools act in. In the main clone that is the worktree saved as open in
        ``.sessions/session.json`` while its folder exists, so the work goes where ``switch_worktree`` moved the branch;
        in a linked worktree, or with no worktree open, it is this checkout."""
        own = self._own_checkout()
        if own.in_memory or own.is_linked_worktree():
            return own
        opened = WorkState(own.root).worktree
        if opened is not None and Path(opened.path).is_dir():
            return opened.repository
        return own

    def _own_checkout(self) -> Repo:
        if self._memory or self.find_root() is not None:
            return self
        return Worktree.open(self.root).repository

    def _primary_repo(self) -> Repo:
        """The main clone; branch commands never act inside a linked worktree."""
        repository = self._own_checkout()
        if repository.in_memory or not repository.is_linked_worktree():
            return repository
        return Repo(repository.primary_root())

    def _work_state(self) -> WorkState:
        return WorkState(self._primary_repo().root)

    def _branch_name(self, name: str) -> str:
        saved = self._work_state().branch
        cleaned = (name or "").strip() or (saved.name if saved is not None else "")
        if not cleaned:
            raise BranchNameRequiredError()
        return cleaned

    @agent_tool
    @mcp
    def switch_branch(self, name: str = "") -> str:
        """Switch the main clone to branch ``name``, creating it when missing.

        ``name`` defaults to ``branch`` in ``.sessions/session.json``. Commits the branch being
        left and pushes it (the default branch is committed but not pushed), checks out
        ``name`` (a new branch starts from origin's copy or the default branch), and saves
        ``name`` as ``branch`` in ``.sessions/session.json``. Does not touch worktrees or sessions.
        """
        wanted = self._branch_name(name)
        repository = self._primary_repo()
        if repository.current_branch != wanted:
            repository.branch_named(repository.current_branch).save(f"branch: switch to {wanted}")
            repository.checkout_from_default(wanted)
        self._work_state().branch = repository.branch_named(wanted)
        return f"on branch {wanted!r} at {repository.root}"

    @agent_tool
    @mcp
    def close_branch(self, name: str = "", commit_message: str = "branch: close") -> str:
        """Close branch ``name``: commit, push, merge into the default branch, push it, delete ``name``.

        ``name`` defaults to ``branch`` in ``.sessions/session.json``. Refuses the default branch and
        a branch still open in a worktree. Deletes ``name`` locally and on origin, leaves the main
        clone on the default branch, and saves the default branch as ``branch``. Does not touch sessions.
        The release that landed (the open session, else ``name``) keeps its end-to-end results, its
        screenshots pushed to ``e2e-latest``; every older release's results are removed and that removal is
        committed and pushed on the default branch.
        """
        wanted = self._branch_name(name)
        repository = self._primary_repo()
        default = repository.default_branch
        if wanted == default:
            raise DefaultBranchError("close", default)
        occupied = repository.branch_named(wanted).worktree
        if occupied is not None and Path(occupied.path).resolve() != Path(repository.root).resolve():
            raise BranchInWorktreeError(wanted, Path(occupied.path))
        release = self._work_state().session or wanted
        self.switch_branch(wanted)
        repository.branch_named(wanted).close(commit_message)
        self._work_state().branch = repository.branch_named(default)
        pruned = [] if repository.in_memory else LatestRelease(repository, release).keep()
        kept = f"; kept {release!r} end-to-end results, removed {', '.join(pruned)}" if pruned else ""
        return f"closed branch {wanted!r}: merged into {default!r}, pushed, and deleted{kept}"

    @agent_tool
    @mcp
    def switch_worktree(self, name: str = "") -> str:
        """Open the sibling worktree for branch ``name``, creating the branch and folder when missing.

        ``name`` defaults to ``branch`` in ``.sessions/session.json`` and must not be the default
        branch. When the main clone has ``name`` checked out, it is committed, pushed, and the main
        clone goes back to the default branch so the worktree can take it. Saves ``branch`` and the
        worktree path as ``worktree`` in ``.sessions/session.json``; later repo tools act in it.
        When the worktree cannot be brought up to date with origin, the reply says so and why.
        """
        wanted = self._branch_name(name)
        primary = self._primary_repo()
        if wanted == primary.default_branch:
            raise DefaultBranchError("open a worktree for", primary.default_branch)
        if primary.current_branch == wanted:
            primary.branch_named(wanted).save(f"worktree: move {wanted} to its worktree")
            primary.checkout_from_default(primary.default_branch)
        branch = primary.branch_named(wanted)
        opened = branch.open_in_worktree()
        state = WorkState(primary.root)
        state.branch = branch
        state.worktree = opened
        behind = f"; not updated from origin: {opened.sync_failure}" if opened.sync_failure else ""
        return f"worktree for {wanted!r} at {opened.path}{behind}"

    @agent_tool
    @mcp
    def close_worktree(self, commit_message: str = "worktree: close") -> str:
        """Close the worktree saved in ``.sessions/session.json``: commit, push its branch, remove the folder.

        Does not merge; the branch stays open as ``branch``. Clears ``worktree`` in
        ``.sessions/session.json`` and returns later repo tools to the main clone.
        """
        state = self._work_state()
        worktree = state.worktree
        if worktree is None:
            raise NoOpenWorktreeError()
        tree = worktree.repository
        branch = tree.branch_named(tree.current_branch)
        branch.save(commit_message)
        Repo(tree.primary_root()).remove_worktree(worktree)
        state.worktree = None
        return f"closed worktree for {branch.name!r}; branch pushed and kept open"

    @command(name="switch-branch")
    @agent_instructions
    def switch_branch_command(self) -> str:
        """Switch the main clone to a branch, creating it when missing.

        Use the branch the user names; otherwise call without a name so the branch saved in
        ``.sessions/session.json`` is used. Call MCP ``repo.switch_branch``."""
        return ""

    @command(name="close-branch")
    @agent_instructions
    def close_branch_command(self) -> str:
        """Close a branch: commit, push, merge into main, push main, delete the branch.

        Use the branch the user names; otherwise call without a name so the branch saved in
        ``.sessions/session.json`` is used. Call MCP ``repo.close_branch``."""
        return ""

    @command(name="switch-worktree")
    @agent_instructions
    def switch_worktree_command(self) -> str:
        """Open the sibling worktree for a branch other than main, creating it when missing.

        Use the branch the user names; otherwise call without a name so the branch saved in
        ``.sessions/session.json`` is used. Call MCP ``repo.switch_worktree``."""
        return ""

    @command(name="close-worktree")
    @agent_instructions
    def close_worktree_command(self) -> str:
        """Close the open worktree: commit, push its branch, remove the folder. The branch stays open.

        Call MCP ``repo.close_worktree``."""
        return ""

    @agent_tool
    @mcp
    def push_commit(
        self,
        message: str,
        *,
        untracked: bool = True,
        sync_remote: bool = True,
    ) -> Commit:
        """Commit the working tree the repo tools act in using ``message`` (subject and optional body)."""
        repository = self._agent_repo()
        text = (message or "").strip()
        if not text:
            raise ValueError("commit message is required")
        sha = repository.commit(
            [str(repository.root)], text, untracked=untracked
        )
        if sync_remote and not repository._memory:
            repository.push_upstream()
        return Commit.from_message(sha, text)

    @command(name="push")
    @agent_instructions
    def push(self, hint: str = "") -> str:
        """Commit local changes. Optional hint: {{hint}}.

        Inspect git status and diff (staged and unstaged) with the Shell tool.
        On Windows PowerShell, chain git commands with ``;`` (``&&`` is not supported).

        Draft a commit message that:
        - Summarizes what changed and why in a short imperative subject.
        - Names practice, fidelity, and artifact format when this session used CDD
          tools (slash commands, MCP tools, or skills), for example bdd-behavior,
          clean-engineering-code, or sketch.
        - Calls out key paths when that clarifies scope.

        If the working tree is clean, say so and do not call ``repo.push_commit``.
        Otherwise call MCP ``repo.push_commit`` with the full message (subject plus body when useful).
        """
        return ""


class Worktree:
    """One checkout of the repository: its folder and the branch checked out there."""

    __slots__ = ("path", "branch", "_repository", "sync_failure")

    def __init__(self, path: Path | str, branch: Branch | None, *, repository: Repo | None = None) -> None:
        self.path = Path(path)
        self.branch = branch
        self._repository = repository
        # Why the last fetch or pull from origin failed; empty while this checkout is up to date with origin.
        self.sync_failure = ""

    @classmethod
    def from_repo(cls, repository: Repo) -> Worktree:
        """The checkout ``repository`` works in, with the branch it has checked out."""
        name = (repository.current_branch or "").strip()
        return cls(repository.root, repository.branch_named(name) if name else None, repository=repository)

    @classmethod
    def from_checkout(cls, path: Path | str, branch_name: str) -> Worktree:
        """The checkout at ``path`` with ``branch_name`` checked out; its branch acts in that checkout."""
        repository = Repo(path)
        name = (branch_name or "").strip()
        return cls(repository.root, repository.branch_named(name) if name else None, repository=repository)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Worktree):
            return NotImplemented
        return self.path == other.path and self.branch == other.branch

    def __hash__(self) -> int:
        return hash((self.path, self.branch))

    def __repr__(self) -> str:
        branch = self.branch.name if self.branch is not None else ""
        return f"Worktree(path={self.path!r}, branch={branch!r})"

    @property
    def repository(self) -> Repo:
        if self._repository is not None:
            return self._repository
        return Repo(self.path)

    @classmethod
    def open(cls, path: str | Path = "") -> Worktree:
        raw = str(path or ".").strip() or "."
        found = Repo(raw).find_root()
        if found is None:
            raise RepoConnectError("repo tools require a git repository")
        return cls.from_repo(Repo(found))

    @staticmethod
    def abbrev_repo_name(folder: str) -> str:
        tokens = [part for part in re.split(r"[-_]+", folder or "") if part]
        if not tokens:
            return folder or "repo"
        if len(tokens) == 1:
            return tokens[0]
        return tokens[0] + "-" + "".join(token[0] for token in tokens[1:])

    @staticmethod
    def dirname(repo_folder: str, branch: Branch) -> str:
        """Sibling directory ``{abbrev}-{short-branch}`` next to the primary clone."""
        slug = branch.name.replace("/", "-")
        ticket = re.search(r"-(\d+)$", slug)
        short = ticket.group(1) if ticket else slug
        if ticket is None and len(short) > 24:
            short = short[:24].rstrip("-")
        return f"{Worktree.abbrev_repo_name(repo_folder)}-{short}"

    def fetch_pull(self) -> None:
        """Bring this checkout up to date with origin. A checkout that cannot reach origin, or whose branch has moved
        apart from origin's, still opens as it is; ``sync_failure`` then says why, so the caller can tell the user the
        work may be behind origin."""
        repository = self.repository
        try:
            repository.fetch()
            repository.pull()
        except RepoConnectError as exc:
            self.sync_failure = str(exc)
            logger.warning("worktree %s is not up to date with origin: %s", self.path, exc)
            return
        self.sync_failure = ""


class Branch:
    """Named branch on a *Repo* — checkout, commit, merge, and close."""

    __slots__ = ("_repo", "_name")

    def __init__(self, repo: Repo, name: str) -> None:
        self._repo = repo
        self._name = (name or "").strip()

    def __eq__(self, other: object) -> bool:
        # A branch is its name: every checkout of one repository shares the same branches.
        if not isinstance(other, Branch):
            return NotImplemented
        return self.name == other.name

    def __hash__(self) -> int:
        return hash(self.name)

    def __repr__(self) -> str:
        return f"Branch({self.name!r})"

    @property
    def repo(self) -> Repo:
        return self._repo

    @property
    @data_field
    def name(self) -> str:
        return self._name

    @property
    @data_field
    def exists(self) -> bool:
        """Whether the repository has this branch yet."""
        return self._repo.has_branch(self.name)

    @property
    @data_field
    def is_checked_out(self) -> bool:
        """Whether the repository has this branch checked out; a commit lands on whatever is checked out."""
        return self.exists and self._repo.current_branch == self.name

    @property
    def worktree(self) -> Worktree | None:
        """The checkout that has this branch checked out; none when no worktree has it."""
        return next((tree for tree in self._repo.list_worktrees() if tree.branch == self), None)

    def checkout(self) -> Branch:
        self._repo.checkout_or_create(self.name)
        return self

    def open_in_worktree(self) -> Worktree:
        """Check out this branch in a sibling worktree and return that worktree."""
        repository = self._repo
        if repository.in_memory:
            self.checkout()
            return Worktree.from_repo(repository)
        existing = self.worktree
        if existing is not None and existing.path.resolve() != repository.root:
            existing.fetch_pull()
            return existing
        if repository.current_branch == self.name:
            opened = Worktree.from_repo(repository)
            opened.fetch_pull()
            return opened
        try:
            # Fetched first so a branch pushed from elsewhere starts from origin's copy.
            repository.fetch()
        except RepoConnectError as exc:
            logger.warning("opening %s from local refs; fetch from origin failed: %s", self.name, exc)
        primary = repository.primary_root()
        opened = repository.add_worktree(primary.parent / Worktree.dirname(primary.name, self), self)
        opened.fetch_pull()
        return opened

    def cli_agents(self) -> CliAgents:
        """The doer and judge CLI agents working on this branch."""
        return self._repo.read_cli_agent_tag(self.name)

    def write_cli_agents(self, agents: CliAgents) -> None:
        """Keep ``agents`` on this branch's ``cli-agent`` tag, which points at this branch."""
        self._repo.write_annotated_tag(self._repo.cli_agent_tag_name(self.name), agents.message(), target=self.name)

    @property
    def head(self) -> Commit:
        return Commit.from_message(
            self._repo.current_commit,
            self._repo._last_commit_message(),
        )

    def commit(self, paths: list[str], message: str) -> Commit:
        sha = self._repo.commit(paths, message)
        return Commit.from_message(sha, message)

    def merge(self, other: Branch, *, message: str = "") -> Commit:

        sha = self._repo.merge_branch(other.name, self.name, message=message)
        return Commit.from_message(sha, message or f"merge {other.name} into {self.name}")

    def save(self, commit_message: str) -> None:
        """Commit every change on this checked-out branch, then push it when origin is behind.

        The default branch is committed locally but never pushed here; closing a branch pushes it.
        """
        repository = self._repo
        if repository.is_dirty():
            repository.commit([str(repository.root)], commit_message, untracked=True)
        if self.name != repository.default_branch and repository.needs_push():
            repository.push_upstream()

    def land_on_default(self) -> None:
        """Merge this branch into the default branch on this clone and push the default branch."""
        repository = self._repo
        default = repository.default_branch
        repository.checkout_from_default(default)
        repository.pull()
        repository.merge_from(self.name, message=f"merge {self.name} into {default}")
        repository.push_upstream()

    def close(self, commit_message: str = "branch: close") -> None:
        """Save this checked-out branch, land it on the default branch, then delete it here and on origin."""
        self.save(commit_message)
        self.land_on_default()
        self._repo.delete_branch(self.name)
