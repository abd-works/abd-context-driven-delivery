// (S) Person --> Show Backlog Items In Session List
// (S) Person --> Start Backlog Item From Session List
// The main chat's session list holds the Backlog closed, saying how many items it holds; opened, a BACKLOG box beside the
// list shows them, a page at a time where the chat has too few rows; a parent is one item, which starts with its child
// items. Starting an item goes down the board's own way out of the Backlog:
// backlog-item.start on the folder chosen beside the new session's name, then ticket.activate, as Open Session does.
// Scenarios: story_tests/move-work-forward-from-chat-bar/steer-sessions/steer_sessions_story.test.md
import { expect, test } from 'claude-code/testing'

// The band above the prompt, maxRows tall; a test that runs the Backlog into columns makes it shorter.
let bandRows = 40
const bandOf = () => ({
  plugin: 'cdd-board',
  component: 'AbovePrompt',
  requestId: 'above-prompt',
  props: { hasSurvey: false, isCollapsed: false, isWorking: false, maxRows: bandRows, bodyColumns: 160, scroll: { offset: 0, bodyRows: bandRows }, view: {} },
}) as const

type TestOn = Parameters<Extract<Parameters<typeof test>[1], (...args: never[]) => unknown>>[1]
type Engine = Parameters<Parameters<typeof test>[1]>[0]
type Called = { tool: string; args: Record<string, unknown> }

// Seed: the repository's own folder, whose chat works on main.
const FOLDER = 'C:/work/shop'

// Seed: main, the session the repository's own chat works on, as board.overview sends it in active.
const MAIN = {
  title: 'main', last_activity: '', name: 'main', is_main: true, text: '', tags: [], children: [], is_pulled_out: false, is_stacked: false,
  session: { name: 'main', session_file: `${FOLDER}/.sessions/main/session.json`, title: 'main', repo_name: 'shop', branch: 'main', is_repository: true, root: FOLDER, scope: '', parent: '', workpath: '', practices: {}, handoff: '' },
  progress: [], column: { name: 'Discovery' }, is_closed: false, is_active: true, is_open: true, parent_choices: [], drop_targets: [], is_done: false,
  next: null, agent_context: '', worktree: '', new_chat_link: '', session_path: '', working_chat: null, stage_work: [], next_place: null, previous_place: null, dropped_work: [],
}

// Seed: the Backlog's items as board.overview sends them: Payment retry on its own, then Checkout flow, the parent of
// Address form and Card form.
const PAYMENT_RETRY = { title: 'Payment retry', children: [] }
const CHECKOUT_FLOW = { title: 'Checkout flow', children: [{ title: 'Address form' }, { title: 'Card form' }] }

function overviewWith(items: unknown[]) {
  return {
    project: 'shop', is_clone: true, folder: FOLDER, practices: [], fidelities: [],
    columns: [{ name: 'Backlog', kind: 'backlog', items, tickets: [] }, { name: 'Discovery', kind: 'stage', items: [], tickets: [{ name: 'main' }] }],
    active: MAIN,
  }
}

// Seed: the ticket an item's start opens, as backlog-item.start and ticket.activate answer it, in its own worktree.
function startedTicket(name: string) {
  return { ...MAIN, name, title: name, is_main: false, is_active: false, worktree: `C:/work/shop-${name}`, working_chat: { id: 'chat-2' } }
}

const nameOf = (title: string) => title.toLowerCase().replace(/ /g, '-')

/** The repository's own chat whose board holds items; backlog-item.start answers each item's ticket unless refused,
 * and ticket.activate opens it unless refused. Each cdd tool called is kept with its arguments, and each failure shown. */
