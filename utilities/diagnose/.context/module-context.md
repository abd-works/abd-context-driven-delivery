# diagnose — module context

## Purpose
Provides a disciplined, phase-sequenced bug-hunting loop as a `@sub_agent` tool.
Hosts (BDD, Stories) call `diagnostic().diagnose()` from `satisfy` / `iterate`
so the six phases stay on the tool — they are not inlined into surrounding
action markdown.

## Seam
`Diagnose.diagnose` is `@prompt(name="diagnose")` plus `@sub_agent` `@agent_tool` (`kind: sub_agent`, `launch: non_blocking`). Slash `/diagnose` is the command; hosts still call `diagnose()` as a non-blocking sub-agent.

## Dependencies
`tools.sub_agent`, `tools.tool`
