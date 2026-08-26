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
- `guidance` — domain generate prose + CleanEngineering companion as a separate tools run. Lifecycle generate / validate / satisfy / document / repair live on kits (`Generate().generate(tools=[ddd])`).
- Tool: `apply_document_workspace_default` — switches the working folder to `domain/` for `/document` unless path or folder was overridden
- Tool: `transform(source_format, target_format, content)`
- Tool: `render(format, content)` — calls `transform` from the current format via CE channels

## Scanners

Discovered under `context_tools/ddd/scanners/` (`*_scanner.py`, same kit as other context tools):

- `screen-interface-not-a-domain-object`
- `private-method-naming`
- `building-blocks-fidelity-requires-tactical-stereotype`
- `flaccid-data-object-no-behavior`
- `no-orphaned-objects`

## Dependencies

BaseContextTool; CleanEngineering (lazy via `ce()` / `transform`); Diagnose (lazy via `diagnostic()`); Scan (`_DddScan` binds this package's `scanners/`)
