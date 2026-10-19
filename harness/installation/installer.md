# Installer

## Install

Install annotated toolsets into the IDE path — skills, commands, rules, MCP, and hooks. `replace` wipes files from the previous install first.

A full install on this repo normally finishes in a few seconds. **If an install call is still running after 10 seconds, stop waiting.** Cancel or kill the hung process, diagnose, fix, retry — prefer the repo venv one-liner over a stuck MCP round-trip when chat install hangs.

**After install finishes, read the diagnostic report back to the user.** `install` always runs `diagnose` and appends to `{install_path}/diagnostics.json` (for this repo, `.cursor/diagnostics.json`). The CLI only prints reports that start with `!` (red); green and yellow stay in the log. Open the latest `installs[]` entry: give the overall `color`, paste the full `diagnose_install` `report` (channel deltas, any new/deleted items, **mcp host**, **hook server**, **hooks registered (events)**, **hook handlers (operations)**), and call out red or yellow. If you ran install via MCP and only got an MCP handle, read that file or run `Installer(...).diagnose_install()` against the same install path — do not leave the user without the summary.

## Clean

Remove files written by the previous install for this IDE path.

## Diagnose Install

Compare this install with the last entry in `diagnostics.json` on the install path. Report green, yellow, or red, each channel as previous -> current (delta), every new or deleted item, whether the MCP host and hook server are running, and which hook events and handler operations are registered on the install path.

## Ensure Runtimes

Start the hook daemon and MCP host; fail if either stays down.

## Diagnose

`diagnostics.json` lives on the install path. Each install is a section. Each `@diagnostic` result is logged on that section with numbers, the message, and a color.

`diagnose` is the last install step. It compares this tree with the last install, then appends this install.

- Green: surface change is at most 10%.
- Yellow: surface change is at most 50%.
- Red: majority of the surface changed. The result starts with `!`, shows each channel delta, and these instructions.

When the result is red, do not treat the last install as wrong until you look:

1. Read the last install in `diagnostics.json` for the channel whose delta is largest.
2. Compare its `items` with the install tree: `skills/**/SKILL.md`, `commands/` or `prompts/`, `rules/**/*.mdc`, `hook-handlers.json`, and the MCP operations recorded for this install.
3. Check whether this install replaced a prior publish or kept it.
4. Check whether a toolset that should deploy was skipped, or an examples toolset was collected.
5. The next install appends another section — do not rewrite the trail.
