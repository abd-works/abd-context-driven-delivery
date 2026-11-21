---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Produce Formal Artifacts

Story map: [Produce Formal Artifacts](../../../.context/story-map.md#e-produce-formal-artifacts). Session release-1-2-fixes.

**Evidence modes.** *Observed* scenarios hold for DDD's format adapters today (`cdd_guidance/practices/ddd/model`) and each names the spec that runs it. The one *Intended* scenario says what a trip should keep where a drawing cannot hold it yet, and names the evidence still missing (`flagged-writes-intended-gwt`). They were written after exploratory testing (defects widget-20 and r3-bolt-03) showed that a bounded-context map and a domain model lost a person's sentences, notes, invariants, events and integration fields on a trip to a drawing and back, and that the arrows a drawing shows were dropped when it was read.

The story below is not on the story map yet. It follows Take Artifact To Another Format And Back ([take_artifact_to_another_format_and_back_story.test.md](take_artifact_to_another_format_and_back_story.test.md)), whose scenario "Keep the prose a drawing cannot hold" was Intended; the scenarios here make it Observed for the case where the markdown file is still there when the drawing is written back.

### Domain terms

- ++document's words++ — what a bounded-context map or a domain model writes that no drawing shows: the lines round its title, the sentence under a bounded context or an aggregate, what a root is, a `//` note, an invariant, a call inside an aggregate, the fields of an integration, and the events an aggregate emits and consumes.
- ++replaced file++ — the markdown file a render writes over, as it is before the render. The Render action hands it to the format that writes the new one (`RenderedFile.previous`).
- ++integration arrow++ — the arrow a drawing shows for an integration, labelled with its pattern, such as `«Customer/Supplier»` from Cart to Book.
- ++call arrow++ — the arrow a domain model's drawing shows from a class to a class of another aggregate, labelled with the operation that makes the call, such as `«addBook»` from Cart to BookRepository.

> In steps: the bookshop's files are the examples below.

## Examples

### files of the bookshop project

| file | holds |
| --- | --- |
| ++.context/bounded-context-map.md++ | `# Bounded Context Map — Bookshop` and a sentence under it; the bounded contexts Ordering (aggregates Cart and Order), Catalogue (Book) and Fulfilment (Shipment), each with a sentence; each root written `Cart - the books a Customer means to buy`; an integration from Cart to Catalogue · Book · Book, from Order to Fulfilment · Shipment · Shipment and from Shipment to Ordering · Order · Order, each with its identity, pattern, direction, crosses and integration; `emits events:` and `consumes events:` lines; an event map with CartCheckedOut and OrderPaid |
| ++.context/domain-model.md++ | front matter, `# Domain Model — Bookshop` and a Sources line; the same three contexts and four aggregates, each aggregate with a sentence, its root, its repository and a member; notes, invariants, the calls `-> BookRepository.load(bookId)`, `-> OrderRepository.create(cart)`, `-> OrderRepository.load(orderId)` and `-> CartLine.subtotal`; an integration under Cart, Order and Shipment with pattern, crosses, integration and sync |

Both files are kept as the specs' fixtures in `cdd_guidance/practices/ddd/model/_examples/trip/three-contexts/`.

## Story: Take Domain Documents To Another Format And Back

### Evidence

| Source | Note |
|--------|------|
| `cdd_guidance/actions/render/rendered_file.py` `RenderedFile.previous` | the file as it was, "which the render keeps what people gave of: a diagram's layout, and a document's own words that its source does not hold" |
| `cdd_guidance/practices/ddd/templates/bounded-context.md`, `templates/model.md` | the sentence under a heading, `Root - one line`, `emits events:` / `consumes events:`, the Invariants section and the `sync:` field are the templates' own lines |
| Defects widget-20, r3-bolt-03 | a map lost 47 lines and a model 74 on a trip through a drawing; all six arrows between aggregates were dropped when a model's drawing was read |

#### Scenario: Keep every line of a bounded-context map read and written again as markdown

Observed (`cdd_guidance/practices/ddd/model/format_round_trip_spec.py`).

*Given* ++.context/bounded-context-map.md++ holds the bookshop's map
*When* Claude Code reads ++.context/bounded-context-map.md++ and writes it again as markdown
*Then* every line a person wrote is in it, and no other line
  *And* that includes the sentence under the title, each bounded context's sentence, `Cart - the books a Customer means to buy`, and each `consumes events:` line

#### Scenario: Keep every line of a domain model read and written again as markdown

Observed (`format_round_trip_spec.py`).

*Given* ++.context/domain-model.md++ holds the bookshop's domain model
*When* Claude Code reads ++.context/domain-model.md++ and writes it again as markdown
*Then* every line a person wrote is in it, and no other line
  *And* that includes the front matter, the Sources line, each aggregate's sentence, and each integration's `sync:` line

#### Scenario Outline: Keep the document's words when a drawing is written back over the file it was drawn from

Observed (`format_round_trip_spec.py`).

*Given* ++<file>++ holds what the examples say
*When* Claude Code renders ++<file>++ to <drawn format>, then the drawing back to markdown, with ++<file>++ as the ++replaced file++
*Then* every line a person wrote is in ++<file>++, and no other line

| file | drawn format |
| --- | --- |
| .context/bounded-context-map.md | drawio |
| .context/bounded-context-map.md | whiteboard |
| .context/domain-model.md | drawio |
| .context/domain-model.md | whiteboard |

#### Scenario: Leave out an integration whose arrow a person removed from the drawing

Observed (`format_round_trip_spec.py`).

*Given* ++.context/bounded-context-map.md++ was rendered to drawio
  *And* a person removed the ++integration arrow++ from Cart to Book in the drawing
*When* Claude Code renders the drawing back to markdown, with ++.context/bounded-context-map.md++ as the ++replaced file++
*Then* Cart has no integration
  *And* Order and Shipment keep their integrations with every field

#### Scenario Outline: Read the arrows between aggregates back from a domain model's drawing

Observed (`format_round_trip_spec.py`).

*Given* ++.context/domain-model.md++ was rendered to <drawn format>
  *And* no markdown file is beside the drawing
*When* Claude Code renders the drawing to markdown
*Then* Cart, Order and Shipment each have the integration their ++integration arrow++ was drawn from, to the same context, aggregate and class, with its pattern
  *And* addBook calls BookRepository, checkOut calls OrderRepository and dispatch calls OrderRepository, as their ++call arrow++ shows

| drawn format |
| --- |
| drawio |
| whiteboard |

#### Scenario: Draw the same arrows again from the markdown read back from a drawing

Observed (`format_round_trip_spec.py`).

*Given* ++.context/domain-model.md++ was rendered to drawio, and the drawing to markdown with no markdown file beside it
*When* Claude Code renders that markdown to drawio again
*Then* the drawing has the same fourteen arrows, between the same cards, with the same labels

#### Scenario: Keep the document's words when no markdown file is beside the drawing

Intended. Evidence still missing: where a drawing keeps the ++document's words++ is the person's decision. A drawing holds no sentence, note, invariant, event, or field of an integration other than its pattern, and a domain model's drawing does not show the model's title, so a drawing rendered to markdown with no ++replaced file++ writes the file without them.

*Given* ++.context/domain-model.md++ was rendered to drawio
  *And* a person deleted ++.context/domain-model.md++
*When* Claude Code renders the drawing to markdown
*Then* ++.context/domain-model.md++ holds its title, its notes, its invariants and each integration's fields

#### Scenario Outline: Name each aggregate in a bounded context's file as a link to the domain model

Observed (`cdd_guidance/practices/ddd/model/context_file_spec.py`, `cdd_guidance/practices/ddd/context_links_alignment_heavy_spec.py`). Written after the person's answer of 2026-11-21. The domain model is created in one format, then checked by the same examples.

*Given* the Bookshop's domain model, whose context Ordering holds the aggregates Cart and Order, is <created>
*When* the Ordering context's own file is written from it
*Then* the file is titled Ordering and names, under `Aggregates:`, `[Cart](../../.context/domain-model.md#cart)` and `[Order](../../.context/domain-model.md#order)`
  *And* each link opens a heading the domain model holds
  *And* the session's diagnosis reports no edge between the context's file and the domain model that no callout shows

| created |
| --- |
| written as markdown |
| taken through a drawing and back |
| taken through a whiteboard and back |
| taken through Python and back |
| taken through TypeScript and back |
| taken through JavaScript and back |

#### Scenario: Keep what a person wrote in a bounded context's file when its aggregates become links

Observed (`cdd_guidance/practices/ddd/model/context_file_spec.py`).

*Given* `ordering/.context/bounded-context.md` holds a sentence a person wrote, the aggregates Cart and Order named in plain words, and the context mapping `Cart → Catalogue · Book`
*When* the file is written again from the domain model
*Then* it keeps the sentence and the context mapping
  *And* it names Cart and Order once each, as links to their headings in the domain model
