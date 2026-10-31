import { expect, test } from 'claude-code/testing'

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

const ticket = (name: string, title: string, column: string, next: string | null, progress: Record<string, string>) => ({
  name,
  title,
  scope: 'feature',
  parent: '',
  column,
  is_done: next === null,
  next,
  last_activity: '2026-10-31T05:00:00Z',
  handoff: `.sessions/${name}/handoff-20261031T0412.md`,
  progress,
})

const PET_VISITS = ticket('pet-visits', 'Pet visits', 'Specification', 'ux-mockup', {
  'stories-scenarios': 'done',
  'ux-mockup': 'violations',
})
const SIGN_UP = ticket('sign-up', 'Sign up', 'Discovery', 'ddd-bounded_context', { 'stories-story_map': 'done' })
const LOYALTY = ticket('loyalty', 'Loyalty points', 'Discovery', null, { 'stories-story_map': 'done' })
const SPRINT_OPEN = ticket('sprint-a', 'Sprint A', 'Discovery', 'stories-story_map', {})
const SPRINT_CLOSED = { ...ticket('sprint-a', 'Sprint A', 'Complete', null, {}), is_done: false, handoff: '' }

const BOARD = {
  project: 'abd-pet-store-demo',
  active: 'pet-visits',
  columns: [
    {
      name: 'Backlog',
      items: [{ title: 'Returns and refunds', path: '.sessions/_backlog/returns.md', last_activity: '2026-10-30T05:00:00Z' }],
    },
    {
      name: 'Discovery',
      work_required: ['stories-story_map', 'ddd-bounded_context'],
      in_progress: [SIGN_UP, SPRINT_OPEN],
      done: [LOYALTY],
    },
    { name: 'Specification', work_required: ['stories-scenarios', 'ux-mockup'], in_progress: [PET_VISITS], done: [] },
    { name: 'Implementation', work_required: [], in_progress: [], done: [] },
    { name: 'Complete', tickets: [SPRINT_CLOSED] },
  ],
}

const answer = (body: unknown) => ({ value: { content: [{ type: 'text', text: JSON.stringify(body) }], isError: false } })

const engine = (
  on: any,
  calls: { tool: string; args: unknown }[] = [],
  statuses: (string | undefined)[] = [],
  fills: string[] = [],
  toasts: string[] = [],
  shown: unknown = BOARD,
) => {
  on('command.register', () => ({ value: { command: 'board' } }))
  on('ui.open', () => ({ value: { isPlaced: true } }))
  on('ui.status', (_: unknown, e: { text: string | undefined }) => {
    statuses.push(e.text)
    return { value: undefined }
  })
  on('ui.toast', (_: unknown, e: { text: string }) => {
    toasts.push(e.text)
    return { value: undefined }
  })
  on('ui.invalidate', () => ({ value: undefined }))
  on('prompt.fill', (_: unknown, e: { text: string }) => {
    fills.push(e.text)
    return { isFilled: true }
  })
  on('clock.now', () => ({ value: Date.parse('2026-10-31T05:04:00Z') }))
  on('mcp.call', (_: unknown, e: { tool: string; args: unknown }) => {
    calls.push({ tool: e.tool, args: e.args })
    return answer(e.tool === 'kanban.board' ? shown : PET_VISITS)
  })
  on('session.start', (_: unknown, e: { cwd: string }) => ({ cwd: e.cwd }))
}

test('the board pane shows every column and the tickets in them, on every surface', async ($, on) => {
  engine(on)
  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })

  for (const surface of SURFACES) {
    const ui = await $.ui.mount({ ...PANE, surface })
    expect((await ui.find({ type: 'Text', text: /^SPECIFICATION$/ }))?.text).toBe('SPECIFICATION')
    expect(await ui.find({ key: 'card-Specification/pet-visits' })).toBeDefined()
    expect((await ui.find({ type: 'Text', text: /^Returns and refunds$/ }))?.text).toBe('Returns and refunds')
    await ui.unmount()
  }
})

test('the board header names the project and counts a session open and closed under one name once', async ($, on) => {
  engine(on)
  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  const ui = await $.ui.mount({ ...PANE, surface: 'desktop' })

  expect((await ui.find({ type: 'Text', text: /tickets$/ }))?.text).toBe('abd-pet-store-demo · 4 tickets')
  await ui.unmount()
})

