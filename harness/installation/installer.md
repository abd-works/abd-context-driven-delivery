# Installer

## Install

Install annotated toolsets into the IDE path — skills, commands, rules, MCP, and hooks. `replace` wipes files from the previous install first.

Use slash **`/install`** (command — not a skill, not MCP). Deployed **commands** and **skills**:

- ``@agent_instructions`` with ``@mcp``: short docstring in the slash/skill file; MCP invoke tail (full instructions stay on the MCP prompt).
- ``@agent_tool`` **without** ``@mcp``: Shell invoke tail — ``scripts/{deploy_name}.py`` when present, else ``python -c`` via ``AgentToolSet.instantiate`` (e.g. ``/install`` → ``scripts/install.py``).
- ``@agent_tool`` **with** ``@mcp``: MCP invoke tail on the same skill/command file (no Shell tail).

Every full install also re-deploys the Installer toolset last so the slash commands stay current.

When install runs **inside** the live MCP host process, the installer skips a second `McpHost.standup()` and skips `ensure_mcp_host()` so it does not reload every toolset or rewrite Cursor `mcp.json` during an unrelated tool request.

**After install finishes, read the diagnostic report back to the user.** `install` always runs `diagnose_after_install` (install-channel counts and runtime status only) and appends to `{install_path}/diagnostics.json` (for this repo, `.cursor/diagnostics.json`). It does not run guidance instruction or action probes — use `/guidance-diagnostics` for those. The CLI only prints reports that start with `!` (red); green and yellow stay in the log. Open the latest `installs[]` entry: give the overall `color`, paste the full `diagnose_install` `report` (channel deltas, any new/deleted items, **mcp host**, **hook server**, **hooks registered (events)**, **hook handlers (operations)**), and call out red or yellow. If you ran install in the shell, read that file or run `Installer(...).diagnose_install()` against the same install path — do not leave the user without the summary.

## Clean

Remove files written by the previous install for this IDE path. Slash **`/clean`** — same automatic Shell tail (``@agent_tool`` without MCP).

## Diagnose Install

Compare this install with the last entry in `diagnostics.json` on the install path. Report green, yellow, or red, each channel as previous -> current (delta), every new or deleted item, whether the MCP host and hook server are running, and which hook events and handler operations are registered on the install path.

`diagnose_after_install` is the last install step. It runs `diagnose_install` and appends one install section to `diagnostics.json`.

- Green: surface change is at most 10%.
- Yellow: surface change is at most 50%.
- Red: majority of the surface changed. The result starts with `!`, shows each channel delta, and these instructions.

When the result is red, do not treat the last install as wrong until you look:

1. Read the last install in `diagnostics.json` for the channel whose delta is largest.
2. Compare its `items` with the install tree: `skills/**/SKILL.md`, `commands/` or `prompts/`, `rules/**/*.mdc`, `hook-handlers.json`, and the MCP operations recorded for this install.
3. Check whether this install replaced a prior publish or kept it.
4. Check whether a toolset that should deploy was skipped, or an examples toolset was collected.
5. The next install appends another section — do not rewrite the trail.

Guidance instruction and action probes live on `/guidance-diagnostics`, not on install.

## Agent tools diagnostics

Probe **space**, **harness**, and **tools**: ping on the live MCP host; light + heavy invoke in a child process ([`cdd-diagnostic`](https://github.com/abd-works/cdd-diagnostic) fixtures). Results in `diagnostics.json` → `agent_tools`. Slash **`/agent-tools-diagnostics`** → MCP `agent-tools-diagnostics.agent_tools_diagnostics`.

## Ensure Runtimes

Start the hook daemon and MCP host; fail if either stays down.
