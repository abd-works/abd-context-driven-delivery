"""Local repository domain model: the clone, its branches, and its commits; the worktrees beside it are in worktree.py."""

from __future__ import annotations

import logging
import threading
from functools import cached_property
from pathlib import Path

from harness.agent_tools import agent_instructions, agent_tool, agent_toolset
from harness.agent_tools.agent_tools import tool_subject
from harness.installation.data_class import data_field, language_adapter
from harness.installation.files import command
from harness.mcp.mcp_annotations import long_call, mcp
from harness.git.checkout import Checkout
from harness.git.git import Git, RepoConnectError
from space.repo.origin import Merges, Origin
from space.repo.worktree import Worktrees
from space.repo.new_repository import NewRepository

logger = logging.getLogger(__name__)

# A file git reports as changed that is the hook server's running log, not work: it never blocks a switch or a close.
_RUNTIME_LOG = "events.log"
# The names a default branch goes by, the newer first: a repository made before git named its first branch main has master.
_DEFAULT_BRANCH_NAMES = ("main", "master")





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
        # The checkout holding root, which answers what its git holds.
        self.checkout = Checkout.holding(self.root)
        # The git command line, run in this clone.
        self.git = Git(self.root)
        # The checkouts of this repository: the main clone and the linked worktrees beside it, each held where this
        # process holds every checkout's repository.
        self.worktrees = Worktrees(self, SERVED_CHECKOUTS)
        # Its refs, and its working tree: what it has not committed yet, and committing it.
        self.refs = Refs(self)
        self.working_tree = WorkingTree(self)
        # What it exchanges with origin, and how it merges a branch in.
        self.origin = Origin(self)
        self.merges = Merges(self)
        # How its work is published: committed and pushed on its branch, or taken to main.
        self.publishing = Publishing(self)
        # Each path already written from the top. The board names every session file this way thousands of times a
        # refresh, and the answer depends only on the path and this repository's root, which never changes.
        self._from_top: dict[Path, str] = {}
        # The default branch once the refs name it; read again until then.
        self._default_branch: str | None = None
        # Held while git writes this checkout's index: a commit, a merge, a checkout. The board's saves commit on main
        # from a thread of their own while a tool call commits or merges in the same folder, and two at once fail on
        # git's index.lock. This process holds one Repo per checkout, so the one lock covers every writer in it.
        self.writing_index = threading.RLock()

    @classmethod
    @tool_subject
    def of_project(cls, project: Path) -> Repo:
        """The clone holding project, the project a tool call names, as this process holds it. One cdd server answers
        every chat, so each call is handed its project and acts on that project's clone, never on a clone named by an
        earlier call; every call and every session of that checkout works on the one Repo held for it, which holds the
        one WorkState of its the chat's open state under ``~/.cdd``."""
        return SERVED_CHECKOUTS.at(Checkout.holding(project).folder)

    @property
    def is_clone(self) -> bool:
        """Whether git works here: a .git folder holding a HEAD, or the .git file of a linked worktree. A .git folder with
        nothing in it only marks a project's root."""
        return self.checkout.is_clone

    @property
    def checkout_folder(self) -> Path:
        """The checkout holding this folder; the folder itself when it is in none."""
        return self.checkout.folder

    @property
    def is_linked_worktree(self) -> bool:
        """Whether this checkout is a linked worktree beside the main clone, whose .git is a file naming its git folder."""
        return self.checkout.is_linked_worktree

    def path_from_top(self, path: Path | str) -> str:
        """path as written from the repository's top, empty for the top itself, or as it is when it lies outside the
        repository, where a session may work."""
        given = Path(path)
        if given not in self._from_top:
            self._from_top[given] = self._written_from_top(given)
        return self._from_top[given]

    def _written_from_top(self, given: Path) -> str:
        if not given.is_relative_to(self.root):
            return given.as_posix()
        relative = given.relative_to(self.root).as_posix()
        return "" if relative == "." else relative

    def branch_named(self, name: str) -> Branch:
        return Branch(self, name)

    @property
    def branches(self) -> list[Branch]:
        """Every local branch of this repository; none for a project that is no clone."""
        return [self.branch_named(name) for name in self.checkout.facts.branch_names()]

    @property
    def current_branch(self) -> Branch:
        """The branch this checkout has checked out."""
        return self.branch_named(self.checkout.facts.head_branch())

    @property
    def is_on_branch(self) -> bool:
        """Whether HEAD names a branch rather than being detached at a commit."""
        return self.checkout.facts.is_on_branch()

    @property
    def current_commit(self) -> str:
        return self.checkout.facts.head_commit() or self.git.run("rev-parse", "HEAD")

    @property
    def default_branch(self) -> Branch:
        """The repository's default branch: the branch origin's HEAD names, else main or master, whichever the clone or
        origin has. A repository made before git named its first branch main keeps master, and a merge or push to its
        default branch must land there, not on a new main. A repository git init made has no branch yet, so its default
        is the branch HEAD names, which its first commit makes; a folder git does not hold has main. Only a branch read
        from the refs is kept, so a folder made a repository, or given its first commit, is read again."""
        if self._default_branch is None:
            found = self._default_branch_in_refs()
            if not found:
                return self.branch_named(self._unborn_branch() or _DEFAULT_BRANCH_NAMES[0])
            self._default_branch = found
        return self.branch_named(self._default_branch)

    def _unborn_branch(self) -> str:
        """The branch HEAD names in a clone with no commit on it yet; empty anywhere else."""
        if not self.is_clone or not self.is_on_branch:
            return ""
        return self.current_branch.name

    def _default_branch_in_refs(self) -> str:
        """The default branch as the refs name it; empty when no ref names one."""
        if not self.is_clone:
            return ""
        try:
            named = self.git.run("symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD")
        except RepoConnectError:
            named = ""
        if named.startswith("origin/"):
            return named.removeprefix("origin/")
        candidates = [f"{place}{name}" for place in ("refs/heads/", "refs/remotes/origin/") for name in _DEFAULT_BRANCH_NAMES]
        found = next((ref for ref in candidates if self.refs.has(ref)), "")
        return found.rsplit("/", 1)[-1] if found else ""

    @property
    def default_start_point(self) -> str:
        """Where a branch origin has never seen starts: origin's default branch, else the local default branch."""
        candidates = (f"origin/{self.default_branch.name}", "origin/main", "origin/master")
        return next((candidate for candidate in candidates if self.refs.has(f"refs/remotes/{candidate}")), self.default_branch.name)

    @property
    def has_origin(self) -> bool:
        """Whether this clone has a remote called origin to push to."""
        return self.checkout.facts.has_remote("origin")

    @property
    def head_message(self) -> str:
        """The message of the commit the checked-out branch is on."""
        return self.git.run("log", "-1", "--format=%B")

    @property
    def is_main_clone(self) -> bool:
        """Whether this checkout is the repository's main clone, not a linked worktree beside it."""
        return self.checkout.is_main

    def catch_up_with_origin(self, fetched: bool = False) -> None:
        """Bring this checkout up to date with origin: fetch it and merge its copy of the branch in, or, when the
        repository has just fetched, merge what it fetched. A checkout that cannot reach origin, or whose branch has
        moved apart from origin's, stays as it is, and the log says why."""
        try:
            self.origin.merge_copy() if fetched else self.origin.catch_up()
        except RepoConnectError as exc:
            logger.warning("checkout %s is not up to date with origin: %s", self.root, exc)

    def close(self, commit_message: str) -> Branch:
        """Save the branch checked out here, committed and pushed, then remove this checkout, a linked worktree; the
        branch stays open."""
        branch = self.current_branch
        branch.save(commit_message)
        self.worktrees.remove(self)
        return branch

    @cached_property
    def main_clone(self) -> Repo:
        """The repository's main checkout, found once: this clone unless it is a linked worktree. Branch commands act
        there, never inside a linked worktree. A folder in no repository is its own main clone, which keeps the sessions
        of a project that is no clone; a branch command there fails the way git does."""
        return self.worktrees.repository_at(self.worktrees.primary_root())

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
        return self.publishing.push_commit(message, untracked=untracked, sync_remote=sync_remote)

    @long_call
    @agent_tool
    @mcp
    def push_work(self) -> Commit:
        """Commit this checkout's work on its branch and push the branch, nothing merged: the chat bar's push. The
        checkout is the one of the project the call names, the folder the calling chat works in. Answer the commit the
        branch is on."""
        return self.publishing.push_work()

    @long_call
    @agent_tool
    @mcp
    def merge_to_main(self) -> Commit:
        """Commit this checkout's work on its branch, then merge that branch into main in the main clone, which goes back
        to the branch it had; nothing is pushed. The checkout is the one of the project the call names, the folder the
        calling chat works in, such as a session's own worktree. Answer the commit main is on."""
        return self.publishing.take_work_to_main(push=False)

    @long_call
    @agent_tool
    @mcp
    def push_to_main(self) -> Commit:
        """Commit this checkout's work on its branch and push the branch, merge it into main in the main clone, and push
        main, so origin's main holds the work; the main clone goes back to the branch it had. Answer the commit main is
        on."""
        return self.publishing.take_work_to_main(push=True)

    @long_call
    @agent_tool
    @mcp
    def make_repository(self) -> str:
        """Make the project, a plain folder, a git repository on main with a first commit of its files, so its tickets get
        branches, worktrees and chats of their own: the chat bar offers it in a session whose project is no repository.
        Its .gitignore first takes what CDD writes into a project (``CDD_WRITTEN_PATTERNS``) and nothing else. A repository already there is left as it is. Answer what
        was done."""
        return NewRepository(self).make_from_folder().sentence

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


