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
// How the queue beside a prompt opens, which tells it from the note about the prompt just sent.
const QUEUE_HEADING = "This chat's prompt queue"
const ASK_FOR_NEXT = 'Take the next prompt on the queue.'

const QUEUED = [
  { id: 'a', text: 'Write the scenarios' },
  { id: 'b', text: 'Run the unit tier' },
]

type TestOn = Parameters<Extract<Parameters<typeof test>[1], (...args: never[]) => unknown>>[1]

// The chat the tests run in, as the engine names it.
const CHAT = 'chat-1'

type Step = { text: string; state: 'pending' | 'in_progress' | 'done' }
type Prompt = { id: string; text: string; steps?: Step[]; attachments?: string[]; is_done?: boolean }

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
      const unfinished = prompts.filter(prompt => !prompt.is_done)
      prompts.splice(0, prompts.length, ...(unfinished.length === prompts.length ? [] : unfinished))
      return answer()
    },
    done: args => {
      prompts[at(args.prompt)]!.is_done = true
      return answer()
    },
    set_steps: args => {
      prompts[at(args.prompt)]!.steps = args.steps as Step[]
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

    const queueBlock = carried[0]?.find(block => block.includes(QUEUE_HEADING))
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
  for (let turn = 0; turn < 1000; turn++) await Promise.resolve()
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

const NO_SERVER_FAILURE = 'The queue did not change: prompt-queue: $.mcp.call: no MCP server plugin:cdd:cdd'

/** A chat no cdd server answers, where pressing clear fails: the box drawn again after the press, as its next render
 * draws it, with the failure the press stored. */
async function boxAfterFailedClear($: Parameters<Parameters<typeof test>[1]>[0], on: TestOn) {
  const seeded = seedQueue(on, true, '', QUEUED, false, '', '', [])
  const pressed = await $.ui.mount({ ...BAND, surface: 'desktop' })
  await pressed.press({ key: 'queue-clear' })
  await pressed.unmount()

  return { seeded, ui: await $.ui.mount({ ...BAND, surface: 'desktop' }) }
}

test("a queue call no cdd server answers keeps its failure, numbered, for CDD's shared failure line to show", async ($, on) => {
  const { seeded, ui } = await boxAfterFailedClear($, on)

  expect(seeded.stored.failure?.value).toEqual({
    id: 1,
    failure: NO_SERVER_FAILURE,
    context: 'Calling prompt-queue.clear on the cdd server, tried as cdd then plugin:cdd:cdd',
  })
  await ui.unmount()
})

test('each new queue failure gets the next number, so the shared line shows it again after an older one was handled', async ($, on) => {
  const { seeded, ui } = await boxAfterFailedClear($, on)

  await ui.press({ key: 'queue-clear' })

  expect((seeded.stored.failure?.value as { id: number }).id).toBe(2)
  await ui.unmount()
})

test('the queue box draws no failure line of its own, leaving Fix and ✕ to the shared line', async ($, on) => {
  const { ui } = await boxAfterFailedClear($, on)

  expect(await ui.find({ type: 'Button', key: 'queue-fix' })).toBeUndefined()
  expect(await ui.find({ type: 'Box', key: 'queue-failure' })).toBeUndefined()
  await ui.unmount()
})


const PLAN_TOOL = 'mcp__ccd_turn__update_plan'
const PLANNED = [
  { content: 'Read the epic', status: 'in_progress' },
  { content: 'Write the stories', status: 'pending' },
]

/** The desktop app's task list tool, answered as the engine answers a tool call that ran. */
function planToolAnswers(on: TestOn): void {
  on('tool.call', () => ({ result: { content: [{ type: 'text', text: 'Plan shown.' }] } }))
}

test('the task list the agent sets is copied onto the prompt it was asked to take', async ($, on) => {
  const seeded = seedQueue(on, true, '', QUEUED, true, '', 'a')
  planToolAnswers(on)

  await $.tool.call({ tool: PLAN_TOOL, items: PLANNED })

  expect(seeded.prompts[0]!.steps).toEqual([
    { text: 'Read the epic', state: 'in_progress' },
    { text: 'Write the stories', state: 'pending' },
  ])
})

test('advancing the task list finishes the step being worked and starts the next on the prompt', async ($, on) => {
  const seeded = seedQueue(on, true, '', QUEUED, true, '', 'a')
  planToolAnswers(on)

  await $.tool.call({ tool: PLAN_TOOL, items: PLANNED })
  await $.tool.call({ tool: PLAN_TOOL, advance: true })

  expect(seeded.prompts[0]!.steps).toEqual([
    { text: 'Read the epic', state: 'done' },
    { text: 'Write the stories', state: 'in_progress' },
  ])
})

test('a prompt sent straight to the chat goes first on the queue, as the prompt being worked', async ($, on) => {
  const seeded = seedQueue(on, false, '', QUEUED, true)
  const carried: string[] = []
  on('prompt.submit', (_, e) => {
    carried.push(...(e.context ?? []))
    return { text: e.text }
  })

  await $.prompt.submit({ text: 'Fix the Files app', wait: false, origin: { kind: 'composer' } })

  expect(seeded.prompts.map(prompt => prompt.text)).toEqual(['Fix the Files app', 'Write the scenarios', 'Run the unit tier'])
  expect(seeded.stored.askedAbout?.value).toBe(seeded.prompts[0]!.id)
  expect(carried.join()).toContain(`as [${seeded.prompts[0]!.id}]`)
})

for (const isPlanSeen of [false, true]) {
  test(`the queue beside a prompt ${isPlanSeen ? 'leaves ticking steps to the task list once one is seen' : 'tells the agent to tick its steps itself until a task list is seen'}`, async ($, on) => {
    seedQueue(on, false, '', QUEUED, true, '', 'a')
    planToolAnswers(on)
    const carried: string[] = []
    on('prompt.submit', (_, e) => {
      carried.push(...(e.context ?? []))
      return { text: e.text }
    })
    if (isPlanSeen) await $.tool.call({ tool: PLAN_TOOL, items: PLANNED })

    await $.prompt.submit({ text: 'Fix the Files app', wait: false, origin: { kind: 'composer' } })

    expect(carried.join().includes('prompt-queue.step_done')).toBe(!isPlanSeen)
    expect(carried.join()).toContain('call prompt-queue.set_steps with its id')
  })
}

test('a wrapped-up turn finishes every step of the prompt being worked', async ($, on) => {
  const seeded = seedQueue(on, true, '', QUEUED, true, '', 'a')
  planToolAnswers(on)

  await $.tool.call({ tool: PLAN_TOOL, items: PLANNED })
  await $.tool.call({ tool: 'mcp__ccd_turn__wrap_up', recap: 'Done.' })

  expect(seeded.prompts[0]!.steps!.map(step => step.state)).toEqual(['done', 'done'])
})

test("a card with steps shows how many are done, and opens them under it", async ($, on) => {
  seedQueue(on, true, '', [
    { id: 'a', text: 'Write the scenarios', steps: [{ text: 'Read the epic', state: 'done' }, { text: 'Write the stories', state: 'in_progress' }] },
    { id: 'b', text: 'Run the unit tier' },
  ] as Prompt[])

  const pressed = await $.ui.mount({ ...BAND, surface: 'desktop' })
  const progress = await pressed.find({ type: 'Button', key: 'steps-a' })
  await pressed.press({ key: 'steps-a' })
  await pressed.unmount()
  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })

  expect(progress?.props.label).toBe('1/2')
  expect(await ui.find({ type: 'Button', key: 'steps-b' })).toBeUndefined()
  expect((await ui.find({ type: 'Box', key: 'steps-of-a' }))?.text).toBe('✓ Read the epic▸ Write the stories')
  await ui.unmount()
})

