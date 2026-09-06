---
catalog_garden_tier: practice
catalog_garden_order: 40
name: abd-architecture-specification
catalogue_one_liner: >-
  Tell engineers exactly how domain concepts become files, classes, and tests in a chosen stack.
description: >-
  Specify how domain concepts and stories map to files, classes, and tests in a chosen stack. Use when starting or extending an architecture spec for a project.
context-perspective: architecture
context-fidelity:
  - level: exploration
    mode: document
---
# abd-architecture-specification

## Purpose

Produce a short, navigable `architecture-specification.md` that routes a developer or AI to the right per-folder `architecture-context.md` for any feature they are about to build — and the per-folder context files themselves. Detail lives next to code, not in the central spec.

---

## Output shape

Two kinds of artefact:

1. **`src/architecture-context.md`** — the central document. Short. Lives at the root of `src/`. Grows through outline → blueprint → specification fidelity in place. Acts as a navigation hub via a `## Where to Start` table. Names every mechanism in one line + link, lists every documented package in one line + link (categorised), and shows an annotated source tree.
2. **`{folder}/architecture-context.md`** — one per folder that has documentation worth keeping. Three tiers; pick the one that matches the folder:

| Tier | When | Template |
|---|---|---|
| **Mechanism** | folder hosts a templated pattern other features will copy (e.g. replicated feature modules, shared bootstrap setup) | [`templates/mechanism-context.md`](templates/mechanism-context.md) |
| **Package** | folder is a functional area with real surface area (multiple methods, named consumers) but is not a templated recipe (e.g. a third-party SDK wrapper) | [`templates/package-context.md`](templates/package-context.md) |
| **Miscellaneous** | folder is tiny (one-class singleton) or a grab-bag of unrelated utilities | [`templates/miscellaneous-context.md`](templates/miscellaneous-context.md) |

---

## Agent Instructions

**MANDATORY:** [`common/reference/skill-workflow.md`](../../../../common/reference/skill-workflow.md) — read in full; complete § Bootstrap and § Read-gates before generating or validating.

## Bootstrap

§ Bootstrap — [`common/reference/skill-workflow.md`](../../../../common/reference/skill-workflow.md).

## Read

§ Read-gates — read all of these before authoring:

- **[`reference/concepts.md`](reference/concepts.md)** — the conceptual model: two-artefact output, central-spec shape, three tiers, boundaries.
- **[`reference/discovery.md`](reference/discovery.md)** — mandatory before any new or refreshed spec. Existing: recursive tree walk. New: design tree from blueprint/stories, classify planned folders. Same decision tree either way.
- **[`reference/generate.md`](reference/generate.md)** — the discovery → classify → author → validate workflow in detail.
- **[`reference/input-traps.md`](reference/input-traps.md)** — pre-flight checklist; flag what is missing before authoring.
- **[`reference/grill-me.md`](reference/grill-me.md)** — interview questions when classification is ambiguous. Mechanics: [`common/reference/grill-me-with-practice-skill.md`](../../../../common/reference/grill-me-with-practice-skill.md).
- **[`reference/testing-architecture.md`](reference/testing-architecture.md)** — what goes in the test-helpers context file (layer-to-tech mapping, folder structure, spec-alignment table, principles) and the one-paragraph pointer rule for the central spec.
- **[`reference/diagram-workflow.md`](reference/diagram-workflow.md)** — where diagrams live (mermaid in mechanism-tier context files; no inline diagrams in the central spec).
- **[`reference/examples.md`](reference/examples.md)** — pointers into the golden fixture for each tier.
- **All files in [`rules/`](rules/)** — every rule has DO / DO NOT examples; the rule set is the contract.
- **All files in [`templates/`](templates/)** — central spec + three context-file tiers.
- **[`eval/pass/golden-spec/`](eval/pass/golden-spec/)** — complete worked example for the `pml-midtier` codebase.

## Generate

1. **Discover.** Follow [`reference/discovery.md`](reference/discovery.md): walk the tree (existing) or design and classify the intended tree (new). Build the classification table.
2. **Update what's needed.** Create or refresh context files and the central spec wherever discovery shows they are stale, missing, or wrong. On greenfield, documentation mode may be the complete deliverable; code mode scaffolds later via [`abd-architecture-code`](../../abd-architecture-code/).
3. **Author context files before the central spec.** For each folder that needs documentation, start from the matching template ([`templates/mechanism-context.md`](templates/mechanism-context.md), [`templates/package-context.md`](templates/package-context.md), [`templates/miscellaneous-context.md`](templates/miscellaneous-context.md)) and place the file as `<folder>/architecture-context.md`.
4. **Author the central spec.** Start from [`templates/architecture-specification.md`](templates/architecture-specification.md). Fill in: Where to Start table, Overview (≤2 paragraphs, no principle list), Mechanisms one-liners, Package Context categories listing every context file, Source Layout tree with mechanism / `[dead code]` / `[legacy]` tags, Testing pointer paragraph.
5. **Link discipline.** Workspace-root paths (`/src/...`) only; no `../../../`; no backticks wrapping any link.

## Validate

Run every rule in [`rules/`](rules/) against the produced artefacts. Each rule names what passes and what fails with examples. The fixture suite in [`eval/`](eval/) — golden pass + one fail fixture per rule — is the regression target.

`eval/cases.json` registers what each fixture is expected to produce. Scanners are not yet implemented; the cases file is the declarative target for when they are.

## Repair

When an output is found wrong (by user, by scanner, or by reviewer), follow [`common/reference/manual-repair-loop.md`](../../../../common/reference/manual-repair-loop.md) (or the agentic equivalent) to capture the bad artefact under `eval/fail/<slug>/`, the corrected one under `eval/pass/<slug>/`, and update `eval/cases.json`.
