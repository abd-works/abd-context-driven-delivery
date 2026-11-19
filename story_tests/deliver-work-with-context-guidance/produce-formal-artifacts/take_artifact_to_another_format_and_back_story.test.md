---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Produce Formal Artifacts

Story map: [Produce Formal Artifacts](../../../.context/story-map.md#e-produce-formal-artifacts). Session release-1-2-fixes.

**Evidence modes.** *Observed* scenarios hold for the practices' format adapters today (`cdd_guidance/practices/stories/model`, `clean_engineering/model`, `ddd/model`) and each names the spec that runs it. *Intended* scenarios say what a trip should keep where a format cannot hold it yet; each names the evidence still missing (`flagged-writes-intended-gwt`). They were written after exploratory testing (defects widget-04, 05, 08, 19, 20) showed that no scenario covered a trip from one format to another and back.

The story below is not on the story map yet: it was split from Render Artifact Into Another Format, which already holds four scenarios about where a render is saved.

### Domain terms

- ++trip++ — an artifact rendered from the format a person wrote it in to another format, and rendered back.
- ++written relationship++ — the `<< composition >>`, `<< aggregation >>` or `<< association >>` a person wrote on a property line of a class model.
- ++cell id++ — the id a story's cell has in a draw.io story map: the ids of the epic and sub-epic it was written under, then its own.

> In steps: the bookshop's files are the examples below.

## Examples

### files of the bookshop project

| file | holds |
| --- | --- |
| ++.context/story-map.md++ | `# Story Map — Bookshop`, then Sell Books, Take Orders with Place Order and Cancel Order |
| ++.context/story-map.drawio++ | the story map's drawing |
| ++src/.context/src-model.md++ | the class model: Order with `<< composition >> lines: list[OrderLine]`, `history: list[OrderLine]`, `total: Money`, `seller: Seller`, `<< association >> bookId: BookId`; OrderLine; Seller |
| ++.context/domain-model.md++ | `# Domain Model — Bookshop`: the Order aggregate with an invariant, a note and a call; the Book aggregate |
| ++.context/bounded-context-map.md++ | `# Bounded Context Map — Bookshop`: Ordering and Catalog, with an Integrations block on Order |
| ++story_tests/sell-books/take-orders/place_order_story.test.md++ | scenarios of Place Order, one a Scenario Outline with a table of two rows |

## Story: Take Artifact To Another Format And Back

### Evidence

| Source | Note |
|--------|------|
| `cdd_guidance/practices/clean_engineering/clean_engineering.md`, model fidelity | "The same classes, operations, and relationships must appear in every selected representation" |
| `cdd_guidance/actions/render/render.py` `Render.render` | a render is saved "keeping the layout people gave a drawing already there" |
| Defects widget-04, 05, 08, 19, 20 | a story came back under the next sub-epic; properties came back with relationships nobody wrote; a map's title came back as the template's placeholder; an outline's table and a model's prose did not come back |

#### Scenario: Bring a story added after the first drawing back under its own sub-epic

Observed (`cdd_guidance/practices/stories/model/drawio/drawio_round_trip_spec.py`).

*Given* ++.context/story-map.drawio++ draws ++.context/story-map.md++
  *And* a person adds the story Track Order under Take Orders and the sub-epic Ship Orders with the story Pack Order to ++.context/story-map.md++
*When* Claude Code renders ++.context/story-map.md++ to drawio again, then ++.context/story-map.drawio++ back to markdown
*Then* Track Order is under Take Orders
  *And* the sub-epic Take Orders is drawn wide enough to cover Track Order
  *And* a drawing that left Track Order past the edge of Take Orders still reads it under Take Orders, by its ++cell id++ `sell-books/take-orders/track-order`

#### Scenario: Move a story a person dragged under another sub-epic

Observed (`drawio_round_trip_spec.py`).

*Given* a person dragged Cancel Order under the sub-epic Ship Orders in ++.context/story-map.drawio++
*When* Claude Code renders ++.context/story-map.drawio++ to markdown
*Then* Cancel Order is under Ship Orders

#### Scenario: Keep the story map's own title on the way back from its drawing

Observed for the Stories markdown adapter when it is handed the file it replaces (`cdd_guidance/practices/stories/model/markdown/markdown_story_map_round_trip_spec.py`). Evidence still missing: the Render action handing the adapter that file on a render from drawio to markdown.

*Given* ++.context/story-map.md++ opens with `# Story Map — Bookshop`
*When* Claude Code renders ++.context/story-map.md++ to drawio, then ++.context/story-map.drawio++ back to markdown
*Then* ++.context/story-map.md++ opens with `# Story Map — Bookshop`
  *And* it holds no sources or scope lines the person did not write

#### Scenario: Add no relationship nobody wrote to a class model

Observed (`cdd_guidance/practices/clean_engineering/model/drawio/drawio_class_model_round_trip_spec.py`; `cdd_guidance/practices/ddd/model/format_round_trip_spec.py` for ++.context/domain-model.md++ through drawio and whiteboard).

*Given* ++src/.context/src-model.md++ holds the class model
*When* Claude Code renders ++src/.context/src-model.md++ to drawio, then the drawing back to markdown
*Then* `history: list[OrderLine]`, `total: Money` and `seller: Seller` carry no ++written relationship++
  *And* `lines` is still a composition and `bookId` still an association

#### Scenario: Keep a domain model's title, and write no rule over operations a class does not have

Observed (`cdd_guidance/practices/ddd/model/format_round_trip_spec.py`).

*Given* ++.context/domain-model.md++ opens with `# Domain Model — Bookshop` and its value object OrderLine has no operations
*When* Claude Code reads ++.context/domain-model.md++ and writes it again as markdown
*Then* it opens with `# Domain Model — Bookshop`
  *And* OrderLine has no `----` rule under its properties

#### Scenario: Keep the prose a drawing cannot hold

Intended. Evidence still missing: where the prose is kept is the person's decision. A drawing holds no front matter, descriptions, `//` notes, `->` calls, invariants, or the direction, crossing and call site of an integration, so today a render back from a drawing writes the file without them.

*Given* ++.context/domain-model.md++ holds an invariant, a note and a call on the Order aggregate
*When* Claude Code renders ++.context/domain-model.md++ to drawio, then the drawing back to markdown
*Then* ++.context/domain-model.md++ still holds the invariant, the note and the call

#### Scenario: Keep a scenario outline's table through code

Intended. Evidence still missing: the story model keeps an outline's rows only as the lines its markdown was read with, so no code format has them to write (defect widget-19).

*Given* ++story_tests/sell-books/take-orders/place_order_story.test.md++ holds a Scenario Outline with a table of two rows
*When* Claude Code renders it to python at ++stories-scenarios++, then the python back to markdown
*Then* the Scenario Outline holds its table of two rows
