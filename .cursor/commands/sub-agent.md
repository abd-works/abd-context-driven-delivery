Run this prompt, the listed context tools, and any listed actions as one non-blocking sub-agent.

tools — context tools (same arguments.tools as iterate / repair / generate).
actions — optional other action kits (iterate, generate, grill, …) to run with those context tools.

The parent sees kind: sub_agent / launch: non_blocking and does not wait.
Inside this sub-agent: follow this prompt. Do not inline any of that on the parent.

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

Pipe the fence to stdin. Do not write a request file. Do not remanifest — this skill is the catalog.
```yaml
toolset: sub_agent.sub_agent:SubAgent
tool: run
```
python -m tools run -
