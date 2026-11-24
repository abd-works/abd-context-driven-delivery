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
type TestEngine = Parameters<Extract<Parameters<typeof test>[1], (...args: never[]) => unknown>>[0]

// The chat the tests run in, as the engine names it.
const CHAT = 'chat-1'

type Step = { text: string; state: 'pending' | 'in_progress' | 'done' }
type Prompt = { id: string; text: string; steps?: Step[]; attachments?: string[]; is_done?: boolean; robot?: string }

/** A prompt as the cdd server answers it: with whether it waits (neither done nor asking a decision) and where its
 * steps' pointer stands, as tools/prompt_queue's QueuedPrompt sends them. */
function answered(prompt: Prompt) {
  const steps = prompt.steps ?? []
  const pointer = steps.findIndex(step => step.state !== 'done')
  return { ...prompt, is_waiting: !prompt.is_done && !prompt.text.startsWith('[decision required]'), step_pointer: pointer === -1 ? steps.length : pointer }
}

/** The cdd server's prompt-queue tools for one chat, in memory: the same operations as tools/prompt_queue's
 * PromptQueue, each answering the queue. */
function promptQueueTools(prompts: Prompt[]) {
  let added = 0
  // The queue as each flush found it, the copy the cdd server keeps in the queue archive.
  const flushes: string[] = []
  const answer = () => ({ chat: CHAT, prompts: prompts.map(answered) })
  const stepsOf = (args: Record<string, unknown>) => prompts[at(args.prompt)]!.steps ?? []
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
    flush: () => {
      flushes.push(JSON.stringify(prompts))
      prompts.splice(0, prompts.length, ...prompts.filter(prompt => !prompt.is_done))
      return answer()
    },
    done: args => {
      prompts[at(args.prompt)]!.is_done = true
      return answer()
    },
    add_interruption: args => {
      const goal = prompts[at(args.prompt)]!
      goal.steps = [...(goal.steps ?? []), { text: `[interruption] ${String(args.text).trim()}`, state: 'pending' }]
      goal.is_done = false
      return answer()
    },
    split: args => {
      const goal = prompts[at(args.prompt)]!
      const isSplit = (step: Step) => step.text.startsWith('[interruption]') && step.state !== 'done'
      const cards = (goal.steps ?? []).filter(isSplit).map(step => ({ id: `added-${++added}`, text: step.text, ...(goal.robot ? { robot: goal.robot } : {}) }))
      goal.steps = (goal.steps ?? []).filter(step => !isSplit(step))
      prompts.splice(at(args.prompt) + 1, 0, ...cards)
      return answer()
    },
    reopen: args => {
      const prompt = prompts[at(args.prompt)]!
      prompt.is_done = false
      if (prompt.steps) prompt.steps = prompt.steps.map(step => ({ ...step, state: 'pending' }))
      return answer()
    },
    assign: args => {
      const prompt = prompts[at(args.prompt)]!
      if (String(args.robot).trim()) prompt.robot = String(args.robot).trim()
      else delete prompt.robot
      return answer()
    },
    set_steps: args => {
      prompts[at(args.prompt)]!.steps = args.steps as Step[]
      return answer()
    },
    move_step: args => {
      const steps = stepsOf(args)
      const place = Number(args.place)
      if (place >= 1 && place <= steps.length) {
        const [moving] = steps.splice(Number(args.step) - 1, 1)
        steps.splice(place - 1, 0, moving!)
      }
      return answer()
    },
    remove_step: args => {
      stepsOf(args).splice(Number(args.step) - 1, 1)
      return answer()
    },
    step_back: args => {
      const steps = stepsOf(args)
      const above = answered(prompts[at(args.prompt)]!).step_pointer - 1
      if (above >= 0) steps.forEach((step, place) => { if (place >= above) step.state = place === above ? 'in_progress' : 'pending' })
      return answer()
    },
    step_on: args => {
      const steps = stepsOf(args)
      const pointed = answered(prompts[at(args.prompt)]!).step_pointer
      if (pointed < steps.length) {
        steps[pointed]!.state = 'done'
        if (pointed + 1 < steps.length) steps[pointed + 1]!.state = 'in_progress'
      }
      return answer()
    },
  }
  return { prompts, flushes, call: (tool: string, args: Record<string, unknown>) => operations[tool.replace('prompt-queue.', '')]!(args) }
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
    queue: { value: { chat: CHAT, prompts: server.prompts.map(answered) }, version: 1 },
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

  return { get prompts() { return server.prompts }, flushes: server.flushes, stored }
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

// Reported 2026-11-19: after a repin and /reload-plugins neither the queue nor the chat bar showed above the prompt.
// A queue an earlier version stored with no prompts makes the draw throw; the queue's row says so instead of vanishing.
test('a queue whose draw throws shows why in red, in place of the queue', async ($, on) => {
  const seeded = seedQueue(on, true)
  seeded.stored.queue = { value: { chat: CHAT }, version: 2 }

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })

  expect((await ui.find({ type: 'Text', text: /^prompt queue failed to draw: / }))?.text).toContain('flatMap')
  await ui.unmount()
})

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

test('flush keeps a copy of the queue as it stood, then takes the finished cards off', async ($, on) => {
  const seeded = seedQueue(on, true, '', [{ id: 'a', text: 'Write the scenarios', is_done: true }, { id: 'b', text: 'Run the unit tier' }])

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  await ui.press({ key: 'queue-flush' })

  expect([seeded.flushes.length, seeded.prompts.map(prompt => prompt.id)]).toEqual([1, ['b']])
  await ui.unmount()
})

test('flush with nothing finished keeps the copy and every card', async ($, on) => {
  const seeded = seedQueue(on, true)

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  await ui.press({ key: 'queue-flush' })

  expect([seeded.flushes.length, seeded.prompts.map(prompt => prompt.id)]).toEqual([1, ['a', 'b']])
  await ui.unmount()
})

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

/** + with a draft in the prompt box, the model answering where it files the draft with placed. */
async function smartAdd($: TestEngine, on: TestOn, placed: object[] | string, queued = QUEUED as Prompt[]) {
  const seeded = seedQueue(on, true, '', queued)
  const asked: string[] = []
  const filled: string[] = []
  on('prompt.read', () => ({ value: { text: 'also run the heavy tier', cursor: 23 } }))
  on('prompt.fill', (_, e) => {
    filled.push((e as { text: string }).text)
    return { isFilled: true }
  })
  on('model.fork', (_, e) => {
    asked.push((e as { prompt: string }).prompt)
    return { value: typeof placed === 'string' ? { isAnswered: false, reason: placed } : { isAnswered: true, text: JSON.stringify(placed), usage: NO_USAGE } }
  })
  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  await ui.press({ key: 'queue-add' })
  await ui.unmount()
  return { seeded, asked, filled }
}

test('+ asks the model where the draft belongs, showing it the goals on the queue', async ($, on) => {
  const { asked } = await smartAdd($, on, [])

  expect(asked.join()).toContain('also run the heavy tier')
  expect(asked.join()).toContain('[b] Run the unit tier')
})

