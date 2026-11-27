import { Component, useCallback, useEffect, useState, useSyncExternalStore, type CSSProperties, type ReactNode } from 'react'

import type { FileEntryData, SessionFileData } from '@cdd/space/session/session'

import { entryClassesOf, publishedOf, type FileFolder, type PublishedFile } from './file-bar'
import type { SourceCallout } from '@source-view/source-callouts'

import { FailureBandView } from './failure-band-view'
import { FormatAlignmentView } from './format-alignment-view'
import { FileView } from './file-view'
import { FilesGraphView } from './files-graph-view'
import type { FilesPage } from './files-page'
import { SCROLLING_PANE } from './file-source-view'
import { drawioPageOf, isDrawio, isWhiteboard, missingNoteOf, revealLabelOf } from './files-paths'
import { formatGlyphOf } from './format-chips'
import { applyTheme, storedTheme, type FilesTheme } from './files-theme'

const fileNameOf = (path: string): string => path.split('/').at(-1) ?? path

function useFilesState(page: FilesPage) {
  return useSyncExternalStore(page.store.subscribe, () => page.store.state)
}

// One file the link names: a file it cannot open says why, not generated yet or deleted on this branch; a whiteboard
// opens as a canvas; a design canvas opens in Claude Desktop's artifact panel; a .drawio file also offers its draw.io
// editor in a tab of its own.
function FileEntryView({ page, entry, isOpen }: { page: FilesPage; entry: FileEntryData; isOpen: boolean }) {
  const published = publishedOf(entry)
  if (published?.kind === 'whiteboard') return <WhiteboardEntryView page={page} entry={entry} published={published} isOpen={isOpen} />
  if (published) return <PublishedFileView page={page} entry={entry} published={published} />
  const hint = entry.exists ? entry.path : `${entry.path}: ${missingNoteOf(entry)}`
  return (
    <li className="file-entry-row">
      <button className={entryClassesOf(entry, isOpen)} title={hint} aria-current={isOpen ? 'true' : undefined} disabled={!entry.exists} onClick={() => void page.open(entry.path)} onContextMenu={menuOn(page, entry.path)}>
        {fileNameOf(entry.path)}
        {entry.exists ? null : <span className="file-entry-note"> {missingNoteOf(entry)}</span>}
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
    <a className="drawio-tab-link" href={drawioPageOf(path, page.link)} target="_blank" rel="noreferrer" title={`${path}: opens in the draw.io editor in a tab of its own`}>
      ↗
    </a>
  )
}

// A whiteboard on a board in Claude opens that board, in Claude Desktop's artifact panel, or in a browser when no chat
// opened the page; one not on a board yet says so, since the app never draws a board. One not on disk says why, as any
// file not on disk does.
function WhiteboardEntryView({ page, entry, published, isOpen }: { page: FilesPage; entry: FileEntryData; published: PublishedFile; isOpen: boolean }) {
  const hint = !entry.exists ? `${entry.path}: ${missingNoteOf(entry)}` : published.link ? `${entry.path}: opens its board in Claude` : `${entry.path}: not on a board in Claude yet`
  const note = entry.exists ? (published.link ? 'whiteboard' : 'whiteboard, not on a board in Claude yet') : `whiteboard, ${missingNoteOf(entry)}`
  const press = async () => {
    if (!(await page.press(entry))) window.open(published.link, '_blank', 'noreferrer')
  }
  return (
    <li className="file-entry-row">
      <button className={entryClassesOf(entry, isOpen)} title={hint} aria-current={isOpen ? 'true' : undefined} disabled={!entry.exists} onClick={() => void press()} onContextMenu={menuOn(page, entry.path)}>
        {published.name}
        <span className="file-entry-note"> {note}</span>
      </button>
      {published.link ? <BoardLinkView page={page} entry={entry} published={published} /> : null}
    </li>
  )
}

