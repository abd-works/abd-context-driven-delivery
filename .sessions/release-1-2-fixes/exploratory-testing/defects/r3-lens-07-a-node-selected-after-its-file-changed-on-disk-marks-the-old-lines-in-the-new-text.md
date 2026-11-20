# A node selected after its file changed on disk marks its old line numbers in the new text, so another member is marked and opened and the selected one stays folded

- **Charter:** Round 3, second pass - explore the Files app's graph view on the combined project in a real browser (checks 5 and 6)
- **Tester:** Lens
- **Story:** Review Generated Work In File Viewer > Explore Graph In Files App ("Selecting a node opens its file at its lines"). No scenario covers a file changed after the graph was read; the graph view is read again only "whenever the bar lists other files" (`harness/files_app/.context/module-context.md`).
- **Module and class:** `harness/files_app/app/files/files-graph.ts` `FilesGraph.select` and `follow` (its `readKey` is the listed paths and the node filter, so a changed file is no reason to read), and `space/session/session_explorer.py` `graph_node_ranges`, which answers the lines the graph read earlier beside the file's text as it is now. Not in the Files app files another chat was editing.
- **Severity:** wrong result (the Files app is where a person reviews files a chat is changing, so the file under a node changes often)

## Steps

Sandbox `C:\dev\_et\round3\lens\work`; script `C:\dev\_et\round3\lens\drv\w12.py` (step 4).

1. In the graph view open **clean_engineering** > **src** > **ordering** > **Order** (of `src/ordering/order.py`) and select **Operation place**: `graph-node-ranges` answers lines 21 to 27, and `def place` is marked and open.
2. On disk, add five lines at the top of `src/ordering/order.py` (`# one` to `# five`). `place` is now at lines 26 to 32.
3. Select another node, then **Operation place** again.

## Expected

The lines of `place` as the file is now (26 to 32) are marked and open; or the page says the graph is older than the file and reads it again.

## Actual

`graph-node-ranges` still answers lines 21 to 27. The page shows the new text (the five comment lines lead the file) and marks lines 21 to 26 of it, which are now `def __init__` and its body, opened; `def place` sits folded at line 26 with only its first line under the mark. Nothing says the graph is stale; no request reads the graph again, and the tree keeps the old graph until the list of files changes. Pressing the practice or format chips off and on reads it again; there is no control that says so.

This is the changed-file face of pixel-08 (a moved file), which now refuses; a changed file is not noticed.

Screenshot: `C:\dev\_et\round3\lens\shots\43-after-edit-on-disk.png`.

## Tier that should catch it

e2e (`story_tests/review-generated-work-in-file-viewer/explore-graph-in-files-app/explore-graph-in-files-app.story.ui_e2e_spec.py`): only a real file changed under a real graph shows it; the unit specs stub the ranges.

## Also seen by
