"""Worktree paths and checkout helpers — branch lifecycle lives on :class:`Branch`."""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from space.repo.repo import Branch, Repo


def cursor_worktree_path(worktree_id: str) -> Path:
    """Detached checkout under ``~/.cursor/worktrees/{worktree_id}``."""
    slug = (worktree_id or "").strip()
    if not slug:
        raise ValueError("worktree id is required")
    return Path.home() / ".cursor" / "worktrees" / slug


def abbrev_repo_name(folder: str) -> str:
    tokens = [part for part in re.split(r"[-_]+", folder or "") if part]
    if not tokens:
        return folder or "repo"
    if len(tokens) == 1:
        return tokens[0]
    return tokens[0] + "-" + "".join(token[0] for token in tokens[1:])


def worktree_dirname(repo_folder: str, branch: str) -> str:
    """Sibling directory ``{abbrev}-{short-branch}`` next to the primary clone."""
    slug = (branch or "").strip().replace("/", "-")
    ticket = re.search(r"-(\d+)$", slug)
    short = ticket.group(1) if ticket else slug
    if ticket is None and len(short) > 24:
        short = short[:24].rstrip("-")
    return f"{abbrev_repo_name(repo_folder)}-{short}"


def open_repo(path: str | Path = ""):
    from space.repo.repo import Repo, RepoConnectError

    raw = str(path or ".").strip() or "."
    found = Repo(raw).find_root()
    if found is None:
        raise RepoConnectError("repo tools require a git repository")
    return Repo(found)


def try_fetch_pull(repository: Repo) -> None:
    from space.repo.repo import RepoConnectError

    try:
        repository.fetch()
    except RepoConnectError:
        return
    try:
        repository.pull()
    except RepoConnectError:
        return


def try_push(repository: Repo) -> None:
    from space.repo.repo import RepoConnectError

    try:
        repository.push()
    except RepoConnectError:
        return


def checkout_in_place(repository: Repo, branch: str) -> Repo:
    return repository.branch_named(branch).open_in_place()


def checkout_in_worktree(repository: Repo, branch: str) -> Repo:
    return repository.branch_named(branch).open_in_worktree()


def remove_worktree_when_clean(repository: Repo) -> bool:
    from space.repo.repo import Repo, RepoConnectError

    if getattr(repository, "_memory", False):
        return True
    try_push(repository)
    repository.clear_stash()
    if repository.is_dirty(untracked=False) or repository.has_unpushed_commits():
        return False
    if not repository.is_linked_worktree():
        return True
    try:
        Repo(repository.primary_root()).remove_worktree(repository.root)
    except RepoConnectError:
        return False
    root = Path(repository.root)
    if root.is_dir():
        try:
            if not any(root.iterdir()):
                root.rmdir()
        except OSError:
            pass
    return True


def close_worktree(
    repository: Repo,
    *,
    commit_message: str = "worktree: close",
) -> str:
    """Commit, push, and remove this linked worktree when clean — does not close branch or session."""
    if repository.is_dirty(untracked=False):
        repository.commit([str(repository.root)], commit_message, untracked=True)
    try_push(repository)
    removed = remove_worktree_when_clean(repository)
    if removed:
        return f"closed worktree at {repository.root!s}"
    return (
        f"worktree at {repository.root!s} kept — dirty tree or unpushed commits"
    )


def close_branch(
    repository: Repo,
    branch: str,
    *,
    commit_message: str = "branch: close",
    merge_to_main: bool = True,
    close_session: bool = True,
) -> str:
    """Close a branch on this checkout — prefer :meth:`Branch.close` on a :class:`Branch`."""
    name = (branch or repository.current_branch or "").strip()
    return repository.branch_named(name).close(
        commit_message=commit_message,
        merge_to_main=merge_to_main,
        close_session=close_session,
    )
