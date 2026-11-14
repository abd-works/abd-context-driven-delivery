import type { HelpBlock, TextRun } from './markdown-text'

export function RunsView({ runs }: { runs: TextRun[] }) {
  return (
    <>
      {runs.map((run, index) => {
        if (run.style === 'bold') return <strong key={index}>{run.text}</strong>
        if (run.style === 'italic') return <em key={index}>{run.text}</em>
        return run.style === 'code' ? <code key={index}>{run.text}</code> : <span key={index}>{run.text}</span>
      })}
    </>
  )
}

function MarkdownListView({ items, className }: { items: TextRun[][]; className: string }) {
  return (
    <ul className={className}>
      {items.map((runs, index) => (
        <li key={index}>
          <RunsView runs={runs} />
        </li>
      ))}
    </ul>
  )
}

export function MarkdownBlockView({ block, className }: { block: HelpBlock; className: string }) {
  if (block.kind === 'preformatted') return <pre className="help-preformatted">{block.text}</pre>
  if (block.kind === 'heading') return <h3 className="help-heading"><RunsView runs={block.runs} /></h3>
  if (block.kind === 'paragraph') return <p className={className}><RunsView runs={block.runs} /></p>
  return <MarkdownListView items={block.items} className={className} />
}

// A markdown file drawn as the page it describes: its headings, paragraphs, lists, and fenced text.
export function MarkdownView({ blocks, className }: { blocks: HelpBlock[]; className: string }) {
  return (
    <>
      {blocks.map((block, index) => (
        <MarkdownBlockView key={index} block={block} className={className} />
      ))}
    </>
  )
}
