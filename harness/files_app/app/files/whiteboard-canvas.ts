// A whiteboard file as the Files app draws it on a canvas: the blocks, labels and arrows its board holds, where the board
// places them (harness/whiteboard/whiteboard.py writes the file: `board/meta` and one record per element).

type BoardRecord = Record<string, unknown>
type Point = { x: number; y: number }

// A block: an epic bar, a story card, a class or module box, or a section drawn round other blocks.
export type CanvasBlock = { id: string; x: number; y: number; w: number; h: number; color: string; lines: string[]; isSection: boolean; isRounded: boolean }
export type CanvasLabel = { id: string; x: number; y: number; text: string; isTitle: boolean }
export type CanvasArrow = { id: string; from: Point; to: Point; isDashed: boolean }
export type CanvasFrame = { x: number; y: number; w: number; h: number }

// The space left round the drawing, so the outermost blocks do not touch the canvas's edge.
const MARGIN = 40
const BLOCK_TYPES = new Set(['shape', 'container'])

export class WhiteboardCanvas {
  private constructor(
    readonly title: string,
    readonly blocks: CanvasBlock[],
    readonly labels: CanvasLabel[],
    readonly arrows: CanvasArrow[],
    readonly problem = '',
  ) {}

  // The board a whiteboard file's text holds; an empty canvas, saying why, for text that is no whiteboard file.
  static from(text: string): WhiteboardCanvas {
    let board: BoardRecord
    try {
      board = JSON.parse(text) as BoardRecord
    } catch (failure) {
      return new WhiteboardCanvas('', [], [], [], `This is not a whiteboard file: ${String(failure)}`)
    }
    const records = (board.elements ?? {}) as Record<string, BoardRecord>
    const ids = inOrder(board, records)
    const blocks = ids.filter(id => BLOCK_TYPES.has(String(records[id]?.type))).map(id => blockOf(id, records[id] as BoardRecord))
    blocks.sort((one, other) => Number(other.isSection) - Number(one.isSection))
    const labels = ids.filter(id => records[id]?.type === 'text').map(id => labelOf(id, records[id] as BoardRecord))
    const byId = new Map(blocks.map(block => [block.id, block]))
    const arrows = ids.flatMap(id => (records[id]?.type === 'arrow' ? arrowOf(id, records[id] as BoardRecord, byId) : []))
    return new WhiteboardCanvas(String(board.title ?? ''), blocks, labels, arrows)
  }

  // The part of the board the canvas shows: every block and label, with a margin round them.
  get frame(): CanvasFrame {
    const corners = [...this.blocks.flatMap(block => [{ x: block.x, y: block.y }, { x: block.x + block.w, y: block.y + block.h }]), ...this.labels]
    if (corners.length === 0) return { x: 0, y: 0, w: 2 * MARGIN, h: 2 * MARGIN }
    const left = Math.min(...corners.map(corner => corner.x))
    const top = Math.min(...corners.map(corner => corner.y))
    const right = Math.max(...corners.map(corner => corner.x))
    const bottom = Math.max(...corners.map(corner => corner.y))
    return { x: left - MARGIN, y: top - MARGIN, w: right - left + 2 * MARGIN, h: bottom - top + 2 * MARGIN }
  }
}

// The element ids in the order the board draws them, back to front: its order, then any it leaves out.
function inOrder(board: BoardRecord, records: Record<string, BoardRecord>): string[] {
  const ordered = Array.isArray(board.order) ? (board.order as string[]).filter(id => id in records) : []
  return [...ordered, ...Object.keys(records).filter(id => !ordered.includes(id))]
}

const numberOf = (value: unknown): number => (typeof value === 'number' ? value : Number(value) || 0)

// The words of a block, one line each, without the asterisks the board sets emphasis with.
const linesOf = (text: unknown): string[] => String(text ?? '').replace(/\*/g, '').split('\n').filter(line => line.trim())

function blockOf(id: string, record: BoardRecord): CanvasBlock {
  return {
    id,
    x: numberOf(record.x),
    y: numberOf(record.y),
    w: numberOf(record.w),
    h: numberOf(record.h),
    color: String(record.color ?? ''),
    lines: linesOf(record.text),
    isSection: record.type === 'container',
    isRounded: record.kind === 'rounded',
  }
}

function labelOf(id: string, record: BoardRecord): CanvasLabel {
  return { id, x: numberOf(record.x), y: numberOf(record.y), text: String(record.text ?? ''), isTitle: record.size === 'title' }
}

// An arrow between the two blocks it names, from the side of the one it leaves that faces the other to the facing side of
// the one it reaches; none when it names a block the board does not hold.
function arrowOf(id: string, record: BoardRecord, byId: Map<string, CanvasBlock>): CanvasArrow[] {
  const from = byId.get(String(record.from ?? ''))
  const to = byId.get(String(record.to ?? ''))
  if (!from || !to) return []
  return [{ id, from: sideFacing(from, to), to: sideFacing(to, from), isDashed: record.dash === true }]
}

function sideFacing(block: CanvasBlock, other: CanvasBlock): Point {
  const middle = { x: block.x + block.w / 2, y: block.y + block.h / 2 }
  const dx = other.x + other.w / 2 - middle.x
  const dy = other.y + other.h / 2 - middle.y
  if (Math.abs(dy) >= Math.abs(dx)) return { x: middle.x, y: dy >= 0 ? block.y + block.h : block.y }
  return { x: dx >= 0 ? block.x + block.w : block.x, y: middle.y }
}