test('+ files the draft as a task of the goal the model picks', async ($, on) => {
  const { seeded } = await smartAdd($, on, [{ goal: 'b', text: 'Run the heavy tier too' }])

  expect(seeded.prompts[1]!.steps!.map(step => step.text)).toEqual(['[interruption] Run the heavy tier too'])
})

test('+ queues new work as a card of its own, given to no robot: the agents button groups robots', async ($, on) => {
  const { seeded, asked } = await smartAdd($, on, [{ card: 'Run the heavy tier', robot: 'Bolt' }])

  expect([seeded.prompts.map(prompt => [prompt.text, prompt.robot]).at(-1), asked.join().includes('robot')]).toEqual([['Run the heavy tier', undefined], false])
})

test("+ in sub-agent mode adds the draft as a card of the open robot's queue", async ($, on) => {
  const seeded = groupedQueue(on)
  seeded.stored.expandedAgents = { value: [1], version: 1 }
  on('prompt.read', () => ({ value: { text: 'Run the heavy tier', cursor: 18 } }))
  on('prompt.fill', () => ({ isFilled: true }))

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  await ui.press({ key: 'queue-add' })
  await ui.unmount()

  expect(seeded.prompts.map(prompt => [prompt.text, prompt.robot]).at(-1)).toEqual(['Run the heavy tier', 'Bolt'])
})

test('/queue with a draft places it into the plan the way + does', async ($, on) => {
  const seeded = seedQueue(on, false)
  on('model.fork', () => ({ value: { isAnswered: true, text: JSON.stringify([{ goal: 'b', text: 'Run the heavy tier too' }]), usage: NO_USAGE } }))

  const ran = await $.command.run({ command: 'queue', args: 'also run the heavy tier', origin: { kind: 'composer' }, presentation: TERMINAL })

  expect([ran.text, seeded.prompts[1]!.steps!.map(step => step.text)]).toEqual(['Placed 1 piece(s) of the draft on the queue.', ['[interruption] Run the heavy tier too']])
})

test('+ empties the prompt box once the draft is filed', async ($, on) => {
  const { filled } = await smartAdd($, on, [{ card: 'Run the heavy tier' }])

  expect(filled).toEqual([''])
})

test('+ keeps the draft in the prompt box when the model cannot place it', async ($, on) => {
  const { seeded, filled } = await smartAdd($, on, 'the model is busy')

  expect([filled, seeded.prompts.length]).toEqual([[], 2])
})

/** The open queue with prompts, pressing the given keys in turn, each on a fresh mount as the next render draws it. */
async function pressedQueue($: TestEngine, on: TestOn, prompts: Prompt[], keys: string[], isSubAgentMode = false) {
  const seeded = seedQueue(on, true, '', prompts)
  seeded.stored.openSteps = { value: prompts.map(prompt => prompt.id), version: 1 }
  if (isSubAgentMode) seeded.stored.isSubAgentMode = { value: true, version: 1 }
  for (const key of keys) {
    const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
    await ui.press({ key })
    await ui.unmount()
  }
  return seeded
}

test("the queue's pointer stands on the left of the next card to do, and on no other", async ($, on) => {
  seedQueue(on, true, '', ONE_DONE)

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })

  expect([Boolean(await ui.find({ type: 'Button', key: 'pointer-up-b' })), Boolean(await ui.find({ type: 'Button', key: 'pointer-up-a' }))]).toEqual([true, false])
  await ui.unmount()
})

test("▲ on the pointer opens the done card above it again, so it runs again", async ($, on) => {
  const seeded = await pressedQueue($, on, ONE_DONE.map(prompt => ({ ...prompt })), ['pointer-up-b'])

  expect(seeded.prompts[0]!.is_done).toBe(false)
})

test('▼ on the pointer marks its card done, so play moves past it', async ($, on) => {
  const seeded = await pressedQueue($, on, ONE_DONE.map(prompt => ({ ...prompt })), ['pointer-down-b'])

  expect(seeded.prompts[1]!.is_done).toBe(true)
})

test('with every card done, the last card is the current one, and its ▲ opens it again', async ($, on) => {
  const seeded = await pressedQueue($, on, QUEUED.map(prompt => ({ ...prompt, is_done: true })), ['pointer-up-b'])

  expect(seeded.prompts.map(prompt => Boolean(prompt.is_done))).toEqual([true, false])
})

test('with every card done, the last card carries the orange working mark', async ($, on) => {
  seedQueue(on, true, '', QUEUED.map(prompt => ({ ...prompt, is_done: true })))

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  const last = JSON.stringify(await ui.find({ type: 'Box', key: 'card-row-b' }))
  await ui.unmount()

  expect(last).toContain('"borderColor":"#E5531A"')
})

const STEPPED = [{ id: 'a', text: 'Write the scenarios', steps: [{ text: 'Read the epic', state: 'done' }, { text: 'Write them', state: 'in_progress' }] }] as Prompt[]

test("▲ on a card's step pointer opens the done step above it again", async ($, on) => {
  const seeded = await pressedQueue($, on, STEPPED.map(prompt => ({ ...prompt })), ['step-pointer-up-a'])

  expect(seeded.prompts[0]!.steps!.map(step => step.state)).toEqual(['in_progress', 'pending'])
})

test("▼ on a card's step pointer marks its step done and points at the next", async ($, on) => {
  const seeded = await pressedQueue($, on, [{ ...STEPPED[0]!, steps: [...STEPPED[0]!.steps!, { text: 'Validate them', state: 'pending' }] }], ['step-pointer-down-a'])

  expect(seeded.prompts[0]!.steps!.map(step => step.state)).toEqual(['done', 'done', 'in_progress'])
})

test("in sub-agent mode each robot's queue has its own pointer", async ($, on) => {
  groupedQueue(on)

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })

  expect([Boolean(await ui.find({ type: 'Button', key: 'pointer-up-a' })), Boolean(await ui.find({ type: 'Button', key: 'pointer-up-b' }))]).toEqual([true, true])
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

  expect(seeded.prompts.map(prompt => prompt.text)).toEqual(['[interruption] Fix the Files app', 'Write the scenarios', 'Run the unit tier'])
  expect(seeded.stored.askedAbout?.value).toBe(seeded.prompts[0]!.id)
  expect(carried.join()).toContain(`as [${seeded.prompts[0]!.id}]`)
})

