import type { ReportRuleData, SourceLineData, ViolationData } from '@cdd/space/kanban/ticket'

import { countOf } from '../shared/board-brand'
import { useBoard } from '../shared/board-context'
import type { ReportPanel } from '../shared/board-store'
import { ChevronIcon } from '../shared/icons'
import { ACCEPT_TITLE, CANDIDATE_TITLE, falseTitleOn, fixTitleOn, isCandidate, locationOf, TAKE_BACK_TITLE, type ReportClient } from './report-client'

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
    <button className="file-link" title={`Open at line ${line}`} onClick={() => void page.editorApp.openFilesOn(panel.ticket, { fidelities: [rule.fidelity.slug], file: violation.location, line })}>
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
    <article className={isCandidate(violation) ? 'violation is-candidate' : 'violation'}>
      <div className="violation-head">
        <div className="violation-words">
          {hasSource ? null : <ViolationLocationView panel={panel} rule={rule} violation={violation} />}
          {isCandidate(violation) ? (
            <span className="candidate-tag" title={CANDIDATE_TITLE}>
              Candidate
            </span>
          ) : null}
          <div className="violation-message">{violation.message}</div>
        </div>
        <div className="violation-actions">
          <button className="fix-button" aria-label={`Fix ${locationOf(violation)}`} disabled={isOff} title={isOff ? 'Connect a chat to send fixes' : fixTitleOn(page.board)} onClick={() => void panel.report.fixViolation(rule, violation)}>
            Fix
          </button>
          <button className="ghost-button false-button" aria-label={`False ${locationOf(violation)}`} disabled={isOff} title={isOff ? 'Connect a chat to send this' : falseTitleOn(page.board)} onClick={() => void panel.report.reportFalseViolation(rule, violation)}>
            False
          </button>
          <button className="ghost-button accept-button" aria-label={`Accept ${locationOf(violation)}`} disabled={panel.ticket.isLocked} title={ACCEPT_TITLE} onClick={() => void panel.report.acceptViolation(rule, violation)}>
            Accept
          </button>
        </div>
      </div>
      {hasSource ? <ViolationSourceView panel={panel} rule={rule} violation={violation} /> : null}
    </article>
  )
}

function RuleHeadView({ report, rule, place, isOpen, isOff }: { report: ReportClient; rule: ReportRuleData; place: string; isOpen: boolean; isOff: boolean }) {
  const { page } = useBoard()
  return (
    <div className="rule-head">
      <div className="rule-words">
        <h2>
          <button className="rule-toggle" aria-expanded={isOpen} onClick={() => page.panels.toggleRule(place)}>
            <ChevronIcon isTurned={!isOpen} />
            <span>{rule.rule.slug}</span>
            {rule.count > rule.candidate_count ? <span className="rule-count">{countOf(rule.count - rule.candidate_count, 'violation')}</span> : null}
            {rule.candidate_count ? <span className="rule-count is-candidate">{countOf(rule.candidate_count, 'candidate')}</span> : null}
          </button>
        </h2>
        <p>{rule.rule.body}</p>
      </div>
      <button className="ghost-button" disabled={isOff} onClick={() => void report.fixRule(rule)}>
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
      <RuleHeadView report={panel.report} rule={rule} place={place} isOpen={isOpen} isOff={isOff} />
      {isOpen ? rule.violations.map((violation, index) => <ViolationView key={`${violation.location}-${violation.line}-${index}`} panel={panel} rule={rule} violation={violation} isOff={isOff} />) : null}
    </section>
  )
}

function AcceptedViolationView({ panel, rule, violation }: { panel: ReportPanel; rule: ReportRuleData; violation: ViolationData }) {
  return (
    <li className="accepted-violation">
      <div className="violation-words">
        <span className="file-location">
          {rule.rule.slug} · {locationOf(violation)}
        </span>
        <div className="accepted-message">{violation.message}</div>
      </div>
      <button className="ghost-button" aria-label={`Take back ${rule.rule.slug} ${locationOf(violation)}`} disabled={panel.ticket.isLocked} title={TAKE_BACK_TITLE} onClick={() => void panel.report.reopenViolation(rule, violation)}>
        Take back
      </button>
    </li>
  )
}

// The violations a person accepted, which Python leaves out of the rules above: listed closed, so a person can take one back.
export function AcceptedViolationsView({ panel }: { panel: ReportPanel }) {
  const { report } = panel
  if (!report.acceptedCount) return null
  return (
    <details className="accepted-violations">
      <summary>{countOf(report.acceptedCount, 'accepted violation')} left out</summary>
      <ul>
        {report.accepted.flatMap(rule =>
          rule.violations.map((violation, index) => <AcceptedViolationView key={`${rule.fidelity.slug}/${rule.rule.slug}/${violation.location}-${violation.line}-${index}`} panel={panel} rule={rule} violation={violation} />),
        )}
      </ul>
    </details>
  )
}