function mainChat(on: TestOn, items: unknown[], refused: { start?: string; activate?: string } = {}, picked = '', rows = 40) {
  bandRows = rows
  const called: Called[] = []
  const toasts: string[] = []
  const stored: Record<string, { value: unknown; version: number }> = {}
  const keyOf = (e: unknown) => {
    const { plugin, key } = e as { plugin: string; key: string }
    return `${plugin}:${key}`
  }
  const answer = (value: unknown) => ({ value: { content: [{ type: 'text', text: JSON.stringify(value) }], isError: false } })
  const refusal = (text: string) => ({ value: { content: [{ type: 'text', text }], isError: true } })
  let shown = items
  on('session.root', () => ({ value: FOLDER }))
  on('session.id', () => ({ value: 'chat-1' }))
  on('session.messages', () => ({ value: [] }))
  on('turn.complete', () => ({ text: 'Done.' }))
  on('mcp.call', (_, e) => {
    const { tool, args } = e as { tool: string; args: Record<string, unknown> }
    called.push({ tool, args })
    if (tool === 'board.overview') return answer(overviewWith(shown))
    if (tool === 'backlog-item.start') {
      if (refused.start) {
        shown = shown.filter(item => (item as { title: string }).title !== args.backlog_item)
        return refusal(refused.start)
      }
      return answer(startedTicket(nameOf(String(args.backlog_item))))
    }
    if (tool === 'ticket.activate') return refused.activate ? refusal(refused.activate) : answer(startedTicket(String(args.ticket)))
    if (tool === 'chats.list') return answer([])
    return refusal('not stubbed')
  })
  // The system's folder picker answers the folder the Person picks, or none.
  on('process.run', () => ({ value: { exitCode: 0, stdout: picked, stderr: '' } }))
  on('tool.list', () => ({ value: [] }))
  on('command.list', () => ({ value: [] }))
  on('ui.status', () => ({ value: undefined }))
  on('ui.toast', (_, e) => {
    toasts.push((e as { text: string }).text)
    return { value: undefined }
  })
  on('ui.invalidate', () => ({ value: undefined }))
  on('clock.after', () => new Promise(() => undefined))
  on('clock.every', () => new Promise(() => undefined))
  on('clock.sleep', () => new Promise(() => undefined))
  on('state.get', (_, e) => ({ value: stored[keyOf(e)] ?? { value: undefined, version: 0 } }))
  on('state.set', (_, e) => {
    const key = keyOf(e)
    const version = (stored[key]?.version ?? 0) + 1
    stored[key] = { value: (e as { value: unknown }).value, version }
    return { value: { isSet: true, version } }
  })
  return { called, toasts, stored }
}

const FINISHED_TURN = { answer: 'Done.', durationMs: 1, isAborted: false, turnId: 't1', reason: 'answer' } as const
const WAIT_MS = 20
const WAITS = 25

// A turn's end reads the board again without holding the turn up, so the test waits for that read before drawing.
async function barAfterRead($: Engine, called: Called[]) {
  const reads = () => called.filter(call => call.tool === 'board.overview').length
  const before = reads()
  await $.turn.complete(FINISHED_TURN)
  for (let tries = 0; tries < WAITS && reads() === before; tries += 1) await new Promise(resolve => setTimeout(resolve, WAIT_MS))
  await new Promise(resolve => setTimeout(resolve, WAIT_MS))
  return $.ui.mount({ ...bandOf(), surface: 'desktop' })
}

type Mounted = Awaited<ReturnType<typeof barAfterRead>>

// The bar drawn again after each press, as the engine draws it once the press has changed what the bar shows.
async function pressedAndDrawn($: Engine, ui: Mounted, ...keys: string[]): Promise<Mounted> {
  let drawn = ui
  for (const key of keys) {
    await drawn.press({ key })
    await drawn.unmount()
    drawn = await $.ui.mount({ ...bandOf(), surface: 'desktop' })
  }
  return drawn
}

// The session list open in the main chat.
async function sessionList($: Engine, called: Called[]): Promise<Mounted> {
  return pressedAndDrawn($, await barAfterRead($, called), 'session-list-button')
}

const TOGGLE = 'session-backlog-toggle'

// The session list open, with the Backlog opened beside it.
async function backlog($: Engine, called: Called[]): Promise<Mounted> {
  return pressedAndDrawn($, await sessionList($, called), TOGGLE)
}

const labelOf = async (ui: Mounted, key: string) => (await ui.find({ type: 'Button', key }))?.props.label
const startKey = (title: string) => `session-backlog-start-${title}`
const isShown = async (ui: Mounted, key: string) => Boolean(await ui.find({ type: 'Button', key }))
// What each call named, without the chat's own fields every cdd call carries.
const namedIn = ({ chat_folder: _folder, conversation_id: _chat, ...named }: Record<string, unknown>) => named
const startsOf = (called: Called[]) => called.filter(call => call.tool === 'backlog-item.start').map(call => namedIn(call.args))

// Show Backlog Items In Session List

test('the session list shows the Backlog closed, saying how many items it holds', async ($, on) => {
  const { called } = mainChat(on, [PAYMENT_RETRY, CHECKOUT_FLOW])

  const ui = await sessionList($, called)

  expect([await labelOf(ui, TOGGLE), await isShown(ui, startKey('Payment retry'))]).toEqual(['◂ ☰ Backlog (2)', false])
  await ui.unmount()
})