class Refs:
    """*Refs* are the refs of one checkout's repository, as its checkout's git facts answer them: read from its .git
    files where they can be, so a lookup asked many times in one board read starts no git, else asked of git."""

    def __init__(self, repo: Repo) -> None:
        self._repo = repo

    def has(self, ref: str) -> bool:
        """Whether the repository has ref, such as ``refs/heads/main``; a folder git does not know has none."""
        return self._repo.checkout.facts.has_ref(ref)


class WorkingTree:
    """*WorkingTree* is one checkout's work not committed yet: whether there is any, whether a merge is under way, and
    committing it. It writes git's index while the *Repo*'s ``writing_index`` is held, so two writers never meet."""

    def __init__(self, repo: Repo) -> None:
        self._repo = repo

    def is_dirty(self, path: str | Path | None = None, *, untracked: bool = True) -> bool:
        """Whether the working tree, or path in it, has changes other than the hook server's running log."""
        args = ["status", "--porcelain", "--untracked-files=normal" if untracked else "--untracked-files=no"]
        if path is not None:
            args.extend(["--", self._relative(path)])
        return any(not self._is_runtime_log(line) for line in self._repo.git.run(*args).splitlines() if line.strip())

    def uncommitted(self, under: Path | None = None) -> list[str]:
        """The files in this checkout, or under a folder of it, that are changed, added, or deleted and not committed,
        as paths from the checkout's top; new files are listed one by one, and the files .gitignore names are not."""
        args = ["status", "--porcelain", "--untracked-files=all", "--no-renames"]
        if under is not None:
            args.extend(["--", self._relative(under)])
        # A status entry is two status letters, a space, and the path.
        return [entry[3:] for entry in self._repo.git.listed(*args)]

    def _is_runtime_log(self, porcelain_line: str) -> bool:
        raw = porcelain_line[3:] if len(porcelain_line) >= 3 else porcelain_line
        name = raw.split(" -> ")[-1].replace("\\", "/").strip()
        return Path(name).name == _RUNTIME_LOG

    @property
    def is_merging(self) -> bool:
        """Whether a merge is in progress in this checkout, so the next commit would conclude it with everything staged."""
        return (self._repo.root / ".git" / "MERGE_HEAD").is_file()

    def commit(self, paths: list[str], message: str, *, untracked: bool = False) -> str:
        """Commit the changes under paths with message, and with untracked also the new files there; the sha of HEAD
        afterwards, which is unchanged when there was nothing to commit. A merge in progress commits everything."""
        if not paths:
            raise CommitPathsRequiredError()
        add_flag = "-A" if untracked else "-u"
        with self._repo.writing_index:
            named = [] if self.is_merging else ["--", *(self._relative(path) for path in paths)]
            self._repo.git.run("add", add_flag, *named)
            if not self._repo.git.run("diff", "--cached", "--name-only", *named):
                return self._repo.current_commit
            self._repo.git.run("commit", "-m", message, *named)
            return self._repo.current_commit

    def commit_all(self, message: str) -> str:
        """Commit everything in this checkout with message, new files included; the sha of HEAD afterwards."""
        return self.commit([str(self._repo.root)], message, untracked=True)

    def _relative(self, path: str | Path) -> str:
        resolved = Path(path).resolve()
        return (resolved.relative_to(self._repo.root) if resolved.is_relative_to(self._repo.root) else resolved).as_posix()


