# Module: cdd

**Purpose:** Orchestrate practice contexts (stories, ddd, ux, clean_engineering, bdd) across CDD delivery stages so agents pick stage + lenses, sketch once, then pipe each child `run` without restating child rules.

**Primary use case:** At a chosen CDD fidelity (`discovery` / `spec` / `engineer`), expand `guidance` to list each stage child as a separate tools run, then pass those children (or Cdd itself) into the lifecycle kits.

**Rationale:** CDD owns stage menu; child generators own domain rules; kits own generate / validate / satisfy / document / grill / sketch / iterate. Stage → child fidelity is the complete contract: each child class declares its own `fidelities` dict keyed by `BaseContextTool` stage constants; the stage menu lists the ordered class sequence per stage; AI may reorder or skip rows.

## Seam

`Cdd(fidelity=…).context_tools()` yields live child toolset instances at the child fidelities for that stage, **without** `mode` pre-set (inline by default). Tool-mode actions set `t.mode = "tool"` inside their own loop body. Child fidelity is resolved from each class's own `fidelities[stage]` dict.

## Public API

- `Cdd(fidelity, format=None, path=None, session=None)`
- `context_tools() -> list` — returns inline instances (no mode pre-set)
- `guidance` — lists each stage child as a tool-mode companion; kits own generate / validate / satisfy / document / grill / sketch / iterate (`Generate().generate(tools=[cdd])`)

## Extend

Stage fidelity → ordered child class list for that stage → each class's `fidelities[stage]` → instantiate → action loop with mode set per action's fidelity level. `guidance` lists each stage child with `mode = "tool"` so the matching kit action is a separate tools run per child — never inline full child recipes.

## Dependencies

`Stories`, `Ddd`, `Ux`, `CleanEngineering`, `Bdd` (via `BaseContextTool`)
