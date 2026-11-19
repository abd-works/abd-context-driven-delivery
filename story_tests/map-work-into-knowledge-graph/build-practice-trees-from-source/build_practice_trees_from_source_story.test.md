---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Build Practice Trees From Source

Story map: [Build Practice Trees From Source](../../../.context/story-map.md#e-build-practice-trees-from-source). Session release-1-2-fixes.

**Evidence mode.** Every scenario here is *Observed*: it holds for the practices' graph readings today and names the spec that runs it. They were written after exploratory testing (defects widget-18, widget-21) showed a file could drop out of the graph without a word.

### Domain terms

- ++module card++ — a folder's `.context/module-context.md`, which makes the folder a module; a folder without one is a package.
- ++byte-order mark++ — the three bytes some editors put at the start of a UTF-8 file.
- ++scenarios file++ — a `*_story.test.md` file, which specifies stories by their names under `## Story:` headings.

> In steps: the bookshop's files are the examples below.

## Examples

### source files of the bookshop project

| file | holds |
| --- | --- |
| ++src/order.py++ | `class Order(:`, which is not Python; `src` has no module card |
| ++src/other.py++ | the class Other |
| ++shop/bom.py++ | the class BomOnly, after a byte-order mark |

### story files of the bookshop project

| file | holds |
| --- | --- |
| ++.context/story-map.md++ | Sell Books, Take Orders, with the stories Place Order and Cancel Order |
| ++story_tests/sell-books/take-orders/take_orders_story.test.md++ | one scenario each for the stories Gift Order and Wrap Order |

## Story: Read Modules Classes And Operations

### Evidence

| Source | Note |
|--------|------|
| `cdd_guidance/practices/clean_engineering/clean_engineering.md` `source-parses` | "A file that does not parse is read into no classes, so every other rule passes it without looking" |
| `cdd_guidance/practices/clean_engineering/model/code_read.py` `CodeRead._parsed` | "A file that does not parse is kept with the reason, so the source-parses rule reports it" |
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

## Story: Read Story Maps And Story Tests

### Evidence

| Source | Note |
|--------|------|
| The supervisor's card for defect widget-21, 2026-11-19 | "scenarios of a story not on the map: a violation, not silence" |
| `cdd_guidance/practices/stories/stories.md` `scenarios-name-a-story-on-the-map` | the rule added for it |
| Defect widget-21 | a scenarios file whose stories the map lacks added nothing to the graph and nothing said so |

#### Scenario: Keep and report the stories a scenarios file names that the map does not hold

Observed (`cdd_guidance/practices/stories/model/graph_reading_spec.py`).

*Given* ++.context/story-map.md++ holds the stories Place Order and Cancel Order
  *And* ++story_tests/sell-books/take-orders/take_orders_story.test.md++ specifies the stories Gift Order and Wrap Order
*When* the Knowledge Graph reads the bookshop project for Stories
*Then* Gift Order and Wrap Order are in the graph with their scenarios, under no epic
  *And* each carries a scenarios-name-a-story-on-the-map violation naming ++story_tests/sell-books/take-orders/take_orders_story.test.md++

#### Scenario: Report nothing for a scenarios file whose stories the map holds

Observed (`graph_reading_spec.py`).

*Given* ++story_tests/sell-books/take-orders/take_orders_story.test.md++ specifies the stories Place Order and Cancel Order
*When* the Knowledge Graph reads the bookshop project for Stories
*Then* Place Order and Cancel Order each hold their scenario
  *And* no story carries a scenarios-name-a-story-on-the-map violation