test('a prompt sent straight to the chat goes above the next prompt to do, below the done ones, marked as an interruption', async ($, on) => {
  const seeded = seedQueue(on, false, '', [
    { id: 'a', text: 'Write the scenarios', is_done: true },
    { id: 'b', text: 'Run the unit tier' },
  ] as Prompt[], true)
  on('prompt.submit', (_, e) => ({ text: e.text }))

  await $.prompt.submit({ text: 'Fix the Files app', wait: false, origin: { kind: 'composer' } })

  expect(seeded.prompts.map(prompt => prompt.text)).toEqual(['Write the scenarios', '[interruption] Fix the Files app', 'Run the unit tier'])
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

  expect(progress).toBeDefined()
  expect((await ui.find({ type: 'Box', key: 'steps-a-box' }))?.text).toContain('1/2')
  expect((await ui.find({ type: 'Box', key: 'steps-b-box' }))?.text).toContain('+')
  expect((await ui.find({ type: 'Box', key: 'step-row-a-1' }))?.text.includes('✓ Read the epic')).toBe(true)
  expect((await ui.find({ type: 'Box', key: 'step-row-a-2' }))?.text.includes('▸ Write the stories')).toBe(true)
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

test("send now on a step sends that step of its prompt to the chat at once", async ($, on) => {
  const seeded = seedQueue(on, true, '', STEPPED.map(prompt => ({ ...prompt })))
  seeded.stored.openSteps = { value: ['a'], version: 1 }
  const submitted: string[] = []
  on('prompt.submit', (_, e) => {
    submitted.push(e.text)
    return { text: e.text }
  })

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  await ui.press({ key: 'send-now-step-a-2' })
  await unawaitedWorkSettled()
  await ui.unmount()

  expect(submitted).toEqual(['Take step 2 of prompt [a] on the queue now: Write them'])
})

test("✎ on a step with an empty prompt box puts the step's text in the box to change", async ($, on) => {
  const seeded = seedQueue(on, true, '', STEPPED.map(prompt => ({ ...prompt })))
  seeded.stored.openSteps = { value: ['a'], version: 1 }
  const filled: string[] = []
  on('prompt.read', () => ({ value: { text: '', cursor: 0 } }))
  on('prompt.fill', (_, e) => {
    filled.push((e as { text: string }).text)
    return { isFilled: true }
  })

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  await ui.press({ key: 'edit-step-a-2' })
  await ui.unmount()

  expect(filled).toEqual(['Write them'])
})

test("✎ on a step with a draft in the prompt box makes the draft the step's text, and the box empties", async ($, on) => {
  const seeded = seedQueue(on, true, '', STEPPED.map(prompt => ({ ...prompt })))
  seeded.stored.openSteps = { value: ['a'], version: 1 }
  on('prompt.read', () => ({ value: { text: 'Write them all', cursor: 14 } }))
  on('prompt.fill', () => ({ isFilled: true }))

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  await ui.press({ key: 'edit-step-a-2' })
  await ui.unmount()

  expect(seeded.prompts[0]!.steps!.map(step => step.text)).toEqual(['Read the epic', 'Write them all'])
})

test("a card's button bar hangs from the last thing in the card, an anchor at its right end laid out in the row, so the bar floats over the card's right end", async ($, on) => {
  seedQueue(on, true)

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  const row = await ui.find({ type: 'Box', key: 'card-row-a' })
  await ui.unmount()
  type Node = { type: string; key?: string; props: Record<string, unknown>; children?: unknown[] }
  const card = (row!.children as Node[]).find(child => child.props.backgroundColor === '#303030')!
  const parts = (card.children ?? []).filter((child): child is Node => typeof child === 'object' && child !== null)
  const bar = parts.at(-1)!

  expect([JSON.stringify(bar).includes('"send-now-a"'), bar.props.position === 'absolute']).toEqual([true, false])
})

test("a card's buttons sit on a solid dark bar, so they read over the prompt's text", async ($, on) => {
  seedQueue(on, true)

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })

  expect((await ui.find({ type: 'Box', key: 'card-a' }))?.children.some(child => JSON.stringify(child).includes('"backgroundColor":"#1C1C1E"'))).toBe(true)
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


const WITH_STEPS = [
  { id: 'a', text: 'Write the scenarios', steps: [
    { text: 'Read the epic', state: 'done' },
    { text: 'Write the stories', state: 'in_progress' },
    { text: 'Validate them', state: 'pending' },
  ] },
  { id: 'b', text: 'Run the unit tier' },
] as Prompt[]

/** The queue drawn again after a press, with prompt a's steps open, as its next render draws it. */
async function stepsOpenAfter($: Parameters<Parameters<typeof test>[1]>[0], press: string) {
  const opening = await $.ui.mount({ ...BAND, surface: 'desktop' })
  await opening.press({ key: 'steps-a' })
  await opening.unmount()
  const pressing = await $.ui.mount({ ...BAND, surface: 'desktop' })
  await pressing.press({ key: press })
  await pressing.unmount()
}

test("+ on a card with no tasks adds the prompt box's draft as its first task, not started, and empties the box", async ($, on) => {
  const seeded = seedQueue(on, true, '', WITH_STEPS.map(prompt => ({ ...prompt })))
  on('prompt.read', () => ({ value: { text: 'Render the map', cursor: 14 } }))
  const filled: string[] = []
  on('prompt.fill', (_, e) => {
    filled.push(e.text)
    return { isFilled: true }
  })

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  await ui.press({ key: 'steps-b' })
  await ui.unmount()

  expect(seeded.prompts[1]!.steps).toEqual([{ text: 'Render the map', state: 'pending' }])
  expect(filled).toEqual([''])
})

test('+ with an empty prompt box says to type the task there first, instead of doing nothing', async ($, on) => {
  const seeded = seedQueue(on, true, '', QUEUED.map(prompt => ({ ...prompt })))
  on('prompt.read', () => ({ value: { text: '  ', cursor: 0 } }))

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  await ui.press({ key: 'steps-a' })
  await ui.unmount()

  expect(seeded.stored.notice?.value).toBe('Type the task in the prompt box, then press + to add it.')
})

test('+ shows on a done card with no tasks too, and its new task opens the card again so it runs', async ($, on) => {
  const seeded = seedQueue(on, true, '', [{ id: 'a', text: 'Write the scenarios', is_done: true }])
  on('prompt.read', () => ({ value: { text: 'Render the map', cursor: 14 } }))
  on('prompt.fill', () => ({ isFilled: true }))

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  await ui.press({ key: 'steps-a' })
  await ui.unmount()

  expect([seeded.prompts[0]!.steps, seeded.prompts[0]!.is_done ?? false]).toEqual([[{ text: 'Render the map', state: 'pending' }], false])
})

test('✕ on a step takes it off its prompt', async ($, on) => {
  const seeded = seedQueue(on, true, '', WITH_STEPS.map(prompt => ({ ...prompt })))

  await stepsOpenAfter($, 'remove-step-a-2')

  expect(seeded.prompts[0]!.steps!.map(step => step.text)).toEqual(['Read the epic', 'Validate them'])
})

test("↑ on a step moves it one place up among its prompt's steps", async ($, on) => {
  const seeded = seedQueue(on, true, '', WITH_STEPS.map(prompt => ({ ...prompt })))

  await stepsOpenAfter($, 'up-step-a-3')

  expect(seeded.prompts[0]!.steps!.map(step => step.text)).toEqual(['Read the epic', 'Validate them', 'Write the stories'])
})

test("↓ on a step moves it one place down among its prompt's steps", async ($, on) => {
  const seeded = seedQueue(on, true, '', WITH_STEPS.map(prompt => ({ ...prompt })))

  await stepsOpenAfter($, 'down-step-a-1')

  expect(seeded.prompts[0]!.steps!.map(step => step.text)).toEqual(['Write the stories', 'Read the epic', 'Validate them'])
})


/** A turn is running on prompt a, the one being worked, when the person sends a message. */
async function messageSentMidWork($: Parameters<Parameters<typeof test>[1]>[0], on: TestOn, text: string) {
  const seeded = seedQueue(on, false, '', QUEUED.map(prompt => ({ ...prompt })), true, '', 'a')
  planToolAnswers(on)
  on('turn.start', (_, e) => e)
  const carried: string[] = []
  on('prompt.submit', (_, e) => {
    carried.push(...(e.context ?? []))
    return { text: e.text }
  })
  await $.turn.start({ text: 'Take the next prompt on the queue.', turnId: 't1' })
  await $.prompt.submit({ text, wait: false, origin: { kind: 'composer' } })
  return { seeded, carried }
}

test("a message sent while a prompt is worked becomes a step of that prompt, marked as the person's interruption", async ($, on) => {
  const { seeded } = await messageSentMidWork($, on, 'cut the text with an ellipsis')

  expect(seeded.prompts.map(prompt => prompt.text)).toEqual(['Write the scenarios', 'Run the unit tier'])
  expect(seeded.prompts[0]!.steps).toEqual([{ text: '[interruption] cut the text with an ellipsis', state: 'pending' }])
})

test('the agent is told a message sent mid-work joined the prompt it works on', async ($, on) => {
  const { carried } = await messageSentMidWork($, on, 'cut the text with an ellipsis')

  expect(carried.join()).toContain('filed it under the goal last worked, [a]')
})

test("the agent's next task list keeps the person's interruption among the prompt's steps", async ($, on) => {
  const { seeded } = await messageSentMidWork($, on, 'cut the text with an ellipsis')

  await $.tool.call({ tool: PLAN_TOOL, items: PLANNED })

  expect(seeded.prompts[0]!.steps!.map(step => step.text)).toContain('[interruption] cut the text with an ellipsis')
})


const GROUPED = [
  { description: 'Write the story map', prompts: ['Write the scenarios', 'Validate them'], name: 'Sparky' },
  { description: 'Run the tests', prompts: ['Run the unit tier'], name: 'Bolt' },
]

/** A queue in sub-agent mode whose prompts are grouped into GROUPED tasks, every robot's queue opened: each card carries
 * its robot's name, as the queue keeps it. */
function groupedQueue(on: TestOn, tasks: { prompts: string[]; name: string }[] = GROUPED) {
  const robotOf = (text: string) => tasks.find(task => task.prompts.includes(text))?.name
  const seeded = seedQueue(on, true, '', QUEUED.map(prompt => ({ ...prompt, ...(robotOf(prompt.text) ? { robot: robotOf(prompt.text) } : {}) })))
  seeded.stored.isSubAgentMode = { value: true, version: 1 }
  seeded.stored.tasks = { value: tasks, version: 1 }
  seeded.stored.expandedAgents = { value: tasks.map((_, place) => place), version: 1 }
  return seeded
}

test("a robot's queue comes back after a reload, from the robot each card keeps on the queue", async ($, on) => {
  const seeded = groupedQueue(on)
  delete seeded.stored.tasks

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  const first = JSON.stringify(await ui.find({ type: 'Box', key: 'agent-column-1' }))
  const second = JSON.stringify(await ui.find({ type: 'Box', key: 'agent-column-2' }))

  expect([first.includes('"card-row-a"'), second.includes('"card-row-b"')]).toEqual([true, true])
  await ui.unmount()
})

test('grouping the queue gives each card its robot on the queue', async ($, on) => {
  const seeded = seedQueue(on, true)
  on('model.complete', () => ({ value: { isAnswered: true, text: JSON.stringify(GROUPED.map(({ description, prompts }) => ({ description, prompts }))), usage: NO_USAGE } }))

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  await ui.press({ key: 'queue-sub-agents' })
  await ui.unmount()

  expect(seeded.prompts.map(prompt => prompt.robot)).toEqual(['Sparky', 'Bolt'])
})

test("grouping the queue closes every robot's queue, leaving only the list of robots", async ($, on) => {
  const seeded = seedQueue(on, true)
  seeded.stored.expandedAgents = { value: [0, 1], version: 1 }
  on('model.complete', () => ({ value: { isAnswered: true, text: JSON.stringify(GROUPED.map(({ description, prompts }) => ({ description, prompts }))), usage: NO_USAGE } }))

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  await ui.press({ key: 'queue-sub-agents' })
  await ui.unmount()

  expect(seeded.stored.expandedAgents?.value).toEqual([])
})

test('grouping new work names its robots apart from the robots already on the queue', async ($, on) => {
  const seeded = seedQueue(on, true, '', [{ id: 'a', text: 'Write the scenarios', is_done: true, robot: 'Sparky' }, { id: 'b', text: 'Run the unit tier' }])
  on('model.complete', () => ({ value: { isAnswered: true, text: JSON.stringify([{ description: 'Run the tests', prompts: ['Run the unit tier'] }]), usage: NO_USAGE } }))

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  await ui.press({ key: 'queue-sub-agents' })
  await ui.unmount()

  expect(seeded.prompts.map(prompt => prompt.robot)).toEqual(['Sparky', 'Bolt'])
})

test('sub-agent mode lists each robot by name, with its picture, and draws its open queue', async ($, on) => {
  groupedQueue(on)

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  const robots = JSON.stringify(await ui.find({ type: 'Box', key: 'agent-robots' }))
  const first = JSON.stringify(await ui.find({ type: 'Box', key: 'agent-column-1' }))
  const second = JSON.stringify(await ui.find({ type: 'Box', key: 'agent-column-2' }))

  expect([robots.includes('Sparky'), robots.includes('Bolt'), robots.includes('<svg')]).toEqual([true, true, true])
  expect(first).toContain('Write the scenarios')
  expect(second).toContain('Run the unit tier')
  await ui.unmount()
})

test("each sub-agent's robot differs from the others", async ($, on) => {
  groupedQueue(on)

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  const robotOf = async (column: number) => {
    const drawn = JSON.stringify(await ui.find({ type: 'Box', key: `agent-robot-${column}` }))
    return drawn.slice(drawn.indexOf('<svg'), drawn.indexOf('</svg>'))
  }

  expect(await robotOf(1)).toContain('<svg')
  expect(await robotOf(1)).not.toEqual(await robotOf(2))
  await ui.unmount()
})

/** A finished turn of this chat while playing in sub-agent mode, with the robots' queue as given: what this chat was
 * then asked to do, if anything. */
async function handOut($: TestEngine, on: TestOn, prompts: Prompt[], sent: Record<string, string> = {}, tasks = GROUPED, agents: Record<string, string> = {}) {
  const seeded = seedQueue(on, true, '', prompts)
  seeded.stored.isSubAgentMode = { value: true, version: 1 }
  seeded.stored.tasks = { value: tasks, version: 1 }
  seeded.stored.isPlaying = { value: true, version: 1 }
  seeded.stored.sentCards = { value: sent, version: 1 }
  seeded.stored.robotAgents = { value: agents, version: 1 }
  const asked: string[] = []
  on('prompt.submit', (_, e) => {
    asked.push(e.text)
    return { text: e.text }
  })
  on('turn.complete', () => ({ text: 'Done.' }))
  await $.turn.complete(FINISHED_TURN)
  await unawaitedWorkSettled()
  return { seeded, asked }
}

const ROBOT_CARDS = [
  { id: 'a', text: 'Write the scenarios', robot: 'Sparky' },
  { id: 'c', text: 'Validate them', robot: 'Sparky' },
  { id: 'b', text: 'Run the unit tier', robot: 'Bolt' },
] as Prompt[]

test("playing in sub-agent mode asks this chat to hand each robot its first card's words", async ($, on) => {
  const { asked } = await handOut($, on, ROBOT_CARDS)

  expect([asked.length, asked[0]?.includes('Sparky'), asked[0]?.includes('Write the scenarios'), asked[0]?.includes('Bolt'), asked[0]?.includes('Run the unit tier'), asked[0]?.includes('Validate them')]).toEqual([1, true, true, true, true, false])
})

test("the hand-out says to send each robot the card's words exactly, and to mark the card done when the robot reports it finished", async ($, on) => {
  const { asked } = await handOut($, on, ROBOT_CARDS)

  expect(['exactly', 'Agent', 'prompt-queue.done'].map(word => asked[0]?.includes(word))).toEqual([true, true, true])
})

test('a robot still working the card it was handed is not handed another', async ($, on) => {
  const { asked } = await handOut($, on, ROBOT_CARDS, { Sparky: 'a' })

  expect([asked[0]?.includes('Sparky'), asked[0]?.includes('Bolt')]).toEqual([false, true])
})

test('a robot whose card is done is handed its next card', async ($, on) => {
  const { asked } = await handOut($, on, [{ ...ROBOT_CARDS[0]!, is_done: true }, ROBOT_CARDS[1]!, ROBOT_CARDS[2]!], { Sparky: 'a', Bolt: 'b' })

  expect([asked[0]?.includes('Validate them'), asked[0]?.includes('Run the unit tier')]).toEqual([true, false])
})

test('a robot whose earlier card was opened again is handed that card, though the later card it was handed is open too', async ($, on) => {
  const { asked } = await handOut($, on, ROBOT_CARDS, { Sparky: 'c', Bolt: 'b' })

  expect([asked[0]?.includes('card [a]: Write the scenarios'), asked[0]?.includes('Run the unit tier')]).toEqual([true, false])
})

test('with every robot still working its card, this chat is asked nothing', async ($, on) => {
  const { asked } = await handOut($, on, ROBOT_CARDS, { Sparky: 'a', Bolt: 'b' })

  expect(asked).toEqual([])
})

test("this chat's Agent call that starts a robot is remembered: the robot's name goes with that sub-agent's id", async ($, on) => {
  const seeded = seedQueue(on, true, '', ROBOT_CARDS)
  seeded.stored.isSubAgentMode = { value: true, version: 1 }
  seeded.stored.tasks = { value: GROUPED, version: 1 }
  on('tool.call', () => ({ result: { status: 'async_launched', agentId: 's1', description: 'Sparky: Write the scenarios' } }))

  await $.tool.call({ tool: 'Agent', description: 'Sparky: Write the scenarios', prompt: 'Write the scenarios' })

  expect(seeded.stored.robotAgents?.value).toEqual({ Sparky: 's1' })
})

test("a robot whose sub-agent is known is handed its next card by that sub-agent's id", async ($, on) => {
  const { asked } = await handOut($, on, [{ ...ROBOT_CARDS[0]!, is_done: true }, ROBOT_CARDS[1]!, ROBOT_CARDS[2]!], { Sparky: 'a', Bolt: 'b' }, GROUPED, { Sparky: 's1' })

  expect(asked[0]?.includes('SendMessage to s1')).toBe(true)
})

test('a robot is handed out under the name it goes by, so this chat can message it by name', async ($, on) => {
  const { asked } = await handOut($, on, ROBOT_CARDS.map(card => (card.robot === 'Sparky' ? { ...card, robot: 'Captain Tests' } : card)), {}, [{ ...GROUPED[0]!, name: 'Captain Tests' }, GROUPED[1]!])

  expect(asked[0]?.includes('Captain Tests')).toBe(true)
})


test("a background task's notice arriving in the chat is not queued as the person's prompt", async ($, on) => {
  const seeded = seedQueue(on, false, '', QUEUED.map(prompt => ({ ...prompt })), true)
  on('prompt.submit', (_, e) => ({ text: e.text }))

  await $.prompt.submit({ text: ['<task-notification>', '<task-id>b1</task-id>', '<status>completed</status>', '</task-notification>'].join(' '), wait: false, origin: { kind: 'composer' } })

  expect(seeded.prompts.map(prompt => prompt.text)).toEqual(['Write the scenarios', 'Run the unit tier'])
})


test('the queue beside a prompt tells the agent to keep one card for each goal, with related messages as its tasks', async ($, on) => {
  seedQueue(on, false, '', QUEUED, true)
  const carried: string[] = []
  on('prompt.submit', (_, e) => {
    carried.push(...(e.context ?? []))
    return { text: e.text }
  })

  await $.prompt.submit({ text: 'Fix the Files app', wait: false, origin: { kind: 'composer' } })

  expect(carried.join()).toContain('one card for each goal')
  expect(carried.join()).toContain('make it a task of that goal')
})


/** The goal last worked, a, is done and its turn ended asking the person something, when the person sends a message. */
async function messageSentAfterQuestion($: TestEngine, on: TestOn, text: string) {
  const seeded = seedQueue(on, false, '', [
    { id: 'a', text: 'Write the scenarios', is_done: true },
    { id: 'b', text: 'Run the unit tier' },
  ] as Prompt[], true, '', 'a')
  planToolAnswers(on)
  const carried: string[] = []
  on('prompt.submit', (_, e) => {
    carried.push(...(e.context ?? []))
    return { text: e.text }
  })
  await $.tool.call({ tool: 'mcp__ccd_turn__wrap_up', recap: 'Two ways to cut it.', ask: 'Cut it with an ellipsis?' })
  await $.prompt.submit({ text, wait: false, origin: { kind: 'composer' } })
  return { seeded, carried }
}

test('an answer sent between turns to the question the agent asked is filed under the goal last worked, opening it again', async ($, on) => {
  const { seeded, carried } = await messageSentAfterQuestion($, on, 'cut the text with an ellipsis')

  expect(seeded.prompts.map(prompt => prompt.text)).toEqual(['Write the scenarios', 'Run the unit tier'])
  expect(seeded.prompts[0]!.steps).toEqual([{ text: '[interruption] cut the text with an ellipsis', state: 'pending' }])
  expect(seeded.prompts[0]!.is_done).toBe(false)
  expect(carried.join()).toContain('filed it under the goal last worked, [a]')
})

test('a message about new work sent between turns starts a goal of its own, not another step of the goal last worked', async ($, on) => {
  const seeded = seedQueue(on, false, '', QUEUED.map(prompt => ({ ...prompt })), true, '', 'a')
  const carried: string[] = []
  on('prompt.submit', (_, e) => {
    carried.push(...(e.context ?? []))
    return { text: e.text }
  })

  await $.prompt.submit({ text: 'Fix the Files app', wait: false, origin: { kind: 'composer' } })

  expect(seeded.prompts.map(prompt => prompt.text)).toEqual(['[interruption] Fix the Files app', 'Write the scenarios', 'Run the unit tier'])
  expect(seeded.prompts[1]!.steps).toBeUndefined()
  expect(seeded.stored.askedAbout?.value).toBe(seeded.prompts[0]!.id)
  expect(carried.join()).toContain(`as [${seeded.prompts[0]!.id}]`)
})

// A first message of a chat as Claude Code hands a paste to the mod: the pasted text inside its tags.
const PASTED_NOTES = '<pasted_content id="7250">\n## Notes from the backlog\nFrom `board-enhancements` the board needs a filter.\n</pasted_content>'

test('a goal sent as pasted text is titled by the paste\'s first line, without its tags', async ($, on) => {
  const seeded = seedQueue(on, false, '', [], true)
  on('prompt.submit', (_, e) => ({ text: e.text }))

  await $.prompt.submit({ text: PASTED_NOTES, wait: false, origin: { kind: 'composer' } })

  expect(seeded.prompts.map(prompt => prompt.text)).toEqual(['[interruption] Notes from the backlog'])
})

test("a goal sent as the person's words with a paste is titled by the person's words", async ($, on) => {
  const seeded = seedQueue(on, false, '', [], true)
  on('prompt.submit', (_, e) => ({ text: e.text }))

  await $.prompt.submit({ text: `Triage these notes into the backlog\n${PASTED_NOTES}`, wait: false, origin: { kind: 'composer' } })

  expect(seeded.prompts.map(prompt => prompt.text)).toEqual(['[interruption] Triage these notes into the backlog'])
})

test("a long goal is titled by its first sentence, cut short with an ellipsis", async ($, on) => {
  const seeded = seedQueue(on, false, '', [], true)
  on('prompt.submit', (_, e) => ({ text: e.text }))
  const long = `Fix the queue band's goal title. ${'Then keep going with every other thing on the list. '.repeat(5)}`

  await $.prompt.submit({ text: `${'Rework '.repeat(20)}the band. ${long}`, wait: false, origin: { kind: 'composer' } })
  await $.prompt.submit({ text: long, wait: false, origin: { kind: 'composer' } })

  // Each message goes above the goal sent before it, the next to do.
  const [sentence, cut] = seeded.prompts.map(prompt => prompt.text)
  expect(sentence).toBe("[interruption] Fix the queue band's goal title.")
  expect(cut!.length).toBeLessThanOrEqual('[interruption] '.length + 80)
  expect(cut!.endsWith('Rework…')).toBe(true)
})

test('messages sent after a pasted first message each start a goal of their own, so no goal gathers them as interruptions', async ($, on) => {
  const seeded = seedQueue(on, false, '', [], true)
  on('prompt.submit', (_, e) => ({ text: e.text }))

  await $.prompt.submit({ text: PASTED_NOTES, wait: false, origin: { kind: 'composer' } })
  await $.prompt.submit({ text: 'Fix the Files app', wait: false, origin: { kind: 'composer' } })
  await $.prompt.submit({ text: 'Run the unit tier', wait: false, origin: { kind: 'composer' } })

  expect(seeded.prompts.map(prompt => prompt.text).sort()).toEqual(
    ['[interruption] Fix the Files app', '[interruption] Notes from the backlog', '[interruption] Run the unit tier'])
  expect(seeded.prompts.flatMap(prompt => prompt.steps ?? [])).toEqual([])
})

test('a pasted message sent mid-work becomes a step titled by its first line, not the paste', async ($, on) => {
  const { seeded } = await messageSentMidWork($, on, PASTED_NOTES)

  expect(seeded.prompts[0]!.steps).toEqual([{ text: '[interruption] Notes from the backlog', state: 'pending' }])
})


test("the note on a filed message tells the agent to decide first where it belongs, listing the goals on the queue", async ($, on) => {
  const { carried } = await messageSentMidWork($, on, 'take the Alt hint off the queue')

  expect(carried.join()).toContain('Before any other work, decide where this message belongs')
  expect(carried.join()).toContain('[b] Run the unit tier')
  expect(carried.join()).toContain('prompt-queue.add_interruption')
})

test('the note on a filed message tells the agent to split a goal that gathered interruptions about other work', async ($, on) => {
  const { carried } = await messageSentMidWork($, on, 'take the Alt hint off the queue')

  expect(carried.join()).toContain('prompt-queue.split')
})


// A goal that gathered the person's messages as interruptions, one of them done, beside the agent's own steps.
const GATHERED = [
  { id: 'a', text: 'Write the scenarios', steps: [
    { text: 'Read the epic', state: 'done' },
    { text: '[interruption] cut the text with an ellipsis', state: 'done' },
    { text: 'Write the stories', state: 'done' },
    { text: '[interruption] Fix the Files app', state: 'pending' },
    { text: 'Validate the scenarios', state: 'in_progress' },
    { text: '[interruption] Run the heavy tier', state: 'pending' },
  ] },
  { id: 'b', text: 'Run the unit tier' },
] as Prompt[]

test('split on a card puts each interruption still to do on a card of its own, right after it', async ($, on) => {
  const seeded = await pressedQueue($, on, GATHERED, ['split-a'])

  expect(seeded.prompts.map(prompt => prompt.text)).toEqual(
    ['Write the scenarios', '[interruption] Fix the Files app', '[interruption] Run the heavy tier', 'Run the unit tier'])
})

test('split leaves the goal its own steps and the interruptions already done', async ($, on) => {
  const seeded = await pressedQueue($, on, GATHERED, ['split-a'])

  expect(seeded.prompts[0]!.steps!.map(step => step.text)).toEqual(
    ['Read the epic', '[interruption] cut the text with an ellipsis', 'Write the stories', 'Validate the scenarios'])
})

test('a card with no interruption still to do has no split', async ($, on) => {
  seedQueue(on, true, '', GATHERED)

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })

  expect(await ui.find({ type: 'Button', key: 'split-b' })).toBeUndefined()
  await ui.unmount()
})

