import type { FileEntryData } from '@cdd/space/session/session'

import type { FilesStore } from './files-state'

// The file bar's two ways of showing the files the page lists: one list, or the folders the files are in.
export type FileBarView = 'list' | 'folders'

// One folder of the files the page lists: its path as the session names it, none for a file at the top; its name, the
// path below the folder every listed file shares; and the files directly in it, in the order the link names them.
export type FileFolder = { path: string; name: string; files: FileEntryData[] }

const folderOf = (path: string): string => path.split('/').slice(0, -1).join('/')

// The folder every one of these folders is in: a session working outside the project names its files from the root of
// the disk, and a name that long is cut off in the bar.
const sharedRootLength = (paths: string[]): number => {
  const [first = [], ...rest] = paths.map(path => path.split('/'))
  const length = first.findIndex((segment, index) => rest.some(segments => segments[index] !== segment))
  return length === -1 ? first.length : length
}

// The folders the files are in, each once, in the order their first file is listed. A folder that holds only another
// folder has no files of its own, so it shows as part of that folder's path.
export const foldersOf = (entries: FileEntryData[]): FileFolder[] => {
  const folders = new Map<string, FileEntryData[]>()
  for (const entry of entries) folders.set(folderOf(entry.path), [...(folders.get(folderOf(entry.path)) ?? []), entry])
  const shared = folders.size > 1 ? sharedRootLength([...folders.keys()]) : 0
  return [...folders].map(([path, files]) => ({ path, name: path.split('/').slice(shared).join('/') || path, files }))
}

// The side bar of the Files app: collapsed to its buttons or expanded, showing the files as a list or in their
// folders. What it shows is held in the page's store, so the view redraws with it; the files are the page's own.
export class FileBar {
  constructor(private readonly store: FilesStore) {}

  // The folders of the files the page lists now, a practice turned off hiding its own.
  get folders(): FileFolder[] {
    return foldersOf(this.store.state.entries)
  }

  isOpen(folder: FileFolder): boolean {
    return this.store.state.fileBar.openFolders.includes(folder.path)
  }

  toggle(): void {
    this.store.change(({ fileBar }) => ({ fileBar: { ...fileBar, isOpen: !fileBar.isOpen } }))
  }

  // Shown as folders, the open file's folder opens, so the person still sees where they are.
  show(view: FileBarView): void {
    this.store.change(({ fileBar, openPath }) => {
      const openFolders = view === 'folders' && openPath ? [...new Set([...fileBar.openFolders, folderOf(openPath)])] : fileBar.openFolders
      return { fileBar: { ...fileBar, view, openFolders } }
    })
  }

  toggleFolder(path: string): void {
    this.store.change(({ fileBar }) => {
      const isOpen = fileBar.openFolders.includes(path)
      return { fileBar: { ...fileBar, openFolders: isOpen ? fileBar.openFolders.filter(each => each !== path) : [...fileBar.openFolders, path] } }
    })
  }
}