test('a card says how long ago its ticket was worked on and what comes next', async ($, on) => {
  engine(on)
  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  const ui = await $.ui.mount({ ...PANE, surface: 'desktop' })

  expect((await ui.find({ key: 'card-Specification/pet-visits' }))?.props?.props).toMatchObject({
    meta: 'feature · 4 min ago',
    tail: { text: 'next: ux-mockup' },
  })
  await ui.unmount()
})

test('the status line names the active ticket, its stage, its next guidance, and its violations', async ($, on) => {
  const statuses: (string | undefined)[] = []
  engine(on, [], statuses)
  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })

  expect(statuses.at(-1)).toBe('pet-visits · Specification · next: ux-mockup · 1 violation')
})

test('with no card pressed, the active ticket\'s detail shows with its fidelities, states, and latest handoff', async ($, on) => {
  engine(on)
  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  const ui = await $.ui.mount({ ...PANE, surface: 'desktop' })

  expect((await ui.find({ type: 'Text', text: /^Pet visits pet-visits/ }))?.text).toBe(
    'Pet visits pet-visits · feature · Specification · in progress',
  )
  expect((await ui.find({ type: 'Text', text: /^mockup$/ }))?.text).toBe('mockup')
  expect((await ui.find({ type: 'Text', text: /^\s*violations\s*$/ }))?.text.trim()).toBe('violations')
  expect((await ui.find({ type: 'Text', text: /^Latest handoff/ }))?.text).toBe(
    'Latest handoff: .sessions/pet-visits/handoff-20261031T0412.md · Next: ux-mockup',
  )
  await ui.unmount()
})

const pressCard = (ui: any, address: string) => ui.pointer({ type: 'down', x: 9, y: 1, button: 'left', in: `card-${address}` })

test('a press anywhere on a card shows that ticket', async ($, on) => {
  engine(on)
  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  const ui = await $.ui.mount({ ...PANE, surface: 'desktop' })

  await pressCard(ui, 'Discovery/sign-up')

  expect((await ui.find({ type: 'Text', text: /^Sign up sign-up/ }))?.text).toBe(
    'Sign up sign-up · feature · Discovery · in progress',
  )
  await ui.unmount()
})

test('a closed session under an open session\'s name can be pressed apart from it', async ($, on) => {
  engine(on)
  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  const ui = await $.ui.mount({ ...PANE, surface: 'desktop' })

  await pressCard(ui, 'Complete/sprint-a')

  expect((await ui.find({ type: 'Text', text: /^Sprint A sprint-a/ }))?.text).toBe('Sprint A sprint-a · feature · Complete')
  await ui.unmount()
})

test('hovering a status in the details names the skill that does that work', async ($, on) => {
  engine(on)
  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  const ui = await $.ui.mount({ ...PANE, surface: 'desktop' })

  expect((await ui.find({ type: 'Text', text: '/practices-ux-ux-mockup' }))?.text).toBe('/practices-ux-ux-mockup')
  await ui.unmount()
})

test('a practice with two words in its name keeps them in its skill', async ($, on) => {
  engine(on, [], [], [], [], {
    ...BOARD,
    columns: BOARD.columns.map(column =>
      column.name === 'Implementation' ? { ...column, work_required: ['clean_engineering-code'] } : column,
    ),
  })
  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  const ui = await $.ui.mount({ ...PANE, surface: 'desktop' })

  expect(
    (await ui.find({ type: 'Text', text: '/practices-clean-engineering-clean-engineering-code' }))?.text,
  ).toBe('/practices-clean-engineering-clean-engineering-code')
  await ui.unmount()
})

test('an arrow on a card moves its ticket to the next column', async ($, on) => {
  const calls: { tool: string; args: unknown }[] = []
  engine(on, calls)
  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  const ui = await $.ui.mount({ ...PANE, surface: 'desktop' })

  await ui.post({ move: 'next', ticket: 'sign-up' }, { in: 'card-Discovery/sign-up' })

  expect(calls.find(call => call.tool === 'kanban.move_next')?.args).toEqual({ ticket: 'sign-up' })
  await ui.unmount()
})

test('an arrow on a card moves its ticket to the previous column', async ($, on) => {
  const calls: { tool: string; args: unknown }[] = []
  engine(on, calls)
  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  const ui = await $.ui.mount({ ...PANE, surface: 'desktop' })

  await ui.post({ move: 'previous', ticket: 'pet-visits' }, { in: 'card-Specification/pet-visits' })

  expect(calls.find(call => call.tool === 'kanban.move_previous')?.args).toEqual({ ticket: 'pet-visits' })
  await ui.unmount()
})

