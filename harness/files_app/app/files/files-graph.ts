import type { CddApi, CddProgress } from '@cdd/cdd-shared'
import type { FilterData, GraphRuleData, GraphRulesCollectionData, NodeSourceData } from '@cdd/harness/graph/graph'
import type { ExplorerEntryData, RangeData, SessionClientGenerated } from '@cdd/space/session/session'
import { NO_CHOICES, chosen, nodeFilter, type FilterSelection } from '@graph-app/filter/filter-selection'

import type { FileBar } from './file-bar'
import type { FilesNotices } from './files-notices'
import type { FilesStore, SelectedNode } from './files-state'
import type { SourceCallout } from '@source-view/source-callouts'

const reasonOf = (failure: unknown): string => (failure instanceof Error ? failure.message : String(failure))

// Where this browser remembers whether the person opened the graph view's node filter.
const STORED_FILTERS_SHOWN = 'cdd-files-graph-filters-shown'

// How often a read under way asks the cdd server what it is doing, in milliseconds.
const PROGRESS_EVERY = 400
const pause = (milliseconds: number) => new Promise(resolve => setTimeout(resolve, milliseconds))

// The list a tool answered: none is an empty list, and anything else, such as the text or error a server lane answers
// for a call it cannot run, is that tool's failure, so the page shows it rather than drawing it as a list.
export function listAnswered<Item>(tool: string, answer: unknown): Item[] {
  if (answer === null || answer === undefined) return []
  if (Array.isArray(answer)) return answer as Item[]
  throw new Error(`${tool} answered no list: ${saidBy(answer)}`)
}

// The choices graph_filter_choices answered: none offers nothing, and anything without its lists of node types, those
// offered, connectors and rules is that tool's failure, so the node filter never draws a list it was not given.
export function choicesAnswered(answer: unknown): FilterData {
  if (answer === null || answer === undefined) return NO_CHOICES
  const lists = ['node_types', 'offered_node_types', 'relationships', 'rules'] as const
  if (typeof answer === 'object' && lists.every(list => Array.isArray((answer as Record<string, unknown>)[list]))) return answer as FilterData
  throw new Error(`session.graph_filter_choices answered no choices: ${saidBy(answer)}`)
}

const saidBy = (answer: unknown): string => {
  if (typeof answer === 'string') return answer
  const error = (answer as { error?: unknown } | null)?.error
  return error !== undefined ? String(error) : JSON.stringify(answer)
}

// An entry below another is a node's entry; the rules a node lists sit beside them and show with the violations.
// The lines a section fold-out names, in the file it names, as a range of that file.
const sectionRange = (foldOut: SourceCallout): RangeData => ({ path: foldOut.path, start_line: foldOut.startLine, end_line: foldOut.endLine, content: foldOut.text, anchor: '' }) as RangeData

// The kind of node a story's example is, which a scenario's steps use from where it is declared.
const EXAMPLE_TYPE = 'Example'

// A connector, such as a step's invokes or observes, is an entry named for its own kind: it holds the nodes it reaches.
const isConnector = (entry: ExplorerEntryData): boolean => entry.type === entry.name

