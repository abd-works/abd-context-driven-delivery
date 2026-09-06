<!--
  Template: scaffold stub for a mechanism-tier architecture-context.md
  Seeded by abd-architecture-blueprint in mode: scaffold.

  PLACEMENT: written to <mechanism-host-folder>/architecture-context.md by
  Step 3c of the blueprint scaffold mode. The host folder is the folder a
  new instance of the mechanism is added inside (e.g. src/integrations/ for
  Partner Integrations, src/setup/Identity/ for Identity Setup).

  CONTENT POLICY: this stub carries BLUEPRINT-FIDELITY content only — the
  mechanism's code-shape constraint and outline-fidelity content (technology
  choice + ADR link). Spec-fidelity slots (File Structure, Participants,
  Class Specification, Rules, Canonical Patterns, Across the Codebase) are
  seeded as <!-- spec to fill --> markers for the abd-architecture-specification
  skill to fill in later.

  GOVERNING RULE: ../rules/scaffold-stubs-are-blueprint-only.md.

  Replace placeholders in {{double-braces}} from the blueprint and outline
  documents. Do NOT remove the spec-fidelity section markers; abd-architecture-specification
  detects them to know which sections it owns.

  DELETE this leading "Template:" instruction block before the file ships.
-->

# Mechanism: {{MechanismName}}

> **Source:** seeded by `abd-architecture-blueprint` (mode: `scaffold`) on {{ISO-date}}. Blueprint-fidelity and outline-fidelity content below. Spec-fidelity sections to be authored by `abd-architecture-specification`.

## Outline context

**Technology choice** -- {{technology named in the outline's Architecture Mechanisms section for this mechanism}}

**NFR justification** -- {{one-sentence NFR justification copied verbatim from the outline}}

**ADR** -- {{link to the outline-level ADR that records this technology choice}}

## Blueprint context

**Code-shape constraint** -- {{the 1–2 paragraph code-shape description copied verbatim from the blueprint's Mechanisms section for this mechanism — what every module that participates in this mechanism must do}}

**Mechanism-module?** -- {{Yes if this mechanism also has a concrete module surface (e.g. Security → Identity module), with link to that module's architecture-context.md; else No}}

**Test tier** -- {{name of the tier from the blueprint's Testing Architecture that exercises instances of this mechanism}}

---

### Overview

<!-- spec to fill: one short paragraph naming what this mechanism owns and what nothing else owns; one short paragraph naming the composition root / registration point / file skeleton -->

### File Structure

<!-- spec to fill: ```folder tree showing universal files + optional files with {placeholders} for per-instance variation``` -->

### Participants

<!-- spec to fill: one bold-name paragraph per role in the skeleton, with workspace-root link to its file -->

### Class Specification

<!-- spec to fill: ```class spec block per central type — initialisation, public methods + interactions, private methods``` -->

### Rules

<!-- spec to fill: must / must-never bullets enforceable by reading code -->

### Canonical Patterns

<!-- spec to fill: ```code blocks showing the canonical shape per non-trivial file in the skeleton, using {placeholders}``` -->

### Across the Codebase

<!-- spec to fill: table listing each existing instance and which optional parts it uses, plus any deviation -->
