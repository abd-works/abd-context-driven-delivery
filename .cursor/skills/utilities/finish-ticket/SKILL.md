---
name: finish-ticket
description: "Finish the open WorkSession — merge to main, Done on the project board, close issue, close session."
disable-model-invocation: true
---

Finish the open WorkSession — merge to main, Done on the project board, close issue, close session.

        Always moves the GitHub Project Status to **Done** (not issue-closed alone).
        Pass ``ticket`` or rely on the session slug's trailing ``-{issue}``.

        Before calling: in the session worktree run ``git status``. Delete only temps
        you know are ephemeral from this session (deploy output, agent BDD run logs,
        scratch request files). Use session context — do not delete durable artifacts.
        Then call finish so merge and worktree removal can proceed on a clean tree.

Use MCP tool: `workflow.finish(outcome: 'str' = '', workspace: 'str' = '', ticket: 'str' = '', reviewed_by: 'str' = '') -> 'dict[str, str]'`
