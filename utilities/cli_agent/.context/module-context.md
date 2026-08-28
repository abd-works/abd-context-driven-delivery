# cli_agent — module context

## Purpose

**CliAgent** is the slash `/cli-agent` utility: same parent launch as **SubAgent** (listed
context tools plus optional actions, same turn policy), but the worker is an IDE
CLI process rather than an in-chat Task. Instructions tell the parent to spawn
`cursor-agent` or the VS Code agent CLI. **IdeCli** takes model, mode,
agent_mode, and judge as construct parameters; they are properties afterward
and map onto vendor flags. `CursorCli.create_chat` / `CursorCli.run` spawn via
`IdeCli.spawn` (`subprocess.run`).

## Primary use case

An agent pipes `toolset: cli_agent.cli_agent:CliAgent` / `tool: run` with
`tools` and optional `actions`. Flags are set when constructing `IdeCli`, then
read as properties on `CliAgent.ide` so the same instance can `run` more than
once. The parent sees `kind: sub_agent` / `launch: non_blocking` and starts the
IDE CLI with those properties. `judge` is a separate CLI session (doer + judge) on the same
**WorkSession**. A folder with no `.context/sessions` is opened the same way
`Workspace.open_work_session` creates the workspace and sprint.

## Rationale

SubAgent already owns turn opening and listed-kit loading. Duplicating that on a
new kit would split policy. The missing seam is **which IDE CLI** and **which
common flags**. Those belong on IdeCli, not on a separate options object.

## Seam

CliAgent, IdeCli, CursorCli, VscodeCli

## Public API

One cohesive file: `cli_agent.py`.

- `CliAgent` — `@agentic_toolset` (`cli_agent.cli_agent:CliAgent`); extends
  `SubAgent`; `/cli-agent` is `@prompt(name="cli-agent")` on `run(tools, actions)`.
  Property: `ide` — reuse across runs.
- `IdeCli` — construct with `model`, `mode`, `agent_mode`, `judge`, `resume`.
  `detect`, `launcher`, `command`, `judge_command`, `commands`, `spawn`,
  `run`, `run_all`.
- `CursorCli` / `VscodeCli` — vendor argv **and** `subprocess.run` via `spawn`

## Dependencies

- `sub_agent` — inherit `SubAgent` turn policy and `@sub_agent` launch kind
- `harness.harness_tool` — `@prompt`
- `primitives.actions` — `@agent_instructions` / `@agentic_toolset`
- `workspace` — WorkSession for doer and judge CLI identity

## Mechanism

- `IdeCli.detect` prefers `cursor-agent` / `agent`, then `code` /
  `code-insiders`.
- Cursor (`cursor-agent --help`): `-p --force --trust --workspace
  --output-format stream-json --stream-partial-output`; `--model` when set;
  `mode=fast` becomes `model[fast=true]`, `mode=medium` becomes
  `model[fast=false]`; `--mode plan|ask` when `agent_mode` is plan or ask.
- VS Code (`code chat`): `code {workspace} chat --new-window --mode
  ask|edit|agent`. `plan` maps to `agent`. No `--model` on this subcommand.
- `judge_command` is a second read-only spawn (`--mode ask`). `commands`
  returns worker argv, then judge argv when `judge` is set.
- `spawn` is `subprocess.run` of that argv. `run` / `run_all` call it.
- Cursor `--resume` is the `resume` property (WorkSession doer chat).
- `CursorCli.create_chat` runs `cursor-agent create-chat`.
