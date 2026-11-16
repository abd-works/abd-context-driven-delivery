import type { ExplorerEntryData, SessionClientGenerated } from '@cdd/space/session/session'

import type { FileBar } from './file-bar'
import type { FilesNotices } from './files-notices'
import type { FilesStore, SelectedNode } from './files-state'

const reasonOf = (failure: unknown): string => (failure instanceof Error ? failure.message : String(failure))

// An entry below another is a node's entry; the rules a node lists sit beside them and show with the violations.
export const isEntry = (child: unknown): child is ExplorerEntryData => typeof child === 'object' && child !== null && 'children_left_out' in child

// The graph view of the Files app's file bar: the session's graph holding only the nodes of the files the bar lists, so
// it is filtered as the file list is, read again whenever the bar lists other files. Selecting a node opens its file at
// its lines; selecting more opens each of their files. Everything it shows is the session's answer, held in the store.
export class FilesGraph {
  constructor(
    private readonly store: FilesStore,
    private readonly session: SessionClientGenerated,
    private readonly fileBar: FileBar,
    private readonly notices: FilesNotices,
    private readonly showNodes: (selected: SelectedNode[]) => Promise<void>,
  ) {}

  // The files the graph is read for: those the bar lists that are there to read.
  get paths(): string[] {
    return this.fileBar.entries.filter(entry => entry.exists).map(entry => entry.path)
  }

  // Reads the graph whenever the bar shows it for files it was not read for, such as a practice turned off or the
  // Changed button pressed. Answers what stops it.
  follow(): () => void {
    const readWhenStale = () => {
      const { fileBar, graph } = this.store.state
      if (fileBar.view === 'graph' && !graph.isReading && graph.readFor !== this.paths.join('\n')) void this.read()
    }
    readWhenStale()
    return this.store.subscribe(readWhenStale)
  }

  async read(): Promise<void> {
    const paths = this.paths
    const readFor = paths.join('\n')
    this.store.change(({ graph }) => ({ graph: { ...graph, readFor, isReading: true, problem: '' } }))
    try {
      const trees = (await this.session.graphTrees(paths)) ?? []
      this.store.change(({ graph }) => (graph.readFor === readFor ? { graph: { ...graph, trees, branches: {}, isReading: false } } : {}))
    } catch (failure) {
      this.store.change(({ graph }) => ({ graph: { ...graph, isReading: false, problem: `The graph did not read: ${reasonOf(failure)}` } }))
      this.notices.fail(`The Files app did not read the session's graph: ${reasonOf(failure)}`, 'Showing the graph view, calling session.graph_trees')
    }
  }

  // The entries below entry, as read with it or, once a person opened it, as its branch was read.
  childrenOf(entry: ExplorerEntryData): ExplorerEntryData[] {
    return (this.store.state.graph.branches[entry.node_id] ?? entry).children.filter(isEntry)
  }

  isOpen(entry: ExplorerEntryData): boolean {
    return this.store.state.graph.openNodes.includes(entry.node_id)
  }

  isSelected(entry: ExplorerEntryData): boolean {
    return this.store.state.graph.selected.some(selected => selected.nodeId === entry.node_id)
  }

  // Opens or closes an entry, reading the entries its answer left out the first time it opens.
  async toggle(entry: ExplorerEntryData): Promise<void> {
    const isOpen = this.isOpen(entry)
    this.store.change(({ graph }) => ({ graph: { ...graph, openNodes: isOpen ? graph.openNodes.filter(id => id !== entry.node_id) : [...graph.openNodes, entry.node_id] } }))
    if (isOpen || !entry.children_left_out || this.store.state.graph.branches[entry.node_id]) return
    try {
      const branch = await this.session.graphBranch(entry.node_id, this.paths)
      if (branch) this.store.change(({ graph }) => ({ graph: { ...graph, branches: { ...graph.branches, [entry.node_id]: branch } } }))
    } catch (failure) {
      this.notices.fail(`The Files app did not open ${entry.name} in the graph: ${reasonOf(failure)}`, 'Opening a node in the graph view, calling session.graph_branch')
    }
  }

  // Selects the node, alone or, with also, beside those already selected, then opens the file of each at its lines. A
  // node read from no lines of a file, such as a practice's root, selects nothing.
  async select(entry: ExplorerEntryData, also = false): Promise<void> {
    try {
      const lines = await this.session.graphNodeRange(entry.node_id)
      if (!lines) return
      const kept = also ? this.store.state.graph.selected.filter(selected => selected.nodeId !== entry.node_id) : []
      const selected = [...kept, { nodeId: entry.node_id, lines }]
      this.store.change(({ graph }) => ({ graph: { ...graph, selected } }))
      await this.showNodes(selected)
    } catch (failure) {
      this.notices.fail(`The Files app did not open ${entry.name}: ${reasonOf(failure)}`, 'Selecting a node in the graph view, calling session.graph_node_range')
    }
  }
}
