# A step of a story test in code whose text holds a quoted phrase is placed at line 1, so selecting it opens the top of the file with the step folded away, and its scenario marks the whole file

- **Charter:** Round 3, second pass - explore the Files app's graph view on the combined project in a real browser (checks 5 and 6)
- **Tester:** Lens
- **Story:** Review Generated Work In File Viewer > Explore Graph In Files App ("Selecting a node opens its file at its lines", `harness/files_app/.context/module-context.md`). No scenario covers a step with a quote in it.
- **Module and class:** the Stories reader of story tests in code, which gives the step its lines (the node's `source.start_line` is 1); it shows through `space/session/node_spans.py` `NodeSpans` and `session.graph_node_ranges`. Not in the Files app files another chat was editing.
- **Severity:** wrong result

## Steps

Sandbox `C:\dev\_et\round3\lens\work`; script `C:\dev\_et\round3\lens\drv\w7.py`.

`story_tests/check-out/place-order/submit-order/submit_order_story.test.py` line 30 reads `with then("the Bookshop refuses with \"the cart is empty\""):`, and `story_tests/check-out/confirm-order/view-order-confirmation/view_order_confirmation_story.test.ts` line 42 reads `then("the Bookshop refuses with \"order 9999 is not found\"", () => {`.

1. In the graph view open **stories** > **Check Out** > **Place Order** > **Submit Order** > **Refuse an empty cart**.
2. Select the step **then the Bookshop refuses with "the cart is empty"**.
3. Select the scenario **Refuse an empty cart**.

## Expected

The step opens `submit_order_story.test.py` with line 30 marked and shown; the scenario marks lines 25 to 33.

## Actual

- `graph-node-ranges` answers `submit_order_story.test.py` lines 1 to 32 for the step (its own line 1, widened by the `but` step below it at 32), and 1 to 32 for the scenario. The page marks the file from line 1 and leaves `with story("Submit Order"):` folded at line 12, so neither the step nor the scenario is on show.
- In the TypeScript story test the step `then the Bookshop refuses with "order 9999 is not found"` answers lines 1 to 1, and its scenario `Refuse an order number the Bookshop does not keep` lines 1 to 45, the whole file.
- The step's connector id carries the line too: `stories:observes:stories:Then:story_tests/.../submit_order_story.test.py:1:11387633`.
- The other steps of the same files, which hold no quote, answer their own lines (the `when` at 28, the `but` at 32).

Screenshot: `C:\dev\_et\round3\lens\shots\20-s-step-then-quoted-py.png`, `20-s-scenario-refuse-empty-cart-py.png`.

## Tier that should catch it

Unit, in the specs of the Stories code reader: its example steps hold no escaped quote, so the search for the step's text in the source (written `\"` there, read back as `"`) was never run on one.

## Also seen by