test('a drag on the split bar gives the board more rows', async ($, on) => {
  engine(on)
  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  const ui = await $.ui.mount({ ...PANE, surface: 'desktop' })

  await ui.post({ boardRows: 30 }, { in: 'split-grip' })

  expect((await ui.find({ key: 'split-grip' }))?.props?.props).toMatchObject({ boardRows: 30 })
  await ui.unmount()
})

test('a drag cannot close either region', async ($, on) => {
  engine(on)
  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  const ui = await $.ui.mount({ ...PANE, surface: 'desktop' })

  await ui.post({ boardRows: 500 }, { in: 'split-grip' })

  expect((await ui.find({ key: 'split-grip' }))?.props?.props).toMatchObject({ boardRows: 34 })
  await ui.unmount()
})

test('Expand board gives the whole pane to the board and Show both brings the details back', async ($, on) => {
  engine(on)
  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  const ui = await $.ui.mount({ ...PANE, surface: 'desktop' })

  await ui.press({ key: 'expand-board' })
  expect(await ui.find({ key: 'detail' })).toBeUndefined()

  await ui.press({ key: 'show-both' })
  expect(await ui.find({ key: 'detail' })).toBeDefined()
  await ui.unmount()
})

test('Expand details gives the whole pane to the details', async ($, on) => {
  engine(on)
  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  const ui = await $.ui.mount({ ...PANE, surface: 'desktop' })

  await ui.press({ key: 'expand-details' })

  expect(await ui.find({ key: 'columns' })).toBeUndefined()
  await ui.unmount()
})

test('on a surface with no surface modules, a card is still pressed to show its ticket', async ($, on) => {
  engine(on)
  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  const ui = await $.ui.mount({ ...PANE, surface: 'vscode' })

  await ui.press({ key: 'ticket-Discovery/sign-up' })

  expect((await ui.find({ type: 'Text', text: /^Sign up sign-up/ }))?.text).toBeDefined()
  await ui.unmount()
})

test('a pressed backlog card offers Start, which opens a ticket for the item', async ($, on) => {
  const calls: { tool: string; args: unknown }[] = []
  engine(on, calls)
  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  const ui = await $.ui.mount({ ...PANE, surface: 'desktop' })

  await ui.press({ key: 'item-Returns and refunds' })
  await ui.press({ key: 'start' })

  expect(calls.find(call => call.tool === 'kanban.start')?.args).toEqual({ backlog_item: 'Returns and refunds' })
  await ui.unmount()
})

test('Pull asks the cdd server to pull a ticket whose stage is done', async ($, on) => {
  const calls: { tool: string; args: unknown }[] = []
  engine(on, calls)
  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  const ui = await $.ui.mount({ ...PANE, surface: 'desktop' })

  await pressCard(ui, 'Discovery/loyalty')
  await ui.press({ key: 'pull' })

  expect(calls.find(call => call.tool === 'kanban.pull')?.args).toEqual({ ticket: 'loyalty' })
  await ui.unmount()
})

test('Pull does nothing on a ticket whose stage is not done', async ($, on) => {
  const calls: { tool: string; args: unknown }[] = []
  engine(on, calls)
  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  const ui = await $.ui.mount({ ...PANE, surface: 'desktop' })

  await ui.press({ key: 'pull' })

  expect(calls.find(call => call.tool === 'kanban.pull')).toBeUndefined()
  await ui.unmount()
})

test('Switch to makes the chosen ticket the current session', async ($, on) => {
  const calls: { tool: string; args: unknown }[] = []
  engine(on, calls)
  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  const ui = await $.ui.mount({ ...PANE, surface: 'desktop' })

  await pressCard(ui, 'Discovery/sign-up')
  await ui.press({ key: 'switch-to' })

  expect(calls.find(call => call.tool === 'session.switch')?.args).toEqual({ name: 'sign-up' })
  await ui.unmount()
})

test('Split fills the prompt with the ticket to split', async ($, on) => {
  const fills: string[] = []
  engine(on, [], [], fills)
  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  const ui = await $.ui.mount({ ...PANE, surface: 'desktop' })

  await ui.press({ key: 'split' })

  expect(fills.at(-1)).toContain('kanban.new with parent pet-visits')
  await ui.unmount()
})

