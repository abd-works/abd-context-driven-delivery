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

        Then: treats the worktree as the unit of isolation, commits every modified, staged,
        deleted, and untracked file under the repository root, pushes, and merges onto main.
        Do not filter by scope paths, session artifacts, author, or which changes you recognize.
        Clear any stash (stash must never keep a worktree), and remove the sibling worktree when
        the tree is clean and pushed. If untracked or dirty files remain after the full-root commit,
        leave the worktree and report what blocked removal.

        When no work session is open (e.g. work landed on main without ``start_work_session``),
        skips session.md / worktree removal and still finishes the turn (commit dirty checkout),
        attaches this chat, and pushes.

Use MCP tool: `work_session.finish_work_session(tools: 'list[Any] | None' = None, outcome: 'str' = '', handoff: 'str' = 'handoff.md') -> 'str'`
