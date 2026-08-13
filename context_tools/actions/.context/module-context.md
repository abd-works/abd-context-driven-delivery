# context_tools/actions — peer action kits

## Purpose
Lifecycle and companion kits always used in the BaseContextTool frame. Deployed as
**skills and** Cursor commands / VS Code prompts that compose with a context-tool
skill already in scope: `/cdd` + `/sketch` → run CDD with `action: sketch`.
Do not run these kits as their own toolset when a context tool is in play.

## Membership
Host-action kits: `sketch`, `iterate`, `grill_context`, `partition`, `repair`, `workspace`
Companions: `echo`, `handoff`

Host-action skill/command names match the BaseContextTool operation (`grill`, not
`grill-context`). Companions keep their own kit name (`echo`, `handoff`).

Non-action tooling stays under `utilities/` (`scanners`, `diagnose`, `agent_skills`, …).
