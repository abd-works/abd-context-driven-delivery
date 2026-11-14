import type { ReactNode } from 'react'

import type { FidelityGuidanceData, HelpData, PracticeGuidanceData } from '@cdd/space/kanban/board'

// The guidance a help panel is about: the fidelity it was opened on, else the practice. It sends its own overview,
// guidance, and rules.
const subjectOf = (help: HelpData): PracticeGuidanceData | FidelityGuidanceData => help.fidelity ?? help.practice

import { useBoard } from '../shared/board-context'
import type { HelpPanel } from '../shared/board-store'
import { MarkdownBlockView } from '../shared/markdown-view'
import { helpBlocksOf } from './help-text'

function HelpTextView({ markdown, className }: { markdown: string; className: string }) {
  return (
    <>
      {helpBlocksOf(markdown).map((block, index) => (
        <MarkdownBlockView key={index} block={block} className={className} />
      ))}
    </>
  )
}

export function HelpPanelHeadView({ panel: { help } }: { panel: HelpPanel }) {
  const { page } = useBoard()
  const practice = page.board.practiceNamed(help.practice.key)
  return (
    <div className="panel-words">
      <div className="panel-kind">
        HELP<span className="accent-mark">_</span>
      </div>
      <h1>{help.fidelity ? page.board.fidelityShown(help.fidelity.slug)?.label : practice?.name}</h1>
      <div className="help-place">
        <span className="practice-chip" style={{ borderLeftColor: practice?.color }}>
          {practice?.name}
        </span>
        <span className="panel-subtitle">{help.stage?.name ?? 'Practice overview'}</span>
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
      {subjectOf(help).rules.map(rule => (
        <div key={rule.slug} className="help-rule">
          <div className="help-rule-name">{rule.slug}</div>
          <div className="help-rule-text">{rule.body.trim()}</div>
        </div>
      ))}
    </HelpGroupView>
  )
}

export function HelpPanelBodyView({ panel: { help } }: { panel: HelpPanel }) {
  const subject = subjectOf(help)
  return (
    <div className="panel-body help-body">
      <div className="help-group">
        <HelpTextView markdown={subject.overview} className="help-overview" />
      </div>
      {subject.guidance.trim() ? (
        <HelpGroupView heading="GUIDANCE">
          <HelpTextView markdown={subject.guidance} className="help-guidance" />
        </HelpGroupView>
      ) : null}
      {subject.rules.length ? <HelpRulesView help={help} /> : null}
    </div>
  )
}
