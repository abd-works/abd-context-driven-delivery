// The Files app's acceptance tests for its graph view, story by story as
// story_tests/review-generated-work-in-file-viewer/switch-files-app-between-files-and-graph/switch_files_app_between_files_and_graph_story.test.md
// writes them; what the session's graph answers is proved by the sub-epic's story tests in story_tests/review-generated-work-in-file-viewer/.
import { fireEvent, render } from '@testing-library/react'
import { createElement } from 'react'
import { beforeEach, describe, expect, it } from 'vitest'

import type { CddApi } from '@cdd/cdd-shared'
import type { GraphRuleData, ViolationData } from '@cdd/harness/graph/graph'
import type { ExplorerEntryData, GuidanceSelectionData } from '@cdd/space/session/session'

import { NodeFilterLists } from '@graph-app/filter/FilterView'
import { NO_CHOICES, NO_FILTER } from '@graph-app/filter/filter-selection'

import { isFailing, ruleTitleOf } from './files-graph'
import { FilesGraphView } from './files-graph-view'
import { FilesLink } from './files-link'
import { FilesPage } from './files-page'

// Each stage's fidelities by practice, as checkout-flow's practices declare them.
const FIDELITIES: Record<string, Record<string, string>> = {
  discovery: { stories: 'stories-story-map' },
  implementation: { clean_engineering: 'clean-engineering-code' },
}
const PRACTICES = [
  { key: 'stories', short_name: 'Stories', colour: '#c0392b' },
  { key: 'clean_engineering', short_name: 'Clean Engineering', colour: '#2471a3' },
]

// Seed: checkout-flow's files, as ticket.root_files answers them, the branch having changed the story map and ticket.py.
const STORY_MAP = '.context/story-map.md'
const TICKET_CODE = 'space/kanban/ticket.py'
const BOARD_CODE = 'space/kanban/board.py'
const rootFile = (path: string, format: string, fidelity: string, is_changed: boolean) => ({ path, exists: true, is_changed, link: '', format, fidelities: [fidelity] })
const CHECKOUT_FLOW_FILES = [
  rootFile(STORY_MAP, 'markdown', 'stories-story-map', true),
  rootFile(TICKET_CODE, 'python', 'clean-engineering-code', true),
  rootFile(BOARD_CODE, 'python', 'clean-engineering-code', false),
]

// Seed: a rule the file breaks, which session.file answers whenever it reads the file's rules.
const BROKEN_RULE = { range: { path: TICKET_CODE, start_line: 460, end_line: 465, content: '', anchor: '' }, violation: { rule: 'keep-operations-small-focused', message: 'activate runs 24 statements' } }

// Seed: checkout-flow's nodes, each in its file at its lines, under its practice's root.
// A node shown under a connector, such as the operation a step invokes, is its own node shown there: shows names it.
// A label is what the graph shows for a node that another beside it shares a name with; any other shows its name.
type SeedNode = { id: string; name: string; type: string; file: string; start: number; end: number; parent: string; shows?: string; label?: string; rules?: GraphRuleData[] }

// Seed: a rule a node carries, as the graph answers it in the node's rules group.
const ruleOf = (name: string, status: string, violations: ViolationData[] = []): GraphRuleData => ({ slug: name, body: '', type: 'Rule', name, node_id: `ticket-activate:rules:${name}`, children: [], status, violations, scope: 'paths', requires_judge: false })
// Seed: Ticket.activate breaks keep-operations-small-focused on lines 460 to 465, passes use-intention-revealing-names,
// and leaves hide-inner-details to the agent's judgement.
const ACTIVATE_TOO_LONG: ViolationData = { rule: 'keep-operations-small-focused', practice: 'clean_engineering', node_id: 'ticket-activate', subject: 'activate', location: TICKET_CODE, line: 460, end_line: 465, message: 'activate runs 24 statements', severity: 'error', source: [], scope: 'paths' }
// Seed: a rule that requires a judge listing lines 462 to 463 of Ticket.activate as a candidate for a reading.
const ACTIVATE_CANDIDATE = ruleOf('use-intention-revealing-names', 'candidate', [{ ...ACTIVATE_TOO_LONG, rule: 'use-intention-revealing-names', line: 462, end_line: 463, message: 'activate may not say why it exists', severity: 'candidate' }])
const ACTIVATE_RULES = [ruleOf('keep-operations-small-focused', 'violating', [ACTIVATE_TOO_LONG]), ruleOf('use-intention-revealing-names', 'passing'), ruleOf('hide-inner-details', 'prompt')]
const CHECKOUT_FLOW_NODES: SeedNode[] = [
  { id: 'stories', name: 'Stories', type: 'Practice', file: '', start: 0, end: 0, parent: '' },
  { id: 'delete-ticket', name: 'Delete Ticket', type: 'Story', file: STORY_MAP, start: 315, end: 319, parent: 'stories' },
  // Seed: Delete Ticket's When step, on lines 316 to 318, invoking Ticket.close, which its invokes connector shows.
  { id: 'delete-ticket-when', name: 'when the Person deletes it', type: 'When', file: STORY_MAP, start: 316, end: 318, parent: 'delete-ticket' },
  { id: 'delete-ticket-when-invokes', name: 'invokes', type: 'invokes', file: STORY_MAP, start: 316, end: 318, parent: 'delete-ticket-when' },
  { id: 'delete-ticket-when-invokes-close', name: 'close', type: 'Operation', file: TICKET_CODE, start: 538, end: 555, parent: 'delete-ticket-when-invokes', shows: 'ticket-close' },
  { id: 'clean_engineering', name: 'Clean Engineering', type: 'Practice', file: '', start: 0, end: 0, parent: '' },
  { id: 'ticket', name: 'Ticket', type: 'OoadClass', file: TICKET_CODE, start: 106, end: 670, parent: 'clean_engineering', label: 'Ticket (ticket.py)' },
  { id: 'ticket-activate', name: 'activate', type: 'Operation', file: TICKET_CODE, start: 460, end: 465, parent: 'ticket', rules: ACTIVATE_RULES },
  { id: 'ticket-close', name: 'close', type: 'Operation', file: TICKET_CODE, start: 538, end: 555, parent: 'ticket' },
  { id: 'board', name: 'Board', type: 'OoadClass', file: BOARD_CODE, start: 104, end: 397, parent: 'clean_engineering' },
  { id: 'board-reread', name: 'reread', type: 'Operation', file: BOARD_CODE, start: 286, end: 289, parent: 'board' },
]

