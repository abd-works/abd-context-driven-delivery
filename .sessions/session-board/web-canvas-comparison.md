# Session board web page against the canvas

Measured on 2026-11-03. The canvas is `Main.dc.html` running under its own `dc-runtime.js`, served on 127.0.0.1. The web page is the live board at `http://127.0.0.1:8778`. Every number was read with `getBoundingClientRect` and computed styles, using the same method as `canvas-comparison.md`. Sizes are CSS px.

**How the two line up.** The canvas is a 1960 px artboard with a 440 px chat column on the left, so its board pane is 1519 px wide. The page was therefore measured at 1520 x 920, where a board column is the same width in both: edge 202.7, stage 347.5, gap 10, grid minimum 1488. At that size the column positions match exactly. Screenshots were also taken at 1600 x 920 and 1960 x 920. At 1960 the page's columns stretch, because the grid uses `fr` units, while the canvas board stays 1519 wide. That difference comes from the artboard, so it is not counted as a discrepancy.

**Safety.** Every request from the page other than GET or HEAD was intercepted. Two read-only listings that the page asks for with POST were answered locally and never reached the server: `POST /tickets/{t}/files`, which returned stub file lists, and `generate-commands`, which returned `[]`. Everything else would have been aborted, and nothing was. No action control was pressed.

