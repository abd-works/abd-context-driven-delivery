# Installer

## Install

Install annotated toolsets into the IDE path — skills, commands, rules, MCP, and hooks. `replace` wipes files from the previous install first.

## Clean

Remove files written by the previous install for this IDE path.

## Diagnose Install

Compare this install with the last entry in `diagnostics.json` on the install path. Report green, yellow, or red, each channel as previous -> current (delta), and every new or deleted item.

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
