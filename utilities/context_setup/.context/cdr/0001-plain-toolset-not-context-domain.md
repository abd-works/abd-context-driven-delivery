# Context Setup is a plain primitives toolset, not a context_tools @context domain

Context Setup (capture → prepare → ask, replacing the 7 script-based
abd-context-* skills) is built directly on `primitives`
(`@agentic_toolset` + `@action` + `@tool`), not as a `context_tools`
`@context` domain like Stories/Bdd/CleanEngineering. Every other capability
in this repo follows the `@context` generate/validate/document/satisfy/repair
shape, so this is a deliberate deviation a future reader will ask about.

We picked this because the domain doesn't fit that shape: there is no
"field of expertise" artifact to generate against a rubric of guidelines.
It's a pipeline of deterministic steps (convert, tag, chunk, embed, search
— each a real script wrapped as a `@tool`) interleaved with a handful of
AI-judgment checkpoints that have no tool (structure-quality read,
chunk-count sanity check, query derivation, citation weighting) — those
checkpoints are exactly what `@action` recipes are for.

## Considered options

- **Model it as a `@context` domain anyway**, treating "the pipeline" as
  the artifact and `generate`/`validate` as run/check. Rejected: there is
  no rubric of authored guidelines to validate output against — the
  quality checks are per-stage judgment calls, not a fixed context to
  satisfy.
- **Seven separate small toolsets, one per stage**, mirroring the seven
  existing skills 1:1. Rejected for increment 1: doc-facing choice (scope
  confirmed 2026-08-04) — increment 1 covers to-markdown → semantic-index
  → chunk → db-embed → db-ask only; live-app capture (sandbox +
  app-extractor) is deferred to increment 2, so a single toolset can hold
  increment 1's stages as tools + actions without the seven-way split
  paying for capability increment 2 hasn't earned yet.