test("a card's finished steps fold into one line under it once there are three, the steps still to do shown", async ($, on) => {
  const seeded = seedQueue(on, true, '', GATHERED)
  seeded.stored.openSteps = { value: ['a'], version: 1 }

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })

  expect((await ui.find({ type: 'Button', key: 'done-steps-a' }))?.props.label).toBe('▸ ✓ 3 done')
  expect(await ui.find({ type: 'Box', key: 'step-row-a-1' })).toBeUndefined()
  expect(await ui.find({ type: 'Box', key: 'step-row-a-4' })).toBeDefined()
  await ui.unmount()
})

test("pressing a card's folded finished steps shows them again", async ($, on) => {
  const seeded = await pressedQueue($, on, GATHERED, ['done-steps-a'])
  void seeded

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })

  expect(await ui.find({ type: 'Box', key: 'step-row-a-1' })).toBeDefined()
  expect((await ui.find({ type: 'Button', key: 'done-steps-a' }))?.props.label).toBe('▾ ✓ 3 done')
  await ui.unmount()
})

test('fewer than three finished steps stay shown, with nothing folded', async ($, on) => {
  const seeded = seedQueue(on, true, '', WITH_STEPS)
  seeded.stored.openSteps = { value: ['a'], version: 1 }

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })

  expect(await ui.find({ type: 'Box', key: 'step-row-a-1' })).toBeDefined()
  expect(await ui.find({ type: 'Button', key: 'done-steps-a' })).toBeUndefined()
  await ui.unmount()
})


