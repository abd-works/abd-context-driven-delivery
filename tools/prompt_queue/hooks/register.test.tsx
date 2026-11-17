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

const QUEUED = [
  { id: 'a', text: 'Write the scenarios' },
  { id: 'b', text: 'Run the unit tier' },
]

type TestOn = Parameters<Extract<Parameters<typeof test>[1], (...args: never[]) => unknown>>[1]

/** The mod's stored values, kept in memory as the engine keeps them: each write raises the value's version. */
function seedQueue(on: TestOn, isExpanded: boolean, queuedByKey = '', queued = QUEUED, isPlaying = false, editingId = '') {
  const stored: Record<string, { value: unknown; version: number }> = {
    prompts: { value: queued, version: 1 },
    isExpanded: { value: isExpanded, version: 1 },
    queuedByKey: { value: queuedByKey, version: 1 },
    isPlaying: { value: isPlaying, version: 1 },
    editingId: { value: editingId, version: 1 },
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

  return { get prompts() { return stored.prompts?.value } }
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

  test(`play submits the next queued prompt, on ${surface}`, async ($, on) => {
    seedQueue(on, true)
    const submitted: string[] = []
    on('prompt.submit', (_, e) => {
      submitted.push(e.text)
      return { text: e.text }
    })

    const ui = await $.ui.mount({ ...BAND, surface })
    await ui.press({ key: 'queue-play' })

    expect(submitted).toEqual(['Write the scenarios'])
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

const FINISHED_TURN = { answer: 'Done.', durationMs: 1, isAborted: false, turnId: 't1', reason: 'answer' } as const

for (const isPlaying of [true, false]) {
  test(`a finished turn ${isPlaying ? 'sends the next prompt while playing' : 'sends nothing while paused'}`, async ($, on) => {
    seedQueue(on, false, '', QUEUED, isPlaying)
    const submitted: string[] = []
    on('prompt.submit', (_, e) => {
      submitted.push(e.text)
      return { text: e.text }
    })
    on('turn.complete', () => ({ text: 'Done.' }))

    await $.turn.complete(FINISHED_TURN)

    expect(submitted).toEqual(isPlaying ? ['Write the scenarios'] : [])
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
    return { value: { isAnswered: true, text: '[]' } }
  })

  const ran = await $.command.run({ command: 'queue', args: PASTED_LIST })
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
  on('model.fork', () => ({ value: { isAnswered: true, text: 'Nothing is left to do.' } }))

  const ran = await $.command.run({ command: 'queue', args: '' })

  expect(ran.text).toBe('Queued 0 prompt(s): the model proposed none. It answered: Nothing is left to do.')
})
