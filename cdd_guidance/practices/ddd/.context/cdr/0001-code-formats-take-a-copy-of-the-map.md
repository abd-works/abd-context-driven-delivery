# The code formats take one copy of the map; the draw.io map is the diagram itself

**Status:** decided, round 6 (finding H1, the part left after its typed fields and the draw.io map were done).

## Decision

*BoundedContextMap* is not itself a *CleanEngineeringModel*. Rendering to Python or TypeScript writes the map into that format's own class model once (`write_classes`), and reading code back makes one card per class (`read_class_model`, `ClassCard.from_code`). The draw.io format is different: *DrawIOBoundedContextMap* subclasses both the map and Clean Engineering's draw.io model, so it draws its own modules and renders itself with no held diagram.

Where a class lives and the integrations of its aggregate travel as real fields, not intent text: the class's `module_path` and its root's dependencies with their details (`Relationship.details`), which the code formats write in the doc comment and read back through Clean Engineering's *DocumentedIntent*.

## Why

- A code format must hold its own language's classes (*PythonClass*, *TypeScriptClass*) to write that language, exactly as every Clean Engineering format copies the model it renders (`translate_from`). Writing the map into the format is that one copy; there is no second one beside it.
- The map's contexts nest aggregates, which nest classes, while a code file is one module per file. Making the map's contexts its Clean Engineering modules would make every code render write context banners the reader cannot read back, and a code class carries none of a card's own parts (its invariants, its root mark). The cards are the domain's form of a class; a code class is the language's.
- The draw.io diagram has none of those limits: its modules view is the map's own shape, so there the map is the diagram.

## Consequences

`Ddd._model_for` writes a map into a code model, and reads a code model into a markdown map; a draw.io map is never treated as a code model, since it is a map first.
