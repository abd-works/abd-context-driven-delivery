---
name: sub-agent
description: "Run the listed context tools and actions as one non-blocking sub-agent."
disable-model-invocation: true
---

Run the listed context tools and actions as one non-blocking sub-agent.

tools — context tools (same arguments.tools as iterate / repair / generate).
actions — optional other action kits (iterate, generate, grill, …) to run with those context tools.
prompt — the task for the sub-agent. Uses the current chat context when omitted.

The parent sees kind: sub_agent / launch: non_blocking and does not wait.
Inside this sub-agent: follow this prompt. Do not inline any of that on the parent.

Model — before launch, read ``.context/sessions/{session}/model`` for the current
work session (or ``sessions/default`` when none). When that file has a model id,
pass it as the sub-agent model (Task/tool model parameter). When unset, inherit
the parent chat model. Never set disable-model-invocation.

When actions is listed and non-empty: run each listed action with the listed
context tools. Listed action kits manage their own session lifecycle.

When actions is missing or empty: do the work, then call **/turn**
(``workspace.workspace:Turn``, tool ``turn``) with context_tool, action, utility,
subject, and message. Report branch and commit back to the parent.

through the tools cli

Pipe the block to stdin from the repo root. Do not write a request file. Do not remanifest — this skill is the catalog. Follow response.instructions only.
```
toolset: cli_agent.cli_agent:CliAgent
tool: run
```
.\tools.ps1 run -
