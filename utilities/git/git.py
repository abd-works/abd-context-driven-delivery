# @toolset-manifest python -m tools manifest git.git:Git
"""Git + GitHub domain model — repo, branches, commits, project tickets."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from tools.tool import toolset

from git._cli import (
    _DirtyBranchSwitchError as DirtyBranchSwitchError,
    _GhConnectError as GhConnectError,
    _GitConnectError as GitConnectError,
    _TicketNotFoundError as TicketNotFoundError,
    _eval_mistakes_notes_ref as eval_mistakes_notes_ref,
    _gh_close_issue as gh_close_issue,
    _gh_create_issue as gh_create_issue,
    _gh_owner_repo as gh_owner_repo,
    _gh_set_project_status as gh_set_project_status,
    _gh_view_issue as gh_view_issue,
    _run_git as run_git,
)


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
        gh_close_issue(repo.root, self.number)
        self.data["closed"] = "true"

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

    @classmethod
    def create(cls, repo: Repo, title: str, body: str) -> Ticket:
        if repo._memory:
            number = (max(repo._tickets.keys(), default=0) + 1) if repo._tickets else 1
            owner, repo_name = repo.owner_repo()
            ticket = cls(
                number=number,
                title=title,
                body=body,
                url=f"https://github.com/{owner}/{repo_name}/issues/{number}",
                _repo=repo,
            )
            repo._tickets[number] = ticket
            return ticket
        payload = gh_create_issue(repo.root, title, body)
        return repo._ticket_from_payload(payload)


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

    def add_ticket(self, ticket: Ticket, state_name: str) -> Ticket:
        self._repo._set_ticket_project_state(ticket, state_name)
        ticket.state = self.state_named(state_name)
        return ticket

    def set_ticket_state(self, ticket: Ticket, state_name: str) -> Ticket:
        return self.add_ticket(ticket, state_name)


class Repo:
    """Local git clone with optional GitHub project + tickets."""

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

    def _init_memory_state(self) -> None:
        self._branch_names: set[str] = {"main"}
        self._branch = "main"
        self._commit = "sha-init"
        self._commits: list[tuple[list[str], str]] = []
        self._pushes: list[str] = []
        self._dirty = False
        self._notes: dict[str, dict[str, str]] = {}

    @property
    def project(self) -> Project | None:
        return self._project

    def attach_project(self, owner: str, number: int) -> Project:
        self._project = Project(self, owner, number)
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
        return run_git(self.root, "rev-parse", "--abbrev-ref", "HEAD")

    @current_branch.setter
    def current_branch(self, name: str) -> None:
        if self.is_dirty() and name != self.current_branch:
            raise DirtyBranchSwitchError(self.current_branch, name)
        if self._memory:
            if name not in self._branch_names:
                raise GitConnectError(f"unknown branch {name}")
            self._branch = name
            return
        run_git(self.root, "checkout", name)

    @property
    def current_commit(self) -> str:
        if self._memory:
            return self._commit
        return run_git(self.root, "rev-parse", "HEAD")

    def owner_repo(self) -> tuple[str, str]:
        if self._memory:
            return self._owner, self._repo_name
        return gh_owner_repo(self.root)

    def is_dirty(self, path: str | Path | None = None) -> bool:
        if self._memory:
            return self._dirty
        args = ["status", "--porcelain", "--untracked-files=normal"]
        if path is not None:
            args.extend(["--", self._rel(path)])
        return bool(run_git(self.root, *args))

    def set_dirty(self, dirty: bool = True) -> None:
        if not self._memory:
            raise RuntimeError("set_dirty is only supported on Repo.memory()")
        self._dirty = dirty

    def create_branch(self, name: str) -> None:
        if self._memory:
            self._branch_names.add(name)
            return
        run_git(self.root, "branch", name)

    def checkout_or_create(self, name: str) -> str:
        if self.current_branch == name:
            return name
        if self.is_dirty():
            raise DirtyBranchSwitchError(self.current_branch, name)
        if self._memory:
            self._branch_names.add(name)
            self._branch = name
            return name
        existing = run_git(self.root, "branch", "--list", name)
        if existing:
            run_git(self.root, "checkout", name)
        else:
            run_git(self.root, "checkout", "-b", name)
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
        run_git(self.root, "add", "--", *rels)
        staged = run_git(self.root, "diff", "--cached", "--name-only", "--", *rels)
        if not staged:
            return self.current_commit
        run_git(self.root, "commit", "-m", message, "--", *rels)
        return self.current_commit

    def push(self) -> None:
        if self._memory:
            self._pushes.append(self.current_branch)
            return
        run_git(self.root, "push", "-u", "origin", self.current_branch)

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
        run_git(self.root, "checkout", into)
        if message:
            run_git(self.root, "merge", source, "-m", message)
        else:
            run_git(self.root, "merge", source, "--no-edit")
        return self.current_commit

    def note(
        self,
        sha: str,
        payload: dict[str, str],
        *,
        ref: str | None = None,
    ) -> None:
        note_ref = ref or eval_mistakes_notes_ref()
        if self._memory:
            self._notes[sha] = dict(payload)
            return
        text = Commit.note_text(payload)
        run_git(
            self.root,
            "notes",
            f"--ref={note_ref}",
            "add",
            "-f",
            "-m",
            text,
            sha,
        )

    def read_notes(self, sha: str, *, ref: str | None = None) -> dict[str, str]:
        note_ref = ref or eval_mistakes_notes_ref()
        if self._memory:
            return dict(self._notes.get(sha, {}))
        try:
            raw = run_git(self.root, "notes", f"--ref={note_ref}", "show", sha)
        except GitConnectError:
            return {}
        return Commit.note_payload(raw)

    def find_mistakes(
        self, entry_ids: list[str], *, ref: str | None = None
    ) -> list[dict[str, str]]:
        note_ref = ref or eval_mistakes_notes_ref()
        wanted = set(entry_ids)
        found: list[dict[str, str]] = []
        if self._memory:
            for sha, payload in self._notes.items():
                if payload.get("entry_id") in wanted:
                    row = dict(payload)
                    row.setdefault("introducing_commit", sha)
                    found.append(row)
            return found
        listing = run_git(self.root, "notes", f"--ref={note_ref}", "list")
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
        payload = gh_view_issue(self.root, Ticket.parse_number(ref))
        if payload is None:
            return None
        return self._ticket_from_payload(payload)

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

    def _set_ticket_project_state(self, ticket: Ticket, state_name: str) -> None:
        if state_name not in DEFAULT_PROJECT_STATES:
            raise ValueError(f"status must be one of {DEFAULT_PROJECT_STATES}")
        if self._memory:
            self._ticket_project_state[ticket.number] = state_name
            ticket.state = TicketState(state_name)
            return
        if self._project is None:
            raise RuntimeError("attach_project before setting ticket state")
        gh_set_project_status(
            ticket.url,
            state_name,
            project_owner=self._project.owner,
            project_number=self._project.number,
        )
        ticket.state = TicketState(state_name)

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
        return run_git(self.root, "log", "-1", "--pretty=%B")

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
