"""GitRepo — git-shaped collaborator at a clone root (WorkSession.git)."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


_DO_NOT_PROCEED = (
    "Do not proceed unless the user tells you to continue without a git connection."
)


class GitConnectError(RuntimeError):
    """Raised when the clone cannot be used for git."""


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


def find_git_root(start: str | Path) -> Path | None:
    current = Path(start).resolve()
    if current.is_file():
        current = current.parent
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return candidate
    return None


def _git_executable() -> str:
    found = shutil.which("git")
    if found:
        return found
    for candidate in (
        Path(r"C:\Program Files\Git\cmd\git.exe"),
        Path(r"C:\Program Files\Git\bin\git.exe"),
    ):
        if candidate.is_file():
            return str(candidate)
    raise GitConnectError(
        f"Cannot connect git: `git` is not available. {_DO_NOT_PROCEED}"
    )


def _git(root: Path, *args: str) -> str:
    try:
        completed = subprocess.run(
            [_git_executable(), "-C", str(root), *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
    except GitConnectError:
        raise
    except OSError as exc:
        raise GitConnectError(
            f"Cannot connect git: {exc}. {_DO_NOT_PROCEED}"
        ) from exc
    if completed.returncode != 0:
        err = (completed.stderr or completed.stdout or "").strip()
        raise GitConnectError(
            f"Cannot connect git: git {' '.join(args)} failed in {root}: "
            f"{err}. {_DO_NOT_PROCEED}"
        )
    return (completed.stdout or "").strip()


_EVAL_MISTAKES_NOTES = "refs/notes/eval-mistakes"


def _payload_to_note(fields: dict[str, str]) -> str:
    return "\n".join(f"{key}: {value}" for key, value in fields.items())


def _note_to_payload(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in (text or "").splitlines():
        if ": " not in line:
            continue
        key, value = line.split(": ", 1)
        out[key.strip()] = value
    return out


class GitRepo:
    """Git working-tree surface — composed on WorkSession, not a collection repo."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).resolve()

    @property
    def current_branch(self) -> str:
        return _git(self.root, "rev-parse", "--abbrev-ref", "HEAD")

    @property
    def current_commit(self) -> str:
        return _git(self.root, "rev-parse", "HEAD")

    @property
    def branch(self) -> str:
        return self.current_branch

    @branch.setter
    def branch(self, name: str) -> None:
        if self.is_dirty() and name != self.current_branch:
            raise DirtyBranchSwitchError(self.current_branch, name)
        _git(self.root, "checkout", name)

    def create_branch(self, name: str) -> None:
        _git(self.root, "branch", name)

    def checkout_or_create(self, name: str) -> str:
        if self.current_branch == name:
            return name
        if self.is_dirty():
            raise DirtyBranchSwitchError(self.current_branch, name)
        existing = _git(self.root, "branch", "--list", name)
        if existing:
            _git(self.root, "checkout", name)
        else:
            _git(self.root, "checkout", "-b", name)
        return name

    def is_dirty(self, path: str | Path | None = None) -> bool:
        args = ["status", "--porcelain", "--untracked-files=normal"]
        if path is not None:
            args.extend(["--", self._rel(path)])
        return bool(_git(self.root, *args))

    def commit(self, paths: list[str], message: str) -> str:
        if not paths:
            raise ValueError("commit requires at least one path")
        rels = [self._rel(path) for path in paths]
        _git(self.root, "add", "--", *rels)
        staged = _git(self.root, "diff", "--cached", "--name-only", "--", *rels)
        if not staged:
            return self.current_commit
        _git(self.root, "commit", "-m", message, "--", *rels)
        return self.current_commit

    def push(self) -> None:
        _git(self.root, "push", "-u", "origin", self.current_branch)

    def note(
        self,
        sha: str,
        payload: dict[str, str],
        *,
        ref: str = _EVAL_MISTAKES_NOTES,
    ) -> None:
        text = _payload_to_note(payload)
        _git(
            self.root,
            "notes",
            f"--ref={ref}",
            "add",
            "-f",
            "-m",
            text,
            sha,
        )

    def read_notes(
        self, sha: str, *, ref: str = _EVAL_MISTAKES_NOTES
    ) -> dict[str, str]:
        try:
            raw = _git(self.root, "notes", f"--ref={ref}", "show", sha)
        except GitConnectError:
            return {}
        return _note_to_payload(raw)

    def find_mistakes(
        self, entry_ids: list[str], *, ref: str = _EVAL_MISTAKES_NOTES
    ) -> list[dict[str, str]]:
        wanted = set(entry_ids)
        found: list[dict[str, str]] = []
        listing = _git(self.root, "notes", f"--ref={ref}", "list")
        for line in listing.splitlines():
            parts = line.split()
            if len(parts) < 2:
                continue
            sha = parts[1]
            payload = self.read_notes(sha, ref=ref)
            if payload.get("entry_id") in wanted:
                payload.setdefault("introducing_commit", sha)
                found.append(payload)
        return found

    def _rel(self, path: str | Path) -> str:
        resolved = Path(path).resolve()
        try:
            return str(resolved.relative_to(self.root)).replace("\\", "/")
        except ValueError:
            return str(resolved).replace("\\", "/")


class NullGitRepo(GitRepo):
    """In-memory GitRepo for isolated unit tests."""

    def __init__(self) -> None:
        self.root = Path(".")
        self.commits: list[tuple[list[str], str]] = []
        self.pushes: list[str] = []
        self._commit = "sha-init"
        self._branch = "main"
        self._branches: set[str] = {"main"}
        self._dirty = False
        self._notes: dict[str, dict[str, str]] = {}

    @property
    def current_branch(self) -> str:
        return self._branch

    @property
    def current_commit(self) -> str:
        return self._commit

    @property
    def branch(self) -> str:
        return self._branch

    @branch.setter
    def branch(self, name: str) -> None:
        if name not in self._branches:
            raise GitConnectError(f"unknown branch {name}")
        if self._dirty and name != self._branch:
            raise DirtyBranchSwitchError(self._branch, name)
        self._branch = name

    def create_branch(self, name: str) -> None:
        self._branches.add(name)

    def checkout_or_create(self, name: str) -> str:
        if self._branch == name:
            return name
        if self._dirty:
            raise DirtyBranchSwitchError(self._branch, name)
        self._branches.add(name)
        self._branch = name
        return name

    def is_dirty(self, path: str | Path | None = None) -> bool:
        return self._dirty

    def set_dirty(self, dirty: bool = True) -> None:
        self._dirty = dirty

    def commit(self, paths: list[str], message: str) -> str:
        self.commits.append((list(paths), message))
        self._commit = f"commit-{len(self.commits)}"
        self._dirty = False
        return self._commit

    def push(self) -> None:
        self.pushes.append(self.current_branch)

    def note(
        self,
        sha: str,
        payload: dict[str, str],
        *,
        ref: str = _EVAL_MISTAKES_NOTES,
    ) -> None:
        self._notes[sha] = dict(payload)

    def read_notes(
        self, sha: str, *, ref: str = _EVAL_MISTAKES_NOTES
    ) -> dict[str, str]:
        return dict(self._notes.get(sha, {}))

    def find_mistakes(
        self, entry_ids: list[str], *, ref: str = _EVAL_MISTAKES_NOTES
    ) -> list[dict[str, str]]:
        wanted = set(entry_ids)
        found: list[dict[str, str]] = []
        for sha, payload in self._notes.items():
            if payload.get("entry_id") in wanted:
                row = dict(payload)
                row.setdefault("introducing_commit", sha)
                found.append(row)
        return found
