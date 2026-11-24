---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Link Practice Trees Across Practices

Story map: [Link Practice Trees Across Practices](../../../../.context/story-map.md#e-link-practice-trees-across-practices). Session release-1-2-fixes.

**Evidence mode.** Every scenario here is *Observed*: it holds for the BDD graph reading today (`cdd_guidance/practices/bdd/model/graph_reading.py`) and names the spec that runs it. They were written after exploratory testing round 3 (defects r3-cog-01, r3-rivet-09), and follow the person's answer of 2026-11-20: "Nothing is joined on a name alone: a call or a link goes to the node the file's own imports, path or link target name."

### Domain terms

- ++imported class++ — a class a spec file's own imports name, found in the file the import names (`CodeFile`, which Clean Engineering's code index answers for the spec file).
- ++nearest setup++ — the `before.each` or `beforeEach` of the innermost describe or state around an observation that has one.

> In steps: the bookshop's files are the examples below.

## Examples

### files of the bookshop project

| file | holds |
| --- | --- |
| ++src/ordering/order.py++ | the class Order with `pay`, `is_paid` and `lines` |
| ++ordering/order/order.py++ | another class Order with `pay` and `is_paid` |
| ++src/checkout_view.py++ | a function `pay` |
| ++src/ordering/cart.py++ | the classes Cart and CartLine, which both have a property `total` |
| ++src/ordering/order_spec.py++ | imports Order from `src.ordering.order`; describes `an order` |
| ++src/ordering/cart_spec.py++ | imports Cart from `src.ordering.cart`; its describe's setup is `self.cart = Cart()` |

## Story: Link Steps And Observations To Operations

### Evidence

| Source | Note |
|--------|------|
| The person's answer 3, 2026-11-20 (`closing-brief-round-3.md`) | nothing is joined on a name alone |
| `cdd_guidance/practices/bdd/model/schema.yaml` | "invokes lists what the nearest enclosing setup calls first, then what the observation's own body calls or reads"; `description.alignsWith?: class` |
| Defects r3-cog-01, r3-rivet-09 | an observation was linked to a same-named operation of a class in another folder and to a function of a view; a read two classes name got no edge; no describe was linked to its class |

#### Scenario: Link an observation to the operation of the class its spec imports

Observed (`cdd_guidance/practices/bdd/model/graph_reading_spec.py`).

*Given* ++src/ordering/order_spec.py++ holds `should be paid` under a state whose setup is `self.order.pay(12)`
*When* the Knowledge Graph reads the bookshop project for BDD and Clean Engineering
*Then* `should be paid` invokes `pay` and `is_paid` of the Order in ++src/ordering/order.py++
  *And* it invokes nothing in ++ordering/order/order.py++ or ++src/checkout_view.py++

#### Scenario: Link a read two imported classes name to the class the spec built

Observed (`graph_reading_spec.py`).

*Given* ++src/ordering/cart_spec.py++ holds `should total zero`, whose body reads `self.cart.total`
*When* the Knowledge Graph reads the bookshop project for BDD and Clean Engineering
*Then* `should total zero` invokes `total` of Cart, the class its describe's setup built `cart` as
  *And* it does not invoke `total` of CartLine

#### Scenario: Start an observation from its nearest setup, a constructor included

Observed (`graph_reading_spec.py`).

*Given* ++src/ordering/order_spec.py++ holds `should hold a line for each cart line` under a state whose setup is `self.order = Order(self.cart)`, inside a describe whose setup calls `self.cart.add`
*When* the Knowledge Graph reads the bookshop project for BDD and Clean Engineering
*Then* `should hold a line for each cart line` invokes the constructor of Order, then `lines` of Order
  *And* it does not invoke `add` of Cart

#### Scenario: Link a describe to the imported class it names

Observed (`graph_reading_spec.py`).

