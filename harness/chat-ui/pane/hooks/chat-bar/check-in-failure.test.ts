// (S) Claude Code --> Check In With CDD
// The chat bar checks in with cdd every second through chat.check_in. When check-ins keep failing, the bar shows the
// server's own words for the failure, such as the LaneUnreachable a restarting dev lane gives, never a JSON parse error
// from reading those words as the commands the check-in answers.
import { expect, test } from 'claude-code/testing'

// Seed: the folder the chat works in.
const FOLDER = 'C:/work/shop'
// Seed: what the cdd server answered chat.check_in while the dev lane restarted (debug report 2026-11-20).
const LANE_UNREACHABLE = 'LaneUnreachable: the cdd server on port 47801 did not answer a tool call sent from the other lane: [WinError 10054] An existing connection was forcibly closed by the remote host'
// The check-in's period, in milliseconds, and how many periods the test lets pass: more than the ten failed check-ins
// the bar waits for before it shows one.
const CHECK_IN_MS = 1000
const PERIODS = 12

type TestOn = Parameters<Extract<Parameters<typeof test>[1], (...args: never[]) => unknown>>[1]

/** A chat in FOLDER, with CDD installed there, whose cdd server answers chat.check_in with the server's failure text,
 * flagged isError or not; every other tool fails. Answers each failure the bar showed, in order. */
function chatWhoseCheckInFails(on: TestOn, isError: boolean) {
  const shown: string[] = []
  const stored: Record<string, { value: unknown; version: number }> = {}
  let periods = 0
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
    if (tool === 'chat.check_in') return { value: { content: [{ type: 'text', text: LANE_UNREACHABLE }], isError } }
    return { value: { content: [{ type: 'text', text: 'not stubbed' }], isError: true } }
  })
  on('tool.list', () => ({ value: [] }))
  on('ui.status', () => ({ value: undefined }))
  on('ui.invalidate', () => ({ value: undefined }))
  on('ui.toast', () => ({ value: undefined }))
  on('clock.after', () => new Promise(() => undefined))
  on('clock.sleep', () => ({ value: undefined }))
  on('clock.every', (_, e) => {
    if ((e as { ms: number }).ms !== CHECK_IN_MS || periods >= PERIODS) return new Promise(() => undefined)
    periods += 1
    return new Promise(resolve => setTimeout(() => resolve({ value: undefined }), 1))
  })
  on('state.get', (_, e) => ({ value: stored[keyOf(e)] ?? { value: undefined, version: 0 } }))
  on('state.set', (_, e) => {
    const key = keyOf(e)
    const value = (e as { value: unknown }).value
    if (key === 'cdd-board:failure' && value) shown.push((value as { failure: string }).failure)
    const version = (stored[key]?.version ?? 0) + 1
    stored[key] = { value, version }
    return { value: { isSet: true, version } }
  })
  on('fs.exists', () => ({ value: true }))
  on('fs.read', () => ({ value: '{}' }))
  on('process.run', () => ({ value: { exitCode: 128, stdout: '', stderr: 'fatal: not a git repository' } }))
  return { shown, periodsPassed: () => periods }
}

const start = ($: { session: { start: (e: object) => Promise<unknown> } }) => $.session.start({ cwd: FOLDER, surface: 'desktop', isInteractive: true })

const WAIT_MS = 20
const WAITS = 50

// The check-ins run on the clock after the chat has started, so a test waits for the bar to show a check-in failure.
async function checkInFailureShown(shown: string[]): Promise<string | undefined> {
  const checkInFailure = () => shown.find(failure => failure.startsWith('This chat has not reached cdd'))
  for (let tries = 0; tries < WAITS && !checkInFailure(); tries += 1) await new Promise(resolve => setTimeout(resolve, WAIT_MS))
  return checkInFailure()
}

// Reported 2026-11-20: while the dev lane restarted, chat.check_in answered LaneUnreachable, and the bar showed
// 'JSON Parse error: Unexpected identifier "chat"' instead.
test("a check-in answered with the server's failure text shows that text, not a JSON parse error", async ($, on) => {
  const { shown } = chatWhoseCheckInFails(on, false)

  await start($)

  expect(await checkInFailureShown(shown)).toBe(`This chat has not reached cdd for 10 check-ins: chat.check_in failed: ${LANE_UNREACHABLE}`)
})

test("a check-in the server flags as failed shows the server's text, naming chat.check_in", async ($, on) => {
  const { shown } = chatWhoseCheckInFails(on, true)

  await start($)

  expect(await checkInFailureShown(shown)).toBe(`This chat has not reached cdd for 10 check-ins: chat.check_in failed: ${LANE_UNREACHABLE}`)
})
