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

through the tools cli

Pipe the fence to stdin from the repo root. Do not write a request file. Do not remanifest — this skill is the catalog. Follow response.instructions only.
```yaml
toolset: workflow.workflow:Workflow
tool: finish
```
.\tools.ps1 run -