*Given* ++src/ordering/order_spec.py++ describes `an order`
*When* the Knowledge Graph reads the bookshop project for BDD and Clean Engineering
*Then* the describe `an order` aligns with the Order in ++src/ordering/order.py++

#### Scenario: Link a step to the operations of the module its story test imports

Observed (`cdd_guidance/practices/stories/model/story_tests_on_map_spec.py`). Defect r3-sparky-09. The files are the bookshop fixture `cdd_guidance/practices/stories/model/fixtures/bookshop`: `story_tests/fulfil-order/pack-order/pack_order_story.test.py` imports OrderRepository from `src.bookshop.order`; `src/bookshop/order.ts` and `ordering/order/order.py` each hold another OrderRepository with `create` and `load`.

*Given* the When "the Shop Clerk packs the Order" of `pack_order_story.test.py` calls `orders.load("1001").pack()`
*When* the Knowledge Graph reads the bookshop project for Stories and Clean Engineering
*Then* the When invokes `load` of OrderRepository and `pack` of Order in `src/bookshop/order.py`
  *And* it invokes nothing in `src/bookshop/order.ts` or `ordering/order/order.py`

## Story: Find The Class A Step Calls

#### Scenario: Link a step to the class its linked domain term names

Observed (`cdd_guidance/practices/stories/model/term_links_spec.py`). Source: the person's answer 2, 2026-11-20, "A step's linked domain term is an edge from the step to the DDD class it links to"; defect r3-sparky-05.

*Given* a When of `add_book_to_cart_story.test.md` links Book to `domain-model.md#book-aggregate-root-entity` and Cart to `domain-model.md#cart-aggregate-root-entity`
*When* the Knowledge Graph reads the bookshop project for Stories and DDD
*Then* the When names the root Book and the root Cart of `.context/domain-model.md`
  *And* each of those roots is named by the When

#### Scenario: Leave a link to a heading the domain model does not hold without an edge

Observed (`term_links_spec.py`).

*Given* a When links Cart to `domain-model.md#basket-aggregate-root-entity`, a heading `.context/domain-model.md` does not hold
*When* the Knowledge Graph reads the bookshop project for Stories and DDD
*Then* the When names no class for that link
  *And* it still names the root Book, whose link names a heading the model holds

#### Scenario: Link a step to the one class its seed's package holds that declares the operation

Observed (`cdd_guidance/practices/stories/model/step_call_reach_spec.py`). Source: the lead's card for Cog, second wave: where the receiver's class cannot be known and exactly one class the story file reaches declares the operation, link to it. The files are that spec's: `space/kanban/ticket.py`, `board.py` and `ticket_story_examples.py`, and `space/archive/archive.py`, which no story test imports.

*Given* a story test imports only the seed `ticket_on_board` from `space/kanban/ticket_story_examples.py`
  *And* its When calls `world.ticket.reread()`, on a receiver no line of the file gives a class
*When* the Knowledge Graph reads the files for Stories and Clean Engineering
*Then* the When invokes `reread` of Board in `space/kanban/board.py`
  *And* it invokes nothing in `space/archive/archive.py`

#### Scenario: Link a step to the class the story file built the receiver as

Observed (`step_call_reach_spec.py`).

*Given* a story test imports Board and Ticket, which both declare `delete`
  *And* its Given writes `self.board = Board()` and its When calls `self.board.delete()`
*When* the Knowledge Graph reads the files for Stories and Clean Engineering
*Then* the When invokes `delete` of Board
  *And* it does not invoke `delete` of Ticket

#### Scenario: Link nothing when two classes in reach declare the operation and the receiver's class is not written

Observed (`step_call_reach_spec.py`).

*Given* a story test imports Board and Ticket, which both declare `delete`
  *And* its When calls `self.board.delete()` on a receiver a seed returned
*When* the Knowledge Graph reads the files for Stories and Clean Engineering
*Then* the When invokes no operation

## Story: Link Examples To Classes And Steps

### Evidence

