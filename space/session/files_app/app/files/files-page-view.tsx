import { Component, useEffect, useState, useSyncExternalStore, type CSSProperties, type ReactNode } from 'react'

import type { FileEntryData, SessionFileData } from '@cdd/space/session/session'

import type { FileFolder } from './file-bar'
import { FileSourceView } from './file-source-view'
import type { FilesPage } from './files-page'
import { isDrawio } from './files-paths'
import { applyTheme, storedTheme, type FilesTheme } from './files-theme'

const fileNameOf = (path: string): string => path.split('/').at(-1) ?? path

function useFilesState(page: FilesPage) {
  return useSyncExternalStore(page.store.subscribe, () => page.store.state)
}

// One file the link names: a .drawio file says it opens in the draw.io viewer, a file not there yet says so.
function FileEntryView({ page, entry, isOpen }: { page: FilesPage; entry: FileEntryData; isOpen: boolean }) {
  const classes = ['file-entry', isOpen ? 'is-open' : '', entry.exists ? '' : 'is-missing', entry.is_changed ? 'is-changed' : ''].filter(Boolean).join(' ')
  const hint = isDrawio(entry.path) ? `${entry.path}: opens in the draw.io viewer` : entry.exists ? entry.path : `${entry.path}: not generated yet`
  return (
    <li>
      <button className={classes} title={hint} aria-current={isOpen ? 'true' : undefined} disabled={!entry.exists} onClick={() => void page.open(entry.path)}>
        {fileNameOf(entry.path)}
        {isDrawio(entry.path) ? <span className="file-entry-note"> ↗ draw.io</span> : null}
      </button>
    </li>
  )
}

function FileListView({ page }: { page: FilesPage }) {
  const state = useFilesState(page)
  if (state.isListing) return <p className="files-note">Reading the files…</p>
  if (!state.entries.length) return <p className="files-note">No files here yet.</p>
  if (state.fileBar.view === 'folders') return <FileFoldersView page={page} />
  return (
    <ul className="file-list" aria-label="Files">
      {state.entries.map(entry => (
        <FileEntryView key={entry.path} page={page} entry={entry} isOpen={entry.path === state.openPath} />
      ))}
    </ul>
  )
}

// The files in their folders, each folder a row that opens and closes to show the files directly in it.
function FileFoldersView({ page }: { page: FilesPage }) {
  const { openPath } = useFilesState(page)
  return (
    <ul className="file-folders" aria-label="Folders">
      {page.fileBar.folders.map(folder => (
        <FileFolderView key={folder.path} page={page} folder={folder} openPath={openPath} />
      ))}
    </ul>
  )
}

// One folder: a row that opens and closes it, and its files while it is open.
function FileFolderView({ page, folder, openPath }: { page: FilesPage; folder: FileFolder; openPath: string }) {
  const isOpen = page.fileBar.isOpen(folder)
  return (
    <li>
      <button className="file-folder" title={folder.path || 'the project folder'} aria-expanded={isOpen} onClick={() => page.fileBar.toggleFolder(folder.path)}>
        <span className="file-folder-mark">{isOpen ? '▾' : '▸'}</span> {folder.name || '/'}<span className="file-entry-note">{folder.files.length}</span>
      </button>
      {isOpen ? (
        <ul className="file-list">
          {folder.files.map(entry => (
            <FileEntryView key={entry.path} page={page} entry={entry} isOpen={entry.path === openPath} />
          ))}
        </ul>
      ) : null}
    </li>
  )
}

// The file bar's buttons: collapse or expand it, and show its files as a list or in their folders.
function FileBarButtonsView({ page }: { page: FilesPage }) {
  const { fileBar } = useFilesState(page)
  return (
    <div className="file-bar-buttons" role="toolbar" aria-label="File bar">
      <button aria-label={fileBar.isOpen ? 'Collapse the file bar' : 'Expand the file bar'} title={fileBar.isOpen ? 'Collapse the file bar' : 'Expand the file bar'} onClick={() => page.fileBar.toggle()}>
        {fileBar.isOpen ? '«' : '»'}
      </button>
      {fileBar.isOpen ? (
        <>
          <button className="file-bar-view" aria-pressed={fileBar.view === 'list'} title="Show the files as a list" onClick={() => page.fileBar.show('list')}>
            List
          </button>
          <button className="file-bar-view" aria-pressed={fileBar.view === 'folders'} title="Show the files in their folders" onClick={() => page.fileBar.show('folders')}>
            Folders
          </button>
        </>
      ) : null}
    </div>
  )
}

