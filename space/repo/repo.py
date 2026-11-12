"""Local repository domain model: the clone, its branches, and its commits; the worktrees beside it are in worktree.py."""

from __future__ import annotations

import threading
from functools import cached_property
from pathlib import Path

from harness.agent_tools import agent_instructions, agent_tool, agent_toolset
from harness.agent_tools.agent_tools import tool_subject
from harness.installation.data_class import data_field, language_adapter
from harness.installation.files import command
from harness.mcp.mcp_server import long_call, mcp
from harness.process.git import Git, RepoConnectError
from space.repo.git_folder import GitFolder
from space.repo.worktree import Worktree, Worktrees

# A file git reports as changed that is the hook server's running log, not work: it never blocks a switch or a close.
_RUNTIME_LOG = "events.log"
# The session files every branch only appends to, which a merge keeps both sides of.
_UNION_MERGED_LOGS = (".sessions/**/session.log merge=union", ".sessions/**/session.err merge=union")





class CommitPathsRequiredError(ValueError):
    """Raised when a commit is asked for with no path to commit, which would otherwise commit nothing or everything."""

    def __init__(self) -> None:
        super().__init__("commit requires at least one path")


class CommitMessageRequiredError(ValueError):
    """Raised when push-commit is called with an empty message, since git refuses a commit without one."""

    def __init__(self) -> None:
        super().__init__("commit message is required")



class Commit:
    """One git commit. Its data is its sha, subject, full message, and the trailers the message carries, which is what
    an MCP tool that makes a commit answers with."""

    def __init__(self, sha: str, message: str) -> None:
        self._sha = sha
        self._message = message

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
    def trailers(self) -> dict[str, str]:
        """The trailers: each ``Key: value`` line after the subject."""
        trailers = [line.split(": ", 1) for line in (self.message or "").splitlines()[1:] if ": " in line]
        return {key.strip(): value.strip() for key, value in trailers}


