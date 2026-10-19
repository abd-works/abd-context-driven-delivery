"""Commit (and sync) working tree changes."""

from __future__ import annotations

from dataclasses import dataclass

from space.repo.repo import Repo


@dataclass(frozen=True)
class PushCommit:
    """Result of a repository push — subject line, branch, and new commit SHA."""

    subject: str
    branch: str
    sha: str


def push_changes(
    repository: Repo,
    message: str,
    *,
    untracked: bool = True,
    sync_remote: bool = True,
) -> PushCommit:
    text = (message or "").strip()
    if not text:
        raise ValueError("commit message is required")
    subject = text.splitlines()[0].strip()
    sha = repository.commit([str(repository.root)], text, untracked=untracked)
    if sync_remote and not getattr(repository, "_memory", False):
        repository.push()
    return PushCommit(subject=subject, branch=repository.current_branch, sha=sha)
