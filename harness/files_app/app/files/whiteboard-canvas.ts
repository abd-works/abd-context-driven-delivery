// A board as the Files app draws it on a canvas: the board Python reads from a whiteboard file (harness/whiteboard's
// WhiteboardFile, the one reader of the file), and what only drawing it needs, the part of the board the canvas shows
// and where each arrow meets the blocks it joins.
import type { BoxData, SectionData, ShapeData, WhiteboardData } from '@cdd/harness/whiteboard/whiteboard-file'

type Point = { x: number; y: number }

export type CanvasArrow = { id: string; from: Point; to: Point; isDashed: boolean }
export type CanvasFrame = { x: number; y: number; w: number; h: number }

// The space left round the drawing, so the outermost blocks do not touch the canvas's edge.
const MARGIN = 40

export class WhiteboardCanvas {
  constructor(readonly board: WhiteboardData) {}

  // Every block the board draws: its sections first, so each lies behind the blocks it holds, then its shapes.
  get blocks(): (SectionData | ShapeData)[] {
    return [...this.board.sections, ...this.board.shapes]
  }

  // Each arrow between two blocks the board holds, from the side of the one it leaves that faces the other to the facing
  // side of the one it reaches; an arrow naming a block the board does not hold is not drawn.
  get arrows(): CanvasArrow[] {
    const byId = new Map(this.blocks.map(block => [block.id, block.box]))
    return this.board.arrows.flatMap(arrow => {
      const from = byId.get(arrow.from_id)
      const to = byId.get(arrow.to_id)
      return from && to ? [{ id: arrow.id, from: sideFacing(from, to), to: sideFacing(to, from), isDashed: arrow.dash }] : []
    })
  }

  // The part of the board the canvas shows: every block and label, with a margin round them.
  get frame(): CanvasFrame {
    const corners = [...this.blocks.flatMap(({ box }) => [{ x: box.x, y: box.y }, { x: box.x + box.w, y: box.y + box.h }]), ...this.board.labels]
    if (corners.length === 0) return { x: 0, y: 0, w: 2 * MARGIN, h: 2 * MARGIN }
    const left = Math.min(...corners.map(corner => corner.x))
    const top = Math.min(...corners.map(corner => corner.y))
    const right = Math.max(...corners.map(corner => corner.x))
    const bottom = Math.max(...corners.map(corner => corner.y))
    return { x: left - MARGIN, y: top - MARGIN, w: right - left + 2 * MARGIN, h: bottom - top + 2 * MARGIN }
  }
}

// The middle of the side of box that faces other: its bottom or top when other lies more below or above it than beside.
function sideFacing(box: BoxData, other: BoxData): Point {
  const middle = { x: box.x + box.w / 2, y: box.y + box.h / 2 }
  const across = other.x + other.w / 2 - middle.x
  const down = other.y + other.h / 2 - middle.y
  if (Math.abs(down) >= Math.abs(across)) return { x: middle.x, y: down >= 0 ? box.y + box.h : box.y }
  return { x: across >= 0 ? box.x + box.w : box.x, y: middle.y }
}