test("a card's progress comes before its text, so a long prompt cannot push it past the card's right edge", async ($, on) => {
  seedQueue(on, true, '', [
    { id: 'a', text: 'Write the scenarios '.repeat(20), steps: [{ text: 'Read the epic', state: 'done' }, { text: 'Write the stories', state: 'pending' }] },
  ] as Prompt[])

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  const row = JSON.stringify((await ui.find({ type: 'Box', key: 'card-row-a' }))?.children)

  expect(row.indexOf('"steps-a"')).toBeGreaterThan(-1)
  expect(row.indexOf('"steps-a"')).toBeLessThan(row.indexOf('"card-text-a"'))
  await ui.unmount()
})

const ATTACHED = [
  { id: 'a', text: 'Write the scenarios', attachments: ['C:/chats/chat-1/attachments/a-1.png'] },
  { id: 'b', text: 'Run the unit tier' },
] as Prompt[]

test('the queue beside a prompt lists the files queued with each prompt, for the agent to open', async ($, on) => {
  seedQueue(on, false, '', ATTACHED, true)
  const carried: string[] = []
  on('prompt.submit', (_, e) => {
    carried.push(...(e.context ?? []))
    return { text: e.text }
  })

  await $.prompt.submit({ text: 'Fix the Files app', wait: false, origin: { kind: 'composer' } })

  expect(carried.join()).toContain('1. [a] Write the scenarios (attached, open each: C:/chats/chat-1/attachments/a-1.png)')
  expect(carried.join()).not.toContain('Run the unit tier (attached')
})

