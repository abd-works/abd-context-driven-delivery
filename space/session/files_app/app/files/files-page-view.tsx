import { Component, useEffect, useState, useSyncExternalStore, type CSSProperties, type ReactNode } from 'react'

import type { FileEntryData, SessionFileData } from '@cdd/space/session/session'

import type { FileFolder } from './file-bar'
import { FileSourceView } from './file-source-view'
import type { FilesPage } from './files-page'
import { drawioPageOf, isDrawio } from './files-paths'
import { formatGlyphOf } from './format-chips'
import { applyTheme, storedTheme, type FilesTheme } from './files-theme'

const fileNameOf = (path: string): string => path.split('/').at(-1) ?? path
// A design canvas's canvas.json is named by its version's folder: `design-canvas/version-2/project/canvas.json` is version-2.
const canvasNameOf = (path: string): string => path.split('/').at(-3) ?? path

function useFilesState(page: FilesPage) {
  return useSyncExternalStore(page.store.subscribe, () => page.store.state)
}

// One file the link names: a .drawio file says it opens in the draw.io viewer, a file not there yet says so, and a file
// published at a link, such as a design canvas, opens there, in Claude Design, in a tab of its own.
function FileEntryView({ page, entry, isOpen }: { page: FilesPage; entry: FileEntryData; isOpen: boolean }) {
  if (entry.link) return <PublishedFileView entry={entry} />
  const classes = ['file-entry', isOpen ? 'is-open' : '', entry.exists ? '' : 'is-missing', entry.is_changed ? 'is-changed' : ''].filter(Boolean).join(' ')
  if (isDrawio(entry.path) && entry.exists) return <DrawioFileView page={page} entry={entry} />
  const hint = entry.exists ? entry.path : `${entry.path}: not generated yet`
  return (
    <li>
      <button className={classes} title={hint} aria-current={isOpen ? 'true' : undefined} disabled={!entry.exists} onClick={() => void page.open(entry.path)}>
        {fileNameOf(entry.path)}
        {entry.exists ? null : <span className="file-entry-note"> not generated yet</span>}
      </button>
    </li>
  )
}

// A .drawio file: a link that opens the draw.io viewer on it in a tab of its own, so this tab keeps its file list. A
// link is a navigation the browser always allows, where a tab a script opens can be refused.
function DrawioFileView({ page, entry }: { page: FilesPage; entry: FileEntryData }) {
  const classes = ['file-entry', 'is-drawio', entry.is_changed ? 'is-changed' : ''].filter(Boolean).join(' ')
  return (
    <li>
      <a className={classes} href={drawioPageOf(entry.path, page.link.chat)} target="_blank" rel="noreferrer" title={`${entry.path}: opens in the draw.io viewer`}>
        {fileNameOf(entry.path)}
        <span className="file-entry-note"> ↗ draw.io</span>
      </a>
    </li>
  )
}

// A design canvas: its version's folder names it, and it opens at the link it is published at.
function PublishedFileView({ entry }: { entry: FileEntryData }) {
  return (
    <li>
      <a className="file-entry is-published" href={entry.link} target="_blank" rel="noreferrer" title={`${entry.path}: opens the design canvas at ${entry.link}`}>
        {canvasNameOf(entry.path)}
        <span className="file-entry-note"> ↗ design canvas</span>
      </a>
    </li>
  )
}

function FileListView({ page }: { page: FilesPage }) {
  const state = useFilesState(page)
  if (state.isListing) return <p className="files-note">Reading the files…</p>
  if (!state.entries.length) return <p className="files-note">{page.emptyReason}</p>
  if (!page.fileBar.entries.length) return <p className="files-note">The branch changed none of these files.</p>
  if (state.fileBar.view === 'folders') return <FileFoldersView page={page} />
  return (
    <ul className="file-list" aria-label="Files">
      {page.fileBar.entries.map(entry => (
        <FileEntryView key={entry.path} page={page} entry={entry} isOpen={entry.path === state.openPath} />
      ))}
    </ul>
  )
}

// The files in their folder tree, as Windows Explorer shows it: folders open and close, each level indented.
function FileFoldersView({ page }: { page: FilesPage }) {
  const { openPath } = useFilesState(page)
  return (
    <ul className="file-tree" role="tree" aria-label="Folders">
      <FolderContentsView page={page} folder={page.fileBar.tree} openPath={openPath} />
    </ul>
  )
}

// What a folder holds: its folders, then its files.
function FolderContentsView({ page, folder, openPath }: { page: FilesPage; folder: FileFolder; openPath: string }) {
  return (
    <>
      {folder.folders.map(inner => (
        <FileFolderView key={inner.path} page={page} folder={inner} openPath={openPath} />
      ))}
      {folder.files.map(entry => (
        <FileEntryView key={entry.path} page={page} entry={entry} isOpen={entry.path === openPath} />
      ))}
    </>
  )
}

// One folder: a row that opens and closes it, and what it holds, one level in, while it is open.
function FileFolderView({ page, folder, openPath }: { page: FilesPage; folder: FileFolder; openPath: string }) {
  const isOpen = page.fileBar.isOpen(folder)
  return (
    <li role="treeitem" aria-expanded={isOpen}>
      <button className="file-folder" title={folder.path} onClick={() => page.fileBar.toggleFolder(folder.path)}>
        <span className="file-folder-mark">{isOpen ? '▾' : '▸'}</span>
        <span className="file-folder-icon">{isOpen ? '📂' : '📁'}</span>
        <span className="file-folder-name">{folder.name}</span>
      </button>
      {isOpen ? (
        <ul className="file-tree-level" role="group">
          <FolderContentsView page={page} folder={folder} openPath={openPath} />
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
          <button className="file-bar-view" aria-pressed={fileBar.isChangedOnly} title="List only the files the session's branch changed" onClick={() => page.fileBar.toggleChangedOnly()}>
            Changed <span className="file-entry-note">{page.fileBar.changedCount}</span>
          </button>
        </>
      ) : null}
    </div>
  )
}

