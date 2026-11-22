// Open Whiteboard In Files App, as
// story_tests/review-generated-work-in-file-viewer/open-files-in-files-app/open_files_in_files_app_story.test.md writes it:
// a whiteboard file opens as its board drawn on a canvas, never as the file's text. The board is Python's reading of the
// file (whiteboard-file.show); the canvas adds only what drawing it needs.
import { describe, expect, it } from 'vitest'

import type { WhiteboardData } from '@cdd/harness/whiteboard/whiteboard-file'

import { WhiteboardCanvas } from './whiteboard-canvas'

const box = (x: number, y: number, w: number, h: number) => ({ x, y, w, h })
const shape = (id: string, at: ReturnType<typeof box>, text: string) => ({
  id, box: at, color: 'yellow', text, kind: 'rounded', stroke: '', size: '', text_align: '', lines: text.split('\n'), is_rounded: true,
})

// A story map board as whiteboard-file.show answers it: an epic bar and a story card inside a section, the board's
// title, an arrow from the epic to the story, and an arrow to an element the board does not hold.
const BOARD: WhiteboardData = {
  title: 'Story Map',
  sections: [{ id: 'lane', box: box(0, 100, 400, 300), color: 'gray', text: 'Release 1', lines: ['Release 1'] }],
  shapes: [shape('epic', box(20, 120, 168, 60), 'Manage Customer Orders'), shape('story', box(32, 280, 152, 152), 'Customer\nBrowse Product Catalog')],
  labels: [{ id: 'title', x: 20, y: 20, text: 'Story Map', size: 'title', wrap: null, is_title: true }],
  arrows: [
    { id: 'link', from_id: 'epic', to_id: 'story', from_side: '', to_side: '', label: '', dash: true, head: '', heads: null, bends: null },
    { id: 'gone', from_id: 'epic', to_id: 'note.1', from_side: '', to_side: '', label: '', dash: false, head: '', heads: null, bends: null },
  ],
}

describe('a whiteboard file drawn on a canvas', () => {
  const canvas = new WhiteboardCanvas(BOARD)

  it('should draw the board\'s sections first, so each lies behind the blocks it holds', () => {
    expect(canvas.blocks.map(block => block.id)).toEqual(['lane', 'epic', 'story'])
  })

  it('should draw an arrow from the middle of the block it leaves to the block it reaches', () => {
    expect(canvas.arrows).toEqual([{ id: 'link', from: { x: 104, y: 180 }, to: { x: 108, y: 280 }, isDashed: true }])
  })

  it('should frame every block and label with a margin round them', () => {
    expect(canvas.frame).toEqual({ x: -40, y: -20, w: 480, h: 492 })
  })
})

describe('a whiteboard file whose board holds nothing', () => {
  it('should frame only the margin', () => {
    expect(new WhiteboardCanvas({ title: '', sections: [], shapes: [], labels: [], arrows: [] }).frame).toEqual({ x: 0, y: 0, w: 80, h: 80 })
  })
})
