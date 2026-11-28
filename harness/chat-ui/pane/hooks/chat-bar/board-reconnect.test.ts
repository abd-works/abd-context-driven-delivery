// (S) Claude Code --> Ask The Chat To Reconnect To CDD
// When the chat bar's board read keeps failing after a chat opens, the bar sends the chat a prompt of its own with the
// steps to reconnect to cdd, so nobody has to notice the red line and press Fix. It sends one prompt for each outage:
// the reads that follow the prompt's own turn fail too, and must not send another.
import { expect, test } from 'claude-code/testing'

// Seed: the folder the chat works in.
const FOLDER = 'C:/work/shop'
// Seed: what Claude Code answered board.overview while the chat had no cdd server (chat bar, 2026-11-26).
const NO_SERVER = 'no connected MCP tool "board.overview" on a server named "plugin:cdd:cdd"'
// The wait between the bar's opening reads of the board.
const OPENING_RETRY_MS = 2000

type TestOn = Parameters<Extract<Parameters<typeof test>[1], (...args: never[]) => unknown>>[1]

/** A chat in FOLDER whose board.overview fails until answersFrom reads have been made, and then answers; every other cdd
 * tool fails. The opening retries run at once. Answers the prompts the bar sent. */
function chatWhoseBoardFails(on: TestOn, answersFrom = Infinity) {
  const submitted: string[] = []
  const stored: Record<string, { value: unknown; version: number }> = {}
  let boardReads = 0
  const keyOf = (e: unknown) => {
    const { plugin, key } = e as { plugin: string; key: string }
    return `${plugin}:${key}`
  }
  on('session.root', () => ({ value: FOLDER }))
  on('session.id', () => ({ value: 'chat-1' }))
  on('session.messages', () => ({ value: [] }))
  on('session.start', (_, e) => ({ cwd: (e as { cwd: string }).cwd }))
  on('command.register', () => ({ value: undefined }))
  on('mcp.call', (_, e) => {
    const tool = (e as { tool: string }).tool
    if (tool === 'board.overview') {
      boardReads += 1
      if (boardReads >= answersFrom) return { value: { content: [{ type: 'text', text: JSON.stringify({ sessions: [] }) }] } }
    }
    return { value: { content: [{ type: 'text', text: NO_SERVER }], isError: true } }
  })
  on('prompt.submit', (_, e) => {
    const { text } = e as { text: string }
    submitted.push(text)
    return { text }
  })
  on('tool.list', () => ({ value: [] }))
  on('ui.status', () => ({ value: undefined }))
  on('ui.invalidate', () => ({ value: undefined }))
  on('ui.toast', () => ({ value: undefined }))
  on('clock.after', (_, e) => {
    if ((e as { ms: number }).ms !== OPENING_RETRY_MS) return new Promise(() => undefined)
    return new Promise(resolve => setTimeout(() => resolve({ value: undefined }), 1))
  })
  on('clock.sleep', () => ({ value: undefined }))
  on('clock.every', () => new Promise(() => undefined))
  on('state.get', (_, e) => ({ value: stored[keyOf(e)] ?? { value: undefined, version: 0 } }))
  on('state.set', (_, e) => {
    const key = keyOf(e)
    const version = (stored[key]?.version ?? 0) + 1
    stored[key] = { value: (e as { value: unknown }).value, version }
    return { value: { isSet: true, version } }
  })
  on('fs.exists', () => ({ value: true }))
  on('fs.read', () => ({ value: '{}' }))
  on('process.run', () => ({ value: { exitCode: 128, stdout: '', stderr: 'fatal: not a git repository' } }))
  return { submitted, boardReadCount: () => boardReads }
}

const start = ($: { session: { start: (e: object) => Promise<unknown> } }) => $.session.start({ cwd: FOLDER, surface: 'desktop', isInteractive: true })

const WAIT_MS = 20
const WAITS = 100

// The opening reads run on the clock after the chat has started, so a test waits until they have all been made.
async function readsMade(count: () => number, atLeast: number): Promise<void> {
  for (let tries = 0; tries < WAITS && count() < atLeast; tries += 1) await new Promise(resolve => setTimeout(resolve, WAIT_MS))
  await new Promise(resolve => setTimeout(resolve, WAIT_MS * 5))
}

// The bar reads the board once as the chat starts and then up to 30 times while cdd connects.
const OPENING_READS = 31

test('a board that never answers while the chat opens sends the chat one prompt to reconnect to cdd', async ($, on) => {
  const { submitted, boardReadCount } = chatWhoseBoardFails(on)

  await start($)
  await readsMade(boardReadCount, OPENING_READS)

  expect(submitted.length).toBe(1)
  expect(submitted[0]).toContain(`The board did not answer: ${NO_SERVER}`)
  expect(submitted[0]).toContain('reconnect_session_connector')
})

test('a board that answers while the chat opens sends no prompt', async ($, on) => {
  const { submitted, boardReadCount } = chatWhoseBoardFails(on, 3)

  await start($)
  await readsMade(boardReadCount, 3)

  expect(submitted).toEqual([])
})
