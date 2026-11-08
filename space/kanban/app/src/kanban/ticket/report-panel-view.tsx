import { useBoard } from '../shared/board-context'
import type { ReportPanel } from '../shared/board-store'
import { RuleView } from './report-rule-view'

export function ReportPanelHeadView({ panel }: { panel: ReportPanel }) {
  const { page } = useBoard()
  const title = panel.progress ? (page.board.practiceNamed(panel.progress.practice.key)?.name ?? panel.progress.fidelity.slug) : panel.ticket.name
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
        <span className="report-number is-error">{panel.report.violationCount}</span>
        <span className="panel-subtitle">violations</span>
      </div>
      <div className="report-stat">
        <span className="report-number">{panel.report.rules.length}</span>
        <span className="panel-subtitle">rules hit</span>
      </div>
    </>
  )
}

function OutOfDateView({ panel, isOff }: { panel: ReportPanel; isOff: boolean }) {
  const { progress } = panel
  return (
    <>
      <p className="panel-warning">This report's saved graph is out of date, so its graph's rules are not shown. Validate again to read them.</p>
      {progress ? (
        <button className="ghost-button" disabled={isOff} title={isOff ? 'Connect a chat to validate' : 'Ask the chat to validate this fidelity again'} onClick={() => void panel.ticket.validateAgain(progress)}>
          Validate again
        </button>
      ) : null}
    </>
  )
}

function ReportStandingView({ panel, isOff }: { panel: ReportPanel; isOff: boolean }) {
  const { report } = panel
  if (!report.path) return <p className="panel-note">No validation report yet.</p>
  if (report.isOutOfDate) return <OutOfDateView panel={panel} isOff={isOff} />
  // The raw text stands in for the rules only when none could be read from it; otherwise it pushes them out of view.
  if (!report.hasSavedGraph) {
    return (
      <>
        <p className="panel-warning">This report has no saved graph, so its rules are only in the report file.</p>
        {report.rules.length ? null : <pre className="report-text">{report.text}</pre>}
      </>
    )
  }
  return report.rules.length ? null : <p className="panel-clean">No open violations. Reviewed is ready on the card.</p>
}

export function ReportPanelBodyView({ panel }: { panel: ReportPanel }) {
  const { page, state } = useBoard()
  const isOff = panel.ticket.isLocked || !page.chat.canSend
  return (
    <div className="panel-body report-body" key={state.board?.project}>
      <ReportStandingView panel={panel} isOff={isOff} />
      {panel.report.rules.length ? (
        <button className="ghost-button" disabled={isOff} title={isOff ? 'Connect a chat to send fixes' : 'Ask the chat to fix all violations found in this report'} onClick={() => void panel.ticket.fixReport(panel.report)}>
          Fix all violations
        </button>
      ) : null}
      {panel.report.rules.map(rule => (
        <RuleView key={`${rule.fidelity.slug}/${rule.rule.slug}`} panel={panel} rule={rule} isOff={isOff} />
      ))}
    </div>
  )
}
