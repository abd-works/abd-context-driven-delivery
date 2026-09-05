---
name: cdd-engineer
description: "Provide guidance for orchestrating CDD stages across stories, ddd, ux, clean_engineering, and bdd."
disable-model-invocation: true
---

# cdd-engineer

Use cdd guidance at `engineer` fidelity only.

Refer to these skills in order to fill in details from previous fidelities if not present:
@cdd-spec
@cdd-discovery

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

## Sketching

When sketching, use the following sketch template. Do not use the produce templates below — stop reading this skill when sketching.

# CDD sketch — one file, themes, flow, TODO trail

One engagement sketch: `{destination}/.context/cdd-sketch.md`.  
Different sketch types sit **beside each other** under a **theme** — not separate files.

Grill and sketch work **finer** than the stage run scope. AI recommends theme kind and flow; user can override.

---

## Stage run scope (default)

| Stage | Default scope for the run |
|---|---|
| **discovery** | Entire solution, or a large subsection of it |
| **explore** | An increment, or a large subsection of that increment |
| **spec** / **engineer** | About a sub-epic inside the solution / increment |

---

## Theme

A theme is what ties a cluster: **epic**, **module**, **user goal (screens)**, **entire increment**, or any one of those.  
Ask the user which kind for the next cluster; lead with a recommendation from stage + context.

When the theme **is** the customer journey / epic, list themes in **story-map / customer-experience order** (`order-themes-by-journey`) — Onboarding before Selfcare — not UX IA / sitemap order.

Under a theme, include only the concept blocks you are advancing this cycle. When present, prefer order: stories → ddd → ux → clean_engineering → bdd (bdd from explore on).

### Lens blocks — child generator notation only

**Hard rule:** Each lens block (`stories:`, `ddd:`, `ux:`, `ce:`, `bdd:`) MUST be filled using that context’s own `sketch_template` from `resolve_targets` — the same notation the child generator would sketch.

- Call **`resolve_targets`** before writing or revising any lens block. Copy/adapt from that row’s `sketch_template` (and its Example section).
- **Forbidden:** free prose, capability slogans, design notes, or “how we will link” sentences inside a lens block.
- **Allowed outside lens blocks:** `flow`, `theme` labels, `## log`, and short `#` comments under a lens only when they annotate a generator-shaped line.
- If a lens is not in play this cycle, omit the block entirely — do not fill it with prose TODOs.

| Block | Must look like |
|---|---|
| `stories:` | Stories sketch — `{Epic}` / `{Sub-epic}` / `{Actor} --> {Story}` (discovery); full scenario sentences (explore+) |
| `ddd:` | DDD sketch — BC names + aggregates (discovery); typed building blocks (explore+) |
| `ux:` | **discovery/ia:** site map lines only (`└─ [nav] action → Destination`). **explore/mockup+:** ASCII screen boxes with regions, glyphs, verb rows, Stories count, domain terms, and key — from the UX `sketch-template.md`. Site map lines alone are **wrong** at explore depth. |
| `ce:` | clean_engineering sketch — class / property / operation indent notation |
| `bdd:` | BDD sketch — describe/it (explore+) |

---

## Flow

After each chunk, update `flow`: stay at this stage or proceed.  
Recommend **proceed** only when the views in play **agree** (no important contradictions or blockers). Otherwise recommend **more at the same stage**. User may override. Use plain language in `note`.

---

## Action trail (TODO → pass)

Track work so CDD does not lose the thread:

- `TODO` → `doing` → `pass #label` (or `skip #why`)
- Keep active items under `flow.open` / theme blocks
- When a cluster closes, move `pass` lines to bottom `## log` as:  
  `stage / scope / theme / pass #label`

---

## Template

```
fidelity: {discovery|explore|spec|engineer}
scope: {run scope — solution | subsection | increment | sub-epic …}

flow:
  status: {in-progress|ready-to-proceed|more-same-stage}
  recommend: {more-same-stage|ready-to-proceed}   # AI; user may override
  next: {same stage or next stage}
  note: {plain English — views agree / still disagree}
  open:
    - TODO {work}  #{label}
    - doing {work} #{label}
  done:
    - pass #{label}

=========
theme: {name}  ({epic|module|user-goal|increment|sub-epic})
---------
stories:
    {Epic verb-noun}                         # from Stories sketch_template
        {Sub-epic verb-noun}
            {Actor} --> {Story verb-noun}
            * approx N–M more stories …
---
ddd:
    {ContextName}                            # from Ddd sketch_template
      aggregates: {Root}, {Root}
---
ux:
    {Screen}                                 # from Ux sketch_template
      └─ [action] {action} → {Destination}
---
ce:
    {ClassName}                              # from clean_engineering sketch_template
      {propertyOrOperation}
---
bdd:                                         # explore+ only; from Bdd sketch_template
    {describe condition}
        {it behaviour}
=========

## log
- {stage} / {scope} / {theme} / pass #{label}
```

---

## Depth by stage (max fill)

| Stage | Fill |
|---|---|
| **discovery** | Named spine — map, domain names, site map, structural names |
| **explore** | Behaviours, context_tools/aggregates, lo-fi screens, module seams |
| **spec** | Concrete examples, types/stereotypes, hi-fi flow, contracts, BDD signatures |
| **engineer** | Tiers/seams, domain/code notes, BDD development — not full impl in the sketch |

CDD owns only theme grouping, flow, and the TODO/log trail. **Lens content is always the child generator’s sketch language** from `resolve_targets[].sketch_template`.

See examples in `context_tools/cdd/examples/` if needed.