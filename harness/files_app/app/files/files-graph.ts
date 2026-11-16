import type { CddApi, CddProgress } from '@cdd/cdd-shared'
import type { NodeSourceData } from '@cdd/harness/graph/graph'
import type { ExplorerEntryData, RangeData, SessionClientGenerated } from '@cdd/space/session/session'

import type { FileBar } from './file-bar'
import type { FilesNotices } from './files-notices'
import type { FilesStore, SelectedNode } from './files-state'

const reasonOf = (failure: unknown): string => (failure instanceof Error ? failure.message : String(failure))

// How often a read under way asks the cdd server what it is doing, in milliseconds.
const PROGRESS_EVERY = 400
const pause = (milliseconds: number) => new Promise(resolve => setTimeout(resolve, milliseconds))

// The list a tool answered: none is an empty list, and anything else, such as the text or error a server lane answers
// for a call it cannot run, is that tool's failure, so the page shows it rather than drawing it as a list.
export function listAnswered<Item>(tool: string, answer: Item[] | null | undefined | unknown): Item[] {
  if (answer === null || answer === undefined) return []
  if (Array.isArray(answer)) return answer as Item[]
  const said = typeof answer === 'string' ? answer : ((answer as { error?: unknown }).error ?? JSON.stringify(answer))
  throw new Error(`${tool} answered no list: ${String(said)}`)
}

// An entry below another is a node's entry; the rules a node lists sit beside them and show with the violations.
export const isEntry = (child: unknown): child is ExplorerEntryData => typeof child === 'object' && child !== null && 'children_left_out' in child

// The graph view of the Files app's file bar: the session's graph holding only the nodes of the files the bar lists, so
// it is filtered as the file list is, read again whenever the bar lists other files, showing the cdd server's progress
// while it reads. Selecting a node opens its file at its lines, or each file below it when it is a folder; selecting more
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

  // Reads the trees, then every member the graph holds, following the cdd server's progress until the trees arrive. A
  // read that fails, or answers anything but a list, holds no tree and shows the failure in place of the graph.
  async read(): Promise<void> {
    const paths = this.paths
    const readFor = paths.join('\n')
    this.store.change(({ graph }) => ({ graph: { ...graph, readFor, isReading: true, log: [], problem: '' } }))
    void this.followProgress(readFor)
    try {
      const trees = listAnswered<ExplorerEntryData>('session.graph_trees', await this.session.graphTrees(paths))
      this.store.change(({ graph }) => (graph.readFor === readFor ? { graph: { ...graph, trees, branches: {}, isReading: false } } : {}))
    } catch (failure) {
      this.store.change(({ graph }) => ({ graph: { ...graph, trees: [], isReading: false, problem: `The graph did not read: ${reasonOf(failure)}` } }))
      this.notices.fail(`The Files app did not read the session's graph: ${reasonOf(failure)}`, 'Showing the graph view, calling session.graph_trees')
      return
    }
    try {
      const members = listAnswered<NodeSourceData>('session.graph_members', await this.session.graphMembers())
      this.store.change(({ graph }) => (graph.readFor === readFor ? { graph: { ...graph, members } } : {}))
    } catch (failure) {
      this.store.change(({ graph }) => ({ graph: { ...graph, members: [] } }))
      this.notices.fail(`The Files app did not read the graph's members: ${reasonOf(failure)}`, 'Showing the graph view, calling session.graph_members')
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

  // Selects the node, alone or, with also, beside those already selected, then opens each file it covers at its lines: a
  // member's own file, or every listed file below a folder such as a package. A node read from no lines of a file selects
  // nothing.
  async select(entry: ExplorerEntryData, also: boolean = false): Promise<void> {
    try {
      const ranges = listAnswered<RangeData>('session.graph_node_ranges', await this.session.graphNodeRanges(entry.node_id, this.paths))
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
