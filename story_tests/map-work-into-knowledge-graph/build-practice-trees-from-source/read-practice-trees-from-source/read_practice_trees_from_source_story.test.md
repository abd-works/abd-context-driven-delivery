---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Read Practice Trees From Source

Story map: [Read Practice Trees From Source](../../../../.context/story-map.md#e-read-practice-trees-from-source). Session release-1-2-fixes.

**Evidence mode.** Every scenario here is *Observed*: it holds for the practices' graph readings today and names the spec that runs it. They were written after exploratory testing (defects widget-18, widget-21) showed a file could drop out of the graph without a word.

### Domain terms

- ++module card++ — a folder's `.context/module-context.md`, which makes the folder a module; a folder without one is a package.
- ++byte-order mark++ — the three bytes some editors put at the start of a UTF-8 file.

> In steps: the bookshop's files are the examples below.

## Examples

### source files of the bookshop project

| file | holds |
| --- | --- |
| ++src/order.py++ | `class Order(:`, which is not Python; `src` has no module card |
| ++src/other.py++ | the class Other |
| ++shop/bom.py++ | the class BomOnly, after a byte-order mark |

## Story: Read Modules Classes And Operations

### Evidence

| Source | Note |
|--------|------|
| `cdd_guidance/practices/clean_engineering/clean_engineering.md` `source-parses` | "A file that does not parse is read into no classes, so every other rule passes it without looking" |
| `cdd_guidance/practices/clean_engineering/reading/code_read.py` `CodeRead._parsed` | "A file that does not parse is kept with the reason, so the source-parses rule reports it" |
| Defect widget-18 | a file that did not parse in a folder with no module card, and a valid file that started with a byte-order mark, left the graph with no violation |

#### Scenario: Report a file that does not parse in a folder with no module card

Observed (`cdd_guidance/practices/clean_engineering/rules/practice_wide_rules_spec.py`, "source-parses").

*Given* ++src/order.py++ is not Python and `src` has no ++module card++
*When* the Knowledge Graph reads the bookshop project for Clean Engineering
*Then* the package `src` carries a source-parses violation naming ++src/order.py++
  *And* the class Other of ++src/other.py++ is in the graph

#### Scenario: Read a byte-order mark as the file's start

Observed (`cdd_guidance/practices/clean_engineering/model/graph_reading_spec.py`; `practice_wide_rules_spec.py`).

*Given* ++shop/bom.py++ starts with a ++byte-order mark++
*When* the Knowledge Graph reads the bookshop project for Clean Engineering
*Then* the class BomOnly is in the graph
  *And* no source-parses violation names ++shop/bom.py++

#### Scenario: Join a call to the operation its receiver names

Observed (`cdd_guidance/practices/clean_engineering/model/graph_bookshop_spec.py`). Source: the person's answer 3 of 2026-11-20, "Nothing is joined on a name alone: a call or a link goes to the node the file's own imports, path or link target name"; defect r3-widget-09.

*Given* Cart and Order both have an operation `total`, and Shipment's `dispatch` calls `self.order.total()` where `order` is typed Order
  *And* ExpressShipment extends Shipment and its constructor calls `super().__init__`
*When* the Knowledge Graph reads the bookshop project for Clean Engineering
*Then* `Shipment.dispatch` invokes `Order.total` and not `Cart.total`
  *And* `ExpressShipment.__init__` invokes `Shipment.__init__` and no other class's constructor
  *And* a read of `self.order.payment.authorised` is joined to `Order.payment` and `Payment.authorised`, not to every property of those names

#### Scenario: Read a constructor's fields, a base class and a list's class

Observed (`graph_bookshop_spec.py`). Source: `clean_engineering/model/schema.yaml`, class, `baseClass?: class`, `dependsOn?: [class]`, `participants?: [operation | property]`; defect r3-widget-10.

*Given* the bookshop's Python classes assign their fields in `__init__`, such as `self.lines: list[CartLine] = []`
*When* the Knowledge Graph reads the bookshop project for Clean Engineering
*Then* each public field a constructor assigns is a property of its class
  *And* ExpressShipment has a baseClass edge to Shipment
  *And* Cart depends on CartLine, the class its list holds
  *And* `Catalogue.search`, which returns `list[Book]`, returns Book

#### Scenario: Hold a class its model document describes and its code declares as one node

Observed (`graph_bookshop_spec.py`, `graph_reading_spec.py`). Source: the person's decisions of 2026-11-22, "One thing is one node in the graph" (`.sessions/_backlog/one-thing-one-node-in-the-graph.md`), which replace their answer 3 of 2026-11-20 that the two were two nodes with an edge; defect r3-widget-08.

*Given* each module of the bookshop holds a class model in `.context` and the Python that declares its classes
*When* the Knowledge Graph reads the bookshop project for Clean Engineering
*Then* each class is one node, at its lines in the code
  *And* the node keeps its card in its own module's model as its place in markdown
  *And* the node keeps the code's measures and the stereotypes the model gives it
  *And* an operation only the model declares is a node under the class, at the model's line, read at the model fidelity
  *And* no edge joins one format to another

#### Scenario: Keep a model's class apart when its module's code cannot tell which class it means

Observed (`graph_reading_spec.py`).

*Given* a module's model describes the class Ledger, and two files of the module's code each declare a class Ledger
*When* the Knowledge Graph reads the project for Clean Engineering
*Then* the model's Ledger is a node of its own at its card, beside the two classes of code
  *And* a model of another module that describes Ledger is a node of its own too, since the module, not the name, says which class a model means
