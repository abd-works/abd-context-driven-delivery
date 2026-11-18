"""NewRepository - a folder made a git repository on main with a first commit, ignoring what the CDD checkout ignores:
a new repository ``repos.open`` creates, or a plain folder a session already works in, made one with
``repo.make_repository``, so its tickets get branches, worktrees and chats of their own."""

from __future__ import annotations

from pathlib import Path

from harness.git.git import Git

# The checkout serving these tools: its .gitignore is what a new repository ignores.
_CDD_CHECKOUT = Path(__file__).resolve().parents[2]
DEFAULT_BRANCH = "main"
_GITIGNORE_HEADER = "# Ignored as the CDD checkout ignores (written by repos.open)"
_FIRST_COMMIT = "Initial commit"


class FolderIsAWorktreeError(ValueError):
    """Raised when the repository named is a linked worktree of another one: it is opened through its ticket, not as a
    repository of its own."""

    def __init__(self, folder: Path) -> None:
        super().__init__(f"{folder} is a linked worktree of another repository, not a repository of its own")
        self.folder = folder


class NewRepository:
    """The folder at root, made a git repository of its own on main."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.git = Git(root)

    @property
    def is_repository(self) -> bool:
        """Whether root is a repository of its own already: its ``.git`` is a folder git holds a HEAD in."""
        return (self.root / ".git" / "HEAD").is_file()

    def create(self) -> str:
        """Make root, made first when missing, a repository on main with a README and a first commit of what it holds.
        A repository already there is left as it is; a linked worktree is refused."""
        if (self.root / ".git").is_file():
            raise FolderIsAWorktreeError(self.root)
        if self.is_repository:
            branch = self.git.run("branch", "--show-current")
            if branch != DEFAULT_BRANCH:
                return f"{self.root} is a repository already, on {branch or 'no branch'}; the new chat opens it as it is."
            return f"{self.root} is a repository already, on {DEFAULT_BRANCH}."
        self.root.mkdir(parents=True, exist_ok=True)
        self.git.run("init", "-b", DEFAULT_BRANCH)
        readme = self.root / "README.md"
        if not readme.exists():
            readme.write_text(f"# {self.root.name}\n", encoding="utf-8")
        self.git.run("add", "-A")
        self.git.run("commit", "-m", _FIRST_COMMIT)
        return f"Created {self.root} on {DEFAULT_BRANCH} with a first commit."

    def make_from_folder(self) -> str:
        """Make the plain folder at root a repository: its .gitignore takes what the CDD checkout ignores before the first
        commit, so that commit holds the folder's own files and not CDD's install or its sessions' working files."""
        if (self.root / ".git").is_file() or self.is_repository:
            return self.create()
        added = self.write_ignores()
        created = self.create()
        return f"{created} Its .gitignore took {added} lines from the CDD checkout's." if added else created

    def ignore_as_cdd_does(self) -> str:
        """Add to root's .gitignore every line of the CDD checkout's that it lacks, and commit it."""
        if not (_CDD_CHECKOUT / ".gitignore").is_file():
            return "The CDD checkout has no .gitignore to copy."
        added = self.write_ignores()
        if not added:
            return ".gitignore already ignores what the CDD checkout ignores."
        self.git.run("add", "--", ".gitignore")
        self.git.run("commit", "-m", "Ignore what the CDD checkout ignores", "--", ".gitignore")
        return f"Added {added} lines to .gitignore from the CDD checkout's, and committed them."

    def write_ignores(self) -> int:
        """Write into root's .gitignore every line of the CDD checkout's that it lacks; answer how many were added, none
        when it ignores every pattern already."""
        source = _CDD_CHECKOUT / ".gitignore"
        if not source.is_file():
            return 0
        target = self.root / ".gitignore"
        have = target.read_text(encoding="utf-8").splitlines() if target.is_file() else []
        present = {line.strip() for line in have}
        wanted = [line for line in source.read_text(encoding="utf-8").splitlines() if line.strip() and line.strip() not in present]
        if not [line for line in wanted if not line.lstrip().startswith("#")]:
            return 0
        target.write_text("\n".join([*have, *([""] if have else []), _GITIGNORE_HEADER, *wanted]) + "\n", encoding="utf-8")
        return len(wanted)
