---
name: stories-story_map
description: "Provide guidance for creating story maps, scenarios, and acceptance tests."
disable-model-invocation: true
---

# stories-story_map

Use stories guidance at `story_map` fidelity only.

# Contexts

Map stakeholder and system interactions as behaviours that deliver a solution.

Interactions fit into a hierarchy: a `StoryMap` of `Epic` → nestable `SubEpic` → `Story`. Each story is `Scenario`s with discrete steps; backgrounds and scenarios carry examples.

| Fidelity | Default Format | Produce |
|---|---|---|
| **story_map** | markdown | Story map |
| **scenarios** | python | Main-flow scenarios per story — `{story}.{tier}.py` GWT files. Pass `format markdown` only when the strategy asks for a markdown view. |
| **acceptance_tests** | python | Same `{story}.{tier}.py` tree as scenarios. CE runs alongside for wrap classes. |

**Templates** live under `templates/` per format. **Scanners** read the canonical model only — never language syntax.

---

## Shared rules

- **`vocabulary-traces-to-domain-source`** — Trace terms to domain language / model when present.
- **`artifacts-mirror-story-hierarchy`** — Mirror Epic → SubEpic → Story on disk as folders for epic and sub-epic, and as `{story}.{tier}.py` files (no per-story directory).
- **`kebab-case-paths`** — Epic and SubEpic **folder** names, story **file** stems, and tier segments use lowercase kebab-case (`sign-up`, `front-end`). No `snake_case` folders or `PascalCase` paths. **Exception:** Python epic helper only — `{epic_slug}_helper.py` at the epic folder root; nothing else may use underscores.
- **`read-all-source-context-in-full`** — Before locking hierarchy **and before any grill/iterate question about a seam**, prove-read **every relevant referenced context** for that decision: owning `*-segment.md`, `module-context.md`, session sketches / grill-answers / handoff, peer story-context, build-order, and any path the plan or prior answers cite. Index / mid-epic stub columns are structure hints only — **not** story inventory. Grep or primer-only skims do not count; cite concrete terms from the files read in the question turn. Also re-read these rules. Do not thin from titles or memory!
- **`do-not-invent-requirements`** — Only model behaviours present in source context or an explicit ask. Never invent:
  - status concepts, maintenance signals, warning badges, or config columns (e.g. `Status (ok/stale)`) the source does not require — unconfigured / not-yet-current = **no row** + the existing fallback, never a new invented state to render;
  - a second, competing command / invoke surface beside one the user already specified (e.g. a raw YAML `toolset`/`fidelity`/`action` "Invoke" block given equal billing next to an already-locked `/{skill} <action> {fidelity}` line). Keep the specified surface primary; any secondary format is a subsidiary link at most — never inlined, never a co-equal page element.

---

## story_map

**Default format:** markdown

**Goal:** Shape the hierarchy — `Epic` → nestable `SubEpic` → `Story` — decomposed on real mechanical variation, not requirement-row bookkeeping.

**Produce:** Story map.

### Scaffold

**When scaffolding only** (`/partition` or a names-only first cut — not full generate at this fidelity): follow this subsection. Do not use ### Rules below, ## Sketching, or ## Templates. **Stop reading this skill when scaffolding.**

Rough story-map outline for a **partition** pass or first cut — **names only**: verb–noun epics + story names (`StoryMap` → `Epic` → `SubEpic` → `Story`). No scenarios, no thin-slice increments, no scope prose yet.

Key rules: `branch-on-mechanical-uniqueness` — split on distinct mechanics, not catalog/requirements rows; `read-all-source-context-in-full` — read segments in full before grouping.

### Rules

- **`verb-noun-format`** — Name Epic / SubEpic / Story verb–noun; actor is metadata; base verb form.
- **`four-to-nine-children`** — 4–9 direct children (warn at 3/10; error ≤2 or ≥11).
- **`branch-on-mechanical-uniqueness`** — Explore context relentlessly for distinct mechanics. Branch on mechanical uniqueness, dstinct mechanics in requirements require *distinct stories* for each mechanic. Different requirement entries with same mechanic is *one story only with different examples or scenarios*. Collapsing real mechanical variation, as well as mindlessly turning requirements into long lists of stories are **defect**
- **`right-size-story-nodes`** — One demonstrable interaction per story.
- **`behaviours-not-one-time-tasks`** — A Story is a repeatable stakeholder/system interaction you can specify Given/When/Then against more than once. One-time maintainer chores (rename X to Y, copy/migrate an asset once, one-off repo surgery) are not Stories — keep them in the plan/todos. Once done, the result is ordinary inventory the remaining stories already cover.
- **`do-not-invent-requirements`** — same rule as Shared: no invented Status/stale/warning-badge concepts; no competing command/invoke surface beside one already specified; unconfigured = no row + existing fallback.

---

## Sketching

When sketching, use the following sketch template. Do not use the produce templates below — stop reading this skill when sketching.

# Stories sketch — match active fidelity

