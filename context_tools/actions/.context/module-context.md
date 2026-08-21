# context_tools/actions — peer action kits

## Purpose
Lifecycle and companion kits always used in the BaseContextTool frame. Deployed as
**skills and** Cursor commands / VS Code prompts that compose with a context-tool
skill already in scope. `/iterate` and `/sketch` run their own toolset once with
`arguments.tools` listing the in-scope context tool(s). Other host actions still
compose as `/cdd` + `/validate` → run CDD with `action: validate`.

## Membership
Host-action kits: `sketch`, `iterate`, `grill_context`, `partition`, `repair`, `workspace`
Companions: `echo`, `handoff`

Host-action skill/command names match the BaseContextTool operation (`grill`, not
`grill-context`). Companions keep their own kit name (`echo`, `handoff`).

Non-action tooling stays under `utilities/` (`scanners`, `diagnose`, `agent_skills`, …).
