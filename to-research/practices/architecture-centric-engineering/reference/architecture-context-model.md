# Architecture Context Model

The shared model that the five architecture skills (`abd-architecture-outline`, `abd-architecture-blueprint`, `abd-architecture-specification`, `abd-architecture-template`, `abd-architecture-code`) all build on top of. Every skill in this practice family inherits the artefact shape, the tier vocabulary, the discovery flow, and the high-level rules defined here.

The model is named after its central distributed artefact: the per-folder `architecture-context.md`. Centralized documents (outline, blueprint, specification) fan out into the same shared per-folder context files, and every skill — including the code skill — reads from that same distributed layer.

This document is the **canonical source** for these concepts. Skill-level `concepts.md` files reference back to this document instead of restating it.

---

## 1. Centralized documents and distributed context files

The architecture family produces **two layers** of artefact. Every architecture skill in this practice writes into one or both layers.

### Centralized layer — `docs/architecture/`

Three sibling documents, one per skill, all living next to each other at the top of the architecture folder. Each is a *map* for its level of fidelity: it routes the reader and links out, but it does not duplicate the detail that lives behind the links.

| Centralized document | Produced by | Role |
|---|---|---|
| `docs/architecture/architecture-outline.md` | `abd-architecture-outline` | One-page system answer: boundary, systems, mechanisms (tech choices + NFR justifications), guiding principles, ADRs. |
| `docs/architecture/architecture-blueprint.md` | `abd-architecture-blueprint` | Platform runtime, mechanisms as code shapes, module catalogue + dependencies, architecture flow, test tiers. |
| `docs/architecture/specification/architecture-specification.md` | `abd-architecture-specification` | Where-to-Start routing, mechanism index, package index, annotated Source Layout. |

### Distributed layer — `architecture-context.md` next to the code

A single `architecture-context.md` lives in every documented folder, beside the code it describes. The context file is the **shared destination** for all three centralized documents — they all fan into it. One file per folder, regardless of how many centralized documents have something to say about that folder.

```
docs/architecture/
  ├─ architecture-outline.md          ┐
  ├─ architecture-blueprint.md         ├─  centralized maps (sibling documents)
  └─ specification/                    │
      └─ architecture-specification.md ┘
                  │
                  │   each centralized document fans out to …
                  ▼
src/<folder>/architecture-context.md   ←  distributed manuals (one per folder)
src/<other>/architecture-context.md
tests/test-helpers/architecture-context.md
…
```

### Why distributed context files

Context files live with the code so detail stays findable when folders move or get refactored. The three centralized documents stay short and navigable; the per-folder files carry the depth.

