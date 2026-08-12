# context_tools/actions — peer action kits

## Purpose
Lifecycle and companion kits always used in the BaseContextTool frame. Deployed as
Cursor commands / VS Code prompts (not standalone skills) so they compose with a
context-tool skill: `/cdd` + `/sketch` → run CDD with `action: sketch`.

## Membership
Host-action kits: `sketch`, `iterate`, `grill_context`, `partition`, `repair`, `workspace`
Companions: `echo`, `handoff`

Non-action tooling stays under `utilities/` (`scanners`, `diagnose`, `agent_skills`, …).
