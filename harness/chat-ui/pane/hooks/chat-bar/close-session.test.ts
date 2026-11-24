// (S) Person --> Protect Work When Closing Session
// Deleting a session's worktree or branch without a commit takes the work nobody committed with it. The chat bar's close
// dialog shows the Ticket's warning and the files it means while those are the choices made, and the toast after the
// close names the files whose work went with the worktree.
import { expect, test } from 'claude-code/testing'

const BAND = {
  plugin: 'cdd-board',
  component: 'AbovePrompt',
  requestId: 'above-prompt',
  props: { hasSurvey: false, isCollapsed: false, isWorking: false, maxRows: 24, bodyColumns: 120, scroll: { offset: 0, bodyRows: 24 }, view: {} },
} as const

type TestOn = Parameters<Extract<Parameters<typeof test>[1], (...args: never[]) => unknown>>[1]
type Engine = Parameters<Parameters<typeof test>[1]>[0]

// Seed: the worktree the chat works in, the ticket checkout-flow's own.
const FOLDER = 'C:/work/shop-checkout-flow'

// Seed: the ticket checkout-flow, active in its own worktree, as board.overview sends it in active.
const CHECKOUT_FLOW = {
  title: 'Checkout flow', last_activity: '', name: 'checkout-flow', is_main: false, text: '', tags: [], children: [], is_pulled_out: false, is_stacked: false,
  session: { name: 'checkout-flow', session_file: `C:/work/shop/.sessions/checkout-flow/session.json`, title: 'Checkout flow', repo_name: 'shop', branch: 'checkout-flow', is_repository: true, root: FOLDER, scope: '', parent: '', workpath: '', practices: {}, handoff: '' },
  progress: [], column: { name: 'Discovery' }, is_closed: false, is_active: true, is_open: true, parent_choices: [], drop_targets: [], is_done: false,
  next: null, agent_context: '', worktree: FOLDER, new_chat_link: '', session_path: '', working_chat: null, stage_work: [], next_place: null, previous_place: null, dropped_work: [],
}

const OVERVIEW = { project: 'shop', is_clone: true, folder: FOLDER, practices: [], fidelities: [], columns: [{ name: 'Discovery', tickets: [{ name: 'checkout-flow' }] }], active: CHECKOUT_FLOW }

const WARNING = "Deleting checkout-flow's worktree or branch without a commit loses the work nobody committed in app/order.py, notes.txt; choose commit to keep it."

// Seed: ticket.close_choices for checkout-flow, whose worktree holds a change to app/order.py and a new notes.txt.
const CLOSE_CHOICES = {
  branch: 'checkout-flow',
  own_branch: 'checkout-flow',
  choices: ['handoff', 'commit', 'push', 'merge', 'delete_branch', 'delete_worktree'],
  unsaved_work: ['app/order.py', 'notes.txt'],
  warning: WARNING,
  chosen: [],
}

// Seed: the closed ticket ticket.close answers, naming the files whose work went with its worktree.
const CLOSED = { ...CHECKOUT_FLOW, is_closed: true, is_active: false, is_open: false, column: { name: 'Complete' }, worktree: '', dropped_work: ['app/order.py', 'notes.txt'] }

/** A chat in checkout-flow's worktree whose cdd tools answer as the Python Ticket does, and whose toasts are kept. */
function chatInWorktree(on: TestOn) {
  const called: string[] = []
  const toasts: string[] = []
  const stored: Record<string, { value: unknown; version: number }> = {}
  const keyOf = (e: unknown) => {
    const { plugin, key } = e as { plugin: string; key: string }
    return `${plugin}:${key}`
  }
  const answer = (value: unknown) => ({ value: { content: [{ type: 'text', text: JSON.stringify(value) }], isError: false } })
  const answers: Record<string, unknown> = { 'board.overview': OVERVIEW, 'ticket.close_choices': CLOSE_CHOICES, 'ticket.close': CLOSED }
  on('session.root', () => ({ value: FOLDER }))
  on('session.id', () => ({ value: 'chat-1' }))
  on('session.messages', () => ({ value: [] }))
  on('turn.complete', () => ({ text: 'Done.' }))
  on('mcp.call', (_, e) => {
    const tool = (e as { tool: string }).tool
    called.push(tool)
    if (tool in answers) return answer(answers[tool])
    return { value: { content: [{ type: 'text', text: 'not stubbed' }], isError: true } }
  })
  on('process.run', () => ({ value: { exitCode: 0, stdout: '', stderr: '' } }))
  on('tool.list', () => ({ value: [] }))
  on('ui.status', () => ({ value: undefined }))
  on('ui.toast', (_, e) => {
    toasts.push((e as { text: string }).text)
    return { value: undefined }
  })
  on('ui.invalidate', () => ({ value: undefined }))
  on('clock.after', () => new Promise(() => undefined))
  on('clock.every', () => new Promise(() => undefined))
  // The busy wheel turns on each sleep while the close runs, so a sleep that answers at once would turn it forever.
  on('clock.sleep', () => new Promise(() => undefined))
  on('state.get', (_, e) => ({ value: stored[keyOf(e)] ?? { value: undefined, version: 0 } }))
  on('state.set', (_, e) => {
    const key = keyOf(e)
    const version = (stored[key]?.version ?? 0) + 1
    stored[key] = { value: (e as { value: unknown }).value, version }
    return { value: { isSet: true, version } }
  })
  return { called, toasts }
}

