import { expect, test } from 'claude-code/testing'

// Organised by story. A test whose name starts `should` has the same signature as a Mamba example in
// harness/kanban/kanban_tools_spec.py; the others cover layout and interaction, which Mamba cannot see.
const SURFACES = ['terminal', 'desktop', 'vscode', 'mobile'] as const

const PANE = {
  plugin: 'cdd-board',
  component: 'Pane',
  requestId: 'cdd-board',
  props: {
    title: 'Board',
    isFocused: false,
    bodyColumns: 120,
    placement: 'dock',
    scroll: { offset: 0, bodyRows: 40 },
    view: {},
  },
} as const

const BAND = {
  plugin: 'cdd-board',
  component: 'AbovePrompt',
  props: { hasSurvey: false, isWorking: false, maxRows: 3, bodyColumns: 120 },
} as const

const CDD_TOOLS = Array.from({ length: 116 }, (_, index) => ({ name: `mcp__cdd__tool_${index}`, description: '', mcp: true }))
const DONE_ACTIONS = { generate: 'done', validate: 'done', review: 'done' }
const NO_ACTIONS = { generate: 'to_do', validate: 'to_do', review: 'to_do' }

const ticket = (name: string, title: string, column: string, next: string | null, progress: Record<string, string>, overrides = {}) => ({
  name,
  title,
  scope: 'feature',
  parent: '',
  column,
  is_done: next === null,
  can_move_next: column !== 'Complete',
  next,
  next_action: next ? 'generate' : '',
  last_activity: '2026-10-31T05:00:00Z',
  handoff: `.sessions/${name}/handoff-20261031T0412.md`,
  reports: {} as Record<string, string>,
  violation_counts: {} as Record<string, number>,
  practices: { stories: true, ddd: true, ux: true, clean_engineering: true, bdd: true } as Record<string, boolean>,
  progress,
  actions: { 'stories-scenarios': DONE_ACTIONS, 'ux-mockup': NO_ACTIONS } as Record<string, unknown>,
  allowed_actions: { 'stories-scenarios': ['generate', 'validate', 'review'], 'ux-mockup': ['generate'], 'stories-story_map': ['generate'] } as Record<string, string[]>,
  ...overrides,
})

const PET_VISITS = ticket('pet-visits', 'Pet visits', 'Specification', 'ux-mockup', { 'stories-scenarios': 'done', 'ux-mockup': 'violations' }, {
  next_action: 'satisfy',
  reports: { 'ux-mockup': '.sessions/pet-visits/validation-reports/ux-mockup-1.md' },
  actions: { 'stories-scenarios': DONE_ACTIONS, 'ux-mockup': { generate: 'done', validate: 'in_progress', review: 'to_do' } },
})
const SIGN_UP = ticket('sign-up', 'Sign up', 'Discovery', 'ddd-bounded_context', { 'stories-story_map': 'done' })
const LOYALTY = ticket('loyalty', 'Loyalty points', 'Discovery', null, { 'stories-story_map': 'done' })
const SPRINT_OPEN = ticket('sprint-a', 'Sprint A', 'Discovery', 'stories-story_map', {})
const SPRINT_CLOSED = { ...ticket('sprint-a', 'Sprint A', 'Complete', null, {}), is_done: false, handoff: '' }

const FORMATS = { 'stories-story_map': ['markdown', 'drawio'], 'ddd-bounded_context': ['markdown'], 'stories-scenarios': ['markdown'], 'ux-mockup': ['html'] }
const DEFAULT_FORMATS = { 'stories-story_map': 'markdown', 'ddd-bounded_context': 'markdown', 'stories-scenarios': 'markdown', 'ux-mockup': 'html' }

const ITEM = { title: 'Returns and refunds', text: 'An idea.', path: '.sessions/_backlog/returns.md', last_activity: '2026-10-30T05:00:00Z' }

const boardOf = (overrides: { active?: string | null; tickets?: unknown[] } = {}) => ({
  project: 'abd-pet-store-demo',
  active: overrides.active === undefined ? 'pet-visits' : overrides.active,
  columns: [
    { name: 'Backlog', items: [ITEM] },
    {
      name: 'Discovery',
      work_required: ['stories-story_map', 'ddd-bounded_context'],
      formats: FORMATS,
      default_formats: DEFAULT_FORMATS,
      wip_limit: 3,
      is_over_limit: false,
      in_progress: [SIGN_UP, SPRINT_OPEN],
      done: [LOYALTY],
    },
    { name: 'Specification', work_required: ['stories-scenarios', 'ux-mockup'], formats: FORMATS, default_formats: DEFAULT_FORMATS, wip_limit: 3, is_over_limit: false, in_progress: [PET_VISITS], done: [] },
    { name: 'Implementation', work_required: [], formats: {}, wip_limit: 3, is_over_limit: false, in_progress: [], done: [] },
    { name: 'Complete', tickets: [SPRINT_CLOSED] },
  ],
})

const REPORT = {
  path: '.sessions/pet-visits/validation-reports/ux-mockup-1.md',
  text: '# Report',
  rules: [
    {
      fidelity: 'ux-mockup',
      name: 'verb-noun-format',
      description: 'Name every story with a verb and a noun.',
      count: 2,
      violations: [
        {
          location: 'docs/map.md',
          line: 12,
          message: 'Name the story with a verb',
          source: [{ number: 11, text: '## Payment' }, { number: 12, text: '- Payment' }, { number: 13, text: '' }],
        },
      ],
    },
  ],
  has_saved_graph: true,
}

const REPORT_WITHOUT_SOURCE = {
  ...REPORT,
  rules: [{ ...REPORT.rules[0]!, violations: [{ location: 'unknown', line: null, message: 'Name the story with a verb', source: [] }] }],
}

const TICKET_VIOLATIONS = {
  ...REPORT,
  path: '.sessions/pet-visits/validation-reports',
  rules: [...REPORT.rules, { ...REPORT.rules[0]!, fidelity: 'stories-scenarios', name: 'one-outcome' }],
}

const HELP = {
  practice: 'stories',
  fidelity: 'story_map',
  stage: 'Discovery',
  overview: 'Map the work.',
  guidance: 'Use verbs.',
  rules: [{ slug: 'verb-noun-format', text: 'Name it.' }],
  href: 'https://forge.abdworks.net/abd-context-driven-delivery/fidelities/stories-story_map.html',
}

const PRACTICE_HELP = { ...HELP, fidelity: '', stage: '' }

const FILES = {
  'stories-story_map': { markdown: [{ path: 'docs/story-map.md', exists: true }], drawio: [{ path: 'docs/story-map.drawio', exists: false }] },
  'stories-scenarios': { markdown: [{ path: 'docs/scenarios.md', exists: false }] },
  'ux-mockup': { html: [{ path: 'docs/mockup.html', exists: true }] },
}

const answer = (body: unknown) => ({ value: { content: [{ type: 'text', text: JSON.stringify(body) }], isError: false } })

type Call = { tool: string; args: any }

type Engine = {
  calls: Call[]
  statuses: (string | undefined)[]
  fills: string[]
  sent: string[]
  toasts: string[]
  answers: Record<string, unknown>
  rawText: Record<string, string>
  board: unknown
  commandFails: boolean
  serverLost: boolean
  paneOpening: { isPlaced: true } | { isPlaced: false; reason: string }
}

// Stands for the engine and the cdd server. A tool answers from `answers`, and board.show answers `board`, which a
// test changes to show what the server would return after a tool ran.
const engine = (on: any, board: unknown = boardOf()): Engine => {
  const stub: Engine = { calls: [], statuses: [], fills: [], sent: [], toasts: [], answers: {}, rawText: {}, board, commandFails: false, serverLost: false, paneOpening: { isPlaced: true } }
  on('command.register', () => ({ value: { command: 'board' } }))
  on('ui.open', () => ({ value: stub.paneOpening }))
  on('ui.status', (_: unknown, e: { text: string | undefined }) => {
    stub.statuses.push(e.text)
    return { value: undefined }
  })
  on('ui.toast', (_: unknown, e: { text: string }) => {
    stub.toasts.push(e.text)
    return { value: undefined }
  })
  on('ui.invalidate', () => ({ value: undefined }))
  on('prompt.fill', (_: unknown, e: { text: string }) => {
    stub.fills.push(e.text)
    return { isFilled: true }
  })
  on('prompt.submit', (_: unknown, e: { text: string }) => ({ text: e.text }))
  on('command.run', (_: unknown, e: { command: string; args: string }) => {
    if (stub.commandFails) throw new Error(`no command named /${e.command} in this session`)
    stub.sent.push(`/${e.command} ${e.args}`.trim())
    return { value: { text: '' } }
  })
  on('clock.now', () => ({ value: Date.parse('2026-10-31T05:04:00Z') }))
  // A timer that never comes due: a test ends before one would fire.
  on('clock.after', () => new Promise(() => undefined))
  on('tool.list', () => ({ value: CDD_TOOLS }))
  on('mcp.call', (_: unknown, e: { tool: string; args: unknown }) => {
    stub.calls.push({ tool: e.tool, args: e.args })
    if (stub.serverLost) throw new Error('no connected MCP tool on a server named "cdd"')
    const raw = stub.rawText[e.tool]
    if (raw !== undefined) return { value: { content: [{ type: 'text', text: raw }], isError: false } }
    if (stub.board === null) return { value: { content: [], isError: true } }
    const found = e.tool === 'board.show' ? stub.board : stub.answers[e.tool]
    return answer(found === undefined ? PET_VISITS : found)
  })
  on('session.start', (_: unknown, e: { cwd: string }) => ({ cwd: e.cwd }))
  return stub
}

const start = ($: any) => $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })

const mount = async ($: any, surface: (typeof SURFACES)[number] = 'desktop', props: object = {}) =>
  $.ui.mount({ ...PANE, surface, props: { ...PANE.props, ...props } })

const called = (stub: Engine, tool: string) => stub.calls.find(call => call.tool === tool)?.args

const findText = (ui: any, text: RegExp | string) => ui.find({ type: 'Text', text })

const openViolations = (ui: any) => ui.press({ key: 'violations-Specification/pet-visits/ux-mockup' })

const pressCard = (ui: any, address: string) => ui.pointer({ type: 'down', x: 9, y: 1, button: 'left', in: `face-${address}` })

// Pressed through a Button surface, so the Buttons a Client holds on the desktop are reached the same way.
const openBoard = async ($: any, on: any, board?: unknown) => {
  const stub = engine(on, board ?? boardOf({ active: 'pet-visits' }))
  await start($)
  const ui = await mount($, 'vscode')
  return { stub, ui }
}

const turnOffOnlyActive = (ui: any) => ui.press({ key: 'only-active' })

// (E) Display Board And Details For Repo

// (S) Person --> Open Board
test('the /board command opens the pane and reads the board', async ($, on) => {
  const stub = engine(on)
  await start($)
  stub.calls.length = 0

  const ran = await $.command.run({ command: 'board', args: '' })

  expect(ran.text).toBe('Board opened.')
  expect(stub.calls[0]?.tool).toBe('board.show')
})

test('with no surface to draw the pane, the /board command says why', async ($, on) => {
  const stub = engine(on)
  await start($)
  stub.paneOpening = { isPlaced: false, reason: 'no surface attached' }

  const ran = await $.command.run({ command: 'board', args: '' })

  expect(ran.text).toBe('Board not drawn: no surface attached')
})

// (S) Board Pane --> Display Board
test('should return every column of the board', async ($, on) => {
  engine(on)
  await start($)

  for (const surface of SURFACES) {
    const ui = await mount($, surface)
    for (const name of ['BACKLOG', 'DISCOVERY', 'SPECIFICATION', 'IMPLEMENTATION', 'COMPLETE']) {
      expect((await findText(ui, new RegExp(`^${name}$`)))?.text).toBe(name)
    }
    await ui.unmount()
  }
})

test('every column shows the tickets in it, on every surface', async ($, on) => {
  engine(on)
  await start($)

  for (const surface of SURFACES) {
    const ui = await mount($, surface)
    expect(await ui.find({ key: 'card-Specification/pet-visits' })).toBeDefined()
    expect(await ui.find({ key: 'card-Backlog/Returns and refunds' })).toBeDefined()
    await ui.unmount()
  }
})

