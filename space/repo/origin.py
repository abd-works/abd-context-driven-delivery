"""Origin and Merges - what a checkout exchanges with the repository it was cloned from, and how it merges a branch in."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from harness.git.git import RepoConnectError

if TYPE_CHECKING:
    from space.repo.repo import Branch, Repo

# The session files every branch only appends to, which a merge keeps both sides of.
_UNION_MERGED_LOGS = (".sessions/**/session.log merge=union", ".sessions/**/session.err merge=union")


class Origin:
    """The remote called origin of one checkout, which its branch is pushed to and caught up from: a push never fails
    because work was pushed to the branch from elsewhere, since it merges origin's copy in first."""

    def __init__(self, repo: Repo) -> None:
        self._repo = repo

    def push_upstream(self) -> None:
        """Push the current branch to origin; when origin refuses because it has commits this branch lacks, merge them
        in and push again. Most pushes go through at once, so origin is fetched only when it refuses."""
        git = self._repo.git
        branch = self._repo.current_branch.name
        try:
            git.run("push", "-u", "origin", branch)
        except RepoConnectError:
            self.catch_up()
            git.run("push", "-u", "origin", branch)

    def catch_up(self) -> None:
        """Fetch origin, then merge its copy of the current branch in as ``merge_copy`` does."""
        self.fetch()
        self.merge_copy()

    def merge_copy(self) -> None:
        """Merge origin's copy of the current branch, as last fetched, into it when origin has commits this branch lacks;
        nothing when origin has no copy yet or this branch already holds every commit of it."""
        repo = self._repo
        tracked = f"origin/{repo.current_branch.name}"
        if not repo.refs.has(f"refs/remotes/{tracked}") or repo.git.succeeds("merge-base", "--is-ancestor", tracked, "HEAD"):
            return
        repo.merges.merge(tracked, "")

    def needs_push(self) -> bool:
        """True when origin has no copy of the current branch yet or the branch is ahead of it. A git failure is raised,
        not read as nothing to push, so a close never reports a branch pushed that was not."""
        repo = self._repo
        branch = repo.current_branch.name
        if not repo.refs.has(f"refs/remotes/origin/{branch}"):
            return True
        return int(repo.git.run("rev-list", f"origin/{branch}..HEAD", "--count") or "0") > 0

    def fetch(self) -> None:
        self._repo.git.run("fetch", "origin")


class MergeRefusedError(RepoConnectError):
    """Raised when git refuses to merge one branch into the branch a checkout has checked out, such as when both changed
    the same lines. The merge is undone before this is raised, so the checkout is as it was. It names both branches and
    carries git's own words, which say where they disagree."""

    def __init__(self, branch: str, into: str, refusal: str) -> None:
        super().__init__(f"{branch} does not merge into {into}; the merge was undone and nothing changed. Merge {into} into {branch} where {branch} is checked out, settle what they disagree on there, and try again. git said: {refusal}")
        self.branch = branch
        self.into = into
        self.refusal = refusal


class Merges:
    """How one checkout merges a branch into the one it has checked out. Every branch appends to the same session logs,
    so those merge by keeping the lines of both sides instead of stopping the merge on a conflict."""

    def __init__(self, repo: Repo) -> None:
        self._repo = repo

    def merge_from(self, other: Branch, message: str = "") -> str:
        """Merge other into the current branch without checking other out; the commit the branch is on after."""
        repo = self._repo
        if other == repo.current_branch:
            return repo.current_commit
        self.merge(other.name, message)
        return repo.current_commit

    def merge(self, ref: str, message: str) -> None:
        """Merge ref into the current branch. A merge left half done blocks every later checkout and commit, so a merge
        that fails is aborted, the checkout goes back as it was, and ``MergeRefusedError`` names the two branches."""
        repo = self._repo
        self.keep_session_logs_by_union()
        with repo.writing_index:
            try:
                repo.git.run("merge", ref, *(["-m", message] if message else ["--no-edit"]))
            except RepoConnectError as refused:
                repo.git.succeeds("merge", "--abort")
                raise MergeRefusedError(ref, repo.current_branch.name, str(refused)) from refused

    def keep_session_logs_by_union(self) -> None:
        """Tell git, in this repository's own attributes file, which no checkout commits, to merge session logs by
        union: each line either side wrote is kept."""
        repo = self._repo
        common = Path(repo.git.run("rev-parse", "--git-common-dir"))
        attributes = (common if common.is_absolute() else repo.root / common) / "info" / "attributes"
        written = attributes.read_text(encoding="utf-8") if attributes.is_file() else ""
        missing = [line for line in _UNION_MERGED_LOGS if line not in written.splitlines()]
        if not missing:
            return
        attributes.parent.mkdir(parents=True, exist_ok=True)
        lead = "" if not written or written.endswith("\n") else "\n"
        attributes.write_text(written + lead + "".join(f"{line}\n" for line in missing), encoding="utf-8")
