import type { BoardJson, ColumnJson, SplitLayoutJson } from '../../types'
import { ticketsOf } from './ticket-summary'

// The engine has no call that says how tall something drew, so the pane works these out from what it draws.
export const HEADER_ROWS = 2
export const COLUMN_GAP = 1
const EDGE_COLUMN_SHARE = 0.14
const STAGE_SHARE = 0.24
const BOARD_SHARE = 0.6
const MINIMUM_REGION_ROWS = 6

// The canvas's column-grid never goes below 1488px, about this many cells, and scrolls sideways past that.
// The canvas's 1488 pixels at the 6.7 pixels a column measures on the desktop surface.
const BOARD_MINIMUM_COLUMNS = 222
export const BOARD_SIDE_COLUMNS = 2
const LIST_GAP_COLUMNS = 3

const AGE_ROWS = 1
const CARD_SIDE_COLUMNS = 6
// The body font fits more letters in a cell than the mono font a cell is measured by.
const LETTERS_PER_CELL = 1.3
// Above the first card: the header, the board's and column's edges, the stage head, and the list's label.
const ROWS_ABOVE_CARDS = 10
// A card's edges, its file links, its moves wrapped onto two lines, and the gap after it.
export const CARD_FRAME_ROWS = 8
const FULLEST_CARD_ROWS = CARD_FRAME_ROWS + 2
// The details' head, one line of tiles for each practice, and an open tile's bar.
const DETAILS_ROWS = 48

const shareOf = (column: ColumnJson): number => (column.work_required ? STAGE_SHARE : EDGE_COLUMN_SHARE)

export const boardColumnsOf = (room: number): number => Math.max(room, BOARD_MINIMUM_COLUMNS)

export function columnWidthOf(column: ColumnJson, boardColumns: number, columnCount: number): number {
  const shared = boardColumns - 2 * BOARD_SIDE_COLUMNS - COLUMN_GAP * (columnCount - 1)
  return Math.round(shared * shareOf(column))
}

// Where a column starts on the board, before any sideways scrolling.
export function columnLeftOf(columns: ColumnJson[], column: ColumnJson, boardColumns: number): number {
  const before = columns.slice(0, columns.indexOf(column))
  return before.reduce((left, shown) => left + columnWidthOf(shown, boardColumns, columns.length) + COLUMN_GAP, BOARD_SIDE_COLUMNS)
}

const SCROLLBAR_ROWS = 1

export function regionRowsOf(bodyRows: number, layout: SplitLayoutJson): { boardRows: number; detailsRows: number } {
  const room = bodyRows - HEADER_ROWS
  if (layout.expanded === 'board') return { boardRows: room - SCROLLBAR_ROWS, detailsRows: 0 }
  if (layout.expanded === 'details') return { boardRows: 0, detailsRows: room - SCROLLBAR_ROWS }
  const largest = Math.max(room - MINIMUM_REGION_ROWS, MINIMUM_REGION_ROWS)
  const wanted = layout.boardRows ?? Math.round(room * BOARD_SHARE)
  const boardRows = Math.min(Math.max(wanted, MINIMUM_REGION_ROWS), largest)
  return { boardRows, detailsRows: room - boardRows }
}

// A stage holds two lists side by side and an edge column one, so a stage's card has half its width.
export function faceRowsOf(title: string, column: ColumnJson, boardColumns: number, columnCount: number): number {
  const width = columnWidthOf(column, boardColumns, columnCount)
  const cardColumns = (column.work_required ? (width - LIST_GAP_COLUMNS) / 2 : width) - CARD_SIDE_COLUMNS
  return Math.ceil(title.length / Math.max(cardColumns * LETTERS_PER_CELL, 1)) + AGE_ROWS
}

export const rowsAboveCards = (): number => ROWS_ABOVE_CARDS

// An opened card: its edges, title, age, file links, and moves with the gaps between them; each tile with its gap; and
// the bar, whose three lines can wrap. Nothing says how tall it drew, so this leans high: a little extra room to
// scroll costs nothing, and too little would leave the end of the card out of reach.
const CARD_BASE_ROWS = 12
const CARD_TILE_ROWS = 4
const CARD_BAR_ROWS = 12
// The row kept above an opened card and the one kept below it.
export const CARD_ROOM_ABOVE = 2

export const cardRowsOf = (tileCount: number, hasBar: boolean): number => CARD_BASE_ROWS + tileCount * CARD_TILE_ROWS + (hasBar ? CARD_BAR_ROWS : 0)

const tallestColumnRows = (board: BoardJson): number =>
  Math.max(...board.columns.map(column => (column.items?.length ?? 0) + ticketsOf(column).length), 0) * FULLEST_CARD_ROWS + ROWS_ABOVE_CARDS

// How far a region may scroll before its last row reaches its top.
export function scrollLimitsOf(board: BoardJson, bodyRows: number, layout: SplitLayoutJson): { board: number; details: number } {
  const { boardRows, detailsRows } = regionRowsOf(bodyRows, layout)
  return { board: Math.max(tallestColumnRows(board) - boardRows, 0), details: Math.max(DETAILS_ROWS - detailsRows, 0) }
}
