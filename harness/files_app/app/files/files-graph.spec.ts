// The Files app's acceptance tests for its graph view, story by story as
// harness/.context/stories/review-generated-work-in-file-viewer/switch-files-app-between-files-and-graph/switch_files_app_between_files_and_graph_story.test.md
// writes them; what the session's graph answers is proved by space/session/session_graph_view_spec.py.
import { describe, expect, it } from 'vitest'

import type { CddApi } from '@cdd/cdd-shared'
import type { ExplorerEntryData, GuidanceSelectionData } from '@cdd/space/session/session'
import { foldsAround } from '@source-view/SourceView'

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
const STORY_MAP = 'harness/.context/stories/story-map.md'
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
// graph_branch and graph_node_range do: only the nodes read from the files a call names, each root opened one level and
// every entry below it closed, its own entries left out.
class FakeFilesServer implements CddApi {
  readonly posts: { path: string; body: Record<string, unknown> }[] = []
  version = 0
  stages = ['discovery', 'implementation']
  practices = ['stories', 'clean_engineering']
  private readonly waiting: (() => void)[] = []

  async post<Result>(path: string, body: Record<string, unknown> = {}): Promise<Result | null> {
    this.posts.push({ path, body })
    if (path.endsWith('/guidance-selection')) return this.selection() as Result
    if (path.endsWith('/update-guidance-selection')) return this.update(body) as Result
    if (path.endsWith('/guidance-selection-after')) return (await this.after(Number(body.version))) as Result
    if (path.endsWith('/fidelity-files')) return {} as Result
    if (path.endsWith('/root-files')) return CHECKOUT_FLOW_FILES as Result
    if (path.endsWith('/graph-trees')) return this.trees(body.paths as string[]) as Result
    if (path.endsWith('/graph-branch')) return this.entry(this.node(String(body.node_id)), body.paths as string[], true) as Result
    if (path.endsWith('/graph-node-range')) return this.range(String(body.node_id)) as Result
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

  private range(id: string) {
    const node = this.node(id)
    return node.file ? { path: node.file, start_line: node.start, end_line: node.end, content: '', anchor: `${node.file}:${node.start}-${node.end}` } : null
  }

  posted(ending: string): { path: string; body: Record<string, unknown> }[] {
    return this.posts.filter(post => post.path.endsWith(ending))
  }
}

const LINK = '?files=checkout-flow&fidelity=stories-story-map,clean-engineering-code&chat=chat-1'

async function settled(): Promise<void> {
  for (let turn = 0; turn < 8; turn += 1) await new Promise(resolve => setTimeout(resolve, 0))
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
  // ticket.py's folds as the source view lays them: Ticket whole, and each of its operations as a block.
  const TICKET_FOLDS = [
    { glyph: 106, start: 107, end: 670, kind: 'class' as const },
    { glyph: 460, start: 461, end: 465, kind: 'block' as const },
    { glyph: 538, start: 539, end: 555, kind: 'block' as const },
  ]

  describe('with Ticket.activate selected and ticket.py open', () => {
    it('should unfold the lines of Ticket.activate and Ticket, and leave Ticket.close folded', () => {
      expect(foldsAround(TICKET_FOLDS, [{ start: 460, end: 465 }])).toEqual(['class:107:670', 'block:461:465'])
    })

    it('should unfold Ticket.close too once the Person also selects it, and keep every other operation folded', async () => {
      const { page, stop } = await showingGraph()
      await page.graph.toggle(entryNamed(page, 'Clean Engineering'))
      await page.graph.toggle(entryNamed(page, 'Ticket'))
      await page.graph.select(entryNamed(page, 'activate'))
      await page.graph.select(entryNamed(page, 'close'), true)
      await settled()
      stop()
      const around = page.selectedLinesIn(TICKET_CODE)
      expect([around, foldsAround(TICKET_FOLDS, around)]).toEqual([
        [
          { start: 460, end: 465 },
          { start: 538, end: 555 },
        ],
        ['class:107:670', 'block:461:465', 'block:539:555'],
      ])
    })
  })
})
