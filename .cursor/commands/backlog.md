Capture an idea on the backlog — GitHub issue + Project Backlog.

Commits the current turn to capture state, then returns a ready-to-launch
sub-agent task. After this tool returns, launch a non-blocking sub-agent
(via /sub-agent with workflow.workflow:Workflow) using the returned
``sub_agent_task`` as the prompt. Do not call capture_backlog inline.

Infer `category` and `theme` unless the user sets them. Types:

- Defect: unexpected or wrong current behavior (the kit should already do this).
- Small change: a change to an existing feature, utility, or tool. Those are all Small changes unless the addition is very large.
- Refactor: changing code and where things are without changing functionality.
- Feature: standing up a new module (a new folder). Example: creating the CLI agent. A small change to an existing feature is not a Feature.

through the tools cli

Pipe the fence to stdin from the repo root. Do not write a request file. Do not remanifest — this skill is the catalog. Follow response.instructions only.
```yaml
toolset: workflow.workflow:Workflow
tool: backlog
```
.\tools.ps1 run -