test('the band above the prompt names the active ticket\'s violations', async ($, on) => {
  engine(on)
  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  const ui = await $.ui.mount({ ...BAND, surface: 'terminal' })

  expect((await ui.find({ type: 'Text', text: /violations/ }))?.text).toBe('pet-visits · Specification · violations: ux-mockup')
  await ui.unmount()
})

test('Satisfy on the band fills the prompt with the fidelities that have violations', async ($, on) => {
  const fills: string[] = []
  engine(on, [], [], fills)
  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })

  await ui.press({ key: 'satisfy' })

  expect(fills.at(-1)).toBe('/actions-satisfy ux-mockup')
  await ui.unmount()
})

test('/ticket pull asks the cdd server to pull the named ticket', async ($, on) => {
  const calls: { tool: string; args: unknown }[] = []
  engine(on, calls)
  on('command.run', (_: unknown, e: unknown) => e)
  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })

  await $.command.run({ command: 'ticket', args: 'pull loyalty', origin: { kind: 'composer' } } as never)

  expect(calls.find(call => call.tool === 'kanban.pull')?.args).toEqual({ ticket: 'loyalty' })
})

test('a session open and closed under one name raises no toast on each read of the board', async ($, on) => {
  const toasts: string[] = []
  engine(on, [], [], [], toasts)
  on('prompt.submit', (_: unknown, e: { text: string }) => ({ text: e.text }))
  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })

  await $.prompt.submit({ text: 'next step?' })

  expect(toasts).toEqual([])
})

test('the system prompt names the active ticket and its next guidance', async ($, on) => {
  engine(on)
  on('prompt.compose', () => ({ sections: [] }))
  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })

  const composed = await $.prompt.compose({
    model: 'claude',
    promptModel: 'claude',
    surfaces: ['desktop'],
    tools: [],
    outputStyle: null,
    traits: [],
  })

  expect(composed.sections.at(-1)?.text).toContain('ticket pet-visits ("Pet visits"), in Specification. Its next guidance is ux-mockup.')
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
    throw new Error('no connected MCP tool "kanban.board" on a server named "cdd"')
  })
  on('session.start', (_: unknown, e: { cwd: string }) => ({ cwd: e.cwd }))

  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  const ui = await $.ui.mount({ ...PANE, surface: 'desktop' })

  expect(statuses.at(-1)).toMatch(/^cdd board: /)
  expect((await ui.find({ type: 'Text' }))?.text).toBe('No board yet: is the cdd MCP server connected?')
  await ui.unmount()
})

test('a prompt sent reads the board again, so a board the cdd server could not give at start appears', async ($, on) => {
  let connected = false
  const statuses: (string | undefined)[] = []
  on('command.register', () => ({ value: { command: 'board' } }))
  on('ui.open', () => ({ value: { isPlaced: true } }))
  on('ui.toast', () => ({ value: undefined }))
  on('ui.status', (_: unknown, e: { text: string | undefined }) => {
    statuses.push(e.text)
    return { value: undefined }
  })
  on('mcp.call', () => (connected ? answer(BOARD) : { value: { content: [], isError: true } }))
  on('session.start', (_: unknown, e: { cwd: string }) => ({ cwd: e.cwd }))
  on('prompt.submit', (_: unknown, e: { text: string }) => ({ text: e.text }))

  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  connected = true
  await $.prompt.submit({ text: 'next step?' })

  expect(statuses.at(-1)).toBe('pet-visits · Specification · next: ux-mockup · 1 violation')
})

test('the system prompt names the ticket even when the board could not be read at session start', async ($, on) => {
  let connected = false
  on('command.register', () => ({ value: { command: 'board' } }))
  on('ui.open', () => ({ value: { isPlaced: true } }))
  on('ui.toast', () => ({ value: undefined }))
  on('ui.status', () => ({ value: undefined }))
  on('ui.invalidate', () => ({ value: undefined }))
  on('mcp.call', () => (connected ? answer(BOARD) : { value: { content: [], isError: true } }))
  on('session.start', (_: unknown, e: { cwd: string }) => ({ cwd: e.cwd }))
  on('prompt.compose', () => ({ sections: [] }))

  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  connected = true
  const composed = await $.prompt.compose({
    model: 'claude',
    promptModel: 'claude',
    surfaces: ['desktop'],
    tools: [],
    outputStyle: null,
    traits: [],
  })

  expect(composed.sections.at(-1)?.text).toContain('ticket pet-visits')
})
