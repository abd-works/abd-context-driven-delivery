---
name: cdd-discovery
description: "Provide guidance for orchestrating CDD stages across stories, ddd, ux, clean_engineering, and bdd."
disable-model-invocation: true
---

# cdd-discovery

Use cdd guidance at `discovery` fidelity only.

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
| **spec** | exploration | tactics | mockup | code | **development** |
| **engineer** | engineering | tactics | — | code | **development** |

UX has no engineering fidelity — production UI follows stories + clean_engineering at **engineer**, honouring the UX spec from **spec**.

### Sketch (one file)

Path: `{session.folder}/cdd-sketch.md` (see `templates/cdd-sketch.md`).

- **One file per engagement** — deepening fidelity (discovery → explore → spec → engineer) updates `fidelity:` at the top and deepens blocks in place. Never create a new file for a new fidelity.
- **Themes** — group lens blocks under one theme (epic, module, user goal, increment, or sub-epic).
- **`order-themes-by-journey`** — When the theme **is** the customer journey / epic, list themes in story-map experience order (Onboarding before Selfcare). Do not follow UX IA / sitemap order.
- **Beside each other** — lens blocks under a theme stay close and comparable; not separate files.
- **Flow** — after each chunk: more at this stage, or proceed. Recommend proceed only when views agree.
- **Trail** — `TODO` → `doing` → `pass #label` (or `skip #why`). Move passes to `## log` as `stage / scope / theme / …`.

### Rules

- **`stage-from-context`** — Infer CDD fidelity from workspace artifacts, sketch, and user intent; confirm when ambiguous.
- **`cdd-owns-grill-sketch`** — Grill and sketch at CDD level. When following a child `tools run`, skip nested child grill/sketch; apply the child generate body only.
- **`views-agree-before-proceed`** — Recommend proceed only when the views in play for the current scope agree; otherwise more at the same stage. User can override.
- **`todo-trail-in-sketch`** — Persist actions as TODO/doing/pass #label in the sketch; archive passes under `## log`.
- **`scaffold-before-content`** — **Hard gate.** Do not write `cdd-sketch.md` (or a file called `sketch.md`) until you have (1) **read** `templates/cdd-sketch.md` and each active child's `sketch_template` from `resolve_targets`, and (2) **AskQuestion** has confirmed which lenses are in play (`confirm-lenses-before-sketch`). Free prose instead of the scaffold is a defect.
- **`order-themes-by-journey`** — When the theme is the customer journey / epic, order themes by the story map / customer experience (Onboarding before Selfcare), not by UX IA.

---

## Templates

Call `load_template` directly with your active format and fidelity:

```python
from context_tools.cdd.cdd import Cdd
Cdd(fidelity="discovery").load_template(format="<your_format>", fidelity="discovery")
```

See examples in `context_tools/cdd/examples/` if needed.