// The board in Claude a whiteboard was published to: it opens in Claude Desktop's artifact panel, beside the chat; a page
// no chat opened opens the link in a browser instead.
function BoardLinkView({ page, entry, published }: { page: FilesPage; entry: FileEntryData; published: PublishedFile }) {
  const open = async (event: { preventDefault: () => void }) => {
    event.preventDefault()
    if (!(await page.openPublished(entry))) window.open(published.link, '_blank', 'noreferrer')
  }
  return (
    <a className="drawio-tab-link board-link" href={published.link} onClick={event => void open(event)} rel="noreferrer" title={`${entry.path}: opens its board in Claude's artifact panel`}>
      ↗
    </a>
  )
}

// A design canvas: it opens in Claude Desktop's artifact panel, beside the chat, never as the file's text; a page no
// chat opened opens the link in a browser instead. One not published yet says so and opens nothing.
function PublishedFileView({ page, entry, published }: { page: FilesPage; entry: FileEntryData; published: PublishedFile }) {
  const path = entry.path
  if (!published.link) {
    return (
      <li>
        <button className="file-entry is-missing" title={`${path}: no ${published.kind} published in Claude yet`} disabled>
          {published.name}
          <span className="file-entry-note"> {published.kind}, not published yet</span>
        </button>
      </li>
    )
  }
  const open = async (event: { preventDefault: () => void }) => {
    event.preventDefault()
    if (!(await page.openPublished(entry))) window.open(published.link, '_blank', 'noreferrer')
  }
  return (
    <li>
      <a className="file-entry is-published" href={published.link} onClick={event => void open(event)} rel="noreferrer" title={`${path}: opens the ${published.kind} in Claude's artifact panel`}>
        {published.name}
        <span className="file-entry-note"> ↗ {published.kind}</span>
      </a>
    </li>
  )
}

