---
name: start-ticket
description: "Start work from a GitHub issue — In Progress, WorkSession, session branch."
disable-model-invocation: true
---

Start work from a GitHub issue — In Progress, WorkSession, session branch.

``kind: sub_agent`` / ``launch: non_blocking`` — the parent launches a sub-agent
for this operation and does not wait. Inside that sub-agent, run start (In Progress,
open WorkSession, session branch) then continue the ticket work.

through the tools cli

Pipe the fence to stdin from the repo root. Do not write a request file. Do not remanifest — this skill is the catalog. Follow response.instructions only.
```yaml
toolset: workflow.workflow:Workflow
tool: start
```
.\tools.ps1 run -