// What Python writes for a fix, which the page sends as it is; its words are pinned by Python's spec.
const FIX_PROMPT = 'Fix this violation using the Clean Engineering practice guidelines and a test-driven approach.\n…\nRule: keep-operations-small-focused'

// The Files app's page against a fake of its own server, which answers the session's graph as session.graph_trees,
// graph_branch, graph_node_ranges and graph_members do: only the nodes read from the files a call names, each root opened
// one level and every entry below it closed, its own entries left out; and the cdd server's progress reports while the
// trees are held back.
class FakeFilesServer implements CddApi {
  readonly posts: { path: string; body: Record<string, unknown> }[] = []
  version = 0
  stages = ['discovery', 'implementation']
  practices = ['stories', 'clean_engineering']
  progress: string[] = []
  // What graph_trees, graph_members and graph_filter_choices answer in place of the seed's, as a server lane that cannot
  // run the call answers: a failure's text, an error, or nothing, rather than what the tool returns.
  treesAnswer: unknown = undefined
  membersAnswer: unknown = undefined
  choicesAnswer: unknown = undefined
  isChoicesAnswered = false
  // What graph_fix_prompt answers: the fix Python writes, or none when the view no longer shows the rule broken.
  fixPrompt = FIX_PROMPT
  private readonly waiting: (() => void)[] = []
  private held: Promise<void> | null = null
  private release: () => void = () => {}

  // Holds the next graph_trees answer back until released, as a long first load does.
  holdTrees(): void {
    this.held = new Promise(resolve => (this.release = resolve))
  }

  releaseTrees(): void {
    this.held = null
    this.release()
  }

  async post<Result>(path: string, body: Record<string, unknown> = {}): Promise<Result | null> {
    this.posts.push({ path, body })
    if (path.endsWith('/graph-trees') && this.treesAnswer !== undefined) return this.treesAnswer as Result
    if (path.endsWith('/graph-fix-prompt')) return this.fixPrompt as Result
    if (path.endsWith('/guidance-selection')) return this.selection() as Result
    if (path.endsWith('/toggle-guidance')) return this.toggle(String(body.part), String(body.name)) as Result
    if (path.endsWith('/guidance-selection-after')) return (await this.after(Number(body.version))) as Result
    if (path.endsWith('/fidelity-files')) return {} as Result
    if (path.endsWith('/root-files')) return this.rootFiles() as Result
    if (path.endsWith('/graph-trees')) return (await this.heldTrees(body.paths as string[])) as Result
    if (path.endsWith('/graph-filter-choices') && this.isChoicesAnswered) return this.choicesAnswer as Result
    if (path.endsWith('/graph-members') && this.membersAnswer !== undefined) return this.membersAnswer as Result
    if (path.endsWith('/graph-filter-choices')) return this.choices(body.node_types as string[]) as Result
    if (path.endsWith('/graph-branch')) return this.entry(this.node(String(body.node_id)), body.paths as string[], true) as Result
    if (path.endsWith('/graph-node-ranges')) return this.ranges(this.node(String(body.node_id)), body.paths as string[]) as Result
    if (path.endsWith('/graph-members')) return CHECKOUT_FLOW_NODES.filter(node => node.file && !node.shows && node.type !== node.name && node.type !== 'When').map(node => ({ node_id: node.id, name: node.name, type: node.type, file: node.file })) as Result
    if (path.endsWith('/cdd/progress')) return this.progress.map(message => ({ tool: 'session.graph_trees', message })) as Result
    if (path.endsWith('/file')) return { path: body.path, text: 'line\n'.repeat(700), language: 'python', comments: [], folds: [], violations: body.rules ? [BROKEN_RULE] : [], changes: [] } as Result
    return null
  }

  // The files under the root as ticket.root_files answers them for the selection: listed while a fidelity it belongs to
  // is selected, and the session's work when the branch changed it.
  private rootFiles() {
    const listed = this.selection().fidelities
    return CHECKOUT_FLOW_FILES.map(file => ({ ...file, is_listed: file.fidelities.some(slug => listed.includes(slug)), is_session_work: file.is_changed }))
  }

  // A press on a practice's toggle, as Session.toggle_guidance answers it: the practice taken out of those selected, or put in.
  toggle(_part: string, name: string): GuidanceSelectionData {
    return this.update({ practices: this.practices.includes(name) ? this.practices.filter(each => each !== name) : [...this.practices, name] })
  }

  // A change made on the chat bar or in the page: the version moves and every waiting read answers.
  update(body: Record<string, unknown>): GuidanceSelectionData {
    if (body.practices) this.practices = [...(body.practices as string[])]
    this.version += 1
    this.waiting.splice(0).forEach(answer => answer())
    return this.selection()
  }

