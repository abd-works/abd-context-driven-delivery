# Where the board pane differs from the canvas

The canvas is the Board artifact at https://claude.ai/artifact/LGLk189R4aZ14bgwcWRiPN. It is a web page, and the pane is a Claude Code mod drawn from the engine's element table (2.1.309). Everything not listed here matches the canvas, as far as the two have been compared: canvas lines 140-250, 325-440, 520-566, and 740-799 have been read only in part.

## The engine cannot draw it

| Canvas | Pane | Why |
| --- | --- | --- |
| Rounded corners | Rounded on desktop, square in the terminal | A Box takes a border style, not a radius, and the surface draws it |
| Colour bar on the left of a tile or practice label, 3px, 7px when reviewed | One column wide, the same when reviewed | A Box has no border of one side and sizes in columns, so the bar is a narrow Box |
| Line under the header and details bar | Background colour only | A Box has no border of one side |
| Faded tiles at 20% and 45% | Each colour on the tile mixed toward the background | A Box has no opacity |
| Segments | Terminal: one ▬ glyph per row, at the same strengths | A terminal cell is the smallest thing it can draw |
| Pressing a segment opens the card on that fidelity | A segment does nothing when pressed; the card opens from its ▾ and a press on the card selects it | A Client has no Svg and reports whole cells, and segments are 10px apart, so a press cannot tell one segment from the next |
| Card shadow | None | A Box has no shadow |
| Dim overlay behind the dialog | Terminal: none | The terminal reads six-digit colours only, so it has no see-through colour |
| Letter spacing on headings | None | Text has no spacing prop |
| Exact pixel sizes and font sizes | Named sizes: caption, footnote, body, heading, title | Text takes a named size and a Box sizes in columns and rows |
| Orange main buttons (Activate, Run, Fix, Satisfy) | An orange Box around a plain Button on every surface with pictures; the terminal's own primary button there | A Button takes no background and a surface draws a primary Button in its own colours |
| Bordered small buttons | The surface's native button | A Button can be primary, secondary, or plain, and the surface draws it |
| Greyed-out disabled controls | Dimmed and does nothing | A Button has no disabled state |
| Greyed-out list box on a locked ticket | The chosen action as dim text | A Select has no disabled state |
| Tooltips on chips, step marks, expand, the hide toggle, and tab paths | None | A Button has no title prop |
| The WIP field closes on Enter, Escape, or leaving it | Closes on Enter or on a × beside it | An Input reports neither Escape nor losing focus |
| A stage head opens its bar on a hover anywhere on it | On a hover over its ▾ | Only a Client hears the pointer, and it has to sit on the mark, so the head's other controls stay pressable |
| Checkboxes in the Activate dialog | Glyphs ☑ and ☐ on Buttons | A Button holds only text |
| The dialog centred on the pane | Placed by its estimated height | No call says how tall the dialog drew, and a tall dialog keeps its top edge in the pane |
| SVG icons for expand, format, and check on Buttons | Glyphs: ⤢ ⤡ ◫ M↓ </> ✓ | A Button holds only text |
| Toggle switch | Glyphs ━● and ●━ | No switch element, and a Button holds only text |
| Dashed line under the WIP limit | Solid underline | Text has one underline style |
| Card grows out of itself and slides between columns | Opens at once, level with the card as near as the rows above it can be counted | No animation or clip props, and no call reads where a Box was drawn. The card is drawn last from the pane's root because a Box paints only over what came before it |
| A card fits the page, which scrolls | A card that fits rises until it does; a taller one starts at the pane's top and the wheel moves it, to an end the pane estimates | It floats over the board, where the engine's window does not reach, and no call says how tall it drew |
| Tooltip under the scope shape | Drawn over the stage head | A Box paints over only what was drawn before it, so one below would be covered |
| A tile on an opened card opens on hover | Opens on a press | The bar moves to the tile, so its rows would slide out from under the pointer |
| Sideways scrolling past 1488px | A bar under the board you drag; ◀ and ▶ on surfaces with no Client | The engine's window moves up and down only, so the wheel cannot move the board sideways |
| Details and board each scroll to their own end | Each scrolls under the wheel, to an end the pane estimates; with a panel open the whole pane scrolls instead | No call says how tall a region's rows drew |
| Tile's action bar inside the tile | Under the stage heads, in that stage's column | Follows from the clipping above: a low tile's bar would be cut off |
| Bottom-right status message | The engine's toast | Toasts are the engine's to draw |
| Violation location opens the file in the editor | Opens the file in the Files panel, from that line | A plugin has no way to open an editor |
| Failing code line tinted see-through | A solid dark red, with the bar one column wide | A Box has no see-through colour |

## Per surface

| Surface | What it loses | Why |
| --- | --- | --- |
| Terminal | Chevron and scope shape; scope shows as ▭ | No Svg |
| VS Code | Hover-open tiles, press-anywhere cards, segment skill line, grip | No Client, so Buttons stand in |
| Mobile | The same, and - / + in place of the limit field, action Buttons in place of the list box, no backlog form | No Client, Input, or Select |

## In the pane but not on the canvas

These are stories with no other way in, so they stayed.

| Pane | Why it stays |
| --- | --- |
| Archive in the details bar | (S) Archive Ticket has no control on the canvas |
| + Ticket in the header | Opens a ticket straight in Discovery; the canvas only starts from the Backlog |
| Ticket names in the Activate dialog's OPEN group | The canvas uses the title there; a branch and worktree are named after the ticket, so the pane says what will be created |
| A band across the pane's top when the cdd server is lost | The canvas has no server to lose |

