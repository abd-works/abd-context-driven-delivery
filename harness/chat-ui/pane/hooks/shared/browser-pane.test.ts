// Why a page did not open in Claude's Browser pane, as the chat bar tells the person, and who opens it instead. The
// health panel's Files icon is pressed: it opens its app through the same openInBrowserPane every app and the chat bar's
// files button open theirs through, and it needs no board to draw.
import { expect, test } from 'claude-code/testing'

import { askedToOpen, whyPaneNotCalled } from './browser-pane'

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

// Interaction: Claude Desktop's refusal of a plugin's own call to the browser pane while the chat is in auto mode.
const AUTO_MODE_REASON = "Not run: in auto mode Claude Desktop doesn't run this tool when a plugin's own code calls it. Have Claude make the call."
const AUTO_MODE_REFUSAL = `cdd-chat-ui: $.mcp.call(Claude_Browser, tabs_context) refused: PreToolUse:mcp__Claude_Browser__tabs_context hook error: ${AUTO_MODE_REASON}`
// Seed: the Files app, running, as app.open and the server's health report answer it.
const FILES_APP = { label: 'Files', status: 'running', port: 9783, url: 'http://127.0.0.1:9783/', server: { folder: 'C:/cdd/files', command: ['node', 'serve.ts'] } }
const HEALTH = { connection: 'connected', report: { apps: [FILES_APP] }, toolCount: 1, problem: null, attempt: 0 }

type TestOn = Parameters<Extract<Parameters<typeof test>[1], (...args: never[]) => unknown>>[1]
type Engine = Parameters<Extract<Parameters<typeof test>[1], (...args: never[]) => unknown>>[0]

/** A chat in auto mode, its health panel showing the Files app running: Claude Desktop refuses every call the plugin
 * makes to the browser pane, the cdd server answers app.open with the Files app, and a prompt the bar submits reaches
 * the chat, or is dropped with dropReason. Answers what the chat was asked and the failure lines shown. */
function chatInAutoMode(on: TestOn, dropReason?: string) {
  const asked: string[] = []
  const stored: Record<string, { value: unknown; version: number }> = { 'cdd-board:serverHealth': { value: HEALTH, version: 1 } }
  const keyOf = (e: unknown) => {
    const { plugin, key } = e as { plugin: string; key: string }
    return `${plugin}:${key}`
  }
  on('session.root', () => ({ value: 'C:/work' }))
  on('session.id', () => ({ value: 'chat-1' }))
  on('mcp.call', (_, e) => {
    const { server, tool } = e as { server: string; tool: string }
    if (server === 'Claude_Browser') return { deny: AUTO_MODE_REASON }
    if (tool === 'app.open') return { value: { content: [{ type: 'text', text: JSON.stringify(FILES_APP) }], isError: false } }
    return { deny: 'no MCP server cdd' }
  })
  on('tool.list', () => ({ value: [] }))
  on('process.run', () => ({ value: { exitCode: 128, stdout: '', stderr: 'fatal: not a git repository', isStdoutTruncated: false, isStderrTruncated: false } }))
  on('clock.after', () => new Promise(() => undefined))
  on('clock.every', () => new Promise(() => undefined))
  on('state.get', (_, e) => ({ value: stored[keyOf(e)] ?? { value: undefined, version: 0 } }))
  on('state.set', (_, e) => {
    const key = keyOf(e)
    const version = (stored[key]?.version ?? 0) + 1
    stored[key] = { value: (e as { value: unknown }).value, version }
    return { value: { isSet: true, version } }
  })
  on('prompt.submit', (_, e) => {
    const { text } = e as { text: string }
    asked.push(text)
    return dropReason === undefined ? { text } : { drop: dropReason }
  })
  const opening = () => (stored['cdd-board:appOpening']?.value ?? null) as { state: string; error: string | null } | null
  return { asked, opening }
}

async function pressFiles($: Engine) {
  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  await ui.press({ key: 'health-app-Files' })
  await ui.unmount()
}

test('a page refused in auto mode tells the person to choose Bypass permissions at the bottom of the chat box', () => {
  expect(whyPaneNotCalled(AUTO_MODE_REFUSAL)).toContain('click the permission mode menu at the bottom of the chat box and choose Bypass permissions')
})

// Reported 2026-11-18 (Nov 18 demo): opening the Files viewer from the chat bar asked for Bypass permissions. Claude
// Desktop refuses only the plugin's own call; the same call made by Claude runs in auto mode.
test('a page refused in auto mode is handed to Claude to open in the browser pane', async ($, on) => {
  const { asked } = chatInAutoMode(on)

  await pressFiles($)

  expect(asked).toEqual([askedToOpen(`${FILES_APP.url}?project=C%3A%2Fwork&chat=chat-1`)])
})

test('a page handed to Claude leaves no failure to fix', async ($, on) => {
  const { opening } = chatInAutoMode(on)

  await pressFiles($)

  expect(opening()?.state).toBe('idle')
})

test('a page refused in auto mode that Claude was not asked to open still says how to let the bar open it', async ($, on) => {
  const { opening } = chatInAutoMode(on, 'a turn is running')

  await pressFiles($)

  expect(opening()?.error ?? '').toContain('choose Bypass permissions')
})
