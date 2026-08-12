# Module: cdd

**Purpose:** Orchestrate practice contexts (stories, ddd, ux, clean_engineering, bdd) across CDD delivery stages so agents pick stage + lenses, sketch once, then pipe each child `run` without restating child rules.

**Primary use case:** At a chosen CDD fidelity (`discovery` / `spec` / `engineer`), call lifecycle actions (`grill`, `sketch`, `generate_output`, `iterate`, `validate`, `satisfy`, `document`) and have each walk the ordered child context tools for that stage.

**Rationale:** CDD owns stage menu and sketch/flow; child generators own domain rules. Stage → child fidelity is the complete contract: each child class declares its own `fidelities` dict keyed by `BaseContextTool` stage constants; `_CONTEXT_TOOLS_BY_STAGE` lists the ordered class sequence per stage; AI may reorder or skip rows.

## Action fidelity ladder

Actions follow a deliberate context-loading hierarchy — both exploration passes are constrained:

- `grill` — inline action mode, constrained context per child. Calls `workspace.open()` + `contexts` (main context file only) + `grill_context.grill_with_context()` per child. Does NOT call `generate()`. Q&A pass only.
- `sketch` — inline action mode, constrained context per child. Calls `workspace.open()` + `contexts` (main context file only) + `sketcher.sketch_session()` per child. Does NOT call `generate()`. Shape pass only.
- `generate_output`, `iterate`, `validate`, `satisfy`, `document` — tool mode. Each child is invoked as a separate, independent tool call (`mode = "tool"` set before each call). Full context per child, isolated from the others.

## Seam

`Cdd(fidelity=…).context_tools()` yields live child toolset instances at the child fidelities for that stage, **without** `mode` pre-set (inline by default). Tool-mode actions set `t.mode = "tool"` inside their own loop body. Child fidelity is resolved from each class's own `fidelities[stage]` dict.

## Public API

- `Cdd(fidelity, format=None, path=None, session=None)`
- `context_tools() -> list` — returns inline instances (no mode pre-set)
- Actions: `grill`, `sketch`, `generate_output`, `iterate`, `validate`, `satisfy`, `document(paths)`

## Dependencies

`Stories`, `Ddd`, `Ux`, `CleanEngineering`, `Bdd` (via `BaseContextTool`)

**Mechanism stereotype:** stage fidelity → `_CONTEXT_TOOLS_BY_STAGE[stage]` ordered class list → each class's `fidelities[stage]` → instantiate → action loop with mode set per action's fidelity level.
