export type TextRun = { text: string; style: 'plain' | 'bold' | 'italic' | 'code' }
export type HelpBlock = { kind: 'paragraph'; runs: TextRun[] } | { kind: 'heading'; runs: TextRun[] } | { kind: 'list'; items: TextRun[][] } | { kind: 'preformatted'; text: string }

const RUN_PATTERN = /(\*\*[^*]+\*\*|`[^`]+`|\*[^*]+\*)/
const LINK_PATTERN = /\[([^\]]+)\]\([^)]+\)/g
const LIST_LINE = /^\s*[-*]\s+/
const HEADING_LINE = /^#{1,6}\s+/
const RULE_LINE = /^\s*(---+|\*\*\*+)\s*$/
const TABLE_LINE = /^\s*\|/
const FENCE_LINE = /^\s*```/

function runOf(part: string): TextRun {
  if (part.startsWith('**')) return { text: part.slice(2, -2), style: 'bold' }
  if (part.startsWith('`')) return { text: part.slice(1, -1), style: 'code' }
  if (part.startsWith('*')) return { text: part.slice(1, -1), style: 'italic' }
  return { text: part, style: 'plain' }
}

export const runsOf = (line: string): TextRun[] => line.replace(LINK_PATTERN, '$1').split(RUN_PATTERN).filter(Boolean).map(runOf)

const blockKindOf = (line: string): string => {
  if (LIST_LINE.test(line)) return 'list'
  return TABLE_LINE.test(line) ? 'table' : 'paragraph'
}

function textBlockOf(kind: string, lines: string[]): HelpBlock {
  if (kind === 'list') return { kind: 'list', items: lines.map(line => runsOf(line.replace(LIST_LINE, ''))) }
  if (kind === 'table') return { kind: 'preformatted', text: lines.join('\n') }
  return { kind: 'paragraph', runs: runsOf(lines.join(' ')) }
}

// Splits text with no fences into blocks: a blank line, a heading, or a change of kind ends one.
function textBlocksOf(lines: string[]): HelpBlock[] {
  const blocks: HelpBlock[] = []
  let kind = ''
  let held: string[] = []
  const flush = () => {
    if (held.length) blocks.push(textBlockOf(kind, held))
    held = []
  }
  for (const line of lines) {
    const lineKind = blockKindOf(line)
    if (!line.trim() || RULE_LINE.test(line) || HEADING_LINE.test(line) || lineKind !== kind) flush()
    if (HEADING_LINE.test(line)) blocks.push({ kind: 'heading', runs: runsOf(line.replace(HEADING_LINE, '')) })
    else if (line.trim() && !RULE_LINE.test(line)) held.push(line)
    kind = lineKind
  }
  flush()
  return blocks
}

// Markdown as the blocks a page draws: between fences the text is ordinary markdown, and inside one it is kept as written.
export function markdownBlocksOf(markdown: string): HelpBlock[] {
  const parts = markdown.split('\n').reduce<{ isFence: boolean; lines: string[] }[]>(
    (found, line) => {
      if (FENCE_LINE.test(line)) return [...found, { isFence: !found.at(-1)!.isFence, lines: [] }]
      found.at(-1)!.lines.push(line)
      return found
    },
    [{ isFence: false, lines: [] }],
  )
  return parts.flatMap((part): HelpBlock[] => (part.isFence ? [{ kind: 'preformatted', text: part.lines.join('\n') }] : textBlocksOf(part.lines)))
}
