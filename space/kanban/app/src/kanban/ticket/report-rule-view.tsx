import type { ReportRuleData, SourceLineData, ViolationData } from '@cdd/space/kanban/ticket'

import { countOf } from '../shared/board-brand'
import { useBoard } from '../shared/board-context'
import type { ReportPanel } from '../shared/board-store'
import { ChevronIcon } from '../shared/icons'
import { locationOf, type ReportClient } from './report-client'
import type { TicketClient } from './ticket-client'

function SourceLineView({ violation, entry }: { violation: ViolationData; entry: SourceLineData }) {
  return (
    <div className={entry.number === violation.line ? 'code-line is-failing' : 'code-line'}>
      <span className="line-number">{entry.number}</span>
      <span className="line-text">{entry.text}</span>
    </div>
  )
}

function ViolationLocationView({ panel, rule, violation }: { panel: ReportPanel; rule: ReportRuleData; violation: ViolationData }) {
  const { page } = useBoard()
  const location = locationOf(violation)
  const line = violation.line ?? 1
  // A location with no source has no file to open, so only one with source lines is a link.
  if (!violation.source.length) return <span className="file-location">{location}</span>
  return (
    <button className="file-link" title={`Open at line ${line}`} onClick={() => void page.files.openFileAtLine(panel.ticket, panel.ticket.progressNamed(rule.fidelity.slug), violation.location, line)}>
      {location}
    </button>
  )
}

// The file and line head the block of source around them, the way a fenced code block names its file.
function ViolationSourceView({ panel, rule, violation }: { panel: ReportPanel; rule: ReportRuleData; violation: ViolationData }) {
  return (
    <div className="violation-source">
      <div className="source-fence">
        <ViolationLocationView panel={panel} rule={rule} violation={violation} />
      </div>
      {violation.source.map(entry => (
        <SourceLineView key={entry.number} violation={violation} entry={entry} />
      ))}
    </div>
  )
}

function ViolationView({ panel, rule, violation, isOff }: { panel: ReportPanel; rule: ReportRuleData; violation: ViolationData; isOff: boolean }) {
  const { page } = useBoard()
  const hasSource = violation.source.length > 0
  return (
    <article className="violation">
      <div className="violation-head">
        <div className="violation-words">
          {hasSource ? null : <ViolationLocationView panel={panel} rule={rule} violation={violation} />}
          <div className="violation-message">{violation.message}</div>
        </div>
        <button className="fix-button" aria-label={`Fix ${locationOf(violation)}`} disabled={isOff} title={isOff ? 'Connect a chat to send fixes' : "Put this fix in the chat's prompt to edit and send"} onClick={() => void panel.ticket.fixViolation(rule, violation)}>
          Fix
        </button>
      </div>
      {hasSource ? <ViolationSourceView panel={panel} rule={rule} violation={violation} /> : null}
    </article>
  )
}

function RuleHeadView({ ticket, report, rule, place, isOpen, isOff }: { ticket: TicketClient; report: ReportClient; rule: ReportRuleData; place: string; isOpen: boolean; isOff: boolean }) {
  const { page } = useBoard()
  return (
    <div className="rule-head">
      <div className="rule-words">
        <h2>
          <button className="rule-toggle" aria-expanded={isOpen} onClick={() => page.panels.toggleRule(place)}>
            <ChevronIcon isTurned={!isOpen} />
            <span>{rule.rule.slug}</span>
            <span className="rule-count">{countOf(rule.count, 'violation')}</span>
          </button>
        </h2>
        <p>{rule.rule.body}</p>
      </div>
      <button className="ghost-button" disabled={isOff} onClick={() => void ticket.fixRule(report, rule)}>
        Fix all
      </button>
    </div>
  )
}

export function RuleView({ panel, rule, isOff }: { panel: ReportPanel; rule: ReportRuleData; isOff: boolean }) {
  const place = `${rule.fidelity.slug}/${rule.rule.slug}`
  const isOpen = !panel.closedRules.includes(place)
  return (
    <section className="report-rule">
      <RuleHeadView ticket={panel.ticket} report={panel.report} rule={rule} place={place} isOpen={isOpen} isOff={isOff} />
      {isOpen ? rule.violations.map((violation, index) => <ViolationView key={`${violation.location}-${violation.line}-${index}`} panel={panel} rule={rule} violation={violation} isOff={isOff} />) : null}
    </section>
  )
}
