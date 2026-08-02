# Instructions

**CDD** (context-driven delivery) orchestrates practice contexts across delivery stages:

| Lens | Context | Owns | Sketch label |
|---|---|---|---|
| interactions | **stories** | journeys, slices, acceptance behaviour | Stories |
| domain | **ddd** | bounded contexts, building blocks, domain code | DDD |
| experience | **ux** | IA → mockups → clickable spec | UX |
| structure | **clean_engineering** (clean-code) | modules, typed design, production code | **Modules** |
| object behaviour | **bdd** | describe/it skeletons → green tests (**explore**+, after clean_engineering) | BDD |

> **Sketch labels** are the user-facing names used when confirming active perspectives. "Modules" is preferred over "clean_engineering" in any AskQuestion prompt — it names the design concern, not the tool.

CDD does **not** restate child rules. It picks **stage + context(s)**, sketches one engagement file, then pipes each row's `run` message to `tools run`.

**Defaults:** grill + sketch first. AI decides **order** and which lenses to run. One sketch file steers themes, flow, and the action trail.

---
# Contexts

## Stages (CDD fidelity)

| Fidelity | Intent | Default run scope |
|---|---|---|
| **discovery** | Whole-solution shape | Entire solution, or a large subsection |
| **explore** | Current increment | Increment, or a large subsection of it |
| **spec** | Narrow, concrete | ~sub-epic inside solution / increment |
| **engineer** | Working software | ~sub-epic inside solution / increment |

Grill and sketch work **much finer** inside that scope. Do not invent detail from a deeper stage.

### Stage → child fidelities

| CDD | stories | ddd | ux | clean_engineering | bdd |
|---|---|---|---|---|---|
| **discovery** | discovery | bounded_context | ia | modules | — |
| **explore** | exploration | building_blocks | mockup | model | **behavior** |
| **spec** | exploration | code | mockup | code | **development** |
| **engineer** | engineering | code | — | code | **development** |

UX has no engineering fidelity — production UI follows stories + clean_engineering at **engineer**, honouring the UX spec from **spec**.

### Sketch (one file)

Path: `{session.folder}/cdd-sketch.md` (see `templates/cdd-sketch.md`).

- **One file per engagement** — deepening fidelity (discovery → explore → spec → engineer) updates `fidelity:` at the top and deepens blocks in place. Never create a new file for a new fidelity.
- **Themes** — group lens blocks under one theme (epic, module, user goal, increment, or sub-epic).
- **Beside each other** — lens blocks under a theme stay close and comparable; not separate files.
- **Flow** — after each chunk: more at this stage, or proceed. Recommend proceed only when views agree.
- **Trail** — `TODO` → `doing` → `pass #label` (or `skip #why`). Move passes to `## log` as `stage / scope / theme / …`.

### Rules

- **`stage-from-context`** — Infer CDD fidelity from workspace artifacts, sketch, and user intent; confirm when ambiguous.
- **`cdd-owns-grill-sketch`** — Grill and sketch at CDD level. When following a child `tools run`, skip nested child grill/sketch; apply the child generate body only.
- **`views-agree-before-proceed`** — Recommend proceed only when the views in play for the current scope agree; otherwise more at the same stage. User can override.
- **`todo-trail-in-sketch`** — Persist actions as TODO/doing/pass #label in the sketch; archive passes under `## log`.

---
# Generate

1. Confirm CDD fidelity and **run scope** (defaults above); set `context.fidelity` if needed.
2. **Grill + sketch** — follow `sketch.md` rules: confirm lenses, scaffold if needed, grill per theme, fill lens blocks from child `sketch_template` notation only.
3. For each chosen row (your order):
   - Mark `doing #…` in the sketch.
   - Pipe `run` to `python -m tools run -`; follow that response (skip nested grill/sketch — CDD already sketched).
   - Mark `pass #…` (or `skip #why`); update flow note.
4. **Check agreement** — after sketching any lens, ask: does this raise questions another lens would answer? If yes, sketch that lens too (same theme, same file). Only when all active views agree, move to the next theme or deepen.
5. Update **flow**: recommend proceed or more-same-stage; wait for user override if they disagree.
6. When proceeding, deepen fidelity or move scope; keep the `## log`.