test('a card with files queued with it shows how many', async ($, on) => {
  seedQueue(on, true, '', ATTACHED)

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })

  expect((await ui.find({ type: 'Box', key: 'card-a' }))?.text).toContain('📎1')
  expect((await ui.find({ type: 'Box', key: 'card-b' }))?.text).not.toContain('📎')
  await ui.unmount()
})


test('send now on a card moves its prompt to the top and sends it to the chat at once', async ($, on) => {
  const seeded = seedQueue(on, true)
  const submitted: string[] = []
  on('prompt.submit', (_, e) => {
    submitted.push(e.text)
    return { text: e.text }
  })

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  await ui.press({ key: 'send-now-b' })
  await unawaitedWorkSettled()

  expect(seeded.prompts.map(prompt => prompt.id)).toEqual(['b', 'a'])
  expect(submitted).toEqual(['Take prompt [b] on the queue now: Run the unit tier'])
  expect(seeded.stored.askedAbout?.value).toBe('b')
  await ui.unmount()
})

test("a card's buttons sit on solid grey, so they read over the prompt's text", async ($, on) => {
  seedQueue(on, true)

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })

  expect((await ui.find({ type: 'Box', key: 'card-a' }))?.children.some(child => JSON.stringify(child).includes('"backgroundColor":"#3F3F3F"'))).toBe(true)
  await ui.unmount()
})

test('the open queue and each card fill the width of the chat box', async ($, on) => {
  seedQueue(on, true)

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })

  expect((await ui.find({ type: 'Box', key: 'prompt-queue' }))?.props.width).toBe('100%')
  expect((await ui.find({ type: 'Box', key: 'card-row-a' }))?.props.width).toBe('100%')
  await ui.unmount()
})


const ONE_DONE = [
  { id: 'a', text: 'Write the scenarios', is_done: true },
  { id: 'b', text: 'Run the unit tier' },
] as Prompt[]

test('a done prompt keeps its card, drawn dim, so the person sees it finish', async ($, on) => {
  seedQueue(on, true, '', ONE_DONE)

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })

  expect((await ui.find({ type: 'Button', key: 'card-text-a' }))?.props.dimColor).toBe(true)
  expect((await ui.find({ type: 'Button', key: 'card-text-b' }))?.props.dimColor).toBe(false)
  await ui.unmount()
})

test('play takes the next prompt not done, passing over done ones', async ($, on) => {
  seedQueue(on, false, '', ONE_DONE, true, '', 'a')
  const submitted: string[] = []
  on('prompt.submit', (_, e) => {
    submitted.push(e.text)
    return { text: e.text }
  })
  on('turn.complete', () => ({ text: 'Done.' }))

  await $.turn.complete(FINISHED_TURN)
  await unawaitedWorkSettled()

  expect(submitted).toEqual([ASK_FOR_NEXT])
})

