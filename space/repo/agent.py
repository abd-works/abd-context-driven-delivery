"""Agent toolset for repository branch lifecycle."""

from __future__ import annotations

from pathlib import Path

from harness.agent_tools import agent_instructions, agent_tool, agent_toolset, tools
from harness.installation.files import command
from harness.mcp.mcp_server import mcp

from space.repo import repo as clone
from space.repo.push import PushCommit, push_changes
from space.repo.worktree import (
    checkout_in_place,
    checkout_in_worktree,
    close_branch,
    close_worktree,
    open_repo,
)


@agent_toolset
class Repo:
    """Branch switch, create, and close (optional worktrees)."""

    def __init__(self, path: str = "") -> None:
        self._path = (path or "").strip()
        self._active: clone.Repo | None = None

    @property
    def current_branch(self) -> str:
        return self._repository().current_branch

    @property
    def checkout_path(self) -> str:
        return str(self._repository().root)

    def _repository(self) -> clone.Repo:
        if self._active is not None:
            return self._active
        return open_repo(self._path or Path.cwd())

    def _bind(self, repository: clone.Repo) -> clone.Repo:
        self._active = repository
        return repository

    @agent_tool
    @mcp
    @command(name="branch-switch")
    def branch_switch(self, name: str, work_tree: bool = True) -> str:
        """Switch to ``name`` — use a sibling worktree when ``work_tree`` is true.

        When ``work_tree`` is false, check out ``name`` in the current clone only.
        Refuses when the tree is dirty (use commit or stash first).
        """
        branch = (name or "").strip()
        if not branch:
            raise ValueError("branch name is required")
        repository = self._repository()
        if work_tree:
            self._bind(checkout_in_worktree(repository, branch))
        else:
            self._bind(checkout_in_place(repository, branch))
        return f"on branch {self.current_branch!r} at {self.checkout_path}"

    @agent_tool
    @mcp
    @command(name="branch-create")
    def branch_create(
        self,
        name: str,
        work_tree: bool = False,
        switch: bool = True,
    ) -> str:
        """Create branch ``name`` from the current HEAD when it does not exist.

        When ``work_tree`` is true, add a sibling worktree for ``name``.
        When ``switch`` is true, activate that branch (worktree or in-place).
        """
        branch = (name or "").strip()
        if not branch:
            raise ValueError("branch name is required")
        repository = self._repository()
        if switch and work_tree:
            self._bind(checkout_in_worktree(repository, branch))
        elif switch:
            self._bind(checkout_in_place(repository, branch))
        else:
            repository.create_branch(branch)
        return f"branch {branch!r} ready at {self.checkout_path}"

    @agent_tool
    @mcp
    @command(name="branch-close")
    def branch_close(
        self,
        name: str = "",
        commit_message: str = "branch: close",
        merge_to_main: bool = True,
    ) -> str:
        """Close the branch — commit if needed, push, merge to default, remove worktree.

        Pass ``name`` when closing a branch other than the current one.
        Skips merge when ``merge_to_main`` is false (commit and sync only).
        """
        repository = self._repository()
        result = close_branch(
            repository,
            (name or repository.current_branch or "").strip(),
            commit_message=commit_message,
            merge_to_main=merge_to_main,
        )
        self._active = None
        return result

    @agent_tool
    @mcp
    @command(name="worktree-switch")
    def worktree_switch(self, name: str) -> str:
        """Open branch ``name`` in a sibling worktree and bind this toolset to that checkout."""
        branch = (name or "").strip()
        if not branch:
            raise ValueError("branch name is required")
        self._bind(checkout_in_worktree(self._repository(), branch))
        return f"worktree for {self.current_branch!r} at {self.checkout_path}"

    @agent_tool
    @mcp
    @command(name="worktree-close")
    def worktree_close(self, commit_message: str = "worktree: close") -> str:
        """Commit, push, and remove this linked worktree when clean. Does not close the branch."""
        result = close_worktree(self._repository(), commit_message=commit_message)
        self._active = None
        return result

    @agent_tool
    def push_commit(self, message: str) -> PushCommit:
        """Commit the working tree using ``message`` (subject and optional body)."""
        return push_changes(self._repository(), message)

    @mcp
    @command(name="push")
    @agent_instructions
    def push(self, hint: str = "") -> str:
        """Commit local changes. Optional hint: {{hint}}.

        Inspect git status and diff (staged and unstaged). Draft a commit message that:
        - Summarizes what changed and why in a short imperative subject.
        - Names practice, fidelity, and artifact format when this session used CDD
          tools (slash commands, MCP tools, or skills), for example bdd-behavior,
          clean-engineering-code, or sketch.
        - Calls out key paths when that clarifies scope.

        If the working tree is clean, say so and do not call push_commit.
        Otherwise call push_commit with the full message (subject plus body when useful).
        """
        tools(self.push_commit(""))
        return "pushed"