test("the first message of a chat is placed from the queue as the server holds it, even when the chat's start could not read it", async ($, on) => {
  const seeded = seedQueue(on, false, '', [
    { id: 'a', text: 'Write the scenarios', is_done: true },
    { id: 'b', text: 'Run the unit tier' },
  ] as Prompt[], true)
  seeded.stored.queue = { value: { chat: CHAT, prompts: [] }, version: 1 }
  on('prompt.submit', (_, e) => ({ text: e.text }))

  await $.prompt.submit({ text: 'Fix the Files app', wait: false, origin: { kind: 'composer' } })

  expect(seeded.prompts.map(prompt => prompt.text)).toEqual(['Write the scenarios', '[interruption] Fix the Files app', 'Run the unit tier'])
})

test("the queue is drawn from the answer of the agent's own prompt-queue call at once, without waiting for the next read", async ($, on) => {
  const seeded = seedQueue(on, true)
  const answered = { chat: CHAT, prompts: [{ ...QUEUED[0], is_done: true }, QUEUED[1]] }
  on('tool.call', () => ({ result: { content: [{ type: 'text', text: JSON.stringify(answered) }], isError: false } }))

  await $.tool.call({ tool: 'mcp__cdd__prompt-queue_done', prompt: 'a' })

  expect((seeded.stored.queue?.value as { prompts: Prompt[] }).prompts[0]!.is_done).toBe(true)
})