function FileListView({ page }: { page: FilesPage }) {
  const state = useFilesState(page)
  if (state.isListing) return <p className="files-note">Reading the files…</p>
  if (state.filtering) return <p className="files-note files-filtering" role="status">Filtering by {state.filtering}…</p>
  // All files lists the session's folders whatever the selection lists, so a selection of no file hides none of them.
  if (state.scope !== 'everything' && !state.entries.length) return <p className="files-note">{page.emptyReason}</p>
  if (state.fileBar.view === 'graph') return <FilesGraphView page={page} />
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
// Where the source view tells a Wrap lines choice the browser would not read or keep.
const wrapFailed = (page: FilesPage) => (failure: string) => page.notices.fail(failure, 'Wrapping long lines in the source view')

const menuOn = (page: FilesPage, path: string) => (event: React.MouseEvent) => {
  event.preventDefault()
  page.menu.open(path, event.clientX, event.clientY)
}

// The menu a right-click shows, where the person clicked: add the file to the chat's context, show it in the system's
// file browser, named for this system, delete it once confirmed, validate it, display the rules broken in it, or add it to
// a practice as a root. A press anywhere else closes it.
function FileMenuView({ page }: { page: FilesPage }) {
  const { menu } = useFilesState(page)
  if (!menu) return null
  return (
    <div className="file-menu-backdrop" onClick={() => page.menu.close()} onContextMenu={event => { event.preventDefault(); page.menu.close() }}>
      <div className="file-menu" role="menu" style={{ left: menu.x, top: menu.y }} onClick={event => event.stopPropagation()}>
        {menu.isConfirmingDelete ? <DeleteConfirmationView page={page} /> : <FileMenuChoicesView page={page} path={menu.path} />}
      </div>
    </div>
  )
}

function FileMenuChoicesView({ page, path }: { page: FilesPage; path: string }) {
  return (
    <>
      <button role="menuitem" title={`${path}: goes with your next prompt in the chat that opened this page`} onClick={() => void page.menu.addToContext()}>
        Add to context
      </button>
      <button role="menuitem" title={path} onClick={() => void page.menu.reveal()}>
        {revealLabelOf(navigator.platform)}
      </button>
      <button role="menuitem" title={`${path}: run the graph rules of each fidelity the session shows that declares it`} onClick={() => void page.menu.validate()}>
        Validate
      </button>
      <button role="menuitem" title={`${path}: the rules the latest reports find broken in it`} onClick={() => void page.menu.showViolations()}>
        Display violations
      </button>
      <PracticeSubmenuView page={page} path={path} />
      <button role="menuitem" className="file-menu-delete" title={`${path}: asks first, since it cannot be undone`} onClick={() => page.menu.askToDelete()}>
        Delete…
      </button>
    </>
  )
}

// Add to practice ▸: the session's practices, opening beside the menu while the pointer is on it.
function PracticeSubmenuView({ page, path }: { page: FilesPage; path: string }) {
  const { practices } = useFilesState(page)
  if (!practices.length) return null
  return (
    <div className="file-submenu-holder" role="none">
      <button role="menuitem" aria-haspopup="menu" title={`${path}: a root of every fidelity of the practice chosen`}>
        Add to practice <span className="file-submenu-mark">▸</span>
      </button>
      <div className="file-menu file-submenu" role="menu" aria-label="Add to practice">
        {practices.map(practice => (
          <button key={practice.name} role="menuitem" style={{ borderLeftColor: practice.colour }} onClick={() => void page.menu.addToPractice(practice)}>
            {practice.short_name}
          </button>
        ))}
      </div>
    </div>
  )
}

// Delete asks first, saying it cannot be undone.
function DeleteConfirmationView({ page }: { page: FilesPage }) {
  return (
    <div className="file-menu-confirm" role="alertdialog" aria-label="Confirm delete">
      <p>{page.menu.confirmation}</p>
      <button className="file-menu-delete" onClick={() => void page.menu.confirmDelete()}>
        Delete
      </button>
      <button onClick={() => page.menu.close()}>Cancel</button>
    </div>
  )
}

// The rules the latest reports find broken in the file or folder the file menu displayed the violations of: each
// violation opens its file at its line.
function ViolationsPanelView({ page }: { page: FilesPage }) {
  const { violations } = useFilesState(page)
  if (!violations) return null
  return (
    <section className="violations-panel" aria-label={`Violations of ${violations.path}`}>
      <header>
        <span>Violations of {violations.path}</span>
        <button type="button" title="Close" onClick={() => page.closeViolations()}>
          ✕
        </button>
      </header>
      {page.violationsNote ? <p className="files-note">{page.violationsNote}</p> : null}
      {violations.report.rules.map(rule => (
        <div key={`${rule.fidelity.slug}-${rule.rule.slug}`} className="violations-rule">
          <h4>
            {rule.rule.slug} <span className="files-note">{rule.fidelity.slug}</span>
          </h4>
          <ul>
            {rule.violations.map(violation => (
              <li key={`${violation.location}:${violation.line}:${violation.message}`}>
                <button type="button" onClick={() => void page.openViolation(violation)}>
                  {violation.location}
                  {violation.line ? `:${violation.line}` : ''} — {violation.message}
                </button>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </section>
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

// The ways the file bar shows its files, each with its button's label and what the button says on hover.
const FILE_BAR_VIEWS = [
  { view: 'list', label: 'List', title: 'Show the files as a list' },
  { view: 'folders', label: 'Folders', title: 'Show the files in their folders' },
  { view: 'graph', label: 'Graph', title: "Show the session's graph of these files" },
] as const

// The file bar's buttons: collapse or expand it, and show its files as a list, in their folders, or as the graph.
function FileBarButtonsView({ page }: { page: FilesPage }) {
  const { fileBar } = useFilesState(page)
  return (
    <div className="file-bar-buttons" role="toolbar" aria-label="File bar">
      <button aria-label={fileBar.isOpen ? 'Collapse the file bar' : 'Expand the file bar'} title={fileBar.isOpen ? 'Collapse the file bar' : 'Expand the file bar'} onClick={() => page.fileBar.toggle()}>
        {fileBar.isOpen ? '«' : '»'}
      </button>
      {fileBar.isOpen
        ? FILE_BAR_VIEWS.map(({ view, label, title }) => (
          <button key={view} className="file-bar-view" aria-pressed={fileBar.view === view} title={title} onClick={() => page.fileBar.show(view)}>
            {label}
          </button>
        ))
        : null}
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
          onClick={() => void page.guidance.toggle('practice', practice.key)}
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
      <iframe className="drawio-frame" title={`${path} in the draw.io editor`} src={drawioPageOf(path, page.link)} />
    </section>
  )
}

// A whiteboard file is only a pointer to its board in Claude: the file view says where the board is and opens it, and
// draws nothing from the file.
function WhiteboardPointerView({ page, path }: { page: FilesPage; path: string }) {
  const entry = page.fileBar.entries.find(each => each.path === path)
  const published = entry ? publishedOf(entry) : null
  return (
    <section className="open-file" aria-label={path}>
      <div className="comment-toolbar">
        <span className="source-path">{path}</span>
        {entry && published?.link ? <BoardLinkView page={page} entry={entry} published={published} /> : null}
      </div>
      <p className="files-note">{published?.link ? 'This whiteboard is its board in Claude: open it with ↗.' : 'This whiteboard is not on a board in Claude yet.'}</p>
    </section>
  )
}

function OpenFileView({ page }: { page: FilesPage }) {
  const state = useFilesState(page)
  const path = state.file?.path ?? ''
  // The open file's selected lines, added to the chat's context; made once per file, so the editor keeps its action.
  const addLines = useCallback((lines: { start: number; end: number }) => void page.chatContext.add(path, lines), [page, path])
  // Go to file on a fold-out, or a press on a link, opens what it shows: a link's file beside this one, anything else in
  // its own file; made once, so the open fold-outs stay as they are.
  const goToFile = useCallback((foldOut: SourceCallout) => void page.goTo(foldOut), [page])
  if (!state.openPath) return <p className="files-note">Choose a file.</p>
  if (isDrawio(state.openPath)) return <DrawioFileView page={page} path={state.openPath} />
  if (isWhiteboard(state.openPath)) return <WhiteboardPointerView page={page} path={state.openPath} />
  if (!state.file) return <p className="files-note">Opening {state.openPath}…</p>
  const isOneOfSeveral = state.moreFiles.length > 0
  return (
    <section className="open-file" aria-label={state.file.path}>
      <CommentToolbarView page={page} file={state.file} />
      {isOneOfSeveral ? <OpenFilesBarView page={page} /> : null}
      {isOneOfSeveral ? <OpenFileHeadView page={page} path={state.file.path} /> : null}
      {page.openFiles.isCollapsed(state.file.path) ? null : (
        <FileView key={state.file.path} file={state.file} callouts={page.callouts} frames={page.frames} actions={page.comments} onAddToContext={addLines} openAround={page.linesShownIn(state.file.path)} anchor={state.openAnchor} onGoToFile={goToFile} members={state.graph.members} keys={page.foldKeys} fail={wrapFailed(page)} />
      )}
      {state.moreFiles.map(file => (
        <MoreFileView key={file.path} page={page} file={file} />
      ))}
    </section>
  )
}

// The open file alone, or, once a link was followed from it, the open file and the file the link opened beside it, each
// in a pane of its own that scrolls, takes comments and closes apart from the other. There are never more than two: the
// next link followed, from either pane, opens its file in the right pane in place of the one there.
function FilePanesView({ page }: { page: FilesPage }) {
  const { linked, openPath } = useFilesState(page)
  if (!linked) return <OpenFileView page={page} />
  return (
    <div className="file-panes">
      <div className={SCROLLING_PANE} aria-label="Open file">
        <PaneHeadView path={openPath} title={`Close ${openPath}, leaving ${linked.path} open`} onClose={() => page.closeOpen()} />
        <OpenFileView page={page} />
      </div>
      <div className={SCROLLING_PANE} aria-label="Linked file">
        <PaneHeadView path={linked.path} title={`Close ${linked.path}`} onClose={() => page.closeLinked()} />
        <LinkedFileView page={page} />
      </div>
    </div>
  )
}

// A pane's file and the button that closes it.
function PaneHeadView({ path, title, onClose }: { path: string; title: string; onClose: () => void }) {
  return (
    <div className="file-pane-head">
      <span className="source-path">{path}</span>
      <button type="button" className="file-pane-close" aria-label={title} title={title} onClick={onClose}>
        ×
      </button>
    </div>
  )
}

// The file a link opened, at the heading the link named: rendered and scrolled to it, or, for a file with no rendered
// form, in the source view at the section's lines.
function LinkedFileView({ page }: { page: FilesPage }) {
  const { linked, graph } = useFilesState(page)
  const path = linked?.path ?? ''
  const addLines = useCallback((lines: { start: number; end: number }) => void page.chatContext.add(path, lines), [page, path])
  const goToFile = useCallback((foldOut: SourceCallout) => void page.goTo(foldOut), [page])
  if (!linked) return null
  if (!linked.file) return <p className="files-note">Opening {linked.path}…</p>
  const openAround = linked.file.rendered_form ? [] : linked.lines
  return (
    <section className="open-file linked-file" aria-label={linked.path}>
      <CommentToolbarView page={page} file={linked.file} />
      <FileView key={`${linked.path}#${linked.anchor}`} file={linked.file} callouts={page.callouts} frames={page.frames} actions={page.linkedComments} onAddToContext={addLines} openAround={openAround} anchor={linked.anchor} onGoToFile={goToFile} members={graph.members} keys={page.foldKeys} fail={wrapFailed(page)} />
    </section>
  )
}

// Above several open files: collapse every one to its name, or expand every one.
function OpenFilesBarView({ page }: { page: FilesPage }) {
  return (
    <div className="open-files-bar" role="toolbar" aria-label="Open files">
      <button type="button" title="Collapse every open file to its name" onClick={() => page.openFiles.collapseAll()}>
        Collapse all
      </button>
      <button type="button" title="Show every open file whole" onClick={() => page.openFiles.expandAll()}>
        Expand all
      </button>
    </div>
  )
}

// An open file's name, which collapses the file to it and expands it again.
function OpenFileHeadView({ page, path }: { page: FilesPage; path: string }) {
  const isCollapsed = page.openFiles.isCollapsed(path)
  return (
    <button type="button" className="open-file-head" aria-expanded={!isCollapsed} title={isCollapsed ? `Show ${path}` : `Collapse ${path} to its name`} onClick={() => page.openFiles.toggle(path)}>
      <span className="open-file-mark">{isCollapsed ? '▸' : '▾'}</span> {path}
    </button>
  )
}

// A file open beside the first, holding a node selected in the graph view.
function MoreFileView({ page, file }: { page: FilesPage; file: SessionFileData }) {
  const addLines = useCallback((lines: { start: number; end: number }) => void page.chatContext.add(file.path, lines), [page, file.path])
  const goToFile = useCallback((foldOut: SourceCallout) => void page.goTo(foldOut), [page])
  return (
    <section className="open-file more-file" aria-label={file.path}>
      <OpenFileHeadView page={page} path={file.path} />
      {page.openFiles.isCollapsed(file.path) ? null : (
        <FileView file={file} callouts={page.callouts} frames={page.frames} actions={page.comments} onAddToContext={addLines} openAround={page.linesShownIn(file.path)} onGoToFile={goToFile} members={page.state.graph.members} keys={page.foldKeys} fail={wrapFailed(page)} />
      )}
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
const STAGE_ICONS: Record<string, string> = { Discovery: '⌕', Specification: '▤', Implementation: '⚙', Hardening: '⛨' }

// A button for each stage, before the practices, as the chat bar's stage buttons: filled orange while selected. A press
// selects the stage beside those selected, or no longer, here and on the chat bar.
// Which files the page lists, first of the filters along the top and orange while selected, as the stages are: every
// file under the session's root, or the ones this session's branch changed, with how many.
function ScopeTogglesView({ page }: { page: FilesPage }) {
  const { scope } = useFilesState(page)
  return (
    <div className="scope-toggles" role="group" aria-label="Files listed">
      <button type="button" className={`scope-toggle ${scope === 'everything' ? 'is-shown' : ''}`} aria-pressed={scope === 'everything'} aria-label="All files" title="All files: every file and folder in the session's folders, whatever the stages, practices and formats selected" onClick={() => page.showScope('everything')}>
        All files
      </button>
      <button type="button" className={`scope-toggle ${scope === 'all' ? 'is-shown' : ''}`} aria-pressed={scope === 'all'} aria-label="All session files" title="All session files: every file of the stages, practices and formats selected, older work included" onClick={() => page.showScope('all')}>
        ▤
      </button>
      <button type="button" className={`scope-toggle ${scope === 'session' ? 'is-shown' : ''}`} aria-pressed={scope === 'session'} aria-label="This session" title={`This session: the ${page.fileBar.sessionWorkCount} files of this session's own work (those its branch changed, or in a folder with no git, those its fidelities declare), among those its stages, practices and formats select`} onClick={() => page.showScope('session')}>
        Δ<sup className="scope-count">{page.fileBar.sessionWorkCount}</sup>
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
          onClick={() => void page.guidance.toggle('stage', stage.name)}
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
          onClick={() => void page.guidance.toggle('format', format.label)}
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

// The look this browser keeps, and the press that switches it and stores the switch; a look that cannot be read or
// kept is told as a notice.
function useTheme(page: FilesPage): [FilesTheme, () => void] {
  const failed = (failure: string) => page.notices.fail(failure, "Changing the Files app's look")
  const [theme, setTheme] = useState<FilesTheme>(() => storedTheme(failed))
  const toggle = () => {
    const next = theme === 'engineering' ? 'light' : 'engineering'
    applyTheme(next, failed)
    setTheme(next)
  }
  return [theme, toggle]
}

// Dark engineering by default; a press turns the light look on or off.
function ThemeToggleView({ page }: { page: FilesPage }) {
  const [theme, toggle] = useTheme(page)
  return (
    <button type="button" className="theme-toggle" aria-pressed={theme === 'light'} title={theme === 'engineering' ? 'Light look' : 'Dark engineering look'} onClick={toggle}>
      {theme === 'engineering' ? '☀' : '◐'}
    </button>
  )
}

// The page's head: what it shows, then the toggles that choose which files show and how the page looks.
function FilesHeadView({ page }: { page: FilesPage }) {
  return (
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
  )
}

// The Files app's page: the files its link names down the side, the open one beside them, and what went wrong.
export function FilesPageView({ page }: { page: FilesPage }) {
  const { problem, fileBar } = useFilesState(page)
  useEffect(() => page.start(), [page])
  return (
    <main className="files-page">
      <FilesHeadView page={page} />
      {problem ? <div className="files-problem" role="alert">{problem}</div> : null}
      <FailureBandView page={page} />
      <ViolationsPanelView page={page} />
      <FormatAlignmentView page={page} />
      <div className={`files-body ${fileBar.isOpen ? '' : 'is-bar-collapsed'}`} style={fileBar.isOpen ? { gridTemplateColumns: `${fileBar.width}px auto 1fr` } : undefined}>
        <nav className="files-side">
          <FileBarButtonsView page={page} />
          {fileBar.isOpen ? <FileListView page={page} /> : null}
        </nav>
        {fileBar.isOpen ? <FileBarDividerView page={page} /> : null}
        <FilePanesView page={page} />
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
