# improvement — peer kit for /repair

## Purpose
Agentic kit for repair and verify_fix. Not composed on BaseContextTool.
Slash `/repair` invokes `improvement.improvement:Improvement` with `arguments.tools`.

## Public API
- `repair(tools, asset, violation)` — `@agent_instructions`
- `verify_fix(tools, theme)` — `@agent_tool`

Domain `Repair` lives on `WorkSession.repairs` (workspace package).

Manual loop until the kit is real: `repair.md` (associate → theme → `/diagnose` → **proposed kit change** → fail-first at that seam). `@instruction(label="repair")` loads it.
