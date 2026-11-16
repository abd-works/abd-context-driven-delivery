import { Component, useCallback, useEffect, useState, useSyncExternalStore, type CSSProperties, type ReactNode } from 'react'

import type { FileEntryData, SessionFileData } from '@cdd/space/session/session'

import type { FileFolder } from './file-bar'
import { FileSourceView } from './file-source-view'
import type { FilesPage } from './files-page'
import { drawioPageOf, isDrawio, revealLabelOf } from './files-paths'
import { formatGlyphOf } from './format-chips'
import { applyTheme, storedTheme, type FilesTheme } from './files-theme'

const fileNameOf = (path: string): string => path.split('/').at(-1) ?? path
// A design canvas's canvas.json is named by its version's folder: `design-canvas/version-2/project/canvas.json` is version-2.
const canvasNameOf = (path: string): string => path.split('/').at(-3) ?? path

function useFilesState(page: FilesPage) {
  return useSyncExternalStore(page.store.subscribe, () => page.store.state)
}

// One file the link names: a file not there yet says so, and a file published at a link, such as a design canvas, opens
// there, in Claude Design, in a tab of its own; a .drawio file also offers its draw.io editor in a tab of its own.
function FileEntryView({ page, entry, isOpen }: { page: FilesPage; entry: FileEntryData; isOpen: boolean }) {
  if (entry.link) return <PublishedFileView entry={entry} />
  const classes = ['file-entry', isOpen ? 'is-open' : '', entry.exists ? '' : 'is-missing', entry.is_changed ? 'is-changed' : ''].filter(Boolean).join(' ')
  const hint = entry.exists ? entry.path : `${entry.path}: not generated yet`
  return (
    <li className="file-entry-row">
      <button className={classes} title={hint} aria-current={isOpen ? 'true' : undefined} disabled={!entry.exists} onClick={() => void page.open(entry.path)} onContextMenu={menuOn(page, entry.path)}>
        {fileNameOf(entry.path)}
        {entry.exists ? null : <span className="file-entry-note"> not generated yet</span>}
      </button>
      {isDrawio(entry.path) && entry.exists ? <DrawioTabLinkView page={page} path={entry.path} /> : null}
    </li>
  )
}

