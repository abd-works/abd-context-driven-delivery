Nudge a stalled doer to advance to the next job.

## When to use

Call when the doer has clearly finished its current job (notes written, ticket updated,
etc.) but the queue has not advanced and no new console opened.

## What kick does

Sends the active doer a short prompt via the CLI asking it to call
``complete_job()`` then ``launch_next()`` if the job is done, or to do nothing
if it is still waiting for the judge.

through the tools cli

Pipe the fence to stdin from the repo root. Do not write a request file. Do not remanifest — this skill is the catalog. Follow response.instructions only.
```yaml
toolset: cli_agent.cli_agent:CliAgent
tool: kick
```
.\tools.ps1 run -