test('the queue beside a prompt leaves out the prompts already done', async ($, on) => {
  seedQueue(on, false, '', ONE_DONE, true)
  const carried: string[] = []
  on('prompt.submit', (_, e) => {
    carried.push(...(e.context ?? []))
    return { text: e.text }
  })

  await $.prompt.submit({ text: 'Fix the Files app', wait: false, origin: { kind: 'composer' } })

  expect(carried.join()).not.toContain('Write the scenarios')
  expect(carried.join()).toContain('Run the unit tier')
})


/** The engine's clock: each wait asked for is held until the test lets that time pass. */
function heldClock(on: TestOn) {
  const waits: { ms: number; pass: () => void }[] = []
  on('clock.after', (_, e) => new Promise<{ value: undefined }>(resolve => {
    waits.push({ ms: (e as { ms: number }).ms, pass: () => resolve({ value: undefined }) })
  }))
  return waits
}

/** A turn that ends with the agent asking the person something, while the queue plays prompt a. */
async function turnEndedAsking($: Parameters<Parameters<typeof test>[1]>[0], on: TestOn) {
  seedQueue(on, false, '', QUEUED, true, '', 'a')
  const waits = heldClock(on)
  const submitted: string[] = []
  on('prompt.submit', (_, e) => {
    submitted.push(e.text)
    return { text: e.text }
  })
  on('turn.complete', () => ({ text: 'Done.' }))
  on('turn.start', (_, e) => e)
  planToolAnswers(on)
  await $.tool.call({ tool: 'mcp__ccd_turn__wrap_up', recap: 'Two ways to do it.', ask: 'Which way?' })
  await $.turn.complete(FINISHED_TURN)
  await unawaitedWorkSettled()
  return { waits, submitted }
}

test('a turn that ends asking the person something waits a minute before play moves on', async ($, on) => {
  const { waits, submitted } = await turnEndedAsking($, on)

  expect(submitted).toEqual([])
  expect(waits.map(wait => wait.ms)).toEqual([60_000])
})

test('with no answer in the minute, the agent is told to put the prompt back as needing a decision and take the next', async ($, on) => {
  const { waits, submitted } = await turnEndedAsking($, on)

  waits[0]!.pass()
  await unawaitedWorkSettled()

  expect(submitted).toHaveLength(1)
  expect(submitted[0]).toContain('[a]')
  expect(submitted[0]).toContain('[decision required]')
})

test('an answer from the person within the minute leaves nothing to send when it passes', async ($, on) => {
  const { waits, submitted } = await turnEndedAsking($, on)

  await $.turn.start({ text: 'Take the first way', turnId: 't2' })
  waits[0]!.pass()
  await unawaitedWorkSettled()

  expect(submitted).toEqual([])
})

test('play passes over a prompt put back as needing a decision', async ($, on) => {
  seedQueue(on, false, '', [
    { id: 'a', text: '[decision required] Which failure route? A or B' },
    { id: 'b', text: 'Run the unit tier' },
  ] as Prompt[], true, '', 'b')
  const submitted: string[] = []
  on('prompt.submit', (_, e) => {
    submitted.push(e.text)
    return { text: e.text }
  })
  on('turn.complete', () => ({ text: 'Done.' }))

  await $.turn.complete(FINISHED_TURN)
  await unawaitedWorkSettled()

  expect(submitted).toEqual([])
})


test('the prompt the agent gives steps to becomes the one being worked, so its task list follows onto it', async ($, on) => {
  const seeded = seedQueue(on, true, '', QUEUED, true, '', 'a')
  planToolAnswers(on)

  await $.tool.call({ tool: 'mcp__cdd__prompt-queue_set_steps', prompt: 'b', steps: [
    { text: 'Read the epic', state: 'in_progress' },
    { text: 'Write the stories', state: 'pending' },
  ] })
  await $.tool.call({ tool: PLAN_TOOL, advance: true })

  expect(seeded.stored.askedAbout?.value).toBe('b')
  expect(seeded.prompts[1]!.steps!.map(step => step.state)).toEqual(['done', 'in_progress'])
  expect(seeded.prompts[0]!.steps).toBeUndefined()
})
