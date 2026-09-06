# Scanners — abd-architecture-blueprint

No automated scanners are shipped yet. The bundled rules are enforced by manual review and the Validate checklist in `SKILL.md`.

Candidates for future automation:

| Rule | Possible scanner check |
|---|---|
| `components-described-in-paragraphs-not-internals` | Component subsections do not contain code fences, file trees, or method lists. |
| `cross-cutting-concerns-named-as-mechanisms` | Section 3 has named `### 3.X {Mechanism}` subsections; no generic "Patterns" or "Implementation notes". |
| `blueprint-defers-deep-detail-to-specification` | Mechanism subsections do not contain code fences > 5 lines or sequence diagrams with > 3 participants. |
| `extension-section-only-when-applicable` | Section 6 either contains real content or is absent — no "TBD" or "to be defined". |
