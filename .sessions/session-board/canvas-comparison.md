# Board pane against the canvas

Written state by state, so an interruption loses nothing. Canvas values come from the running prototype (`Main.dc.html` under its own `dc-runtime.js`, served locally) through `getBoundingClientRect` and computed styles, unless a line says otherwise. Pane values come from Windows UI Automation and screenshots of the running desktop app.

## How the two are measured

| Fact | Value | How it was established |
| --- | --- | --- |
| Display scale | 192 dpi, so 2 physical px = 1 canvas CSS px | `GetDeviceCaps(LOGPIXELSX)` |
| Canvas board pane | 1519 by 920 CSS px; 879 wide with one side panel, 239 with two | Rendered |
| Pane's board region | about 1640 physical = 820 CSS px wide with the chat beside it | UI Automation and screenshot |
| One column | 13.4 physical = 6.7 CSS px (`ch`) | Stage pitch 716 physical at 53.4 columns |
| One row | 37 physical = 18.5 CSS px (`lh`) | Client region heights |
| Canvas at the pane's width | Compare against the canvas with one panel open (879 CSS px); a board column is the same width in both, so positions inside a column compare directly | Rendered |

## What the desktop renderer does with a Box

Read from the app's own bundle (`ion-dist.asar`, `c2719cf1b-*.js`) because "the engine cannot" has been wrong repeatedly here.

| Prop | Becomes | Consequence |
| --- | --- | --- |
| `width`, `left`, `right`, a number across | `ch` | Columns are 6.7 CSS px |
| `height`, `top`, `bottom` | `lh` | Rows are 18.5 CSS px |
| padding, gap, a number down | `calc(n * 1lh)` inside a Pane | `gap={1}` down is 18.5 CSS px where the canvas uses 6 to 8 |
| padding, gap, a step name | The app's own scale, in rem | `xs` to `xl`, the way to reach the canvas's 6 to 14 CSS px |
| `borderStyle` | A 1px border and a default `padding: pad.md pad.lg`, overridden by any padding prop | A bordered Box with no padding prop is much larger than its border, which is why the card's move buttons do not fit |
| `bold` border | 2px | |

The step sizes below are inferred, not read: `pad.lg` measured 28 physical px on a bordered Box, which fits the app's comfortable density at a 14px rem. That gives pad `xs` 5, `sm` 7, `md` 10.5, `lg` 14, `xl` 21 and gap `xs` 7, `sm` 10.5, `md` 14, `lg` 24.5, `xl` 35 CSS px. Confirm them on the first install that uses a step.

## What this run covers

The pane on screen was 0.4.7: `←`, `Activate`, and `→` sit on one line and `→` runs past the card, which only the 0.4.7 change produces. Installed `0.4.7` is byte-identical to the working tree.

The user was pressing the pane by hand during the run, then closed it at 12:02. **Measured on the real pane:** board at rest, board expanded, opened card with its action bar, files panel, header, and the details region at rest. **Not measured on the real pane:** help, report, the dialog, the details tile bar, Active session only off, and the Backlog draft. Canvas values for those are recorded so the comparison can finish when a board is open. Pane values are physical px / 2, from UI Automation where it reported them and from the screenshots otherwise. All sizes are CSS px.

## Board at rest

| Measure | Canvas | Pane 0.4.7 | Result | Closable |
| --- | --- | --- | --- | --- |
| Edge column width | 202.7 | 205 | match | |
| Stage width | 347.5 | 351 | match | |
| Stage pitch | 357.5 | 358 | match | |
| Gap between columns | 10 | 7.5 | gap | Yes: `columnGap="sm"` |
| Board's top padding | 14 | 8.6 | gap | Yes: step in place of a row |
| Stage head inset from its column | 7 | 22 sideways, 20 down | gap | Yes: `padding="xs"` on the head's wrapper |
| Stage head width | 333.5 | 307 | gap | Follows from the inset |
| BACKLOG label inset | 13 | 22 | gap | Yes: step padding |
| Card width in a stage | 160.8 | 150 | gap | Yes: list gap and stage inset |
| List pitch (IN PROGRESS to DONE) | 169 | 157 | gap | Yes, same cause |
| Card height, no violations | 103 | 118 | gap | Yes: the moves line is the excess |
| Gap between cards | 8 | 10 | close | `gap="xs"` |
| list / folder / files widths | 26 / 40 / 33 | 27 / 44 / 33 | match | |
| Gap between those links | 10 | 6.5 | gap | Yes: `columnGap="sm"` |
| `←` button on a card | 33 by 23.5 | 52 by 41 | **gap** | Yes: `padding={0}` on the bordered Box; its default padding is the excess |
| Activate button on a card | about 60 | 86 | **gap** | Same |
| `→` on a card | inside the card | **ends 40 past the card and is clipped, so a pointer cannot reach it** | **bug, new in 0.4.7** | Yes: same fix. 0.4.7 removed the wrap without removing the Box's default padding |
| Segments | 14 by 7 | 14 by 7 | match | |
| Expand mark | 20 by 20, bordered | 22 by 19, no border | gap | Yes: a bordered Box with `padding={0}` |
| Opened on load | Active ticket's card open | All closed | gap | Decide: the canvas's demo state or a real rule |

