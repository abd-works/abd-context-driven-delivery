# @toolset-manifest python -m tools manifest git.git:Git
"""Git + GitHub domain model — repo, branches, commits, project tickets."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from tools.tool import toolset

_GIT_DO_NOT_PROCEED = (
    "Do not proceed unless the user tells you to continue without a git connection."
)
_GH_DO_NOT_PROCEED = (
    "Do not proceed unless the user tells you to continue without GitHub CLI access."
)


class GitConnectError(RuntimeError):
    """Raised when the clone cannot be used for git."""


class GhConnectError(RuntimeError):
    """Raised when gh cannot be used."""


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


class TicketNotFoundError(LookupError):
    """Raised when a GitHub issue reference does not resolve."""


DEFAULT_PROJECT_STATES: tuple[str, ...] = ("Backlog", "In Progress", "Done")
_ISSUE_NUMBER = re.compile(r"^\d+$")


@dataclass
class Commit:
    sha: str
    message: str
    data: dict[str, str] = field(default_factory=dict)

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
        return cls(sha=sha, message=message, data=cls.trailers(message))

    @classmethod
    def trailers(cls, message: str) -> dict[str, str]:
        lines = (message or "").splitlines()
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

    @classmethod
    def note_payload(cls, text: str) -> dict[str, str]:
        out: dict[str, str] = {}
        for line in (text or "").splitlines():
            if ": " not in line:
                continue
            key, value = line.split(": ", 1)
            out[key.strip()] = value
        return out


@dataclass
class TicketState:
    name: str

    @classmethod
    def backlog(cls) -> TicketState:
        return cls(DEFAULT_PROJECT_STATES[0])

    @classmethod
    def in_progress(cls) -> TicketState:
        return cls(DEFAULT_PROJECT_STATES[1])

    @classmethod
    def done(cls) -> TicketState:
        return cls(DEFAULT_PROJECT_STATES[2])


@dataclass
class Ticket:
    number: int
    title: str
    body: str
    url: str = ""
    state: TicketState | None = None
    data: dict[str, str] = field(default_factory=dict)
    _repo: Repo | None = field(default=None, repr=False, compare=False)

    @property
    def closed(self) -> bool:
        return self.data.get("closed") == "true"

    def close(self) -> None:
        repo = self._repo
        if repo is None:
            raise RuntimeError("Ticket.close requires a repo")
        if repo._memory:
            if self.number not in repo._tickets:
                raise TicketNotFoundError(f"GitHub issue not found: {self.number}")
            repo._closed_tickets.add(self.number)
            self.data["closed"] = "true"
            return
        repo._gh("issue", "close", str(self.number))
        self.data["closed"] = "true"

    def set_status(self, state_name: str) -> Ticket:
        repo = self._repo
        if repo is None:
            raise RuntimeError("Ticket.set_status requires a repo")
        project = repo.project
        if project is None:
            raise RuntimeError("attach_project before setting ticket status")
        state = project.state_named(state_name)
        if repo._memory:
            repo._ticket_project_state[self.number] = state_name
            self.state = state
            return self
        item_raw = repo._gh(
            "project",
            "item-add",
            str(project.number),
            "--owner",
            project.owner,
            "--url",
            self.url,
            "--format",
            "json",
        )
        item = json.loads(item_raw or "{}")
        item_id = item.get("id")
        if not item_id:
            raise GhConnectError(
                f"Could not add issue to project. {_GH_DO_NOT_PROCEED}"
            )
        repo._gh(
            "project",
            "item-edit",
            str(project.number),
            "--owner",
            project.owner,
            "--url",
            self.url,
            "--field",
            "Status",
            "--value",
            state_name,
        )
        self.state = state
        return self

    @classmethod
    def parse_number(cls, ref: str) -> int:
        cleaned = ref.strip()
        if not cleaned:
            raise ValueError(f"not a GitHub issue reference: {ref!r}")
        if cleaned.startswith("#"):
            return int(cleaned[1:])
        if "#" in cleaned:
            suffix = cleaned.rsplit("#", 1)[-1]
            if _ISSUE_NUMBER.match(suffix):
                return int(suffix)
        if "/issues/" in cleaned:
            suffix = cleaned.rstrip("/").split("/")[-1]
            if _ISSUE_NUMBER.match(suffix):
                return int(suffix)
        if _ISSUE_NUMBER.match(cleaned):
            return int(cleaned)
        raise ValueError(f"not a GitHub issue reference: {ref!r}")

    @classmethod
    def github_ref(cls, owner: str, repo: str, number: int) -> str:
        return f"{owner}/{repo}#{number}"


class Branch:
    """Named branch on a repo — checkout, commit, merge."""

    __slots__ = ("_repo", "name")

    def __init__(self, repo: Repo, name: str) -> None:
        self._repo = repo
        self.name = name

    def checkout(self) -> Branch:
        self._repo.checkout_or_create(self.name)
        return self

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


class Project:
    """GitHub Project board on a repo — owns ticket states."""

    __slots__ = ("_repo", "owner", "number", "states")

    def __init__(self, repo: Repo, owner: str, number: int) -> None:
        self._repo = repo
        self.owner = owner
        self.number = number
        self.states = [TicketState(name) for name in DEFAULT_PROJECT_STATES]

    def state_named(self, name: str) -> TicketState:
        for state in self.states:
            if state.name == name:
                return state
        raise ValueError(f"unknown project state: {name!r}")

    def link_repository(self) -> None:
        """Attach this org project to the current GitHub repository."""
        repo = self._repo
        owner, name = repo.owner_repo()
        if repo._memory:
            repo._project_links.append((self.owner, self.number, f"{owner}/{name}"))
            return
        repo._gh(
            "project",
            "link",
            str(self.number),
            "--owner",
            self.owner,
            "--repo",
            f"{owner}/{name}",
        )


class Repo:
    """Local git clone with optional GitHub project + tickets."""

    NOTES_REF = "refs/notes/eval-mistakes"

    def __init__(
        self,
        root: str | Path,
        *,
        memory: bool = False,
        owner: str = "",
        repo_name: str = "",
    ) -> None:
        self.root = Path(root).resolve()
        self.default_branch = "main"
        self._memory = memory
        self._owner = owner
        self._repo_name = repo_name
        self._project: Project | None = None
        self._tickets: dict[int, Ticket] = {}
        self._ticket_project_state: dict[int, str] = {}
        self._closed_tickets: set[int] = set()
        if memory:
            self._init_memory_state()

    @classmethod
    def find_root(cls, start: str | Path) -> Path | None:
        current = Path(start).resolve()
        if current.is_file():
            current = current.parent
        for candidate in (current, *current.parents):
            if (candidate / ".git").exists():
                return candidate
        return None

    @classmethod
    def open(cls, start: str | Path) -> Repo:
        root = cls.find_root(start)
        if root is None:
            raise GitConnectError(f"not a git clone: {start!r}")
        return cls(root)

    @classmethod
    def memory(cls, root: str | Path = ".", *, owner: str = "demo-org", repo_name: str = "demo-repo") -> Repo:
        return cls(root, memory=True, owner=owner, repo_name=repo_name)

    @classmethod
    def git(cls, root: str | Path, *args: str) -> str:
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
            raise GitConnectError(
                f"Cannot connect git: `git` is not available. {_GIT_DO_NOT_PROCEED}"
            )
        try:
            completed = subprocess.run(
                [found, "-C", str(root), *args],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
        except OSError as exc:
            raise GitConnectError(
                f"Cannot connect git: {exc}. {_GIT_DO_NOT_PROCEED}"
            ) from exc
        if completed.returncode != 0:
            err = (completed.stderr or completed.stdout or "").strip()
            raise GitConnectError(
                f"Cannot connect git: git {' '.join(args)} failed in {root}: "
                f"{err}. {_GIT_DO_NOT_PROCEED}"
            )
        return (completed.stdout or "").strip()

    @classmethod
    def gh(
        cls,
        *args: str,
        cwd: str | Path | None = None,
        stdin: str | None = None,
    ) -> str:
        found = shutil.which("gh")
        if not found:
            raise GhConnectError(
                f"Cannot connect gh: `gh` is not available. {_GH_DO_NOT_PROCEED}"
            )
        try:
            completed = subprocess.run(
                [found, *args],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
                cwd=str(cwd) if cwd is not None else None,
                input=stdin,
            )
        except OSError as exc:
            raise GhConnectError(
                f"Cannot connect gh: {exc}. {_GH_DO_NOT_PROCEED}"
            ) from exc
        if completed.returncode != 0:
            err = (completed.stderr or completed.stdout or "").strip()
            shown = " ".join(a for a in args if a != stdin)
            raise GhConnectError(
                f"Cannot connect gh: gh {shown} failed: {err}. {_GH_DO_NOT_PROCEED}"
            )
        return (completed.stdout or "").strip()

    def _git(self, *args: str) -> str:
        return type(self).git(self.root, *args)

    def _gh(self, *args: str, stdin: str | None = None) -> str:
        return type(self).gh(*args, cwd=self.root, stdin=stdin)

    def _init_memory_state(self) -> None:
        self._branch_names: set[str] = {"main"}
        self._branch = "main"
        self._commit = "sha-init"
        self._commits: list[tuple[list[str], str]] = []
        self._pushes: list[str] = []
        self._dirty = False
        self._notes: dict[str, dict[str, str]] = {}
        self._project_links: list[tuple[str, int, str]] = []

    @property
    def project(self) -> Project | None:
        return self._project

    def attach_project(self, owner: str, number: int) -> Project:
        self._project = Project(self, owner, number)
        self._project.link_repository()
        return self._project

    @property
    def branch(self) -> Branch:
        return Branch(self, self.current_branch)

    def branch_named(self, name: str) -> Branch:
        return Branch(self, name)

    @property
    def branch(self) -> str:
        return self.current_branch

    @branch.setter
    def branch(self, name: str) -> None:
        self.current_branch = name

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
                raise GitConnectError(f"unknown branch {name}")
            self._branch = name
            return
        self._git( "checkout", name)

    @property
    def current_commit(self) -> str:
        if self._memory:
            return self._commit
        return self._git("rev-parse", "HEAD")

    def owner_repo(self) -> tuple[str, str]:
        if self._memory:
            return self._owner, self._repo_name
        raw = self._gh("repo", "view", "--json", "nameWithOwner")
        payload = json.loads(raw or "{}")
        name = payload.get("nameWithOwner", "")
        if "/" not in name:
            raise GhConnectError(
                f"Cannot resolve owner/repo for {self.root}. {_GH_DO_NOT_PROCEED}"
            )
        owner, repo = name.split("/", 1)
        return owner, repo

    def is_dirty(self, path: str | Path | None = None) -> bool:
        if self._memory:
            return self._dirty
        args = ["status", "--porcelain", "--untracked-files=normal"]
        if path is not None:
            args.extend(["--", self._rel(path)])
        return bool(self._git(*args))

    def set_dirty(self, dirty: bool = True) -> None:
        if not self._memory:
            raise RuntimeError("set_dirty is only supported on Repo.memory()")
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

    def commit(self, paths: list[str], message: str) -> str:
        if not paths:
            raise ValueError("commit requires at least one path")
        if self._memory:
            self._commits.append((list(paths), message))
            self._commit = f"commit-{len(self._commits)}"
            self._dirty = False
            return self._commit
        rels = [self._rel(path) for path in paths]
        self._git( "add", "--", *rels)
        staged = self._git( "diff", "--cached", "--name-only", "--", *rels)
        if not staged:
            return self.current_commit
        self._git( "commit", "-m", message, "--", *rels)
        return self.current_commit

    def push(self) -> None:
        if self._memory:
            self._pushes.append(self.current_branch)
            return
        self._git( "push", "-u", "origin", self.current_branch)

    def merge_branch(self, source: str, into: str = "main", message: str = "") -> str:
        if self.is_dirty():
            raise DirtyBranchSwitchError(self.current_branch, into)
        if self._memory:
            if source not in self._branch_names:
                self._branch_names.add(source)
            self._branch = into
            text = message or f"merge {source} into {into}"
            self._commits.append(([], text))
            self._commit = f"merge-{source}-into-{into}"
            return self._commit
        self._git( "checkout", into)
        if message:
            self._git( "merge", source, "-m", message)
        else:
            self._git( "merge", source, "--no-edit")
        return self.current_commit

    def note(
        self,
        sha: str,
        payload: dict[str, str],
        *,
        ref: str | None = None,
    ) -> None:
        note_ref = ref or self.NOTES_REF
        if self._memory:
            self._notes[sha] = dict(payload)
            return
        text = Commit.note_text(payload)
        self._git(
            "notes",
            f"--ref={note_ref}",
            "add",
            "-f",
            "-m",
            text,
            sha,
        )

    def read_notes(self, sha: str, *, ref: str | None = None) -> dict[str, str]:
        note_ref = ref or self.NOTES_REF
        if self._memory:
            return dict(self._notes.get(sha, {}))
        try:
            raw = self._git("notes", f"--ref={note_ref}", "show", sha)
        except GitConnectError:
            return {}
        return Commit.note_payload(raw)

    def find_mistakes(
        self, entry_ids: list[str], *, ref: str | None = None
    ) -> list[dict[str, str]]:
        note_ref = ref or self.NOTES_REF
        wanted = set(entry_ids)
        found: list[dict[str, str]] = []
        if self._memory:
            for sha, payload in self._notes.items():
                if payload.get("entry_id") in wanted:
                    row = dict(payload)
                    row.setdefault("introducing_commit", sha)
                    found.append(row)
            return found
        listing = self._git( "notes", f"--ref={note_ref}", "list")
        for line in listing.splitlines():
            parts = line.split()
            if len(parts) < 2:
                continue
            sha = parts[1]
            payload = self.read_notes(sha, ref=note_ref)
            if payload.get("entry_id") in wanted:
                payload.setdefault("introducing_commit", sha)
                found.append(payload)
        return found

    def ticket(self, ref: str) -> Ticket | None:
        if self._memory:
            number = Ticket.parse_number(ref)
            ticket = self._tickets.get(number)
            if ticket is None:
                return None
            ticket._repo = self
            state_name = self._ticket_project_state.get(number)
            if state_name:
                ticket.state = TicketState(state_name)
            ticket.data["closed"] = "true" if number in self._closed_tickets else "false"
            return ticket
        number = Ticket.parse_number(ref)
        try:
            raw = self._gh(
                "issue",
                "view",
                str(number),
                "--json",
                "number,title,body,url,state",
            )
        except GhConnectError as exc:
            message = str(exc).lower()
            if "could not resolve" in message or "not found" in message:
                return None
            raise
        payload = json.loads(raw or "{}")
        if not payload:
            return None
        return self._ticket_from_payload(payload)

    def create_ticket(self, title: str, body: str) -> Ticket:
        if self._memory:
            number = (max(self._tickets.keys(), default=0) + 1) if self._tickets else 1
            owner, repo_name = self.owner_repo()
            ticket = Ticket(
                number=number,
                title=title,
                body=body,
                url=f"https://github.com/{owner}/{repo_name}/issues/{number}",
                _repo=self,
            )
            self._tickets[number] = ticket
            return ticket
        raw = self._gh(
            "issue",
            "create",
            "--title",
            title,
            "--body-file",
            "-",
            stdin=body,
        )
        url = (raw or "").strip().splitlines()[-1].strip() if raw else ""
        if "/issues/" not in url:
            raise GhConnectError(
                f"Cannot parse issue URL from gh issue create: {raw!r}. {_GH_DO_NOT_PROCEED}"
            )
        number = int(url.rstrip("/").rsplit("/", 1)[-1])
        ticket = self.ticket(str(number))
        if ticket is None:
            return self._ticket_from_payload(
                {"number": number, "title": title, "body": body, "url": url}
            )
        ticket.body = body
        ticket.title = title
        return ticket

    def workflow_commit_message(
        self,
        subject: str,
        issue_number: int,
        workflow_state: str,
        *,
        reviewed_by: str = "",
    ) -> str:
        owner, repo = self.owner_repo()
        trailers = {
            "GitHub-Issue": Ticket.github_ref(owner, repo, issue_number),
            "Workflow-State": workflow_state,
        }
        if reviewed_by.strip():
            trailers["Reviewed-By"] = reviewed_by.strip()
        return Commit.format(subject, trailers)

    def _ticket_from_payload(self, payload: dict[str, Any]) -> Ticket:
        number = int(payload["number"])
        ticket = Ticket(
            number=number,
            title=str(payload.get("title") or ""),
            body=str(payload.get("body") or ""),
            url=str(payload.get("url") or ""),
            _repo=self,
        )
        self._tickets[number] = ticket
        return ticket

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

    # Legacy test surface (was NullGitRepo)
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


# Legacy names used by workspace and specs
GitRepo = Repo


@toolset
class Git:
    """Manifest entry for the git utility package."""

    pass
