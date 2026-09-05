# Concepts -- abd-architecture-specification

> **The shared model — centralized documents + distributed per-folder context files, three tiers, the vocabulary chain, the existing-vs-new flow, the read-side scan of distributed context, and the higher-level rules — is canonicalised at the practice level:** [`practices/architecture-centric-engineering/reference/architecture-context-model.md`](../../../reference/architecture-context-model.md). This skill's concepts page restates what the spec skill specifically owns and adds the "what good looks like" criteria backed by the rules under [`../rules/`](../rules/).

## Two artefacts

1. **Central `architecture-specification.md`** at `docs/architecture/specification/architecture-specification.md`. A map: routing table, one-line summaries, folder indexes, annotated source tree. It links out; it does not explain.
2. **Per-folder `architecture-context.md`** next to the code. The manuals: file structure, participants, rules, diagrams, canonical patterns.

Co-locate context files with the code they describe so detail stays findable when folders move or get refactored.

## Central spec

Section layout and placeholders: [../templates/architecture-specification.md](../templates/architecture-specification.md). Constraints: [../rules/](../rules/).

## Three tiers

Pick from what the folder contains, not its name.

| Tier | What it is | Template |
|---|---|---|
| **Mechanism** | Reusable pattern; new instances follow a recipe. | [templates/mechanism-context.md](../templates/mechanism-context.md) |
| **Package** | Module with deep functional surface area; no replication recipe. | [templates/package-context.md](../templates/package-context.md) |
| **Miscellaneous** | A sentence or two, or a holder for unrelated subfolders/files. | [templates/miscellaneous-context.md](../templates/miscellaneous-context.md) |

## Vocabulary

Mechanism names, layer names, and system names must match the architecture's agreed source of truth (ADRs, blueprint, outline). Update the source of truth before introducing a new name in the spec.

## Boundary

The central spec is not a blueprint, outline, domain specification, or code-generation manual. Link to those artefacts; do not copy their content into this skill's output.

Package-tier context files describe architecture seams, not domain invariants ? those belong in `abd-domain-specification`.

## What good looks like

The structure above is necessary but not sufficient. A two-artefact spec with the right tiers can still be bad documentation if the units inside it are poorly formed. Each criterion below has an enforcing rule in [`../rules/`](../rules/).

### Good mechanism

- **Pattern coherence across instances.** Every instance follows the same canonical shape ? same file skeleton, same extension points, same wiring contract. A mechanism may legitimately span several responsibilities (request lifecycle: validate + route + translate; identity setup: authenticate + authorise + refresh) so long as every instance does them the same way. The test is shape consistency, not responsibility count. ? [mechanism-pattern-is-coherent-across-instances](../rules/mechanism-pattern-is-coherent-across-instances.md)
- **Activation path named.** The context file names how a new instance becomes live ? composition-root registration, base-class inheritance + consumer usage, file-glob discovery, or decorator-driven scanning. The reader can answer "what makes this code run?" without reading existing instances. ? [mechanism-activation-path-is-named](../rules/mechanism-activation-path-is-named.md)
- **Parameters obvious from the pattern.** The Participants and Canonical Patterns use placeholders (`{Partner}`, `{System}`) so a reader can see what varies per instance and what stays fixed. An explicit "Adding a new instance" recipe is optional and only needed when extension touches files outside the mechanism folder. ? [mechanism-parameters-are-obvious-from-the-pattern](../rules/mechanism-parameters-are-obvious-from-the-pattern.md)
- **Rules that can fail a review.** Every bullet in the Rules section names a must / must-never with a code-visible violation. Sentiments ("strive for", "prefer") are not rules. ? [mechanism-rules-are-code-verifiable](../rules/mechanism-rules-are-code-verifiable.md)

### Good package

- **Cohesive surface.** Operations share one subject ? the same concept, the same external system, the same capability. Junk drawers get reclassified as miscellaneous. ? [package-surface-is-cohesive](../rules/package-surface-is-cohesive.md)
- **Minimal seam, deep functionality.** The package's *public surface* is a short named list; the *functionality behind it* is substantial. Shallow packages (one-line wrappers around an SDK) and bloated public surfaces (every helper exported) both fail this property. ? [package-seam-is-minimal-and-named](../rules/package-seam-is-minimal-and-named.md)
- **Named consumers.** Anonymous packages ("used across the codebase") are unmaintainable; consumers are listed by file path.
- **Documents the package, not the domain.** The context file covers public surface AND internals (lifecycle, helpers, wiring) ? anyone modifying the package needs them. What it stays out of is domain rules: business invariants, state machines, and validation policies live in `abd-domain-specification`. ? [package-context-file-stays-out-of-domain-details](../rules/package-context-file-stays-out-of-domain-details.md)

### Good interactions between packages

- **One direction of dependency per pair.** Cycles are seams in disguise ? break them with a third package or an event.
- **Calls cross documented seams, not internals.** A consumer that reaches into another package's private files is coupled to its implementation; both packages now refactor together.
- **Packages don't construct each other.** Collaborators are received, not instantiated ? through a composition root, framework auto-wiring, or a documented inheritance contract. Keeps the seam testable and the package replaceable.
- **Failure shapes are uniform across the seam.** A package's errors are part of its surface; consumers translate at one point, not at every call site.

### Good system-level structure

- **Boundary stated both ways.** The Overview names what the system owns AND what it explicitly does not ? the negative half is what stops scope creep. ? [overview-names-system-boundary](../rules/overview-names-system-boundary.md)
- **One vocabulary.** Mechanism, layer, and system names match the agreed source of truth (ADRs, blueprint) verbatim. ? [vocabulary-matches-source-of-truth](../rules/vocabulary-matches-source-of-truth.md)
- **Live distinguishable from dead.** Every shown folder is tagged with its owning unit or marked `[dead code]` / `[legacy]`; a reader can tell what is reachable from the system's entry point. ? [live-and-dead-code-are-distinguished](../rules/live-and-dead-code-are-distinguished.md)
- **Every documented unit is reachable.** A context file that the central spec does not index is invisible; the index entries match the context files on disk. ? [every-documented-folder-is-reachable-from-central-spec](../rules/every-documented-folder-is-reachable-from-central-spec.md)

### Good documentation, regardless of tier

- **Purposeful.** Every section answers a question the reader actually has. Sections that exist because the template included them are dead weight.
- **Navigation over explanation.** The central spec routes; detail lives next to code. Anyone who has to read the whole central spec to find one fact is being failed by it.
- **Examples are canonical, not aspirational.** Code blocks would pass production review with only placeholder renaming. ? [canonical-examples-are-production-ready](../rules/canonical-examples-are-production-ready.md)
- **Routes by need, not by code.** The Where to Start questions describe feature requirements a product owner could answer, not artefacts only insiders know. ? [where-to-start-routes-by-feature-need](../rules/where-to-start-routes-by-feature-need.md)
- **Testing architecture has a shape.** The test-helpers context file names the pattern and the stub boundary; "tests use Jest" is not enough. ? [testing-architecture-names-pattern-and-seam](../rules/testing-architecture-names-pattern-and-seam.md)

