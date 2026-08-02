# Module: cdd

**Purpose:** Orchestrate practice contexts (stories, ddd, ux, clean_engineering, bdd) across CDD delivery stages so agents pick stage + lenses, sketch once, then pipe each child `run` without restating child rules.

**Primary use case:** At a chosen CDD fidelity (`discovery` / `explore` / `spec` / `engineer`), call lifecycle actions (`grill`, `sketch`, `generate_output`, `iterate`, `validate`, `satisfy`, `document`) and have each walk the ordered child context tools for that stage.

**Rationale:** CDD owns stage menu and sketch/flow; child generators own domain rules. Stage → child fidelity is the complete contract in code (`_STAGES`); AI may reorder or skip rows.

## Seam

`Cdd(fidelity=…).context_tools()` yields live child toolset instances at the child fidelities for that stage. Lifecycle `@action` methods for-each those instances and call the matching child action.

## Public API

- `Cdd(fidelity, format=None, path=None, session=None)`
- `context_tools() -> list`
- Actions: `generate_output`, `grill`, `sketch`, `iterate`, `validate`, `satisfy`, `document(paths)`

## Dependencies

`Stories`, `Ddd`, `Ux`, `CleanEngineering`, `Bdd` (via `BaseContextTool`)

**Mechanism stereotype:** stage fidelity → ordered (ContextClass, child_fidelity) → instantiate → for-each child action
