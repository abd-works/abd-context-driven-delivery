# cli_agent — module context

## Purpose

**CliAgent** is the slash `/cli-agent` utility: same parent launch as **SubAgent** (listed
context tools plus optional actions, same turn policy), but the worker is an
interactive session rather than an in-chat Task. Instructions tell the parent to
spawn `cursor-agent` or the VS Code agent CLI. **IdeCli** takes model, mode,
agent_mode, and judge as construct parameters; they are properties afterward
and map onto vendor flags. `CursorCli.create_chat` uses `subprocess.run`.
`CursorCli.run` / `IdeCli.spawn` start the process with `Popen` and return.

## Primary use case

An agent pipes `toolset: cli_agent.cli_agent:CliAgent` / `tool: run` with
`tools` and optional `actions`. Flags are set when constructing `IdeCli`, then
read as properties on `CliAgent.ide` so the same instance can `run` more than
once. The parent sees `kind: sub_agent` / `launch: non_blocking` and starts an
interactive session with those properties. `judge` is a separate CLI session
(doer + judge) on the same **WorkSession**. A folder with no `.context/sessions`
is opened the same way `Workspace.open_work_session` creates the workspace and
sprint.

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
- `CursorCli` / `VscodeCli` — vendor argv **and** `Popen` via `spawn`

## Dependencies

- `sub_agent` — inherit `SubAgent` turn policy and `@sub_agent` launch kind
- `harness.harness_tool` — `@prompt`
- `primitives.actions` — `@agent_instructions` / `@agentic_toolset`
- `workspace` — WorkSession for doer and judge CLI identity

## Mechanism

- `IdeCli.detect` prefers `cursor-agent` / `agent`, then `code` /
  `code-insiders`.
- Default Cursor argv is an interactive session (`--trust --workspace`);
  `--model` when set; `mode=fast` becomes `model[fast=true]`, `mode=medium`
  becomes `model[fast=false]`; `--mode plan|ask` when `agent_mode` is plan or
  ask. `print_mode` adds `-p --force` and stream-json.
- VS Code (`code chat`): `code {workspace} chat --new-window --mode
  ask|edit|agent`. `plan` maps to `agent`. No `--model` on this subcommand.
- `judge_command` is a second spawn using the instance `agent_mode`. `commands`
  returns doer argv, then judge argv when `judge` is set. CliAgent describes the
  Turn (`action`, `tool_keys`, `toolCalls`) in the prompt. The CLI opens and
  finishes the hanging `workspace.Turn`. After finish, remaining actions are
  the next Turns — the CLI starts them without waiting for the operator.
  Judge validate uses that Turn's tools, fidelity, and format. The parent
  checks the CLI every once in a while and reports back; it does not drive
  with `-p`.
- `spawn` is `Popen` of that argv (Windows: new console). `run` / `run_all`
  call it and return.
- Cursor `--resume` is the `resume` property (WorkSession doer).
  `judge_resume` is the judge session.
- `CursorCli.create_chat` runs `cursor-agent create-chat`.
