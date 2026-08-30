# sub_agent — module context

## Purpose

`sub_agent` provides the `@sub_agent` decorator and `SubAgentTool` dataclass that together mark a toolset method as a non-blocking background sub-agent launch. When the decorator is applied on top of `@agent_tool` or `@agent_instructions`, it routes the method as a sub-agent so the standard tool-discovery path skips it; `discover_sub_agent_tools` picks it up instead and produces `SubAgentTool` objects whose `signature_entry` renders as `kind: sub_agent / launch: non_blocking` in the manifest.

`SubAgent.run` is the slash action `/sub-agent`. When `actions` is listed and non-empty, those kits already open the work session and turn — this kit does **not** wrap them in `performTurn`. When `actions` is missing or empty, the worker runs `performTurn` (`workspace.workspace:Turn`, `action: performTurn`) around the listed context-tool work (open the hanging turn, each context tool as its own tools run, `finish_turn`; report branch and commit). `AgenticToolset.context_tools` loads `tools` (context tools) plus optional `actions` (other action kits). The parent launches **this prompt plus those context tools plus those actions** as one non-blocking sub-agent and does not wait.

Before launch, read `.context/sessions/{session}/model` (or `sessions/default` when none). When set, pass that model id as the sub-agent model; when unset, inherit the parent chat model. Never set disable-model-invocation.

## Seam

`SubAgent.run` (`kind: sub_agent`, `launch: non_blocking`); `SubAgentTool`, `sub_agent`, `discover_sub_agent_tools`

## Extend

Decorator stacking — inner `@agent_tool` / `@agent_instructions` captures the signature; `@sub_agent` flips routing so the method surfaces with sub-agent semantics. `register()` attaches the same discoverer as `members("sub_agent")` so `python -m tools run` with `tool:` still executes the method. `/sub-agent` is that stacking on `run`, with `context_tools(tools)` and `context_tools(actions)` resolved the same way other kits resolve `arguments.tools`.

## Dependencies

`tools.tool`, `harness.harness_tool`, `primitives.actions`