> A third class of artefact — the **template package** at `docs/architecture/templates/<slug>/` — sits alongside the two layers described here. It is a runnable scaffold (not a markdown document and not a per-folder manual) produced by `abd-architecture-template` from one specific mechanism-tier context file. See [§ 7](#7-skill-level-handoff-summary) for its place in the family handoff.

### What each centralized document contributes to a context file

A single `architecture-context.md` is the integration point for everything the three centralized documents say about its folder.

| Source | What it contributes to a folder's context file |
|---|---|
| Outline | Which mechanism(s) this folder participates in and the technology choice + NFR justification for each; the ADR(s) that govern those choices. |
| Blueprint | Which module this folder belongs to, the code-shape constraint of any mechanism active here, which test tier exercises it, dependencies to other modules. |
| Specification | File structure, participants, rules, canonical patterns, class specification, "Across the Codebase" cross-references. |

A folder may receive contributions from one, two, or all three centralized documents. The owning skill for each layer's content is named explicitly so a reviewer can trace any line in a context file back to the centralized document that authorised it.

### Reachability is two-way

Each centralized document must link to every context file it fans into; every context file must be reachable from at least one centralized document. The `every-documented-folder-is-reachable-from-central-spec` rule (enforced by the specification skill) is one instance of this property; the same reachability check applies to the outline and blueprint where their content reaches into a per-folder file.

### Skills read the distributed layer for context at their fidelity

Every skill in the family — not just the specification — reads existing `architecture-context.md` files when running against an existing project, picking up signals at its own level of fidelity:

| Skill | Reads from per-folder `architecture-context.md` |
|---|---|
| `abd-architecture-outline` | Mechanism mentions, technology choices recorded in context files, system / boundary signals — to corroborate or correct the outline being authored. |
| `abd-architecture-blueprint` | Module signals, code-shape descriptions, inter-module dependencies, mechanism-module hints — to ground the blueprint in what the code actually does today. |
| `abd-architecture-specification` | Existing tier classifications, file structures, participants, rules — discovery's primary source on existing systems. |
| `abd-architecture-template` | One specific mechanism-tier `architecture-context.md` (File Structure, Participants, Class Specification, Rules, Canonical Patterns) plus the test-helpers package-tier context file — together they fully define the template package contents. |
| `abd-architecture-code` | The full integrated context (mechanism rules + canonical patterns + class spec) for every folder the story touches. |

This is **read-side awareness**, not write-side responsibility, with one opt-in exception: the blueprint skill has an optional `scaffold` mode that *seeds* per-folder `architecture-context.md` files with blueprint-fidelity content (owning module, mechanism code-shape, technology + ADR link, test tier, dependencies) and leaves spec-fidelity slots empty for `abd-architecture-specification` to fill in later. See [`abd-architecture-blueprint` § Optional: scaffold mode](../skills/abd-architecture-blueprint/reference/concepts.md#optional-scaffold-mode). Outside of scaffold mode, every upstream skill scans what exists, treats it as a contributing source, and surfaces conflicts (vocabulary drift, missing mechanisms, dead patterns) the same way it surfaces other architecture violations.

---

## 2. Three tiers of context file

Every `architecture-context.md` is one of three tiers. Classify by **what the folder contains**, not by its name.

| Tier | What it is | Template (in `abd-architecture-specification`) |
|---|---|---|
| **Mechanism** | Reusable pattern; new instances follow a recipe. Activation layer (composition root / framework scan / inherited base) brings instances to life. | [`templates/mechanism-context.md`](../skills/abd-architecture-specification/templates/mechanism-context.md) |
| **Package** | Module with deep functional surface area; no replication recipe. Public seam + internals + lifecycle. | [`templates/package-context.md`](../skills/abd-architecture-specification/templates/package-context.md) |
| **Miscellaneous** | A sentence or two, or a holder for unrelated subfolders / files. Tiny utility, grab-bag, or container. | [`templates/miscellaneous-context.md`](../skills/abd-architecture-specification/templates/miscellaneous-context.md) |

Dead and legacy folders are not a tier — tag them `[dead code]` or `[legacy]` in the central spec's Source Layout.

---

## 3. The vocabulary chain

Names flow downhill. Each skill is the source of truth for the names it introduces, and every downstream skill must use those names verbatim.

```
abd-architecture-outline
  ├─ system names           ┐
  ├─ mechanism names         │
  ├─ mechanism tech choices  │  (source of truth)
  └─ ADRs                    │
                             ▼
abd-architecture-blueprint
  ├─ inherits all of the above verbatim
  ├─ adds module names
  ├─ adds mechanism code-shape constraints
  └─ adds test tier names
                             ▼
abd-architecture-specification
  ├─ inherits all of the above verbatim
  ├─ adds per-folder context files (file structure, participants, rules, canonical patterns)
  └─ adds Where-to-Start routing
                             ▼
abd-architecture-template
  ├─ inherits all of the above verbatim (placeholder vocabulary copied from Canonical Patterns)
  └─ adds runnable scaffold (template/, templates/tests/, example/, rules/, parameters.json)
                             ▼
abd-architecture-code
  └─ inherits all of the above verbatim; instantiates the template package's patterns for stories
```

**The contract:** if a downstream skill needs to rename or invent a name, the rename happens in the highest skill that owns it (and any associated ADR is updated), then it propagates down. Discovery surfacing a missing mechanism is an outline / blueprint update — never a quiet spec-level invention.

The enforcing rule, applied by the specification skill: [`vocabulary-matches-source-of-truth`](../skills/abd-architecture-specification/rules/vocabulary-matches-source-of-truth.md).

---

## 4. Existing system vs new system — same procedure, different Step 1

The full discovery procedure lives in [`abd-architecture-specification/reference/discovery.md`](../skills/abd-architecture-specification/reference/discovery.md). The outcome is always the same: a complete folder tree, a classification table, a context file per documented folder, and a Source Layout. Only **where the tree comes from** changes.

| Situation | Where the tree comes from | What "discovery" reads |
|---|---|---|
| **Existing codebase** | Recursively enumerate what is on disk. | The code itself — entry point, activation layer, repetition, consumers. |
| **New system** | Design the intended tree before code exists. | Blueprint, outline, domain spec, story map — which patterns will repeat, which packages are planned, where folders should live. |

For a **new system**, the documentation comes first: name mechanisms and packages, pick folder paths, write context files and Source Layout **in advance of any code**. A common greenfield four-step is:

1. **`abd-architecture-blueprint` mode: `scaffold`** seeds the folder skeleton and stub `architecture-context.md` files carrying blueprint-fidelity content (no source code).
2. **`abd-architecture-specification` mode: `document`** fills the spec-fidelity slots (File Structure, Participants, Class Specification, Rules, Canonical Patterns) inside those stubs and authors the central spec.
3. **`abd-architecture-template` mode: `project`** (or `mechanism` for multi-mechanism projects) produces a runnable parameterized reference module at `docs/architecture/templates/<slug>/` — `template/`, `templates/tests/`, `example/`, `rules/`, `parameters.json` — embodying the spec's design as working code.
4. **`abd-architecture-code`** resolves the template package for the mechanism in scope, copies-and-renames it per feature, and writes per-story tests and production code.

Scaffolding does not invent structure — each step implements what the step above it already describes.

For an **existing codebase**, documentation mode means walk the code and update stale docs. Code-mode work then follows the spec that already exists on disk.

---

## 5. Where mechanism-tier context files land

The *mechanism tier* classification (one of the three tiers in [§ 2](#2-three-tiers-of-context-file)) applies to the `architecture-context.md` in the folder that **hosts the templated pattern** — the folder a new instance is added inside. Examples:

| Mechanism | Folder whose `architecture-context.md` is mechanism-tier |
|---|---|
| Partner Integrations | `src/integrations/` (each `{Partner}/` is an instance) |
| Identity Setup | `src/setup/Identity/` (each protected area copies the skeleton) |
| Typed Failure Pipeline | `src/shared/errors/` (every inbound handler uses it) |
| Test Helpers | `tests/test-helpers/` (every story extends the fixture skeleton) |

A mechanism that also has a concrete module surface (e.g. Security → Identity module, App Server → Bootstrap module) gets a mechanism-tier file in its host folder *and* a separate package-tier file for its public surface. The blueprint's **mechanism-modules** section flags these.

Because the per-folder context file is shared across the family ([§ 1](#1-centralized-documents-and-distributed-context-files)), a mechanism-tier file at `src/integrations/architecture-context.md` carries blueprint code-shape detail and outline mechanism ADR links alongside the specification's File Structure / Participants / Rules / Canonical Pattern sections — all in one file.

---

## 6. Higher-level rules (apply across the skill family)

These four rules are not mechanical formatting checks — they are properties of a healthy architecture context model that every skill in this family must respect.

### 6.1 Vocabulary matches the source of truth

Every architecture artefact uses the names introduced by the artefact above it in the vocabulary chain (§ 3) verbatim. Synonyms, casing drift, and locally invented names break traceability across documents.

→ Enforced in spec output by [`vocabulary-matches-source-of-truth`](../skills/abd-architecture-specification/rules/vocabulary-matches-source-of-truth.md). The blueprint and outline producers must hand mechanism names down unchanged; the code skill must hand them through to generated code symbols.

### 6.2 A mechanism is a code-shape constraint, not a technology choice

The outline records the **technology choice** for each mechanism (with NFR justification and an ADR). The blueprint, the specification, and the code skill all describe the **code shape every module must adopt** to participate in the mechanism. The two are not the same. "We use Redis" is a tech choice. "Every cache key follows `{tenant}:{entity}:{id}`, every cache miss falls through to the source-of-truth repository, every write invalidates the matching key" is the code-shape constraint.

→ Definition: [`architecture-mechanism.md`](./architecture-mechanism.md). Enforced in spec output by [`mechanism-pattern-is-coherent-across-instances`](../skills/abd-architecture-specification/rules/mechanism-pattern-is-coherent-across-instances.md) and [`mechanism-rules-are-code-verifiable`](../skills/abd-architecture-specification/rules/mechanism-rules-are-code-verifiable.md).

### 6.3 A package seam is minimal and named

Wherever a package's public surface is described — blueprint mechanism-modules section, spec package-tier context file, code generated for a package — the surface is a short named list of operations consumers actually call. Deep functionality lives behind it. A package that exports every internal helper has a fictional seam; a package that one-to-one re-exports a third-party SDK is shallow and adds no architecture.

→ Enforced in spec output by [`package-seam-is-minimal-and-named`](../skills/abd-architecture-specification/rules/package-seam-is-minimal-and-named.md). Honored by the code skill when generating module exports.

### 6.4 Discover before authoring

Before writing or generating any architecture artefact, complete the discovery procedure in [`abd-architecture-specification/reference/discovery.md`](../skills/abd-architecture-specification/reference/discovery.md). On an existing codebase, "discovery" means walking the code. On a new system, "discovery" means designing the planned tree and classifying its planned folders. "I already know the codebase" is not discovery — it is remembering. "No code exists yet" is not an excuse — design the tree first.

→ Applies to every skill in the family. The outline and blueprint discover the system as a whole; the spec discovers each folder; the code skill discovers the context model it must implement.

---

## 7. Skill-level handoff summary

Each skill writes into the centralized document it owns *and* contributes its layer of content to the per-folder `architecture-context.md` files for every folder its content touches. Downstream skills inherit both the upstream centralized document and the upstream contributions already present in those context files. The template skill writes a third kind of artefact — a runnable scaffold package — that the code skill consumes.

| Skill | Writes centralized | Contributes to per-folder `architecture-context.md` | Writes template package |
|---|---|---|---|
| `abd-architecture-outline` | `architecture-outline.md` | For each folder participating in a mechanism: mechanism name(s), technology choice, NFR justification, ADR link. *Read-only today; lands via blueprint scaffold or via specification.* | — |
| `abd-architecture-blueprint` | `architecture-blueprint.md` | For each folder: owning module, code-shape constraint for any mechanism active here, test tier, inter-module dependencies. **Writes** when running in `mode: scaffold` (opt-in) — seeds stubs with blueprint-fidelity content and leaves spec-fidelity slots empty. Read-only in default `mode: blueprint`. | — |
| `abd-architecture-specification` | `architecture-specification.md` (central) | **Writes** for each folder: file structure, participants, rules, canonical pattern, class specification, "Across the Codebase". When a blueprint-scaffolded stub already exists, fills the empty spec-fidelity slots and preserves blueprint-fidelity content as-is. | — |
| `abd-architecture-template` | — | Read-only. Consumes one specific mechanism-tier context file + the test-helpers package-tier context file. | **Writes** `docs/architecture/templates/<slug>/` — `template/`, `templates/tests/`, `example/`, `rules/`, `parameters.json`, `README.md`. One package in `project` mode; many in `mechanism` mode. |
| `abd-architecture-code` | — | Does not produce architecture documentation. Reads all three centralized documents and the relevant per-folder context files; generates code that conforms to them. | Read-only. Resolves the template package for the mechanism in scope and copies-and-renames it per feature. |

Inheritance is transitive — `abd-architecture-code` reads outline, blueprint, *and* spec, plus the per-folder context files that integrate all three, plus the relevant template package, all using the same vocabulary ([§ 3](#3-the-vocabulary-chain)).
