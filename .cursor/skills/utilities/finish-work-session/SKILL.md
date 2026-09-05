---
name: finish-work-session
description: "finish_work_session — close the current work session."
disable-model-invocation: true
---

finish_work_session — close the current work session.

Before calling: in the session worktree run ``git status``. Delete only temps
you know are ephemeral from this session (examples: ``Harness.write_deploy``
output under ``.cursor/commands`` and ``.cursor/skills``, agent BDD run logs
under ``.context/.agent_bdd_sessions/`` from spec runs, ``_req*.yaml`` scratch
files). Use session context — do not delete durable generate, product files, or
anything you cannot attribute to disposable temps. Never ask the user whether
to delete the worktree.

Then: commits change-related paths (scope + session artifacts), pushes, merges onto main,
clears any stash (stash must never keep a worktree), and removes the sibling worktree when
the tree is clean and pushed. If untracked or dirty files remain after you removed known
temps, leave the worktree and report what blocked removal.

When no work session is open (e.g. work landed on main without ``start_work_session``),
skips session.md / worktree removal and still finishes the turn (commit dirty checkout),
attaches this chat, and pushes.

through the tools cli

Pipe the block to stdin from the repo root. Do not write a request file. Do not remanifest — this skill is the catalog. Follow response.instructions only.
```
toolset: workspace.workspace:WorkSession
tool: finish_work_session
```
.\tools.ps1 run -
