// (S) Person --> Create Git Repository First
// CDD works in a git repository. In a session whose project is a plain folder, the chat bar asks to create the git
// repository first and offers nothing else; Create the git repository calls repo.make_repository, and the bar reads the
// board again and draws the session.
import { expect, test } from 'claude-code/testing'

const BAND = {
  plugin: 'cdd-board',
  component: 'AbovePrompt',
  requestId: 'above-prompt',
  props: { hasSurvey: false, isCollapsed: false, isWorking: false, maxRows: 24, bodyColumns: 120, scroll: { offset: 0, bodyRows: 24 }, view: {} },
} as const

type TestOn = Parameters<Extract<Parameters<typeof test>[1], (...args: never[]) => unknown>>[1]

// Seed: the folder the chat works in.
const FOLDER = 'C:/work/notes'

// Seed: the folder's main session, as board.overview sends it in active.
const MAIN = {
  title: 'main', last_activity: '', name: 'main', is_main: true, text: '', tags: [], children: [], is_pulled_out: false, is_stacked: false,
  session: { name: 'main', session_file: `${FOLDER}/.sessions/main/session.json`, title: 'main', repo_name: 'notes', branch: '', is_repository: false, root: FOLDER, scope: '', parent: '', workpath: '', practices: {}, handoff: '' },
  progress: [], column: { name: 'Discovery' }, is_closed: false, is_active: true, is_open: true, parent_choices: [], drop_targets: [], is_done: false,
  next: null, agent_context: '', worktree: '', new_chat_link: '', session_path: '', working_chat: null, stage_work: [], next_place: null, previous_place: null,
}

// Seed: board.overview for the folder, as Python sends it; is_clone says whether git works there.
function overviewOf(isClone: boolean) {
  return { project: 'notes', is_clone: isClone, folder: FOLDER, practices: [], fidelities: [], columns: [{ name: 'Discovery', tickets: [{ name: 'main' }] }], active: { ...MAIN, session: { ...MAIN.session, is_repository: isClone } } }
}

/** A chat in FOLDER whose board answers as a plain folder until repo.make_repository runs, and as a repository after
 * it. Answers each cdd tool called, in order. */
function chatInPlainFolder(on: TestOn) {
  const called: string[] = []
  let isClone = false
  const stored: Record<string, { value: unknown; version: number }> = {}
  const keyOf = (e: unknown) => {
    const { plugin, key } = e as { plugin: string; key: string }
    return `${plugin}:${key}`
  }
  const answer = (value: unknown) => ({ value: { content: [{ type: 'text', text: typeof value === 'string' ? value : JSON.stringify(value) }], isError: false } })
  on('session.root', () => ({ value: FOLDER }))
  on('session.id', () => ({ value: 'chat-1' }))
  on('session.messages', () => ({ value: [] }))
  on('turn.complete', () => ({ text: 'Done.' }))
  on('mcp.call', (_, e) => {
    const tool = (e as { tool: string }).tool
    called.push(tool)
    if (tool === 'repo.make_repository') {
      isClone = true
      return answer(`Created ${FOLDER} on main with a first commit.`)
    }
    if (tool === 'board.overview') return answer(overviewOf(isClone))
    return { value: { content: [{ type: 'text', text: 'not stubbed' }], isError: true } }
  })
  on('process.run', () => ({ value: { exitCode: 128, stdout: '', stderr: 'fatal: not a git repository' } }))
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

const FINISHED_TURN = { answer: 'Done.', durationMs: 1, isAborted: false, turnId: 't1', reason: 'answer' } as const
const WAIT_MS = 20
const WAITS = 25

// A turn's end reads the board again without holding the turn up, so the test waits for that read before drawing.
async function barAfterRead($: Parameters<Parameters<typeof test>[1]>[0], called: string[]) {
  const reads = called.filter(tool => tool === 'board.overview').length
  await $.turn.complete(FINISHED_TURN)
  for (let tries = 0; tries < WAITS && called.filter(tool => tool === 'board.overview').length === reads; tries += 1) {
    await new Promise(resolve => setTimeout(resolve, WAIT_MS))
  }
  await new Promise(resolve => setTimeout(resolve, WAIT_MS))
  return $.ui.mount({ ...BAND, surface: 'desktop' })
}

test('a session in a plain folder asks to create the git repository first', async ($, on) => {
  const { called } = chatInPlainFolder(on)

  const ui = await barAfterRead($, called)

  expect(await ui.find({ type: 'Button', key: 'make-repository-button' })).toBeDefined()
  await ui.unmount()
})

test('a session in a plain folder offers nothing else on the chat bar', async ($, on) => {
  const { called } = chatInPlainFolder(on)

  const ui = await barAfterRead($, called)

  expect(await ui.find({ type: 'Button', key: 'handoff' })).toBeUndefined()
  await ui.unmount()
})

test('Create the git repository calls repo.make_repository and reads the board again', async ($, on) => {
  const { called } = chatInPlainFolder(on)

  const ui = await barAfterRead($, called)
  await ui.press({ key: 'make-repository-button' })

  expect(called.slice(called.indexOf('repo.make_repository'))).toEqual(['repo.make_repository', 'board.overview'])
  await ui.unmount()
})

test('once the repository is created the chat bar asks no more', async ($, on) => {
  const { called } = chatInPlainFolder(on)

  const pressed = await barAfterRead($, called)
  await pressed.press({ key: 'make-repository-button' })
  await pressed.unmount()
  const ui = await barAfterRead($, called)

  expect([called.includes('repo.make_repository'), await ui.find({ type: 'Button', key: 'make-repository-button' }), Boolean(await ui.find({ type: 'Button', key: 'handoff' }))]).toEqual([true, undefined, true])
  await ui.unmount()
})
