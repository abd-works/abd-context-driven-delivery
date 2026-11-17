import type { FileEntryData } from '@cdd/space/session/session'

import { FILE_BAR_WIDTH, type FilesStore } from './files-state'

// The file bar's ways of showing the files the page lists: one list, the folder tree they are in, or the practice trees
// of the session's graph holding only those files' nodes.
export type FileBarView = 'list' | 'folders' | 'graph'

// One folder of the tree, as Windows Explorer shows it: its path as the session names it, none for the top of the tree;
// its name, the folders it holds that hold nothing else joined to it (`src/checkout`); the folders in it; and the files
// directly in it, folders first, each sorted by name.
export type FileFolder = { path: string; name: string; folders: FileFolder[]; files: FileEntryData[] }

const folderOf = (path: string): string => path.split('/').slice(0, -1).join('/')
const nameOf = (path: string): string => path.split('/').pop() ?? path
const byName = (one: string, other: string): number => one.localeCompare(other, undefined, { sensitivity: 'base', numeric: true })

const emptyFolder = (path: string): FileFolder => ({ path, name: nameOf(path), folders: [], files: [] })

// A file that stands for something published in Claude, which pressing it opens instead of the file: a `.whiteboard`
// file its board, and a design canvas version's `canvas.json` its canvas. Named as the person knows it, kept in the folder
// it lives in, and at the link the session answers for it, none while it is not published yet.
export type PublishedFile = { kind: 'whiteboard' | 'design canvas'; name: string; folder: string; link: string }

const WHITEBOARD_SUFFIX = '.whiteboard'
// A design canvas version as the UX mockup writes it: `<design-canvas>/version-N/project/canvas.json`, its versions'
// links kept in `<design-canvas>/versions.json` (harness/design_canvas/versions.py).
const CANVAS_VERSION = /^(?:(.*)\/)?design-canvas\/([^/]+)\/project\/canvas\.json$/

export function publishedOf(entry: FileEntryData): PublishedFile | null {
  if (entry.path.endsWith(WHITEBOARD_SUFFIX)) return { kind: 'whiteboard', name: nameOf(entry.path).slice(0, -WHITEBOARD_SUFFIX.length), folder: folderOf(entry.path), link: entry.link }
  const canvas = CANVAS_VERSION.exec(entry.path)
  if (canvas) return { kind: 'design canvas', name: canvas[2] ?? '', folder: canvas[1] ? `${canvas[1]}/design-canvas` : 'design-canvas', link: entry.link }
  if (entry.link) return { kind: 'design canvas', name: nameOf(entry.path), folder: folderOf(entry.path), link: entry.link }
  return null
}

// The folder the tree lists a file in: a design canvas in its design-canvas folder, where its versions' links are kept.
const placeOf = (entry: FileEntryData): string => publishedOf(entry)?.folder ?? folderOf(entry.path)

function folderAt(top: FileFolder, path: string): FileFolder {
  let folder = top
  for (const segment of path.split('/').filter(Boolean)) {
    const inner = folder.path ? `${folder.path}/${segment}` : segment
    let next = folder.folders.find(each => each.path === inner)
    if (!next) folder.folders.push((next = emptyFolder(inner)))
    folder = next
  }
  return folder
}

// A folder holding only one folder and no files shows as one row with the two names joined, as Explorer's compact view.
function compacted(folder: FileFolder): FileFolder {
  let shown = folder
  while (shown.files.length === 0 && shown.folders.length === 1) {
    const [only] = shown.folders as [FileFolder]
    shown = { ...only, name: `${shown.name}/${only.name}` }
  }
  return {
    ...shown,
    folders: shown.folders.map(compacted).sort((one, other) => byName(one.name, other.name)),
    files: [...shown.files].sort((one, other) => byName(nameOf(one.path), nameOf(other.path))),
  }
}

