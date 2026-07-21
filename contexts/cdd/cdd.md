# Instructions

**CDD** (context-driven delivery) orchestrates practice contexts across delivery stages:

| Lens | Context | Owns |
|---|---|---|
| interactions | **stories** | journeys, slices, acceptance behaviour |
| domain | **ddd** | bounded contexts, building blocks, domain code |
| experience | **ux** | IA → mockups → clickable spec |
| structure | **clean_engineering** (clean-code) | modules, typed design, production code |
| object behaviour | **bdd** | describe/it skeletons → green tests (**explore**+, after clean_engineering) |

CDD does **not** restate child rules. It picks **stage + context(s)** via `resolve_targets`, then pipes each row’s `run` message to `tools run`.

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
| **discovery** | discovery | bounded_context | ia | language | — |
| **explore** | exploration | building_blocks | mockup | modules | **behavior** |
| **spec** | specification | code | specification | specification | **development** |
| **engineer** | engineering | code | — | code | **development** |

UX has no engineering fidelity — production UI follows stories + clean_engineering at **engineer**, honouring the UX spec from **spec**.

### Sketch (one file)

Path: engagement `{destination}/.context/cdd-sketch.md` (see `sketch-template.md`).

- **Themes** — Group short sketches of different types under one theme (epic, module, user goal/screens, increment, or sub-epic). Ask which kind; recommend from context.
- **Beside each other** — Lens blocks under a theme stay close and comparable; not separate files.
- **Flow** — After each chunk: more at this stage, or proceed. Recommend proceed only when views in play **agree**; else stay. User may override. Plain language in notes.
- **Trail** — `TODO` → `doing` → `pass #label` (or `skip #why`). Move completed passes to bottom `## log` as `stage / scope / theme / …`.

### Rules

- **`stage-from-context`** — Infer CDD fidelity from workspace artifacts, sketch, and user intent; confirm when ambiguous.
- **`resolve-then-sketch-then-run`** — Call `resolve_targets` **before any lens content**. Sketch the one CDD file by filling each lens from that row’s `sketch_template` (child notation only). Then order/skip rows and pipe each chosen `run` to `tools run`. Do not open each child’s own sketch session.
- **`lens-from-child-template`** — A lens block that is not in the child generator’s sketch language is invalid. No free prose inside `stories:` / `ddd:` / `ux:` / `ce:` / `bdd:`. If you cannot yet name Epic/Actor→Story (etc.), leave `* approx …` or omit the block — do not write design commentary there.
- **`cdd-owns-grill-sketch`** — Grill and sketch at CDD. When following a child `tools run`, skip nested child grill/sketch; apply the child generate body only.
- **`views-agree-before-proceed`** — Recommend proceed only when the views in play for the current scope agree; otherwise more at the same stage. User can override.
- **`todo-trail-in-sketch`** — Persist actions as TODO/doing/pass #label in the sketch; archive passes under `## log`.

---
# Generate

1. Confirm CDD fidelity and **run scope** (defaults above); set `context.fidelity` if needed.
2. Call **`resolve_targets`** first — each row is `{context, fidelity, sketch_template, run}`. Keep the `sketch_template` text for every lens you will fill.
3. **Grill** open questions — short rounds inside the run scope. After every 2–3 answers, refresh the sketch using step 4 (not free prose).
4. **Sketch** one engagement file: CDD `sketch-template.md` for shell (theme/flow/trail); **each lens block body from the matching child `sketch_template`**. Reject/replace any prose-only lens lines.
5. For each chosen row (your order):
   - Mark `doing #…` in the sketch.
   - Pipe `run` to `python -m tools run -`; follow that response (skip nested grill/sketch — CDD already sketched).
   - Mark `pass #…` (or `skip #why`); update flow note.
6. Keep theme clusters short — one cluster, then check whether views agree.
7. Update **flow**: recommend proceed or more-same-stage; wait for user override if they disagree.
8. When proceeding, deepen fidelity or move scope; keep the `## log`.