export const isEntry = (child: unknown): child is ExplorerEntryData => typeof child === 'object' && child !== null && 'children_left_out' in child
// The group the graph sends first under every node, open or closed, holding the rules the node is judged by.
const isRulesGroup = (child: unknown): child is GraphRulesCollectionData => typeof child === 'object' && child !== null && (child as { type?: string }).type === 'rules'
// The lines a broken rule names: each place its violations point at.
const violationRange = (hit: GraphRuleData['violations'][number]): RangeData => ({ path: hit.location, start_line: hit.line ?? 1, end_line: hit.end_line ?? hit.line ?? 1, content: '', anchor: '' })

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
  private get nodeFilter(): Record<string, unknown> {
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
  // A read that fails, or answers anything other than what the tool returns, is shown and told; trees that arrived stay.
  async read(): Promise<void> {
    const paths = this.paths
    const readFor = this.readKey
    this.store.change(({ graph }) => ({ graph: { ...graph, readFor, isReading: true, log: [], problem: '' } }))
    void this.followProgress(readFor)
    try {
      const trees = listAnswered<ExplorerEntryData>('session.graph_trees', await this.session.graphTrees(paths, this.nodeFilter))
      this.store.change(({ graph }) => (graph.readFor === readFor ? { graph: { ...graph, trees, branches: {}, isReading: false } } : {}))
      await this.readOpenBranches(readFor)
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
    try {
      const { filter } = this.store.state.graph
      const choices = choicesAnswered(await this.session.graphFilterChoices(filter.practices, filter.node_types))
      this.store.change(({ graph }) => (graph.readFor === readFor ? { graph: { ...graph, choices } } : {}))
    } catch (failure) {
      this.store.change(({ graph }) => ({ graph: { ...graph, choices: NO_CHOICES } }))
      this.notices.fail(`The Files app did not read the graph's node filter: ${reasonOf(failure)}`, 'Showing the graph view, calling session.graph_filter_choices')
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
      const choices = isNewTypes ? choicesAnswered(await this.session.graphFilterChoices(next.practices, next.node_types)) : this.store.state.graph.choices
      const filter = isNewTypes ? chosen(next, choices) : next
      this.store.change(({ graph }) => ({ graph: { ...graph, filter, choices } }))
    } catch (failure) {
      this.notices.fail(`The Files app did not filter the graph: ${reasonOf(failure)}`, 'Filtering the graph view, calling session.graph_filter_choices')
    }
  }

  // Whether the node filter shows above the trees: closed until the person opens it, then as this browser remembers. A
  // browser that keeps nothing, such as a private window, refuses with a DOMException and the filter stays closed.
  get areFiltersShown(): boolean {
    try {
      return window.localStorage.getItem(STORED_FILTERS_SHOWN) === 'shown'
    } catch (refusal) {
      if (!(refusal instanceof DOMException)) throw refusal
      return false
    }
  }

  // Remembers in this browser whether the person opened or closed the node filter; a browser that keeps nothing forgets.
  showFilters(isShown: boolean): void {
    try {
      window.localStorage.setItem(STORED_FILTERS_SHOWN, isShown ? 'shown' : 'closed')
    } catch (refusal) {
      if (!(refusal instanceof DOMException)) throw refusal
    }
  }

  // The entries below entry, as read with it or, once a person opened it, as its branch was read.
  childrenOf(entry: ExplorerEntryData): ExplorerEntryData[] {
    return (this.store.state.graph.branches[entry.node_id] ?? entry).children.filter(isEntry)
  }

  // Go to file on a fold-out: the node it shows opens in its own file at its lines, as selecting it at its home in the
  // tree opens it; a section a markdown link opens is no node, so its file opens at the lines it names.
  async goToFile(foldOut: SourceCallout): Promise<void> {
    try {
      const ranges = foldOut.kind === 'section' ? [sectionRange(foldOut)] : listAnswered<RangeData>('session.graph_node_ranges', await this.session.graphNodeRanges(foldOut.id, this.paths))
      if (!ranges.length) return
      const selected = ranges.map(lines => ({ nodeId: foldOut.id, lines }))
      this.store.change(({ graph }) => ({ graph: { ...graph, selected, expanded: [] } }))
      await this.showNodes(selected)
    } catch (failure) {
      this.notices.fail(`The Files app did not open the file of ${foldOut.title}: ${reasonOf(failure)}`, 'Go to file on a fold-out, calling session.graph_node_ranges')
    }
  }

  // The node whose connector reaches entry, in the trees as they are open: the step above an invokes or observes
  // connector entry sits under, or the scenario or step an example sits under; none for a node shown at its own home.
  private connectorHolderOf(target: ExplorerEntryData): ExplorerEntryData | null {
    const above = (this.store.state.graph.trees ?? []).map(tree => this.pathTo(target, tree, [])).find(Boolean) ?? []
    const parent = above.at(-1)
    if (parent && isConnector(parent)) return above.at(-2) ?? null
    return parent && target.type === EXAMPLE_TYPE ? parent : null
  }

  // The entries from tree down to target, target left out; none when tree does not hold it.
  private pathTo(target: ExplorerEntryData, entry: ExplorerEntryData, above: ExplorerEntryData[]): ExplorerEntryData[] | null {
    if (entry === target) return above
    for (const child of this.childrenOf(entry)) {
      const found = this.pathTo(target, child, [...above, entry])
      if (found) return found
    }
    return null
  }

  // The rules entry is judged by, passing, broken and left to the agent's judgement, as the graph sent them with it.
  rulesOf(entry: ExplorerEntryData): GraphRuleData[] {
    const group = (this.store.state.graph.branches[entry.node_id] ?? entry).children.find(isRulesGroup)
    return group ? group.children : []
  }

  breaksARule(entry: ExplorerEntryData): boolean {
    return this.rulesOf(entry).some(rule => rule.status === 'violating')
  }

  isOpen(entry: ExplorerEntryData): boolean {
    return this.store.state.graph.openNodes.includes(entry.node_id)
  }

  isSelected(entry: ExplorerEntryData): boolean {
    return this.store.state.graph.selected.some(selected => selected.nodeId === entry.node_id)
  }

  // Reads each node the person has open again, for the files and node filter the trees were just read for: a branch
  // read for the old list holds the old list's nodes, so an open node would go on showing them.
  private async readOpenBranches(readFor: string): Promise<void> {
    const paths = this.paths
    const filter = this.nodeFilter
    const read = await Promise.all(this.store.state.graph.openNodes.map(async nodeId => [nodeId, await this.session.graphBranch(nodeId, paths, filter)] as const))
    const branches = Object.fromEntries(read.filter((each): each is readonly [string, ExplorerEntryData] => each[1] !== null))
    this.store.change(({ graph }) => (graph.readFor === readFor ? { graph: { ...graph, branches: { ...graph.branches, ...branches } } } : {}))
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
  // member's own file, or every listed file below a folder such as a package. A node reached through a connector, such as
  // the operation a step invokes or an example a scenario uses, never opens its own file: the node holding the connector
  // opens at its lines, and the node expands in place under the line that uses it. A node read from no lines of a file
  // selects nothing.
  async select(entry: ExplorerEntryData, also: boolean = false): Promise<void> {
    try {
      const holder = this.connectorHolderOf(entry)
      const ranges = listAnswered<RangeData>('session.graph_node_ranges', await this.session.graphNodeRanges((holder ?? entry).node_id, this.paths))
      if (!ranges.length) return
      const kept = also ? this.store.state.graph.selected.filter(selected => selected.nodeId !== entry.node_id) : []
      const selected = [...kept, ...ranges.map(lines => ({ nodeId: entry.node_id, lines }))]
      const expanded = [...(also ? this.store.state.graph.expanded.filter(id => id !== entry.node_id) : []), ...(holder ? [entry.node_id] : [])]
      this.store.change(({ graph }) => ({ graph: { ...graph, selected, expanded } }))
      await this.showNodes(selected)
    } catch (failure) {
      this.notices.fail(`The Files app did not open ${entry.name}: ${reasonOf(failure)}`, 'Selecting a node in the graph view, calling session.graph_node_ranges')
    }
  }

  // Selects a rule entry carries: a broken rule opens the lines its violations name, unfolded, as a selected node opens
  // its own; any other rule opens the node it sits under.
  async selectRule(entry: ExplorerEntryData, rule: GraphRuleData): Promise<void> {
    const named = rule.status === 'violating' ? rule.violations.filter(hit => hit.location && hit.line) : []
    if (!named.length) return this.select(entry)
    const selected = named.map(hit => ({ nodeId: entry.node_id, lines: violationRange(hit) }))
    this.store.change(({ graph }) => ({ graph: { ...graph, selected, expanded: [] } }))
    await this.showNodes(selected)
  }
}