test('should name the project the board belongs to', async ($, on) => {
  engine(on)
  await start($)
  const ui = await mount($)

  expect((await findText(ui, /tickets/))?.text).toMatch(/^abd-pet-store-demo · 4 tickets · active: /)
  await ui.unmount()
})

test('with the cdd server not connected, the status line says so and the pane asks for it', async ($, on) => {
  const statuses: (string | undefined)[] = []
  on('command.register', () => ({ value: { command: 'board' } }))
  on('ui.open', () => ({ value: { isPlaced: true } }))
  on('ui.status', (_: unknown, e: { text: string | undefined }) => {
    statuses.push(e.text)
    return { value: undefined }
  })
  on('mcp.call', () => {
    throw new Error('no connected MCP tool "board.show" on a server named "cdd"')
  })
  on('session.start', (_: unknown, e: { cwd: string }) => ({ cwd: e.cwd }))

  await start($)
  const ui = await mount($)

  expect(statuses.at(-1)).toMatch(/^cdd board: /)
  expect((await ui.find({ type: 'Text' }))?.text).toBe('No board yet: is the cdd MCP server connected?')
  await ui.unmount()
})

test('with the cdd server lost after the board was read, a band across the pane says so', async ($, on) => {
  const stub = engine(on)
  await start($)
  const ui = await mount($)

  stub.serverLost = true
  await $.prompt.submit({ text: 'next step?' })

  expect((await ui.find({ key: 'server-band' }))?.props?.top).toBe(0)
  expect((await findText(ui, /^cdd server lost/))?.text).toContain('Reconnect it with /mcp')
  await ui.unmount()
})

test('the band goes when the cdd server answers again', async ($, on) => {
  const stub = engine(on)
  await start($)
  const ui = await mount($)
  stub.serverLost = true
  await $.prompt.submit({ text: 'next step?' })

  stub.serverLost = false
  await $.prompt.submit({ text: 'next step?' })

  expect(await ui.find({ key: 'server-band' })).toBeUndefined()
  await ui.unmount()
})

test('a board read back as words instead of JSON says so', async ($, on) => {
  const stub = engine(on)
  await start($)
  stub.rawText['ticket.report'] = 'Output too large for the conversation.'
  const ui = await mount($, 'vscode')

  await openViolations(ui)

  expect(stub.toasts.at(-1)).toContain('cdd ticket.report sent back what the board cannot read')
  await ui.unmount()
})

test('a prompt sent reads the board again, so a board the cdd server could not give at start appears', async ($, on) => {
  const stub = engine(on, null)
  await start($)
  stub.board = boardOf()
  await $.prompt.submit({ text: 'next step?' })

  expect(stub.statuses.at(-1)).toBe('pet-visits · Specification · next: ux-mockup · 1 violation')
})

test('a cdd tool call that finishes reads the board again', async ($, on) => {
  const stub = engine(on)
  on('tool.call', () => ({ result: {} }))
  await start($)
  stub.calls.length = 0

  await $.tool.call({ tool: 'mcp__cdd__session_switch' } as never)

  expect(stub.calls.some(call => call.tool === 'board.show')).toBe(true)
})

test('a ticket that moves raises a toast naming its new column', async ($, on) => {
  const stub = engine(on)
  await start($)
  stub.board = boardOf({ active: null })
  const moved = { ...SIGN_UP, column: 'Specification' }
  const board = boardOf()
  board.columns[2]!.in_progress = [PET_VISITS, moved]
  board.columns[1]!.in_progress = [SPRINT_OPEN]
  stub.board = board

  await $.prompt.submit({ text: 'next step?' })

  expect(stub.toasts).toEqual(['Sign up moved to Specification · In progress'])
})

test('a session open and closed under one name raises no toast on each read of the board', async ($, on) => {
  const stub = engine(on)
  await start($)

  await $.prompt.submit({ text: 'next step?' })

  expect(stub.toasts).toEqual([])
})

// (S) Person --> Arrange Board And Details
test('a drag on the split bar gives the board more rows', async ($, on) => {
  engine(on)
  await start($)
  const ui = await mount($)

  await ui.pointer({ type: 'move', x: 0, y: 6, button: 'left', in: 'split-grip' })

  expect((await ui.find({ key: 'split-grip' }))?.props?.props).toMatchObject({ boardRows: 29 })
  await ui.unmount()
})

test('a drag cannot close either region', async ($, on) => {
  engine(on)
  await start($)
  const ui = await mount($)

  await ui.pointer({ type: 'move', x: 0, y: 500, button: 'left', in: 'split-grip' })

  expect((await ui.find({ key: 'split-grip' }))?.props?.props).toMatchObject({ boardRows: 32 })
  await ui.unmount()
})

test('Expand board gives the whole pane to the board and a second press brings the details back', async ($, on) => {
  engine(on)
  await start($)
  const ui = await mount($)

  await ui.press({ key: 'expand-board' })
  expect(await ui.find({ key: 'detail' })).toBeUndefined()

  await ui.press({ key: 'expand-board' })
  expect(await ui.find({ key: 'detail' })).toBeDefined()
  await ui.unmount()
})

test('Expand details gives the whole pane to the details', async ($, on) => {
  engine(on)
  await start($)
  const ui = await mount($)

  await ui.press({ key: 'expand-details' })

  expect(await ui.find({ key: 'columns' })).toBeUndefined()
  await ui.unmount()
})

// (S) Board Pane --> Display Backlog Items As Tickets
test('should say when a backlog item last changed', async ($, on) => {
  engine(on)
  await start($)
  const ui = await mount($)

  expect((await ui.find({ key: 'face-Backlog/Returns and refunds' }))?.props?.props.meta).toBe('yesterday')
  await ui.unmount()
})

test('should give a backlog item its text', async ($, on) => {
  const { ui } = await openBoard($, on)

  await ui.press({ key: 'item-Returns and refunds' })

  expect((await findText(ui, /^An idea\.$/))?.text).toBe('An idea.')
  await ui.unmount()
})

// (S) Board Pane --> Display Ticket Card
test('a card says how long ago its ticket was worked on', async ($, on) => {
  engine(on)
  await start($)
  const ui = await mount($)

  expect((await ui.find({ key: 'face-Specification/pet-visits' }))?.props?.props).toMatchObject({
    meta: '4 min ago',
  })
  await ui.unmount()
})

test('a card shows each enabled practice as a block and dims work not started', async ($, on) => {
  engine(on)
  await start($)
  const ui = await mount($)

  const drawn = JSON.stringify(await ui.find({ key: 'card-Discovery/sign-up' }))
  expect(drawn).toContain('#6bcb77')
  expect(drawn).toContain('#23203d')
  await ui.unmount()
})

test('a card shows the skill of the practice under the pointer', async ($, on) => {
  engine(on)
  await start($)
  const ui = await mount($)

  const drawn = JSON.stringify(await ui.find({ key: 'card-Discovery/sign-up' }))

  expect(drawn).toContain('"display":"flex"')
  expect(drawn).toContain('/practices-ddd-ddd-bounded-context')
  await ui.unmount()
})

test('the active ticket has a thick orange outline', async ($, on) => {
  engine(on)
  await start($)
  const ui = await mount($)

  expect((await ui.find({ key: 'card-Specification/pet-visits' }))?.props).toMatchObject({ borderStyle: 'bold', borderColor: '#E5531A' })
  await ui.unmount()
})

test('the status line names the active ticket, its stage, its next guidance, and its violations', async ($, on) => {
  const stub = engine(on)
  await start($)

  expect(stub.statuses.at(-1)).toBe('pet-visits · Specification · next: ux-mockup · 1 violation')
})

// (S) Board Pane --> Display Ticket Details
test('with no card pressed, the active ticket\'s detail shows with its fidelities, states, and latest handoff', async ($, on) => {
  engine(on)
  await start($)
  const ui = await mount($)

  expect((await findText(ui, /^Pet visits pet-visits/))?.text).toBe('Pet visits pet-visits · feature · Specification · in progress')
  expect((await ui.find({ key: 'tile-Specification/pet-visits/ux-mockup' }))?.props?.props).toMatchObject({ label: 'mockup' })
  expect(await ui.find({ key: 'violations-Specification/pet-visits/ux-mockup' })).toBeDefined()
  expect((await findText(ui, /^Latest handoff/))?.text).toBe('Latest handoff: .sessions/pet-visits/handoff-20261031T0412.md · Next: ux-mockup, fix violations')
  await ui.unmount()
})

test('the board is no wider than the pane', async ($, on) => {
  const { ui } = await openBoard($, on)

  expect((await ui.find({ key: 'main' }))?.props?.width).toBe(120)
  await ui.unmount()
})

test('the wheel moves the board and leaves the details where they are', async ($, on) => {
  const { ui } = await openBoard($, on)

  await $.ui.scroll({ component: 'Pane', requestId: 'cdd-board', offset: 3, by: 3, bodyRows: 40, contentRows: 60, origin: { kind: 'person' } })

  expect((await ui.find({ key: 'board-rows' }))?.props?.marginTop).toBeLessThan(0)
  expect((await ui.find({ key: 'details-rows' }))?.props?.marginTop).toBe(-0)
  await ui.unmount()
})

test('a card opens level with where it sits in its column', async ($, on) => {
  engine(on)
  await start($)
  const ui = await mount($, 'vscode', { scroll: { offset: 0, bodyRows: 80 } })

  await ui.press({ key: 'expand-Discovery/sign-up' })
  const first = (await ui.find({ key: 'card-tiles' }))?.props?.top
  await ui.press({ key: 'expand-Discovery/sprint-a' })

  expect((await ui.find({ key: 'card-tiles' }))?.props?.top).toBeGreaterThan(first)
  await ui.unmount()
})

test('the board dims behind the activation dialog', async ($, on) => {
  const { ui } = await openBoard($, on)

  await ui.press({ key: 'activate-Discovery/sign-up' })

  expect((await ui.find({ key: 'backdrop' }))?.props?.backgroundColor).toBe('#0000008C')
  await ui.unmount()
})

test('a press anywhere on a card shows that ticket', async ($, on) => {
  engine(on)
  await start($)
  const ui = await mount($)

  await pressCard(ui, 'Discovery/sign-up')

  expect((await findText(ui, /^Sign up sign-up/))?.text).toBe('Sign up sign-up · feature · Discovery · in progress')
  await ui.unmount()
})

test('a closed session under an open session\'s name can be pressed apart from it', async ($, on) => {
  engine(on)
  await start($)
  const ui = await mount($)

  await pressCard(ui, 'Complete/sprint-a')

  expect((await findText(ui, /^Sprint A sprint-a/))?.text).toBe('Sprint A sprint-a · feature · Complete')
  await ui.unmount()
})

test('on a surface with no surface modules, a card is still pressed to show its ticket', async ($, on) => {
  const { ui } = await openBoard($, on)

  await ui.press({ key: 'ticket-Discovery/sign-up' })

  expect((await findText(ui, /^Sign up sign-up/))?.text).toBeDefined()
  await ui.unmount()
})

test('hovering a status in the details names the skill that does that work', async ($, on) => {
  engine(on)
  await start($)
  const ui = await mount($)

  expect((await ui.find({ type: 'Text', text: '/practices-ux-ux-mockup' }))?.text).toBe('/practices-ux-ux-mockup')
  await ui.unmount()
})

test('a practice with two words in its name keeps them in its skill', async ($, on) => {
  const board = boardOf()
  board.columns[3]!.work_required = ['clean_engineering-code']
  engine(on, board)
  await start($)
  const ui = await mount($)

  expect((await ui.find({ type: 'Text', text: '/practices-clean-engineering-clean-engineering-code' }))?.text).toBe('/practices-clean-engineering-clean-engineering-code')
  await ui.unmount()
})

test('Expand on a card shows its tiles over the closed card', async ($, on) => {
  const { ui } = await openBoard($, on)

  await ui.press({ key: 'expand-Discovery/sign-up' })

  expect(await ui.find({ key: 'card-tiles' })).toBeDefined()
  await ui.unmount()
})