  private after(version: number): Promise<GuidanceSelectionData> {
    if (this.version > version) return Promise.resolve(this.selection())
    return new Promise(resolve => this.waiting.push(() => resolve(this.selection())))
  }

  selection(): GuidanceSelectionData {
    const fidelities = this.stages.flatMap(stage => this.practices.map(key => FIDELITIES[stage]![key]).filter((slug): slug is string => Boolean(slug)))
    return {
      version: this.version,
      is_stage_chosen: true,
      stages: Object.keys(FIDELITIES).map(name => ({ name, title: name, is_selected: this.stages.includes(name) })),
      covered_stages: this.stages,
      practices: PRACTICES.map(practice => ({ ...practice, is_selected: this.practices.includes(practice.key) })),
      formats: [],
      fidelities,
      commands: {},
    } as GuidanceSelectionData
  }

  private node(id: string): SeedNode {
    return CHECKOUT_FLOW_NODES.find(node => node.id === id)!
  }

  // Whether a node, or one below it, was read from one of paths.
  private holds(node: SeedNode, paths: string[]): boolean {
    return paths.includes(node.file) || CHECKOUT_FLOW_NODES.some(child => child.parent === node.id && this.holds(child, paths))
  }

  private entry(node: SeedNode, paths: string[], isOpened: boolean): ExplorerEntryData {
    const below = CHECKOUT_FLOW_NODES.filter(child => child.parent === node.id && this.holds(child, paths))
    const node_id = node.shows ?? node.id
    // Every entry keeps its rules, open or closed, in a rules group the graph puts first.
    const rules = node.rules ? [{ type: 'rules', name: 'rules', node_id: `${node_id}:rules`, children: node.rules }] : []
    const label = node.label ?? node.name
    if (!isOpened) return { node_id, name: node.name, label, type: node.type, children: rules as never[], children_left_out: below.length } as ExplorerEntryData
    return { node_id, name: node.name, label, type: node.type, children: [...rules, ...below.map(child => this.entry(child, paths, false))] as never[], children_left_out: 0 } as ExplorerEntryData
  }

  private trees(paths: string[]): ExplorerEntryData[] {
    return CHECKOUT_FLOW_NODES.filter(node => !node.parent && this.holds(node, paths)).map(root => this.entry(root, paths, true))
  }

  private async heldTrees(paths: string[]): Promise<ExplorerEntryData[]> {
    if (this.held) await this.held
    return this.trees(paths)
  }

  // A node read from a file's lines answers that range; any other, such as a practice's root or a folder, answers each
  // listed file below it, spanning the lines its nodes cover there.
  private ranges(node: SeedNode, paths: string[]) {
    const spans = new Map<string, [number, number]>()
    const widen = (each: SeedNode) => {
      if (each.file) {
        if (!paths.includes(each.file)) return
        const [start, end] = spans.get(each.file) ?? [each.start, each.end]
        spans.set(each.file, [Math.min(start, each.start), Math.max(end, each.end)])
        return
      }
      CHECKOUT_FLOW_NODES.filter(child => child.parent === each.id).forEach(widen)
    }
    widen(node)
    return [...spans].map(([path, [start, end]]) => ({ path, start_line: start, end_line: end, content: '', anchor: `${path}:${start}-${end}` }))
  }

  // The choices Python's Filter offers for the node types chosen: operations sit on owns and invokes, and carry their rules.
  private choices(nodeTypes: string[]) {
    const operations = nodeTypes.includes('Operation')
    return {
      node_types: nodeTypes,
      offered_node_types: ['OoadClass', 'Operation'],
      relationships: operations ? ['owns', 'invokes'] : ['owns'],
      rules: operations ? ['clean_engineering.Operation.keep-operations-small-focused'] : [],
    }
  }

  posted(ending: string): { path: string; body: Record<string, unknown> }[] {
    return this.posts.filter(post => post.path.endsWith(ending))
  }
}

const LINK = '?files=checkout-flow&fidelity=stories-story-map,clean-engineering-code&chat=chat-1'

async function settled(): Promise<void> {
  for (let turn = 0; turn < 5; turn += 1) await new Promise(resolve => setTimeout(resolve, 0))
}

// The page as the person finds it once it opened, following the session's selection, its files listed in All session
// files.
async function opened(server = new FakeFilesServer()): Promise<{ page: FilesPage; server: FakeFilesServer; stop: () => void }> {
  const page = new FilesPage(server, new FilesLink(LINK))
  const stop = page.start()
  await settled()
  page.showScope('all')
  await settled()
  return { page, server, stop }
}

// The page showing checkout-flow's graph.
async function showingGraph(server = new FakeFilesServer()): Promise<{ page: FilesPage; server: FakeFilesServer; stop: () => void }> {
  const shown = await opened(server)
  shown.page.fileBar.show('graph')
  await settled()
  return shown
}

const treeNames = (page: FilesPage): string[] => (page.state.graph.trees ?? []).map(tree => tree.name)
const namesBelow = (page: FilesPage, name: string): string[] => {
  const tree = (page.state.graph.trees ?? []).find(each => each.name === name)
  return tree ? page.graph.childrenOf(tree).map(entry => entry.name) : []
}
const entryNamed = (page: FilesPage, name: string): ExplorerEntryData => {
  const found = (entries: ExplorerEntryData[]): ExplorerEntryData | undefined =>
    entries.map(entry => (entry.name === name ? entry : found(page.graph.childrenOf(entry)))).find(Boolean)
  return found(page.state.graph.trees ?? [])!
}

