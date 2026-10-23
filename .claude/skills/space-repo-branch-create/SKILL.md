---
name: space-repo-branch-create
description: >-
  Create branch ``name`` from HEAD in the current clone only.
  
  Does not add a worktree. For a sibling worktree use ``repo.new_worktree`` or ``/branch``.
---

Create branch ``name`` from HEAD in the current clone only.

Does not add a worktree. For a sibling worktree use ``repo.new_worktree`` or ``/branch``.

Use MCP tool: `repo.new_branch(name: 'str', switch: 'bool' = True)`
