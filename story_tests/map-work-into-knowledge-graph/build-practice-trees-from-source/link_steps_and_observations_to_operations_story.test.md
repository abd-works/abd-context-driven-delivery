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
