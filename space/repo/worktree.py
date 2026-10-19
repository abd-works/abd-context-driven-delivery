"""Worktree checkout and branch close — shared with legacy WorkSession."""

from __future__ import annotations

import re
from pathlib import Path


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


def try_fetch_pull(repository) -> None:
    from space.repo.repo import RepoConnectError

    try:
        repository.fetch()
    except RepoConnectError:
        return
    try:
        repository.pull()
    except RepoConnectError:
        return


def try_push(repository) -> None:
    from space.repo.repo import RepoConnectError

    try:
        repository.push()
    except RepoConnectError:
        return


def checkout_in_place(repository, branch: str):
    repository.checkout_or_create(branch)
    try_fetch_pull(repository)
    return repository


def checkout_in_worktree(repository, branch: str):
    from space.repo.repo import Repo, RepoConnectError

    if getattr(repository, "_memory", False):
        repository.checkout_or_create(branch)
        return repository
    existing = repository.worktree_for(branch)
    if existing is not None and existing.path.resolve() != Path(repository.root).resolve():
        other = Repo(existing.path)
        try_fetch_pull(other)
        return other
    if repository.current_branch == branch:
        try_fetch_pull(repository)
        return repository
    try:
        repository.fetch()
    except RepoConnectError:
        pass
    primary = repository.primary_root()
    dest = primary.parent / worktree_dirname(primary.name, branch)
    tree_path = repository.add_worktree(dest, branch)
    other = Repo(tree_path)
    try_fetch_pull(other)
    return other


def land_branch_on_default(repository, branch: str) -> None:
    from space.repo.repo import Repo, RepoConnectError

    if getattr(repository, "_memory", False):
        return
    default = repository.default_branch
    try_push(repository)
    for candidate in (default, f"origin/{default}", "main", "origin/main"):
        try:
            repository.merge_from(
                candidate,
                message=f"merge {candidate} into {branch}",
            )
            break
        except RepoConnectError:
            continue
    try:
        repository.push_to(default)
    except RepoConnectError:
        pass
    occupier = repository.worktree_for(default)
    if occupier is None:
        try:
            repository._git("branch", "-f", default, "HEAD")
        except RepoConnectError:
            return
        return
    if occupier.path.resolve() == Path(repository.root).resolve():
        return
    other = Repo(occupier.path)
    other.clear_stash()
    if other.is_dirty():
        return
    try:
        other.merge_from(
            branch,
            message=f"merge {branch} into {default}",
        )
    except RepoConnectError:
        return


def remove_worktree_when_clean(repository) -> bool:
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


def close_branch(
    repository,
    branch: str,
    *,
    commit_message: str = "branch: close",
    merge_to_main: bool = True,
) -> str:
    name = (branch or repository.current_branch or "").strip()
    if not name:
        raise ValueError("branch name is required")
    if repository.is_dirty(untracked=False):
        repository.commit([str(repository.root)], commit_message, untracked=True)
    if merge_to_main:
        land_branch_on_default(repository, name)
    removed = remove_worktree_when_clean(repository)
    if removed:
        return f"closed branch {name!r} — merged to default and removed worktree when clean"
    return (
        f"closed branch {name!r} — merged when possible; "
        "worktree kept (dirty or unpushed commits)"
    )
