# Module: ddd

**Purpose:** Apply DDD — bounded contexts, aggregates, building blocks — on top of CleanEngineering. CE owns the OO ladder; Ddd overlays strategic/domain vocabulary and fidelity mapping.

**Primary use case:** Author or repair bounded-context maps and building-block stereotypes, then hand off to CleanEngineering at the mapped fidelity for OO deepen / code.

**Rationale:** Keep domain language and context maps in DDD fidelities (`bounded_context` → `building_blocks` → `tactics`) while reusing CE for modules/model/code work through `ce()`.

## Seam

`Ddd` is the seam: construct at a DDD fidelity, expand lifecycle actions, and transform sideways via CE channels.

Constraint: do not restate CleanEngineering class/module analysis in DDD artifacts — use the fidelity's Clean Engineering companion instead. Constraint: do not invent detail from a deeper DDD fidelity than the active one. Fidelity map: bounded_context→modules, building_blocks→model, tactics→code.

## Public API

- `Ddd(fidelity, format=None, path=None, session=None, workspace=None)`
- `diagnostic() -> Diagnose`
- `contexts` instruction
- `guidance` — domain generate prose plus the current fidelity's Clean Engineering companion when one is named
- `render(format, content)` — `PracticeGuidance.render`; DDD has no format folders, so conversion uses the companion practice
- Scan rules discovered under `practices/ddd/scanners/` (`screen-interface-not-a-domain-object`, `private-method-naming`, `building-blocks-fidelity-requires-tactical-stereotype`, `flaccid-data-object-no-behavior`, `no-orphaned-objects`)

## Dependencies

PracticeGuidance; CleanEngineering companion on each fidelity; Diagnose (lazy via `diagnostic()`); Scan (binds this package's `scanners/`)
