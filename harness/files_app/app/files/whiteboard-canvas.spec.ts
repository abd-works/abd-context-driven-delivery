// Open Whiteboard In Files App, as
// story_tests/review-generated-work-in-file-viewer/open-files-in-files-app/open_files_in_files_app_story.test.md writes it:
// a whiteboard file opens as its board drawn on a canvas, never as the file's text.
import { describe, expect, it } from 'vitest'

import { WhiteboardCanvas } from './whiteboard-canvas'

// A story map board as Render saves it: an epic bar, a story card inside a section, the board's title, and an arrow.
const BOARD = JSON.stringify({
  v: 1,
  title: 'Story Map',
  order: ['lane', 'epic', 'story', 'title', 'link'],
  elements: {
    lane: { type: 'container', color: 'gray', text: 'Release 1', x: 0, y: 100, w: 400, h: 300 },
    epic: { type: 'shape', color: 'purple', text: 'Manage Customer Orders', kind: 'rounded', x: 20, y: 120, w: 168, h: 60 },
    story: { type: 'shape', color: 'yellow', text: '*Customer*\nBrowse Product Catalog', x: 32, y: 280, w: 152, h: 152 },
    title: { type: 'text', text: 'Story Map', x: 20, y: 20, size: 'title' },
    link: { type: 'arrow', from: 'epic', to: 'story', dash: true },
  },
})

describe('a whiteboard file drawn on a canvas', () => {
  const canvas = WhiteboardCanvas.from(BOARD)

  it('should be titled as its board', () => {
    expect(canvas.title).toBe('Story Map')
  })

  it('should draw each block where the board places it', () => {
    expect(canvas.blocks.map(block => [block.id, block.x, block.y, block.w, block.h])).toEqual([
      ['lane', 0, 100, 400, 300],
      ['epic', 20, 120, 168, 60],
      ['story', 32, 280, 152, 152],
    ])
  })

  it('should draw a section behind the blocks it holds', () => {
    expect(canvas.blocks[0]).toMatchObject({ id: 'lane', isSection: true })
  })

  it('should write a block\'s words line by line, without the board\'s emphasis marks', () => {
    expect(canvas.blocks[2]?.lines).toEqual(['Customer', 'Browse Product Catalog'])
  })

  it('should write a label where the board places it', () => {
    expect(canvas.labels).toEqual([{ id: 'title', x: 20, y: 20, text: 'Story Map', isTitle: true }])
  })

  it('should draw an arrow from the middle of the block it leaves to the block it reaches', () => {
    expect(canvas.arrows).toEqual([{ id: 'link', from: { x: 104, y: 180 }, to: { x: 108, y: 280 }, isDashed: true }])
  })

  it('should frame every element with a margin round them', () => {
    expect(canvas.frame).toEqual({ x: -40, y: -20, w: 480, h: 492 })
  })
})

describe('a whiteboard file that holds no board', () => {
  it('should draw nothing, rather than fail', () => {
    const canvas = WhiteboardCanvas.from('{}\n')
    expect([canvas.blocks.length, canvas.labels.length, canvas.arrows.length]).toEqual([0, 0, 0])
  })

  it('should say the file is no board when it is not JSON', () => {
    expect(WhiteboardCanvas.from('not a board').problem).toContain('not a whiteboard file')
  })
})