describe('Switch Files App To Graph View', () => {
  describe('with the Files app listing checkout-flow\'s Stories and Clean Engineering files', () => {
    it('should show the Stories and Clean Engineering practice trees when the file bar switches to the graph view', async () => {
      const { page, stop } = await showingGraph()
      stop()
      expect(treeNames(page)).toEqual(['Stories', 'Clean Engineering'])
    })

    it('should show each practice tree collapsed', async () => {
      const { page, stop } = await showingGraph()
      stop()
      expect(page.state.graph.openNodes).toEqual([])
    })

    it('should keep the open file open in the source view', async () => {
      const { page, stop } = await opened()
      const before = page.state.openPath
      page.fileBar.show('graph')
      await settled()
      stop()
      expect([page.state.openPath, before]).toEqual([STORY_MAP, STORY_MAP])
    })
  })

  describe('with the Files app showing checkout-flow\'s graph', () => {
    it('should list checkout-flow\'s files in folders again when the file bar switches back', async () => {
      const { page, stop } = await showingGraph()
      page.fileBar.show('folders')
      stop()
      expect([page.state.fileBar.view, page.fileBar.entries.map(entry => entry.path)]).toEqual(['folders', [STORY_MAP, TICKET_CODE, BOARD_CODE]])
    })
  })
})

describe('Filter Graph Like The File List', () => {
  describe('with Stories and Clean Engineering on', () => {
    it('should hold only the Stories tree once the Person turns Clean Engineering off', async () => {
      const { page, stop } = await showingGraph()
      await page.guidance.toggle('practice', 'clean_engineering')
      // The session answers the files again for the selection the press leaves, then the graph is read for them.
      await settled()
      await settled()
      stop()
      expect(treeNames(page)).toEqual(['Stories'])
    })

    it('should list only story-map.md when switched back to the files', async () => {
      const { page, stop } = await showingGraph()
      await page.guidance.toggle('practice', 'clean_engineering')
      await settled()
      await settled()
      page.fileBar.show('list')
      stop()
      expect(page.fileBar.entries.map(entry => entry.path)).toEqual([STORY_MAP])
    })

    it('should hold only the Stories tree once the Person selects only the Stories dot on the chat bar', async () => {
      const { page, server, stop } = await showingGraph()
      server.update({ practices: ['stories'] })
      await settled()
      stop()
      expect(treeNames(page)).toEqual(['Stories'])
    })
  })

  describe('with Clean Engineering on and the Changed button turned on', () => {
    it('should keep Ticket in the Clean Engineering tree but not Board, since board.py is unchanged on the branch', async () => {
      const { page, stop } = await showingGraph()
      page.showScope('session')
      await settled()
      stop()
      expect(namesBelow(page, 'Clean Engineering')).toEqual(['Ticket'])
    })
  })
})

describe('Filter Graph By Node Type And Connector', () => {
  describe("with checkout-flow's graph shown", () => {
    async function filteredToOperations() {
      const shown = await showingGraph()
      await shown.page.graph.filterTo({ ...shown.page.state.graph.filter, node_types: ['Operation'] })
      await settled()
      return shown
    }

    it('should offer the node types the graph holds once it is read', async () => {
      const { page, stop } = await showingGraph()
      stop()
      expect(page.state.graph.choices.offered_node_types).toEqual(['OoadClass', 'Operation'])
    })

    it('should read the graph again for the files listed, narrowed to operations, when the Person filters to operations', async () => {
      const { server, stop } = await filteredToOperations()
      stop()
      expect(server.posted('/graph-trees').at(-1)?.body).toEqual({ paths: [STORY_MAP, TICKET_CODE, BOARD_CODE], node_filter: { types: ['Operation'], relationships: ['owns', 'invokes'] } })
    })

    it('should offer the connectors and rules operations carry', async () => {
      const { page, stop } = await filteredToOperations()
      stop()
      expect([page.state.graph.choices.relationships, page.state.graph.choices.rules]).toEqual([['owns', 'invokes'], ['clean_engineering.Operation.keep-operations-small-focused']])
    })

    it('should keep only the nodes on the invokes connector when the Person chooses it', async () => {
      const { page, server, stop } = await filteredToOperations()
      await page.graph.filterTo({ ...page.state.graph.filter, relationships: ['invokes'] })
      await settled()
      stop()
      expect(server.posted('/graph-trees').at(-1)?.body.node_filter).toEqual({ types: ['Operation'], relationships: ['invokes'] })
    })

    it('should open a node with the same node filter', async () => {
      const { page, server, stop } = await filteredToOperations()
      await page.graph.toggle(entryNamed(page, 'Clean Engineering'))
      await page.graph.toggle(entryNamed(page, 'Ticket'))
      stop()
      expect(server.posted('/graph-branch').at(-1)?.body.node_filter).toEqual({ types: ['Operation'], relationships: ['owns', 'invokes'] })
    })

    it('should keep the node filter when the file list changes to the changed files', async () => {
      const { page, server, stop } = await filteredToOperations()
      page.showScope('session')
      await settled()
      stop()
      expect(server.posted('/graph-trees').at(-1)?.body).toEqual({ paths: [STORY_MAP, TICKET_CODE], node_filter: { types: ['Operation'], relationships: ['owns', 'invokes'] } })
    })

    it('should send no node type once the Person clears the node types with None', async () => {
      const { page, server, stop } = await filteredToOperations()
      await page.graph.filterTo({ ...page.state.graph.filter, node_types: [] })
      await settled()
      stop()
      expect(server.posted('/graph-trees').at(-1)?.body.node_filter).toEqual({ relationships: ['owns'] })
    })

    it('should keep only violating nodes, of the rules chosen, once the Person turns on Violations', async () => {
      const { page, server, stop } = await filteredToOperations()
      await page.graph.filterTo({ ...page.state.graph.filter, violations: true })
      await settled()
      stop()
      expect(server.posted('/graph-trees').at(-1)?.body.node_filter).toEqual({
        types: ['Operation'],
        relationships: ['owns', 'invokes'],
        violations: true,
        rules: ['clean_engineering.Operation.keep-operations-small-focused'],
      })
    })
  })
})

