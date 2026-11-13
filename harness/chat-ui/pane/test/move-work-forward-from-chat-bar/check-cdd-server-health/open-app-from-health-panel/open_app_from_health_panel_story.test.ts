import { expect, test } from 'claude-code/testing'

// Epic: Move Work Forward From Chat Bar
// Sub-epic: Check CDD Server Health
// Map: ../../../../../../.context/stories/story-map.md#s-person----open-app-from-health-panel
// Realizations: inline under each step, along the mod's line: PartsView press -> openApp($, app) -> board server or the
// repository's start scripts -> the Claude desktop app's browser pane

// The engine beneath the mod: cdd answers server-health.report with `health`; anything else cdd is asked is refused, so
// the chat bar shows its problem line and the panel still draws. The board answers once it has been started, when
// `isBoardUp` is false at first. The agent is asked to open each URL in the desktop app's browser pane, unless `hasPane`
// is false and the chat takes no prompts. Every tab opened and every process the mod runs or spawns is kept, in order.
type World = {
  health: Record<string, unknown>
  isBoardUp: boolean
  hasPane: boolean
  tabs: string[]
  runs: string[][]
  spawns: string[][]
  toasts: string[]
  started: Record<string, unknown>
}

const REPOSITORY = '/repo'
const HEALTHY = { kanban_app_port: 8778, kanban_app_url: 'http://127.0.0.1:8778', graph_app_port: 5173, is_hook_server_running: false }
const BOARD_PAGE = `http://127.0.0.1:8778/?project=${encodeURIComponent(REPOSITORY)}`
const OPENER = 'rundll32'

const BAR = {
  plugin: 'cdd-board',
  component: 'AbovePrompt',
  surface: 'desktop',
  props: { hasSurvey: false, isWorking: false, maxRows: 24, bodyColumns: 160, scroll: { offset: 0, bodyRows: 24 }, view: {} },
} as const

const answer = (text: string, isError = false) => ({ value: { content: [{ type: 'text', text }], isError } })

function engine(on: any, health: Record<string, unknown>): World {
  const world: World = { health, isBoardUp: true, hasPane: true, tabs: [], runs: [], spawns: [], toasts: [], started: {} }
  on('command.register', () => ({ value: undefined }))
  on('session.start', (_: unknown, e: { cwd: string }) => ({ cwd: e.cwd }))
  on('session.id', () => ({ value: 'chat-1' }))
  on('session.cwd', () => ({ value: REPOSITORY }))
  on('session.root', () => ({ value: REPOSITORY }))
  on('session.messages', () => ({ value: [] }))
  on('clock.every', () => ({ value: undefined }))
  on('clock.after', () => ({ value: undefined }))
  on('tool.list', () => ({ value: [] }))
  on('tool.call', () => ({ result: {} }))
  on('mcp.call', (_: unknown, e: { tool: string }) => (e.tool === 'server-health.report' ? answer(JSON.stringify(world.health)) : answer(`${e.tool} is not part of this story`, true)))
  on('ui.toast', (_: unknown, e: { text: string }) => {
    world.toasts.push(e.text)
    return { value: undefined }
  })
  on('ui.status', () => ({ value: undefined }))
  on('ui.invalidate', () => ({ value: undefined }))
  on('ui.log', () => ({ value: undefined }))
  // The agent is asked, by a prompt, to open each tab of the desktop app's browser pane; a chat whose prompts cannot be
  // submitted refuses it.
  on('prompt.submit', (_: unknown, e: { text: string }) => {
    const tab = /^Open (\S+) in the browser pane: call mcp__Claude_Browser__preview_start with url \1,/.exec(e.text)
    if (!tab) return { text: e.text }
    if (!world.hasPane) throw new Error('this chat takes no prompts')
    world.tabs.push(tab[1])
    return { text: e.text }
  })
  on('env.get', () => ({ value: undefined }))
  on('http.fetch', () => ({ value: { ok: world.isBoardUp, status: world.isBoardUp ? 200 : 503, text: '' } }))
  // The board and the graph app are installed in the repository's own folder, and it has its own Python.
  on('fs.exists', (_: unknown, e: { path: string }) => ({ value: /node_modules$|dist$|python\.exe$/.test(e.path) }))
  on('process.run', (_: unknown, e: { argv: string[] }) => {
    world.runs.push(e.argv)
    if (e.argv[0] === 'git') return { value: { exitCode: 0, stdout: `${REPOSITORY}/.git\n`, stderr: '' } }
    const script = e.argv[1] ?? ''
    // A start script prints its report, and fails when the server did not come up.
    const report = world.started[script] as { ok?: boolean } | undefined
    if (report) return { value: { exitCode: report.ok === false ? 1 : 0, stdout: JSON.stringify(report), stderr: '' } }
    return { value: { exitCode: 0, stdout: '', stderr: '' } }
  })
  // The board's server answers once it is started, and its loop ends at once here.
  on('process.spawn', async function* (_: unknown, e: { argv: string[] }) {
    world.spawns.push(e.argv)
    world.isBoardUp = true
    return { value: { code: 0, signal: null } }
  })
  return world
}

// The chat starts, one prompt reads the server's health, and the person pins the session card open with the health mark,
// so the server health panel shows its parts.
async function openPanel($: any) {
  await $.session.start({ cwd: REPOSITORY, surface: 'desktop', isInteractive: true })
  await $.prompt.submit({ text: 'look' })
  const ui = await $.ui.mount(BAR)
  await ui.press({ key: 'health-icon' })
  return ui
}