test('an expanded card shows the same tiles as the details', async ($, on) => {
  const { ui } = await openBoard($, on)

  await ui.press({ key: 'expand-Specification/pet-visits' })

  expect(await ui.find({ key: 'toggle-card/Specification/pet-visits/ux-mockup' })).toBeDefined()
  await ui.unmount()
})

test('only one card is expanded at a time', async ($, on) => {
  engine(on)
  await start($)
  const ui = await mount($)

  await ui.press({ key: 'expand-Discovery/sign-up' })
  await ui.press({ key: 'expand-Specification/pet-visits' })

  expect((await ui.find({ key: 'expand-Discovery/sign-up' }))?.props?.label).toBe('▾')
  await ui.unmount()
})

// (S) Person --> Set Stage WIP Limit
test('should give every stage a limit of 3 tickets until a person sets one', async ($, on) => {
  engine(on)
  await start($)
  const ui = await mount($)

  expect((await findText(ui, /^3 \/$/))?.text).toBe('3 /')
  expect((await ui.find({ key: 'wip-limit-Discovery' }))).toBeDefined()
  await ui.unmount()
})

test('should show the stage over its limit', async ($, on) => {
  const stub = engine(on)
  await start($)
  const ui = await mount($)

  await ui.press({ key: 'wip-limit-Discovery' })
  await ui.input({ key: 'wip-input-Discovery', text: '2' })

  expect(called(stub, 'board.set_wip_limit')).toEqual({ stage: 'Discovery', limit: 2 })
  await ui.unmount()
})

test('a limit that is not a number changes nothing', async ($, on) => {
  const stub = engine(on)
  await start($)
  const ui = await mount($)

  await ui.press({ key: 'wip-limit-Discovery' })
  await ui.input({ key: 'wip-input-Discovery', text: 'many' })

  expect(called(stub, 'board.set_wip_limit')).toBeUndefined()
  expect(await ui.find({ key: 'wip-limit-Discovery' })).toBeDefined()
  await ui.unmount()
})

test('on a surface with no Input, the limit steps with Buttons', async ($, on) => {
  const stub = engine(on)
  await start($)
  const ui = await mount($, 'mobile')

  await ui.press({ key: 'wip-less-Discovery' })

  expect(called(stub, 'board.set_wip_limit')).toEqual({ stage: 'Discovery', limit: 2 })
  await ui.unmount()
})

test('a stage over its limit shows its count in red', async ($, on) => {
  const board = boardOf()
  board.columns[1]!.is_over_limit = true
  engine(on, board)
  await start($)
  const ui = await mount($)

  expect((await findText(ui, /^3 \/$/))?.props?.color).toBe('#EF4444')
  await ui.unmount()
})

test('× closes the limit field without changing the limit', async ($, on) => {
  const stub = engine(on)
  await start($)
  const ui = await mount($)

  await ui.press({ key: 'wip-limit-Discovery' })
  await ui.press({ key: 'wip-cancel-Discovery' })

  expect(await ui.find({ key: 'wip-input-Discovery' })).toBeUndefined()
  expect(called(stub, 'board.set_wip_limit')).toBeUndefined()
  await ui.unmount()
})

// (S) Person --> Arrange Side Panel
const openHelpPanel = async (ui: any) => ui.press({ key: 'practice-help-stories' })

test('a drag on a panel\'s left edge sets its width', async ($, on) => {
  const stub = engine(on)
  stub.answers['board.help'] = HELP
  await start($)
  const ui = await mount($)
  await openHelpPanel(ui)

  await ui.pointer({ type: 'move', x: -10, y: 0, button: 'left', in: 'panel-grip-help' })

  expect((await ui.find({ key: 'panel-grip-help' }))?.props?.props).toMatchObject({ width: 70 })
  await ui.unmount()
})

test('a panel cannot be dragged narrower than its smallest width', async ($, on) => {
  const stub = engine(on)
  stub.answers['board.help'] = HELP
  await start($)
  const ui = await mount($)
  await openHelpPanel(ui)

  await ui.pointer({ type: 'move', x: 500, y: 0, button: 'left', in: 'panel-grip-help' })

  expect((await ui.find({ key: 'panel-grip-help' }))?.props?.props).toMatchObject({ width: 30 })
  await ui.unmount()
})

test('an expanded panel takes the board\'s width, and only one is expanded at a time', async ($, on) => {
  const stub = engine(on)
  stub.answers['board.help'] = HELP
  stub.answers['ticket.report'] = REPORT
  await start($)
  const ui = await mount($)
  await openViolations(ui)
  await openHelpPanel(ui)

  await ui.press({ key: 'panel-expand-help' })
  await ui.press({ key: 'panel-expand-report' })

  expect(await ui.find({ key: 'columns' })).toBeUndefined()
  expect((await ui.find({ key: 'panel-expand-help' }))?.props?.label).toBe('⤢')
  await ui.unmount()
})

test('× closes a side panel', async ($, on) => {
  const stub = engine(on)
  stub.answers['board.help'] = HELP
  await start($)
  const ui = await mount($)
  await openHelpPanel(ui)

  await ui.press({ key: 'panel-close-help' })

  expect(await ui.find({ key: 'panel-help' })).toBeUndefined()
  await ui.unmount()
})

test('columns keep their width and scroll sideways when the pane is narrower than the board', async ($, on) => {
  const { ui } = await openBoard($, on)
  const width = (await ui.find({ key: 'column-Discovery' }))?.props?.width

  await ui.press({ key: 'columns-right' })

  expect((await ui.find({ key: 'column-Discovery' }))?.props?.width).toBe(width)
  expect((await ui.find({ key: 'board-rows' }))?.props?.marginLeft).toBeLessThan(0)
  await ui.unmount()
})

test('a drag on the bar under the board moves it sideways', async ($, on) => {
  engine(on)
  await start($)
  const ui = await mount($)
  await ui.resize({ columns: 100, rows: 1, in: 'board-scrollbar' })

  await ui.pointer({ type: 'down', x: 100, y: 0, button: 'left', in: 'board-scrollbar' })

  expect((await ui.find({ key: 'board-rows' }))?.props?.marginLeft).toBe(-102)
  await ui.unmount()
})

test('an expanded card is ready to generate, with its formats and Run', async ($, on) => {
  const { ui } = await openBoard($, on)

  await ui.press({ key: 'expand-Discovery/sign-up' })

  expect(await ui.find({ key: 'run' })).toBeDefined()
  expect(await ui.find({ key: 'validate' })).toBeDefined()
  expect(await ui.find({ key: 'reviewed' })).toBeDefined()
  await ui.unmount()
})

test('the pane fills the room it is given on every layout', async ($, on) => {
  const { ui } = await openBoard($, on)

  expect((await ui.find({ key: 'pane' }))?.props?.minHeight).toBe(40)
  expect((await ui.find({ key: 'pane-row' }))?.props?.flexGrow).toBe(1)
  await ui.press({ key: 'expand-board' })
  expect((await ui.find({ key: 'main' }))?.props?.height).toBe(40)
  await ui.press({ key: 'expand-board' })
  await ui.press({ key: 'expand-details' })
  expect((await ui.find({ key: 'main' }))?.props?.height).toBe(40)
  await ui.unmount()
})

const SMALL_PANE = { scroll: { offset: 0, bodyRows: 20 } }

const wheel = ($: any, bodyRows: number) => $.ui.scroll({ component: 'Pane', requestId: 'cdd-board', offset: 3, by: 3, bodyRows, contentRows: 60, origin: { kind: 'person' } })

test('a card taller than the pane opens at the top and the wheel moves it', async ($, on) => {
  engine(on)
  await start($)
  const ui = await mount($, 'vscode', SMALL_PANE)

  await ui.press({ key: 'expand-Discovery/sprint-a' })
  expect((await ui.find({ key: 'card-tiles' }))?.props?.top).toBe(1)

  await wheel($, 20)

  expect((await ui.find({ key: 'card-tiles' }))?.props?.top).toBe(-2)
  await ui.unmount()
})

test('the wheel stops at the end of a tall card', async ($, on) => {
  engine(on)
  await start($)
  const ui = await mount($, 'vscode', SMALL_PANE)
  await ui.press({ key: 'expand-Discovery/sprint-a' })

  for (let turn = 0; turn < 20; turn += 1) await wheel($, 20)

  expect((await ui.find({ key: 'card-tiles' }))?.props?.top).toBe(-13)
  await ui.unmount()
})

test('should show the whole opened card', async ($, on) => {
  const { ui } = await openBoard($, on)

  await ui.press({ key: 'expand-Discovery/sign-up' })
  await wheel($, 40)

  expect((await ui.find({ key: 'card-tiles' }))?.props?.top).toBe(7)
  expect((await ui.find({ key: 'board-rows' }))?.props?.marginTop).toBeLessThan(0)
  await ui.unmount()
})

test('should keep a card\'s controls inside the card', async ($, on) => {
  const { ui } = await openBoard($, on)

  expect((await ui.find({ key: 'card-Specification/pet-visits' }))?.props).toMatchObject({ overflow: 'hidden', minWidth: 0 })
  expect((await ui.find({ key: 'card-files-Specification/pet-visits' }))?.props?.flexWrap).toBe('wrap')
  await ui.unmount()
})

test('should keep a card\'s move buttons on one line', async ($, on) => {
  const { ui } = await openBoard($, on)

  expect((await ui.find({ key: 'moves-Specification/pet-visits' }))?.props?.flexWrap).toBeUndefined()
  await ui.unmount()
})

test('panels share the room the board does not need', async ($, on) => {
  const stub = engine(on)
  stub.answers['board.help'] = HELP
  stub.answers['ticket.report'] = REPORT
  stub.answers['ticket.files'] = FILES
  await start($)
  const ui = await mount($)
  await openViolations(ui)
  await openHelpPanel(ui)
  await ui.press({ key: 'card-Specification/pet-visits-list' })

  expect((await ui.find({ key: 'main' }))?.props?.width).toBe(42)
  expect((await ui.find({ key: 'panel-grip-help' }))?.props?.props).toMatchObject({ width: 26 })
  await ui.unmount()
})

test('a panel opens again at the width it was dragged to', async ($, on) => {
  const stub = engine(on)
  stub.answers['board.help'] = HELP
  await start($)
  const ui = await mount($)
  await openHelpPanel(ui)
  await ui.pointer({ type: 'move', x: -10, y: 0, button: 'left', in: 'panel-grip-help' })
  await ui.press({ key: 'panel-close-help' })

  await openHelpPanel(ui)

  expect((await ui.find({ key: 'panel-grip-help' }))?.props?.props).toMatchObject({ width: 70 })
  await ui.unmount()
})

test('should offer the action list and Run on an opened card', async ($, on) => {
  const stub = engine(on)
  stub.answers['ticket.files'] = FILES
  await start($)

  for (const surface of SURFACES) {
    const ui = await mount($, surface)
    await ui.press({ key: 'expand-Discovery/sign-up' })
    expect(await ui.find({ key: 'card-bar' })).toBeDefined()
    expect(await ui.find({ key: 'run' })).toBeDefined()
    await ui.press({ key: 'open-expand-Discovery/sign-up' })
    await ui.unmount()
  }
})

test('an answer the board cannot read says so, and the card still opens with its bar', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.rawText['ticket.files'] = 'Output too large for the conversation.'

  await ui.press({ key: 'expand-Discovery/sign-up' })

  expect(stub.toasts.at(-1)).toContain('cdd ticket.files sent back what the board cannot read')
  expect(await ui.find({ key: 'run' })).toBeDefined()
  await ui.unmount()
})

test('a hover on a tile leaves the bar a person pressed open on a card', async ($, on) => {
  const stub = engine(on)
  stub.answers['ticket.files'] = FILES
  await start($)
  const ui = await mount($)
  await ui.press({ key: 'expand-Discovery/sign-up' })
  const place = 'tile-Discovery/sign-up/stories-story_map'

  await ui.pointer({ type: 'enter', x: 0, y: 0, in: place })
  await ui.advance(500)
  await ui.pointer({ type: 'leave', x: 0, y: 0, in: place })

  expect(await ui.find({ key: 'card-bar' })).toBeDefined()
  await ui.unmount()
})

