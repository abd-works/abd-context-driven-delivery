import type { CddApi, CddProgress } from '@cdd/cdd-shared'
import type { ExplorerEntryData, SessionClientGenerated } from '@cdd/space/session/session'
import { NO_CHOICES, chosen, nodeFilter, type FilterSelection } from '@graph-app/filter/filter-selection'

import type { FileBar } from './file-bar'
import type { FilesNotices } from './files-notices'
import type { FilesStore, SelectedNode } from './files-state'

const reasonOf = (failure: unknown): string => (failure instanceof Error ? failure.message : String(failure))

// How often a read under way asks the cdd server what it is doing, in milliseconds.
const PROGRESS_EVERY = 400
const pause = (milliseconds: number) => new Promise(resolve => setTimeout(resolve, milliseconds))

// An entry below another is a node's entry; the rules a node lists sit beside them and show with the violations.
export const isEntry = (child: unknown): child is ExplorerEntryData => typeof child === 'object' && child !== null && 'children_left_out' in child

// The graph view of the Files app's file bar: the session's graph holding only the nodes of the files the bar lists, so
// it is filtered as the file list is, read again whenever the bar lists other files, showing the cdd server's progress
// while it reads. Its node filter, the Graph app's, is a filter other than the file list that applies with it: it
// narrows the nodes of the files listed and never widens the list, and a change of either reads the graph again with
// both. Selecting a node opens its file at its lines, or each file below it when it is a folder; selecting more
// opens each of their files. Everything it shows is the session's answer, held in the store.
export class FilesGraph {
  constructor(
    private readonly store: FilesStore,
    private readonly session: SessionClientGenerated,
    private readonly api: CddApi,
    private readonly fileBar: FileBar,
    private readonly notices: FilesNotices,
    private readonly showNodes: (selected: SelectedNode[]) => Promise<void>,
  ) {}

  // The files the graph is read for: those the bar lists that are there to read.
  get paths(): string[] {
    return this.fileBar.entries.filter(entry => entry.exists).map(entry => entry.path)
  }

  // The node filter as the session's graph takes it, for the selection the person made.
  get nodeFilter(): Record<string, unknown> {
    return nodeFilter(this.store.state.graph.filter)
  }

  // What the graph is read for: the files listed and the node filter, so a change of either reads it again.
  private get readKey(): string {
    return `${this.paths.join('\n')}\n${JSON.stringify(this.nodeFilter)}`
  }

  // Reads the graph whenever the bar shows it for files or a node filter it was not read for, such as a practice turned
  // off, the Changed button pressed or operations chosen. Answers what stops it.
  follow(): () => void {
    const readWhenStale = () => {
      const { fileBar, graph } = this.store.state
      if (fileBar.view === 'graph' && !graph.isReading && graph.readFor !== this.readKey) void this.read()
    }
    readWhenStale()
    return this.store.subscribe(readWhenStale)
  }

  // Reads the trees, then every member the graph holds and the node filter's choices for what it holds, following the cdd server's progress until the trees arrive.
  async read(): Promise<void> {
    const paths = this.paths
    const readFor = this.readKey
    this.store.change(({ graph }) => ({ graph: { ...graph, readFor, isReading: true, log: [], problem: '' } }))
    void this.followProgress(readFor)
    try {
      const trees = (await this.session.graphTrees(paths, this.nodeFilter)) ?? []
      this.store.change(({ graph }) => (graph.readFor === readFor ? { graph: { ...graph, trees, branches: {}, isReading: false } } : {}))
      const members = (await this.session.graphMembers()) ?? []
      this.store.change(({ graph }) => (graph.readFor === readFor ? { graph: { ...graph, members } } : {}))
      const { filter } = this.store.state.graph
      const choices = (await this.session.graphFilterChoices(filter.practices, filter.node_types)) ?? NO_CHOICES
      this.store.change(({ graph }) => (graph.readFor === readFor ? { graph: { ...graph, choices } } : {}))
    } catch (failure) {
      this.store.change(({ graph }) => ({ graph: { ...graph, isReading: false, problem: `The graph did not read: ${reasonOf(failure)}` } }))
      this.notices.fail(`The Files app did not read the session's graph: ${reasonOf(failure)}`, 'Showing the graph view, calling session.graph_trees')
    }
  }

  // Adds each new progress report to the log while the read for readFor is under way. A report that does not come is
  // left out: the read itself still answers or fails.
  private async followProgress(readFor: string): Promise<void> {
    const isUnderWay = () => this.store.state.graph.isReading && this.store.state.graph.readFor === readFor
    while (isUnderWay()) {
      const reports = await this.api.post<CddProgress[]>('/cdd/progress', {}).catch(() => null)
      const newest = reports?.at(-1)?.message
      if (newest && isUnderWay()) this.store.change(({ graph }) => (graph.log.at(-1) === newest ? {} : { graph: { ...graph, log: [...graph.log, newest] } }))
      await pause(PROGRESS_EVERY)
    }
  }

  // Filters the graph's nodes by next, the lists Python's Filter offers for it: a change of node types takes the
  // connectors and rules it offers for them, as the Graph app's filter does. The graph is read again with it.
  async filterTo(next: FilterSelection): Promise<void> {
    try {
      const isNewTypes = next.node_types.join('\n') !== this.store.state.graph.filter.node_types.join('\n')
      const choices = isNewTypes ? ((await this.session.graphFilterChoices(next.practices, next.node_types)) ?? NO_CHOICES) : this.store.state.graph.choices
      const filter = isNewTypes ? chosen(next, choices) : next
      this.store.change(({ graph }) => ({ graph: { ...graph, filter, choices } }))
    } catch (failure) {
      this.notices.fail(`The Files app did not filter the graph: ${reasonOf(failure)}`, 'Filtering the graph view, calling session.graph_filter_choices')
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
      const branch = await this.session.graphBranch(entry.node_id, this.paths, this.nodeFilter)
      if (branch) this.store.change(({ graph }) => ({ graph: { ...graph, branches: { ...graph.branches, [entry.node_id]: branch } } }))
    } catch (failure) {
      this.notices.fail(`The Files app did not open ${entry.name} in the graph: ${reasonOf(failure)}`, 'Opening a node in the graph view, calling session.graph_branch')
    }
  }

  // Selects the node, alone or, with also, beside those already selected, then opens each file it covers at its lines: a
  // member's own file, or every listed file below a folder such as a package. A node read from no lines of a file selects
  // nothing.
  async select(entry: ExplorerEntryData, also: boolean = false): Promise<void> {
    try {
      const ranges = (await this.session.graphNodeRanges(entry.node_id, this.paths)) ?? []
      if (!ranges.length) return
      const kept = also ? this.store.state.graph.selected.filter(selected => selected.nodeId !== entry.node_id) : []
      const selected = [...kept, ...ranges.map(lines => ({ nodeId: entry.node_id, lines }))]
      this.store.change(({ graph }) => ({ graph: { ...graph, selected } }))
      await this.showNodes(selected)
    } catch (failure) {
      this.notices.fail(`The Files app did not open ${entry.name}: ${reasonOf(failure)}`, 'Selecting a node in the graph view, calling session.graph_node_ranges')
    }
  }
}
