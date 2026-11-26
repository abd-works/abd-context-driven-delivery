import type { FilterChoicesData, NodeSourceData } from '@cdd/harness/graph/graph'
import { NO_CHOICES, NO_FILTER, type FilterSelection } from '@graph-app/filter/filter-selection'
import type { ExplorerEntryData, FileEntryData, GuidanceSelectionData, RangeData, SessionFileData } from '@cdd/space/session/session'

import type { ShownFailure } from './failure-fixes'

// One fidelity's files as the session answers them, each saying whether the page lists it.
export type FidelityFiles = { slug: string; entries: FileEntryData[] }

// A node a person selected in the graph view, with the lines it covers in its file, which open and unfold there.
export type SelectedNode = { nodeId: string; lines: RangeData }

// The file a link opened beside the open file: its path, the heading anchor the link names, none for the whole file,
// the lines of that section, which a file with no rendered form shows in its source view, and the file as the session
// answers it, none until read.
export type LinkedFileState = { path: string; anchor: string; lines: { start: number; end: number }[]; file: SessionFileData | null }

// The graph view of the file bar: the practice trees of the session's graph holding only the nodes of the files the bar
// lists, read for those files (readFor names them), the branches a person opened and the entries read below them, the
// nodes selected, every class, operation and property the graph holds, which the open file opens its calls in place from
// even in another file, the cdd server's progress reports while a read is under way, and whether it failed. Its node
// filter is the Graph app's, a filter other than the file list that applies with it: it narrows the nodes of the files
// listed, with the node types, connectors and rules Python's Filter offers for it (choices).
export type FilesGraphState = {
  trees: ExplorerEntryData[] | null
  readFor: string
  filter: FilterSelection
  choices: FilterChoicesData
  branches: Record<string, ExplorerEntryData>
  openNodes: string[]
  selected: SelectedNode[]
  members: NodeSourceData[]
  log: string[]
  isReading: boolean
  problem: string
}

export const NO_GRAPH: FilesGraphState = { trees: null, readFor: '', filter: NO_FILTER, choices: NO_CHOICES, branches: {}, openNodes: [], selected: [], members: [], log: [], isReading: false, problem: '' }

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
  // What a change of the selection is filtering the files by while the session answers and the list is read again,
  // such as markdown; empty while nothing is being filtered.
  filtering: string
  openPath: string
  file: SessionFileData | null
  // The heading the open file is shown at: the one a link named when the file it opened beside became the open file.
  openAnchor: string
  // The file a link followed from either file opened beside the open file; at most one, so the next link replaces it.
  linked: LinkedFileState | null
  // The other files open beside the first, each holding a node selected in the graph view; none outside it.
  moreFiles: SessionFileData[]
  // The open files a person collapsed to their names; every other open file shows whole.
  collapsedFiles: string[]
  graph: FilesGraphState
  problem: string
  // Every failure the page met and still shows, each with its Fix button, until a person dismisses it.
  failures: ShownFailure[]
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
  filtering: '',
  openPath: '',
  file: null,
  openAnchor: '',
  linked: null,
  moreFiles: [],
  collapsedFiles: [],
  graph: NO_GRAPH,
  problem: '',
  failures: [],
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
