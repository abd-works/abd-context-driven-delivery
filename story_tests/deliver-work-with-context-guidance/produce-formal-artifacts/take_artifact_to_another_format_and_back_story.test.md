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

#### Scenario: Keep the words a story map's drawing cannot hold

Observed for the Stories markdown adapter when it is handed the file it replaces (`cdd_guidance/practices/stories/model/markdown/markdown_story_map_round_trip_spec.py`), through drawio and through whiteboard. The Render action hands it that file (`RenderedFile.previous`). Written after defect r3-sparky-02.

*Given* ++.context/story-map.md++ opens with `# Story Map — Bookshop`, holds a sentence under the epic Sell Books and under the story Place Order, links Place Order to ++story_tests/sell-books/take-orders/place_order_story.test.md++, and ends with a `## Scope boundary` section
*When* Claude Code renders ++.context/story-map.md++ to drawio, then ++.context/story-map.drawio++ back to markdown
*Then* ++.context/story-map.md++ is as the person wrote it
  *And* it holds no sources or scope lines the person did not write
  *And* a story added in the drawing is written under its sub-epic, beside the sentences the person wrote

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

Observed for the Stories code adapters (`cdd_guidance/practices/stories/model/code_outline_examples_spec.py`), for Python and TypeScript, with the rows under an `#### Examples` heading as `templates/md/scenarios.md` writes them. Written after defects widget-19 and r3-sparky-06. Evidence still missing: a table written directly under the outline with no Examples heading, and the front matter, Story type, Domain terms and links to the domain model, which no code format holds.

*Given* ++story_tests/sell-books/take-orders/place_order_story.test.md++ holds a Scenario Outline with a table of two rows
*When* Claude Code renders it to python at ++stories-scenarios++, then the python back to markdown
*Then* the python parses, and imports only examples whose names are names in Python
  *And* the Scenario Outline holds its table of two rows, each named by its `scenario` column, under the columns it was written with
  *And* a render to typescript writes no examples file holding data the scenarios file does not name

#### Scenario: Bring a finished spec back from another language as it was written

Observed (`cdd_guidance/practices/bdd/model/spec_trip_spec.py`). Written after exploratory testing round 3 (defect r3-rivet-07): every test body and setup came back commented out, and each further trip wrapped them again.

*Given* `src/ordering/cart_spec.py` is a finished Mamba spec with its imports, a `before.each` in its describe and in two states, and a test body in each `it`
*When* Claude Code renders `src/ordering/cart_spec.py` to typescript at ++bdd-development++, then the typescript back to python
*Then* the typescript holds each python body, setup and import as comments under `// python body to translate:`
  *And* the python that comes back is `src/ordering/cart_spec.py` as it was written
  *And* a second trip holds the same lines as the first

#### Scenario: Keep the order of observations and nested states through a render

Observed (`spec_trip_spec.py`; defect r3-rivet-03). `cdd_guidance/practices/bdd/bdd.md` `hierarchy-preservation`: "1:1 from sketch nesting to code. Nothing added, removed, or flattened".

*Given* the describe tree of a cart holds, under `with a book added`, two observations and then the nested state `that has the same book added again`
*When* Claude Code renders the tree to python, or to typescript, and back to markdown
*Then* both observations stand above the nested state, in the order they were written
  *And* a nested state written above an observation stays above it

#### Scenario: Keep each observation's call graph between a realization tree and spec code

Observed (`spec_trip_spec.py`; defect r3-rivet-06). `bdd.md`, realization: "Store graphs on observations in the BDD model ... round-tripped through `practices/bdd/model`".

*Given* the realization tree of an order holds a fenced call graph above each `it should`
*When* Claude Code renders the tree to python at ++bdd-realization++, then the python back to markdown
*Then* the python holds each call graph as comment lines above `pass  # BDD: SIGNATURE`
  *And* the markdown that comes back holds the same call graph under each observation, indented as it was
  *And* the same python rendered to typescript holds each call graph as `//` comment lines above `// BDD: SIGNATURE`

#### Scenario: Read a realization sketch written in the sketch template's notation

Observed (`spec_trip_spec.py`; defect r3-rivet-05). `cdd_guidance/practices/bdd/templates/bdd-sketch.md`: "Under the deepest heading, a fenced block holds the `it should` observations and the `->` call surface".

*Given* a sketch holds `## behavior driven development:`, the subject `### a cart`, the state `#### with a book added`, and two fences that each hold call lines above one `it should`
*When* Claude Code reads the sketch for ++bdd-realization++
*Then* each observation carries the call lines of its own fence
  *And* no call line is read as a state

#### Scenario: Write a sketch in the sketch template's notation

Observed (`spec_trip_spec.py`; defect r3-rivet-04). `bdd-sketch.md`: "Subjects and their enabling conditions nest through markdown headings" and "Declare fidelity once at the top of the file".

*Given* a behavior sketch holds `Fidelity: behavior`, `## behavior driven development:`, a subject, its states, and fenced `it should` lines
*When* Claude Code renders the sketch to python, then the python to sketch
*Then* the sketch that comes back opens with `Fidelity: behavior` and `## behavior driven development:`
  *And* each subject is a `###` heading, each state a heading one `#` deeper, and each heading's observations stand in a fence under it

#### Scenario: Offer only the formats BDD reads, renders and checks

Observed (`cdd_guidance/practices/bdd/bdd_spec.py`). Written after exploratory testing round 3 (defect r3-rivet-01): Java was offered for BDD specs, and nothing read, rendered or checked a Java spec.

*Given* Claude Code generates at ++bdd-behavior++ or ++bdd-development++
*When* the answer names the formats to save
*Then* it names python and typescript, each of which BDD has a format adapter for
  *And* it names no java path