test("the orange working mark stands on the pointer's card, whichever card the agent last touched, so it moves with the pointer", async ($, on) => {
  seedQueue(on, true, '', QUEUED, false, '', 'b')

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  const pointed = JSON.stringify(await ui.find({ type: 'Box', key: 'card-row-a' }))
  const below = JSON.stringify(await ui.find({ type: 'Box', key: 'card-row-b' }))
  await ui.unmount()

  expect([pointed.includes('"borderColor":"#E5531A"'), below.includes('"borderColor":"#E5531A"')]).toEqual([true, false])
})

test('a set_steps call the server refused leaves the prompt being worked as it was', async ($, on) => {
  const seeded = seedQueue(on, true, '', QUEUED, true, '', 'a')
  on('tool.call', () => ({ result: { content: [{ type: 'text', text: "PromptNotQueued: no prompt 'b' is on the queue" }], isError: true } }))

  await $.tool.call({ tool: 'mcp__cdd__prompt-queue_set_steps', prompt: 'b', steps: [{ text: 'Read the epic', state: 'in_progress' }] })

  expect(seeded.stored.askedAbout?.value).toBe('a')
})


test("sub-agent mode draws one queue per agent in the list's place, each made of the queue's own cards", async ($, on) => {
  groupedQueue(on)

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  const first = JSON.stringify(await ui.find({ type: 'Box', key: 'agent-column-1' }))
  const second = JSON.stringify(await ui.find({ type: 'Box', key: 'agent-column-2' }))

  expect(first).toContain('"card-row-a"')
  expect(second).toContain('"card-row-b"')
  expect(first).not.toContain('"card-row-b"')
  await ui.unmount()
})