const opened = (world: World) => world.tabs
const openedOutside = (world: World) => world.runs.filter(argv => argv[0] === OPENER).map(argv => argv[2])
const scriptsRun = (world: World) => world.runs.filter(argv => argv[0].endsWith('python.exe')).map(argv => argv[1])

// (S) Person --> Open App From Health Panel
test('Open App From Health Panel › Open the Kanban app while it runs', async ($, on) => {
  // Given the Kanban app is running on port 8778
  const world = engine(on, HEALTHY)
  const ui = await openPanel($)
  // When the Person presses the Kanban app on the server health panel
  // PartsView -> OpenAppView press -> openApp($, 'Kanban app') -> startedBoard($) -> openInBrowserPane -> prompt asking the agent to call preview_start
  await ui.press({ key: 'health-open-kanban-app' })
  // Then the board page for this repository opens in the browser pane
  expect(opened(world)).toEqual([BOARD_PAGE])
  // And nothing was started
  expect(world.spawns).toEqual([])
  await ui.unmount()
})

test('Open App From Health Panel › Start the Kanban app, then open it, when it is not running', async ($, on) => {
  // Given the Kanban app is not running, and cdd says where it answers
  const world = engine(on, { ...HEALTHY, kanban_app_port: null })
  world.isBoardUp = false
  const ui = await openPanel($)
  expect((await ui.find({ type: 'Text', text: 'not running' }))?.text).toBe('not running')
  // When the Person presses the Kanban app on the server health panel
  await ui.press({ key: 'health-open-kanban-app' })
  // Then the board server starts from the repository's own folder
  expect(world.spawns).toEqual([['node', '--import', 'tsx', 'packages/session-board/serve.ts']])
  // And once it answers, the board page opens in the browser pane
  expect(opened(world)).toEqual([BOARD_PAGE])
  await ui.unmount()
})

test('Open App From Health Panel › Open the Graph app while it runs', async ($, on) => {
  // Given the Graph app is running on port 5173
  const world = engine(on, HEALTHY)
  const ui = await openPanel($)
  // When the Person presses the Graph app on the server health panel
  // PartsView -> OpenAppView press -> openApp($, 'Graph app') -> openInBrowserPane -> prompt asking the agent to call preview_start
  await ui.press({ key: 'health-open-graph-app' })
  // Then the Graph app opens in the browser pane, and no start script runs
  expect(opened(world)).toEqual(['http://localhost:5173'])
  expect(scriptsRun(world)).toEqual([])
  await ui.unmount()
})

test('Open App From Health Panel › Start the Graph app, then open it, when it is not running', async ($, on) => {
  // Given the Graph app is not running
  const world = engine(on, { ...HEALTHY, graph_app_port: null })
  world.started = {
    'scripts/start_graph_web.py': { ok: true, ping: 'pong', url: 'http://127.0.0.1:3000', port: 3000 },
    'scripts/start_graph_app.py': { ok: true, ping: 'pong', url: 'http://localhost:5174', port: 5174 },
  }
  const ui = await openPanel($)
  // When the Person presses the Graph app on the server health panel
  // openApp($, 'Graph app') -> python scripts/start_graph_web.py, scripts/start_graph_app.py -> openInBrowserPane -> prompt asking the agent to call preview_start
  await ui.press({ key: 'health-open-graph-app' })
  // Then its web server and its app start, with the repository's Python, in that order
  expect(scriptsRun(world)).toEqual(['scripts/start_graph_web.py', 'scripts/start_graph_app.py'])
  // And the Graph app opens where its start script says it answers
  expect(opened(world)).toEqual(['http://localhost:5174'])
  // And the Person is told it is starting
  expect(world.toasts).toEqual(['Starting the Graph app.'])
  await ui.unmount()
})

test('Open App From Health Panel › Say why the Graph app did not start', async ($, on) => {
  // Given the Graph app is not running, and its app server does not come up
  const world = engine(on, { ...HEALTHY, graph_app_port: null })
  world.started = {
    'scripts/start_graph_web.py': { ok: true, ping: 'pong', url: 'http://127.0.0.1:3000', port: 3000 },
    'scripts/start_graph_app.py': { ok: false, ping: 'down', url: null, port: null, log: 'scripts/.run/graph-app.log' },
  }
  const ui = await openPanel($)
  // When the Person presses the Graph app on the server health panel
  await ui.press({ key: 'health-open-graph-app' })
  // Then nothing opens, and the Person is told which script failed and where its log is
  expect(opened(world)).toEqual([])
  expect(world.toasts.at(-1)).toContain('scripts/start_graph_app.py failed, see scripts/.run/graph-app.log')
  await ui.unmount()
})

test('Open App From Health Panel › Say why the app did not open when the agent cannot be asked', async ($, on) => {
  // Given the Graph app is running, and the chat takes no prompts
  const world = engine(on, HEALTHY)
  world.hasPane = false
  const ui = await openPanel($)
  // When the Person presses the Graph app on the server health panel
  // openApp($, 'Graph app') -> openInBrowserPane -> prompt.submit refused
  await ui.press({ key: 'health-open-graph-app' })
  // Then nothing opens anywhere else
  expect(world.tabs).toEqual([])
  expect(openedOutside(world)).toEqual([])
  // And the Person is told where the app is and why it did not open
  expect(world.toasts.at(-1)).toContain('The Graph app is at http://localhost:5173 but did not open: the agent could not be asked to open it in the browser pane')
  await ui.unmount()
})