| Source | Note |
|--------|------|
| The person's answer 2, 2026-11-20 (`closing-brief-round-3.md`), and the lead's card for Cog | an example's demonstrates edge follows the link as a step's does, never a name alone |
| Defect r3-sparky-05 | the example Tiny Tales, a Book, had no `demonstrates` edge to the model's Book |

#### Scenario: Have an example demonstrate the class of the linked term written before it

Observed (`cdd_guidance/practices/stories/model/term_links_spec.py`).

*Given* a When of `add_book_to_cart_story.test.md` writes the example Tiny Tales straight after the term Book, linked to `domain-model.md#book-aggregate-root-entity`
*When* the Knowledge Graph reads the bookshop project for Stories and DDD
*Then* the example Tiny Tales demonstrates the root Book of `.context/domain-model.md`

#### Scenario: Have an example a story test in code names demonstrate the linked class

Observed (`term_links_spec.py`).

*Given* a Given of `pack_order_story.test.py` says "the Bookshop keeps Order paid order", with Order linked to `domain-model.md#order-aggregate-root-entity`
*When* the Knowledge Graph reads the bookshop project for Stories and DDD
*Then* the example `paid_order` demonstrates the root Order of `.context/domain-model.md`

#### Scenario: Have a Then observe the examples its text and its Background name, with no code read

Observed (`cdd_guidance/practices/stories/model/modelled_areas_spec.py`). Written after exploratory testing round 3 (defect r3-sparky-04): a Then had an `observes` edge only when Clean Engineering was read beside Stories, and "the Cart total is 5", which names no example, could never have one.

*Given* `add_book_to_cart_story.test.md` holds the examples Tiny Tales, Grand Atlas and empty cart, and its Background names Tiny Tales and empty cart
*When* the Knowledge Graph reads the bookshop project for Stories and DDD
*Then* the Then "the Bookshop refuses with Grand Atlas is out of stock" observes Grand Atlas
  *And* the Then "the Cart total is 5" observes Tiny Tales and empty cart

#### Scenario: Report a Then that observes no example where a model is written for its area

Observed (`modelled_areas_spec.py`, and the example pair of `then-observes-an-example`). The person's answer of 2026-11-20: a Then must observe an Example "only if a domain model or class model has been written for that area of the story graph".

*Given* a step of a story under the sub-epic Confirm Order links the term Order to `domain-model.md#order-aggregate-root-entity`
  *And* a Then of that sub-epic, "the Bookshop refuses with order 9999 is not found", names no example, and no Given of its scenario names one
*When* the Knowledge Graph checks the Stories rules on the bookshop project read for Stories and DDD
*Then* that Then carries a then-observes-an-example violation
  *And* the violation says a model is written for its area

#### Scenario: Hold no Then to an example where no model is written for its area

Observed (`modelled_areas_spec.py`). Written after defect r3-sparky-04: scenarios written after the template failed validate with one violation for each Then.

*Given* the story test of Search Books, under the epic Browse Books, links no domain term to a model
  *And* the stories of the sub-epic Add Books link Cart and Book to `domain-model.md`
*When* the Knowledge Graph checks the Stories rules on the bookshop project read for Stories and DDD
*Then* no Then of Search Books carries a then-observes-an-example violation
  *And* the Thens of the areas whose steps link to the model are still held to it

#### Scenario: Report nothing for a term linked to a model document that is not there

Observed (`modelled_areas_spec.py`). The person's answer of 2026-11-20: "scenarios may link to terms it comes up with but the graph doesn't need to connect".

*Given* the steps of `add_book_to_cart_story.test.md` link Cart and Book to `domain-model.md`
  *But* the bookshop project holds no `.context/domain-model.md`
*When* the Knowledge Graph checks the Stories rules on the bookshop project read for Stories and DDD
*Then* no step of that file has a `names` edge
  *And* no step that holds such a link carries a violation
  *And* no example of the project is held to demonstrate a class