test('a main button is solid orange with dark text on a surface with pictures', async ($, on) => {
  const stub = engine(on)
  stub.answers['ticket.files'] = FILES
  await start($)
  const ui = await mount($, 'desktop')
  await ui.press({ key: 'expand-Specification/pet-visits' })

  expect((await ui.find({ key: 'primary-run' }))?.props).toMatchObject({ backgroundColor: '#E5531A', borderColor: '#E5531A' })
  expect((await findText(ui, 'Run'))?.props).toMatchObject({ color: '#0B0B0B', weight: 'semibold' })
  await ui.unmount()
})

test('should draw the primary action in the accent colour', async ($, on) => {
  const stub = engine(on)
  stub.answers['ticket.workspace'] = { has_branch: true, has_worktree: false, leaving_has_branch: true }
  await start($)
  const ui = await mount($, 'desktop')

  await ui.press({ key: 'activate-Discovery/sign-up' })

  expect((await ui.find({ key: 'primary-confirm-activation' }))?.props?.backgroundColor).toBe('#E5531A')
  await ui.unmount()
})

test('a main button that is off is a pale orange and does nothing', async ($, on) => {
  const stub = engine(on)
  stub.answers['ticket.files'] = {}
  await start($)
  const ui = await mount($, 'desktop')
  await ui.press({ key: 'expand-Specification/pet-visits' })
  await ui.press({ key: 'format-markdown' })
  await ui.press({ key: 'format-code' })

  await ui.press({ key: 'run' })

  expect((await ui.find({ key: 'primary-run' }))?.props?.backgroundColor).not.toBe('#E5531A')
  expect(stub.sent).toEqual([])
  await ui.unmount()
})

test('a terminal keeps its own primary button', async ($, on) => {
  const stub = engine(on)
  stub.answers['ticket.files'] = FILES
  await start($)
  const ui = await mount($, 'terminal')
  await ui.press({ key: 'expand-Specification/pet-visits' })

  expect(await ui.find({ key: 'primary-run' })).toBeUndefined()
  expect((await ui.find({ key: 'run' }))?.props?.variant).toBe('primary')
  await ui.unmount()
})

test('a card opening selects its ticket', async ($, on) => {
  const { ui } = await openBoard($, on)

  await ui.press({ key: 'expand-Discovery/sign-up' })

  expect((await findText(ui, /^Sign up sign-up/))?.text).toBeDefined()
  await ui.unmount()
})

test('a tile opening selects its ticket', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.answers['ticket.files'] = FILES
  await ui.press({ key: 'expand-Discovery/sign-up' })
  await ui.press({ key: 'ticket-Specification/pet-visits' })

  await ui.press({ key: 'toggle-card/Discovery/sign-up/stories-story_map' })

  expect((await findText(ui, /^Sign up sign-up/))?.text).toBeDefined()
  await ui.unmount()
})

// (E) Tickets

// (S) Person --> Add Backlog Item
test('should show the item in the Backlog with its text', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.answers['backlog-item.add'] = { ...ITEM, title: 'Gift cards', text: 'Sell gift cards.' }

  await ui.press({ key: 'add-to-backlog' })
  await ui.input({ key: 'draft-title', text: 'Gift cards', kind: 'change' })
  await ui.input({ key: 'draft-text', text: 'Sell gift cards.', kind: 'change' })
  await ui.press({ key: 'add-item' })

  expect(called(stub, 'backlog-item.add')).toEqual({ title: 'Gift cards', text: 'Sell gift cards.' })
  await ui.unmount()
})

test('Add stays off until the item has a title', async ($, on) => {
  const { stub, ui } = await openBoard($, on)

  await ui.press({ key: 'add-to-backlog' })
  await ui.press({ key: 'add-item' })

  expect(called(stub, 'backlog-item.add')).toBeUndefined()
  await ui.unmount()
})

test('an added item is selected and announced', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.answers['backlog-item.add'] = { ...ITEM, title: 'Gift cards', text: 'Sell gift cards.' }
  const board = boardOf()
  board.columns[0]!.items = [ITEM, { ...ITEM, title: 'Gift cards', text: 'Sell gift cards.' }]
  stub.board = board

  await ui.press({ key: 'add-to-backlog' })
  await ui.input({ key: 'draft-title', text: 'Gift cards', kind: 'change' })
  await ui.press({ key: 'add-item' })

  expect(stub.toasts.at(-1)).toBe('Gift cards added to Backlog')
  expect((await findText(ui, /^Sell gift cards\.$/))?.text).toBeDefined()
  await ui.unmount()
})

test('a started item is selected as a ticket and announced', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.answers['backlog-item.start'] = SIGN_UP

  await ui.press({ key: 'start-Returns and refunds' })

  expect(stub.toasts.at(-1)).toBe('Returns and refunds started in Discovery')
  expect((await findText(ui, /^Sign up sign-up/))?.text).toBeDefined()
  await ui.unmount()
})

test('should return the new ticket in Discovery', async ($, on) => {
  const { stub, ui } = await openBoard($, on)

  await ui.press({ key: 'start-Returns and refunds' })

  expect(called(stub, 'backlog-item.start')).toEqual({ backlog_item: 'Returns and refunds' })
  await ui.unmount()
})

test('should take the item off the Backlog', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  const board = boardOf()
  board.columns[0]!.items = []
  stub.board = board

  await ui.press({ key: 'start-Returns and refunds' })

  expect(await ui.find({ key: 'card-Backlog/Returns and refunds' })).toBeUndefined()
  await ui.unmount()
})

test('should bring the ticket back with its work', async ($, on) => {
  const { stub, ui } = await openBoard($, on)

  await ui.press({ key: 'item-Returns and refunds' })
  await ui.press({ key: 'start' })

  expect(called(stub, 'backlog-item.start')).toEqual({ backlog_item: 'Returns and refunds' })
  await ui.unmount()
})

// (S) Person --> Open Ticket Session
test('+ Ticket fills the prompt to open a ticket', async ($, on) => {
  const { stub, ui } = await openBoard($, on)

  await ui.press({ key: 'new-ticket' })

  expect(stub.fills.at(-1)).toContain('ticket.new')
  await ui.unmount()
})

const pressActivate = async (ui: any, address: string) => ui.press({ key: `activate-${address}` })

test('should create the ticket\'s branch when a ticket that has none is activated', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.answers['ticket.workspace'] = { has_branch: false, has_worktree: false, leaving_has_branch: true }

  await pressActivate(ui, 'Discovery/sign-up')
  await ui.press({ key: 'confirm-activation' })

  expect(called(stub, 'ticket.activate')).toEqual({ ticket: 'sign-up', leaving: ['commit', 'push'], opening: ['branch'] })
  await ui.unmount()
})

test('should commit the branch the ticket being left is on', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.answers['ticket.workspace'] = { has_branch: false, has_worktree: false, leaving_has_branch: true }

  await pressActivate(ui, 'Discovery/sign-up')
  await ui.press({ key: 'confirm-activation' })

  expect(called(stub, 'ticket.activate')?.leaving).toEqual(['commit', 'push'])
  await ui.unmount()
})

test('should commit nothing on a ticket that has no branch', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.answers['ticket.workspace'] = { has_branch: false, has_worktree: false, leaving_has_branch: false }

  await pressActivate(ui, 'Discovery/sign-up')
  await ui.press({ key: 'leave-commit' })
  await ui.press({ key: 'confirm-activation' })

  expect(called(stub, 'ticket.activate')?.leaving).toEqual([])
  await ui.unmount()
})

test('should say the ticket being left has no branch yet', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.answers['ticket.workspace'] = { has_branch: false, has_worktree: false, leaving_has_branch: false }

  await pressActivate(ui, 'Discovery/sign-up')

  expect((await findText(ui, /none yet/))?.text).toBeDefined()
  await ui.unmount()
})

test('activating selects the ticket and says what was done', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.answers['ticket.workspace'] = { has_branch: false, has_worktree: true, leaving_has_branch: true }

  await pressActivate(ui, 'Discovery/sign-up')
  await ui.press({ key: 'confirm-activation' })

  expect(stub.toasts.at(-1)).toBe('Pet visits: committed, pushed · Sign up: branch created · Sign up is now active')
  expect((await findText(ui, /^Sign up sign-up/))?.text).toBeDefined()
  await ui.unmount()
})

test('closing says what was done and selects the closed ticket', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.answers['ticket.workspace'] = { has_branch: true, has_worktree: false, leaving_has_branch: true }
  stub.answers['ticket.close'] = SPRINT_CLOSED

  await pressActivate(ui, 'Specification/pet-visits')
  await ui.press({ key: 'confirm-activation' })

  expect(stub.toasts.at(-1)).toBe('Pet visits: committed, pushed · Session Pet visits closed')
  await ui.unmount()
})

// (S) Person --> Close Active Session
test('should show the ticket in Complete', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.answers['ticket.workspace'] = { has_branch: true, has_worktree: false, leaving_has_branch: true }

  await pressActivate(ui, 'Specification/pet-visits')
  await ui.press({ key: 'confirm-activation' })

  expect(called(stub, 'ticket.close')).toEqual({ ticket: 'pet-visits', leaving: ['commit', 'push'] })
  await ui.unmount()
})

test('should leave no ticket active', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.answers['ticket.workspace'] = { has_branch: true, has_worktree: false, leaving_has_branch: true }
  stub.board = boardOf({ active: null })

  await pressActivate(ui, 'Specification/pet-visits')
  await ui.press({ key: 'confirm-activation' })

  expect(stub.statuses.at(-1)).toBeUndefined()
  await ui.unmount()
})

test('the Close button is on the active ticket alone', async ($, on) => {
  const { stub, ui } = await openBoard($, on)

  await ui.press({ key: 'ticket-Discovery/sign-up' })
  await ui.press({ key: 'close' })

  expect(called(stub, 'ticket.workspace')).toBeUndefined()
  await ui.unmount()
})

// (S) Person --> Restrict Actions To Active Session
test('with Active session only on, an arrow on another ticket does nothing', async ($, on) => {
  const { stub, ui } = await openBoard($, on)

  await ui.press({ key: 'next-Discovery/sign-up' })

  expect(called(stub, 'ticket.move_next')).toBeUndefined()
  await ui.unmount()
})

test('with Active session only on, information about another ticket stays open', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.answers['ticket.files'] = FILES

  await ui.press({ key: 'ticket-Discovery/sign-up' })
  await ui.press({ key: 'card-Discovery/sign-up-list' })

  expect(await ui.find({ key: 'panel-files' })).toBeDefined()
  await ui.unmount()
})

test('with Active session only off, every ticket can be acted on', async ($, on) => {
  const { stub, ui } = await openBoard($, on)

  await turnOffOnlyActive(ui)
  await ui.press({ key: 'next-Discovery/sign-up' })

  expect(called(stub, 'ticket.move_next')).toEqual({ ticket: 'sign-up' })
  await ui.unmount()
})

// (S) Person --> Move Ticket
const movedTo = (column: string, isDone = false) => ({ ...PET_VISITS, column, is_done: isDone })

const boardWithPetVisits = (moved: ReturnType<typeof movedTo>) => {
  const board = boardOf()
  board.columns[2]!.in_progress = []
  const column = board.columns.find(entry => entry.name === moved.column)!
  if (moved.column === 'Complete') column.tickets = [SPRINT_CLOSED, moved]
  else if (moved.is_done) column.done = [...(column.done ?? []), moved]
  else column.in_progress = [...(column.in_progress ?? []), moved]
  return board
}

const moveAndShow = async ($: any, on: any, press: string, moved: ReturnType<typeof movedTo>) => {
  const { stub, ui } = await openBoard($, on)
  stub.board = boardWithPetVisits(moved)
  await ui.press({ key: `${press}-Specification/pet-visits` })
  return { stub, ui }
}

