---
name: space-repo-branch-switch
description: >-
  Switch to ``name``. ``work_tree`` is required.
  
  When ``work_tree`` is true, use a sibling worktree.
  When ``work_tree`` is false, check out ``name`` in the current clone only.
  Refuses when the tree is dirty (use commit or stash first).
---

Switch to ``name``. ``work_tree`` is required.

When ``work_tree`` is true, use a sibling worktree.
When ``work_tree`` is false, check out ``name`` in the current clone only.
Refuses when the tree is dirty (use commit or stash first).

Use MCP tool: `repo.branch_switch(name: 'str', work_tree: 'bool')`
