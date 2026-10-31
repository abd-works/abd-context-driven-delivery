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
  progress,
})

const PET_VISITS = ticket('pet-visits', 'Pet visits', 'Specification', 'ux-mockup', {
  'stories-scenarios': 'done',
  'ux-mockup': 'violations',
})
const SIGN_UP = ticket('sign-up', 'Sign up', 'Discovery', 'ddd-bounded_context', { 'stories-story_map': 'done' })

const BOARD = {
  active: 'pet-visits',
  columns: [
    { name: 'Backlog', items: [{ title: 'Returns and refunds', path: '.sessions/_backlog/returns.md' }] },
    { name: 'Discovery', work_required: ['stories-story_map', 'ddd-bounded_context'], in_progress: [SIGN_UP], done: [] },
    { name: 'Specification', work_required: ['stories-scenarios', 'ux-mockup'], in_progress: [PET_VISITS], done: [] },
    { name: 'Implementation', work_required: [], in_progress: [], done: [] },
    { name: 'Complete', tickets: [] },
  ],
}

const answer = (body: unknown) => ({ value: { content: [{ type: 'text', text: JSON.stringify(body) }], isError: false } })

const engine = (on: any, calls: { tool: string; args: unknown }[] = [], statuses: (string | undefined)[] = []) => {
  on('command.register', () => ({ value: { command: 'board' } }))
  on('ui.open', () => ({ value: { isPlaced: true } }))
  on('ui.status', (_: unknown, e: { text: string | undefined }) => {
    statuses.push(e.text)
    return { value: undefined }
  })
  on('ui.toast', () => ({ value: undefined }))
  on('mcp.call', (_: unknown, e: { tool: string; args: unknown }) => {
    calls.push({ tool: e.tool, args: e.args })
    return answer(e.tool === 'kanban.board' ? BOARD : PET_VISITS)
  })
  on('session.start', (_: unknown, e: { cwd: string }) => ({ cwd: e.cwd }))
}

test('the board pane shows every column and the tickets in them, on every surface', async ($, on) => {
  engine(on)
  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })

  for (const surface of SURFACES) {
    const ui = await $.ui.mount({ ...PANE, surface })
    expect((await ui.find({ type: 'Text', text: /Specification \(1\)/ }))?.text).toBe('Specification (1)')
    expect(await ui.find({ key: 'ticket-pet-visits' })).toBeDefined()
    expect((await ui.find({ type: 'Text', text: /Returns and refunds/ }))?.text).toBe('Returns and refunds')
    await ui.unmount()
  }
})

test('the status line names the active ticket, its stage, and its next guidance', async ($, on) => {
  const statuses: (string | undefined)[] = []
  engine(on, [], statuses)
  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })

  expect(statuses.at(-1)).toBe('pet-visits · Specification · next: ux-mockup')
})

test('a pressed card shows that ticket and its progress', async ($, on) => {
  engine(on)
  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  const ui = await $.ui.mount({ ...PANE, surface: 'desktop' })

  await ui.press({ key: 'ticket-sign-up' })

  expect((await ui.find({ type: 'Text', text: /^Sign up/ }))?.text).toBe('Sign up sign-up · Discovery · next: ddd-bounded_context')
  await ui.unmount()
})

test('Pull asks the cdd server to pull the chosen ticket', async ($, on) => {
  const calls: { tool: string; args: unknown }[] = []
  engine(on, calls)
  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  const ui = await $.ui.mount({ ...PANE, surface: 'desktop' })

  await ui.press({ key: 'pull' })

  expect(calls.find(call => call.tool === 'kanban.pull')?.args).toEqual({ ticket: 'pet-visits' })
  await ui.unmount()
})

test('the band above the prompt names the active ticket\'s violations', async ($, on) => {
  engine(on)
  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  const ui = await $.ui.mount({ ...BAND, surface: 'terminal' })

  expect((await ui.find({ type: 'Text', text: /violations/ }))?.text).toBe('pet-visits · Specification · violations: ux-mockup')
  await ui.unmount()
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
