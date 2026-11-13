import { markdownBlocksOf, type HelpBlock } from '../shared/markdown-text'

export { runsOf, type HelpBlock, type TextRun } from '../shared/markdown-text'

// Help arrives as the markdown of the practice's files. Its first heading is its section's own name, which the panel
// already says.
export function helpBlocksOf(markdown: string): HelpBlock[] {
  const blocks = markdownBlocksOf(markdown)
  return blocks[0]?.kind === 'heading' ? blocks.slice(1) : blocks
}
