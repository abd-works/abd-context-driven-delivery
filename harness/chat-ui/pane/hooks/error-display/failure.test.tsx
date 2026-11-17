// CDD's one failure line above the chat bar shows the prompt queue's failures too, with the same Fix and ✕: the queue is
// a plugin of its own and only its owner writes a value, so the queue keeps its latest failure and the board reads it.
// Fix and ✕ hide that failure through a value the board owns, the id of the queue failure it last handled.
import { expect, test } from 'claude-code/testing'

const BAND = {
  plugin: 'cdd-board',
  component: 'AbovePrompt',
  requestId: 'above-prompt',
  props: {
    hasSurvey: false,
    isCollapsed: false,
    isWorking: false,
    maxRows: 24,
    bodyColumns: 80,
    scroll: { offset: 0, bodyRows: 24 },
    view: {},
  },
} as const

type TestOn = Parameters<Extract<Parameters<typeof test>[1], (...args: never[]) => unknown>>[1]

// Seed: the queue's latest failure, as the prompt queue keeps it.
const QUEUE_FAILURE = {
  id: 3,
  failure: 'The queue did not change: no MCP server plugin:cdd:cdd',
  context: 'Calling prompt-queue.clear on the cdd server, tried as cdd then plugin:cdd:cdd',
}

/** A chat whose prompt queue holds a failure: every stored value in memory, kept under its plugin's name; the cdd
 * server answers nothing, so the bar draws its problem line and the failure line above it. */
function chatWithQueueFailure(on: TestOn) {
  const stored: Record<string, { value: unknown; version: number }> = {
    'prompt-queue:failure': { value: QUEUE_FAILURE, version: 1 },
  }
  const keyOf = (e: unknown) => {
    const { plugin, key } = e as { plugin: string; key: string }
    return `${plugin}:${key}`
  }
  on('session.root', () => ({ value: 'C:/work' }))
  on('session.id', () => ({ value: 'chat-1' }))
  on('mcp.call', () => ({ deny: 'no MCP server cdd' }))
  on('process.run', () => ({ value: { exitCode: 128, stdout: '', stderr: 'fatal: not a git repository' } }))
  on('clock.after', () => new Promise(() => undefined))
  on('clock.every', () => new Promise(() => undefined))
  on('state.get', (_, e) => ({ value: stored[keyOf(e)] ?? { value: undefined, version: 0 } }))
  on('state.set', (_, e) => {
    const key = keyOf(e)
    const version = (stored[key]?.version ?? 0) + 1
    stored[key] = { value: (e as { value: unknown }).value, version }
    return { value: { isSet: true, version } }
  })
  const ran: { command: string; args: string }[] = []
  on('command.run', (_, e) => {
    ran.push({ command: e.command, args: e.args })
    return {}
  })
  return { stored, ran }
}

async function textOf(ui: { find: (query: object) => Promise<{ children: unknown[] } | undefined> }): Promise<string> {
  return JSON.stringify((await ui.find({ type: 'Box', key: 'failure' }))?.children ?? null)
}

test("the chat bar's failure line shows the prompt queue's failure, with its context and Fix", async ($, on) => {
  chatWithQueueFailure(on)

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })

  expect(await textOf(ui)).toContain(QUEUE_FAILURE.failure)
  expect(await textOf(ui)).toContain(QUEUE_FAILURE.context)
  expect(await ui.find({ type: 'Button', key: 'fix-failure' })).toBeDefined()
  await ui.unmount()
})

test("Fix on the queue's failure sends it to the debug command, and the line no longer shows it", async ($, on) => {
  const { ran } = chatWithQueueFailure(on)

  const pressed = await $.ui.mount({ ...BAND, surface: 'desktop' })
  await pressed.press({ key: 'fix-failure' })
  await pressed.unmount()
  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })

  expect(ran.map(run => run.command)).toEqual(['space-session-debug-session'])
  expect(ran[0]!.args).toContain(QUEUE_FAILURE.failure)
  expect(await ui.find({ type: 'Button', key: 'fix-failure' })).toBeUndefined()
  await ui.unmount()
})

test("✕ on the queue's failure hides it, leaving the queue's own value as the queue wrote it", async ($, on) => {
  const { stored } = chatWithQueueFailure(on)

  const pressed = await $.ui.mount({ ...BAND, surface: 'desktop' })
  await pressed.press({ key: 'dismiss-failure' })
  await pressed.unmount()
  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })

  expect(await ui.find({ type: 'Button', key: 'fix-failure' })).toBeUndefined()
  expect(stored['prompt-queue:failure']!.value).toEqual(QUEUE_FAILURE)
  await ui.unmount()
})

test("a newer failure from the queue shows again after an older one was hidden", async ($, on) => {
  const { stored } = chatWithQueueFailure(on)

  const pressed = await $.ui.mount({ ...BAND, surface: 'desktop' })
  await pressed.press({ key: 'dismiss-failure' })
  await pressed.unmount()
  stored['prompt-queue:failure'] = { value: { ...QUEUE_FAILURE, id: 4, failure: 'Not sent: the chat is closed' }, version: 2 }
  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })

  expect(await textOf(ui)).toContain('Not sent: the chat is closed')
  await ui.unmount()
})