class Publishing:
    """*Publishing* is how one checkout's work leaves it: committed on its branch and pushed, or taken to main in the main
    clone, which goes back to the branch it had. The *Repo* answers what git holds; this runs the steps that publish it."""

    def __init__(self, repo: Repo) -> None:
        self._repo = repo

    def push_commit(self, message: str, *, untracked: bool, sync_remote: bool) -> Commit:
        """Commit the checkout's working tree with message, and push its branch when sync_remote."""
        text = (message or "").strip()
        if not text:
            raise CommitMessageRequiredError()
        repo = self._repo
        sha = repo.working_tree.commit([str(repo.root)], text, untracked=untracked)
        if sync_remote:
            repo.origin.push_upstream()
        return Commit(sha, text)

    def push_work(self) -> Commit:
        """Commit the checkout's work on its branch and push the branch, nothing merged."""
        repo = self._repo
        branch = repo.current_branch
        branch.save(f"{branch.name}: work pushed")
        return Commit(repo.current_commit, repo.head_message)

    def take_work_to_main(self, push: bool) -> Commit:
        """Commit the checkout's work on its branch, merge it into main in the main clone, pushing both when push, and
        bring the main clone back to the branch it had."""
        repo = self._repo
        branch = repo.current_branch
        repo.working_tree.commit_all(f"{branch.name}: work taken to main")
        if push and not branch.is_default and repo.has_origin:
            repo.origin.push_upstream()
        clone = repo.main_clone
        returning_to = clone.current_branch
        # The clone's own changes are its work too, such as the session's log, which this call has just written there; a
        # merge refuses to run over them.
        clone.working_tree.commit_all(f"{returning_to.name}: work kept before merging {branch.name}")
        branch.merge_into_default()
        if push and clone.has_origin:
            clone.origin.push_upstream()
        landed = Commit(clone.current_commit, clone.head_message)
        # Nothing is committed on the way back: git refuses the checkout when uncommitted work would be overwritten.
        if clone.current_branch != returning_to:
            returning_to.check_out()
        return landed


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
        return self._repo.refs.has(f"refs/heads/{self.name}")

    @property
    @data_field
    def is_checked_out(self) -> bool:
        """Whether any checkout of the repository has this branch checked out: the main clone or a linked worktree."""
        return self.exists and self.checkout is not None

    @property
    def is_checked_out_here(self) -> bool:
        """Whether the checkout this branch was found from has it checked out; a commit there lands on it."""
        return self.exists and self._repo.current_branch == self

    @property
    def is_default(self) -> bool:
        return self == self._repo.default_branch

    @property
    def linked_worktree(self) -> Repo | None:
        """The linked worktree beside the main clone that has this branch checked out; none while the main clone itself
        has it, since git lists the main clone among its worktrees too. Asked from inside that worktree, the branch is
        checked out there, and the worktree is still its own."""
        checkout = self._repo.worktrees.of(self)
        return checkout if checkout is not None and not checkout.is_main_clone else None

    @property
    def start_point(self) -> str:
        """Where a new copy of this branch starts: origin's copy, else origin's default branch, else the local default."""
        if self._repo.refs.has(f"refs/remotes/origin/{self.name}"):
            return f"origin/{self.name}"
        return self._repo.default_start_point

    def changed_files(self) -> list[str]:
        """Paths from the repository root that this branch changed since it left the default branch, with uncommitted
        changes when it is checked out; none for a branch the repository does not have."""
        if not self.exists:
            return []
        git = self._repo.git
        committed = git.listed("diff", "--name-only", f"{self._repo.default_branch.name}...{self.name}")
        checkout = self.checkout
        if checkout is None:
            return committed
        return [*committed, *checkout.working_tree.uncommitted()]

    @property
    def checkout(self) -> Repo | None:
        """The checkout that has this branch checked out: this clone, or the linked worktree beside it, such as a
        ticket's; none when no checkout has it. Its root is where the branch's changed paths are."""
        if self._repo.current_branch == self:
            return self._repo
        return self._repo.worktrees.of(self)

    def check_out(self) -> Branch:
        """Check this branch out in its clone; a branch the clone does not have starts from ``start_point``. Changes
        not committed go along and are merged into the branch checked out, so a session log every tool call appends to
        never stops a switch; its lines merge by union."""
        self._repo.merges.keep_session_logs_by_union()
        with self._repo.writing_index:
            if self.exists:
                self._repo.git.run("checkout", "-m", self.name)
            else:
                self._repo.git.run("checkout", "-m", "-b", self.name, self.start_point)
        return self

    def open_in_worktree(self) -> Repo:
        """Check out this branch in a sibling worktree and return that worktree."""
        return self._repo.worktrees.open(self)

    def save(self, commit_message: str, push: bool = True) -> None:
        """Commit every change in the checkout that has this branch out, with commit_message, and, with push, push the
        branch when origin lacks some of it. A branch no checkout has holds no change to save."""
        checkout = self.checkout
        if checkout is None:
            return
        if checkout.working_tree.is_dirty():
            checkout.working_tree.commit_all(commit_message)
        if push:
            self.push()

    def push(self) -> None:
        """Push this branch's commits from the checkout that has it out, committing nothing, when origin lacks some of
        them. A branch no checkout has, or a checkout with no origin, has nothing to push."""
        checkout = self.checkout
        if checkout is not None and checkout.has_origin and checkout.origin.needs_push():
            checkout.origin.push_upstream()

    def land_on_default(self) -> None:
        """Merge this branch into the default branch in the main clone and push the default branch."""
        self.merge_into_default().origin.push_upstream()

    def merge_into_default(self) -> Repo:
        """Merge this branch into the default branch in the main clone, after origin's copy of it, and answer the main
        clone, left on the default branch. A linked worktree cannot check the default branch out while the main clone
        has it, and may be gone by now, so the main clone does the merge whichever checkout this branch was found from."""
        repository = self._repo.main_clone
        default = repository.default_branch
        default.check_out()
        repository.origin.catch_up()
        repository.merges.merge_from(self, message=f"merge {self.name} into {default.name}")
        return repository

    def delete(self, unmerged: bool = False) -> None:
        """Delete this branch here and on origin. git refuses a branch not merged into the default branch unless
        unmerged says the person chose to delete it as it is. The main clone deletes it, since a linked worktree this
        branch was found from may be removed already."""
        repository = self._repo.main_clone
        repository.git.run("branch", "-D" if unmerged else "-d", self.name)
        if repository.refs.has(f"refs/remotes/origin/{self.name}"):
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

    def serve(self, repo: Repo) -> Repo:
        """Hold repo as the repository of the checkout at its root from now on, such as a mocked one a spec works on, so
        every tool call and session of that checkout works on it."""
        with self._lock:
            self._at[repo.root] = repo
            return repo


# The checkouts this process works in, held for as long as it runs.
SERVED_CHECKOUTS = ServedCheckouts()
