"""NewRepository - a folder made a git repository on main with a first commit, ignoring what CDD writes into a project:
a new repository ``repos.open`` creates, or a plain folder a session already works in, made one with
``repo.make_repository``, so its tickets get branches, worktrees and chats of their own."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from space.repo.repo import Repo

DEFAULT_BRANCH = "main"
_GITIGNORE_HEADER = "# What CDD writes into a project and no repository keeps (written by CDD)"
# What CDD writes into a project it works in: each IDE's install, the per-machine MCP entry and install record, the hook
# daemon's files, and a session's working files. A new repository ignores these and nothing else, so no file of the
# person's own is left out of a commit because the CDD checkout happens to ignore a name like it.
CDD_WRITTEN_PATTERNS = (
    ".claude/",
    ".cursor/",
    ".kilo/",
    ".mcp.json",
    "**/.install-state.json",
    "**/.install-lock",
    ".hook-server/",
    ".context/prompt-log.txt",
    "**/.context/graph.json",
    ".sessions/session.json",
    ".sessions/main/session.json",
    ".sessions/main/session.log",
    ".sessions/main/validation-reports/",
    ".sessions/**/session.err",
    ".sessions/**/logs/dispatch.debug",
    ".sessions/**/chat-injections/",
    ".sessions/**/graph.json",
    ".sessions/**/progress-cache.json",
    ".sessions/**/e2e-test-results/",
)
_FIRST_COMMIT = "Initial commit"


class FolderIsAWorktreeError(ValueError):
    """Raised when the repository named is a linked worktree of another one: it is opened through its ticket, not as a
    repository of its own."""

    def __init__(self, folder: Path) -> None:
        super().__init__(f"{folder} is a linked worktree of another repository, not a repository of its own")
        self.folder = folder


class FolderInsideARepositoryError(ValueError):
    """Raised when the folder named lies inside another repository's checkout: a repository made there would nest in
    that one, which could then no longer commit the folder's files."""

    def __init__(self, folder: Path, repository: Path) -> None:
        super().__init__(f"{folder} is inside the repository at {repository}; CDD makes no repository inside another")
        self.folder = folder
        self.repository = repository


@dataclass(frozen=True)
class MadeRepository:
    """What making a folder a repository did: whether it was a repository already, the branch it is on (empty when on
    none), and how many lines its .gitignore was given for what CDD writes into a project."""

    root: Path
    was_there: bool
    branch: str
    ignored_lines: int = 0

    @property
    def sentence(self) -> str:
        """What was done, as the tool that made it tells the chat."""
        if not self.was_there:
            made = f"Created {self.root} on {self.branch} with a first commit."
        elif self.branch != DEFAULT_BRANCH:
            made = f"{self.root} is a repository already, on {self.branch or 'no branch'}; the new chat opens it as it is."
        else:
            made = f"{self.root} is a repository already, on {DEFAULT_BRANCH}."
        return f"{made} Its .gitignore ignores what CDD writes into a project ({self.ignored_lines} lines)." if self.ignored_lines else made


class NewRepository:
    """The checkout of repo, a folder made a git repository of its own on main."""

    def __init__(self, repo: Repo) -> None:
        self.repo = repo

    @property
    def root(self) -> Path:
        return self.repo.root

    def create(self) -> MadeRepository:
        """Make root, made first when missing, a repository on main with a README and a first commit of what it holds.
        A repository already there is left as it is; a linked worktree, or a folder inside another repository, is
        refused."""
        existing = self._existing()
        if existing is not None:
            return existing
        self._commit_first()
        return MadeRepository(self.root, was_there=False, branch=DEFAULT_BRANCH)

    def make_from_folder(self) -> MadeRepository:
        """Make the folder at root, made first when missing, a repository: its .gitignore takes what CDD writes into a
        project before the first commit, so that commit holds the folder's own files and not CDD's install or its
        sessions' working files. Refused, before anything is written, as create refuses."""
        existing = self._existing()
        if existing is not None:
            return existing
        added = self.write_ignores()
        self._commit_first()
        return MadeRepository(self.root, was_there=False, branch=DEFAULT_BRANCH, ignored_lines=added)

    def _existing(self) -> MadeRepository | None:
        """The repository root is already, or None for a folder in no repository; refused when root is a linked
        worktree or lies inside another repository's checkout, whose git would otherwise hold it."""
        checkout = self.repo.checkout
        if checkout.is_clone and checkout.folder != self.root:
            raise FolderInsideARepositoryError(self.root, checkout.folder)
        if checkout.is_linked_worktree:
            raise FolderIsAWorktreeError(self.root)
        if checkout.is_clone:
            return MadeRepository(self.root, was_there=True, branch=checkout.branch)
        return None

    def _commit_first(self) -> None:
        """git init root on main, with a README when it has none, and commit everything it holds."""
        self.root.mkdir(parents=True, exist_ok=True)
        self.repo.git.run("init", "-b", DEFAULT_BRANCH)
        readme = self.root / "README.md"
        if not readme.exists():
            readme.write_text(f"# {self.root.name}\n", encoding="utf-8")
        self.repo.git.run("add", "-A")
        self.repo.git.run("commit", "-m", _FIRST_COMMIT)

    def ignore_as_cdd_does(self) -> int:
        """Add to root's .gitignore each pattern for what CDD writes into a project that it lacks, and commit it; answer
        how many lines were added."""
        added = self.write_ignores()
        if added:
            self.repo.git.run("add", "--", ".gitignore")
            self.repo.git.run("commit", "-m", "Ignore what CDD writes into a project", "--", ".gitignore")
        return added

    def write_ignores(self) -> int:
        """Write into root's .gitignore each pattern for what CDD writes into a project that it lacks; answer how many
        were added, none when it ignores every one already."""
        self.root.mkdir(parents=True, exist_ok=True)
        target = self.root / ".gitignore"
        have = target.read_text(encoding="utf-8").splitlines() if target.is_file() else []
        present = {line.strip() for line in have}
        wanted = [pattern for pattern in CDD_WRITTEN_PATTERNS if pattern not in present]
        if not wanted:
            return 0
        target.write_text("\n".join([*have, *([""] if have else []), _GITIGNORE_HEADER, *wanted]) + "\n", encoding="utf-8")
        return len(wanted)
