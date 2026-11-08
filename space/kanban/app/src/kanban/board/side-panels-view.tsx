import type { ReactNode } from 'react'

import { FilesPanelBodyView, FilesPanelHeadView } from '../ticket/files-panel-view'
import { ReportPanelBodyView, ReportPanelHeadView, ReportStatsView } from '../ticket/report-panel-view'
import { useBoard } from '../shared/board-context'
import type { SidePanel } from '../shared/board-store'
import { useDragGrip } from './drag-grip'
import { HelpPanelBodyView, HelpPanelHeadView } from './help-panel-view'
import { ExpandIcon } from '../shared/icons'

const KIND_ORDER = ['report', 'files', 'help']
const KIND_WORDS: Record<string, string> = { report: 'report', files: 'files', help: 'help' }

function PanelGripView({ kind }: { kind: string }) {
  const { page } = useBoard()
  const grip = useDragGrip(
    'x',
    () => page.panels.widthOf(kind),
    (width, distance) => page.panels.setWidth(kind, width - distance),
  )
  return <button className="pane-grip" aria-label={`Drag to resize the ${KIND_WORDS[kind]}`} {...grip} />
}

function PanelControlsView({ panel }: { panel: SidePanel }) {
  const { page } = useBoard()
  const words = KIND_WORDS[panel.kind]
  const toggleLabel = `${panel.isExpanded ? 'Collapse' : 'Expand'} ${words}`
  return (
    <div className="panel-controls">
      {panel.kind === 'help' ? (
        <a className="action small" href={panel.help.href} target="_blank" rel="noreferrer">
          Forge
        </a>
      ) : null}
      <button className="icon-button" aria-label={toggleLabel} title={toggleLabel} onClick={() => page.panels.toggleExpanded(panel.kind)}>
        <ExpandIcon isExpanded={panel.isExpanded} />
      </button>
      <button className="icon-button" aria-label={`Close ${words}`} title={`Close ${words}`} onClick={() => page.panels.close(panel.kind)}>
        ×
      </button>
    </div>
  )
}

function panelHeadOf(panel: SidePanel): ReactNode {
  if (panel.kind === 'report') return <ReportPanelHeadView panel={panel} />
  return panel.kind === 'files' ? <FilesPanelHeadView panel={panel} /> : <HelpPanelHeadView panel={panel} />
}

function panelBodyOf(panel: SidePanel): ReactNode {
  if (panel.kind === 'report') return <ReportPanelBodyView panel={panel} />
  return panel.kind === 'files' ? <FilesPanelBodyView panel={panel} /> : <HelpPanelBodyView panel={panel} />
}

function SidePanelView({ panel }: { panel: SidePanel }) {
  const { page } = useBoard()
  const size = panel.isExpanded ? { flex: '1 1 0' } : { flexBasis: page.panels.widthOf(panel.kind) }
  return (
    <aside className="report-root" data-panel={panel.kind} aria-label={`${panel.kind} panel`} style={size}>
      {panel.isExpanded ? null : <PanelGripView kind={panel.kind} />}
      <header className={panel.kind === 'files' ? 'panel-head is-compact' : 'panel-head'}>
        {panelHeadOf(panel)}
        <div className="panel-head-side">
          {panel.kind === 'report' ? <ReportStatsView panel={panel} /> : null}
          <PanelControlsView panel={panel} />
        </div>
      </header>
      {panelBodyOf(panel)}
    </aside>
  )
}

export function SidePanelsView() {
  const { state } = useBoard()
  const panels = [...state.panels].sort((one, other) => KIND_ORDER.indexOf(one.kind) - KIND_ORDER.indexOf(other.kind))
  return (
    <>
      {panels.map(panel => (
        <SidePanelView key={panel.kind} panel={panel} />
      ))}
    </>
  )
}
