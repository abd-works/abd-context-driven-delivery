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

#### Scenario: Name a second class model's own classes in its markdown

Observed (`cdd_guidance/practices/clean_engineering/model/class_model_trip_spec.py`). Source: `PracticeFormats.adapter`, "every render and every read through it uses the same one"; defect r3-widget-04.

*Given* Claude Code rendered the Ordering model's Python (Cart, CartLine, Order, Payment) to markdown
*When* Claude Code renders the Fulfilment model's drawing to markdown in the same session
*Then* the markdown names Shipment and ExpressShipment, and none of the Ordering model's classes
  *And* ExpressShipment still extends Shipment

#### Scenario: Write a class model back from its drawing as the person wrote it

Observed for drawio and whiteboard (`class_model_trip_spec.py`). Source: `clean_engineering.md`, model fidelity, "The same classes, operations, and relationships must appear in every selected representation"; `RenderedFile.previous`, "a document's own words that its source does not hold"; defect widget-08.

*Given* ++src/.context/src-model.md++ is written after the class model template, with front matter, a Module line, descriptions, a group heading, `//` notes and `->` calls
*When* Claude Code renders it to drawio, then the drawing back to markdown over ++src/.context/src-model.md++
*Then* ++src/.context/src-model.md++ reads as the person wrote it

#### Scenario: Keep a class's notes and calls when its drawing gains an operation

Observed (`class_model_trip_spec.py`). Defect widget-08.

*Given* a person adds the operation `recall(): None` to Shipment in the Fulfilment model's drawing
*When* Claude Code renders the drawing to markdown over the model's markdown
*Then* Shipment holds `recall(): None`
  *And* `dispatch(): None` still holds its call `-> Order.total` and its note
  *And* the file still opens with its front matter and the module's description

#### Scenario: Bring a class model back from Python with its relationships, notes and call owners

Observed (`class_model_trip_spec.py`). Source: the Python render itself writes `# << composition >>`, the notes and `Book.is_in_stock()`; defect r3-widget-06.

*Given* the Ordering model's markdown holds `<< composition >> lines: list[CartLine]`, a note under `customer_id`, and the call `-> Book.is_in_stock` under `add`
*When* Claude Code renders it to python, then the python back to markdown
*Then* `lines` is still a composition and `customer_id` still holds its note
  *And* `add` still calls `Book.is_in_stock`, with its note
  *And* the constructor reads `Cart(customer_id: str)`, and no class holds an `__init__` operation

#### Scenario: Spell types and calls in the language a class model is rendered to

Observed (`class_model_trip_spec.py`). Defects r3-widget-07, r3-bolt-07.

*Given* the Ordering model's markdown holds `lines: list[CartLine]` and `add(book: Book, quantity: int): CartLine`, which calls `Book.is_in_stock`
*When* Claude Code renders it to typescript
*Then* the property reads `lines: CartLine[];` and the operation `add(book: Book, quantity: number): CartLine`
  *And* the call reads `Book.isInStock();`, the name the file gives the operation
  *And* the TypeScript rendered to python reads `-> bool` and `lines: list[CartLine]`

#### Scenario: Write module cards back from their drawing as the person wrote them

Observed for drawio and whiteboard (`cdd_guidance/practices/clean_engineering/model/module_card_trip_spec.py`). Source: rules `language-opens-the-card` and `named-seam-and-constraint`; defect r3-widget-02.

*Given* three module cards, each with its language, its Purpose, Seam and Dependencies, and a Constraint section
*When* Claude Code renders the cards to drawio, then the drawing back to markdown over the cards
*Then* each card reads as the person wrote it
  *And* a card whose module gained a dependency in the drawing holds the new dependency, with its language and its constraint

#### Scenario: Read back from a modules whiteboard only the modules a person wrote

Observed (`module_card_trip_spec.py`). Source: the drawio modules view, where a box that only groups modules is no module; defect r3-widget-03.