// The session's practices along the top, each a toggle in its practice colour: filled while the session works on it,
// an outline while it is off. A press turns it on or off for the session, here and on the chat bar.
function PracticeTogglesView({ page }: { page: FilesPage }) {
  const { practices } = useFilesState(page)
  if (!practices.length) return null
  return (
    <div className="practice-toggles" role="group" aria-label="Practices">
      {practices.map(practice => (
        <button
          key={practice.name}
          className={`practice-toggle ${practice.enabled ? 'is-on' : 'is-off'}`}
          style={{ '--practice-colour': practice.colour } as CSSProperties}
          aria-pressed={practice.enabled}
          title={`${practice.short_name}: ${practice.enabled ? 'on, press to hide its files' : 'off, press to show its files'}`}
          onClick={() => void page.togglePractice(practice.name)}
        >
          {practice.short_name}
        </button>
      ))}
    </div>
  )
}

// The open file's comment actions along the top left: send every comment not yet sent, clear the processed ones.
function CommentToolbarView({ page, file }: { page: FilesPage; file: SessionFileData }) {
  const open = file.comments.filter(comment => comment.state === 'not_sent').length
  const processed = file.comments.filter(comment => comment.state === 'processed').length
  return (
    <div className="comment-toolbar">
      <button disabled={!open} onClick={() => void page.comments.sendOpen()}>
        Send all open comments{open ? ` (${open})` : ''}
      </button>
      <button disabled={!processed} onClick={() => void page.comments.clearProcessed()}>
        Clear processed{processed ? ` (${processed})` : ''}
      </button>
      <span className="files-hint">Select lines, right-click, Add comment</span>
    </div>
  )
}

function OpenFileView({ page }: { page: FilesPage }) {
  const state = useFilesState(page)
  if (!state.openPath) return <p className="files-note">Choose a file.</p>
  if (!state.file) return <p className="files-note">Opening {state.openPath}…</p>
  return (
    <section className="open-file" aria-label={state.file.path}>
      <CommentToolbarView page={page} file={state.file} />
      <FileSourceView key={state.file.path} file={state.file} actions={page.comments} />
    </section>
  )
}

function ToastsView({ page }: { page: FilesPage }) {
  const { toasts } = useFilesState(page)
  return (
    <div className="toasts" role="status">
      {toasts.map(text => (
        <div key={text} className="toast">
          {text}
        </div>
      ))}
    </div>
  )
}

// Dark engineering by default; a press turns the light look on or off.
function ThemeToggleView() {
  const [theme, setTheme] = useState<FilesTheme>(storedTheme)
  const toggle = () => {
    const next = theme === 'engineering' ? 'light' : 'engineering'
    applyTheme(next)
    setTheme(next)
  }
  return (
    <button type="button" className="theme-toggle" aria-pressed={theme === 'light'} title={theme === 'engineering' ? 'Light look' : 'Dark engineering look'} onClick={toggle}>
      {theme === 'engineering' ? '☀' : '◐'}
    </button>
  )
}

// The Files app's page: the files its link names down the side, the open one beside them, and what went wrong.
export function FilesPageView({ page }: { page: FilesPage }) {
  const { problem, fileBar } = useFilesState(page)
  useEffect(() => page.start(), [page])
  return (
    <main className="files-page">
      <header className="files-head">
        <span className="files-kind">FILES</span>
        <span className="files-subject">{page.link.subject}</span>
        <PracticeTogglesView page={page} />
        <ThemeToggleView />
      </header>
      {problem ? <div className="files-problem" role="alert">{problem}</div> : null}
      <div className={`files-body ${fileBar.isOpen ? '' : 'is-bar-collapsed'}`}>
        <nav className="files-side">
          <FileBarButtonsView page={page} />
          {fileBar.isOpen ? <FileListView page={page} /> : null}
        </nav>
        <OpenFileView page={page} />
      </div>
      <ToastsView page={page} />
    </main>
  )
}

// A view that throws would otherwise leave an empty page, so the person sees what broke.
export class FilesFailureView extends Component<{ children: ReactNode }, { failure: string }> {
  state = { failure: '' }

  static getDerivedStateFromError(error: unknown) {
    return { failure: error instanceof Error ? error.message : String(error) }
  }

  render() {
    if (!this.state.failure) return this.props.children
    return (
      <main className="files-page">
        <div className="files-problem" role="alert">
          The Files page stopped: {this.state.failure}
        </div>
      </main>
    )
  }
}