describe('Read Open Nodes Again For A Switched Scope', () => {
  describe("with Clean Engineering and Ticket open in checkout-flow's graph", () => {
    it('should read each open node again for the changed files once the Person switches the file list to them', async () => {
      const { page, server, stop } = await showingGraph()
      await page.graph.toggle(entryNamed(page, 'Clean Engineering'))
      await page.graph.toggle(entryNamed(page, 'Ticket'))
      const ticket = entryNamed(page, 'Ticket').node_id
      page.showScope('session')
      await settled()
      stop()
      const readForChanged = server.posted('/graph-branch').filter(post => (post.body.paths as string[]).join() === [STORY_MAP, TICKET_CODE].join())
      expect(readForChanged.map(post => post.body.node_id)).toContain(ticket)
    })
  })
})

describe('Collapse The Graph Node Filter', () => {
  beforeEach(() => window.localStorage.clear())

  const shownView = (page: FilesPage) => render(createElement(FilesGraphView, { page }))
  const filtersToggle = (view: ReturnType<typeof render>) => view.getByRole('button', { name: 'Filters' })
  const nodeFilterShown = (view: ReturnType<typeof render>) => view.queryByLabelText('Node filter') !== null

  describe('with the Person never having opened the filters in this browser', () => {
    it('should show one closed Filters toggle above the trees', async () => {
      const { page, stop } = await showingGraph()
      stop()
      const view = shownView(page)
      expect(filtersToggle(view).getAttribute('aria-expanded')).toBe('false')
      view.unmount()
    })

    it('should not show the node type, connector and rule lists', async () => {
      const { page, stop } = await showingGraph()
      stop()
      const view = shownView(page)
      expect(nodeFilterShown(view)).toBe(false)
      view.unmount()
    })
  })

  describe('with the Person pressing Filters', () => {
    it('should show the node filter above the trees', async () => {
      const { page, stop } = await showingGraph()
      stop()
      const view = shownView(page)
      fireEvent.click(filtersToggle(view))
      expect(nodeFilterShown(view)).toBe(true)
      view.unmount()
    })

    it('should open the next graph view in this browser with the node filter shown', async () => {
      const { page, stop } = await showingGraph()
      stop()
      const first = shownView(page)
      fireEvent.click(filtersToggle(first))
      first.unmount()
      const next = shownView(page)
      expect(nodeFilterShown(next)).toBe(true)
      next.unmount()
    })

    it('should close the node filter again once the Person presses Filters a second time', async () => {
      const { page, stop } = await showingGraph()
      stop()
      const view = shownView(page)
      fireEvent.click(filtersToggle(view))
      fireEvent.click(filtersToggle(view))
      expect(nodeFilterShown(view)).toBe(false)
      view.unmount()
    })
  })
})

describe('Open Several Files From Graph Nodes', () => {
  describe('with checkout-flow\'s graph shown', () => {
    async function selectedActivate() {
      const shown = await showingGraph()
      await shown.page.graph.toggle(entryNamed(shown.page, 'Clean Engineering'))
      await shown.page.graph.toggle(entryNamed(shown.page, 'Ticket'))
      await shown.page.graph.select(entryNamed(shown.page, 'activate'))
      await settled()
      return shown
    }

    it('should open ticket.py at lines 460 to 465 when the Person selects Ticket.activate', async () => {
      const { page, stop } = await selectedActivate()
      stop()
      expect([page.state.openPath, page.linesShownIn(TICKET_CODE)]).toEqual([TICKET_CODE, [{ start: 460, end: 465 }]])
    })

    it('should read ticket.py with its folds', async () => {
      const { page, server, stop } = await selectedActivate()
      stop()
      expect(server.posted('/file').at(-1)?.body).toMatchObject({ path: TICKET_CODE, rules: true })
      expect(page.state.file?.path).toBe(TICKET_CODE)
    })

    it('should open ticket.py and board.py both when the Person also selects Board.reread', async () => {
      const { page, stop } = await selectedActivate()
      await page.graph.toggle(entryNamed(page, 'Board'))
      await page.graph.select(entryNamed(page, 'reread'), true)
      await settled()
      stop()
      expect([page.state.openPath, page.state.moreFiles.map(file => file.path)]).toEqual([TICKET_CODE, [BOARD_CODE]])
    })
  })
})

describe('Fold Open Files To Selected Nodes', () => {
  // Opening the lines asked for, with every other fold closed, is the source view's own (harness/graph/app/app.test.tsx,
  // "should fold everything with Monaco's Fold All"); the page asks it for the lines of every node selected in the file.
  describe('with Ticket.activate selected and ticket.py open', () => {
    it('should ask the source view to open Ticket.close too once the Person also selects it', async () => {
      const { page, stop } = await showingGraph()
      await page.graph.toggle(entryNamed(page, 'Clean Engineering'))
      await page.graph.toggle(entryNamed(page, 'Ticket'))
      await page.graph.select(entryNamed(page, 'activate'))
      await page.graph.select(entryNamed(page, 'close'), true)
      await settled()
      stop()
      expect(page.linesShownIn(TICKET_CODE)).toEqual([
        { start: 460, end: 465 },
        { start: 538, end: 555 },
      ])
    })
  })
})

