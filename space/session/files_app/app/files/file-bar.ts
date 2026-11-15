import type { FileEntryData } from '@cdd/space/session/session'

import type { FilesStore } from './files-state'

// The file bar's two ways of showing the files the page lists: one list, or the folder tree they are in.
export type FileBarView = 'list' | 'folders'

// One folder of the tree, as Windows Explorer shows it: its path as the session names it, none for the top of the tree;
// its name, the folders it holds that hold nothing else joined to it (`src/checkout`); the folders in it; and the files
// directly in it, folders first, each sorted by name.
export type FileFolder = { path: string; name: string; folders: FileFolder[]; files: FileEntryData[] }

const folderOf = (path: string): string => path.split('/').slice(0, -1).join('/')
const nameOf = (path: string): string => path.split('/').pop() ?? path
const byName = (one: string, other: string): number => one.localeCompare(other, undefined, { sensitivity: 'base', numeric: true })

const emptyFolder = (path: string): FileFolder => ({ path, name: nameOf(path), folders: [], files: [] })

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
  for (const entry of entries) folderAt(top, folderOf(entry.path)).files.push(entry)
  return { ...top, folders: top.folders.map(compacted).sort((one, other) => byName(one.name, other.name)), files: [...top.files].sort((one, other) => byName(nameOf(one.path), nameOf(other.path))) }
}

// The folders on the way down to the file at path, the folder it is in last.
const foldersAbove = (tree: FileFolder, path: string): string[] =>
  tree.folders.filter(folder => path.startsWith(`${folder.path}/`)).flatMap(folder => [folder.path, ...foldersAbove(folder, path)])

// The side bar of the Files app: collapsed to its buttons or expanded, showing the files as a list or in their folder
// tree. What it shows is held in the page's store, so the view redraws with it; the files are the page's own.
export class FileBar {
  constructor(private readonly store: FilesStore) {}

  // The files the bar lists: every file the page lists, a practice turned off hiding its own; or, changed only, the
  // ones the session's branch changed, the ticket's own work, and a design canvas, which opens at its link.
  get entries(): FileEntryData[] {
    const { entries, fileBar } = this.store.state
    return fileBar.isChangedOnly ? entries.filter(entry => entry.is_changed || entry.link) : entries
  }

  // How many of the listed files the session's branch changed, for the changed-only button.
  get changedCount(): number {
    return this.store.state.entries.filter(entry => entry.is_changed).length
  }

  // The folder tree of the files the bar lists.
  get tree(): FileFolder {
    return treeOf(this.entries)
  }

  isOpen(folder: FileFolder): boolean {
    return this.store.state.fileBar.openFolders.includes(folder.path)
  }

  toggle(): void {
    this.store.change(({ fileBar }) => ({ fileBar: { ...fileBar, isOpen: !fileBar.isOpen } }))
  }

  // Shown as folders, every folder down to the open file opens, so the person still sees where they are.
  show(view: FileBarView): void {
    this.store.change(({ fileBar, openPath }) => {
      const above = view === 'folders' && openPath ? foldersAbove(this.tree, openPath) : []
      return { fileBar: { ...fileBar, view, openFolders: [...new Set([...fileBar.openFolders, ...above])] } }
    })
  }

  // Lists only the files the session's branch changed, or every file again.
  toggleChangedOnly(): void {
    this.store.change(({ fileBar }) => ({ fileBar: { ...fileBar, isChangedOnly: !fileBar.isChangedOnly } }))
  }

  toggleFolder(path: string): void {
    this.store.change(({ fileBar }) => {
      const isOpen = fileBar.openFolders.includes(path)
      return { fileBar: { ...fileBar, openFolders: isOpen ? fileBar.openFolders.filter(each => each !== path) : [...fileBar.openFolders, path] } }
    })
  }
}
