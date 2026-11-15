import type { FileEntryData, GuidanceSelectionData, SessionFileData } from '@cdd/space/session/session'

// One fidelity's files as the link names them, kept by fidelity so a practice turned off hides its own, with the format
// each file is in, so a format chip turned on shows only its own.
export type FidelityFiles = { slug: string; entries: FileEntryData[]; formatOf?: Record<string, string> }

// What the page draws: the session's practices with their toggles, the files its link names, the one open, and what went wrong. The open file is the session's
// answer itself (text, comments, folds, violations, changes), never a copy kept beside it.
export type FilesState = {
  // The session's guidance selection as last drawn: its stages, practices and formats, the chat bar's buttons' too.
  guidance: GuidanceSelectionData | null
  // Where the files are, as the header shows it: the repository, the branch, and the session's root.
  place: string
  // What the open file is read with: its own rules, read on its own, and the rules across the whole working copy. Both
  // off by default, so browsing never reads a graph.
  reads: { rules: boolean; crossFile: boolean }
  byFidelity: FidelityFiles[]
  entries: FileEntryData[]
  isListing: boolean
  openPath: string
  file: SessionFileData | null
  problem: string
  toasts: string[]
  fileBar: { isOpen: boolean; view: 'list' | 'folders'; openFolders: string[]; isChangedOnly: boolean }
}

export const NO_FILES: FilesState = {
  guidance: null,
  place: '',
  reads: { rules: false, crossFile: false },
  byFidelity: [],
  entries: [],
  isListing: true,
  openPath: '',
  file: null,
  problem: '',
  toasts: [],
  fileBar: { isOpen: true, view: 'list', openFolders: [], isChangedOnly: false },
}

// A change to the state, applied by the store that holds it.
export type FilesChange = (state: FilesState) => Partial<FilesState>

// The one place the page's state is held and changed; a view subscribes and reads it whole.
export class FilesStore {
  private current: FilesState = NO_FILES
  private readonly listeners = new Set<() => void>()

  get state(): FilesState {
    return this.current
  }

  change(change: FilesChange): void {
    this.current = { ...this.current, ...change(this.current) }
    for (const listener of this.listeners) listener()
  }

  subscribe = (listener: () => void): (() => void) => {
    this.listeners.add(listener)
    return () => {
      this.listeners.delete(listener)
    }
  }
}