test('should show the ticket in the next stage', async ($, on) => {
  const { stub, ui } = await moveAndShow($, on, 'next', movedTo('Implementation'))

  expect(called(stub, 'ticket.move_next')).toEqual({ ticket: 'pet-visits' })
  expect(await ui.find({ key: 'card-Implementation/pet-visits' })).toBeDefined()
  await ui.unmount()
})

test('should show the ticket in progress there', async ($, on) => {
  const { ui } = await moveAndShow($, on, 'next', movedTo('Implementation'))

  expect((await findText(ui, /^Pet visits pet-visits/))?.text).toContain('in progress')
  await ui.unmount()
})

// (S) Person --> Mark Ticket Done In Stage
test('should show the ticket in that stage\'s Done all the same', async ($, on) => {
  const { ui } = await moveAndShow($, on, 'next', movedTo('Specification', true))

  expect(await ui.find({ key: 'card-Specification/pet-visits' })).toBeDefined()
  await ui.unmount()
})

test('should show the ticket in progress in that stage', async ($, on) => {
  const { stub, ui } = await moveAndShow($, on, 'previous', movedTo('Specification'))

  expect(called(stub, 'ticket.move_previous')).toEqual({ ticket: 'pet-visits' })
  await ui.unmount()
})

test('should close the ticket', async ($, on) => {
  const { ui } = await moveAndShow($, on, 'next', movedTo('Complete'))

  expect(await ui.find({ key: 'card-Complete/pet-visits' })).toBeDefined()
  await ui.unmount()
})

test('should leave a ticket in Complete where it is on another move forward', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  await turnOffOnlyActive(ui)

  await ui.press({ key: 'next-Complete/sprint-a' })

  expect(called(stub, 'ticket.move_next')).toBeUndefined()
  await ui.unmount()
})

test('should reopen the ticket in Implementation', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  await turnOffOnlyActive(ui)

  await ui.press({ key: 'previous-Complete/sprint-a' })

  expect(called(stub, 'ticket.move_previous')).toEqual({ ticket: 'sprint-a' })
  await ui.unmount()
})

test('should show the ticket in Discovery', async ($, on) => {
  const { ui } = await moveAndShow($, on, 'previous', movedTo('Discovery', true))

  expect(await ui.find({ key: 'card-Discovery/pet-visits' })).toBeDefined()
  await ui.unmount()
})

test('should show the ticket in Discovery\'s Done', async ($, on) => {
  const { ui } = await moveAndShow($, on, 'previous', movedTo('Discovery', true))

  expect((await findText(ui, /^Pet visits pet-visits/))?.text).toContain('Discovery · done')
  await ui.unmount()
})

test('should show an item in the Backlog with the ticket\'s title', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  await turnOffOnlyActive(ui)
  const board = boardOf()
  board.columns[0]!.items = [ITEM, { ...ITEM, title: 'Sign up' }]
  board.columns[1]!.in_progress = [SPRINT_OPEN]
  stub.board = board

  await ui.press({ key: 'previous-Discovery/sign-up' })

  expect(await ui.find({ key: 'card-Backlog/Sign up' })).toBeDefined()
  await ui.unmount()
})

test('should take the ticket off the board\'s stages', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  await turnOffOnlyActive(ui)
  const board = boardOf()
  board.columns[1]!.in_progress = [SPRINT_OPEN]
  stub.board = board

  await ui.press({ key: 'previous-Discovery/sign-up' })

  expect(await ui.find({ key: 'card-Discovery/sign-up' })).toBeUndefined()
  await ui.unmount()
})

test('a ticket marked done raises a toast naming its place in the stage', async ($, on) => {
  const { stub } = await moveAndShow($, on, 'next', movedTo('Specification', true))

  expect(stub.toasts).toContain('Pet visits moved to Specification · Done')
})

test('a ticket moved to the Backlog raises a toast', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  await turnOffOnlyActive(ui)
  stub.answers['ticket.move_previous'] = { ...ITEM, title: 'Sign up' }
  const board = boardOf()
  board.columns[0]!.items = [ITEM, { ...ITEM, title: 'Sign up' }]
  board.columns[1]!.in_progress = [SPRINT_OPEN]
  stub.board = board

  await ui.press({ key: 'previous-Discovery/sign-up' })

  expect(stub.toasts).toEqual(['Sign up moved to Backlog'])
  await ui.unmount()
})

test('a ticket that moves takes its selection with it', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.answers['ticket.move_next'] = movedTo('Implementation')
  stub.board = boardWithPetVisits(movedTo('Implementation'))

  await ui.press({ key: 'next-Specification/pet-visits' })

  expect((await findText(ui, /^Pet visits pet-visits/))?.text).toContain('Implementation')
  await ui.unmount()
})

test('an open bar moves with its ticket to the tile worked on next', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.answers['ticket.files'] = FILES
  await openTileBar(ui, 'ux-mockup')
  const moved = { ...PET_VISITS, column: 'Discovery', next: 'ddd-bounded_context' }
  stub.answers['ticket.move_previous'] = moved
  stub.board = boardWithPetVisits(moved as ReturnType<typeof movedTo>)

  await ui.press({ key: 'previous-Specification/pet-visits' })

  expect((await ui.find({ key: 'toggle-Discovery/pet-visits/stories-story_map' }))?.props?.label).toContain('▴')
  await ui.unmount()
})

test('a ticket moved to the Backlog closes its card, its bar, and its panels', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.answers['ticket.files'] = FILES
  stub.answers['ticket.report'] = REPORT
  await turnOffOnlyActive(ui)
  await ui.press({ key: 'expand-Specification/pet-visits' })
  await openViolations(ui)
  stub.answers['ticket.move_previous'] = { ...ITEM, title: 'Pet visits' }
  const board = boardOf()
  board.columns[0]!.items = [ITEM, { ...ITEM, title: 'Pet visits' }]
  board.columns[2]!.in_progress = []
  stub.board = board

  await ui.press({ key: 'previous-Specification/pet-visits' })

  expect(await ui.find({ key: 'card-tiles' })).toBeUndefined()
  expect(await ui.find({ key: 'card-bar' })).toBeUndefined()
  expect(await ui.find({ key: 'panel-report' })).toBeUndefined()
  await ui.unmount()
})

test('a card\'s arrow is a pane Button on a surface with surface modules too', async ($, on) => {
  const stub = engine(on)
  await start($)
  const ui = await mount($)

  await ui.press({ key: 'previous-Specification/pet-visits' })

  expect(called(stub, 'ticket.move_previous')).toEqual({ ticket: 'pet-visits' })
  await ui.unmount()
})

test('/ticket next moves the ticket it names', async ($, on) => {
  const stub = engine(on)
  await start($)

  await $.command.run({ command: 'ticket', args: 'next pet-visits' })

  expect(called(stub, 'ticket.move_next')).toEqual({ ticket: 'pet-visits' })
})

test('/ticket with no verb it knows says how to use it', async ($, on) => {
  engine(on)
  await start($)

  const ran = await $.command.run({ command: 'ticket', args: 'pull pet-visits' })

  expect(ran.text).toBe('Usage: /ticket next|previous|close|activate <ticket>')
})

// (S) Person --> Activate Ticket
test('should make the chosen ticket the current session', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.answers['ticket.workspace'] = { has_branch: true, has_worktree: false, leaving_has_branch: true }

  await ui.press({ key: 'ticket-Discovery/sign-up' })
  await ui.press({ key: 'switch-to' })
  await ui.press({ key: 'confirm-activation' })

  expect(called(stub, 'ticket.activate')).toEqual({ ticket: 'sign-up', leaving: ['commit', 'push'], opening: [] })
  await ui.unmount()
})

test('the Activate dialog chooses what to do on leaving and opens with merge off', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.answers['ticket.workspace'] = { has_branch: true, has_worktree: false, leaving_has_branch: true }

  await pressActivate(ui, 'Discovery/sign-up')
  await ui.press({ key: 'leave-merge' })
  await ui.press({ key: 'leave-push' })
  await ui.press({ key: 'confirm-activation' })

  expect(called(stub, 'ticket.activate')?.leaving).toEqual(['commit', 'merge'])
  await ui.unmount()
})

test('Cancel in the Activate dialog changes nothing', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.answers['ticket.workspace'] = { has_branch: true, has_worktree: false, leaving_has_branch: true }

  await pressActivate(ui, 'Discovery/sign-up')
  await ui.press({ key: 'cancel-activation' })

  expect(called(stub, 'ticket.activate')).toBeUndefined()
  expect(await ui.find({ key: 'activation' })).toBeUndefined()
  await ui.unmount()
})

// (S) Person --> Split Ticket Into Child Tickets
test('should name the ticket it was split from', async ($, on) => {
  const { stub, ui } = await openBoard($, on)

  await ui.press({ key: 'split' })

  expect(stub.fills.at(-1)).toContain('ticket.new with parent pet-visits')
  await ui.unmount()
})

// (S) Person --> Archive Ticket
test('should leave the ticket off the board', async ($, on) => {
  const { stub, ui } = await openBoard($, on)

  await ui.press({ key: 'archive' })

  expect(called(stub, 'ticket.archive')).toEqual({ ticket: 'pet-visits' })
  await ui.unmount()
})

// (S) Person --> Write Ticket Handoff
test('Handoff fills the prompt with the handoff command', async ($, on) => {
  const { stub, ui } = await openBoard($, on)

  await ui.press({ key: 'handoff' })

  expect(stub.fills.at(-1)).toContain('/space-handoff-handoff-session')
  await ui.unmount()
})

// (S) Board Pane --> Display Latest Handoff
test('should show the latest handoff', async ($, on) => {
  const { ui } = await openBoard($, on)

  expect((await findText(ui, /^Latest handoff/))?.text).toContain('handoff-20261031T0412.md')
  await ui.unmount()
})

test('should show no handoff for a ticket that has none', async ($, on) => {
  const { ui } = await openBoard($, on)

  await ui.press({ key: 'ticket-Complete/sprint-a' })

  expect((await findText(ui, /^No handoff yet/))?.text).toBeDefined()
  await ui.unmount()
})

// (E) Practices

// (S) Board Pane --> Display Fidelity Progress
test('should show each fidelity\'s Generate, Validate, and Review', async ($, on) => {
  const { ui } = await openBoard($, on)

  await openTileBar(ui)

  expect((await ui.find({ type: 'Text', text: /^✓$/ }))?.text).toBe('✓')
  await ui.unmount()
})

// (S) Person --> Open Practice Tile
test('a short hover on a tile opens it and leaving closes it', async ($, on) => {
  const stub = engine(on)
  stub.answers['ticket.files'] = FILES
  await start($)
  const ui = await mount($)
  const place = 'tile-Specification/pet-visits/ux-mockup'

  await ui.pointer({ type: 'enter', x: 0, y: 0, in: place })
  await ui.advance(500)
  expect(await ui.find({ key: 'tile-bar' })).toBeDefined()

  await ui.pointer({ type: 'leave', x: 0, y: 0, in: place })
  expect(await ui.find({ key: 'tile-bar' })).toBeUndefined()
  await ui.unmount()
})

test('a press on a tile keeps it open after the pointer leaves', async ($, on) => {
  const stub = engine(on)
  stub.answers['ticket.files'] = FILES
  await start($)
  const ui = await mount($)
  const place = 'tile-Specification/pet-visits/ux-mockup'

  await ui.pointer({ type: 'down', x: 0, y: 0, button: 'left', in: place })
  await ui.pointer({ type: 'leave', x: 0, y: 0, in: place })

  expect(await ui.find({ key: 'tile-bar' })).toBeDefined()
  await ui.unmount()
})

// (S) Person --> Choose Ticket Practices
test('should show the practice off for that ticket', async ($, on) => {
  const { stub, ui } = await openBoard($, on)

  await ui.press({ key: 'practice-ux' })

  expect(called(stub, 'ticket.enable_practice')).toEqual({ ticket: 'pet-visits', practice: 'ux', is_enabled: false })
  await ui.unmount()
})

// (S) Person --> Run Action Across Practices
const chooseTileAction = async (ui: any, action: string) => ui.select({ key: 'action', value: action })

const openStageMenu = async (ui: any) => ui.press({ key: 'stage-menu-Specification' })

