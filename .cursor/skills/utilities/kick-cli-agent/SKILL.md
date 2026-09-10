---
name: kick-cli-agent
description: "Nudge a stalled doer to advance to the next job."
disable-model-invocation: true
---

Nudge a stalled doer to advance to the next job.

        ## When to use

        Call when the doer has clearly finished its current job (notes written, ticket updated,
        etc.) but the queue has not advanced and no new console opened.

        ## What kick does

        Sends the active doer a short prompt via the CLI asking it to call
        ``complete_job()`` then ``launch_next()`` if the job is done, or to do nothing
        if it is still waiting for the judge.

Use MCP tool: `cli_agent.kick() -> 'str'`
