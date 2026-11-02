# Session board audit

Gaps between the requirements and the production pane, ranked by how visible they are. This comes from reading the code; the pane was not run.

File references without a folder are in `harness/kanban/pane/hooks/kanban/`. "story" is `harness/kanban/.context/story-map.md`. "canvas" is the Board canvas, `Main.dc.html`.

| # | Requirement | Reference | What the pane does | Fixable? | Decision |
|---|---|---|---|---|---|
| 1 | A tile opens with the default-format chips already picked (`defaultPicks`), so Run is ready | canvas 1616-1617, 1723-1726 | Opens with `picked: []`, so Run stays dim: ticket-client.ts:188, tile-bar.tsx:56-59; test at register.test.tsx:1312 expects this | Yes; column JSON lists formats but no default (board.py:259); `default_format` is at harness/guidance/guidance.py:35 | Fix, in Python and pane; change the test |
| 2 | A chip means a group; each fidelity uses one format from it (`groupFormat`, `chosenFormats`) | canvas 1653-1656, 1727-1730 | The code chip sends every offered code format: ticket-client.ts:218-225, 232 | Yes, with the default format | Fix |
| 3 | With no branch, the leaving ticket shows "none yet" and commit, push and merge are off and unchecked | canvas 1395, 1406-1416 | Always shows the title as branch, options live, commit and push on: activation-view.tsx:62-63, ticket-client.ts:269-277. `_leave` acts anyway (ticket.py:378-383) and could commit and push the checked-out branch | Yes | Fix first; guard `_leave` in Python too |
| 4 | A disabled practice's tiles fade to 20%, don't open, and its label dims | canvas 2081, 2083, 2104 | `TileView` ignores enablement: ticket-view.tsx:214, 228, 338-345; `dimColor` has no effect on coloured text: ticket-view.tsx:367-369 | Yes | Fix with `faded` |
| 5 | Each fidelity shows Generate, Validate and Review as to do, in progress or done | story 158 | Closed tile shows only a final check or "violations"; open bar has no Generate mark or in-progress mark: tile-bar.tsx:83-90, 114-118. `ACTION_MARKS` is unused | Yes | Fix |
| 6 | A toast shows when a ticket moves, including In progress to Done and to the Backlog | story 37; canvas 1918-1919, 1949 | Only when the column changes; a ticket leaving for the Backlog is never compared: board-client.ts:112-118 | Partly | Fix both |
| 7 | Chips reflect what was just generated, and Run clears the picks | canvas 1672-1673, 1772, 1776 | `tile.files` is read once at open; picks stay set: ticket-client.ts:188, 230-238 | Yes | Fix |
| 8 | The Files panel reflects current generated state | canvas 1260, 1217 | Snapshot at open; only the report is re-read: side-panel-client.ts:71-73, register.tsx:56-59 | Yes | Fix |
| 9 | A card shows title, age and next step | story 54 | Title and age only; the canvas card also has no next step (canvas 255-256) | Yes | Canvas wins: correct the story |
| 10 | The selection follows the ticket acted on: Activate, Close, ▾, opening a tile, new backlog item, Start | canvas 1383, 1390, 1598, 1624, 1874, 1958 | None of these select: ticket-client.ts:175, 268, backlog-item-client.ts `add`, `start` | Yes | Fix |
| 11 | Status messages for activate, close, practice on/off, added and started | canvas 1404, 1445, 1490, 1875, 1960 | No toast for any: ticket-client.ts:298-303, 142-145 | Yes | Fix |
| 12 | With Active session only on, list boxes are disabled too | story 112; canvas 283 | Action list stays live on a locked ticket: tile-bar.tsx:49, 52 | Partly; `Select` has no disabled prop | Draw dim text in its place; mobile Buttons take a no-op |
| 13 | The card's violations link shows the rules of every fidelity with violations | canvas 1184-1190, 1355 | Opens only the first fidelity's report: ticket-view.tsx:197 | Yes | Fix with one domain operation and one tool, keeping one action to one MCP call |
| 14 | Pressing a segment opens the card on that fidelity | canvas 1990-1993 | The segment Box has no press handler; canvas-differences wrongly says it selects the card | Not at the canvas's size: a Client has no Svg and reports whole cells, while segments are 10px apart | Do not build; record the true reason. The mark opens the card |
| 15 | Moving a ticket moves its open bar to the next tile; moving it to the Backlog closes its card, tile, files and report | canvas 1913-1916, 1943-1946 | Tile isn't updated and the bar disappears: ticket-view.tsx:300, ticket-client.ts:38-40 | Yes | Fix |
| 16 | Panels stay usable when several are open | story 83-86 | Main width not clamped; panels run off the edge: view-context.ts:46, side-panel-view.tsx:336 | Yes | Shrink panels to the room left |
| 17 | Chip states: on, done (green), and "n of m done" | canvas 1667, 1672-1673, 1649 | A check shows if any fidelity has the format; no green: tile-bar.tsx:26-27, 35 | Yes | Fix with a plain Button holding Text |
| 18 | A stage head in the details opens its bar on hover | canvas 450, 469, 1803 | Opens only on a ▾ press: ticket-view.tsx:351 | Yes | Fix with `tile-hover` |
| 19 | Files tabs run markdown, code, diagram | canvas 880, 1223-1227 | Drawio comes first, so the panel opens on raw XML: side-panel-client.ts:17, 55-60 | Yes | Fix the order; keep one tab per format as story 264 says |
| 20 | When held on violations, Run next says "fix violations" | story 198; canvas 1854 | Says "Run next: satisfy": ticket-client.ts:88-90, ticket-view.tsx:479 | Yes | Fix |
| 21 | Run next on generate renders the earlier fidelity first when formats differ | story 216; canvas 1513 | Fills plain `/actions-generate`, skipping `ticket.generate_commands`: ticket-client.ts:166-168 | Yes | Fix |
| 22 | Run is off for render with nothing to render, and off with no formats | canvas 1766, 1787 | No source check: tile-bar.tsx:56-59; sketch, iterate and document run with no format | Yes | Follow the canvas |
| 23 | Practice help heads its rules "SHARED RULES", and hides the section when empty | story 187; canvas 1330-1331 | Always "RULES", always drawn: side-panel-view.tsx:217-218 | Yes | Fix |
| 24 | The help head shows a practice label in its colour, plus stage or "Practice overview" | canvas 757-758, 1321-1324 | Title only: side-panel-view.tsx:261-267; titles are the class name: board.py:141 | Yes | Fix |
| 25 | The Files head names the fidelities | canvas 685, 1263 | Shows the ticket name: side-panel-view.tsx:255-257 | Yes | Fix |
| 26 | A panel keeps its dragged width when reopened | canvas 1294, 1301, 1378 | Every open resets to 60 columns: side-panel-client.ts:33, 73, 127 | Yes | Fix |
| 27 | Tooltips on chips, step marks, expand, the hide toggle and tab paths | canvas 289, 299, 307, 445, 728 | None | Partly; `Button` has no title prop | Record in canvas-differences |
| 28 | Fix names the file and line | canvas 1141, 1151 | Sends the location without its line: side-panel-view.tsx:157, ticket-client.ts:248-250 | Yes | Fix |
| 29 | The WIP field closes on Enter, Escape or blur | canvas 1122 | Closes only on submit: board-view.tsx:115 | Partly; `Input` has no blur or Escape event | Add a × cancel control; record the difference |
| 30 | With the server lost, the pane says so and asks for it | story 34; rule `fail-loud-on-mcp` | Stored board stays drawn with just a status line: register.tsx:157-158, board-client.ts:98-100, 127 | Yes | Fix: a band across the pane's top saying what failed |
| 31 | With no enabled practice, validate, review and Run are off | canvas 1738-1740, 1765 | `every` on an empty list passes: tile-bar.tsx:61, 84-88, 114 | Yes | Fix |

## Not covered by the audit

- Canvas lines 140-250, 325-440, 520-590, and 740-799 were read only in part. Line 818 was skipped.
- `panel-grip.tsx`, `split-grip.tsx`, `board-scrollbar.tsx`, and Python-only stories were not checked.
- `canvas-differences.md` opens with "Everything not listed here was changed to match", which is not true until these gaps are closed.
