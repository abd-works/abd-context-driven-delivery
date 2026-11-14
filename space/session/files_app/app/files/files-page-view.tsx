import { Component, useEffect, useSyncExternalStore, type ReactNode } from 'react'

import type { FileEntryData, SessionFileData } from '@cdd/space/session/session'

import { FileSourceView } from './file-source-view'
import type { FilesPage } from './files-page'
import { isDrawio } from './files-paths'

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
  return (
    <ul className="file-list" aria-label="Files">
      {state.entries.map(entry => (
        <FileEntryView key={entry.path} page={page} entry={entry} isOpen={entry.path === state.openPath} />
      ))}
    </ul>
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

// The Files app's page: the files its link names down the side, the open one beside them, and what went wrong.
export function FilesPageView({ page }: { page: FilesPage }) {
  const { problem } = useFilesState(page)
  useEffect(() => page.start(), [page])
  return (
    <main className="files-page">
      <header className="files-head">
        <span className="files-kind">FILES</span>
        <span className="files-subject">{page.link.subject}</span>
      </header>
      {problem ? <div className="files-problem" role="alert">{problem}</div> : null}
      <div className="files-body">
        <nav className="files-side">
          <FileListView page={page} />
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