## Sideways scrollbar

The user called this the most obvious issue. It is drawn in one layout and missing in the other.

| Measure | Canvas | Pane 0.4.7 | Result | Closable |
| --- | --- | --- | --- | --- |
| Split layout | Bottom of the board region | Drawn there, thumb 50% of the track | match | |
| **Board expanded** | Bottom of the region | **Not on screen** | **bug** | Yes, see below |
| Thickness | 15 track | 18 solid slab | gap | Yes: thumb `height="40%"`; percentages pass through to CSS |
| Colour | Scrollbar on a dark track | `#71717A` thumb on `#111113` | gap, looks heavy | Yes, with the thinner thumb |

**Cause when expanded:** `regionRowsOf` takes `HEADER_ROWS = 2`. The real header is 3.4 rows on one line and 3.8 or more when it wraps, because a number of rows of padding is whole `lh` and its Buttons are 1.4 `lh` tall. So the region plus the bar overrun `height={bodyRows}`, and `overflow="hidden"` cuts the bar off. The split layout survives only because its bottom region absorbs the overrun.

**Fix:** stop computing it. Give the expanded region `flexGrow={1}`, `minHeight={0}`, and the bar `flexShrink={0}`, and the bar stays at the bottom however tall the header is. `height` in rows is only needed for the split.

## Header

| Measure | Canvas | Pane 0.4.7 | Result | Closable |
| --- | --- | --- | --- | --- |
| Lines at the pane's width, no panel | 1 at 1519 wide | 2: Refresh and expand wrap | gap | Yes: no wrap, and truncate the meta text |
| Lines with a panel open | not measured at 879 wide | 4, at 119 tall | **gap**, board loses 60 | Yes, same |
| Height | 57 | 70 | gap | Yes: `paddingY="md"` |
| Padding | 12 by 16 | 18.5 by 14 | gap | Yes |
| Refresh | 73 by 31.5 | 64 by 26 | close | Surface's native Button |
| Expand | 32 by 32 | 32 by 26 | close | Surface's native Button |
| Active session only switch | 28 by 16 | Glyph, 32 by 19 | known | Listed in canvas-differences.md |
| + Ticket | Absent | Present | known | Stays: listed |

## Details region

| Measure | Canvas | Pane 0.4.7 | Result | Closable |
| --- | --- | --- | --- | --- |
| **Action buttons** | Always in the pane, right-aligned | **Past the pane's right edge at rest; sideways scrolling is the only way to them** | **bug** | Yes: move `DetailHeadView` out of `WideRowsView`. The canvas's head sits above the part that scrolls |
| Details' expand toggle | In the pane | Past the right edge, same cause | **bug** | Same |
| Details head height | 58 | 52 | close | |
| Practice column left | 16 | 8.5 | gap | Yes |
| Grid under board columns | Same x as each column | Off by up to 7.5, changing along the board | **gap** | Yes: the grid uses percentages and the board uses `columnWidthOf`; use one |
| Stage head height | 47 | 41 | close | |
| Tile pitch | 48 | 50 | match | |
| Tile contents | Name, ✓ when done, ? | Name, three action marks, ? | gap | Decide: the marks may be wanted |
| Region clips at its bottom | Scrolls | Scrolls under the wheel | match | |

## Opened card

Canvas values are for `alpha`, with its five tiles and the action bar always present.