const FINISHED_TURN = { answer: 'Done.', durationMs: 1, isAborted: false, turnId: 't1', reason: 'answer' } as const
const WAIT_MS = 20
const WAITS = 25

// A turn's end reads the board again without holding the turn up, so the test waits for that read before drawing.
async function barAfterRead($: Engine, called: string[]) {
  const reads = called.filter(tool => tool === 'board.overview').length
  await $.turn.complete(FINISHED_TURN)
  for (let tries = 0; tries < WAITS && called.filter(tool => tool === 'board.overview').length === reads; tries += 1) {
    await new Promise(resolve => setTimeout(resolve, WAIT_MS))
  }
  await new Promise(resolve => setTimeout(resolve, WAIT_MS))
  return $.ui.mount({ ...BAND, surface: 'desktop' })
}

// The bar drawn again after a press, as the engine draws it once the press has changed what the bar shows.
async function pressedAndDrawn($: Engine, ui: Awaited<ReturnType<typeof barAfterRead>>, key: string) {
  await ui.press({ key })
  await ui.unmount()
  return $.ui.mount({ ...BAND, surface: 'desktop' })
}

// The close dialog open, with the choices pressed in order.
async function closeDialogWith($: Engine, called: string[], pressed: string[]) {
  let ui = await pressedAndDrawn($, await barAfterRead($, called), 'close-button')
  for (const choice of pressed) ui = await pressedAndDrawn($, ui, `close-${choice}`)
  return ui
}

const warningOf = (ui: Awaited<ReturnType<typeof barAfterRead>>) => ui.find({ type: 'Text', text: WARNING })

test('the close dialog does not warn while nothing that removes the worktree is chosen', async ($, on) => {
  const { called } = chatInWorktree(on)

  const ui = await closeDialogWith($, called, [])

  expect(await warningOf(ui)).toBeUndefined()
  await ui.unmount()
})

test('choosing to delete the worktree shows the warning that the work nobody committed is lost', async ($, on) => {
  const { called } = chatInWorktree(on)

  const ui = await closeDialogWith($, called, ['delete_worktree'])

  expect((await warningOf(ui))?.text).toBe(WARNING)
  await ui.unmount()
})

test('choosing to delete the worktree lists each file whose work nobody committed', async ($, on) => {
  const { called } = chatInWorktree(on)

  const ui = await closeDialogWith($, called, ['delete_worktree'])

  expect([(await ui.find({ type: 'Text', text: '  • app/order.py' }))?.text, (await ui.find({ type: 'Text', text: '  • notes.txt' }))?.text]).toEqual(['  • app/order.py', '  • notes.txt'])
  await ui.unmount()
})

test('choosing to delete the branch shows the warning too', async ($, on) => {
  const { called } = chatInWorktree(on)

  const ui = await closeDialogWith($, called, ['delete_branch'])

  expect((await warningOf(ui))?.text).toBe(WARNING)
  await ui.unmount()
})

test('choosing to commit as well takes the warning away', async ($, on) => {
  const { called } = chatInWorktree(on)

  const ui = await closeDialogWith($, called, ['delete_worktree', 'commit'])

  expect(await warningOf(ui)).toBeUndefined()
  await ui.unmount()
})

test('closing with only the worktree deleted names the files whose work went with it', async ($, on) => {
  const { called, toasts } = chatInWorktree(on)

  const ui = await closeDialogWith($, called, ['delete_worktree'])
  await ui.press({ key: 'close-confirm' })

  expect(toasts).toContain('Checkout flow: worktree deleted · uncommitted work lost in app/order.py, notes.txt · Session Checkout flow closed')
  await ui.unmount()
})