test('switching sub-agent mode on groups only the work not done yet', async ($, on) => {
  seedQueue(on, true, '', ONE_DONE)
  const asked: string[] = []
  on('model.complete', (_, e) => {
    asked.push((e as { prompt: string }).prompt)
    return { value: { isAnswered: true, text: '[]', usage: NO_USAGE } }
  })

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  await ui.press({ key: 'queue-sub-agents' })
  await ui.unmount()

  expect(asked).toEqual([JSON.stringify(['Run the unit tier'])])
})

test("grouping leaves the person's interruptions out, as this chat decides where they go", async ($, on) => {
  seedQueue(on, true, '', [{ id: 'a', text: 'Run the unit tier' }, { id: 'm', text: '[interruption] is it started' }])
  const asked: string[] = []
  on('model.complete', (_, e) => {
    asked.push((e as { prompt: string }).prompt)
    return { value: { isAnswered: true, text: '[]', usage: NO_USAGE } }
  })

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  await ui.press({ key: 'queue-sub-agents' })
  await ui.unmount()

  expect(asked).toEqual([JSON.stringify(['Run the unit tier'])])
})

test("in sub-agent mode the cards no robot has show under the robots at the queue's full width, as in the single queue", async ($, on) => {
  const seeded = groupedQueue(on)
  seeded.stored.queue = { value: { chat: CHAT, prompts: ([...QUEUED.map(prompt => ({ ...prompt, robot: prompt.id === 'a' ? 'Sparky' : 'Bolt' })), { id: 'm', text: '[interruption] is it started' }]).map(answered) }, version: 2 }

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  const loose = await ui.find({ type: 'Box', key: 'agent-loose-cards' })
  const robots = JSON.stringify(await ui.find({ type: 'Box', key: 'agent-columns' }))
  await ui.unmount()

  expect([JSON.stringify(loose).includes('"card-row-m"'), robots.includes('"card-row-m"'), loose?.props.width]).toEqual([true, false, '100%'])
})

test('sending the queue to sub-agents keeps their cards, so each can mark its own card done', async ($, on) => {
  const seeded = groupedQueue(on)
  seeded.stored.isPlaying = { value: true, version: 1 }
  on('prompt.submit', (_, e) => ({ text: e.text }))
  on('turn.complete', () => ({ text: 'Done.' }))

  await $.turn.complete(FINISHED_TURN)
  await unawaitedWorkSettled()

  expect(seeded.prompts.map(prompt => prompt.text)).toEqual(['Write the scenarios', 'Run the unit tier'])
})

test("a robot's card has the same buttons as a card in the single queue, shown on hover", async ($, on) => {
  groupedQueue(on)

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  const column = JSON.stringify(await ui.find({ type: 'Box', key: 'agent-column-1' }))
  await ui.unmount()

  expect(['"send-now-a"', '"edit-a"', '"up-a"', '"down-a"', '"remove-a"'].every(key => column.includes(key))).toBe(true)
})