Screenshots are in the scratchpad folder `...\scratchpad\wc\`, named `canvas-<state>.png` and `live-<state>.png`. Element dumps are named `d-<kind>-<state>.txt`.

## Ranked by how visible they are

| # | State | Canvas | Page | Severity | Likely source |
|---|---|---|---|---|---|
| 1 | Stage head ▾ in the details | The stage's action bar opens under that stage's own column, 347 wide | The bar opens under the **practice column** (grid column 1, 202 wide). Run wraps to a second line and the bar sits under the wrong stage | **bug** | `ticket/practice-grid-view.tsx:48` `page.board.stages.indexOf(stage)` always returns -1, because `board-client.tsx:33-38` builds new `ColumnClient` objects on every call to `stages`. Measured `grid-column: 1` |
| 2 | Header with a side panel open (files, help, report) | One line, 57 tall. The meta text wraps and the buttons stay on the right | Two lines, **97 tall**: Chat, Active session only, + Ticket, Refresh, and ⤢ wrap. The board loses 40 px. With two panels open at 1520 it grows to about 200 tall | visible gap | `board/board.css:38` `.board-header` with `flex-wrap: wrap`, plus the chat picker (`chat/chat-picker-view.tsx`) and + Ticket, which the canvas header does not have. Fix: no wrap, a shrinking meta, a narrower picker |
| 3 | Opening a card with ▾ | The card opens with its tiles only (145 tall for one tile). The bar appears inside a tile, under its heading, after the tile or a segment is hovered or pressed | The card opens with a card-level action bar above the tiles every time (**378 tall** with 5 tiles) | visible gap | `ticket/ticket-card-view.tsx:122` (`state.cardMenu`), set by `open-card-client.ts` on toggle |
| 4 | Details tiles | Name, a ✓ only when reviewed, a red `violations` link, ? | Name, **three action marks `○ ○ ○`** (generate, validate, review), then ✓ / violations, then ?, on every tile in the details and on the card | visible gap (also noted in the pane comparison) | `ticket/tile-view.tsx:19-33, 72` `ActionMarksView` |
| 5 | Details stage heads | All three are 46 tall, because the head row stretches | 38 / 40 / 46: each height follows its scope shape, so the row looks ragged | minor, but visible | `board.css:56` `.column-grid { align-items: start }` applies to the head row too. The canvas head row has no `align-items` (line 442 of the canvas) |
| 6 | Backlog item selected in the details | Path relative to the repository: `.sessions/_backlog/plugin.md`. No buttons | Absolute Windows path `C:\dev\...\.sessions\_backlog\claude-code-plugin.md`, plus an orange **Start** button | visible gap (Start is an addition not listed in canvas-differences.md) | `backlog-item/backlog-item-view.tsx:59, 63-65`, `item.path` |
| 7 | Backlog cards | A 20x20 bordered empty mark at the top right of every backlog card (the shared card template's `expand-mark`) | No mark | minor | `backlog-item-view.tsx:30-47` |
| 8 | Card hover | Background `--raised` **and** border `--muted`; the title turns orange | Background and title change, the border does not | minor | `board.css:94` lacks `border-color: var(--muted)` |
| 9 | Buttons with class `.action` (Refresh, + Ticket, Run next, Split, card ← →) | 13px Inter (`.board-root button { font: inherit }` beats `.action`). Refresh is 73.4 x 32, a card arrow 33.2 x 23 | **12px**. Refresh 69.7 x 31, a card arrow 32.4 x 22, the details buttons about 1px shorter | minor | `board.css:28` `.board-root .action { font-size: 12px }` |
| 10 | Tile action bar | List box 84 wide, padding 4/6. No mark before Run | List box **88** wide, padding 4/2, so the chips sit 4px further right. An extra generate step mark `○` sits before Run | minor | `board.css:145` `.action-choice`; `ticket/action-bar-view.tsx:55` `StepMarkView step={bar.generate}` |

## Further measured differences (minor)

| State | Canvas | Page | Source |
|---|---|---|---|
| BACKLOG / COMPLETE labels | Span 16 tall | 20 tall (line box), same position | `board.css:80` |
| Card title | 16 tall | 16.9 (the `line-height: 1.3` div), which makes the active card 104.9 tall against 101.9 | `board.css:97` |
| Files panel, card link | The `files` link on the card is underlined while its panel is open | Not underlined | `ticket-card-view.tsx:52-63` |
| Files panel, tabs | Wrap | One line with `overflow-x: auto`; a fourth tab is cut off at 600 wide | `board.css:234` |
| Help body | Plain text | Renders the source markdown: italics and `code` spans | `board/help-panel-view.tsx`. Arguably better |
| Two side panels at 1520 | Panels stay 640 and the board narrows to 239 | Panels shrink to 600 so the board keeps 320 | `board.css:19, 174` (`flex: 0 1 640px`, `min-width: min(320px,100%)`) |
| Details sideways scroll | scrollWidth 1519 | scrollWidth 1504 with the right padding lost (the board region is fine at 1520) | `board.css:166` |
| Dialog backdrop | Covers the board pane only | Covers the whole page, including side panels | `board.css:257`, `activation-view.tsx:90` |
| Report subtitle | `pml-web · code · 2026-10-28 18:05 UTC` | The report file path | `ticket/report-panel-view.tsx:14` |
| Opened on load | The active ticket's card is open | All cards closed | Decide: demo state or a rule |

## These match within 1px

Header at rest (57 tall, padding 12/16, brand mark, wordmark spacing 1.3px, 32x32 expand button); column grid and widths; stage head (35/40/46, inset 7, over-limit red border and count); IN PROGRESS / DONE labels; card padding 8/26/8/9, 3px active border, segments 14x7 with 3px gap, list/folder/files 26/40/33 with 10px gap; details bar 59 tall at 10/16 with a 16px title; grid corner 202.7 x 46; practice labels 32 tall with a 3px coloured edge and 28x16 switches; tiles 347.5 x 36 at a 48px pitch, opacity .45 for not started and .2 for off, orange border for next; open card width 347.5 with tiles 27 tall at a 33px pitch and unboxed 61px practice chips; tile bar 323.5 x 112 at padding 8, step controls 84 x 26, chips 26 x 26, Run 84 x 26 on the first line at the right, list/folder/files at the right of the review line; split grip 14 tall with a 72 x 3 line; files and help panels 640 wide at 1960, help header (kind, 26px title, Forge, ⤢, ×); board expanded (bar gone, region fills); details expanded (head at y 57); Active session only off (switch to grey; ← and → on cards that are not active become enabled in the canvas, and the page shows the same rule in `isLocked`); sideways scroll with a panel open (board region scrollWidth 1520 against client 960).

## States the page cannot show with this data

The canvas shows these, but the live board has only one active ticket and one backlog item, so nothing on the page can display them. The source has code for each:
- Reviewed tile: 7px green edge and ✓ (`tile-view.tsx:15, 73, 95`).
- Violations tile: red border and `violations` link (`tile-view.tsx:74-78, 91`); card `violations` link; violations band.
- A ticket in DONE, a card in COMPLETE, an over-limit WIP count.
- The details of a ticket that is not active: dimmed buttons, Switch to enabled, "Activate this session to run actions".
- Disabled ← and → on cards that are not active.
- The report panel. The page offered no `report` link: the behavior bar shows Run, validate (off), review, list, folder, files. The report was compared from source only (`report-panel-view.tsx`, `report-rule-view.tsx`, `board.css:174-221`). It has the same structure as the canvas, 26px numbers, Fix all as a ghost button and Fix in orange, with the subtitle difference noted above.

## Compared from source only (unsafe on the live board)

- **Activate dialog** (`activation-view.tsx`, `board.css:257-268`). It matches the canvas: 480 wide, padding 18, gap 14, facts grid 72px, options 28 tall, Cancel then a primary Activate. Differences: it says "Branch X already exists" or "Worktree already exists" when they exist; it adds a CLOSE heading when closing; and the backdrop is page-wide (see above).
- **Backlog draft** (`backlog-item-view.tsx:7-28`, `board.css:83-86`). Title input, a 5-row text box, padding 6/8 on `--bg`, Add (primary, small) and Cancel. These match the canvas at padding 2/8, 11px. The page's `.action.small` is `3px 8px`, which makes Add and Cancel 2px taller than the canvas's 19.
- **WIP edit field**: 44 wide with an orange border, same in both (`board.css:69`).

## Intentional additions (not bugs)

These are listed in `retired/harness/kanban/canvas-differences.md`:
- Archive in the details bar.
- + Ticket in the header.
- Ticket names in the dialog.
- The band shown when the server is lost.

These are new and not yet listed there:
- The Chat picker in the header. The canvas has a chat column instead.
- The Start button on a backlog item.
- The violations band with Show and Satisfy.
- The toasts stack.