@language_adapter(language="typescript")
@agent_toolset
class Repo:
    """Local git clone: its branches and its commits. The checkouts beside it are its ``worktrees``."""

    def __init__(self, root: str | Path = ".") -> None:
        self.root = Path(root).resolve()
        self.default_branch = "main"
        # The git command line, run in this clone.
        self.git = Git(self.root)
        # The checkouts of this repository: the main clone and the linked worktrees beside it.
        self.worktrees = Worktrees(self)

    @classmethod
    @tool_subject
    def of_project(cls, project: Path) -> Repo:
        """The clone holding project, the project a tool call names, as this process holds it. One cdd server answers
        every chat, so each call is handed its project and acts on that project's clone, never on a clone named by an
        earlier call; every call and every session of that checkout works on the one Repo held for it, which holds the
        one WorkState of its the chat's open state under ``~/.cdd``."""
        folder = Path(project).resolve()
        return SERVED_CHECKOUTS.at(cls._marked_checkout(folder) or folder)

    @staticmethod
    def _marked_checkout(folder: Path) -> Path | None:
        """The nearest folder at or above folder that git marks as a checkout's top; none when no folder is marked."""
        current = folder.parent if folder.is_file() else folder
        return next((candidate for candidate in (current, *current.parents) if (candidate / ".git").exists()), None)

    def find_root(self) -> Path | None:
        return self._marked_checkout(self.root)

    def checkout_at(self, folder: Path | str) -> Repo:
        """The repository as checked out at folder, another checkout of this one, such as a linked worktree beside it,
        as this process holds it."""
        return SERVED_CHECKOUTS.at(Path(folder).resolve())

    @property
    def is_clone(self) -> bool:
        """Whether git works here: a .git folder holding a HEAD, or the .git file of a linked worktree. A .git folder with
        nothing in it only marks a project's root."""
        root = self.find_root()
        if root is None:
            return False
        marker = root / ".git"
        return marker.is_file() or (marker / "HEAD").is_file()

    @property
    def checkout_folder(self) -> Path:
        """The checkout holding this folder; the folder itself when it is in none."""
        return self.find_root() or self.root

    def is_linked_worktree(self) -> bool:
        return (self.root / ".git").is_file()

    def primary_root(self) -> Path:
        """The repository's main checkout. A linked worktree's ``.git`` is a file naming its git folder, whose
        ``commondir`` leads back to the main checkout's ``.git``; any other checkout is its own main checkout."""
        checkout = self.checkout_folder
        marker = checkout / ".git"
        if not marker.is_file():
            return checkout
        worktree_git = (checkout / marker.read_text(encoding="utf-8").split("gitdir:", 1)[-1].strip()).resolve()
        common = worktree_git / "commondir"
        if not common.is_file():
            return checkout
        return (worktree_git / common.read_text(encoding="utf-8").strip()).resolve().parent

    def path_from_top(self, path: Path | str) -> str:
        """path as written from the repository's top, empty for the top itself, or as it is when it lies outside the
        repository, where a session may work."""
        given = Path(path)
        if not given.is_relative_to(self.root):
            return given.as_posix()
        relative = given.relative_to(self.root).as_posix()
        return "" if relative == "." else relative

    def branch_named(self, name: str) -> Branch:
        return Branch(self, name)

    @property
    def branches(self) -> list[Branch]:
        """Every local branch of this repository; none for a project that is no clone."""
        if not self.is_clone:
            return []
        folder = self._readable_folder
        names = folder.branch_names() if folder is not None else self.git.run("for-each-ref", "--format=%(refname:short)", "refs/heads").splitlines()
        return [self.branch_named(name) for name in names if name.strip()]

    @property
    def current_branch(self) -> Branch:
        """The branch this checkout has checked out."""
        folder = self._readable_folder
        return self.branch_named(folder.head_branch() if folder is not None else self.git.run("rev-parse", "--abbrev-ref", "HEAD"))

    @property
    def is_on_branch(self) -> bool:
        """Whether HEAD names a branch rather than being detached at a commit."""
        folder = self._readable_folder
        return folder.is_on_branch() if folder is not None else self.git.succeeds("symbolic-ref", "-q", "HEAD")

    @property
    def current_commit(self) -> str:
        folder = self._readable_folder
        read = folder.head_commit() if folder is not None else ""
        return read or self.git.run("rev-parse", "HEAD")

    @property
    def default_start_point(self) -> str:
        """Where a branch origin has never seen starts: origin's default branch, else the local default branch."""
        candidates = (f"origin/{self.default_branch}", "origin/main", "origin/master")
        return next((candidate for candidate in candidates if self.has_ref(f"refs/remotes/{candidate}")), self.default_branch)

    def has_ref(self, ref: str) -> bool:
        folder = self._readable_folder
        return folder.has_ref(ref) if folder is not None else self.git.succeeds("show-ref", "--verify", "--quiet", ref)

    def worktree_listing(self) -> list[tuple[Path, str]]:
        """Every checkout of the repository with the branch it has checked out (empty when none is), the main clone
        first, as git lists them; read from the .git folder where it can be."""
        folder = self._readable_folder
        if folder is not None:
            return folder.worktrees()
        listed = []
        for block in self.git.run("worktree", "list", "--porcelain").split("\n\n"):
            fields = dict(line.split(" ", 1) for line in block.splitlines() if " " in line)
            if "worktree" in fields:
                listed.append((Path(fields["worktree"]), fields.get("branch", "").removeprefix("refs/heads/")))
        return listed

    @property
    def _readable_folder(self) -> GitFolder | None:
        """The checkout's .git, read from its files, so a lookup asked many times in one board read starts no git;
        none where only git reads it, such as a project that is no clone or one whose refs are kept in a reftable."""
        folder = GitFolder(self.checkout_folder)
        return folder if folder.is_readable else None

    def is_dirty(self, path: str | Path | None = None, *, untracked: bool = True) -> bool:
        """Whether the working tree, or path in it, has changes other than the hook server's running log."""
        args = ["status", "--porcelain", "--untracked-files=normal" if untracked else "--untracked-files=no"]
        if path is not None:
            args.extend(["--", self._relative(path)])
        return any(not self._is_runtime_log(line) for line in self.git.run(*args).splitlines() if line.strip())

    def _is_runtime_log(self, porcelain_line: str) -> bool:
        raw = porcelain_line[3:] if len(porcelain_line) >= 3 else porcelain_line
        name = raw.split(" -> ")[-1].replace("\\", "/").strip()
        return Path(name).name == _RUNTIME_LOG

    @property
    def is_merging(self) -> bool:
        """Whether a merge is in progress in this checkout, so the next commit would conclude it with everything staged."""
        return (self.root / ".git" / "MERGE_HEAD").is_file()

    def commit(self, paths: list[str], message: str, *, untracked: bool = False) -> str:
        """Commit the changes under paths with message, and with untracked also the new files there; the sha of HEAD
        afterwards, which is unchanged when there was nothing to commit. A merge in progress commits everything."""
        if not paths:
            raise CommitPathsRequiredError()
        add_flag = "-A" if untracked else "-u"
        named = [] if self.is_merging else ["--", *(self._relative(path) for path in paths)]
        self.git.run("add", add_flag, *named)
        if not self.git.run("diff", "--cached", "--name-only", *named):
            return self.current_commit
        self.git.run("commit", "-m", message, *named)
        return self.current_commit

    @property
    def has_origin(self) -> bool:
        """Whether this clone has a remote called origin to push to."""
        folder = self._readable_folder
        return folder.has_remote("origin") if folder is not None else self.git.succeeds("remote", "get-url", "origin")

    def push_upstream(self) -> None:
        """Push the current branch to origin; when origin refuses because it has commits this branch lacks, merge them
        in and push again, so a push never fails because work was pushed to the branch from elsewhere. Most pushes go
        through at once, so origin is fetched only when it refuses."""
        branch = self.current_branch.name
        try:
            self.git.run("push", "-u", "origin", branch)
        except RepoConnectError:
            self.catch_up_with_origin()
            self.git.run("push", "-u", "origin", branch)

    def catch_up_with_origin(self) -> None:
        """Merge origin's copy of the current branch into it when origin has commits this branch lacks; nothing when
        origin has no copy yet or this branch already holds every commit of it."""
        branch = self.current_branch.name
        self.fetch()
        tracked = f"origin/{branch}"
        if not self.has_ref(f"refs/remotes/{tracked}") or self.git.succeeds("merge-base", "--is-ancestor", tracked, "HEAD"):
            return
        self._merge(tracked, "")

    def needs_push(self) -> bool:
        """True when origin has no copy of the current branch yet or the branch is ahead of it. A git failure is raised,
        not read as nothing to push, so a close never reports a branch pushed that was not."""
        branch = self.current_branch.name
        if not self.has_ref(f"refs/remotes/origin/{branch}"):
            return True
        return int(self.git.run("rev-list", f"origin/{branch}..HEAD", "--count") or "0") > 0

    def fetch(self) -> None:
        self.git.run("fetch", "origin")

    def merge_from(self, other: Branch, message: str = "") -> str:
        """Merge other into the current branch without checking other out."""
        if other == self.current_branch:
            return self.current_commit
        self._merge(other.name, message)
        return self.current_commit

    def _merge(self, ref: str, message: str) -> None:
        """Merge ref into the current branch. Every branch appends to the same session logs, so those merge by keeping
        the lines of both sides instead of stopping the merge on a conflict."""
        self.prepare_merges()
        try:
            self.git.run("merge", ref, *(["-m", message] if message else ["--no-edit"]))
        except RepoConnectError:
            # A merge left half done blocks every later checkout and commit, so the checkout goes back as it was.
            self.git.succeeds("merge", "--abort")
            raise

    def prepare_merges(self) -> None:
        """Tell git, in this repository's own attributes file, which no checkout commits, to merge session logs by
        union: each line either side wrote is kept."""
        common = Path(self.git.run("rev-parse", "--git-common-dir"))
        attributes = (common if common.is_absolute() else self.root / common) / "info" / "attributes"
        written = attributes.read_text(encoding="utf-8") if attributes.is_file() else ""
        missing = [line for line in _UNION_MERGED_LOGS if line not in written.splitlines()]
        if not missing:
            return
        attributes.parent.mkdir(parents=True, exist_ok=True)
        lead = "" if not written or written.endswith("\n") else "\n"
        attributes.write_text(written + lead + "".join(f"{line}\n" for line in missing), encoding="utf-8")

    def _relative(self, path: str | Path) -> str:
        resolved = Path(path).resolve()
        return (resolved.relative_to(self.root) if resolved.is_relative_to(self.root) else resolved).as_posix()

    @cached_property
    def main_clone(self) -> Repo:
        """The repository's main checkout, found once: this clone unless it is a linked worktree. Branch commands act
        there, never inside a linked worktree. A folder in no repository is its own main clone, which keeps the sessions
        of a project that is no clone; a branch command there fails the way git does."""
        primary = self.primary_root()
        return self if primary == self.root else self.checkout_at(primary)

    @long_call
    @agent_tool
    @mcp
    def push_commit(
        self,
        message: str,
        *,
        untracked: bool = True,
        sync_remote: bool = True,
    ) -> Commit:
        """Commit this checkout's working tree using ``message`` (subject and optional body), and push its branch: the
        checkout of the project the call names, which is the folder the calling chat works in, such as a ticket's own
        worktree."""
        text = (message or "").strip()
        if not text:
            raise CommitMessageRequiredError()
        sha = self.commit([str(self.root)], text, untracked=untracked)
        if sync_remote:
            self.push_upstream()
        return Commit(sha, text)

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


