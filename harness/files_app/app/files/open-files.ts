import type { FilesStore } from './files-state'

// The files open in the source view, the first and each other one below it, such as the files of the nodes selected in
// the graph view: each collapses to its name and expands again on its own, and all of them at once. Keeps which are
// collapsed in the page's store (`collapsedFiles`), so a file read again stays as the person left it.
export class OpenFiles {
  constructor(private readonly store: FilesStore) {}

  // The path of every file open, the first first.
  get paths(): string[] {
    const { openPath, moreFiles } = this.store.state
    return [openPath, ...moreFiles.map(file => file.path)].filter(Boolean)
  }

  isCollapsed(path: string): boolean {
    return this.store.state.collapsedFiles.includes(path)
  }

  toggle(path: string): void {
    this.store.change(({ collapsedFiles }) => ({ collapsedFiles: collapsedFiles.includes(path) ? collapsedFiles.filter(held => held !== path) : [...collapsedFiles, path] }))
  }

  collapseAll(): void {
    this.store.change(() => ({ collapsedFiles: this.paths }))
  }

  expandAll(): void {
    this.store.change(() => ({ collapsedFiles: [] }))
  }
}
