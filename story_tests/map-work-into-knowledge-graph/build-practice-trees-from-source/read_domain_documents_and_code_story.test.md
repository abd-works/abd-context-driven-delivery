---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Build Practice Trees From Source

Story map: [Build Practice Trees From Source](../../../.context/story-map.md#e-build-practice-trees-from-source). Session release-1-2-fixes.

**Evidence mode.** Every scenario here is *Observed*: it holds for DDD's graph reading today (`cdd_guidance/practices/ddd/model/graph_reading.py`) and is run by `cdd_guidance/practices/ddd/model/graph_reading_spec.py`. They were written after round 3 of exploratory testing (defects r3-bolt-01, r3-bolt-02, r3-bolt-05 and the question r3-cog-05) showed that the graph held none of the contexts, integrations and events the bounded-context map and the domain model write, and after the person answered that one class in several practices is several nodes joined by edges.

The story below is not on the story map yet.

### Domain terms

- ++domain document++ — a document DDD reads contexts and aggregates from, in a `.context` folder: the bounded-context map (`bounded-context-map.md`) or a domain model (`domain-model.md`).
- ++described block++ — the building block a domain model draws as a class card, a node at the card's lines in the document.
- ++declared block++ — the building block a class in code is, a node at the class's lines in its file.
- ++marker file++ — `.context/bounded-context.md` in a folder, which makes that folder a bounded context.

> In steps: the bookshop's files are the examples below.

## Examples

### domain documents of the bookshop project

| file | holds |
| --- | --- |
| ++.context/bounded-context-map.md++ | the bounded contexts Ordering (aggregates Cart and Order), Catalogue (Book) and Fulfilment (Shipment); an integration from Cart to Catalogue · Book · Book (Customer/Supplier), from Order to Fulfilment · Shipment · Shipment (Open Host / Published Language) and from Shipment to Ordering · Order · Order (Conformist); an event map: CartCheckedOut emitted by Cart and consumed by Order, OrderPaid emitted by Order and consumed by Shipment |
| ++.context/domain-model.md++ | the same contexts and aggregates, each aggregate with its root, its repository and a member; the same three integrations; Cart's operations call `BookRepository.load(bookId)` and `OrderRepository.create(cart)`, and `checkOut()` returns an Order; Book integrates with no other aggregate |

### code of the bookshop project

| file | holds |
| --- | --- |
| ++ordering/.context/bounded-context.md++ | the ++marker file++ titled Ordering, with the line `Cart → Catalogue · Book` |
| ++catalogue/.context/bounded-context.md++ | the ++marker file++ titled Catalogue |
| ++ordering/cart/cart.py++, ++ordering/cart/cart.ts++ | the root Cart and CartRepository, in Python and in TypeScript; Cart's doc comment keeps the integration `---<<Customer/Supplier>>--> Book` with `context: Catalogue`, `aggregate: Book`, `entity: Book` |
| ++catalogue/book/book.py++, ++catalogue/book/book.ts++ | the root Book and BookRepository, in Python and in TypeScript |

## Story: Read Domain Documents And Code

### Evidence

| Source | Note |
|--------|------|
| `cdd_guidance/practices/ddd/model/schema.yaml` | a `boundedContext` holds `aggregate`; `mappedTo: contextMapping` with `local`, `remote` and `pattern`; a `repository` `accesses` its `entityRoot`; an `entityRoot` `associates` with entities |
| `cdd_guidance/practices/ddd/model/nodes.py` `DomainEvent` | "One producer aggregate, one or many consumers" |
| `.sessions/release-1-2-fixes/exploratory-testing/closing-brief-round-3.md`, the person's answer 3 | a DDD node has an "is a" edge to the Clean Engineering class read from the same file; a class in a model document and the class in code that implements it are two nodes with an edge; nothing is joined on a name alone |
| Defects r3-bolt-01, r3-bolt-02, r3-bolt-05, r3-cog-05 | one bounded context called "bounded context"; no mapping, event or dependency between aggregates; a mapping with no side; a Python repository accessing the TypeScript root; a model's class leaving the graph when code is loaded |

#### Scenario: Read the bounded contexts the domain documents head

*Given* the bookshop holds its ++domain document++s and no ++marker file++
*When* Claude Code loads the bookshop into the graph
*Then* the DDD practice holds the bounded contexts Ordering, Catalogue and Fulfilment, and none called `bounded context`
  *And* Cart and Order sit under Ordering, Book under Catalogue and Shipment under Fulfilment, each aggregate once

#### Scenario: Read each integration as a context mapping between two aggregates

*Given* the bookshop holds its ++domain document++s and no ++marker file++
*When* Claude Code loads the bookshop into the graph
*Then* a context mapping leads from Cart to Book with the pattern Customer/Supplier, from Order to Shipment with Open Host / Published Language, and from Shipment to Order with Conformist
  *And* each mapping sits under the bounded context of the aggregate that has the dependency
  *And* an integration both documents write is one mapping

#### Scenario: Read each event with the aggregate that emits it and the aggregates that consume it

*Given* the bookshop holds its ++domain document++s and no ++marker file++
*When* Claude Code loads the bookshop into the graph
*Then* CartCheckedOut has Cart as its producer and Order as a consumer
  *And* OrderPaid has Order as its producer and Shipment as a consumer

#### Scenario: Relate the roots a domain model's integrations and calls join

*Given* the bookshop holds its ++domain document++s and no ++marker file++
*When* Claude Code loads the bookshop into the graph
*Then* the root Cart associates with the root Book, Order with Shipment, and Shipment with Order
  *And* Cart depends on BookRepository and OrderRepository, which its operations call, on Order, which `checkOut()` returns, and on CartLine, which it composes

#### Scenario: Find a domain model written after the template conforms to the schema

*Given* the bookshop holds its ++domain document++s and no ++marker file++
*When* Claude Code checks conforms-to-schema on the DDD practice
*Then* no violation is reported
  *And* Book, which integrates with no other aggregate, is not asked for an associates relationship

#### Scenario: Link a mapping's sides to aggregates whose folders are named in lower case

*Given* the bookshop holds its code
*When* Claude Code loads the bookshop into the graph
*Then* the mapping `Cart → Catalogue · Book` of ++ordering/.context/bounded-context.md++ has the aggregate `cart` as its local side and the aggregate `book` as its remote side

#### Scenario: Link a block to the block written in its own language

*Given* the bookshop holds its code
*When* Claude Code loads the bookshop into the graph
*Then* CartRepository of ++ordering/cart/cart.py++ accesses the root Cart of ++ordering/cart/cart.py++, and CartRepository of ++ordering/cart/cart.ts++ the root Cart of ++ordering/cart/cart.ts++
  *And* the root Cart of ++ordering/cart/cart.py++ associates with the root Book of ++catalogue/book/book.py++, which its doc comment's integration reaches, and the TypeScript Cart with the TypeScript Book

#### Scenario: Join a building block to the Clean Engineering class it is

*Given* the bookshop holds its code
*When* Claude Code loads the bookshop into the graph
*Then* the ++declared block++ Cart of ++ordering/cart/cart.py++ has an `isA` edge to the Clean Engineering class Cart read from ++ordering/cart/cart.py++

#### Scenario: Keep a described block beside the declared block that implements it

*Given* a project holds `src/.context/domain-model.md`, which draws the root Cart in the aggregate Cart, and `src/cart/cart.py`, which declares the class Cart as an aggregate root
*When* Claude Code loads the project into the graph
*Then* the DDD practice holds the ++described block++ Cart and the ++declared block++ Cart
  *And* the ++declared block++ has an `implements` edge to the ++described block++, because its folder `cart` is named for the aggregate the document draws the class in