// The session's practices along the top, each a toggle in its practice colour: filled while selected, which is the
// session working on it, an outline while it is off. A press turns it on or off for the session, here and on the chat bar.
function PracticeTogglesView({ page }: { page: FilesPage }) {
  const { guidance } = useFilesState(page)
  if (!guidance?.practices.length) return null
  return (
    <div className="practice-toggles" role="group" aria-label="Practices">
      {guidance.practices.map(practice => (
        <button
          key={practice.key}
          type="button"
          className={`practice-toggle ${practice.is_selected ? 'is-on' : 'is-off'}`}
          style={{ '--practice-colour': practice.colour } as CSSProperties}
          aria-pressed={practice.is_selected}
          title={`${practice.short_name}: ${practice.is_selected ? 'on, press to turn it off here and on the chat bar' : 'off, press to turn it on here and on the chat bar'}`}
          onClick={() => void page.togglePractice(practice.key)}
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

// The chat bar's icon for each stage (harness/chat-ui/pane/hooks/chat-bar/stage-client.ts STAGE_ICONS), so a stage looks
// the same on the bar and here.
const STAGE_ICONS: Record<string, string> = { Discovery: '⌕', Specification: '▤', Implementation: '⚙' }

// A button for each stage, before the practices, as the chat bar's stage buttons: filled orange while selected. A press
// selects the stage beside those selected, or no longer, here and on the chat bar.
function StageTogglesView({ page }: { page: FilesPage }) {
  const { guidance } = useFilesState(page)
  if (!guidance?.stages.length) return null
  return (
    <div className="stage-toggles" role="group" aria-label="Stages">
      {guidance.stages.map(stage => (
        <button
          key={stage.name}
          type="button"
          className={`stage-toggle ${stage.is_selected ? 'is-shown' : ''}`}
          aria-pressed={stage.is_selected}
          title={`${stage.title}: ${stage.is_selected ? 'selected, press to hide its files here and on the chat bar' : 'press to show its files here and on the chat bar'}`}
          onClick={() => void page.toggleStage(stage.name)}
        >
          {STAGE_ICONS[stage.title] ?? stage.title}
        </button>
      ))}
    </div>
  )
}

// The format groups the selected fidelities offer, after the practices, with the chat bar's glyphs: filled orange while
// selected. A press selects it or no longer, here and on the chat bar; while any is selected, the list shows only the
// files in the formats selected.
function FormatTogglesView({ page }: { page: FilesPage }) {
  const { guidance } = useFilesState(page)
  if (!guidance?.formats.length) return null
  return (
    <div className="format-toggles" role="group" aria-label="Formats">
      {guidance.formats.map(format => (
        <button
          key={format.label}
          type="button"
          className={`format-toggle ${format.is_selected ? 'is-chosen' : 'is-not-made'}`}
          aria-pressed={format.is_selected}
          title={`${format.label}: offered by ${format.offered}; ${format.is_selected ? 'selected, press to show every format' : 'press to show only the formats selected'}`}
          onClick={() => void page.toggleFormat(format.label)}
        >
          {formatGlyphOf(format.label)}
        </button>
      ))}
    </div>
  )
}

// What the open file is read with, each on its own and both off by default, so browsing never reads a graph: Rules shows
// its folds and its own broken rules, the file read alone; Cross-file the rules only the whole working copy finds,
// linking files and practices, which takes far longer.
function ReadsTogglesView({ page }: { page: FilesPage }) {
  const { reads } = useFilesState(page)
  return (
    <div className="reads-toggles" role="group" aria-label="Read the open file with">
      <button type="button" className="file-bar-view" aria-pressed={reads.rules} title="The file's own rules, read on its own: under a second" onClick={() => void page.toggleRules()}>
        Rules
      </button>
      <button type="button" className="file-bar-view" aria-pressed={reads.crossFile} title="Only the rules that link files and practices: the graph reads the whole working copy first, which takes far longer" onClick={() => void page.toggleCrossFile()}>
        Cross-file
      </button>
    </div>
  )
}

// Dark engineering by default; a press turns the light look on or off.
function ThemeToggleView({ page }: { page: FilesPage }) {
  const failed = (failure: string) => page.fail(failure, "Changing the Files app's look")
  const [theme, setTheme] = useState<FilesTheme>(() => storedTheme(failed))
  const toggle = () => {
    const next = theme === 'engineering' ? 'light' : 'engineering'
    applyTheme(next, failed)
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
        <span className="files-subject">{page.heading}</span>
        <StageTogglesView page={page} />
        <PracticeTogglesView page={page} />
        <FormatTogglesView page={page} />
        <ReadsTogglesView page={page} />
        <ThemeToggleView page={page} />
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
export class FilesFailureView extends Component<{ page: FilesPage; children: ReactNode }, { failure: string }> {
  state = { failure: '' }

  static getDerivedStateFromError(error: unknown) {
    return { failure: error instanceof Error ? error.message : String(error) }
  }

  // What stopped the page goes to the chat that opened it too, since the page can show nothing else now.
  componentDidCatch(error: unknown) {
    this.props.page.fail(`The Files page stopped: ${error instanceof Error ? error.message : String(error)}`, 'Drawing the Files page', { isShownOnPage: true })
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
