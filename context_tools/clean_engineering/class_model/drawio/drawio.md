# Contexts

Rules for rendering and auditing UML class diagrams in Draw.io under clean engineering. Layout is a judgment call constrained by these rules — not a script dump. Prefer incremental edits when a `.drawio` already exists; full regeneration destroys manual positioning. Pass **`keep_positioning=true`** on `render` / `create_diagram` (or `transform` with `previous` XML) to update class contents in place, leave existing relationship routing, and layout only new classes.

**Scanners** live under `scanners/` (`*_scanner.py`, rule slug = `RULE` / filename). Run them via the Drawio kit **scan** / **validate** after every **render**; iterate until hard violations are gone. On failure, **repair** (sub-agent) fixes the layout generator.

---

## Page and hierarchy

One page per module / Key Abstraction (KA). Page name matches the module/KA name. Local classes live on that page; cross-boundary types appear as **imported** cards at the top.

### Hierarchy rules

- **`base-above-derived`** — Base and imported ancestor classes sit at higher vertical positions (lower `y`) than their derived classes. Inheritance arrows point **upward** (child → parent). Sibling subtypes share a `y` row side by side below the parent. Do not put a base below its children, and do not flatten grandchild and grandparent onto the same row.
- **`cross-model-ancestors-on-page`** — When a local type extends or uses a type from another module/KA, import the **full ancestor chain** needed to read the ancestry — grandparents included — at the top of the page. Imported cards use a **dashed border** and a `«from: Module/KA Name»` stereotype above the class name; show only key properties (enough to recognise the type). Do not render imports as solid local cards, and do not omit a grandparent that explains where the immediate parent comes from.
- **`module-spatial-cohesion`** — Classes of the same module/KA form a tight cluster (short internal edges). Different modules/KAs on the same page sit with a clear gap (~200px+). Cross-boundary edges may be longer — that length is the signal. Instance notes sit beside their class inside the cluster, not in the gap. On multi-module pages, if mental bounding boxes overlap, reposition until they separate. A single-module page satisfies cohesion by default — still avoid scattering classes unnecessarily far apart.
- **`leaf-nodes-not-in-horizontal-row`** — A hub with 4+ leaf neighbours must not place those leaves in one wide horizontal row (same `y`, large `x` span). Fan leaves into multiple rows or a compact cluster.

---

## Edge routing

An edge relates exactly two classes. Routing that cuts a third class, stacks on another edge, or shares a default anchor makes relationships unreadable.

### Routing rules

- **`edges-do-not-cross-classes`** — No edge segment may enter the bounding box of any class except its two endpoints. Prefer exit/entry sides that keep obstacles off the direct path; otherwise add explicit waypoints so the edge dog-legs around the obstacle. Do not rely on Draw.io’s auto-router for long inheritance edges across siblings.
- **`edges-do-not-overlap-edges`** — Two orthogonal edges must not share the same column or row for more than ~12px. Spread parallel runs ~20–40px apart with waypoints, and give each edge a unique exit/entry on a shared side.
- **`edges-do-not-cross-other-edges`** — Transverse crossings (one segment through another) are distinct from collinear overlap — both fail readability; crossings are definitive.
- **`distinct-anchor-points`** — When two or more edges leave or arrive on the same side of a class, assign explicit `exitX`/`exitY` or `entryX`/`entryY` so paths are visually distinct. Do not leave a shared side on the default center anchor for every edge.
- **`edges-approach-perpendicular`** — The first and last segments must hit the exit/entry side head-on (perpendicular), not slide along the class border.

### Audit

- **`run-audit-after-every-render`** — After every generate or layout change, run Drawio **scan** / `audit_diagram_report` and iterate until done. Priority:
  1. class box overlap → **must be zero**
  2. **`edges-do-not-cross-classes`** → **must be zero**
  3. **`edges-do-not-overlap-edges`** / **`edges-do-not-cross-other-edges`** → **minimize** / definitive
  4. **`distinct-anchor-points`** / **`edges-approach-perpendicular`** → **minimize**

  Use orthogonal inheritance routing when a subtype is not directly under its parent. Do not skip the audit because the layout “looks right” during generation.

---

## Domain Language → diagram

When the source is a Domain Language file (`*-domain-language.md`, `state: domain-language`), the diagram uses the same card / row / collaborator shape as a domain model, but structure comes from prose, not typed blocks.

| ULL element | Diagram element |
|---|---|
| `## KAName` / module heading | One page named exactly that |
| `### concept_name` | One class card |
| Verb-led behavior bullet | One row: `<bullet text> : <Collaborator>, …` |
| `*italicized*` terms in a bullet | Collaborator list on that row |
| `**Invariant:** …` bullet | Row in the invariant compartment |
| `### Subtype *is a type of* Base` | Inheritance edge child → parent |
| Stub whose first bullet is `is a property of *parent*` | Property row on parent, or lightweight stub with `«property of: Parent»` |
| `### term *(boundary)*` | Imported dashed card with `«boundary: OwningModule»` |
| Parenthetical primitive (e.g. `(integer)`) | Inline value on the row — no separate card |

### Mapping rules

- **`ull-bullets-become-rows`** — One card per `### concept`, one row per behavior bullet (italic markers stripped; collaborators = italicized terms). Fold duplicate cross-concept references into **one** association edge. Inheritance comes only from `*is a type of*` headings — do not also draw an association to the base for inherited behavior. Boundary stubs are dashed imports; property stubs are a parent row or a `«property of: …»` stub. Do not drop bullets, italic terms, or invariants; do not invent type annotations the source lacks; do not emit one edge per bullet hit; do not treat italic terms inside `**Invariant:**` lines as association edges (invariants never produce edges).

**Notes**

- Italicized terms must already resolve to named concepts in the Domain Language source — fix unresolved italics upstream; do not invent cards here.
- Domain Language sync-to-model is one-way for **new/deleted concepts** only. Bullet text does not round-trip; prose in markdown remains authoritative.

---

## Relationship notation (class view)

Reuse clean engineering relationship kinds on Draw.io edges (hollow triangle for inheritance; filled/unfilled diamond for composition/aggregation; open arrow for association). Cardinality and navigability belong on the edge when the source model states them. Modules-view diagrams use dependency arrows and containment nesting instead — see `drawio_class_model.py` — not these UML edge styles.
