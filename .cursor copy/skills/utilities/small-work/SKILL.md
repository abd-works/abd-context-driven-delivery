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

Use MCP tool: `plan_commands.small_work(context: 'str' = '', workspace: 'str' = '', hil_reply: 'str' = '', issue: 'str' = '', issues: 'list | None' = None) -> 'dict[str, Any]'`