| Measure | Canvas | Pane 0.4.7 | Result | Closable |
| --- | --- | --- | --- | --- |
| Left | Its own card's left | 22 left of it | gap | Partly: position is in columns |
| Top | Its own card's top | Moved up to fit in the pane | gap | Yes once it is shorter |
| Width | 347.5, the stage | 363, 48% of the pane | gap | Yes: use the stage's width |
| Height | 374 | 546 | **gap** | Yes: tiles and lines below |
| Over the header | Never: clipped by the board region | **Covers the header** | **gap** | Partly: it floats from the pane's root so that it paints last |
| Over a side panel | Never | **Covers the panel and its title** | **gap** | Yes: size and clip it to the main area |
| Tile on the card | 27 tall, top rule only, no box | 41 tall, boxed, raised, colour bar | **gap** | Yes: a card tile drops the box and bar. The canvas's `.card-open .skill-cell` strips them |
| Tile pitch | 33 | 50 | **gap** | Same |
| Practice chip | 61 wide, chip with a 3px bar | Text with a separate bar | gap | Yes |
| Action list | 84 by 26 | 87 by 26 | match | |
| Format chips | 26 by 26 icons | 58 to 72 wide words, 35 tall | **gap** | Partly: a Button holds text, so short glyphs. `FORMAT_GROUPS` has them and `chipWords` computes them, but the Button draws `chip.label` |
| Run | Same line, right-aligned, 84 by 26 | **Wrapped to its own line**, left-aligned, 42 wide | **gap** | Yes: follows from the chips, then a `flexGrow` spacer in place of the canvas's auto margin |
| validate, review | 84 by 26, same width | 66 and 59 by 26 | gap | Yes: a fixed `width` Box |
| Line pitch in the bar | 34 | 35 to 62, uneven | gap | Yes: `rowGap="sm"` |
| Move line | ← and → at the ends, 33 wide | At the ends, 45 and 62 wide | gap | Yes: `padding={0}` |
| Mark | 20 by 20 | 22 by 19 | match | |

## Files panel

| Measure | Canvas | Pane 0.4.7 | Result | Closable |
| --- | --- | --- | --- | --- |
| Opens beside the board | Yes | Yes | match | |
| Width | 640 of 1519 (42%) | 405 of 757 (53%) | differs by the pane's own width | Check after the header fix |
| Tabs | Wrap | Wrap | match | |
| With about 40 files | not measured | Tabs fill the panel, so the file's text is pushed below them | gap | Check against the canvas with a long list |
| Closing the panel keeps the opened card | Yes | not measured | | |
| Two panels open | Second opens beside the first, board narrows to 239 | not measured | | |
| Close | 32 by 32 | 31 by 26 | close | |

## Not yet measured on the real pane

Canvas values to compare against, once a board is open.

| State | Canvas |
| --- | --- |
| Help | Panel 640 wide, header 117.5, title 26px, Forge button 48 by 32, expand and close 32 by 32 |
| Report | Panel 640 wide, header 116.5, title 26px, rule heading 19.5px, Fix all 61 by 29.5, Fix 44 by 29.5, opens beside an open files panel |
| Dialog | 480 wide, 458 tall, centred, backdrop 55% black, padding 18, gap 14, option 28 tall, Cancel 69 by 31.5, primary 78 by 31.5 in `#E5531A` on `#0B0B0B` |
| Details tile bar | As wide as its stage, padding 8, gap 8 on `#0B0B0B`, list 84 by 26, chips 26 by 26, Run on the same line at the right, list, folder, files at the right of the review line |
| Active session only on | Disabled: Run, validate, review, ←, →, chips, the list box, Run next, Split, Handoff, Close session. Note reads "Activate this session to run actions" |
| Backlog draft | Title 28.5 tall, Text 101 tall, both 184.7 wide on `#0B0B0B`, Add and Cancel 19 tall, form pushes the first card down to 292.5 |
| Expanded board | Header 57, region 863 |
| Expanded details | Header 57, region 863, including its own head |
| Split grip | 16 tall, full width |

The `+` on the Backlog is not on the list of controls allowed on the real pane, so test the draft through `claude plugin test`, or get approval to press it.

## Fix order for the batch

Nothing here has been applied. The batch needs a board on screen to prove each failing check red first.

1. `→` clipped on a card: `padding={0}` on `CardButtonView`'s Box, and the same on the format chips.
2. Bar lost when expanded: flex in place of `HEADER_ROWS`.
3. Details' buttons off screen: move `DetailHeadView` out of the sideways-scrolled part.
4. Header on one line.
5. Spacing: replace row and column numbers with step names through the board, card, and tile, and retune `CARD_FRAME_ROWS`, `CARD_BASE_ROWS`, `CARD_TILE_ROWS`, and `ROWS_ABOVE_CARDS` against what they then measure. Step names are cells in the terminal, so the terminal keeps working.
6. Opened card: width from the stage, unboxed tiles, glyph chips, Run on the first line, and stop covering a side panel.
7. Grid under the board: one width rule for both.
8. Bar: thinner thumb.
