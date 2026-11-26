// A chat bar button puts its command in the prompt box. A chat whose folder had no CDD install when its skills were
// last read has not loaded them, so the prompt box marks a slash command naming one as "not a command", and sent, it
// reaches the agent as plain text. The button then puts in a request the agent runs through the CDD MCP tool its skill
// names, and says why the skill is missing. Every button goes through the one promptCommand; the version badge's
// "Update and reinstall" is pressed here because it needs no board to draw.
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
    bodyColumns: 120,
    scroll: { offset: 0, bodyRows: 24 },
    view: {},
  },
} as const

// Seed: the command the update button puts in the prompt box.
const INSTALL_LATEST = '/harness:installation:install-latest'
// Seed: the version badge as a check left it, a minor release behind, its update dialog open.
const VERSION = {
  data: { version: 'v1.2', latest: 'v1.3', standing: 'behind minor', summary: 'v1.3 is out' },
  problem: null,
  isAsking: true,
  update: 'idle',
  error: null,
}

type TestOn = Parameters<Extract<Parameters<typeof test>[1], (...args: never[]) => unknown>>[1]

/** A chat whose slash commands are those named, whose prompt box takes what is put in it, and whose toasts are kept;
 * the cdd server answers nothing. */
function chatWithCommands(on: TestOn, names: string[]) {
  const filled: string[] = []
  const toasts: string[] = []
  const stored: Record<string, { value: unknown; version: number }> = { 'cdd-board:cddVersion': { value: VERSION, version: 1 } }
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
  on('command.list', () => ({ value: names.map(name => ({ name, description: '', source: 'user' as const })) }))
  on('prompt.fill', (_, e) => {
    filled.push((e as { text: string }).text)
    return { isFilled: true }
  })
  on('ui.toast', (_, e) => {
    toasts.push((e as { text: string }).text)
    return { value: undefined }
  })
  return { filled, toasts }
}

async function pressUpdate($: Parameters<Extract<Parameters<typeof test>[1], (...args: never[]) => unknown>>[0]) {
  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  await ui.press({ key: 'update-confirm' })
  await ui.unmount()
}

test('a command the chat has loaded goes in the prompt box as it is', async ($, on) => {
  const { filled } = chatWithCommands(on, ['compact', 'harness:installation:install-latest'])

  await pressUpdate($)

  expect(filled).toEqual([INSTALL_LATEST])
})

test('a command the chat has not loaded goes in without its slash, as a request for its MCP tool', async ($, on) => {
  const { filled } = chatWithCommands(on, ['compact', 'help'])

  await pressUpdate($)

  expect(filled).toEqual([
    'Run the CDD skill harness:installation:install-latest, which this chat has not loaded, through the MCP tool or script its SKILL.md names: harness:installation:install-latest',
  ])
})

test('a command the chat has not loaded says CDD was not installed in this folder when the chat read its skills', async ($, on) => {
  const { toasts } = chatWithCommands(on, ['compact', 'help'])

  await pressUpdate($)

  expect(toasts.join(' ')).toContain('This chat has not loaded the CDD skill harness:installation:install-latest')
})
