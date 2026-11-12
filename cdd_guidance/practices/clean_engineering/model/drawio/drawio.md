## Overview

Rules for rendering and auditing UML class diagrams in Draw.io under clean engineering. Prefer incremental edits when a `.drawio` already exists, because full regeneration replaces every position a person chose. Pass **`keep_positioning=true`** on `render` / `create_diagram` (or `transform` with `previous` XML) to update class contents in place, leave existing relationship routing, and layout only new classes.

## How the diagram is drawn

`diagram/class_layout.py` draws every class-shaped view, so the Clean Engineering class view and the DDD aggregate view read the same way.

- **Cards fit their text.** Each card is as wide as its longest line, so nothing wraps and the card height stays true.
- **Cards sit on a compact grid.** `CardPlacement` swaps cards on a grid, the way a person tidies a diagram by hand, and keeps the arrangement with the fewest crossings and the shortest arrows. A base stays above what derives from it, an owner above what it owns, and a module's cards together. The search is seeded, so one model always gives one diagram.
- **Arrows are searched, not guessed.** `ArrowRouter` finds each arrow's way across a 10px grid, around every card and every arrow already drawn, then lifts each arrow that still crosses another and searches again with the rest in place. An arrow keeps its own point on the card, and two arrows run at least 20px apart. A crossing costs as much as a 1,500px detour, so a few clean crossings win over a line that circles the page. Each arrow is searched first in a box round its two ends, and over the whole page only when that box holds no way, so a large hand-placed page draws in minutes, not hours. An arrow keeps 20px from other cards when it can; between cards a person placed closer than that, it passes through the gap rather than giving up.
- **Subclasses of one base share a trunk.** All the subclasses of one base arrive on the same side of it, the side most of them face, so the base shows one arrowhead; a subclass on the other side comes round to it. When two or more subclasses reach one base, each drops a short line to a shared horizontal bar and one line with the hollow triangle runs from the bar to one point on the base, the standard UML tree. Each subclass still has its own arrow to the base, so the diagram reads back with every base. A single subclass keeps a direct arrow. When a straight bar would cross a card or run along another arrow, the trunk is searched instead: the subclass nearest the base finds its way to the base, and each other subclass finds its way around the cards until it meets that line and joins it, so the family still ends in one arrowhead.
- **Colour shows the module.** A page holding two or more modules colours each card by its module, so a reader sees where a class lives without a tab per module.
- **Labels name the relationship.** An arrow carries the property it stands for.
- **One arrow per relationship.** A subclass restating its base's field draws no arrow, and two opposite arrows draw only the stronger. A class no field reaches gets one dashed arrow from its first use in an operation, so no card stands alone.

A good diagram comes from a good model: mark each relationship with `<< composition >>`, `<< aggregation >>`, or `<< association >>` and write `Derived : Base` on the class heading, because those are what draw the arrows.

**Scanners** live under `scanners/` (`*_scanner.py`, rule slug = `RULE` / filename). Run them via the Drawio toolset's **scan** / **validate** after every **render**; iterate until hard violations are gone. On failure, **repair** (sub-agent) fixes the layout generator.

---

## Page and hierarchy

A model of up to 40 classes draws on one page, coloured by module, because a reader follows a relationship across modules far more easily on one page than across tabs. A larger model draws one page per module / Key Abstraction (KA): the page name matches the module/KA name, local classes live on that page, and cross-boundary types appear as **imported** cards.

- **`class-title-no-markdown-bold`** — Class titles are plain text inside the HTML `<b>` tag. Do not bake markdown `**name**` into the label; bold is already the `<b>` wrapper. `**Prospect**` displayed inside `<b>` shows the asterisks.
- **`stereotype-above-class-name`** — UML stereotype sits **above** the class name on its own line, italic, not bold. The class name is bold. Do not put `<<Stereotype>>` on the same line as the name inside `<b>`.

### Hierarchy rules