**MUST:** Read all source context in full before drafting or refining. **MUST:** Branch on **mechanical uniqueness** only — split distinct mechanics; do not mint one story per TOC / catalog / requirements row. **MUST:** Do not invent requirements — no Status/stale/warning-badge stories or columns unless source already requires them; no second command/invoke surface beside one already specified (no co-equal YAML Invoke block next to a locked `/{skill} <action> {fidelity}` line — secondary formats are a subsidiary link only). Unconfigured = no row + existing fallback. See `stories.md`: `read-all-source-context-in-full`, `branch-on-mechanical-uniqueness`, `do-not-invent-requirements`.

Sketch the story hierarchy first, then deepen only as far as the active fidelity needs. Confirm epics and sub-epics (the e2e journey), then drill into exact stories by risk or uncertainty — unique **mechanical** flows first, then scaffold patterns already encountered.

Sketch increments next if there will be more than one.

Then detail groups of related stories together — e.g. stories for a sub-epic in a particular increment. Narrate in e2e flow order.

When detailing stories, start with the main-flow scenario (including domain objects usable for examples); then other scenarios, real example data, etc. Given names only conditions the running system actually checks. When is the domain operation. Then asserts; further outcomes are `And` / `.and()`.

**Unmapped areas** live here as `* approx N–M stories…` lines — not in a separate outline map. Discovery materializes named stories; drop approx lines once those stories are named on the real map.

**Order:** epics → sub-epics → confirming stories + approx gaps → thin-slice order → main-flow scenario → variations / shared setup (`specification`) → tier notes (`engineering` only).

Do **not** tag lines with fidelity markers. Depth is what you fill:

| Fidelity | Fill |
|---|---|
| **discovery** | Epic / SubEpic / named stories + thin-slice; clear approx gaps as you name stories |
| **exploration** | Main-flow Given / When / Then under each confirming story; objects from ExampleFactory fakes; assert public interface. No shared background yet. |
| **specification** | Extra scenarios, shared setup / background; still fake + public interface; values from factories |
| **engineering** | Which tier(s) (`domain` / `client` / `server` / `e2e` / project-specific); not full impl in the sketch |

**Notation:** indent = nesting · `{Actor} --> {Verb Noun}` story · `* approx N–M …` unmapped · `~>` increment · `//` note.

---

## Template

```
{Epic verb-noun}
    * approx N–M total stories
    {Sub-epic verb-noun}
        {Actor} --> {Confirming story verb-noun}
            given {shared setup}                    // specification only
            {main scenario name}
                given {precondition the running system actually checks}
                    and {precondition with object.object.field}
                    and …
                when {the domain operation}
                    and …
                then {observable outcome {object.field=descriptive term}}
                    and {next observable outcome}
            {next scenario name}                    // specification only
                …
        {Actor} --> {Confirming story verb-noun}
        * approx N–M more stories (what unmapped work likely includes)
    {Sub-epic verb-noun}
        * approx N–M more stories (what unmapped work likely includes)
~> Increment 1: {capability outcome}: {Story verb-noun}, {Story verb-noun}, …
```

---

## Example

```
Manage Customer Orders
    * approx 18-22 total stories
    Place New Order
        Customer --> Browse Product Catalog
            browse catalog shows available products
                given a Catalog with published Products
                    and a Customer with an empty Cart
                when the Customer browses the Catalog
                then available Products are listed with price
                    and Product.name and Product.price are shown
        Customer --> Submit Order
            given a Cart with line items and a Payment Method   // specification only
            order accepted for valid cart and payment
                given a Cart with Items totalling amount.currency
                    and a Payment Method with status authorised
                when the Customer submits the Order
                then an Order is created with status placed
                    and an Order.number is returned
            order rejected when payment declined                // specification only
                given a Cart with Items totalling amount.currency
                    and a Payment Method with status declined
                when the Customer submits the Order
                then the Order is rejected with reason payment_declined
                    and the Cart contents are preserved
        * approx 4-5 more stories (cart, address, delivery, review)
    Track Order Status
        * approx 3-4 more stories (pending, shipped, delivered)
    Cancel Order
        Customer --> Request Order Cancellation
        * approx 2-3 more stories (refund, partial cancel, policy)
~> Increment 1: Customer can place a paid order: Browse Product Catalog, Submit Order
```

## Templates

### markdown

## story-map.md

---
fidelity: [discovery]
artifact: [story-map]
format: md
section: body
---

<!-- Discovery fidelity — every sub-epic decomposed to named stories.
     Do not wrap epic, sub-epic, story, or actor names in backticks. -->

# Story Map — Product / Feature Name

**Sources / context:** context files used

---

(E) Epic Verb–Noun
    (E) Sub-Epic Verb–Noun
        (S) Actor --> Story Verb–Noun
        (S) Actor --> Story Verb–Noun
    (E) Sub-Epic Verb–Noun
        (S) Actor --> Story Verb–Noun

---

## Scope boundary

**In scope:** what is included
**Out of scope:** what is explicitly excluded

See examples in `context_tools/stories/examples/` if needed.