test('opening the Backlog shows its items in a BACKLOG box', async ($, on) => {
  const { called } = mainChat(on, [PAYMENT_RETRY, CHECKOUT_FLOW])

  const ui = await backlog($, called)

  expect([Boolean(await ui.find({ type: 'Text', text: 'BACKLOG' })), await isShown(ui, startKey('Payment retry')), await isShown(ui, startKey('Checkout flow'))]).toEqual([true, true, true])
  await ui.unmount()
})

test('the BACKLOG box opens beside the session list, which keeps its rows', async ($, on) => {
  const { called } = mainChat(on, [PAYMENT_RETRY, CHECKOUT_FLOW])

  const ui = await backlog($, called)

  expect([Boolean(await ui.find({ type: 'Box', key: 'session-backlog-box' })), Boolean(await ui.find({ type: 'Box', key: 'session-list' })), await labelOf(ui, TOGGLE)]).toEqual([true, true, '▸ ☰ Backlog (2)'])
  await ui.unmount()
})

test('the Backlog is closed again each time the session list opens', async ($, on) => {
  const { called } = mainChat(on, [PAYMENT_RETRY])

  const ui = await pressedAndDrawn($, await backlog($, called), 'session-list-button', 'session-list-button')

  expect(await isShown(ui, startKey('Payment retry'))).toBe(false)
  await ui.unmount()
})

// Seed: twelve items in a chat whose band has 11 rows, which leaves the BACKLOG box room for seven.
const TWELVE_IDEAS = Array.from({ length: 12 }, (_, place) => ({ title: `Idea ${place + 1}`, children: [] }))
const SHORT_BAND_ROWS = 11
const PAGE_UP = 'session-backlog-box-up'
const PAGE_DOWN = 'session-backlog-box-down'
const isSaid = async (ui: Mounted, text: string) => Boolean(await ui.find({ type: 'Text', text }))

test('a Backlog taller than the chat has room for shows its first items, and says which of how many', async ($, on) => {
  const { called } = mainChat(on, TWELVE_IDEAS, {}, '', SHORT_BAND_ROWS)

  const ui = await backlog($, called)

  expect([await isShown(ui, startKey('Idea 7')), await isShown(ui, startKey('Idea 8')), await isSaid(ui, '1–7 of 12')]).toEqual([true, false, true])
  await ui.unmount()
})

test('paging a tall Backlog down shows the items after them, as far as its last', async ($, on) => {
  const { called } = mainChat(on, TWELVE_IDEAS, {}, '', SHORT_BAND_ROWS)

  const ui = await pressedAndDrawn($, await backlog($, called), PAGE_DOWN)

  expect([await isShown(ui, startKey('Idea 5')), await isShown(ui, startKey('Idea 12')), await isSaid(ui, '6–12 of 12')]).toEqual([false, true, true])
  await ui.unmount()
})

test('paging a tall Backlog up again shows its first items', async ($, on) => {
  const { called } = mainChat(on, TWELVE_IDEAS, {}, '', SHORT_BAND_ROWS)

  const ui = await pressedAndDrawn($, await backlog($, called), PAGE_DOWN, PAGE_UP)

  expect([await isShown(ui, startKey('Idea 1')), await isShown(ui, startKey('Idea 8'))]).toEqual([true, false])
  await ui.unmount()
})

test('a tall Backlog opens on its first items each time it opens', async ($, on) => {
  const { called } = mainChat(on, TWELVE_IDEAS, {}, '', SHORT_BAND_ROWS)

  const ui = await pressedAndDrawn($, await backlog($, called), PAGE_DOWN, TOGGLE, TOGGLE)

  expect(await isShown(ui, startKey('Idea 1'))).toBe(true)
  await ui.unmount()
})

test('a Backlog the chat has room for shows every item, with nothing to page', async ($, on) => {
  const { called } = mainChat(on, [PAYMENT_RETRY, CHECKOUT_FLOW])

  const ui = await backlog($, called)

  expect([await isShown(ui, PAGE_UP), await isShown(ui, PAGE_DOWN)]).toEqual([false, false])
  await ui.unmount()
})

test('an item whose title is longer than the box has room for shows it cut short, ending in an ellipsis', async ($, on) => {
  const title = 'Chat bar shows the robots queue as clearly as a drawn card view'
  const { called } = mainChat(on, [{ title, children: [] }])

  const ui = await backlog($, called)

  expect(await labelOf(ui, startKey(title))).toBe('☰ Chat bar shows the robots queu…')
  await ui.unmount()
})