describe('Open Every File Of A Folder Node', () => {
  describe("with checkout-flow's graph shown", () => {
    it('should open ticket.py and board.py, the files below it, when the Person selects the Clean Engineering root', async () => {
      const { page, stop } = await showingGraph()
      await page.graph.select(entryNamed(page, 'Clean Engineering'))
      await settled()
      stop()
      expect([page.state.openPath, page.state.moreFiles.map(file => file.path), page.linesShownIn(BOARD_CODE)]).toEqual([TICKET_CODE, [BOARD_CODE], [{ start: 104, end: 397 }]])
    })
  })
})

describe('Show Graph Load Steps', () => {
  describe("with the session's graph still loading", () => {
    it('should show each step the cdd server reports while the trees are read', async () => {
      const server = new FakeFilesServer()
      server.holdTrees()
      server.progress = ['load: 1/2 stories']
      const { page, stop } = await showingGraph(server)
      await new Promise(resolve => setTimeout(resolve, 0))
      const reading = { isReading: page.state.graph.isReading, log: page.state.graph.log }
      server.releaseTrees()
      await settled()
      stop()
      expect([reading, page.state.graph.isReading]).toEqual([{ isReading: true, log: ['load: 1/2 stories'] }, false])
    })
  })
})

describe('Open Calls Across Files', () => {
  describe("with checkout-flow's graph read", () => {
    it('should hold every class and operation the graph holds, so the open file opens a call from board.py in place', async () => {
      const { page, stop } = await showingGraph()
      stop()
      expect(page.state.graph.members.map(member => member.name)).toEqual(['Delete Ticket', 'Ticket', 'activate', 'close', 'Board', 'reread'])
    })
  })
})

describe('Show A Graph Read That Failed', () => {
  // The text a server lane answers when it cannot run a graph call, as an older lane does for a newer page's call.
  const LANE_FAILURE = "TypeError: Session.graph_trees() got an unexpected keyword argument 'node_filter'"
  const drawn = (page: FilesPage) => () => render(createElement(FilesGraphView, { page })).unmount()

  describe("with session.graph_trees answering a failure's text instead of the trees", () => {
    it('should hold no tree and show the failure in place of the graph', async () => {
      const server = new FakeFilesServer()
      server.treesAnswer = LANE_FAILURE
      const { page, stop } = await showingGraph(server)
      stop()
      expect([page.state.graph.trees, page.state.graph.isReading, page.state.graph.problem]).toEqual([[], false, expect.stringContaining(LANE_FAILURE)])
    })

    it('should copy the failure for the chat when the Person presses Copy for AI', async () => {
      const server = new FakeFilesServer()
      server.treesAnswer = LANE_FAILURE
      const { page, stop } = await showingGraph(server)
      stop()
      const copied: string[] = []
      Object.defineProperty(navigator, 'clipboard', { value: { writeText: async (text: string) => void copied.push(text) }, configurable: true })
      const view = render(createElement(FilesGraphView, { page }))
      fireEvent.click(view.getByRole('button', { name: 'Copy for AI' }))
      await settled()
      view.unmount()
      expect(copied).toEqual([page.state.graph.problem])
    })

    it('should name session.graph_trees in the failure when it answers an error', async () => {
      const server = new FakeFilesServer()
      server.treesAnswer = { error: LANE_FAILURE }
      const { page, stop } = await showingGraph(server)
      stop()
      expect(page.state.graph.problem).toContain('session.graph_trees')
    })
  })

  describe('with session.graph_members answering something other than a list', () => {
    it('should keep the trees and hold no member', async () => {
      const server = new FakeFilesServer()
      server.membersAnswer = 'no members'
      const { page, stop } = await showingGraph(server)
      stop()
      expect([treeNames(page), page.state.graph.members]).toEqual([['Stories', 'Clean Engineering'], []])
    })
  })

  for (const [said, answer] of [
    ["a failure's text", "ToolNotEnrolled: session.graph_filter_choices"],
    ['an error', { error: 'ToolNotEnrolled: session.graph_filter_choices' }],
    ['nothing', undefined],
    ['choices without offered_node_types', { node_types: [], relationships: [], rules: [] }],
  ] as const) {
    describe(`with session.graph_filter_choices answering ${said}`, () => {
      async function shownWithChoices() {
        const server = new FakeFilesServer()
        server.isChoicesAnswered = true
        server.choicesAnswer = answer
        return showingGraph(server)
      }

      it('should draw the graph view with its node filter offering nothing', async () => {
        const { page, stop } = await shownWithChoices()
        stop()
        expect(drawn(page)).not.toThrow()
        expect(page.state.graph.choices).toEqual(NO_CHOICES)
      })

      it('should keep the trees it read', async () => {
        const { page, stop } = await shownWithChoices()
        stop()
        expect(treeNames(page)).toEqual(['Stories', 'Clean Engineering'])
      })

      if (answer !== undefined) {
        it('should tell the failure, naming session.graph_filter_choices', async () => {
          const { page, stop } = await shownWithChoices()
          stop()
          expect(page.state.toasts.some(toast => toast.includes('session.graph_filter_choices'))).toBe(true)
        })
      }
    })
  }

  describe('with a node filter given no lists to offer', () => {
    it('should draw its lists empty rather than throw', () => {
      const lists = { selection: NO_FILTER, nodeTypes: undefined, relationships: undefined, rules: undefined, onChange: () => {} }
      expect(() => render(createElement(NodeFilterLists, lists)).unmount()).not.toThrow()
    })
  })
})