const boardWithUxOff = () => {
  const off = { ...PET_VISITS, practices: { ...PET_VISITS.practices, ux: false } }
  const shown = boardOf({ active: 'pet-visits' })
  return { ...shown, columns: shown.columns.map(column => (column.name === 'Specification' ? { ...column, in_progress: [off] } : column)) }
}

test('a practice turned off fades its tile, which does not open', async ($, on) => {
  const { ui } = await openBoard($, on, boardWithUxOff())

  expect(await ui.find({ key: 'toggle-Specification/pet-visits/ux-mockup' })).toBeUndefined()
  expect(JSON.stringify(await ui.find({ key: 'tile-box-Specification/pet-visits/ux-mockup' }))).toContain('#3c3c3f')
  await ui.unmount()
})

test('a practice turned off dims its label', async ($, on) => {
  const { ui } = await openBoard($, on, boardWithUxOff())

  expect((await ui.find({ key: 'practice-help-ux' }))?.props?.dimColor).toBeUndefined()
  await ui.unmount()
})

test('turning a practice off says so, says where it was saved, and lets go of its tile', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.answers['ticket.files'] = FILES
  await openTileBar(ui, 'ux-mockup')

  await ui.press({ key: 'practice-ux' })

  expect(stub.toasts.at(-1)).toBe('UX off for Pet visits · saved to .sessions/pet-visits/session.json')
  expect(await ui.find({ key: 'tile-bar' })).toBeUndefined()
  await ui.unmount()
})

test('with no practice left on a stage, the bar has nothing to run', async ($, on) => {
  const off = { ...PET_VISITS, practices: { stories: false, ddd: false, ux: false, clean_engineering: false, bdd: false } }
  const shown = boardOf({ active: 'pet-visits' })
  const { stub, ui } = await openBoard($, on, { ...shown, columns: shown.columns.map(column => (column.name === 'Specification' ? { ...column, in_progress: [off] } : column)) })
  stub.answers['ticket.files'] = {}

  await openStageMenu(ui)
  await ui.press({ key: 'validate' })
  await ui.press({ key: 'reviewed' })
  await ui.press({ key: 'run' })

  expect(stub.sent).toEqual([])
  await ui.unmount()
})

test('a closed tile shows its Generate, Validate, and Review marks', async ($, on) => {
  const { ui } = await openBoard($, on)

  const marks = JSON.stringify(await ui.find({ key: 'marks-Specification/pet-visits/ux-mockup' }))

  expect(marks).toContain('✓')
  expect(marks).toContain('…')
  expect(marks).toContain('○')
  await ui.unmount()
})

test('the open bar marks Generate as well as Validate and Review', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.answers['ticket.files'] = FILES

  await openTileBar(ui, 'ux-mockup')

  expect(JSON.stringify(await ui.find({ key: 'run-line' }))).toContain('✓')
  await ui.unmount()
})

test('a stage head opens its bar on a hover', async ($, on) => {
  engine(on)
  await start($)
  const ui = await mount($)

  expect((await ui.find({ key: 'stage-menu-Specification' }))?.props).toMatchObject({ module: 'hooks/kanban/tile-hover.tsx' })
  expect((await ui.find({ key: 'stage-menu-Specification' }))?.props?.props).toMatchObject({ opensOnHover: true, slugs: ['stories-scenarios', 'ux-mockup'] })
  await ui.unmount()
})

test('a stage head runs one action on every enabled practice in the stage', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.answers['ticket.files'] = FILES

  await openStageMenu(ui)
  await chooseTileAction(ui, 'sketch')
  await ui.press({ key: 'run' })

  expect(stub.sent.at(-1)).toBe('/actions-sketch stories-scenarios ux-mockup')
  await ui.unmount()
})

// (S) Board Pane --> Add Active Ticket To System Prompt
const composePrompt = ($: any) =>
  $.prompt.compose({ model: 'claude', promptModel: 'claude', surfaces: ['desktop'], tools: [], outputStyle: null, traits: [] })

test('the system prompt names the active ticket and its next guidance', async ($, on) => {
  engine(on)
  on('prompt.compose', () => ({ sections: [] }))
  await start($)

  const composed = await composePrompt($)

  expect(composed.sections.at(-1)?.text).toContain('ticket pet-visits ("Pet visits"), in Specification. Its next guidance is ux-mockup.')
})

test('the system prompt names the ticket even when the board could not be read at session start', async ($, on) => {
  const stub = engine(on, null)
  on('prompt.compose', () => ({ sections: [] }))
  await start($)
  stub.board = boardOf()

  const composed = await composePrompt($)

  expect(composed.sections.at(-1)?.text).toContain('ticket pet-visits')
})

// (S) Person --> Open Help
test('should show the fidelity\'s rules', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.answers['board.help'] = HELP

  await ui.press({ key: 'help-Specification/pet-visits/ux-mockup' })

  expect(called(stub, 'board.help')).toEqual({ practice: 'ux', fidelity: 'mockup' })
  expect((await findText(ui, 'verb-noun-format'))?.text).toBe('verb-noun-format')
  await ui.unmount()
})

test('should show the practice\'s shared rules', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.answers['board.help'] = HELP

  await ui.press({ key: 'practice-help-stories' })

  expect(called(stub, 'board.help')).toEqual({ practice: 'stories', fidelity: '' })
  await ui.unmount()
})

test('should link to the fidelity\'s page on the forge', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.answers['board.help'] = HELP

  await ui.press({ key: 'practice-help-stories' })
  await ui.press({ key: 'panel-expand-help' })

  expect((await ui.find({ type: 'Link' }))?.props?.href).toBe(HELP.href)
  await ui.unmount()
})

test('should name the stage a fidelity belongs to', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.answers['board.help'] = HELP

  await ui.press({ key: 'help-Specification/pet-visits/ux-mockup' })

  expect((await findText(ui, 'Discovery'))?.text).toBeDefined()
  expect((await findText(ui, 'story-map'))?.text).toBeDefined()
  expect(JSON.stringify(await ui.find({ key: 'help-place' }))).toContain('#6BCB77')
  await ui.unmount()
})

test('a practice\'s help heads its rules SHARED RULES and says Practice overview', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.answers['board.help'] = PRACTICE_HELP

  await ui.press({ key: 'practice-help-stories' })

  expect((await findText(ui, 'SHARED RULES'))?.text).toBeDefined()
  expect((await findText(ui, 'Practice overview'))?.text).toBeDefined()
  await ui.unmount()
})

test('help with no rules has no rules section', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.answers['board.help'] = { ...PRACTICE_HELP, rules: [] }

  await ui.press({ key: 'practice-help-stories' })

  expect(await ui.find({ key: 'help-rules' })).toBeUndefined()
  await ui.unmount()
})

// (S) Person --> Run Next Step
test('should name generate as the next action', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.answers['ticket.generate_commands'] = ['/actions-generate ddd-bounded-context format=markdown']

  await turnOffOnlyActive(ui)
  await ui.press({ key: 'ticket-Discovery/sign-up' })
  await ui.press({ key: 'run-next' })

  expect(called(stub, 'ticket.generate_commands')).toEqual({ ticket: 'sign-up', fidelities: ['ddd-bounded_context'], formats: ['markdown'] })
  expect(stub.sent).toEqual(['/actions-generate ddd-bounded-context format=markdown'])
  await ui.unmount()
})

test('Run next on held violations says fix violations', async ($, on) => {
  const { ui } = await openBoard($, on)

  expect((await ui.find({ key: 'run-next' }))?.props?.label).toBe('Run next: fix violations')
  await ui.unmount()
})

test('Run next on generate renders the earlier fidelity first', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.answers['ticket.generate_commands'] = ['/actions-render stories-story-map format=markdown source=drawio', '/actions-generate ddd-bounded-context format=markdown']

  await turnOffOnlyActive(ui)
  await ui.press({ key: 'ticket-Discovery/sign-up' })
  await ui.press({ key: 'run-next' })

  expect(stub.sent).toEqual(['/actions-render stories-story-map format=markdown source=drawio', '/actions-generate ddd-bounded-context format=markdown'])
  await ui.unmount()
})

test('Run next names the step that runs next', async ($, on) => {
  const { ui } = await openBoard($, on)

  await turnOffOnlyActive(ui)
  await ui.press({ key: 'ticket-Discovery/sign-up' })

  expect((await ui.find({ key: 'run-next' }))?.props?.label).toBe('Run next: generate')
  await ui.unmount()
})

test('should name satisfy as the next action', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.answers['ticket.report'] = REPORT

  await ui.press({ key: 'run-next' })

  expect(await ui.find({ key: 'panel-report' })).toBeDefined()
  await ui.unmount()
})

// (E) Generate

// (S) Person --> Choose Action And Formats
const openTileBar = async (ui: any, slug = 'stories-scenarios') => ui.press({ key: `toggle-Specification/pet-visits/${slug}` })

test('should allow only Generate before anything is generated', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.answers['ticket.files'] = FILES

  await openTileBar(ui, 'ux-mockup')
  await ui.press({ key: 'validate' })

  expect(stub.sent).toEqual([])
  await ui.unmount()
})

test('should not allow Review until Validate is clean', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.answers['ticket.files'] = FILES

  await openTileBar(ui, 'ux-mockup')
  await ui.press({ key: 'reviewed' })

  expect(stub.sent).toEqual([])
  await ui.unmount()
})

test('a format already generated carries a check', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.answers['ticket.files'] = FILES

  await openTileBar(ui, 'ux-mockup')

  expect((await ui.find({ key: 'format-code' }))?.props?.label).toBe('code')
  expect((await findText(ui, '✓ </>'))?.text).toBeDefined()
  await ui.unmount()
})

test('should give each fidelity its default format', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.answers['ticket.files'] = FILES
  stub.answers['ticket.generate_commands'] = []

  await openTileBar(ui)
  await ui.press({ key: 'run' })

  expect(called(stub, 'ticket.generate_commands')).toEqual({ ticket: 'pet-visits', fidelities: ['stories-scenarios'], formats: ['markdown'] })
  await ui.unmount()
})

const boardWithCode = () => {
  const shown = boardOf({ active: 'pet-visits' })
  const formats = { 'stories-scenarios': ['typescript', 'python'], 'ux-mockup': ['typescript', 'python'] }
  const default_formats = { 'stories-scenarios': 'python', 'ux-mockup': 'python' }
  return { ...shown, columns: shown.columns.map(column => (column.name === 'Specification' ? { ...column, formats, default_formats } : column)) }
}

const CODE_FILES = { 'stories-scenarios': { python: [{ path: 'a_spec.py', exists: true }] }, 'ux-mockup': { python: [{ path: 'b_spec.py', exists: false }] } }

test('a chip stands for a group, and each fidelity uses its default format from it', async ($, on) => {
  const { stub, ui } = await openBoard($, on, boardWithCode())
  stub.answers['ticket.files'] = { 'stories-scenarios': {}, 'ux-mockup': {} }
  stub.answers['ticket.generate_commands'] = []

  await openStageMenu(ui)
  await ui.press({ key: 'run' })

  expect(called(stub, 'ticket.generate_commands')?.formats).toEqual(['python'])
  await ui.unmount()
})

test('a format generated on some of the fidelities says how many', async ($, on) => {
  const { stub, ui } = await openBoard($, on, boardWithCode())
  stub.answers['ticket.files'] = CODE_FILES

  await openStageMenu(ui)

  expect((await findText(ui, '</> 1 of 2'))?.text).toBeDefined()
  await ui.unmount()
})

test('a format already generated is green', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.answers['ticket.files'] = FILES

  await openTileBar(ui, 'ux-mockup')

  expect((await findText(ui, '✓ </>'))?.props?.color).toBe('#22C55E')
  await ui.unmount()
})

test('a chosen format is solid orange', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.answers['ticket.files'] = FILES

  await openTileBar(ui)

  expect((await ui.find({ key: 'format-box-markdown' }))?.props?.backgroundColor).toBe('#E5531A')
  await ui.unmount()
})

