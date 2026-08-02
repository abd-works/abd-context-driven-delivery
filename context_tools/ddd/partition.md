## Top-level artifacts

**Bounded contexts** — discrete areas of the domain where language and models are internally consistent (`DomainMap` → `BoundedContext` → `Aggregate` → `BuildingBlock` per `ddd.md`). Thin: context name + candidate aggregates + short ubiquitous-language note.

Key rules: `language-is-context-scoped` — a term's meaning is only valid inside the context that defines it; the same word in two contexts is two different concepts.

