# Selecting a graph node whose file has moved or gone leaves another node's file on show, with no word that the node's source is not there

- **Charter:** Round 2 - explore the Kanban board's pages and the Files app's graph view in a real browser as a person whose tickets and files change under the page
- **Tester:** Pixel
- **Story:** Review Generated Work In File Viewer > Explore Graph In Files App (a node selected opens its source at its lines). No scenario covers a node whose file moved after the graph was read.
- **Module and class:** `harness/files_app/app/files/files-graph.ts` (selecting a node, reading `session.graph_node_ranges`) and `files-graph-view.tsx`; `space/session/session.py` `Session.graph_node_ranges`, which answers 200 for a node whose file is not there.
- **Severity:** misleading message (the person selects Class Cart and reads Order's code under it; nothing says the graph is older than the folder)

## Steps

Sandbox: `C:\dev\_et\pixel\work\repo`, branch and session `pixel-files`, with `src/cart.py` (class Cart, operation add) and `src/order.py` (class Order, operation total); Files server on 8902 (`C:\dev\_et\pixel\work\scripts\stack.py`); script `C:\dev\_et\pixel\work\scripts\g1.py`.

1. Open `http://127.0.0.1:8902/?files=pixel-files&fidelity=stories-story-map,clean-engineering-code,stories-acceptance-tests&project=C:\dev\_et\pixel\work\repo`, press **All session files**, show every format, press **Graph**, and open every branch.
2. Select **Class Cart**: `src/cart.py` opens. Select **Operation total**: `src/order.py` opens. (Both as promised.)
3. On disk, move `src/cart.py` to `src/moved/cart.py` and move `src/order.py` out of the repository.
4. Select **Operation add**, then **Class Cart**, then **Operation total**.

## Expected

The page says the node's file is not where the graph has it (or reads the graph again), and does not leave another node's source under the selection.

## Actual

Each selection sends `graph-node-ranges` with the old node id (`clean_engineering:OoadClass:src/cart.py:Cart`), which answers 200. The open file stays `src/order.py` with Order's lines for **Operation add** and **Class Cart**, and for **Operation total** too, although `src/order.py` is no longer on disk: the text shown is the one read before the move. No notice, no failed request, nothing in the console; the tree keeps both classes. Screenshot: `C:\dev\_et\pixel\work\shots\g1-moved.png`.

Same family as pixel-01 (a file gone from disk reads as no text, with no sign it is gone).

## Tier that should catch it

e2e (`explore-graph-in-files-app` browser story test): the graph and the folder only disagree on a real folder that changes after a real graph read; the unit specs stub the ranges.

## Also seen by

## Confirmation (Rivet, round 2)
- Result: confirmed
- What I ran and saw: my own stack (`pstack3.py`: cdd server on 8913, Files server on 8914, headless Chromium) on a fresh repository with `src/cart.py` (Cart, add) and `src/order.py` (Order, total). Before the move, **Class Cart** shows Cart's lines and **Operation total** shows Order's. After moving `cart.py` to `src/moved/` and `order.py` out of the repository, **Operation add**, **Class Cart** and **Operation total** each send `graph-node-ranges`, each answered 200, and the editor keeps `class Order: / def total(self): / return 1` under all three; no console error, no notice. In an earlier run where the file open before the move was the moved file itself, the editor went empty instead, which is pixel-01's face of it.
- Cause, if you found it: not looked into beyond the report's own (`Session.graph_node_ranges` answers 200 for a node whose file is not there, and `files-graph.ts` then leaves the open file as it is).
- Shares its cause with: pixel-01 (a file gone from disk is answered as no text, with nothing that says it is gone)

## Confirmation (Pixel, closing)
- Result: confirmed
- What I ran and saw: my own stack (`C:\dev\_et\pixel-close\scripts\stack.py`: cdd server on 8921, Files server on 8922, headless Chromium, 1600 by 900) on a copy of the round's repository, with the report's script (`scripts\g1.py`). With the files in place, **Class Cart** opens `src/cart.py` and **Operation total** opens `src/order.py`. After `src/cart.py` moved to `src/moved/cart.py` and `src/order.py` moved out, **Operation add**, **Class Cart** and **Operation total** each send `graph-node-ranges` with the old node id, each answers 200, and the open file stays `src/order.py` with Order's lines; no notice, no failed request, nothing in the console. Asked directly, `POST /api/session/pixel-files/graph-node-ranges` for `clean_engineering:OoadClass:src/cart.py:Cart` answers the range of lines 1 to 3 while the file is there and `[]` once it has moved, and `session/pixel-files/file` for `src/cart.py` answers 200 with an empty text.
- Cause, if you found it: `space/session/node_spans.py` `NodeSpans._lines_file` answers no file for a node whose file is not on disk, the same answer it gives a node read from no lines, so `Session.graph_node_ranges` answers no ranges and `files-graph.ts` `select` returns at `if (!ranges.length) return` without a word. The graph still holds the node.
- Shares its cause with: pixel-01 (a file gone from disk answered as nothing, with no sign it is gone)
