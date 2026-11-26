# Selecting the second scenario of a markdown story marks the first scenario's lines and leaves the selected scenario folded, because the story's examples sit under every scenario at the first scenario's heading

- **Charter:** Round 3, second pass - explore the Files app's graph view on the combined project in a real browser (checks 5 and 6)
- **Tester:** Lens
- **Story:** Review Generated Work In File Viewer > Explore Graph In Files App ("Selecting a node opens its file at its lines"; "An open file then opens only the folds holding a selected node", `harness/files_app/.context/module-context.md`). No scenario selects a second scenario of a markdown story.
- **Module and class:** the Stories markdown reader, which records each example of the story's `### Examples` tables under every scenario with the first scenario's heading as its line (`stories:Example:...add_book_to_cart_story.test.md:Tiny Tales` answers lines 42 to 42); `space/session/node_spans.py` `NodeSpans._below` then widens a scenario with them (`_used_from_elsewhere` leaves out only an example of another file). Not in the Files app files another chat was editing.
- **Severity:** wrong result

## Steps

Sandbox `C:\dev\_et\round3\lens\work`; script `C:\dev\_et\round3\lens\drv\w7.py`. `story_tests/fill-cart/add-books/add_book_to_cart_story.test.md` holds `### Examples` at line 19 (tables `book` and `cart`), `#### Scenario: Add a book in stock` at line 42 and `#### Scenario: Refuse a book out of stock` at line 55.

1. In the graph view open **stories** > **Fill Cart** > **Add Books** > **Add Book To Cart**.
2. Select the scenario **Refuse a book out of stock**.
3. Open **Add a book in stock** and look at what it holds; select its example **Grand Atlas**.

## Expected

The file opens with lines 55 to 60 marked and unfolded. Each example shows once, where the story declares it (the Examples table, lines 19 to 33), or under the scenarios that use it.

## Actual

- `graph-node-ranges` answers lines 42 to 60 for **Refuse a book out of stock**. The page marks lines 42 to 60, opens the first scenario, and leaves `#### Scenario: Refuse a book out of stock` folded at line 55: the person reads the scenario they did not select. Same in `change_cart_line_quantity_story.test.md`: **Remove the line at quantity zero** answers 28 to 47, from the first scenario's heading.
- Both scenarios of the story list all four examples (Tiny Tales, Grand Atlas, empty cart, cart with Tiny Tales) as their own entries, so the tree shows 13 Example rows for the 8 Example nodes the graph counts (`graph.inventory`), and **Add a book in stock** shows Grand Atlas, which it does not use.
- Selecting the example **Grand Atlas** under **Add a book in stock** marks that scenario (42 to 53); nothing leads to the example's line in the table (line 25).

Screenshot: `C:\dev\_et\round3\lens\shots\20-s-scenario-refuse-out-of-stock.png`, `20-s-example-grand-atlas.png`.

## Tier that should catch it

Unit (`space/session/session_graph_spec.py` or the graph view examples in `space/session/graph_view_examples.py`): the examples there are of story tests in code with an examples module; no markdown story with an Examples table and two scenarios is asked for its second scenario's lines.

## Also seen by
