// The Files app's acceptance tests for its graph view, story by story as
// story_tests/review-generated-work-in-file-viewer/switch-files-app-between-files-and-graph/switch_files_app_between_files_and_graph_story.test.md
// writes them; what the session's graph answers is proved by the sub-epic's story tests in story_tests/review-generated-work-in-file-viewer/.
import { describe, expect, it } from 'vitest'

import type { CddApi } from '@cdd/cdd-shared'
import type { ExplorerEntryData, GuidanceSelectionData } from '@cdd/space/session/session'

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

// Seed: checkout-flow's nodes, each in its file at its lines, under its practice's root.
type SeedNode = { id: string; name: string; type: string; file: string; start: number; end: number; parent: string }
const CHECKOUT_FLOW_NODES: SeedNode[] = [
  { id: 'stories', name: 'Stories', type: 'Practice', file: '', start: 0, end: 0, parent: '' },
  { id: 'delete-ticket', name: 'Delete Ticket', type: 'Story', file: STORY_MAP, start: 315, end: 319, parent: 'stories' },
  { id: 'clean_engineering', name: 'Clean Engineering', type: 'Practice', file: '', start: 0, end: 0, parent: '' },
  { id: 'ticket', name: 'Ticket', type: 'OoadClass', file: TICKET_CODE, start: 106, end: 670, parent: 'clean_engineering' },
  { id: 'ticket-activate', name: 'activate', type: 'Operation', file: TICKET_CODE, start: 460, end: 465, parent: 'ticket' },
  { id: 'ticket-close', name: 'close', type: 'Operation', file: TICKET_CODE, start: 538, end: 555, parent: 'ticket' },
  { id: 'board', name: 'Board', type: 'OoadClass', file: BOARD_CODE, start: 104, end: 397, parent: 'clean_engineering' },
  { id: 'board-reread', name: 'reread', type: 'Operation', file: BOARD_CODE, start: 286, end: 289, parent: 'board' },
]

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
    if (path.endsWith('/guidance-selection')) return this.selection() as Result
    if (path.endsWith('/update-guidance-selection')) return this.update(body) as Result
    if (path.endsWith('/guidance-selection-after')) return (await this.after(Number(body.version))) as Result
    if (path.endsWith('/fidelity-files')) return {} as Result
    if (path.endsWith('/root-files')) return CHECKOUT_FLOW_FILES as Result
    if (path.endsWith('/graph-trees')) return (await this.heldTrees(body.paths as string[])) as Result
    if (path.endsWith('/graph-filter-choices')) return this.choices(body.node_types as string[]) as Result
    if (path.endsWith('/graph-branch')) return this.entry(this.node(String(body.node_id)), body.paths as string[], true) as Result
    if (path.endsWith('/graph-node-ranges')) return this.ranges(this.node(String(body.node_id)), body.paths as string[]) as Result
    if (path.endsWith('/graph-members')) return CHECKOUT_FLOW_NODES.filter(node => node.file).map(node => ({ node_id: node.id, name: node.name, type: node.type, file: node.file })) as Result
    if (path.endsWith('/cdd/progress')) return this.progress.map(message => ({ tool: 'session.graph_trees', message })) as Result
    if (path.endsWith('/file')) return { path: body.path, text: 'line\n'.repeat(700), language: 'python', comments: [], folds: [], violations: [], changes: [] } as Result
    return null
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
      practices: PRACTICES.map(practice => ({ ...practice, is_selected: this.practices.includes(practice.key) })),
      formats: [],
      fidelities,
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
    if (!isOpened) return { node_id: node.id, name: node.name, type: node.type, children: [], children_left_out: below.length }
    return { node_id: node.id, name: node.name, type: node.type, children: below.map(child => this.entry(child, paths, false)), children_left_out: 0 }
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
      await page.guidance.togglePractice('clean_engineering')
      await settled()
      stop()
      expect(treeNames(page)).toEqual(['Stories'])
    })

    it('should list only story-map.md when switched back to the files', async () => {
      const { page, stop } = await showingGraph()
      await page.guidance.togglePractice('clean_engineering')
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
      expect([page.state.openPath, page.selectedLinesIn(TICKET_CODE)]).toEqual([TICKET_CODE, [{ start: 460, end: 465 }]])
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
      expect(page.selectedLinesIn(TICKET_CODE)).toEqual([
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
      expect([page.state.openPath, page.state.moreFiles.map(file => file.path), page.selectedLinesIn(BOARD_CODE)]).toEqual([TICKET_CODE, [BOARD_CODE], [{ start: 104, end: 397 }]])
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
