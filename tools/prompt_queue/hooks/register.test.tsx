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
// The messages the stubbed cdd server reads as only talk: which messages are talk is the server's to decide
// (prompt_queue_spec.py), so the mod is tested on what it does with the answer.
const TALK = ['why is there no flush button?', 'yes']

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
  // Whether the person switched the queue on for the chat; most tests work a queue that is on.
  const switched = { isOn: true }
  const answer = () => ({ chat: CHAT, prompts: prompts.map(answered), is_on: switched.isOn })
  const stepsOf = (args: Record<string, unknown>) => prompts[at(args.prompt)]!.steps ?? []
  const at = (id: unknown) => prompts.findIndex(prompt => prompt.id === id)
  const operations: Record<string, (args: Record<string, unknown>) => unknown> = {
    show: () => answer(),
    switch_on: () => {
      switched.isOn = true
      return answer()
    },
    switch_off: () => {
      switched.isOn = false
      return answer()
    },
    is_only_talk: args => ({ is_only_talk: TALK.includes(String(args.message)) }),
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
  return { prompts, flushes, switched, call: (tool: string, args: Record<string, unknown>) => operations[tool.replace('prompt-queue.', '')]!(args) }
}

/** The mod's stored values, kept in memory as the engine keeps them: each write raises the value's version; the queue
 * itself is the cdd server's, through prompt-queue's tools. */
