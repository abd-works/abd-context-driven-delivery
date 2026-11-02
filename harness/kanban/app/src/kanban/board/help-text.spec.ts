import { describe, expect, it } from 'vitest'

import { helpBlocksOf } from './help-text'

describe('Open Help', () => {
  it('should drop the section heading the panel already says', () => {
    expect(helpBlocksOf('#### Overview\n\nScope the solution.')).toEqual([{ kind: 'paragraph', runs: [{ text: 'Scope the solution.', style: 'plain' }] }])
  })

  it('should keep a lead in bold and code as code', () => {
    expect(helpBlocksOf('**Name the layers.** Actors are `people`.')).toEqual([
      {
        kind: 'paragraph',
        runs: [
          { text: 'Name the layers.', style: 'bold' },
          { text: ' Actors are ', style: 'plain' },
          { text: 'people', style: 'code' },
          { text: '.', style: 'plain' },
        ],
      },
    ])
  })

  it('should show a link\'s words, with no address to follow', () => {
    expect(helpBlocksOf('Read [the tools](../tools.md).')).toEqual([{ kind: 'paragraph', runs: [{ text: 'Read the tools.', style: 'plain' }] }])
  })

  it('should keep a list as a list', () => {
    expect(helpBlocksOf('- one\n- two')).toEqual([{ kind: 'list', items: [[{ text: 'one', style: 'plain' }], [{ text: 'two', style: 'plain' }]] }])
  })

  it('should keep a fenced block as written', () => {
    expect(helpBlocksOf('Before\n\n```\nhello\n\n  there\n```\n\nAfter').map(block => block.kind)).toEqual(['paragraph', 'preformatted', 'paragraph'])
  })

  it('should keep a table as written', () => {
    expect(helpBlocksOf('| a | b |\n|---|---|\n| 1 | 2 |')).toEqual([{ kind: 'preformatted', text: '| a | b |\n|---|---|\n| 1 | 2 |' }])
  })

  it('should keep a heading inside the text', () => {
    expect(helpBlocksOf('First\n\n## Later\n\nSecond').map(block => block.kind)).toEqual(['paragraph', 'heading', 'paragraph'])
  })

  it('should give nothing for no text', () => {
    expect(helpBlocksOf('')).toEqual([])
  })
})