// The draw.io editor on a .drawio file in a tab of its own, where the browser opens one; the app's browser pane opens
// none, which is why the file view shows the editor too. A link is a navigation the browser always allows, where a tab
// a script opens can be refused.
function DrawioTabLinkView({ page, path }: { page: FilesPage; path: string }) {
  return (
    <a className="drawio-tab-link" href={drawioPageOf(path, page.link.chat)} target="_blank" rel="noreferrer" title={`${path}: opens in the draw.io editor in a tab of its own`}>
      ↗
    </a>
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

// A right-click on a file or folder: its menu instead of the browser's.
const menuOn = (page: FilesPage, path: string) => (event: React.MouseEvent) => {
  event.preventDefault()
  page.menu.open(path, event.clientX, event.clientY)
}

// The menu a right-click shows, where the person clicked: show the file or folder in the system's file browser, named
// for this system. A press anywhere else closes it.
function FileMenuView({ page }: { page: FilesPage }) {
  const { menu } = useFilesState(page)
  if (!menu) return null
  return (
    <div className="file-menu-backdrop" onClick={() => page.menu.close()} onContextMenu={event => { event.preventDefault(); page.menu.close() }}>
      <div className="file-menu" role="menu" style={{ left: menu.x, top: menu.y }} onClick={event => event.stopPropagation()}>
        <button role="menuitem" title={`${menu.path}: goes with your next prompt in the chat that opened this page`} onClick={() => void page.menu.addToContext()}>
          Add to context
        </button>
        <button role="menuitem" title={menu.path} onClick={() => void page.menu.reveal()}>
          {revealLabelOf(navigator.platform)}
        </button>
      </div>
    </div>
  )
}

// One folder: a row that opens and closes it, and what it holds, one level in, while it is open.
function FileFolderView({ page, folder, openPath }: { page: FilesPage; folder: FileFolder; openPath: string }) {
  const isOpen = page.fileBar.isOpen(folder)
  return (
    <li role="treeitem" aria-expanded={isOpen}>
      <button className="file-folder" title={folder.path} onClick={() => page.fileBar.toggleFolder(folder.path)} onContextMenu={menuOn(page, folder.path)}>
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

// The line between the file bar and the open file: dragged, it makes the bar as wide as the pointer is from the bar's
// left edge. The divider keeps the pointer while dragging, so the drag goes on over the editor.
function FileBarDividerView({ page }: { page: FilesPage }) {
  const widthAt = (event: React.PointerEvent<HTMLDivElement>) => {
    const bar = event.currentTarget.previousElementSibling
    if (bar) page.fileBar.resize(event.clientX - bar.getBoundingClientRect().left)
  }
  return (
    <div
      className="file-bar-divider"
      role="separator"
      aria-orientation="vertical"
      aria-label="Drag to resize the file bar"
      title="Drag to resize the file bar"
      onPointerDown={event => event.currentTarget.setPointerCapture(event.pointerId)}
      onPointerMove={event => (event.currentTarget.hasPointerCapture(event.pointerId) ? widthAt(event) : undefined)}
      onPointerUp={event => event.currentTarget.releasePointerCapture(event.pointerId)}
    />
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
          onClick={() => void page.guidance.togglePractice(practice.key)}
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
      <span className="files-hint">Select lines, right-click, Add comment or Add to context</span>
    </div>
  )
}

// A .drawio file in the draw.io editor, beside the file list: the Files server's draw.io page starts the viewer on it,
// or says in the frame why it did not, as it tells the chat.
function DrawioFileView({ page, path }: { page: FilesPage; path: string }) {
  return (
    <section className="open-file open-diagram" aria-label={path}>
      <div className="comment-toolbar">
        <span className="source-path">{path}</span>
        <DrawioTabLinkView page={page} path={path} />
      </div>
      <iframe className="drawio-frame" title={`${path} in the draw.io editor`} src={drawioPageOf(path, page.link.chat)} />
    </section>
  )
}

function OpenFileView({ page }: { page: FilesPage }) {
  const state = useFilesState(page)
  const path = state.file?.path ?? ''
  // The open file's selected lines, added to the chat's context; made once per file, so the editor keeps its action.
  const addLines = useCallback((lines: { start: number; end: number }) => void page.chatContext.add(path, lines), [page, path])
  if (!state.openPath) return <p className="files-note">Choose a file.</p>
  if (isDrawio(state.openPath)) return <DrawioFileView page={page} path={state.openPath} />
  if (!state.file) return <p className="files-note">Opening {state.openPath}…</p>
  return (
    <section className="open-file" aria-label={state.file.path}>
      <CommentToolbarView page={page} file={state.file} />
      <FileSourceView key={state.file.path} file={state.file} actions={page.comments} onAddToContext={addLines} />
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
// Which files the page lists, first of the filters along the top and orange while selected, as the stages are: every
// file under the session's root, or the ones this session's branch changed, with how many.
function ScopeTogglesView({ page }: { page: FilesPage }) {
  const { scope } = useFilesState(page)
  return (
    <div className="scope-toggles" role="group" aria-label="Files listed">
      <button type="button" className={`scope-toggle ${scope === 'all' ? 'is-shown' : ''}`} aria-pressed={scope === 'all'} aria-label="All session files" title="All session files: every file of the stages, practices and formats selected, older work included" onClick={() => page.showScope('all')}>
        ▤
      </button>
      <button type="button" className={`scope-toggle ${scope === 'session' ? 'is-shown' : ''}`} aria-pressed={scope === 'session'} aria-label="This session" title={`This session: the ${page.fileBar.changedCount} files this session's branch changed, among those its stages, practices and formats select`} onClick={() => page.showScope('session')}>
        Δ<sup className="scope-count">{page.fileBar.changedCount}</sup>
      </button>
    </div>
  )
}

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
          onClick={() => void page.guidance.toggleStage(stage.name)}
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
          onClick={() => void page.guidance.toggleFormat(format.label)}
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
  const failed = (failure: string) => page.notices.fail(failure, "Changing the Files app's look")
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
        <ScopeTogglesView page={page} />
        <StageTogglesView page={page} />
        <PracticeTogglesView page={page} />
        <FormatTogglesView page={page} />
        <ReadsTogglesView page={page} />
        <ThemeToggleView page={page} />
      </header>
      {problem ? <div className="files-problem" role="alert">{problem}</div> : null}
      <div className={`files-body ${fileBar.isOpen ? '' : 'is-bar-collapsed'}`} style={fileBar.isOpen ? { gridTemplateColumns: `${fileBar.width}px auto 1fr` } : undefined}>
        <nav className="files-side">
          <FileBarButtonsView page={page} />
          {fileBar.isOpen ? <FileListView page={page} /> : null}
        </nav>
        {fileBar.isOpen ? <FileBarDividerView page={page} /> : null}
        <OpenFileView page={page} />
      </div>
      <FileMenuView page={page} />
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
    this.props.page.notices.fail(`The Files page stopped: ${error instanceof Error ? error.message : String(error)}`, 'Drawing the Files page', { isShownOnPage: true })
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
