---
description: "Treat the complete worktree as the unit committed and pushed"
alwaysApply: true
---

# Worktree Ownership

The Git worktree is the unit of isolation. Every modified, staged, deleted, and untracked file in that worktree belongs to it, whether the change came from the user, an agent, a generator, or a tool.

When the user says to commit or push the repository, commit and push the entire worktree. Do not filter files by task scope, session paths, who changed them, or which changes you recognize. Inspect the complete status and diff, then stage all changes with `git add -A` and commit them together. Only leave something out when the user explicitly excludes it; never silently narrow the request.

Finishing a work session follows the same rule. Commit the repository root before pushing the session branch and merging it to main. Worktrees already provide the required isolation, so additional path filtering can strand valid work in a branch that the user asked to finish.
