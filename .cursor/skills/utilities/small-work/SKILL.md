---
name: small-work
description: "/plan /small-work {context} — load small-work Workflow; run themed tickets when theme is set."
disable-model-invocation: true
---

/plan /small-work {context} — load small-work Workflow; run themed tickets when theme is set.

With ``theme:…`` in context, processes that theme's issues. Pass ``issue`` to run
one ticket only (one Turn). Thin context triggers Grill + HIL Grill; the judge
(not the parent) replies via ``hil_reply``. Fixture ``issues`` may be passed for
Agent BDD. Without a theme, only opens the Plan on the prebaked Workflow.

through the tools cli

Pipe the block to stdin from the repo root. Do not write a request file. Do not remanifest — this skill is the catalog. Follow response.instructions only.
```
toolset: plan.plan:Plan
tool: small_work
```
.\tools.ps1 run -
