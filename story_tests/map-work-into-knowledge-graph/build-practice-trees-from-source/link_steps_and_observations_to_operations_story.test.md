---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Build Practice Trees From Source

Story map: [Build Practice Trees From Source](../../../.context/story-map.md#e-build-practice-trees-from-source). Session release-1-2-fixes.

**Evidence mode.** Every scenario here is *Observed*: it holds for the BDD graph reading today (`cdd_guidance/practices/bdd/model/graph_reading.py`) and names the spec that runs it. They were written after exploratory testing round 3 (defects r3-cog-01, r3-rivet-09), and follow the person's answer of 2026-11-20: "Nothing is joined on a name alone: a call or a link goes to the node the file's own imports, path or link target name."

### Domain terms

- ++imported class++ — a class a spec file's own imports name, found in the file the import names (`ImportedCode`).
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

