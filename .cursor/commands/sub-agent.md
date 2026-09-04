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
context tools. Listed action kits already open the work session and turn.
Do not wrap those in performTurn. This kit does not open a work session itself
when actions are listed.

When actions is missing or empty: do not leave the worker on a bare context-tool
tools run. Run performTurn (workspace.workspace:Turn, action: performTurn)
around the work — open the hanging turn, run each listed context tool as its
own tools run, then finish_turn. finish_turn commits/pushes; report branch
and commit back to the parent.

through the tools cli

Pipe the fence to stdin from the repo root. Do not write a request file. Do not remanifest — this skill is the catalog. Follow response.instructions only.
```yaml
toolset: cli_agent.cli_agent:CliAgent
tool: run
```
.\tools.ps1 run -
