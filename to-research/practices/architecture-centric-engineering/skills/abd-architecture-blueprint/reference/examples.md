# Architecture Blueprint — Examples

## Typical blueprint for a SaaS platform

```
docs/architecture/
├── architecture-blueprint.md                  ← human-readable, embeds the two PNGs
├── architecture-outline.md                    ← produced by abd-architecture-outline
├── diagrams/
│   ├── (the four outline diagrams from abd-architecture-outline)
│   ├── component-overview.drawio              ← source (this skill)
│   ├── component-overview.png                 ← rendered
│   ├── entity-relationships.drawio            ← source (this skill)
│   └── entity-relationships.png               ← rendered
└── decisions/
    ├── ADR-004-result-object-error-handling.md
    ├── ADR-005-write-through-redis-cache.md
    └── ADR-006-outbox-event-publishing.md
```

---

## The shape of a good blueprint

```
{Title} — Architecture Blueprint

1. Scope
   Linked from the architecture outline. This blueprint adds component-level
   description and mechanism catalogue. Mechanism walkthroughs live in
   `abd-architecture-specification` output — the central
   `docs/architecture/specification/architecture-specification.md` plus per-folder
   `architecture-context.md` files (mechanism / package / miscellaneous tiers).

2. Components
   2.1 {System} components
       - {Component name}
         {1–2 paragraphs: purpose, dependencies, interactions. No internals.}
       - {Next component …}
   ...

3. Architecture Mechanisms
   3.1 Security
       {1–2 paragraphs: what concern it addresses, which components depend
       on it, how they interact with it. Defer mechanism internals (file
       structure, participants, canonical patterns, rules) to that mechanism's
       `architecture-context.md` under `abd-architecture-specification`.}
   3.2 Error Handling & Resilience
       {1–2 paragraphs}
   ...

4. Data Architecture
   {Entity overview diagram (mermaid classDiagram or ER). Ownership boundary
   table: which component owns which aggregate.}

5. Testing Architecture
   {Common test tiers; common test doubles; framework of record. Mechanism-
   specific testing detail defers to each mechanism's reference section.}

6. Extension & Evolution (if applicable)
   {Only include when the system has real plug-in points: a documented
   adapter contract, a registry-driven extension, a SaaS multi-tenancy
   isolation seam.}

7. Decision Records
   | ID | Decision | One-line consequence |
   |---|---|---|
   | ADR-NNN | ... | ... |
   (each ADR is a separate file under docs/architecture/decisions/)
```
