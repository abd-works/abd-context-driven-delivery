import type { FileEntryData, SessionFileData } from '@cdd/space/session/session'

// What the page draws: the files its link names, the one open, and what went wrong. The open file is the session's
// answer itself (text, comments, folds, violations, changes), never a copy kept beside it.
export type FilesState = {
  entries: FileEntryData[]
  isListing: boolean
  openPath: string
  file: SessionFileData | null
  problem: string
  toasts: string[]
}

export const NO_FILES: FilesState = { entries: [], isListing: true, openPath: '', file: null, problem: '', toasts: [] }

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
