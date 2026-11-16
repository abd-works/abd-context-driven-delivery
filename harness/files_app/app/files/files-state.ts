import type { ExplorerEntryData, FileEntryData, GuidanceSelectionData, RangeData, SessionFileData } from '@cdd/space/session/session'

// One fidelity's files as the link names them, kept by fidelity so a practice turned off hides its own, with the format
// each file is in, so a format chip turned on shows only its own.
export type FidelityFiles = { slug: string; entries: FileEntryData[]; formatOf?: Record<string, string> }

// A node a person selected in the graph view, with the lines it covers in its file, which open and unfold there.
export type SelectedNode = { nodeId: string; lines: RangeData }

// The graph view of the file bar: the practice trees of the session's graph holding only the nodes of the files the bar
// lists, read for those files (readFor names them), the branches a person opened and the entries read below them, the
// nodes selected, and whether a read is under way or failed.
export type FilesGraphState = {
  trees: ExplorerEntryData[] | null
  readFor: string
  branches: Record<string, ExplorerEntryData>
  openNodes: string[]
  selected: SelectedNode[]
  isReading: boolean
  problem: string
}

export const NO_GRAPH: FilesGraphState = { trees: null, readFor: '', branches: {}, openNodes: [], selected: [], isReading: false, problem: '' }

// What the page draws: the session's practices with their toggles, the files its link names, the one open, and what went wrong. The open file is the session's
// answer itself (text, comments, folds, violations, changes), never a copy kept beside it.
export type FilesState = {
  // The session's guidance selection as last drawn: its stages, practices and formats, the chat bar's buttons' too.
  guidance: GuidanceSelectionData | null
  // Where the files are, as the header shows it: the repository, the branch, and the session's root.
  place: string
  // What the page lists of the files its stages, practices and formats select: This session, those the session's
  // branch changed against main; or All session files, every one under the session's root, older work included.
  scope: 'session' | 'all'
  // Every file under the session's root, each with its format and the fidelities it belongs to; none until read.
  rootFiles: FileEntryData[] | null
  // What the open file is read with: its own rules, read on its own, and the rules across the whole working copy. Both
  // off by default, so browsing never reads a graph.
  reads: { rules: boolean; crossFile: boolean }
  byFidelity: FidelityFiles[]
  entries: FileEntryData[]
  isListing: boolean
  openPath: string
  file: SessionFileData | null
  // The other files open beside the first, each holding a node selected in the graph view; none outside it.
  moreFiles: SessionFileData[]
  graph: FilesGraphState
  problem: string
  toasts: string[]
  // The file or folder a person right-clicked and where, whose menu shows there; none while no menu shows.
  menu: { path: string; x: number; y: number } | null
  // The folders a person closed: every other folder is open, so a folder a filter change brings is open too. Its width
  // is what the person dragged it to, in pixels.
  fileBar: { isOpen: boolean; view: 'list' | 'folders' | 'graph'; closedFolders: string[]; width: number }
}

// How wide the file bar may be dragged, in pixels: narrow enough to give the open file the page, wide enough for deep
// folders, and where it starts.
export const FILE_BAR_WIDTH = { narrowest: 160, usual: 288, widest: 900 }

export const NO_FILES: FilesState = {
  guidance: null,
  place: '',
  scope: 'session',
  rootFiles: null,
  reads: { rules: false, crossFile: false },
  byFidelity: [],
  entries: [],
  isListing: true,
  openPath: '',
  file: null,
  moreFiles: [],
  graph: NO_GRAPH,
  problem: '',
  toasts: [],
  menu: null,
  fileBar: { isOpen: true, view: 'folders', closedFolders: [], width: FILE_BAR_WIDTH.usual },
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
