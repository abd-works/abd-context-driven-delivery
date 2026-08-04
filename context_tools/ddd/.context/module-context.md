# Module: ddd

**Purpose:** Apply DDD — bounded contexts, aggregates, building blocks — on top of CleanEngineering. CE owns the OO ladder; Ddd overlays strategic/domain vocabulary and fidelity mapping.

**Primary use case:** Author or repair bounded-context maps and building-block stereotypes, then hand off to CleanEngineering at the mapped fidelity for OO deepen / code.

**Rationale:** Keep domain language and context maps in DDD fidelities (`bounded_context` → `building_blocks` → `tactics`) while reusing CE for modules/model/code work through `ce()`.

## Seam

`Ddd` is the seam: construct at a DDD fidelity, expand lifecycle actions, and transform sideways via CE channels.

Constraint: do not restate CleanEngineering class/module analysis in DDD artifacts — call `ce()` at the mapped fidelity instead. Constraint: do not invent detail from a deeper DDD fidelity than the active one. Fidelity map: bounded_context→modules, building_blocks→model, tactics→code.

## Public API

- `Ddd(fidelity, format=None, path=None, session=None, workspace=None)`
- `ce() -> CleanEngineering` (tool mode)
- `diagnostic() -> Diagnose`
- `contexts` instruction
- Actions: `generate_output`, `validate`, `satisfy`, `repair(asset, violation)`
- Tool: `transform(source_format, target_format, content)`

## Dependencies

BaseContextTool; CleanEngineering (lazy via `ce()` / `transform`); Diagnose (lazy via `diagnostic()`)
