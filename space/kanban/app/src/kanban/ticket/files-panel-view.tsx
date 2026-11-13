import { useBoard } from '../shared/board-context'
import type { FilesPanel } from '../shared/board-store'
import { FileViewerView } from './file-viewer-view'
import { practicesOf, shownTabs } from './files-panel-client'
import type { FileTab } from './files-panel-client'

const fileNameOf = (path: string): string => path.split('/').at(-1) ?? path

function subjectOf(panel: FilesPanel): string {
  if (panel.source === 'session') return `${panel.ticket.name} session folder`
  if (panel.source === 'workpath') return panel.ticket.session.workpath || 'whole repository'
  return `${panel.ticket.name} · ${panel.ticket.stagePlace}`
}

// A toggle per practice of the ticket's stage, by its short form and in its colour, then the changed-files filter.
function FileFiltersView({ panel }: { panel: FilesPanel }) {
  const { page } = useBoard()
  return (
    <div className="file-filters" role="group" aria-label="File filters">
      {practicesOf(panel).map(key => {
        const practice = page.board.practiceNamed(key)
        const isOn = panel.practicesOn.includes(key)
        return (
          <button key={key} className={isOn ? 'practice-filter is-on' : 'practice-filter'} aria-pressed={isOn} title={`Show ${practice?.name ?? key} files`} style={{ borderColor: practice?.color, background: isOn ? practice?.color : undefined }} onClick={() => void page.files.togglePractice(key)}>
            {practice?.name ?? key}
          </button>
        )
      })}
      <label className="changed-filter">
        <input type="checkbox" checked={panel.changedOnly} onChange={event => void page.files.filterChanged(event.target.checked)} />
        only changed files
      </label>
    </div>
  )
}

export function FilesPanelHeadView({ panel }: { panel: FilesPanel }) {
  return (
    <div className="panel-words">
      <div className="panel-kind">
        FILES<span className="accent-mark">_</span>
      </div>
      <div className="files-subject">{subjectOf(panel)}</div>
      <FileFiltersView panel={panel} />
    </div>
  )
}

function FileTabView({ panel, tab }: { panel: FilesPanel; tab: FileTab }) {
  const { page } = useBoard()
  const color = tab.practice ? page.board.practiceNamed(tab.practice)?.color : undefined
  const isActive = tab.path === panel.activeTab
  return (
    <div className={isActive ? 'file-tab is-active' : 'file-tab'} data-practice={tab.practice || undefined} style={{ borderTopColor: color }}>
      <button role="tab" aria-selected={isActive} title={tab.path} className={tab.exists ? 'file-tab-name' : 'file-tab-name is-missing'} onClick={() => void page.files.openTab(tab.path)}>
        {fileNameOf(tab.path)}
      </button>
    </div>
  )
}

export function FilesPanelBodyView({ panel }: { panel: FilesPanel }) {
  const tabs = shownTabs(panel)
  return (
    <div className="file-tabs-body">
      <div role="tablist" className="file-tabs">
        {tabs.map(tab => (
          <FileTabView key={tab.path} panel={panel} tab={tab} />
        ))}
      </div>
      {tabs.length ? <div className="active-file">{panel.activeTab}</div> : <p className="panel-note files-empty">No files to show: turn a filter on.</p>}
      {panel.activeTab ? <FileViewerView key={panel.activeTab} file={panel.shown} marked={panel.lines[panel.activeTab] ?? 0} /> : null}
    </div>
  )
}
