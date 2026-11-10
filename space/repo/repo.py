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
from space.repo.latest_release import LatestRelease
from space.repo.worktree import Worktree, Worktrees
from harness.agent_tools.tool_call import ToolCall
from space.work_state import WorkState

# A file git reports as changed that is the hook server's running log, not work: it never blocks a switch or a close.
_RUNTIME_LOG = "events.log"
# The session files every branch only appends to, which a merge keeps both sides of.
_UNION_MERGED_LOGS = (".sessions/**/session.log merge=union", ".sessions/**/session.err merge=union")


class BranchNameRequiredError(ValueError):
    """Raised when a branch command has no name and none is saved in the chat's open state under ``~/.cdd``."""

    def __init__(self) -> None:
        super().__init__(
            "branch name is required: pass name, or switch to a branch first so "
            "it is saved as this chat's open branch"
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


class CommitPathsRequiredError(ValueError):
    """Raised when a commit is asked for with no path to commit, which would otherwise commit nothing or everything."""

    def __init__(self) -> None:
        super().__init__("commit requires at least one path")


class CommitMessageRequiredError(ValueError):
    """Raised when push-commit is called with an empty message, since git refuses a commit without one."""

    def __init__(self) -> None:
        super().__init__("commit message is required")


class NoOpenWorktreeError(RuntimeError):
    """Raised when close-worktree runs with no worktree saved in the chat's open state under ``~/.cdd``."""

    def __init__(self) -> None:
        super().__init__("no open worktree: this chat has no worktree open")


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
        names = self.git.run("for-each-ref", "--format=%(refname:short)", "refs/heads").splitlines()
        return [self.branch_named(name) for name in names if name.strip()]

    @property
    def current_branch(self) -> Branch:
        """The branch this checkout has checked out."""
        return self.branch_named(self.git.run("rev-parse", "--abbrev-ref", "HEAD"))

    @property
    def current_commit(self) -> str:
        return self.git.run("rev-parse", "HEAD")

    @property
    def default_start_point(self) -> str:
        """Where a branch origin has never seen starts: origin's default branch, else the local default branch."""
        candidates = (f"origin/{self.default_branch}", "origin/main", "origin/master")
        return next((candidate for candidate in candidates if self.git.succeeds("rev-parse", "--verify", candidate)), self.default_branch)

    def has_ref(self, ref: str) -> bool:
        return self.git.succeeds("show-ref", "--verify", "--quiet", ref)

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

    def commit(self, paths: list[str], message: str, *, untracked: bool = False) -> str:
        """Commit the changes under paths with message, and with untracked also the new files there; the sha of HEAD
        afterwards, which is unchanged when there was nothing to commit. A merge in progress commits everything."""
        if not paths:
            raise CommitPathsRequiredError()
        add_flag = "-A" if untracked else "-u"
        merging = (self.root / ".git" / "MERGE_HEAD").is_file()
        named = [] if merging else ["--", *(self._relative(path) for path in paths)]
        self.git.run("add", add_flag, *named)
        if not self.git.run("diff", "--cached", "--name-only", *named):
            return self.current_commit
        self.git.run("commit", "-m", message, *named)
        return self.current_commit

    @property
    def has_origin(self) -> bool:
        """Whether this clone has a remote called origin to push to."""
        return self.git.succeeds("remote", "get-url", "origin")

    def push_upstream(self) -> None:
        """Push the current branch to origin, first merging in what origin's copy has that this branch lacks, so a push
        never fails because work was pushed to the branch from elsewhere."""
        self.catch_up_with_origin()
        self.git.run("push", "-u", "origin", self.current_branch.name)

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

    @property
    def own_work_state(self) -> WorkState:
        """The branch, worktree, and session open for this checkout folder, kept under ``~/.cdd`` and never in the
        checkout: the entry of the chat whose call is being answered, else this folder's own."""
        call = ToolCall.answering()
        return WorkState(self.root, call.chat_id if call is not None else "")

    @property
    def work_state(self) -> WorkState:
        """The branch, worktree, and session open in the main clone for the calling chat; every checkout of the
        repository reads the main clone's ``own_work_state``."""
        return self.main_clone.own_work_state

    @property
    def open_worktree(self) -> Worktree | None:
        """The worktree saved as open, as the main clone's worktrees list it; none when none is saved or git no longer
        lists one there."""
        folder = self.work_state.worktree_folder
        return self.main_clone.worktrees.at(folder) if folder is not None else None

    def _checkout_tools_act_in(self) -> Repo:
        """The checkout the repo tools act in. In the main clone that is the open worktree while its folder exists, so
        the work goes where ``switch_worktree`` moved the branch; in a linked worktree, or with no worktree open, it is
        this checkout."""
        if self.is_linked_worktree():
            return self
        opened = self.open_worktree
        return opened.repository if opened is not None and opened.path.is_dir() else self.main_clone

    def _named_or_saved_branch(self, name: str) -> Branch:
        """The branch called name on the main clone, else the branch saved as open."""
        cleaned = (name or "").strip() or self.work_state.branch_name
        if not cleaned:
            raise BranchNameRequiredError()
        return self.main_clone.branch_named(cleaned)

    @long_call
    @agent_tool
    @mcp
    def switch_branch(self, name: str = "") -> str:
        """Switch the main clone to branch ``name``, creating it when missing.

        ``name`` defaults to ``branch`` in the chat's open state under ``~/.cdd``. Commits nothing: work
        left uncommitted goes along to ``name``, as git carries it, and git refuses the switch when it would
        overwrite that work. Checks out ``name`` (a new branch starts from origin's copy or the default
        branch) and saves ``name`` as ``branch`` in the chat's open state under ``~/.cdd``. Does not touch
        worktrees or sessions.
        """
        branch = self._named_or_saved_branch(name).switch_to()
        self.work_state.branch_name = branch.name
        return f"on branch {branch.name!r} at {branch.repo.root}"

    @long_call
    @agent_tool
    @mcp
    def close_branch(self, name: str = "", commit_message: str = "branch: close") -> str:
        """Close branch ``name``: commit, push, merge into the default branch, push it, delete ``name``.

        ``name`` defaults to ``branch`` in the chat's open state under ``~/.cdd``. Refuses the default branch and
        a branch still open in a worktree. Deletes ``name`` locally and on origin, leaves the main
        clone on the default branch, and saves the default branch as ``branch``. Does not touch sessions.
        The release that landed (the open session, else ``name``) keeps its end-to-end results, its
        screenshots pushed to ``e2e-latest``; every older release's results are removed and that removal is
        committed and pushed on the default branch.
        """
        branch = self._named_or_saved_branch(name)
        release = LatestRelease(branch.repo, self.work_state.session or branch.name)
        branch.close(commit_message)
        self.work_state.branch_name = branch.repo.default_branch
        pruned = release.keep()
        kept = f"; kept {release.release!r} end-to-end results, removed {', '.join(pruned)}" if pruned else ""
        return f"closed branch {branch.name!r}: merged into {branch.repo.default_branch!r}, pushed, and deleted{kept}"

    @long_call
    @agent_tool
    @mcp
    def switch_worktree(self, name: str = "") -> str:
        """Open the sibling worktree for branch ``name``, creating the branch and folder when missing.

        ``name`` defaults to ``branch`` in the chat's open state under ``~/.cdd`` and must not be the default
        branch. When the main clone has ``name`` checked out, it is committed, pushed, and the main
        clone goes back to the default branch so the worktree can take it. Saves ``branch`` and the
        worktree path as ``worktree`` in the chat's open state under ``~/.cdd``; later repo tools act in it.
        When the worktree cannot be brought up to date with origin, the reply says so and why.
        """
        opened = self._named_or_saved_branch(name).move_to_worktree()
        self.work_state.branch_name = opened.branch.name
        self.work_state.worktree_folder = opened.path
        behind = f"; not updated from origin: {opened.sync_failure}" if opened.sync_failure else ""
        return f"worktree for {opened.branch.name!r} at {opened.path}{behind}"

    @long_call
    @agent_tool
    @mcp
    def close_worktree(self, commit_message: str = "worktree: close") -> str:
        """Close the worktree saved in the chat's open state under ``~/.cdd``: commit, push its branch, remove the folder.

        Does not merge; the branch stays open as ``branch``. Clears ``worktree`` in
        the chat's open state under ``~/.cdd`` and returns later repo tools to the main clone.
        """
        worktree = self.open_worktree
        if worktree is None:
            raise NoOpenWorktreeError()
        branch = worktree.close(commit_message)
        self.work_state.worktree_folder = None
        return f"closed worktree for {branch.name!r}; branch pushed and kept open"

    @command(name="switch-branch")
    @agent_instructions
    def switch_branch_command(self) -> str:
        """Switch the main clone to a branch, creating it when missing. Nothing is committed: uncommitted work goes along.

        Use the branch the user names; otherwise call without a name so the branch saved in
        the chat's open state under ``~/.cdd`` is used. Call MCP ``repo.switch_branch``."""
        return ""

    @command(name="close-branch")
    @agent_instructions
    def close_branch_command(self) -> str:
        """Close a branch: commit, push, merge into main, push main, delete the branch.

        Use the branch the user names; otherwise call without a name so the branch saved in
        the chat's open state under ``~/.cdd`` is used. Call MCP ``repo.close_branch``."""
        return ""

    @command(name="switch-worktree")
    @agent_instructions
    def switch_worktree_command(self) -> str:
        """Open the sibling worktree for a branch other than main, creating it when missing.

        Use the branch the user names; otherwise call without a name so the branch saved in
        the chat's open state under ``~/.cdd`` is used. Call MCP ``repo.switch_worktree``."""
        return ""

    @command(name="close-worktree")
    @agent_instructions
    def close_worktree_command(self) -> str:
        """Close the open worktree: commit, push its branch, remove the folder. The branch stays open.

        Call MCP ``repo.close_worktree``."""
        return ""

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
        """Commit the working tree the repo tools act in using ``message`` (subject and optional body)."""
        text = (message or "").strip()
        if not text:
            raise CommitMessageRequiredError()
        repository = self._checkout_tools_act_in()
        sha = repository.commit([str(repository.root)], text, untracked=untracked)
        if sync_remote:
            repository.push_upstream()
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

    def move_to_worktree(self) -> Worktree:
        """Move this branch out of the main clone into its sibling worktree. The clone goes back to the default branch
        when it has this one checked out, after saving it."""
        repository = self._repo
        if self.is_default:
            raise DefaultBranchError("open a worktree for", repository.default_branch)
        if repository.current_branch == self:
            self.save(f"worktree: move {self.name} to its worktree")
            repository.branch_named(repository.default_branch).check_out()
        return self.open_in_worktree()

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

    def close(self, commit_message: str = "branch: close") -> None:
        """Save this branch, land it on the default branch, and delete it here and on origin. Refuses the default
        branch, and a branch still checked out in a linked worktree."""
        repository = self._repo
        if self.is_default:
            raise DefaultBranchError("close", repository.default_branch)
        occupied = self.worktree
        if occupied is not None and occupied.path.resolve() != repository.root:
            raise BranchInWorktreeError(self.name, occupied.path)
        leaving = repository.current_branch
        if leaving != self:
            leaving.save(commit_message)
        self.switch_to()
        self.save(commit_message)
        self.land_on_default()
        self.delete()


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
