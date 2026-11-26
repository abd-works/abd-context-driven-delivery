// Requested 2026-11-26 from pml-web: a press on a format chip can take a while to filter, and nothing showed it was
// working. While session.toggle_guidance runs, the pressed chip shows the busy wheel and the bar says what it filters
// by; both clear once the answer lands, and a second press while one runs starts no second toggle.
import { expect, test } from 'claude-code/testing'

const BAND = {
  plugin: 'cdd-board',
  component: 'AbovePrompt',
  requestId: 'above-prompt',
  props: { hasSurvey: false, isCollapsed: false, isWorking: false, maxRows: 24, bodyColumns: 120, scroll: { offset: 0, bodyRows: 24 }, view: {} },
} as const

type TestOn = Parameters<Extract<Parameters<typeof test>[1], (...args: never[]) => unknown>>[1]
type Engine = Parameters<Parameters<typeof test>[1]>[0]

const FOLDER = 'C:/work/shop'
const SESSION_FILE = `${FOLDER}/.sessions/main/session.json`

// Seed: the main ticket, open in the chat's folder.
const MAIN = {
  title: 'main', last_activity: '', name: 'main', is_main: true, text: '', tags: [], children: [], is_pulled_out: false, is_stacked: false,
  session: { name: 'main', session_file: SESSION_FILE, title: 'main', repo_name: 'shop', branch: 'main', is_repository: true, root: FOLDER, scope: '', parent: '', workpath: '', practices: {}, handoff: '' },
  progress: [], column: { name: 'Discovery' }, is_closed: false, is_active: true, is_open: true, parent_choices: [], drop_targets: [], is_done: false,
  next: null, agent_context: '', worktree: FOLDER, new_chat_link: '', session_path: '', working_chat: null, stage_work: [], next_place: null, previous_place: null, dropped_work: [],
}
const OVERVIEW = { project: 'shop', is_clone: false, folder: FOLDER, practices: [], fidelities: [], columns: [{ name: 'Discovery', tickets: [{ name: 'main' }] }], active: MAIN }

// Seed: the session's guidance selection, offering the markdown group, as session.guidance_selection answers it.
const selection = (version: number, isChosen: boolean) => ({
  version, is_stage_chosen: false, stages: [], covered_stages: [], practices: [], fidelities: [], commands: {},
  formats: [{ label: 'markdown', offered: 1, formats: ['markdown'], is_selected: isChosen }],
})

/** A chat whose session offers the markdown chip, and whose toggle answers only when the test lets it. */
function chatWithFormatChip(on: TestOn) {
  const toggles: string[] = []
  let answerToggle: () => void = () => undefined
  const stored: Record<string, { value: unknown; version: number }> = {}
  const keyOf = (e: unknown) => {
    const { plugin, key } = e as { plugin: string; key: string }
    return `${plugin}:${key}`
  }
  const answer = (value: unknown) => ({ value: { content: [{ type: 'text', text: JSON.stringify(value) }], isError: false } })
  on('session.root', () => ({ value: FOLDER }))
  on('session.id', () => ({ value: 'chat-1' }))
  on('session.messages', () => ({ value: [] }))
  on('mcp.call', (_, e) => {
    const tool = (e as { tool: string }).tool
    if (tool === 'board.overview') return answer(OVERVIEW)
    if (tool === 'session.guidance_selection') return answer(selection(1, false))
    // The waiting read answers only once something changes, which nothing in this test does.
    if (tool === 'session.guidance_selection_after') return new Promise(() => undefined)
    if (tool === 'session.toggle_guidance') {
      toggles.push(tool)
      return new Promise(resolve => {
        answerToggle = () => resolve(answer(selection(2, true)))
      })
    }
    return { value: { content: [{ type: 'text', text: 'not stubbed' }], isError: true } }
  })
  on('process.run', () => ({ value: { exitCode: 0, stdout: '', stderr: '' } }))
  on('tool.list', () => ({ value: [] }))
  on('ui.status', () => ({ value: undefined }))
  on('ui.toast', () => ({ value: undefined }))
  on('ui.invalidate', () => ({ value: undefined }))
  on('clock.after', () => new Promise(() => undefined))
  on('clock.every', () => new Promise(() => undefined))
  // The busy wheel turns on each sleep while the toggle runs, so a sleep that answers at once would turn it forever.
  on('clock.sleep', () => new Promise(() => undefined))
  on('state.get', (_, e) => ({ value: stored[keyOf(e)] ?? { value: undefined, version: 0 } }))
  on('state.set', (_, e) => {
    const key = keyOf(e)
    const version = (stored[key]?.version ?? 0) + 1
    stored[key] = { value: (e as { value: unknown }).value, version }
    return { value: { isSet: true, version } }
  })
  return { toggles, answer: () => answerToggle() }
}

const WAIT_MS = 20

const settled = () => new Promise(resolve => setTimeout(resolve, WAIT_MS))

// The bar drawn again, as the engine draws it once what it shows has changed.
async function drawn($: Engine) {
  await settled()
  return $.ui.mount({ ...BAND, surface: 'desktop' })
}

// The bar with the markdown chip pressed, its toggle still running.
async function pressedOnce($: Engine) {
  const bar = await drawn($)
  void bar.press({ key: 'format-chip-markdown' })
  await bar.unmount()
  return drawn($)
}

const filteringLineOf = (ui: Awaited<ReturnType<typeof drawn>>) => ui.find({ type: 'Text', text: /filtering by markdown/ })

test('a pressed format chip says the bar is filtering by it while its toggle runs', async ($, on) => {
  chatWithFormatChip(on)

  const ui = await pressedOnce($)

  expect(await filteringLineOf(ui)).toBeDefined()
  await ui.unmount()
})

test('the filtering line clears once the toggle answers', async ($, on) => {
  const chat = chatWithFormatChip(on)
  ;(await pressedOnce($)).unmount()

  chat.answer()
  const ui = await drawn($)

  expect(await filteringLineOf(ui)).toBeUndefined()
  await ui.unmount()
})

test('a second press while the toggle runs starts no second toggle', async ($, on) => {
  const chat = chatWithFormatChip(on)
  const ui = await pressedOnce($)

  void ui.press({ key: 'format-chip-markdown' })
  await settled()

  expect(chat.toggles).toHaveLength(1)
  await ui.unmount()
})
