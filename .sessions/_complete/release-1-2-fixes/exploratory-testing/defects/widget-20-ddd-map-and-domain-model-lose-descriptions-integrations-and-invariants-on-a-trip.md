# A bounded-context map and a domain model rendered to drawio, whiteboard or Python and back lose their descriptions, the Integrations block, invariants, notes and calls, and the file a person wrote is overwritten

- **Charter:** Round 2 - the knowledge graph and the formats of the other practices, as an agent whose files move, rename and stop parsing between two calls
- **Tester:** Widget
- **Story:** epic "Deliver Work With Context Guidance"; no scenario covers a DDD file's trip through its formats.
- **Module and class:** `cdd_guidance/practices/ddd/ddd_formats.py` and `cdd_guidance/practices/ddd/model/`, saved by `cdd_guidance/actions/render/rendered_file.py` `RenderedFile.save`.
- **Severity:** wrong result (the same kind as widget-04 and widget-08, in the DDD formats)

## Steps
Sandbox `repo` (`C:\dev\_et\widget\work\repo`), session `main`, throwaway cdd server (`C:\dev\_et\widget\work\drv\run.py`, calls in `drv\d8.json`, `drv\d9.json`). The originals are kept in `repo\trip\orig\`.

1. `.context/bounded-context-map.md` written after `templates/bounded-context.md`: a sentence under the title, contexts `## Ordering | custom` and `## Catalog | custom` each with a sentence, aggregate roots written `Order - what a Customer asked for`, and under Order an `Integrations:` block (Catalog by BookId, with Direction, What crosses, Integration, Pattern).
2. `render.render {"guidance": "ddd-bounded-context", "format": "drawio", "paths": [".context/bounded-context-map.md"], "source": "markdown"}`, then `{"guidance": "ddd-bounded-context", "format": "markdown", "paths": [".context/bounded-context-map.drawio"], "source": "drawio"}`. Restore the file and do the same through `whiteboard`.
3. `.context/domain-model.md` written after `templates/model.md`; `render.render` at `ddd-model` to `drawio` and back, and to `python` (content saved to a file) and back.

## Expected
The contexts, aggregates, members and integrations a person wrote come back, or the render does not write over the fuller file. The Integrations block is part of the map's own template.

## Actual
**Bounded-context map through drawio:** gone are the sentence under the title, both context descriptions, the root descriptions (`Order - what a Customer asked for` is now `Order`), and the whole Integrations block (7 lines). Through whiteboard the title also became `# Bounded Context Map` (no "— Bookshop").

**Domain model through drawio:** gone are the front matter, the title's "— Bookshop" and the Sources line, each aggregate's sentence, the note `// held by identity — Book lives in Catalog`, the call `-> OrderLine.price`, the note on cancel, and the **Invariants** section. Every plain property (`orderId`, `title`, `price`, `bookId`) gained `<< association >>`.

**Domain model through Python:** the association on `bookId` and its note are gone, `-> OrderLine.price` became `-> price`, `Collection<Order>` became `Collection[Order]`, and the invariants and descriptions are gone. The Python itself declares `def cancel(self, reason: Reason) -> void`.

## Tier that should catch it
Unit (`ddd_spec.py` and the adapters' specs): no example compares a map with integrations, or a model with invariants and notes, before and after a trip.

## Confirmation (Cog)
- Result: confirmed
- What I ran and saw: The DDD adapters called directly on files of my own written after the two templates (`C:\dev\_et\cog\bcm.md`, `dm.md`, run by `w20.py` and `w20py.py`), not through the cdd server, so the save over the person's file was not run. Map through drawio and whiteboard: the sentence under the title, both context sentences, the root descriptions and the Integrations block are gone; through whiteboard the title is `# Bounded Context Map`. Domain model through drawio: front matter, title, Sources line, aggregate sentences, notes, the call and the Invariants are gone. Through Python: `<< association >> bookId` and its note are gone, `-> OrderLine.price` is `-> price`, `Collection<Order>` is `Collection[Order]`, and the Python declares `-> void`.
- Cause, in four places: (1) the markdown adapter itself drops the title's own words, the prose under headings and a root's description on a plain read and write (`ddd/model/markdown/nodes.py` `_text` wrote `# Domain Model` whatever the title was), and wrote a `----` rule under a class with no operations; (2) the drawing holds no prose, notes, calls or invariants, and of an integration only its target aggregate and pattern; an integration whose target names a bounded context (`Catalog`) and no aggregate draws no arrow, so the whole block goes; (3) every property whose type is a capitalised name was given `<< association >>` when read (`clean_engineering/model/property.py` `FieldArrow.derive`); (4) the whiteboard reader did not read the map's title back.
- Fix: (1) the title and the rule, (3) and (4) are fixed. Not fixed: the prose, notes, calls, invariants and the integration to a bounded context (where a drawing keeps them is the person's decision), and the Python trip.

## Also seen by
- Bolt, round 3 (build at 4d47fdf8e, files in `C:\dev\_et\round3\bolt\orig` and `trips`, batches `drv\t1.json` and `drv\t2.json`): still fails. Map through drawio or whiteboard and back: the title now survives, and each integration keeps its arrow and pattern, but the sentence under the title, each context's sentence, the roots' descriptions, each integration's entity, identity (`(by BookId)`), `direction`, `crosses` and `integration`, and, not in the first report, every `emits events:` / `consumes events:` line and the whole `## event map` are gone (47 changed lines). Model through drawio or whiteboard and back: front matter, title (`# Domain Model` from drawio, `# Classes` from whiteboard), Sources line, aggregate sentences, notes, calls, Invariants and now every `Integrations:` block are gone (74 changed lines); plain properties no longer gain `<< association >>`. Classes, stereotypes, properties, operations and relationships inside an aggregate come back the same.