class Branch:
    """Named branch on a *Repo*: checkout, commit, merge, and delete."""

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
        return self._repo.has_ref(f"refs/heads/{self.name}")

    @property
    @data_field
    def is_checked_out(self) -> bool:
        """Whether the repository has this branch checked out; a commit lands on whatever is checked out."""
        return self.exists and self._repo.current_branch == self

    @property
    def is_default(self) -> bool:
        return self.name == self._repo.default_branch

    @property
    def worktree(self) -> Worktree | None:
        """The checkout that has this branch checked out; none when no worktree has it."""
        return self._repo.worktrees.of(self)

    @property
    def start_point(self) -> str:
        """Where a new copy of this branch starts: origin's copy, else origin's default branch, else the local default."""
        if self._repo.has_ref(f"refs/remotes/origin/{self.name}"):
            return f"origin/{self.name}"
        return self._repo.default_start_point

    def changed_files(self) -> list[str]:
        """Paths from the repository root that this branch changed since it left the default branch, with uncommitted
        changes when it is checked out; none for a branch the repository does not have."""
        if not self.exists:
            return []
        git = self._repo.git
        committed = git.run("diff", "--name-only", f"{self._repo.default_branch}...{self.name}").splitlines()
        if self._repo.current_branch != self:
            return committed
        uncommitted = git.run("status", "--porcelain", "--untracked-files=all", "--no-renames").splitlines()
        return [*committed, *(line[3:].strip('"') for line in uncommitted)]

    def check_out(self) -> Branch:
        """Check this branch out in its clone; a branch the clone does not have starts from ``start_point``. Changes
        not committed go along and are merged into the branch checked out, so a session log every tool call appends to
        never stops a switch; its lines merge by union."""
        self._repo.prepare_merges()
        if self.exists:
            self._repo.git.run("checkout", "-m", self.name)
        else:
            self._repo.git.run("checkout", "-m", "-b", self.name, self.start_point)
        return self

    def switch_to(self) -> Branch:
        """Check this branch out in its clone. Nothing is committed: a switch moves between branches and leaves the
        work as it is, and git refuses the checkout when uncommitted work would be overwritten."""
        if self._repo.current_branch != self:
            self.check_out()
        return self

    def open_in_worktree(self) -> Worktree:
        """Check out this branch in a sibling worktree and return that worktree."""
        return self._repo.worktrees.open(self)

    def save(self, commit_message: str) -> None:
        """Commit every change on this checked-out branch, then push it when origin is behind.

        The default branch is committed locally but never pushed here; closing a branch pushes it.
        """
        repository = self._repo
        if repository.is_dirty():
            repository.commit([str(repository.root)], commit_message, untracked=True)
        if not self.is_default and repository.needs_push():
            repository.push_upstream()

    def land_on_default(self) -> None:
        """Merge this branch into the default branch in the main clone and push the default branch. A linked worktree
        cannot check the default branch out while the main clone has it, and may be gone by now, so the main clone does
        the merge whichever checkout this branch was found from."""
        repository = self._repo.main_clone
        default = repository.default_branch
        repository.branch_named(default).check_out()
        repository.catch_up_with_origin()
        repository.merge_from(self, message=f"merge {self.name} into {default}")
        repository.push_upstream()

    def delete(self, unmerged: bool = False) -> None:
        """Delete this branch here and on origin. git refuses a branch not merged into the default branch unless
        unmerged says the person chose to delete it as it is. The main clone deletes it, since a linked worktree this
        branch was found from may be removed already."""
        repository = self._repo.main_clone
        repository.git.run("branch", "-D" if unmerged else "-d", self.name)
        if repository.has_ref(f"refs/remotes/origin/{self.name}"):
            repository.git.run("push", "origin", "--delete", self.name)



class ServedCheckouts:
    """The repository of every checkout this process works in, each made once and held while it runs, so every tool
    call and every session of one checkout work on the same Repo, and two objects never read and write one
    the chat's open state under ``~/.cdd``."""

    def __init__(self) -> None:
        self._at: dict[Path, Repo] = {}
        self._lock = threading.Lock()

    def at(self, root: Path) -> Repo:
        """The repository checked out at root, made the first time this process works in it."""
        with self._lock:
            held = self._at.get(root)
            if held is None:
                held = self._at[root] = Repo(root)
            return held


# The checkouts this process works in, held for as long as it runs.
SERVED_CHECKOUTS = ServedCheckouts()
