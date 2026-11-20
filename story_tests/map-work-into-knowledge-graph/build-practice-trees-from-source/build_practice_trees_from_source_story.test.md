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

### story files of the second bookshop project

The project round 3 of exploratory testing loaded, kept as `cdd_guidance/practices/stories/model/fixtures/bookshop`.

| file | holds |
| --- | --- |
| ++.context/story-map.md++ (second bookshop) | 16 stories, Pack Order, Cancel Order, Submit Order, Add Book To Cart and Change Cart Line Quantity among them |
| ++add_book_to_cart_story.test.md++ | two scenarios of Add Book To Cart under a Background with a Given and an And |
| ++change_cart_line_quantity_story.test.md++ | two scenarios of Change Cart Line Quantity and no Background |
| ++pack_order_story.test.py++ | two scenarios of Pack Order, whose When calls `orders.load("1001").pack()`, with the examples `paid_order` and `unpaid_order` |
| ++confirm-order.story.shared.ts++ | the scenarios "Cancel a submitted order" and "Keep the total of a cancelled order" of Cancel Order |
| ++confirm-order.story.ui.spec.ts++ | the scenario "Cancel a submitted order" of Cancel Order, as its screen runs it |
| ++submit_order_story.test.py++ | two scenarios of Submit Order |

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

#### Scenario: Hold the same graph after a refresh of a Stories file nobody changed

Observed (`cdd_guidance/practices/stories/model/story_refresh_spec.py`). Source: `Graph.refresh`, "Every other node stays as it was"; defect r3-cog-02.

*Given* the Knowledge Graph holds the second bookshop project, read from its story map, scenarios files, and story tests
*When* the Knowledge Graph refreshes ++.context/story-map.md++ (second bookshop), which nobody changed
*Then* each story still holds the scenarios its story tests gave it
  *And* the graph holds the nodes and edges it held before the refresh

#### Scenario: Hold each story once after a refresh of one story test

Observed (`story_refresh_spec.py`). Defect r3-cog-02.

*Given* the Knowledge Graph holds the second bookshop project
*When* the Knowledge Graph refreshes ++pack_order_story.test.py++, which nobody changed
*Then* Pack Order is in the graph once
  *And* it sits under the epic the story map gives it
  *And* the scenarios written in markdown and those written in code are all still in the graph

#### Scenario: Give a story the scenarios of every story file in code that specifies it

Observed (`cdd_guidance/practices/stories/model/story_tests_on_map_spec.py`). Source: `StoryTestScenarios.take`, "a story written in a shared story file and a screen spec holds the scenarios of both"; defect r3-sparky-08.

*Given* ++confirm-order.story.shared.ts++ and ++confirm-order.story.ui.spec.ts++ both specify Cancel Order
*When* the Knowledge Graph reads the second bookshop project for Stories with its story map
*Then* Cancel Order holds "Cancel a submitted order" and "Keep the total of a cancelled order"
  *And* each scenario is in the file that writes it

#### Scenario: Keep a story test's code and examples when its story map is read with it

Observed (`story_tests_on_map_spec.py`). Defect r3-sparky-08.

*Given* ++pack_order_story.test.py++ specifies Pack Order, which ++.context/story-map.md++ (second bookshop) holds
*When* the Knowledge Graph reads the second bookshop project for Stories and Clean Engineering
*Then* the When of Pack Order invokes `pack` of Order
  *And* the examples `paid_order` and `unpaid_order` are in the graph

#### Scenario: Record a Background only on the story whose scenarios file writes it

Observed (`cdd_guidance/practices/stories/model/graph_reading_spec.py`). Source: commit 4d47fdf8e, "A Background its story's scenarios share is recorded in the graph, so graph rules see its steps"; defect r3-sparky-03.

*Given* ++add_book_to_cart_story.test.md++ has a Background and ++change_cart_line_quantity_story.test.md++ has none
*When* the Knowledge Graph reads the second bookshop project for Stories
*Then* Add Book To Cart holds one Background, in ++add_book_to_cart_story.test.md++, given by its Given step with the And chained onto it
  *And* Change Cart Line Quantity holds no Background

#### Scenario: Keep and report a story test in code whose story left the map

Observed (`story_tests_on_map_spec.py`). Source: `scenarios-name-a-story-on-the-map`, "scenarios the map cannot place are otherwise left out of every check without a word"; defect r3-cog-04.

*Given* ++submit_order_story.test.py++ specifies Submit Order
  *But* ++.context/story-map.md++ (second bookshop) holds no Submit Order
*When* the Knowledge Graph reads the second bookshop project for Stories
*Then* Submit Order is in the graph with its two scenarios
  *And* it sits under the epic its story test's folders name
  *And* it carries a scenarios-name-a-story-on-the-map violation naming ++submit_order_story.test.py++

#### Scenario: Read story tests in code on a load of the whole working copy

Observed (`story_tests_on_map_spec.py`). Source: `Graph.load_practice_roots`, "the Graph app's whole load"; defect r3-cog-03.

*Given* the second bookshop project holds scenarios in markdown and story tests in Python and TypeScript
*When* the Knowledge Graph loads the whole working copy of the second bookshop project
*Then* the graph holds the scenarios a load of the same files holds, those written in code among them
  *And* their steps invoke the operations a load of the same files links them to
