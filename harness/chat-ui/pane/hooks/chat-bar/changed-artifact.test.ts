// (S:system) Claude Code --> Check Graph Rules When An Artifact Changes
// When the agent edits a file in the session, the chat bar asks the session to run the graph rules on it
// (session.check_changed_artifact) with no explicit validate, then reads the board again, so its violation count follows
// the edit.
import { expect, test } from 'claude-code/testing'

type TestOn = Parameters<Extract<Parameters<typeof test>[1], (...args: never[]) => unknown>>[1]
type TestEngine = Parameters<Parameters<typeof test>[1]>[0]

// Seed: the folder the chat works in, and the story map the agent edits in it.
const FOLDER = 'C:/work/shop'
const STORY_MAP = `${FOLDER}/.context/story-map.md`
const SESSION_FILE = `${FOLDER}/.sessions/checkout-flow/session.json`

// Seed: the checkout-flow session, active on the board, as board.overview sends it.
const CHECKOUT_FLOW = {
  title: 'checkout-flow', last_activity: '', name: 'checkout-flow', is_main: false, text: '', tags: [], children: [], is_pulled_out: false, is_stacked: false,
  session: { name: 'checkout-flow', session_file: SESSION_FILE, title: 'checkout-flow', repo_name: 'shop', branch: 'checkout-flow', is_repository: true, root: FOLDER, scope: '', parent: '', workpath: '', practices: {}, handoff: '' },
  progress: [], column: { name: 'Discovery' }, is_closed: false, is_active: true, is_open: true, parent_choices: [], drop_targets: [], is_done: false,
  next: null, agent_context: '', worktree: '', new_chat_link: '', session_path: '', working_chat: null, stage_work: [], next_place: null, previous_place: null,
}
const OVERVIEW = { project: 'shop', is_clone: true, folder: FOLDER, practices: [], fidelities: [], columns: [{ name: 'Discovery', tickets: [{ name: 'checkout-flow' }] }], active: CHECKOUT_FLOW }

const FINISHED_TURN = { answer: 'Done.', durationMs: 1, isAborted: false, turnId: 't1', reason: 'answer' } as const
const WAIT_MS = 20
const WAITS = 25

/** A chat in FOLDER whose board shows checkout-flow active; each cdd tool called is kept, with its arguments. */
function chatOnCheckoutFlow(on: TestOn) {
  const called: { tool: string; args: Record<string, unknown> }[] = []
  const stored: Record<string, { value: unknown; version: number }> = {}
  const keyOf = (e: unknown) => {
    const { plugin, key } = e as { plugin: string; key: string }
    return `${plugin}:${key}`
  }
  const answer = (value: unknown) => ({ value: { content: [{ type: 'text', text: JSON.stringify(value) }], isError: false } })
  on('session.root', () => ({ value: FOLDER }))
  on('session.id', () => ({ value: 'chat-1' }))
  on('session.messages', () => ({ value: [] }))
  on('turn.complete', () => ({ text: 'Done.' }))
  on('mcp.call', (_, e) => {
    const { tool, args } = e as { tool: string; args: Record<string, unknown> }
    called.push({ tool, args })
    if (tool === 'board.overview') return answer(OVERVIEW)
    if (tool === 'session.check_changed_artifact') return answer({ path: args.path, checked: ['stories-story-map'] })
    return { value: { content: [{ type: 'text', text: 'not stubbed' }], isError: true } }
  })
  on('tool.call', (_, e) => ({ result: { filePath: (e as { file_path?: string }).file_path ?? '' }, isError: (e as { old_string?: string }).old_string === 'missing' }))
  on('process.run', () => ({ value: { exitCode: 0, stdout: '', stderr: '' } }))
  on('tool.list', () => ({ value: [] }))
  on('ui.status', () => ({ value: undefined }))
  on('ui.toast', () => ({ value: undefined }))
  on('ui.invalidate', () => ({ value: undefined }))
  on('clock.after', () => new Promise(() => undefined))
  on('clock.every', () => new Promise(() => undefined))
  on('clock.sleep', () => ({ value: undefined }))
  on('state.get', (_, e) => ({ value: stored[keyOf(e)] ?? { value: undefined, version: 0 } }))
  on('state.set', (_, e) => {
    const key = keyOf(e)
    const version = (stored[key]?.version ?? 0) + 1
    stored[key] = { value: (e as { value: unknown }).value, version }
    return { value: { isSet: true, version } }
  })
  return { called }
}

// The bar reads the board after a turn ends; the check runs without holding the edit up, so each wait looks for a call.
async function waitFor(called: { tool: string }[], isDone: () => boolean): Promise<void> {
  for (let tries = 0; tries < WAITS && !isDone(); tries += 1) await new Promise(resolve => setTimeout(resolve, WAIT_MS))
  await new Promise(resolve => setTimeout(resolve, WAIT_MS))
}

async function boardRead($: TestEngine, called: { tool: string }[]): Promise<void> {
  await $.turn.complete(FINISHED_TURN)
  await waitFor(called, () => called.some(call => call.tool === 'board.overview'))
}

const checksOf = (called: { tool: string; args: Record<string, unknown> }[]) => called.filter(call => call.tool === 'session.check_changed_artifact')

test('an edit of a file asks the session to check it as a changed artifact', async ($, on) => {
  const { called } = chatOnCheckoutFlow(on)
  await boardRead($, called)

  await $.tool.call({ tool: 'Edit', file_path: STORY_MAP, old_string: 'Order Placement', new_string: 'Place Order' })
  await waitFor(called, () => checksOf(called).length > 0)

  expect(checksOf(called).map(call => [call.args.session, call.args.path])).toEqual([[SESSION_FILE, STORY_MAP]])
})

test('the chat bar reads the board again once the changed artifact is checked', async ($, on) => {
  const { called } = chatOnCheckoutFlow(on)
  await boardRead($, called)

  await $.tool.call({ tool: 'Write', file_path: STORY_MAP, content: '# Story Map\n' })
  await waitFor(called, () => {
    const checked = called.findIndex(call => call.tool === 'session.check_changed_artifact')
    return checked !== -1 && called.slice(checked + 1).some(call => call.tool === 'board.overview')
  })

  const checked = called.findIndex(call => call.tool === 'session.check_changed_artifact')
  expect(checked === -1 ? [] : called.slice(checked + 1).map(call => call.tool)).toContain('board.overview')
})

test('an edit that failed checks nothing', async ($, on) => {
  const { called } = chatOnCheckoutFlow(on)
  await boardRead($, called)

  await $.tool.call({ tool: 'Edit', file_path: STORY_MAP, old_string: 'missing', new_string: 'Place Order' })
  await waitFor(called, () => checksOf(called).length > 0)

  expect(checksOf(called)).toEqual([])
})

test('a read of a file checks nothing', async ($, on) => {
  const { called } = chatOnCheckoutFlow(on)
  await boardRead($, called)

  await $.tool.call({ tool: 'Read', file_path: STORY_MAP })
  await waitFor(called, () => checksOf(called).length > 0)

  expect(checksOf(called)).toEqual([])
})
