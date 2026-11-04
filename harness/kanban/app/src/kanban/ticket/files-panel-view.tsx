import { useEffect, useRef } from 'react'

import { guidanceSlug } from '../board/board-brand'
import { useBoard } from '../board/board-context'
import type { FilesPanel } from '../board/board-store'
import { folderGroupsOf, generatedPaths } from './files-panel-client'

const FILE_MODES = ['folder', 'files']
const NOT_GENERATED = ['Not generated yet.', 'Pick this format on the card, then generate or render it.']

const fileNameOf = (path: string): string => path.split('/').at(-1) ?? path

export function FilesPanelHeadView({ panel }: { panel: FilesPanel }) {
  const { page } = useBoard()
  return (
    <div className="panel-words">
      <div className="panel-kind">
        FILES<span className="accent-mark">_</span>
      </div>
      <div className="files-subject">{panel.isSession ? `${panel.ticket} session folder` : panel.slugs.map(guidanceSlug).join(', ')}</div>
      <div className="file-modes">
        {FILE_MODES.map(mode => (
          <button key={mode} className={panel.mode === mode ? 'file-mode is-chosen' : 'file-mode'} onClick={() => void page.files.chooseMode(mode)}>
            {mode}
          </button>
        ))}
      </div>
    </div>
  )
}

function FolderGroupsView({ paths }: { paths: string[] }) {
  const { page } = useBoard()
  return (
    <div className="folder-groups">
      {folderGroupsOf(paths).map(folder => (
        <div key={folder.root} className="folder-group">
          <div className="folder-root">{folder.root}</div>
          {folder.entries.map(entry => (
            <button key={entry.path} className="file-link folder-entry" onClick={() => void page.files.openTab(entry.path)}>
              {entry.name}
            </button>
          ))}
        </div>
      ))}
    </div>
  )
}

function FileTabView({ panel, path }: { panel: FilesPanel; path: string }) {
  const { page } = useBoard()
  const name = fileNameOf(path)
  const isActive = path === panel.activeTab
  return (
    <div className={isActive ? 'file-tab is-active' : 'file-tab'}>
      <button role="tab" aria-selected={isActive} title={path} className="file-tab-name" onClick={() => void page.files.openTab(path)}>
        {name}
      </button>
      <button aria-label={`Close ${name}`} className="file-tab-close" onClick={() => page.files.closeTab(path)}>
        ×
      </button>
    </div>
  )
}

// A file opened from a violation shows its failing line, in the middle of the panel.
function FileLinesView({ text, marked }: { text: string; marked: number }) {
  const line = useRef<HTMLDivElement>(null)
  // Braces matter: newer browsers return a promise from scrollIntoView, and React would call it as the effect's cleanup.
  useEffect(() => {
    line.current?.scrollIntoView({ block: 'center' })
  }, [marked, text])
  const lines = text ? text.split('\n') : NOT_GENERATED
  return (
    <div className="file-lines">
      {lines.map((entry, index) => {
        const isMarked = index + 1 === marked
        return (
          <div key={index} ref={isMarked ? line : undefined} className={isMarked ? 'code-line is-failing' : 'code-line'}>
            <span className="line-number">{index + 1}</span>
            <span className="line-text">{entry}</span>
          </div>
        )
      })}
    </div>
  )
}

function FileTabsView({ panel }: { panel: FilesPanel }) {
  return (
    <div className="file-tabs-body">
      <div role="tablist" className="file-tabs">
        {panel.tabs.map(path => (
          <FileTabView key={path} panel={panel} path={path} />
        ))}
      </div>
      <div className="active-file">{panel.activeTab}</div>
      <FileLinesView text={panel.texts[panel.activeTab] ?? ''} marked={panel.lines[panel.activeTab] ?? 0} />
    </div>
  )
}

export function FilesPanelBodyView({ panel }: { panel: FilesPanel }) {
  const paths = generatedPaths(panel)
  if (panel.mode === 'files' && panel.tabs.length) return <FileTabsView panel={panel} />
  if (panel.mode === 'files' || !paths.length) return <p className="panel-note files-empty">Nothing generated yet for this fidelity.</p>
  return (
    <div className="panel-body files-body">
      <FolderGroupsView paths={paths} />
    </div>
  )
}