describe("Open A Relationship's Member In Its Own File", () => {
  describe("with Delete Ticket's When step invoking Ticket.close, shown under its invokes group", () => {
    async function selectedInvokedClose() {
      const shown = await showingGraph()
      for (const name of ['Delete Ticket', 'when the Person deletes it', 'invokes']) await shown.page.graph.toggle(entryNamed(shown.page, name))
      const invokes = entryNamed(shown.page, 'invokes')
      await shown.page.graph.select(shown.page.graph.childrenOf(invokes)[0]!)
      await settled()
      return shown
    }

    it('should open ticket.py at the lines close covers when the Person selects close there', async () => {
      const { page, stop } = await selectedInvokedClose()
      stop()
      expect([page.state.openPath, page.linesShownIn(TICKET_CODE)]).toEqual([TICKET_CODE, [{ start: 538, end: 555 }]])
    })

    it("should mark no line of the step's own file", async () => {
      const { page, stop } = await selectedInvokedClose()
      stop()
      expect(page.linesShownIn(STORY_MAP)).toEqual([])
    })
  })
})

describe('Show Rules Only When Asked', () => {
  describe('with Rules off and Ticket.activate selected in the graph, which reads ticket.py with its rules for its folds', () => {
    it('should show no broken rule in ticket.py', async () => {
      const { page, stop } = await showingGraph()
      await page.graph.toggle(entryNamed(page, 'Clean Engineering'))
      await page.graph.toggle(entryNamed(page, 'Ticket'))
      await page.graph.select(entryNamed(page, 'activate'))
      await settled()
      stop()
      expect([page.state.reads.rules, page.state.file?.violations]).toEqual([false, []])
    })
  })
})

describe('Go To A Fold-out File', () => {
  describe("with close's fold-out open under Delete Ticket's When step", () => {
    const CLOSE_FOLD_OUT = { id: 'ticket-close', kind: 'call', line: 317, title: 'Ticket.close', path: 'kanban/ticket.py', startLine: 538, endLine: 555, text: '' } as const

    it('should open ticket.py at the lines close covers when the Person chooses Go to file on it', async () => {
      const { page, stop } = await showingGraph()
      await page.graph.goToFile(CLOSE_FOLD_OUT)
      await settled()
      stop()
      expect([page.state.openPath, page.linesShownIn(TICKET_CODE)]).toEqual([TICKET_CODE, [{ start: 538, end: 555 }]])
    })
  })

  describe("with a story map story's scenarios section open under its line", () => {
    const SECTION_FOLD_OUT = { id: `${STORY_MAP}:315`, kind: 'section', line: 4, title: 'Delete Ticket', path: STORY_MAP, startLine: 315, endLine: 319, text: '' } as const

    it('should open the file the section is in, at its lines', async () => {
      const { page, stop } = await showingGraph()
      await page.graph.goToFile(SECTION_FOLD_OUT)
      await settled()
      stop()
      expect([page.state.openPath, page.linesShownIn(STORY_MAP)]).toEqual([STORY_MAP, [{ start: 315, end: 319 }]])
    })
  })
})

describe('See Rules Under Node', () => {
  describe("with Ticket open in checkout-flow's graph", () => {
    async function ticketOpen() {
      const shown = await showingGraph()
      await shown.page.graph.toggle(entryNamed(shown.page, 'Clean Engineering'))
      await shown.page.graph.toggle(entryNamed(shown.page, 'Ticket'))
      shown.stop()
      return shown
    }
    const rulesView = (page: FilesPage) => render(createElement(FilesGraphView, { page }))

    it("should offer to open activate, which holds nothing below it but its rules", async () => {
      const { page } = await ticketOpen()
      const view = rulesView(page)
      expect(view.queryByRole('button', { name: 'Open activate' })).not.toBeNull()
      view.unmount()
    })

    it('should list the passing, broken and prompt rules of activate once the Person opens them', async () => {
      const { page } = await ticketOpen()
      const view = rulesView(page)
      fireEvent.click(view.getByRole('button', { name: 'Open activate' }))
      fireEvent.click(view.getByRole('button', { name: 'Open rules' }))
      const shown = view.getAllByTitle(/^Rule /).map(rule => [rule.querySelector('.node-name')?.textContent, rule.className.includes('violating') ? 'violating' : rule.className.includes('passing') ? 'passing' : 'prompt'])
      expect(shown).toEqual([['keep-operations-small-focused', 'violating'], ['use-intention-revealing-names', 'passing'], ['hide-inner-details', 'prompt']])
      view.unmount()
    })

    it('should mark activate in the tree as breaking a rule, and close as not', async () => {
      const { page } = await ticketOpen()
      const view = rulesView(page)
      const marked = view.getAllByTitle(/^Operation /).map(node => [node.querySelector('.node-name')?.textContent, node.className.includes('tree-violating')])
      expect(marked).toEqual([['activate', true], ['close', false]])
      view.unmount()
    })

    it('should show Ticket by the label the graph gives it', async () => {
      const { page } = await ticketOpen()
      const view = rulesView(page)
      const shown = view.getByTitle(/^Class Ticket/).querySelector('.node-name')?.textContent
      view.unmount()
      expect(shown).toBe('Ticket (ticket.py)')
    })

    it("should name Ticket's label in the title a hover shows", async () => {
      const { page } = await ticketOpen()
      const view = rulesView(page)
      const title = view.getByTitle(/^Class Ticket/).getAttribute('title')
      view.unmount()
      expect(title).toBe('Class Ticket (ticket.py)')
    })

    it("should show the broken rule's message when the Person hovers over it", async () => {
      const { page } = await ticketOpen()
      const view = rulesView(page)
      fireEvent.click(view.getByRole('button', { name: 'Open activate' }))
      fireEvent.click(view.getByRole('button', { name: 'Open rules' }))
      expect(view.getByTitle(/^Rule keep-operations-small-focused/).getAttribute('title')).toBe('Rule keep-operations-small-focused: activate runs 24 statements')
      view.unmount()
    })
  })
})