function seedQueue(on: TestOn, isExpanded: boolean, queuedByKey = '', queued = QUEUED, isPlaying = false, editingId = '', askedAbout = '', servers = ['cdd']) {
  // A deep copy, as the cdd server reads its own file: a shallow one shared each prompt's steps with the test's
  // examples, so a test that took a step off or moved the step pointer changed the examples the next test seeded.
  const server = promptQueueTools(structuredClone(queued))
  on('session.id', () => ({ value: CHAT }))
  on('session.root', () => ({ value: 'C:/work' }))
  // Each tool the mod called, with its arguments, and the tools the server refuses, as a test sets them.
  const calls: { tool: string; args: Record<string, unknown> }[] = []
  const refused = new Set<string>()
  on('mcp.call', (_, e) => {
    const { server: called, tool, args } = e as { server: string; tool: string; args: Record<string, unknown> }
    if (!servers.includes(called)) {
      return { deny: `no MCP server ${called}` }
    }
    calls.push({ tool, args })
    if (refused.has(tool)) {
      return { deny: `${tool} could not answer` }
    }
    return { value: { content: [{ type: 'text', text: JSON.stringify(server.call(tool, args)) }], isError: false } }
  })
  const stored: Record<string, { value: unknown; version: number }> = {
    queue: { value: { chat: CHAT, prompts: server.prompts.map(answered), is_on: server.switched.isOn }, version: 1 },
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

  /** The queue switched off for the chat, on the server and as the mod last read it. */
  const switchOff = () => {
    server.switched.isOn = false
    stored.queue = { value: { chat: CHAT, prompts: server.prompts.map(answered), is_on: false }, version: stored.queue!.version + 1 }
  }

  return { get prompts() { return server.prompts }, get isOn() { return server.switched.isOn }, flushes: server.flushes, stored, calls, refuse: (tool: string) => refused.add(tool), switchOff }
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

// A chat's queue is off until the person switches it on, so a chat that does not use it is left alone.
test('a queue switched off shows only its on/off button on the queue bar', async ($, on) => {
  const seeded = seedQueue(on, true)
  seeded.switchOff()

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  const shown = [await ui.find({ type: 'Button', key: 'queue-power' }), await ui.find({ type: 'Button', key: 'queue-stack' })]
  await ui.unmount()

  expect(shown.map(button => button !== undefined)).toEqual([true, false])
})

test('pressing the on/off button of a queue switched off switches it on for the chat', async ($, on) => {
  const seeded = seedQueue(on, false)
  seeded.switchOff()

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  await ui.press({ key: 'queue-power' })
  await ui.unmount()

  expect(seeded.isOn).toBe(true)
})

test('pressing the on/off button of a queue switched on switches it off for the chat', async ($, on) => {
  const seeded = seedQueue(on, false)

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  await ui.press({ key: 'queue-power' })
  await ui.unmount()

  expect(seeded.isOn).toBe(false)
})

test('switching the queue off pauses it, so no finished turn asks for the next prompt', async ($, on) => {
  const seeded = seedQueue(on, false, '', QUEUED, true)

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  await ui.press({ key: 'queue-power' })
  await ui.unmount()

  expect(seeded.stored.isPlaying?.value).toBe(false)
})

test('a finished turn asks for no next prompt while the queue is switched off, even playing', async ($, on) => {
  const seeded = seedQueue(on, false, '', QUEUED, true)
  seeded.switchOff()
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

test('a message the person sends carries no note while the queue is switched off', async ($, on) => {
  const seeded = seedQueue(on, false, '', QUEUED, true)
  seeded.switchOff()
  const carried: string[] = []
  on('prompt.submit', (_, e) => {
    carried.push(...(e.context ?? []))
    return { text: e.text }
  })

  await $.prompt.submit({ text: 'Fix the Files app', wait: false, origin: { kind: 'composer' } })

  expect(carried).toEqual([])
})

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
async function messageSentMidWork($: Parameters<Parameters<typeof test>[1]>[0], on: TestOn, text: string, arrange: (seeded: ReturnType<typeof seedQueue>) => void = () => {}) {
  const seeded = seedQueue(on, false, '', QUEUED.map(prompt => ({ ...prompt })), true, '', 'a')
  arrange(seeded)
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

// The state the Claude app puts before a message sent while a board viewer is open: the viewer's, not the person's.
const VIEWER_STATE = '<artifact-view-context artifact="c9a2df8e">\n{"context":{"mode":"board","dirty":false,"selected":[]}}\n' +
  "(The JSON line above is this viewer's live state in the artifact, not typed by the user.)\n<artifact-content-authored-by-others/>\n</artifact-view-context>"

// A message goes to the chat as sent: the agent decides whether it is work and puts it on the queue itself, titled cleanly.
test('a message sent between turns puts nothing on the queue', async ($, on) => {
  const seeded = seedQueue(on, false, '', QUEUED, true)
  on('prompt.submit', (_, e) => ({ text: e.text }))

  await $.prompt.submit({ text: 'Fix the Files app', wait: false, origin: { kind: 'composer' } })

  expect(seeded.prompts.map(prompt => prompt.text)).toEqual(['Write the scenarios', 'Run the unit tier'])
})

test('a message sent while a prompt is worked adds no step to it', async ($, on) => {
  const { seeded } = await messageSentMidWork($, on, 'cut the text with an ellipsis')

  expect(seeded.prompts[0]!.steps ?? []).toEqual([])
})

test('a pasted message puts nothing on the queue', async ($, on) => {
  const seeded = seedQueue(on, false, '', [], true)
  on('prompt.submit', (_, e) => ({ text: e.text }))

  await $.prompt.submit({ text: PASTED_NOTES, wait: false, origin: { kind: 'composer' } })

  expect(seeded.prompts).toEqual([])
})

test('the agent is told the message is on no card and to queue it only when it is work, titled cleanly', async ($, on) => {
  const { carried } = await messageSentMidWork($, on, 'cut the text with an ellipsis')

  expect(carried.join()).toContain('it is on no card of the queue')
})

test('the agent is told how to file work under the goal being worked, by its id', async ($, on) => {
  const { carried } = await messageSentMidWork($, on, 'cut the text with an ellipsis')

  expect(carried.join()).toContain('prompt-queue.add_interruption')
})

test('the agent is told the goal being worked when a message is sent mid-work', async ($, on) => {
  const { carried } = await messageSentMidWork($, on, 'cut the text with an ellipsis')

  expect(carried.join()).toContain('the one being worked, [a]')
})

test('the agent is told the chat id to pass to the queue, so it can place the message', async ($, on) => {
  const { carried } = await messageSentMidWork($, on, 'cut the text with an ellipsis')

  expect(carried.join()).toContain(`chat "${CHAT}"`)
})

test("the agent is told a board viewer's state is not the person's words and never goes in a title", async ($, on) => {
  const { carried } = await messageSentMidWork($, on, 'cut the text with an ellipsis')

  expect(carried.join()).toContain('artifact-view-context')
})

test('the agent is told to check the queue after placing the message', async ($, on) => {
  const { carried } = await messageSentMidWork($, on, 'cut the text with an ellipsis')

  expect(carried.join()).toContain('prompt-queue.show')
})

// A question, an answer or a comment is talk, not work: the chat answers it, and the queue keeps only work to do.
for (const talk of TALK) {
  test(`a message the cdd server reads as only talk, such as ${JSON.stringify(talk)}, sent mid-work carries no note`, async ($, on) => {
    const { carried } = await messageSentMidWork($, on, talk)

    expect(carried.join()).not.toContain('on no card')
  })

  test(`a message the cdd server reads as only talk, such as ${JSON.stringify(talk)}, sent between turns is not queued`, async ($, on) => {
    const seeded = seedQueue(on, false, '', [], true)
    on('prompt.submit', (_, e) => ({ text: e.text }))

    await $.prompt.submit({ text: talk, wait: false, origin: { kind: 'composer' } })

    expect(seeded.prompts).toEqual([])
  })
}

test('the mod asks the cdd server whether a message is only talk, sending the message as the person sent it', async ($, on) => {
  const { seeded } = await messageSentMidWork($, on, `${VIEWER_STATE}

?`)

  expect(seeded.calls.filter(call => call.tool === 'prompt-queue.is_only_talk').map(call => call.args.message)).toEqual([`${VIEWER_STATE}

?`])
})

test('a message the cdd server could not read is given the note, so the agent still decides where it goes', async ($, on) => {
  const { carried } = await messageSentMidWork($, on, 'yes', seeded => seeded.refuse('prompt-queue.is_only_talk'))

  expect(carried.join()).toContain('on no card')
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

// Out of sub-agent mode the work is the chat's own again, so no card keeps a robot and no robot stays on the queue.
test('switching sub-agent mode off takes every robot off the queue', async ($, on) => {
  const seeded = groupedQueue(on)

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  await ui.press({ key: 'queue-sub-agents' })
  await ui.unmount()

  expect(seeded.prompts.map(prompt => prompt.robot ?? '')).toEqual(seeded.prompts.map(() => ''))
})

test('switching sub-agent mode off forgets the robots and their sub-agents', async ($, on) => {
  const seeded = groupedQueue(on)
  seeded.stored.robotAgents = { value: { Sparky: 'agent-1' }, version: 1 }

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  await ui.press({ key: 'queue-sub-agents' })
  await ui.unmount()

  expect([seeded.stored.tasks!.value, seeded.stored.robotAgents!.value, seeded.stored.expandedAgents!.value]).toEqual([[], {}, []])
})

/** The grouped queue with each robot's sub-agent running and its card handed to it, each robot's queue open. */
function runningRobots(on: TestOn) {
  const seeded = groupedQueue(on)
  seeded.stored.robotAgents = { value: { Sparky: 'agent-1', Bolt: 'agent-2' }, version: 1 }
  seeded.stored.sentCards = { value: { Sparky: 'a', Bolt: 'b' }, version: 1 }
  return seeded
}

/** What the mod still holds of each robot: its task, its sub-agent, the card it was handed, and the open queues. */
function robotsHeld(seeded: ReturnType<typeof groupedQueue>) {
  return [
    (seeded.stored.tasks!.value as { name: string }[]).map(task => task.name),
    seeded.stored.robotAgents!.value,
    seeded.stored.sentCards!.value,
    seeded.stored.expandedAgents!.value,
  ]
}

// A robot no card names any more is gone from the queue, so the mod forgets it as leaving sub-agent mode does.
test("removing a robot's last card forgets that robot, its sub-agent, its card and its open queue", async ($, on) => {
  const seeded = runningRobots(on)

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  await ui.press({ key: 'remove-a' })
  await ui.unmount()

  expect(robotsHeld(seeded)).toEqual([['Bolt'], { Bolt: 'agent-2' }, { Bolt: 'b' }, [0]])
})

test('flushing the finished cards forgets a robot whose cards were all finished', async ($, on) => {
  const seeded = runningRobots(on)
  seeded.prompts[0]!.is_done = true

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  await ui.press({ key: 'queue-flush' })
  await ui.unmount()

  expect(robotsHeld(seeded)).toEqual([['Bolt'], { Bolt: 'agent-2' }, { Bolt: 'b' }, [0]])
})

test('removing a card keeps a robot another card still names', async ($, on) => {
  const seeded = runningRobots(on)
  seeded.prompts[1]!.robot = 'Sparky'

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  await ui.press({ key: 'remove-a' })
  await ui.unmount()

  expect((seeded.stored.robotAgents!.value as Record<string, string>).Sparky).toEqual('agent-1')
})

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

test("the hand-out tells each robot to put its own task list on its card with prompt-queue.set_steps before it starts", async ($, on) => {
  const { asked } = await handOut($, on, ROBOT_CARDS)

  expect([asked[0]?.includes('task list of your own plan'), asked[0]?.includes('prompt-queue.set_steps')]).toEqual([true, true])
})

test("the hand-out tells each robot to tick its card's steps with prompt-queue.step_done, naming this chat", async ($, on) => {
  const { asked } = await handOut($, on, ROBOT_CARDS)

  expect([asked[0]?.includes('prompt-queue.step_done'), asked[0]?.includes(CHAT)]).toEqual([true, true])
})

/** A robot whose sub-agent is known, with the person's change to one of its cards: what this chat is then asked. */
async function changeRobotCard($: TestEngine, on: TestOn, press: string, draft = '') {
  const seeded = groupedQueue(on)
  seeded.stored.robotAgents = { value: { Sparky: 'agent-1' }, version: 1 }
  const asked: string[] = []
  on('prompt.submit', (_, e) => {
    asked.push(e.text)
    return { text: e.text }
  })
  on('prompt.read', () => ({ value: { text: draft, cursor: draft.length } }))
  on('prompt.fill', () => ({ isFilled: true }))
  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  await ui.press({ key: press })
  await ui.unmount()
  await unawaitedWorkSettled()
  return asked.join('\n')
}

// A robot works only the words this chat sends it, so a card the person changes under it is news it must be sent.
test("taking a robot's card off asks this chat to tell that robot, by its sub-agent", async ($, on) => {
  const asked = await changeRobotCard($, on, 'remove-a')

  expect([asked.includes('SendMessage to agent-1'), asked.includes('[a]')]).toEqual([true, true])
})

test("moving a robot's card asks this chat to tell that robot its cards' new order", async ($, on) => {
  const asked = await changeRobotCard($, on, 'down-a')

  expect(asked).toContain('SendMessage to agent-1')
})

test("a change to a card of a robot with no sub-agent yet asks this chat nothing, as the robot gets the card as it stands", async ($, on) => {
  const asked = await changeRobotCard($, on, 'remove-b')

  expect(asked).toBe('')
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

/** This chat starts a sub-agent with the description and prompt given: what the started task shows as, and the queue's
 * stored state after it. */
async function agentStarted($: TestEngine, on: TestOn, description: string, prompt: string) {
  const seeded = seedQueue(on, true, '', ROBOT_CARDS)
  seeded.stored.isSubAgentMode = { value: true, version: 1 }
  seeded.stored.tasks = { value: GROUPED, version: 1 }
  const started: string[] = []
  on('agent.spawn', (_, e) => {
    started.push(e.description)
    return { model: 'sonnet', agentId: 's1' }
  })
  await $.agent.spawn({ description, prompt })
  return { seeded, started }
}

test("this chat's Agent call that starts a robot is remembered: the robot's name goes with that sub-agent's id", async ($, on) => {
  const { seeded } = await agentStarted($, on, 'Sparky: Write the scenarios', 'Write the scenarios')

  expect(seeded.stored.robotAgents?.value).toEqual({ Sparky: 's1' })
})

test("a sub-agent started for a card goes by the name of the card's robot on the queue, whatever name this chat wrote", async ($, on) => {
  const { started } = await agentStarted($, on, 'Robot 20: run the tests', 'Card [b]: Run the unit tier')

  expect(started).toEqual(['Bolt: run the tests'])
})

test("a sub-agent started for a card is remembered as the card's robot", async ($, on) => {
  const { seeded } = await agentStarted($, on, 'Robot 20: run the tests', 'Card [b]: Run the unit tier')

  expect(seeded.stored.robotAgents?.value).toEqual({ Bolt: 's1' })
})

test("the hand-out asks that each robot's sub-agent be started with its card's id, so the task and the robot share one name", async ($, on) => {
  const { asked } = await handOut($, on, ROBOT_CARDS)

  expect(asked[0]).toContain('its prompt starting "Card [a]: "')
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

// A first message of a chat as Claude Code hands a paste to the mod: the pasted text inside its tags.
const PASTED_NOTES = '<pasted_content id="7250">\n## Notes from the backlog\nFrom `board-enhancements` the board needs a filter.\n</pasted_content>'

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


test("the first message of a chat is answered with the queue as the server holds it, even when the chat's start could not read it", async ($, on) => {
  const seeded = seedQueue(on, false, '', [
    { id: 'a', text: 'Write the scenarios', is_done: true },
    { id: 'b', text: 'Run the unit tier' },
  ] as Prompt[], true)
  seeded.stored.queue = { value: { chat: CHAT, is_on: true, prompts: [] }, version: 1 }
  const carried: string[] = []
  on('prompt.submit', (_, e) => {
    carried.push(...(e.context ?? []))
    return { text: e.text }
  })

  await $.prompt.submit({ text: 'Fix the Files app', wait: false, origin: { kind: 'composer' } })

  expect(carried.join()).toContain('[b] Run the unit tier')
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
  seeded.stored.queue = { value: { chat: CHAT, is_on: true, prompts: ([...QUEUED.map(prompt => ({ ...prompt, robot: prompt.id === 'a' ? 'Sparky' : 'Bolt' })), { id: 'm', text: '[interruption] is it started' }]).map(answered) }, version: 2 }

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  const loose = await ui.find({ type: 'Box', key: 'agent-loose-cards' })
  const robots = JSON.stringify(await ui.find({ type: 'Box', key: 'agent-columns' }))
  await ui.unmount()

  expect([JSON.stringify(loose).includes('"card-row-m"'), robots.includes('"card-row-m"'), loose?.props.width]).toEqual([true, false, '100%'])
})

// A card queued for a robot by name stands in that robot's queue, so it is not drawn again among the cards no robot has.
test("in sub-agent mode a card queued for a robot by name shows only in that robot's queue, not again under the robots", async ($, on) => {
  const seeded = groupedQueue(on)
  seeded.stored.queue = { value: { chat: CHAT, is_on: true, prompts: ([...QUEUED.map(prompt => ({ ...prompt, robot: prompt.id === 'a' ? 'Sparky' : 'Bolt' })), { id: 'n', text: '[for Bolt] Run the heavy tier' }]).map(answered) }, version: 2 }

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  const loose = await ui.find({ type: 'Box', key: 'agent-loose-cards' })
  await ui.unmount()

  expect(JSON.stringify(loose ?? {}).includes('"card-row-n"')).toBe(false)
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
  seeded.stored.queue = { value: { chat: CHAT, is_on: true, prompts: (seeded.prompts.map(prompt => ({ ...prompt }))).map(answered) }, version: 2 }

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
  expect(carried.join()).toContain('prompt-queue.assign')
  expect(carried.join()).toContain('do it yourself')
})

test("a card queued for a robot by name shows in that robot's queue", async ($, on) => {
  const seeded = groupedQueue(on)
  seeded.stored.queue = { value: { chat: CHAT, is_on: true, prompts: ([...seeded.prompts, { id: 'c', text: '[for Bolt] Run the heavy tier' }]).map(answered) }, version: 2 }

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })

  expect(JSON.stringify(await ui.find({ type: 'Box', key: 'agent-column-2' }))).toContain('"card-row-c"')
  await ui.unmount()
})

// Answered 2026-11-23 (sparky-06): an agent types a robot's name by hand, so case and outer spaces do not make another robot.
test("a card queued for a robot by name in another case and with spaces shows in that robot's queue", async ($, on) => {
  const seeded = groupedQueue(on)
  seeded.stored.queue = { value: { chat: CHAT, is_on: true, prompts: ([...seeded.prompts, { id: 'c', text: '[for  bolt ] Run the heavy tier' }]).map(answered) }, version: 2 }

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })

  expect(JSON.stringify(await ui.find({ type: 'Box', key: 'agent-column-2' }))).toContain('"card-row-c"')
  await ui.unmount()
})

test("a card given to a robot spelled in another case stands in that robot's queue, not in a second robot's", async ($, on) => {
  const seeded = groupedQueue(on)
  seeded.stored.queue = { value: { chat: CHAT, is_on: true, prompts: ([...seeded.prompts, { id: 'c', text: 'Run the heavy tier', robot: 'bOLT' }]).map(answered) }, version: 2 }

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  const bolt = JSON.stringify(await ui.find({ type: 'Box', key: 'agent-column-2' }))
  const third = await ui.find({ type: 'Box', key: 'agent-column-3' })

  expect([bolt.includes('"card-row-c"'), third]).toEqual([true, undefined])
  await ui.unmount()
})

test("a card given to one robot and named for another stands only in the queue of the robot it was given to", async ($, on) => {
  const seeded = groupedQueue(on)
  seeded.stored.queue = { value: { chat: CHAT, is_on: true, prompts: ([...seeded.prompts, { id: 'c', text: '[for Bolt] Run the heavy tier', robot: 'Sparky' }]).map(answered) }, version: 2 }

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

/** The robots' queues with Sparky's sub-agent known, robot 1 open as given: the views the person was shown on pressing
 * robot 1. */
async function robotPressed($: TestEngine, on: TestOn, open: number[]) {
  const seeded = groupedQueue(on)
  seeded.stored.expandedAgents = { value: open, version: 1 }
  seeded.stored.robotAgents = { value: { Sparky: 's1' }, version: 1 }
  const viewed: unknown[] = []
  on('ui.view', (_, e) => {
    viewed.push(e)
    return { value: {} }
  })
  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  await ui.press({ key: 'collapse-agent-1' })
  await ui.unmount()
  return viewed
}

test("pressing a closed robot whose sub-agent is running shows that sub-agent's task in the main view", async ($, on) => {
  expect(await robotPressed($, on, [])).toEqual([{ agentId: 's1' }])
})

test('pressing the open robot goes back to the main conversation', async ($, on) => {
  expect(await robotPressed($, on, [0])).toEqual([{}])
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

// The see-through press lies over the whole row, so a press on the robot's name or count opens its queue too: its blank
// label reaches past the robot's picture, a gap, the name, a gap and the count.
test("a robot's whole row takes the press, its robot, its name and its count", async ($, on) => {
  groupedQueue(on)

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  const press = await ui.find({ type: 'Button', key: 'collapse-agent-1' })
  const count = await ui.find({ type: 'Text', key: 'agent-progress-1' })
  const nameAndCount = `Sparky ${count?.text ?? ''}`.length

  expect(String(press?.props.label).length).toBeGreaterThan(nameAndCount + 1)
  await ui.unmount()
})

test("a closed robot shows how many of its items are done beside it, such as 1/2", async ($, on) => {
  const seeded = groupedQueue(on, [{ description: 'Write the story map', prompts: ['Write the scenarios', 'Run the unit tier'], name: 'Sparky' }])
  seeded.stored.expandedAgents = { value: [], version: 1 }
  seeded.stored.queue = { value: { chat: CHAT, is_on: true, prompts: ([{ ...QUEUED[0], is_done: true, robot: 'Sparky' }, { ...QUEUED[1], robot: 'Sparky' }]).map(answered) }, version: 2 }

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })

  expect((await ui.find({ type: 'Box', key: 'agent-robot-1' }))?.text).toContain('1/2')
  await ui.unmount()
})


/** A robot's sub-agent ends its turn while this chat plays in sub-agent mode: what this chat is asked, and the waits the
 * queue set to check on the robot again. */
async function robotStopped($: TestEngine, on: TestOn, prompts: Prompt[] = ROBOT_CARDS, agentId = 's1') {
  const seeded = seedQueue(on, true, '', prompts)
  seeded.stored.isSubAgentMode = { value: true, version: 1 }
  seeded.stored.tasks = { value: GROUPED, version: 1 }
  seeded.stored.isPlaying = { value: true, version: 1 }
  seeded.stored.sentCards = { value: { Sparky: 'a', Bolt: 'b' }, version: 1 }
  seeded.stored.robotAgents = { value: { Sparky: 's1', Bolt: 's2' }, version: 1 }
  const waits = heldClock(on)
  const asked: string[] = []
  on('prompt.submit', (_, e) => {
    asked.push(e.text)
    return { text: e.text }
  })
  on('turn.start', (_, e) => e)
  on('turn.complete', () => ({ text: 'Done.' }))
  await $.turn.start({ text: 'Card [a]: Write the scenarios', turnId: 'r1', agentId } as never)
  await $.turn.complete({ ...FINISHED_TURN, agentId } as never)
  await unawaitedWorkSettled()
  return { asked, waits }
}

test('a robot whose sub-agent stops with its card not done is checked on a minute later', async ($, on) => {
  const { asked, waits } = await robotStopped($, on)

  expect([asked, waits.map(wait => wait.ms)]).toEqual([[], [60_000]])
})

test("checking on a stopped robot asks this chat to read its report and resume it by its sub-agent's id when the card is not finished", async ($, on) => {
  const { asked, waits } = await robotStopped($, on)

  waits[0]!.pass()
  await unawaitedWorkSettled()

  expect([asked.length, asked[0]?.includes('Sparky'), asked[0]?.includes('[a]'), asked[0]?.includes('SendMessage to s1')]).toEqual([1, true, true, true])
})

test('a stopped robot whose card is still not done is checked on again every ten minutes', async ($, on) => {
  const { waits } = await robotStopped($, on)

  waits[0]!.pass()
  await unawaitedWorkSettled()

  expect(waits.map(wait => wait.ms)).toEqual([60_000, 600_000])
})

test('a robot whose card was marked done before the check is not checked on', async ($, on) => {
  const { asked, waits } = await robotStopped($, on, ROBOT_CARDS.map(card => (card.robot === 'Bolt' ? { ...card, is_done: true } : card)), 's2')

  waits[0]?.pass()
  await unawaitedWorkSettled()

  expect(asked).toEqual([])
})

test('a robot whose sub-agent started again before the check is not checked on', async ($, on) => {
  const { asked, waits } = await robotStopped($, on)

  await $.turn.start({ text: 'Carry on', turnId: 'r2', agentId: 's1' } as never)
  waits[0]!.pass()
  await unawaitedWorkSettled()

  expect(asked).toEqual([])
})


test("in sub-agent mode the note on a new message says work that waits on a robot's result goes to that robot, so no robot waits on another", async ($, on) => {
  groupedQueue(on)
  const carried: string[] = []
  on('prompt.submit', (_, e) => {
    carried.push(...(e.context ?? []))
    return { text: e.text }
  })

  await $.prompt.submit({ text: 'write the heavy results into the report', wait: false, origin: { kind: 'composer' } })

  expect(carried.join()).toContain("waits on a robot's result goes to that robot")
})

test('grouping asks for work that waits on another prompt\'s result to go to the same robot, so no robot waits on another', async ($, on) => {
  seedQueue(on, true)
  const systems: string[] = []
  on('model.complete', (_, e) => {
    systems.push((e as { system: string }).system)
    return { value: { isAnswered: true, text: '[]', usage: NO_USAGE } }
  })

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  await ui.press({ key: 'queue-sub-agents' })
  await ui.unmount()

  expect(systems[0]).toContain("needs another prompt's result")
})


test("a sub-agent this chat starts for a card is that card handed out, so the robot is not handed it again", async ($, on) => {
  const { seeded } = await agentStarted($, on, 'Bolt: run the tests', 'Card [b]: Run the unit tier')

  expect(seeded.stored.sentCards?.value).toEqual({ Bolt: 'b' })
})

test("a card this chat sends a robot's sub-agent itself is that card handed out, so the robot is not handed it again", async ($, on) => {
  const seeded = seedQueue(on, true, '', ROBOT_CARDS)
  seeded.stored.isSubAgentMode = { value: true, version: 1 }
  seeded.stored.tasks = { value: GROUPED, version: 1 }
  seeded.stored.robotAgents = { value: { Sparky: 's1' }, version: 1 }
  planToolAnswers(on)

  await $.tool.call({ tool: 'SendMessage', to: 's1', message: 'New card [c]: Validate them' })

  expect(seeded.stored.sentCards?.value).toEqual({ Sparky: 'c' })
})


test('the hand-out tells each robot to fix every failing test it meets, including one that failed before its change', async ($, on) => {
  const { asked } = await handOut($, on, ROBOT_CARDS)

  expect(asked[0]).toContain('including one that failed before your change')
})


test("in sub-agent mode the note on a new message says to give a card its steps when it is added, wherever its work has clear parts", async ($, on) => {
  groupedQueue(on)
  const carried: string[] = []
  on('prompt.submit', (_, e) => {
    carried.push(...(e.context ?? []))
    return { text: e.text }
  })

  await $.prompt.submit({ text: 'run every tier and merge', wait: false, origin: { kind: 'composer' } })

  expect(carried.join()).toContain('give it its steps with prompt-queue.set_steps as you add it')
})

test("the hand-out tells a robot whose card already has steps to work those steps, adding or changing them as it learns", async ($, on) => {
  const { asked } = await handOut($, on, ROBOT_CARDS.map(card => (card.id === 'a' ? { ...card, steps: [{ text: 'Read the epic', state: 'pending' as const }] } : card)))

  expect(asked[0]).toContain('When a card already has steps, work them')
})


test('the note on a message that is new work says to give its card steps as it is added, when its work has clear parts', async ($, on) => {
  seedQueue(on, false, '', QUEUED, true)
  const carried: string[] = []
  on('prompt.submit', (_, e) => {
    carried.push(...(e.context ?? []))
    return { text: e.text }
  })

  await $.prompt.submit({ text: 'add a release checklist', wait: false, origin: { kind: 'composer' } })

  expect(carried.join()).toContain('and, when its work has clear parts, give it its steps with prompt-queue.set_steps')
})