test('Run clears the picks', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.answers['ticket.files'] = FILES
  stub.answers['ticket.generate_commands'] = []

  await openTileBar(ui)
  await ui.press({ key: 'run' })

  expect((await ui.find({ key: 'format-box-markdown' }))?.props?.backgroundColor).not.toBe('#E5531A')
  await ui.unmount()
})

test('an open tile reads its files again as a turn ends', async ($, on) => {
  on('turn.complete', () => ({ text: '' }))
  const { stub, ui } = await openBoard($, on)
  stub.answers['ticket.files'] = FILES
  await openTileBar(ui)
  stub.answers['ticket.files'] = { 'stories-scenarios': { markdown: [{ path: 'docs/scenarios.md', exists: true }] } }

  await $.turn.complete({ reason: 'answer', answer: 'done' } as never)

  expect((await findText(ui, '✓ M↓'))?.text).toBeDefined()
  await ui.unmount()
})

test('with Active session only on, the action list is drawn as text', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.answers['ticket.files'] = FILES

  await ui.press({ key: 'expand-Discovery/sign-up' })

  expect(await ui.find({ type: 'Select' })).toBeUndefined()

  await turnOffOnlyActive(ui)

  expect(await ui.find({ type: 'Select' })).toBeDefined()
  await ui.unmount()
})

test('with Active session only on, Run does nothing on another ticket', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.answers['ticket.files'] = FILES

  await ui.press({ key: 'expand-Discovery/sign-up' })
  await ui.press({ key: 'run' })

  expect(called(stub, 'ticket.generate_commands')).toBeUndefined()
  await ui.unmount()
})

// (S) Person --> Generate Fidelity Output
test('should render the earlier fidelity into the new format first', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.answers['ticket.files'] = FILES
  stub.answers['ticket.generate_commands'] = ['/actions-render stories-story-map format=markdown source=drawio', '/actions-generate stories-scenarios format=markdown']

  await openTileBar(ui)
  await ui.press({ key: 'run' })

  expect(called(stub, 'ticket.generate_commands')).toEqual({ ticket: 'pet-visits', fidelities: ['stories-scenarios'], formats: ['markdown'] })
  expect(stub.sent).toEqual(['/actions-render stories-story-map format=markdown source=drawio', '/actions-generate stories-scenarios format=markdown'])
  await ui.unmount()
})

test('Run stays off until a format is chosen', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.answers['ticket.files'] = FILES

  await openTileBar(ui)
  await ui.press({ key: 'format-markdown' })
  await ui.press({ key: 'run' })

  expect(stub.sent).toEqual([])
  await ui.unmount()
})

// (S) Person --> Render Fidelity Format
test('Render turns existing output into the chosen format', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.answers['ticket.files'] = { 'stories-scenarios': { markdown: [{ path: 'docs/scenarios.md', exists: true }] } }

  await openTileBar(ui)
  await chooseTileAction(ui, 'render')
  await ui.press({ key: 'format-markdown' })
  await ui.press({ key: 'run' })

  expect(stub.sent.at(-1)).toBe('/actions-render stories-scenarios format=markdown')
  await ui.unmount()
})

test('Render stays off with nothing to render', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.answers['ticket.files'] = FILES

  await openTileBar(ui)
  await chooseTileAction(ui, 'render')
  await ui.press({ key: 'run' })

  expect(stub.sent).toEqual([])
  await ui.unmount()
})

// (S) Person --> Send Sketch Iterate Or Document
test('a command the session does not have says so in a toast', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.answers['ticket.files'] = FILES
  stub.commandFails = true

  await openTileBar(ui)
  await chooseTileAction(ui, 'sketch')
  await ui.press({ key: 'run' })

  expect(stub.toasts.at(-1)).toContain('/actions-sketch stories-scenarios failed')
  await ui.unmount()
})

test('Sketch, Iterate, and Document send their command to the chat', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.answers['ticket.files'] = FILES

  await openTileBar(ui)
  for (const action of ['sketch', 'iterate', 'document']) {
    await chooseTileAction(ui, action)
    await ui.press({ key: 'run' })
  }

  expect(stub.sent).toEqual(['/actions-sketch stories-scenarios', '/actions-iterate stories-scenarios', '/actions-document stories-scenarios'])
  await ui.unmount()
})

// (E) Validate

// (S) Person --> Validate Fidelity
test('Validate on a tile sends the fidelity to validate', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.answers['ticket.files'] = FILES

  await openTileBar(ui)
  await ui.press({ key: 'validate' })

  expect(stub.sent.at(-1)).toBe('/actions-validate stories-scenarios')
  await ui.unmount()
})

// (S) Person --> Open Validation Report
test('should show that fidelity\'s latest report', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.answers['ticket.report'] = REPORT

  await openViolations(ui)

  expect(called(stub, 'ticket.report')).toEqual({ ticket: 'pet-visits', fidelity: 'ux-mockup' })
  expect((await findText(ui, REPORT.path))?.text).toBe(REPORT.path)
  await ui.unmount()
})

const boardWithCounts = (violation_counts: Record<string, number>) => {
  const counted = { ...PET_VISITS, violation_counts }
  const shown = boardOf({ active: 'pet-visits' })
  return { ...shown, columns: shown.columns.map(column => (column.name === 'Specification' ? { ...column, in_progress: [counted] } : column)) }
}

test('should count the violations of the fidelity on its ticket', async ($, on) => {
  const { stub, ui } = await openBoard($, on, boardWithCounts({ 'ux-mockup': 2 }))
  stub.answers['ticket.files'] = FILES

  await openTileBar(ui, 'ux-mockup')

  expect((await findText(ui, /^2 violations$/))?.text).toBeDefined()
  await ui.unmount()
})

test('should leave a fidelity with no saved graph uncounted', async ($, on) => {
  const { stub, ui } = await openBoard($, on, boardWithCounts({}))
  stub.answers['ticket.files'] = FILES

  await openTileBar(ui, 'ux-mockup')

  expect((await findText(ui, /^violations$/))?.text).toBeDefined()
  await ui.unmount()
})

test('should show no report for a fidelity that has none', async ($, on) => {
  const { stub, ui } = await openBoard($, on)

  await turnOffOnlyActive(ui)
  await ui.press({ key: 'ticket-Discovery/sign-up' })

  expect(await ui.find({ key: 'violations-Discovery/sign-up' })).toBeUndefined()
  expect(called(stub, 'ticket.report')).toBeUndefined()
  await ui.unmount()
})

test('should list the rules of every fidelity with violations', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.answers['ticket.violations'] = TICKET_VIOLATIONS

  await ui.press({ key: 'violations-Specification/pet-visits' })

  expect(called(stub, 'ticket.violations')).toEqual({ ticket: 'pet-visits' })
  expect(await ui.find({ key: 'rule-ux-mockup/verb-noun-format' })).toBeDefined()
  expect(await ui.find({ key: 'rule-stories-scenarios/one-outcome' })).toBeDefined()
  await ui.unmount()
})

test('should name the fidelity a rule was broken on', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.answers['ticket.violations'] = TICKET_VIOLATIONS

  await ui.press({ key: 'violations-Specification/pet-visits' })
  await ui.press({ key: 'fix-all-stories-scenarios/one-outcome' })

  expect(stub.sent.at(-1)).toBe('/actions-satisfy stories-scenarios rule one-outcome')
  await ui.unmount()
})

// (S) Person --> Fix Report Violations
test('should list each rule the report names with its violations', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.answers['ticket.report'] = REPORT

  await openViolations(ui)

  expect((await findText(ui, /^Name the story with a verb$/))?.text).toBeDefined()
  await ui.unmount()
})

test('should show the text of each rule under its name', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.answers['ticket.report'] = REPORT

  await openViolations(ui)

  expect((await findText(ui, /^Name every story with a verb and a noun\.$/))?.text).toBeDefined()
  await ui.unmount()
})

test('should give a violation the line it failed on', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.answers['ticket.report'] = REPORT

  await openViolations(ui)

  expect((await findText(ui, /^docs\/map\.md:12$/))?.text).toBeDefined()
  await ui.unmount()
})

test('should show the source lines around a violation', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.answers['ticket.report'] = REPORT

  await openViolations(ui)

  expect((await findText(ui, /^## Payment$/))?.text).toBeDefined()
  expect((await findText(ui, /^13$/))?.text).toBeDefined()
  await ui.unmount()
})

test('the line a violation failed on is marked', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.answers['ticket.report'] = REPORT

  await openViolations(ui)

  expect((await ui.find({ key: 'failing-line-12' }))?.props).toMatchObject({ backgroundColor: '#2F1414' })
  await ui.unmount()
})

test('should show no source for a file that is not in the repository', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.answers['ticket.report'] = REPORT_WITHOUT_SOURCE

  await openViolations(ui)

  expect(await ui.find({ key: 'violation-source' })).toBeUndefined()
  expect(await ui.find({ key: 'open-unknown-Name the story with a verb' })).toBeUndefined()
  await ui.unmount()
})

test('a violation\'s location opens the file at its line', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.answers['ticket.report'] = REPORT
  stub.answers['ticket.files'] = FILES
  stub.answers['ticket.read_file'] = { path: 'docs/map.md', text: Array.from({ length: 14 }, (_, index) => `line ${index + 1}`).join('\n') }

  await openViolations(ui)
  await ui.press({ key: 'open-docs/map.md:12-Name the story with a verb' })

  expect(called(stub, 'ticket.read_file')).toEqual({ ticket: 'pet-visits', path: 'docs/map.md' })
  expect((await ui.find({ type: 'Code' }))?.props).toMatchObject({ source: 'line 12\nline 13\nline 14', startLine: 12 })
  await ui.unmount()
})

test('should say a report has no saved graph', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.answers['ticket.report'] = { ...REPORT, rules: [], has_saved_graph: false }

  await openViolations(ui)

  expect((await findText(ui, /has no saved graph/))?.text).toBeDefined()
  expect(await findText(ui, 'No violations in this report')).toBeUndefined()
  await ui.unmount()
})

test('a report with its saved graph and no rules says it has no violations', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.answers['ticket.report'] = { ...REPORT, rules: [] }

  await openViolations(ui)

  expect((await findText(ui, 'No violations in this report'))?.text).toBeDefined()
  await ui.unmount()
})

test('Fix sends satisfy for one violation', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.answers['ticket.report'] = REPORT

  await openViolations(ui)
  await ui.press({ key: 'fix-ux-mockup-verb-noun-format-docs/map.md:12-Name the story with a verb' })

  expect(stub.sent.at(-1)).toBe('/actions-satisfy ux-mockup docs/map.md:12 rule verb-noun-format')
  await ui.unmount()
})

test('Fix all sends satisfy for every violation of a rule', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.answers['ticket.report'] = REPORT

  await openViolations(ui)
  await ui.press({ key: 'fix-all-ux-mockup/verb-noun-format' })

  expect(stub.sent.at(-1)).toBe('/actions-satisfy ux-mockup rule verb-noun-format')
  await ui.unmount()
})

test('an open report is read again after a cdd tool call', async ($, on) => {
  const stub = engine(on)
  on('tool.call', () => ({ result: {} }))
  stub.answers['ticket.report'] = REPORT
  await start($)
  const ui = await mount($, 'vscode')
  await openViolations(ui)
  stub.answers['ticket.report'] = { ...REPORT, rules: [] }

  await $.tool.call({ tool: 'mcp__cdd__validate_validate' } as never)

  expect((await findText(ui, /^No violations in this report$/))?.text).toBeDefined()
  await ui.unmount()
})

// (S) Person --> Satisfy Violations From Band
test('Satisfy on the band fills the prompt with the fidelities that have violations', async ($, on) => {
  const stub = engine(on)
  await start($)
  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })

  await ui.press({ key: 'satisfy' })

  expect(stub.fills.at(-1)).toBe('/actions-satisfy ux-mockup')
  await ui.unmount()
})

test('the band above the prompt names the active ticket\'s violations', async ($, on) => {
  engine(on)
  await start($)
  const ui = await $.ui.mount({ ...BAND, surface: 'terminal' })

  expect((await findText(ui, /violations/))?.text).toBe('pet-visits · Specification · violations: ux-mockup')
  await ui.unmount()
})

