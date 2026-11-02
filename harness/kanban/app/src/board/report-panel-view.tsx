import type { ReportRule, SourceLine, Violation } from './board'
import { countOf, practiceOf } from './board-brand'
import { useBoard } from './board-context'
import { locationOf } from './board-page'
import type { ReportPanel } from './board-store'
import { ChevronIcon } from './icons'

const violationsIn = (panel: ReportPanel): number => panel.report.rules.reduce((total, rule) => total + rule.count, 0)

export function ReportPanelHeadView({ panel }: { panel: ReportPanel }) {
  const title = panel.fidelity ? (practiceOf(panel.fidelity)?.name ?? panel.fidelity) : panel.ticket
  return (
    <div className="panel-words">
      <div className="panel-kind">
        VALIDATION REPORT<span className="accent-mark">_</span>
      </div>
      <h1>{title}</h1>
      <div className="panel-subtitle">{panel.report.path}</div>
    </div>
  )
}

export function ReportStatsView({ panel }: { panel: ReportPanel }) {
  return (
    <>
      <div className="report-stat">
        <span className="report-number is-error">{violationsIn(panel)}</span>
        <span className="panel-subtitle">violations</span>
      </div>
      <div className="report-stat">
        <span className="report-number">{panel.report.rules.length}</span>
        <span className="panel-subtitle">rules hit</span>
      </div>
    </>
  )
}

function SourceLineView({ violation, entry }: { violation: Violation; entry: SourceLine }) {
  return (
    <div className={entry.number === violation.line ? 'code-line is-failing' : 'code-line'}>
      <span className="line-number">{entry.number}</span>
      <span className="line-text">{entry.text}</span>
    </div>
  )
}

function ViolationLocationView({ panel, rule, violation }: { panel: ReportPanel; rule: ReportRule; violation: Violation }) {
  const { page } = useBoard()
  const location = locationOf(violation)
  const line = violation.line ?? 1
  // A location with no source has no file to open, so only one with source lines is a link.
  if (!violation.source.length) return <span className="file-location">{location}</span>
  return (
    <button className="file-link" title={`Open at line ${line}`} onClick={() => void page.panels.openFileAtLine(panel.ticket, rule.fidelity, violation.location, line)}>
      {location}
    </button>
  )
}

function ViolationView({ panel, rule, violation, isOff }: { panel: ReportPanel; rule: ReportRule; violation: Violation; isOff: boolean }) {
  const { page } = useBoard()
  return (
    <article className="violation">
      <div className="violation-head">
        <div className="violation-words">
          <ViolationLocationView panel={panel} rule={rule} violation={violation} />
          <div className="violation-message">{violation.message}</div>
        </div>
        <button className="fix-button" aria-label={`Fix ${locationOf(violation)}`} disabled={isOff} onClick={() => void page.fixViolation(rule, violation)}>
          Fix
        </button>
      </div>
      {violation.source.length ? (
        <div className="violation-source">
          {violation.source.map(entry => (
            <SourceLineView key={entry.number} violation={violation} entry={entry} />
          ))}
        </div>
      ) : null}
    </article>
  )
}

function RuleView({ panel, rule, isOff }: { panel: ReportPanel; rule: ReportRule; isOff: boolean }) {
  const { page } = useBoard()
  const place = `${rule.fidelity}/${rule.name}`
  const isOpen = !panel.closedRules.includes(place)
  return (
    <section className="report-rule">
      <div className="rule-head">
        <div className="rule-words">
          <h2>
            <button className="rule-toggle" aria-expanded={isOpen} onClick={() => page.panels.toggleRule(place)}>
              <ChevronIcon isTurned={!isOpen} />
              <span>{rule.name}</span>
              <span className="rule-count">{countOf(rule.count, 'violation')}</span>
            </button>
          </h2>
          <p>{rule.description}</p>
        </div>
        <button className="ghost-button" disabled={isOff} onClick={() => void page.fixRule(rule)}>
          Fix all
        </button>
      </div>
      {isOpen ? rule.violations.map((violation, index) => <ViolationView key={`${violation.location}-${violation.line}-${index}`} panel={panel} rule={rule} violation={violation} isOff={isOff} />) : null}
    </section>
  )
}

function ReportStandingView({ panel }: { panel: ReportPanel }) {
  const { report } = panel
  if (!report.path) return <p className="panel-note">No validation report yet.</p>
  if (!report.has_saved_graph) {
    return (
      <>
        <p className="panel-warning">This report has no saved graph, so its rules are only in the report file.</p>
        <pre className="report-text">{report.text}</pre>
      </>
    )
  }
  return report.rules.length ? null : <p className="panel-clean">No open violations. Reviewed is ready on the card.</p>
}

export function ReportPanelBodyView({ panel }: { panel: ReportPanel }) {
  const { page, state } = useBoard()
  const owner = page.board.tickets.find(ticket => ticket.name === panel.ticket)
  const isLocked = owner ? page.ticket(owner).isLocked : false
  const isOff = isLocked || !page.chat.canSend
  return (
    <div className="panel-body report-body" key={state.board?.project}>
      <ReportStandingView panel={panel} />
      {panel.report.rules.map(rule => (
        <RuleView key={`${rule.fidelity}/${rule.name}`} panel={panel} rule={rule} isOff={isOff} />
      ))}
    </div>
  )
}
