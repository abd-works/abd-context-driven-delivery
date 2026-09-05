<!--
  Template: scaffold stub for a package-tier architecture-context.md
  Seeded by abd-architecture-blueprint in mode: scaffold.

  PLACEMENT: written to <module-folder>/architecture-context.md by Step 3c
  of the blueprint scaffold mode. One per module named in the blueprint's
  Modules section.

  CONTENT POLICY: this stub carries BLUEPRINT-FIDELITY content only.
  Spec-fidelity slots (Surface, Participants, Class Specification, Rules,
  Canonical Pattern) are seeded as <!-- spec to fill --> markers for the
  abd-architecture-specification skill to fill in later.

  GOVERNING RULE: ../rules/scaffold-stubs-are-blueprint-only.md.

  Replace placeholders in {{double-braces}} from the blueprint document.
  Do NOT remove the spec-fidelity section markers; abd-architecture-specification
  detects them to know which sections it owns.

  DELETE this leading "Template:" instruction block before the file ships.
-->

# {{ModuleName}}

> **Source:** seeded by `abd-architecture-blueprint` (mode: `scaffold`) on {{ISO-date}}. Blueprint-fidelity content below. Spec-fidelity sections to be authored by `abd-architecture-specification`.

## Blueprint context

**Owning module** -- `{{ModuleName}}`

**Business scope** -- {{one or two sentences copied verbatim from the blueprint's Modules section for this module}}

**Mechanisms used** -- {{list from the blueprint's per-module mechanism list, using the *common set* shorthand + module-specific extras as the blueprint records them}}

**Test tier** -- {{name of the tier from the blueprint's Testing Architecture that exercises this module}}

**Dependencies** -- {{list other modules this one depends on, exactly as named in the blueprint's module diagram}}

**Mechanism-module?** -- {{Yes if this module is also a named mechanism (e.g. Security → Identity module); else No}}

**ADR references** -- {{links to ADRs in `docs/architecture/decisions/` that govern this module — outline-level mechanism ADRs for each mechanism used; blueprint-level ADRs for module boundary / dependency decisions}}

---

## Public surface

<!-- spec to fill: list of public operations / exports consumers actually call -->

## Participants

<!-- spec to fill: bold-name paragraphs, one per file or symbol in the package, marked public vs internal -->

## Rules

<!-- spec to fill: must / must-never bullets enforceable by reading code -->

## Across the Codebase

<!-- spec to fill: named consumers (file paths) of this package's public surface; or "none — this module has no public surface yet" -->