- **`base-above-derived`** — Base and imported ancestor classes sit at higher vertical positions (lower `y`) than their derived classes. Inheritance arrows point **upward** (child → parent). Sibling subtypes share a `y` row side by side below the parent. Do not put a base below its children, and do not flatten grandchild and grandparent onto the same row.
- **`cross-model-ancestors-on-page`** — On a page per module, when a local type extends or uses a type from another module/KA, import the **full ancestor chain** needed to read the ancestry — grandparents included. Imported cards use a **dashed border** and a `«from: Module/KA Name»` stereotype above the class name; show only key properties (enough to recognise the type). Do not render imports as solid local cards, and do not omit a grandparent that explains where the immediate parent comes from.
- **`module-spatial-cohesion`** — Classes of the same module/KA form a tight cluster with short internal edges, and each module has its own card colour. Cross-boundary edges may be longer — that length is the signal. Instance notes sit beside their class inside the cluster. Wrap long edge labels so labels do not sit on boxes.
- **`aggregate-layout-cohesion`** — Cluster an aggregate root with its members and its repository. Do not insert unrelated objects (auth cards) in the gap between a root and its value objects. Repositories sit beside the aggregate they collect.
- **`repository-aggregation-diamond`** — A Repository relates to its aggregate with an aggregation (hollow diamond) and a `<<Repository>>` tag. A repo with no diamond is an unlabeled box, not a collection.
- **`leaf-nodes-not-in-horizontal-row`** — A hub with 4+ leaf neighbours must not place those leaves in one wide horizontal row (same `y`, large `x` span). Fan leaves into multiple rows or a compact cluster.

---

## Edge routing

An edge relates exactly two classes. Routing that cuts a third class, stacks on another edge, or shares a default anchor makes relationships unreadable.

### Routing rules

- **`prefer-short-routes`** — Related classes sit near each other so arrows stay short. Prefer **0–2** explicit waypoints across a short gap. Do not park imports far from the locals they link to, and do not stretch a tall single-column stack when a compact grid would keep ownership edges short. Cross-boundary length is a signal only when two *modules* share one page — on a single-module / per-aggregate page, every edge should be short.
- **`edges-do-not-cross-classes`** — No edge segment may enter the bounding box of any class except its two endpoints. Every edge carries explicit waypoints, because Draw.io's own router ignores other cards on long edges.
- **`edges-do-not-overlap-edges`** — Two orthogonal edges must not share the same column or row for more than ~12px. Keep parallel runs at least 20px apart, and give each edge a unique exit/entry on a shared side. Inheritance edges from several subclasses that end at the same anchor on one base are one shared trunk, drawn as one line, and do not count as overlapping.
- **`edges-do-not-cross-other-edges`** — Transverse crossings (one segment through another) are distinct from collinear overlap, and both hurt readability. A page may keep up to 5 crossings, each at a right angle, because some models cannot be drawn flat and a few clean crossings read better than long detours. More than 5 is a violation.
- **`distinct-anchor-points`** — When two or more edges leave or arrive on the same side of a class, assign explicit `exitX`/`exitY` or `entryX`/`entryY` so paths are visually distinct. Do not leave a shared side on the default center anchor for every edge. Inheritance edges joined into one trunk end at one anchor on their base on purpose, so the base reads as one arrowhead.
- **`edges-approach-perpendicular`** — The first and last segments must hit the exit/entry side head-on (perpendicular), not slide along the class border.

### Audit

- **`run-audit-after-every-render`** — After every generate or layout change, run Drawio **scan** and iterate until done. Priority:
  1. class box overlap → **must be zero**
  2. **`edges-do-not-cross-classes`** → **must be zero**
  3. **`edges-do-not-overlap-edges`** / **`distinct-anchor-points`** → **must be zero**
  4. **`edges-do-not-cross-other-edges`** → **at most 5 on a page**
  5. **`prefer-short-routes`** / **`edges-approach-perpendicular`** → **minimize**

  Do not skip the audit because the layout “looks right” during generation.

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

Reuse clean engineering relationship kinds on Draw.io edges (hollow triangle for inheritance; filled/unfilled diamond for composition/aggregation; open arrow for association). Cardinality and navigability belong on the edge when the source model states them. A dashed open arrow is a use in an operation, not a field. Modules-view diagrams use dependency arrows and containment nesting instead — see `drawio_class_model.py` — not these UML edge styles.