*Given* the modules whiteboard draws `src/catalogue`, `src/ordering` and `src/fulfilment` inside a box for `src`, which no card describes
*When* Claude Code renders the whiteboard to markdown
*Then* the markdown holds the three modules and no module `src`
  *And* no module depends on `src`
  *And* each module's purpose is written once

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
*Then* it names python, typescript and javascript, each of which BDD has a format adapter for
  *And* it names no java path

#### Scenario: Offer JavaScript for specs and story tests wherever TypeScript is offered

Observed (`cdd_guidance/practices/bdd/bdd_spec.py`, `cdd_guidance/practices/stories/javascript_story_tests_spec.py`). Written after the person's answer of 2026-11-20: "Java: remove for now; we can create when we need it; restrict to python and typescript or js".

*Given* a fidelity of BDD or Stories offers typescript among the formats it writes
*When* Claude Code generates at that fidelity
*Then* the answer names a javascript path beside the typescript one
  *And* no fidelity of BDD or Stories names java

#### Scenario Outline: Keep a story map's stories, scenarios and steps through another format and back

Observed (`cdd_guidance/practices/stories/model/story_test_behaviours_spec.py`). The trip is created from the project written in one format, then checked by the same examples the project itself is checked by.

*Given* the Pack Orders project is written as <format>
*When* its story files are written as <other format> and written again as <format>
*Then* the graph read from the files that come back holds the same stories, scenarios and steps
  *And* each Then still observes the example its Given names in plain words

| format | other format |
| --- | --- |
| Python story tests | markdown scenarios |
| TypeScript story tests | markdown scenarios |
| TypeScript story tests | JavaScript story tests |
| JavaScript story tests | markdown scenarios |
| JavaScript story tests | TypeScript story tests |

#### Scenario: Bring a JavaScript spec back from TypeScript as it was written

Observed (`cdd_guidance/practices/bdd/model/code_spec_render_spec.py`).

*Given* a finished JavaScript spec of a cart, with its imports, its `beforeEach` and one test body
*When* Claude Code renders it to typescript and renders that back to javascript
*Then* the spec comes back as it was written

#### Scenario: Save a class model rendered to code in each module's own file

Observed (`cdd_guidance/practices/clean_engineering/model/class_model_languages_spec.py`, `cdd_guidance/practices/clean_engineering/class_model_render_heavy_spec.py`). Written after the person's answer of 2026-11-20: every render ends in a saved file. The model is created from the module written in one language, then checked by the same examples.

*Given* the Ordering module's class model is written as <source>
*When* Claude Code renders it to <code format> at the Clean Engineering model fidelity
*Then* the module's classes are saved in `ordering/ordering` with that format's extension
  *And* that file is one the fidelity declares for the format, `{module}/{module}` with the extension

| source | code format |
| --- | --- |
| a markdown class model | python, typescript, javascript |
| Python code | python, typescript, javascript |
| TypeScript code | python, typescript, javascript |
| JavaScript code | python, typescript, javascript |

#### Scenario: Save a domain model rendered to code in each aggregate's own file

Observed (`cdd_guidance/practices/ddd/model/domain_model_languages_spec.py`, `cdd_guidance/practices/ddd/domain_model_render_heavy_spec.py`). DDD writes JavaScript with the class model TypeScript is written with, its types left out.

*Given* the Ordering bounded context, with its aggregates Cart and Order, is written as <source>
*When* Claude Code renders it to <code format> at the DDD model fidelity
*Then* each aggregate's classes are saved in `ordering/cart/cart` and `ordering/order/order` with that format's extension
  *And* each file is one the fidelity declares for the format

| source | code format |
| --- | --- |
| a markdown domain model | python, typescript, javascript |
| Python code whose classes name their place | python, typescript, javascript |
| TypeScript code whose classes name their place | python, typescript, javascript |
| JavaScript code whose classes name their place | python, typescript, javascript |
