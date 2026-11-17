import { expect, test } from 'claude-code/testing'

const BAND = {
  plugin: 'prompt-queue',
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

// What play sends when a turn ends: the queue rides beside it.
const ASK_FOR_NEXT = 'Take the next prompt on the queue.'

const QUEUED = [
  { id: 'a', text: 'Write the scenarios' },
  { id: 'b', text: 'Run the unit tier' },
]

type TestOn = Parameters<Extract<Parameters<typeof test>[1], (...args: never[]) => unknown>>[1]

// The chat the tests run in, as the engine names it.
const CHAT = 'chat-1'

type Prompt = { id: string; text: string }

/** The cdd server's prompt-queue tools for one chat, in memory: the same operations as tools/prompt_queue's
 * PromptQueue, each answering the queue. */
function promptQueueTools(prompts: Prompt[]) {
  let added = 0
  const answer = () => ({ chat: CHAT, prompts })
  const at = (id: unknown) => prompts.findIndex(prompt => prompt.id === id)
  const operations: Record<string, (args: Record<string, unknown>) => unknown> = {
    show: () => answer(),
    add: args => operations.add_all!({ texts: [args.text] }),
    add_all: args => {
      for (const text of (args.texts as string[]).filter(text => text.trim())) prompts.push({ id: `added-${++added}`, text: text.trim() })
      return answer()
    },
    edit: args => {
      prompts[at(args.prompt)]!.text = String(args.text)
      return answer()
    },
    move: args => {
      const [moving] = prompts.splice(at(args.prompt), 1)
      prompts.splice(Math.max(0, Math.min(Number(args.to), prompts.length)), 0, moving!)
      return answer()
    },
    remove: args => {
      prompts.splice(at(args.prompt), 1)
      return answer()
    },
    clear: () => {
      prompts.splice(0)
      return answer()
    },
    done: args => {
      prompts.splice(at(args.prompt), 1)
      return answer()
    },
  }
  return { prompts, call: (tool: string, args: Record<string, unknown>) => operations[tool.replace('prompt-queue.', '')]!(args) }
}

/** The mod's stored values, kept in memory as the engine keeps them: each write raises the value's version; the queue
 * itself is the cdd server's, through prompt-queue's tools. */
function seedQueue(on: TestOn, isExpanded: boolean, queuedByKey = '', queued = QUEUED, isPlaying = false, editingId = '', askedAbout = '', servers = ['cdd']) {
  const server = promptQueueTools(queued.map(prompt => ({ ...prompt })))
  on('session.id', () => ({ value: CHAT }))
  on('session.root', () => ({ value: 'C:/work' }))
  on('mcp.call', (_, e) => {
    const { server: called, tool, args } = e as { server: string; tool: string; args: Record<string, unknown> }
    if (!servers.includes(called)) {
      return { deny: `no MCP server ${called}` }
    }
    return { value: { content: [{ type: 'text', text: JSON.stringify(server.call(tool, args)) }], isError: false } }
  })
  const stored: Record<string, { value: unknown; version: number }> = {
    queue: { value: { chat: CHAT, prompts: [...server.prompts] }, version: 1 },
    isExpanded: { value: isExpanded, version: 1 },
    queuedByKey: { value: queuedByKey, version: 1 },
    isPlaying: { value: isPlaying, version: 1 },
    editingId: { value: editingId, version: 1 },
    askedAbout: { value: askedAbout, version: 1 },
  }
  on('state.get', (_, e) => {
    const key = (e as { key: string }).key
    return { value: stored[key] ?? { value: undefined, version: 0 } }
  })
  on('state.set', (_, e) => {
    const { key, value } = e as { key: string; value: unknown }
    const version = (stored[key]?.version ?? 0) + 1
    stored[key] = { value, version }
    return { value: { isSet: true, version } }
  })

  return { get prompts() { return server.prompts }, stored }
}

for (const surface of ['desktop', 'terminal'] as const) {
  test(`the queue at rest shows the stack with its count, on ${surface}`, async ($, on) => {
    seedQueue(on, false)

    const ui = await $.ui.mount({ ...BAND, surface })

    expect(await ui.find({ type: 'Button', key: 'queue-stack' })).toBeDefined()
    await ui.unmount()
  })

  test(`the open queue lists every queued prompt, on ${surface}`, async ($, on) => {
    seedQueue(on, true)

    const ui = await $.ui.mount({ ...BAND, surface })

    expect(await ui.find({ type: 'Button', key: 'queue-clear' })).toBeDefined()
    await ui.unmount()
  })

  test(`the open queue stacks a card for each queued task, on ${surface}`, async ($, on) => {
    seedQueue(on, true)

    const ui = await $.ui.mount({ ...BAND, surface })

    expect(await ui.find({ type: 'Button', key: 'remove-b' })).toBeDefined()
    await ui.unmount()
  })

  test(`play asks the agent to take the next prompt and leaves it on the queue, on ${surface}`, async ($, on) => {
    const seeded = seedQueue(on, true)
    const submitted: string[] = []
    on('prompt.submit', (_, e) => {
      submitted.push(e.text)
      return { text: e.text }
    })

    const ui = await $.ui.mount({ ...BAND, surface })
    await ui.press({ key: 'queue-play' })

    expect(submitted).toEqual([ASK_FOR_NEXT])
    expect(seeded.prompts.map(prompt => prompt.text)).toEqual(['Write the scenarios', 'Run the unit tier'])
    await ui.unmount()
  })
}

// Seen 2026-11-17: a long pasted list queued with Alt+Enter was still sent to the chat.
test('the submission that follows Alt+Enter does not enter when the desktop sends its lines with other endings', async ($, on) => {
  seedQueue(on, false, ['1. Rules fix not checked live.  ', '2. No Go to file on a fold-out.'].join(String.fromCharCode(13, 10)))
  on('prompt.submit', (_, e) => ({ text: e.text }))

  const submitted = await $.prompt.submit({ text: ['1. Rules fix not checked live.', '2. No Go to file on a fold-out.', ''].join(String.fromCharCode(10)), wait: false, origin: { kind: 'composer' } })

  expect(submitted.drop).toBe('Queued for later')
})

test('the submission that follows Alt+Enter does not enter, as its draft is queued', async ($, on) => {
  seedQueue(on, false, 'Run the heavy tier')
  on('prompt.submit', (_, e) => ({ text: e.text }))

  const submitted = await $.prompt.submit({ text: 'Run the heavy tier', wait: false, origin: { kind: 'composer' } })

  expect(submitted.drop).toBe('Queued for later')
})

test('a queued slash command runs as the command, not as a prompt', async ($, on) => {
  seedQueue(on, true, '', [{ id: 'c', text: '/actions-generate stories-story-map format=drawio' }])
  const ran: { command: string; args: string }[] = []
  on('command.run', (_, e) => {
    ran.push({ command: e.command, args: e.args })
    return {}
  })

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  await ui.press({ key: 'queue-play' })

  expect(ran).toEqual([{ command: 'actions-generate', args: 'stories-story-map format=drawio' }])
  await ui.unmount()
})

for (const isPlaying of [true, false]) {
  test(`a prompt ${isPlaying ? 'carries the queue and how to work through it while playing' : 'carries no queue while paused'}`, async ($, on) => {
    seedQueue(on, false, '', QUEUED, isPlaying)
    const carried: (readonly string[] | undefined)[] = []
    on('prompt.submit', (_, e) => {
      carried.push(e.context)
      return { text: e.text }
    })

    await $.prompt.submit({ text: 'Fix the Files app', wait: false, origin: { kind: 'composer' } })

    const queueBlock = carried[0]?.find(block => block.includes('prompt-queue.done'))
    expect(queueBlock !== undefined).toBe(isPlaying)
    if (isPlaying) {
      expect(queueBlock).toContain('1. [a] Write the scenarios')
      expect(queueBlock).toContain('2. [b] Run the unit tier')
    }
  })
}

test("the queue is read from the cdd plugin's server in a chat whose project names no cdd server of its own", async ($, on) => {
  const seeded = seedQueue(on, true, '', QUEUED, false, '', '', ['plugin:cdd:cdd'])

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  await ui.press({ key: 'queue-clear' })

  expect(seeded.prompts).toEqual([])
  await ui.unmount()
})

test('a prompt being edited is left out of the queue the agent sees', async ($, on) => {
  seedQueue(on, false, '', QUEUED, true, 'a')
  const carried: string[] = []
  on('prompt.submit', (_, e) => {
    carried.push(...(e.context ?? []))
    return { text: e.text }
  })

  await $.prompt.submit({ text: 'Fix the Files app', wait: false, origin: { kind: 'composer' } })

  expect(carried.join()).not.toContain('Write the scenarios')
  expect(carried.join()).toContain('1. [b] Run the unit tier')
})

test('play pauses when the agent left the prompt it was asked to take on the queue', async ($, on) => {
  const seeded = seedQueue(on, false, '', QUEUED, true, '', 'a')
  const submitted: string[] = []
  on('prompt.submit', (_, e) => {
    submitted.push(e.text)
    return { text: e.text }
  })
  on('turn.complete', () => ({ text: 'Done.' }))

  await $.turn.complete(FINISHED_TURN)

  expect(submitted).toEqual([])
  expect(seeded.stored.isPlaying?.value).toBe(false)
})

/** A turn's end submits the next prompt without awaiting it, as awaiting would hold the turn open; the submission's hooks
 * read the queue first, so the test lets that unawaited work run before it looks. */
async function unawaitedWorkSettled(): Promise<void> {
  for (let turn = 0; turn < 100; turn++) await Promise.resolve()
}

const FINISHED_TURN = { answer: 'Done.', durationMs: 1, isAborted: false, turnId: 't1', reason: 'answer' } as const

for (const isPlaying of [true, false]) {
  test(`a finished turn ${isPlaying ? 'asks the agent for the next prompt while playing' : 'asks nothing while paused'}`, async ($, on) => {
    seedQueue(on, false, '', QUEUED, isPlaying)
    const submitted: string[] = []
    on('prompt.submit', (_, e) => {
      submitted.push(e.text)
      return { text: e.text }
    })
    on('turn.complete', () => ({ text: 'Done.' }))

    await $.turn.complete(FINISHED_TURN)
    await unawaitedWorkSettled()

    expect(submitted).toEqual(isPlaying ? [ASK_FOR_NEXT] : [])
  })
}

test('the pencil on a card puts its prompt in the prompt box to be edited', async ($, on) => {
  seedQueue(on, true)
  const filled: string[] = []
  on('prompt.fill', (_, e) => {
    filled.push(e.text)
    return { isFilled: true }
  })

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  await ui.press({ key: 'edit-b' })

  expect(filled).toEqual(['Run the unit tier'])
  await ui.unmount()
})

test('adding while a prompt is being edited puts the draft back in its place', async ($, on) => {
  const written = seedQueue(on, true, '', QUEUED, false, 'a')
  on('prompt.read', () => ({ value: { text: 'Write the scenarios again', cursor: 25 } }))
  on('prompt.fill', () => ({ isFilled: true }))

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  await ui.press({ key: 'queue-add' })

  expect(written.prompts).toEqual([{ id: 'a', text: 'Write the scenarios again' }, QUEUED[1]])
  await ui.unmount()
})

// What a model call cost and where a command ran, which the queue's tests do not read.
const NO_USAGE = { input_tokens: 0, output_tokens: 0, cache_read_input_tokens: 0, cache_creation_input_tokens: 0 }
const TERMINAL = { isFullscreen: false, columns: 80 }

// Seen 2026-11-17: /queue with a pasted list of outstanding items answered "Queued 0 prompt(s)".
const PASTED_LIST = [
  '2. Right-click Go to file on a fold-out.',
  '3. Files e2e not re-run since the connector fold-outs.',
  '',
  'Session roots setup',
  '7. No story tests for the three Choose Session And Practice Roots scenarios.',
].join(String.fromCharCode(10))

test('/queue given a pasted list queues each item in order, without asking the model', async ($, on) => {
  const store = seedQueue(on, false, '', [])
  let isModelAsked = false
  on('model.fork', () => {
    isModelAsked = true
    return { value: { isAnswered: true, text: '[]', usage: NO_USAGE } }
  })

  const ran = await $.command.run({ command: 'queue', args: PASTED_LIST, origin: { kind: 'composer' }, presentation: TERMINAL })
  const queued = store.prompts as { text: string }[]

  expect([ran.text, queued.map(prompt => prompt.text), isModelAsked]).toEqual([
    'Queued 3 prompt(s).',
    [
      'Right-click Go to file on a fold-out.',
      'Files e2e not re-run since the connector fold-outs.',
      'No story tests for the three Choose Session And Practice Roots scenarios.',
    ],
    false,
  ])
})

test('/queue whose plan holds no prompt says why', async ($, on) => {
  seedQueue(on, false, '', [])
  on('model.fork', () => ({ value: { isAnswered: true, text: 'Nothing is left to do.', usage: NO_USAGE } }))

  const ran = await $.command.run({ command: 'queue', args: '', origin: { kind: 'composer' }, presentation: TERMINAL })

  expect(ran.text).toBe('Queued 0 prompt(s): the model proposed none. It answered: Nothing is left to do.')
})
