import type { ReactNode } from 'react'

import type { HelpData } from '@cdd/space/kanban/board'

import { useBoard } from './board-context'
import type { HelpPanel } from './board-store'
import { helpBlocksOf } from './help-text'
import type { HelpBlock, TextRun } from './help-text'

function RunsView({ runs }: { runs: TextRun[] }) {
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

function HelpListView({ items, className }: { items: TextRun[][]; className: string }) {
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

function HelpBlockView({ block, className }: { block: HelpBlock; className: string }) {
  if (block.kind === 'preformatted') return <pre className="help-preformatted">{block.text}</pre>
  if (block.kind === 'heading') return <h3 className="help-heading"><RunsView runs={block.runs} /></h3>
  if (block.kind === 'paragraph') return <p className={className}><RunsView runs={block.runs} /></p>
  return <HelpListView items={block.items} className={className} />
}

function HelpTextView({ markdown, className }: { markdown: string; className: string }) {
  return (
    <>
      {helpBlocksOf(markdown).map((block, index) => (
        <HelpBlockView key={index} block={block} className={className} />
      ))}
    </>
  )
}

export function HelpPanelHeadView({ panel: { help } }: { panel: HelpPanel }) {
  const { page } = useBoard()
  const practice = page.board.practiceNamed(help.practice)
  return (
    <div className="panel-words">
      <div className="panel-kind">
        HELP<span className="accent-mark">_</span>
      </div>
      <h1>{help.fidelity ? practice?.fidelityNameOf(help.slug) : practice?.name}</h1>
      <div className="help-place">
        <span className="practice-chip" style={{ borderLeftColor: practice?.color }}>
          {practice?.name}
        </span>
        <span className="panel-subtitle">{help.stage || 'Practice overview'}</span>
      </div>
    </div>
  )
}

function HelpGroupView({ heading, children }: { heading: string; children: ReactNode }) {
  return (
    <div className="help-group wide">
      <div className="panel-kind">
        {heading}
        <span className="accent-mark">_</span>
      </div>
      {children}
    </div>
  )
}

function HelpRulesView({ help }: { help: HelpData }) {
  return (
    <HelpGroupView heading={help.fidelity ? 'RULES' : 'SHARED RULES'}>
      {help.rules.map(rule => (
        <div key={rule.slug} className="help-rule">
          <div className="help-rule-name">{rule.slug}</div>
          <div className="help-rule-text">{rule.text}</div>
        </div>
      ))}
    </HelpGroupView>
  )
}

export function HelpPanelBodyView({ panel: { help } }: { panel: HelpPanel }) {
  return (
    <div className="panel-body help-body">
      <div className="help-group">
        <HelpTextView markdown={help.overview} className="help-overview" />
      </div>
      {help.guidance ? (
        <HelpGroupView heading="GUIDANCE">
          <HelpTextView markdown={help.guidance} className="help-guidance" />
        </HelpGroupView>
      ) : null}
      {help.rules.length ? <HelpRulesView help={help} /> : null}
    </div>
  )
}