test("the robots sit one under another on the left, the open queue taking the room to their right", async ($, on) => {
  groupedQueue(on)

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  const row = await ui.find({ type: 'Box', key: 'agent-columns' })
  const queues = await ui.find({ type: 'Box', key: 'agent-queues' })
  const robots = await ui.find({ type: 'Box', key: 'agent-robots' })
  await ui.unmount()

  const drawn = JSON.stringify(row)
  expect([drawn.indexOf('"agent-robots"') < drawn.indexOf('"agent-queues"'), queues?.props.flexGrow, robots?.props.flexDirection, robots?.props.flexShrink]).toEqual([true, 1, 'column', 0])
})

test("work a robot finishes stays in that robot's queue, dimmed", async ($, on) => {
  const seeded = groupedQueue(on)
  seeded.prompts[0]!.is_done = true
  seeded.stored.queue = { value: { chat: CHAT, prompts: (seeded.prompts.map(prompt => ({ ...prompt }))).map(answered) }, version: 2 }

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  const card = await ui.find({ type: 'Button', key: 'card-text-a' })

  expect(JSON.stringify(await ui.find({ type: 'Box', key: 'agent-column-1' }))).toContain('"card-row-a"')
  expect(card?.props.dimColor).toBe(true)
  await ui.unmount()
})


test("in sub-agent mode the note on a new message shows the robots' queues and lets the agent decide where it goes", async ($, on) => {
  const seeded = groupedQueue(on)
  seeded.stored.askedAbout = { value: 'a', version: 1 }
  const carried: string[] = []
  on('prompt.submit', (_, e) => {
    carried.push(...(e.context ?? []))
    return { text: e.text }
  })

  await $.prompt.submit({ text: 'also run the heavy tier', wait: false, origin: { kind: 'composer' } })

  expect(carried.join()).toContain('Bolt: [b] Run the unit tier')
  expect(carried.join()).toContain('[for <robot name>]')
  expect(carried.join()).toContain('do it yourself')
})

test("a card queued for a robot by name shows in that robot's queue", async ($, on) => {
  const seeded = groupedQueue(on)
  seeded.stored.queue = { value: { chat: CHAT, prompts: ([...seeded.prompts, { id: 'c', text: '[for Bolt] Run the heavy tier' }]).map(answered) }, version: 2 }

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })

  expect(JSON.stringify(await ui.find({ type: 'Box', key: 'agent-column-2' }))).toContain('"card-row-c"')
  await ui.unmount()
})

// Answered 2026-11-23 (sparky-06): an agent types a robot's name by hand, so case and outer spaces do not make another robot.
test("a card queued for a robot by name in another case and with spaces shows in that robot's queue", async ($, on) => {
  const seeded = groupedQueue(on)
  seeded.stored.queue = { value: { chat: CHAT, prompts: ([...seeded.prompts, { id: 'c', text: '[for  bolt ] Run the heavy tier' }]).map(answered) }, version: 2 }

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })

  expect(JSON.stringify(await ui.find({ type: 'Box', key: 'agent-column-2' }))).toContain('"card-row-c"')
  await ui.unmount()
})

test("a card given to a robot spelled in another case stands in that robot's queue, not in a second robot's", async ($, on) => {
  const seeded = groupedQueue(on)
  seeded.stored.queue = { value: { chat: CHAT, prompts: ([...seeded.prompts, { id: 'c', text: 'Run the heavy tier', robot: 'bOLT' }]).map(answered) }, version: 2 }

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  const bolt = JSON.stringify(await ui.find({ type: 'Box', key: 'agent-column-2' }))
  const third = await ui.find({ type: 'Box', key: 'agent-column-3' })

  expect([bolt.includes('"card-row-c"'), third]).toEqual([true, undefined])
  await ui.unmount()
})

test("a card given to one robot and named for another stands only in the queue of the robot it was given to", async ($, on) => {
  const seeded = groupedQueue(on)
  seeded.stored.queue = { value: { chat: CHAT, prompts: ([...seeded.prompts, { id: 'c', text: '[for Bolt] Run the heavy tier', robot: 'Sparky' }]).map(answered) }, version: 2 }

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  const sparky = JSON.stringify(await ui.find({ type: 'Box', key: 'agent-column-1' }))
  const bolt = JSON.stringify(await ui.find({ type: 'Box', key: 'agent-column-2' }))

  expect([sparky.includes('"card-row-c"'), bolt.includes('"card-row-c"')]).toEqual([true, false])
  await ui.unmount()
})

test("pressing the open robot closes its queue, leaving the robots alone", async ($, on) => {
  const seeded = groupedQueue(on)
  seeded.stored.expandedAgents = { value: [0], version: 1 }

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  await ui.press({ key: 'collapse-agent-1' })
  await ui.unmount()

  expect(seeded.stored.expandedAgents?.value).toEqual([])
})

test("opening one robot's queue closes the robot that was open, so one queue shows at a time", async ($, on) => {
  const seeded = groupedQueue(on)
  seeded.stored.expandedAgents = { value: [1], version: 1 }

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  await ui.press({ key: 'collapse-agent-1' })
  await ui.unmount()

  expect(seeded.stored.expandedAgents?.value).toEqual([0])
})

test("pressing a closed robot opens its queue", async ($, on) => {
  const seeded = groupedQueue(on)
  seeded.stored.expandedAgents = { value: [1], version: 1 }

  const before = await $.ui.mount({ ...BAND, surface: 'desktop' })
  await before.press({ key: 'collapse-agent-1' })
  await before.unmount()
  const after = await $.ui.mount({ ...BAND, surface: 'desktop' })

  expect(JSON.stringify(await after.find({ type: 'Box', key: 'agent-column-1' }))).toContain('"card-row-a"')
  await after.unmount()
})


test("a robot's queue is closed until the robot is pressed, the robot listed with its name and nothing more", async ($, on) => {
  const seeded = groupedQueue(on)
  delete seeded.stored.expandedAgents

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  const queue = await ui.find({ type: 'Box', key: 'agent-column-1' })
  const robot = await ui.find({ type: 'Box', key: 'agent-robot-1' })

  expect([queue === undefined, robot?.text.includes('Sparky')]).toEqual([true, true])
  await ui.unmount()
})

test("a closed robot shows how many of its items are done beside it, such as 1/2", async ($, on) => {
  const seeded = groupedQueue(on, [{ description: 'Write the story map', prompts: ['Write the scenarios', 'Run the unit tier'], name: 'Sparky' }])
  seeded.stored.expandedAgents = { value: [], version: 1 }
  seeded.stored.queue = { value: { chat: CHAT, prompts: ([{ ...QUEUED[0], is_done: true, robot: 'Sparky' }, { ...QUEUED[1], robot: 'Sparky' }]).map(answered) }, version: 2 }

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })

  expect((await ui.find({ type: 'Box', key: 'agent-robot-1' }))?.text).toContain('1/2')
  await ui.unmount()
})