describe('Open Violation In Files App Source', () => {
  describe("with activate's rules open in checkout-flow's graph", () => {
    it('should open ticket.py at lines 460 to 465 when the Person selects the broken rule', async () => {
      const { page, stop } = await showingGraph()
      await page.graph.toggle(entryNamed(page, 'Clean Engineering'))
      await page.graph.toggle(entryNamed(page, 'Ticket'))
      await page.graph.selectRule(entryNamed(page, 'activate'), ACTIVATE_RULES[0]!)
      await settled()
      stop()
      expect([page.state.openPath, page.linesShownIn(TICKET_CODE)]).toEqual([TICKET_CODE, [{ start: 460, end: 465 }]])
    })

    // Found on 2026-11-22 (e2e tier): a rule that requires a judge lists a candidate, and the graph view treated it as a
    // rule that found nothing: no message on hover, and selecting it opened the node, not the candidate's lines.
    describe('with a rule that requires a judge listing activate as a candidate', () => {
      it("should open ticket.py at the candidate's lines, 462 to 463, when the Person selects the rule", async () => {
        const { page, stop } = await showingGraph()
        await page.graph.toggle(entryNamed(page, 'Clean Engineering'))
        await page.graph.toggle(entryNamed(page, 'Ticket'))
        await page.graph.selectRule(entryNamed(page, 'activate'), ACTIVATE_CANDIDATE)
        await settled()
        stop()
        expect([page.state.openPath, page.linesShownIn(TICKET_CODE)]).toEqual([TICKET_CODE, [{ start: 462, end: 463 }]])
      })

      it("should show the candidate's message when the Person hovers over the rule", () => {
        expect(ruleTitleOf(ACTIVATE_CANDIDATE)).toBe('Rule use-intention-revealing-names: activate may not say why it exists')
      })

      it('should count as a rule that found something there', () => {
        expect(isFailing(ACTIVATE_CANDIDATE)).toBe(true)
      })
    })
  })
})

describe('Fix Graph Violations From Files App', () => {
  describe("with activate's broken rule shown in checkout-flow's graph, opened from chat-1", () => {
    async function activateShown() {
      const shown = await showingGraph()
      await shown.page.graph.toggle(entryNamed(shown.page, 'Clean Engineering'))
      await shown.page.graph.toggle(entryNamed(shown.page, 'Ticket'))
      shown.stop()
      return shown
    }
    const fixAsked = (server: FakeFilesServer) => server.posts.filter(post => post.path.endsWith('/graph-fix-prompt')).map(post => post.body)
    const filledIn = (server: FakeFilesServer) => server.posts.filter(post => post.path === '/chat/chat-1/send' && post.body.kind === 'fill').map(post => post.body.text)

    it('should ask Python for the fix of the rule on activate alone when the Person fixes this one', async () => {
      const { page, server } = await activateShown()
      await page.graph.fix({ rule: 'keep-operations-small-focused', nodeId: 'ticket-activate' })
      expect(fixAsked(server)).toEqual([expect.objectContaining({ rule: 'keep-operations-small-focused', node_id: 'ticket-activate' })])
    })

    it('should ask Python for the fix of the rule on every node the view shows when the Person fixes the rule', async () => {
      const { page, server } = await activateShown()
      await page.graph.fix({ rule: 'keep-operations-small-focused' })
      expect(fixAsked(server)).toEqual([expect.objectContaining({ rule: 'keep-operations-small-focused', node_id: '' })])
    })

    it('should ask Python for the fix of every rule the view shows broken, for the files listed, when the Person fixes all', async () => {
      const { page, server } = await activateShown()
      await page.graph.fix()
      expect(fixAsked(server)).toEqual([expect.objectContaining({ paths: page.graph.paths, rule: '', node_id: '' })])
    })

    it("should fill chat-1's prompt with the fix Python wrote, and answer that it was sent", async () => {
      const { page, server } = await activateShown()
      const outcome = await page.graph.fix()
      expect([filledIn(server), outcome]).toEqual([[FIX_PROMPT], { isSent: true, words: 'Sent to chat' }])
    })

    it('should offer Fix this one and Fix rule beside the broken rule, and Fix all on the view', async () => {
      const { page } = await activateShown()
      const view = render(createElement(FilesGraphView, { page }))
      fireEvent.click(view.getByRole('button', { name: 'Open activate' }))
      fireEvent.click(view.getByRole('button', { name: 'Open rules' }))
      expect([view.getAllByTestId('graph-fix-one').length, view.getAllByTestId('graph-fix-rule').length, view.getAllByTestId('graph-fix-all').length]).toEqual([1, 1, 1])
      view.unmount()
    })

    describe('with the rule no longer broken where the view shows it', () => {
      it('should send nothing, answer that it was not sent, and say why', async () => {
        const server = new FakeFilesServer()
        server.fixPrompt = ''
        const shown = await showingGraph(server)
        const outcome = await shown.page.graph.fix({ rule: 'keep-operations-small-focused' })
        shown.stop()
        expect([filledIn(server), outcome, shown.page.state.toasts.some(toast => toast.includes('no longer shows keep-operations-small-focused broken'))]).toEqual([[], { isSent: false, words: 'Not sent' }, true])
      })
    })
  })
})