// (E) Review

// (S) Person --> List Ticket Files
const openFilesList = async ($: any, on: any) => {
  const opened = await openBoard($, on)
  opened.stub.answers['ticket.files'] = FILES
  opened.stub.answers['ticket.read_file'] = { path: 'docs/story-map.md', text: '# Story map' }
  await opened.ui.press({ key: 'card-Discovery/sign-up-list' })
  return opened
}

test('should list the files a pattern finds there', async ($, on) => {
  const { ui } = await openFilesList($, on)

  expect(await ui.find({ key: 'file-docs/story-map.md' })).toBeDefined()
  await ui.unmount()
})

test('should list the file with whether it exists', async ($, on) => {
  const { ui } = await openFilesList($, on)

  expect(await ui.find({ key: 'file-docs/story-map.md' })).toBeDefined()
  expect(await ui.find({ key: 'file-docs/story-map.drawio' })).toBeUndefined()
  await ui.unmount()
})

test('should list only the fidelities asked for', async ($, on) => {
  const { stub, ui } = await openFilesList($, on)

  expect(called(stub, 'ticket.files')).toEqual({ ticket: 'sign-up', fidelities: ['stories-story_map', 'ddd-bounded_context'] })
  await ui.unmount()
})

test('a list that cannot be read says so and opens nothing', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.rawText['ticket.files'] = 'Output too large for the conversation.'

  await ui.press({ key: 'card-Discovery/sign-up-list' })

  expect(stub.toasts.at(-1)).toBe('The files of sign-up could not be read')
  expect(await ui.find({ key: 'panel-files' })).toBeUndefined()
  await ui.unmount()
})

test('the Files head names the fidelities', async ($, on) => {
  const { ui } = await openFilesList($, on)

  expect((await findText(ui, 'stories-story-map, ddd-bounded-context'))?.text).toBeDefined()
  await ui.unmount()
})

test('an open Files panel is read again after a cdd tool call, and a closed tab stays closed', async ($, on) => {
  on('tool.call', () => ({ result: {} }))
  const { stub, ui } = await openFilesList($, on)
  await ui.press({ key: 'mode-files' })
  await ui.press({ key: 'tab-close-docs/story-map.drawio' })
  stub.answers['ticket.files'] = {
    'stories-story_map': { markdown: [{ path: 'docs/story-map.md', exists: true }, { path: 'docs/more.md', exists: true }], drawio: [{ path: 'docs/story-map.drawio', exists: true }] },
  }

  await $.tool.call({ tool: 'mcp__cdd__session_switch' } as never)

  expect(await ui.find({ key: 'tab-open-docs/more.md' })).toBeDefined()
  expect(await ui.find({ key: 'tab-open-docs/story-map.drawio' })).toBeUndefined()
  await ui.unmount()
})

// (S) Person --> Browse Ticket Folder
test('the folder mode groups the files under their folders', async ($, on) => {
  const { ui } = await openFilesList($, on)

  await ui.press({ key: 'mode-folder' })

  expect((await findText(ui, /^docs\/$/))?.text).toBe('docs/')
  await ui.unmount()
})

// (S) Person --> View Files
test('should return the file\'s text', async ($, on) => {
  const { stub, ui } = await openFilesList($, on)

  await ui.press({ key: 'file-docs/story-map.md' })

  expect(called(stub, 'ticket.read_file')).toEqual({ ticket: 'sign-up', path: 'docs/story-map.md' })
  await ui.unmount()
})

test('the files mode opens on markdown ahead of a diagram', async ($, on) => {
  const { stub, ui } = await openFilesList($, on)

  await ui.press({ key: 'mode-files' })

  expect(called(stub, 'ticket.read_file')?.path).toBe('docs/story-map.md')
  await ui.unmount()
})

test('the files mode opens one tab per format, generated or not', async ($, on) => {
  const { ui } = await openFilesList($, on)

  await ui.press({ key: 'mode-files' })

  expect(await ui.find({ key: 'tab-open-docs/story-map.drawio' })).toBeDefined()
  expect(await ui.find({ key: 'tab-open-docs/story-map.md' })).toBeDefined()
  await ui.unmount()
})

test('a format not generated says so in its tab', async ($, on) => {
  const { ui } = await openFilesList($, on)

  await ui.press({ key: 'mode-files' })
  await ui.press({ key: 'tab-open-docs/story-map.drawio' })

  expect((await findText(ui, /^Not generated yet$/))?.text).toBeDefined()
  await ui.unmount()
})

test('× closes one tab', async ($, on) => {
  const { ui } = await openFilesList($, on)

  await ui.press({ key: 'mode-files' })
  await ui.press({ key: 'tab-close-docs/story-map.drawio' })

  expect(await ui.find({ key: 'tab-open-docs/story-map.drawio' })).toBeUndefined()
  await ui.unmount()
})

// (S) Person --> Review Fidelity
test('Reviewed on a tile sends the fidelity to review after a clean validate', async ($, on) => {
  const { stub, ui } = await openBoard($, on)
  stub.answers['ticket.files'] = FILES

  await openTileBar(ui)
  await ui.press({ key: 'reviewed' })

  expect(stub.sent.at(-1)).toBe('/actions:review:review stories-scenarios')
  await ui.unmount()
})

test('an earlier version\'s stored board is declined', async ($, on) => {
  engine(on, null)
  on('state.get', { key: 'board' }, () => ({ value: { value: { shape: 'board-1', value: { columns: 'old' } }, version: 1 } }))
  await start($)
  const ui = await mount($)

  expect((await ui.find({ type: 'Text' }))?.text).toBe('No board yet: is the cdd MCP server connected?')
  await ui.unmount()
})

test('should fill the pane\'s height', async ($, on) => {
  engine(on, boardOf({ active: 'pet-visits' }))
  await start($)
  const ui = await mount($)
  expect((await ui.find({ key: 'pane' }))?.props?.minHeight).toBe(PANE.props.scroll.bodyRows)
})

test('should open the files list beside the board', async ($, on) => {
  const { ui } = await openFilesList($, on)
  expect(await ui.find({ key: 'pane-row' })).toBeTruthy()
  expect(await ui.find({ key: 'panel-expand-files' })).toBeTruthy()
})

test('should keep the sideways scrollbar on screen', async ($, on) => {
  const { ui } = await openBoard($, on)
  await ui.press({ key: 'expand-board' })
  expect((await ui.find({ key: 'main' }))?.props?.height).toBe(PANE.props.scroll.bodyRows)
  expect(await ui.find({ key: 'columns-right' })).toBeTruthy()
})

test('should draw a card at the canvas width', async ($, on) => {
  const { ui } = await openBoard($, on)
  expect((await ui.find({ key: 'board-rows' }))?.props?.width).toBe(222)
})

// (E) Server Health Band

const HEALTHY = { graph_app_port: 5173, is_hook_server_running: false }

const healthEngine = (on: any) => {
  const stub = engine(on)
  stub.answers['server-health.report'] = HEALTHY
  return stub
}

const mountHealthBand = async ($: any) => {
  await $.prompt.submit({ text: 'look' })
  return $.ui.mount({ ...BAND, surface: 'desktop', props: { ...BAND.props, scroll: { offset: 0, bodyRows: 3 }, view: {} } })
}

const expandedOf = async (ui: any) => {
  const band = await ui.find({ key: 'server-health' })
  return band?.children?.[0]
}

const pinned = async (ui: any) => {
  await ui.press({ key: 'health-icon' })
  return ui
}

test('should report the port the graph app answers on', async ($, on) => {
  healthEngine(on)
  await start($)
  const ui = await pinned(await mountHealthBand($))

  expect((await findText(ui, 'running :5173'))?.text).toBe('running :5173')
  await ui.unmount()
})

test('should report no graph app port', async ($, on) => {
  const stub = healthEngine(on)
  stub.answers['server-health.report'] = { ...HEALTHY, graph_app_port: null }
  await start($)
  const ui = await pinned(await mountHealthBand($))

  expect((await findText(ui, 'not running'))?.text).toBe('not running')
  await ui.unmount()
})

test('should report the hook server is not running', async ($, on) => {
  healthEngine(on)
  await start($)
  const ui = await pinned(await mountHealthBand($))

  expect((await findText(ui, 'not installed'))?.text).toBe('not installed')
  await ui.unmount()
})

test('connected draws one check mark until it is pinned', async ($, on) => {
  healthEngine(on)
  await start($)
  const ui = await mountHealthBand($)

  expect((await expandedOf(ui))?.props?.display).toBe('none')
  await ui.unmount()
})

test('the expanded band reveals itself on hover', async ($, on) => {
  healthEngine(on)
  await start($)
  const ui = await mountHealthBand($)

  expect((await expandedOf(ui))?.hover?.display).toBe('flex')
  await ui.unmount()
})

test('connected shows all five parts with the count of loaded tools', async ($, on) => {
  healthEngine(on)
  await start($)
  const ui = await pinned(await mountHealthBand($))

  expect((await findText(ui, '116 loaded'))?.text).toBe('116 loaded')
  await ui.unmount()
})

test('a second press on the icon collapses the band', async ($, on) => {
  healthEngine(on)
  await start($)
  const ui = await pinned(await mountHealthBand($))

  await ui.press({ key: 'health-icon' })

  expect((await expandedOf(ui))?.props?.display).toBe('none')
  await ui.unmount()
})

test('a lost server shows Disconnected', async ($, on) => {
  const stub = healthEngine(on)
  await start($)
  stub.serverLost = true
  const ui = await pinned(await mountHealthBand($))

  expect((await findText(ui, 'Disconnected'))?.text).toBe('Disconnected')
  await ui.unmount()
})

test('a server from another checkout shows Tools missing with the count', async ($, on) => {
  const stub = healthEngine(on)
  stub.rawText['server-health.report'] = "KeyError: 'server-health.report'"
  await start($)
  const ui = await pinned(await mountHealthBand($))

  expect((await findText(ui, /116 loaded, server-health.report/))?.text).toBe('116 loaded, server-health.report is not one of them.')
  await ui.unmount()
})

test('Reconnect that succeeds says the MCP host is back', async ($, on) => {
  const stub = healthEngine(on)
  await start($)
  stub.serverLost = true
  const ui = await pinned(await mountHealthBand($))
  stub.serverLost = false

  await ui.press({ key: 'health-reconnect' })

  expect((await findText(ui, /MCP host is back/))?.text).toBe('MCP host is back. Board refreshed.')
  await ui.unmount()
})

test('Reconnect that succeeds reads the board again', async ($, on) => {
  const stub = healthEngine(on)
  await start($)
  stub.serverLost = true
  const ui = await pinned(await mountHealthBand($))
  stub.serverLost = false
  stub.calls.length = 0

  await ui.press({ key: 'health-reconnect' })

  expect(stub.calls.some(call => call.tool === 'board.show')).toBe(true)
  await ui.unmount()
})

test('Reconnect on a server still lost shows the try it is on', async ($, on) => {
  const stub = healthEngine(on)
  await start($)
  stub.serverLost = true
  const ui = await pinned(await mountHealthBand($))

  await ui.press({ key: 'health-reconnect' })

  expect((await findText(ui, /Try 1 of 3/))?.text).toBe('Waiting for cdd to answer. Try 1 of 3.')
  await ui.unmount()
})

test('Details lists the failing tool, the error and the fix', async ($, on) => {
  const stub = healthEngine(on)
  await start($)
  stub.serverLost = true
  const ui = await pinned(await mountHealthBand($))

  await ui.press({ key: 'health-details' })

  expect((await findText(ui, /Press Reconnect/))?.text).toBe('Press Reconnect. If that fails, press Run install.')
  await ui.unmount()
})

test('the health band yields to a survey', async ($, on) => {
  healthEngine(on)
  await start($)
  await $.prompt.submit({ text: 'look' })

  // Beneath the plugins nothing draws, so a band that passed the survey through finds nothing to mount.
  await expect($.ui.mount({ ...BAND, surface: 'desktop', props: { ...BAND.props, hasSurvey: true } })).rejects.toThrow('no implementation for ui.render')
})
