# diagnose — module context

## Purpose
Provides a disciplined, phase-sequenced bug-hunting loop as a `@sub_agent` tool.
Hosts (BDD, Stories) call `diagnostic().diagnose()` from `satisfy` / `iterate`
so the six phases stay on the tool — they are not inlined into surrounding
action markdown.

## Seam
`Diagnose.diagnose` (`kind: sub_agent`, `launch: non_blocking`)

## Dependencies
`sub_agent.sub_agent`, `tools.tool`