// The tree of the folders the files are in. Its top holds no name: the folders under it are the tree's first rows.
export function treeOf(entries: FileEntryData[]): FileFolder {
  const top = emptyFolder('')
  for (const entry of entries) folderAt(top, placeOf(entry)).files.push(entry)
  return { ...top, folders: top.folders.map(compacted).sort((one, other) => byName(one.name, other.name)), files: [...top.files].sort((one, other) => byName(nameOf(one.path), nameOf(other.path))) }
}

// The folders on the way down to the file at path, the folder it is in last.
const foldersAbove = (tree: FileFolder, path: string): string[] =>
  tree.folders.filter(folder => path.startsWith(`${folder.path}/`)).flatMap(folder => [folder.path, ...foldersAbove(folder, path)])

// The side bar of the Files app: collapsed to its buttons or expanded, showing the files as a list or in their folder
// tree. What it shows is held in the page's store, so the view redraws with it; the files are the page's own.
// Where this browser keeps the width the person last dragged the file bar to.
const STORED_WIDTH = 'cdd-files-bar-width'

export class FileBar {
  constructor(private readonly store: FilesStore) {}

  // The files the bar lists: in This session, the ones the session's branch changed, its own work, and a design canvas,
  // which opens at its link; in All session files, every one.
  get entries(): FileEntryData[] {
    const { entries, scope } = this.store.state
    return scope === 'session' ? entries.filter(entry => entry.is_changed || entry.link) : entries
  }

  // How many files the session's branch changed among those the page lists, for the This session button.
  get changedCount(): number {
    return this.store.state.entries.filter(entry => entry.is_changed).length
  }

  // The folder tree of the files the bar lists.
  get tree(): FileFolder {
    return treeOf(this.entries)
  }

  isOpen(folder: FileFolder): boolean {
    return !this.store.state.fileBar.closedFolders.includes(folder.path)
  }

  toggle(): void {
    this.store.change(({ fileBar }) => ({ fileBar: { ...fileBar, isOpen: !fileBar.isOpen } }))
  }

  // Shown as folders, every folder down to the open file opens, so the person still sees where they are.
  show(view: FileBarView): void {
    this.store.change(({ fileBar, openPath }) => {
      const above = view === 'folders' && openPath ? foldersAbove(this.tree, openPath) : []
      return { fileBar: { ...fileBar, view, closedFolders: fileBar.closedFolders.filter(path => !above.includes(path)) } }
    })
  }

  // The width the person dragged the bar to, kept between its narrowest and widest, and remembered in this browser so
  // the next page opens at it.
  resize(width: number): void {
    const kept = Math.round(Math.min(FILE_BAR_WIDTH.widest, Math.max(FILE_BAR_WIDTH.narrowest, width)))
    this.store.change(({ fileBar }) => ({ fileBar: { ...fileBar, width: kept } }))
    try {
      window.localStorage.setItem(STORED_WIDTH, String(kept))
    } catch (refusal) {
      // A browser that keeps nothing, such as a private window, refuses with a DOMException and opens the next page at
      // the usual width; anything else is a fault and is raised.
      if (!(refusal instanceof DOMException)) throw refusal
    }
  }

  // The width this browser remembered, when it remembered one; the usual width otherwise.
  restoreWidth(): void {
    let stored = NaN
    try {
      stored = Number(window.localStorage.getItem(STORED_WIDTH) ?? NaN)
    } catch (refusal) {
      // A browser that keeps nothing refuses with a DOMException, and the bar keeps the usual width.
      if (!(refusal instanceof DOMException)) throw refusal
      return
    }
    if (Number.isFinite(stored)) this.resize(stored)
  }

  toggleFolder(path: string): void {
    this.store.change(({ fileBar }) => {
      const isClosed = fileBar.closedFolders.includes(path)
      return { fileBar: { ...fileBar, closedFolders: isClosed ? fileBar.closedFolders.filter(each => each !== path) : [...fileBar.closedFolders, path] } }
    })
  }
}