test('a parent shows as one item, with nothing that opens its child items', async ($, on) => {
  const { called } = mainChat(on, [PAYMENT_RETRY, CHECKOUT_FLOW])

  const ui = await backlog($, called)

  expect([await isShown(ui, startKey('Checkout flow')), await isShown(ui, 'session-backlog-open-Checkout flow'), await isShown(ui, startKey('Address form'))]).toEqual([true, false, false])
  await ui.unmount()
})

test('an empty Backlog shows no Backlog row', async ($, on) => {
  const { called } = mainChat(on, [])

  const ui = await sessionList($, called)

  expect(await ui.find({ type: 'Button', key: TOGGLE })).toBeUndefined()
  await ui.unmount()
})

// Start Backlog Item From Session List

test('starting an item starts it on the whole repository, then opens its ticket as Open Session does', async ($, on) => {
  const { called } = mainChat(on, [PAYMENT_RETRY])

  const ui = await pressedAndDrawn($, await backlog($, called), startKey('Payment retry'))

  expect(called.filter(call => ['backlog-item.start', 'ticket.activate'].includes(call.tool)).map(call => ({ tool: call.tool, args: namedIn(call.args) }))).toEqual([
    { tool: 'backlog-item.start', args: { backlog_item: 'Payment retry' } },
    { tool: 'ticket.activate', args: { ticket: 'payment-retry' } },
  ])
  await ui.unmount()
})

test('starting an item closes the session list', async ($, on) => {
  const { called } = mainChat(on, [PAYMENT_RETRY])

  const ui = await pressedAndDrawn($, await backlog($, called), startKey('Payment retry'))

  expect(await ui.find({ type: 'Text', text: 'BACKLOG' })).toBeUndefined()
  await ui.unmount()
})

test('starting an item says it started in Discovery', async ($, on) => {
  const { called, toasts } = mainChat(on, [PAYMENT_RETRY])

  const ui = await pressedAndDrawn($, await backlog($, called), startKey('Payment retry'))

  expect(toasts).toContain('Payment retry started in Discovery')
  await ui.unmount()
})

// The folder button's picker closes the session list, as a press outside it does, so the Person opens it again.
test('starting an item starts it on the folder chosen beside the new session name', async ($, on) => {
  const { called } = mainChat(on, [PAYMENT_RETRY], {}, `${FOLDER}/app/payments`)

  const ui = await pressedAndDrawn($, await sessionList($, called), 'new-session-folder', 'session-list-button', TOGGLE, startKey('Payment retry'))

  expect(startsOf(called)).toEqual([{ backlog_item: 'Payment retry', path: `${FOLDER}/app/payments` }])
  await ui.unmount()
})

test('a started item leaves no folder chosen beside the new session name', async ($, on) => {
  const { called } = mainChat(on, [PAYMENT_RETRY], {}, `${FOLDER}/app/payments`)

  const ui = await pressedAndDrawn($, await sessionList($, called), 'new-session-folder', 'session-list-button', TOGGLE, startKey('Payment retry'), 'session-list-button')

  expect(await ui.find({ type: 'Text', text: 'in app/payments' })).toBeUndefined()
  await ui.unmount()
})

test('starting a parent starts it, and with it its child items', async ($, on) => {
  const { called } = mainChat(on, [CHECKOUT_FLOW])

  const ui = await pressedAndDrawn($, await backlog($, called), startKey('Checkout flow'))

  expect(startsOf(called)).toEqual([{ backlog_item: 'Checkout flow' }])
  await ui.unmount()
})

test('a start refused shows why on the failure line, and opens no ticket', async ($, on) => {
  const { called } = mainChat(on, [PAYMENT_RETRY], { start: 'BacklogItemNotFoundError: no backlog item titled Payment retry' })

  const ui = await pressedAndDrawn($, await backlog($, called), startKey('Payment retry'))

  expect([Boolean(await ui.find({ type: 'Text', text: /Payment retry did not start/ })), called.some(call => call.tool === 'ticket.activate')]).toEqual([true, false])
  await ui.unmount()
})

test('a started item whose ticket does not open says it did not open', async ($, on) => {
  const { called } = mainChat(on, [PAYMENT_RETRY], { activate: 'WorktreeNotFoundError: the worktree is held open' })

  const ui = await pressedAndDrawn($, await backlog($, called), startKey('Payment retry'))

  expect(Boolean(await ui.find({ type: 'Text', text: /payment-retry did not open/ }))).toBe(true)
  await ui.unmount()
})
