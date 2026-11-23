// (S) Claude Code --> Install CDD Into Chat Folder
// When the board mod starts in a chat whose folder has no .claude/skills or .claude/commands, it runs the installer into
// that folder, the same install the health panel's Run install runs, so a chat in a new project gets CDD's skills and
// commands without anyone pressing a button.
import { expect, test } from 'claude-code/testing'

// Seed: the folder the chat works in.
const FOLDER = 'C:/work/shop'
// Seed: the install command the cdd home publishes beside the mod.
const INSTALL = ['C:/Python312/python.exe', 'C:/cdd/runtime/scripts/install.py', '--ide', 'Claude', '--from-chat']

type TestOn = Parameters<Extract<Parameters<typeof test>[1], (...args: never[]) => unknown>>[1]

/** A chat starting in FOLDER, holding the IDE folders named in present; the cdd server answers nothing. Answers each
 * command the mod ran, and a promise that settles once both install folders were looked for. */
function chatStartingWith(on: TestOn, present: string[], installExit = 0) {
  const ran: string[][] = []
  const lookedFor: string[] = []
  let looked: () => void = () => undefined
  const bothLooked = new Promise<void>(resolve => (looked = resolve))
  const stored: Record<string, { value: unknown; version: number }> = {}
  const keyOf = (e: unknown) => {
    const { plugin, key } = e as { plugin: string; key: string }
    return `${plugin}:${key}`
  }
  on('session.root', () => ({ value: FOLDER }))
  on('session.id', () => ({ value: 'chat-1' }))
  on('session.messages', () => ({ value: [] }))
  on('session.start', (_, e) => ({ cwd: (e as { cwd: string }).cwd }))
  on('command.register', () => ({ value: undefined }))
  on('mcp.call', () => ({ deny: 'no MCP server cdd' }))
  on('tool.list', () => ({ value: [] }))
  on('ui.status', () => ({ value: undefined }))
  on('ui.invalidate', () => ({ value: undefined }))
  on('ui.toast', () => ({ value: undefined }))
  on('clock.after', () => new Promise(() => undefined))
  on('clock.every', () => new Promise(() => undefined))
  on('state.get', (_, e) => ({ value: stored[keyOf(e)] ?? { value: undefined, version: 0 } }))
  on('state.set', (_, e) => {
    const key = keyOf(e)
    const version = (stored[key]?.version ?? 0) + 1
    stored[key] = { value: (e as { value: unknown }).value, version }
    return { value: { isSet: true, version } }
  })
  on('fs.exists', (_, e) => {
    const path = slashed((e as { path: string }).path)
    if (path.endsWith('install.json')) return { value: true }
    lookedFor.push(path)
    if (lookedFor.length === 2) looked()
    return { value: present.some(folder => path === `${FOLDER}/${folder}`) }
  })
  on('fs.read', () => ({ value: JSON.stringify({ command: INSTALL }) }))
  on('process.run', (_, e) => {
    const argv = (e as { argv: string[] }).argv
    ran.push(argv)
    const exitCode = argv.includes('--from-chat') ? installExit : 0
    return { value: { exitCode, stdout: '', stderr: exitCode === 0 ? '' : `not installed: ${FOLDER} is the home folder` } }
  })
  return { ran, bothLooked, lookedFor, stored }
}

const start = ($: { session: { start: (e: object) => Promise<unknown> } }) => $.session.start({ cwd: FOLDER, surface: 'desktop', isInteractive: true })

// The install runs after the chat has started, without holding it up, so a test waits for it to be asked.
const WAIT_MS = 20
const WAITS = 25
async function settled(ran: string[][], until: (ran: string[][]) => boolean): Promise<void> {
  for (let tries = 0; tries < WAITS && !until(ran); tries += 1) await new Promise(resolve => setTimeout(resolve, WAIT_MS))
}

// The engine hands a path on in the platform's own separators.
const slashed = (path: string) => path.replaceAll('\\', '/')

const installs = (ran: string[][]) => ran.filter(argv => argv.includes('--from-chat'))

test("a chat started in a folder without CDD's skills and commands runs the install into that folder", async ($, on) => {
  const { ran } = chatStartingWith(on, [])

  await start($)
  await settled(ran, found => installs(found).length > 0)

  expect(installs(ran)).toEqual([[...INSTALL, FOLDER]])
})

test('a chat started in a folder whose commands are missing runs the install, though its skills are there', async ($, on) => {
  const { ran } = chatStartingWith(on, ['.claude', '.claude/skills'])

  await start($)
  await settled(ran, found => installs(found).length > 0)

  expect(installs(ran)).toEqual([[...INSTALL, FOLDER]])
})

test('a chat started in a folder CDD is installed in runs no install', async ($, on) => {
  const { ran, bothLooked, lookedFor } = chatStartingWith(on, ['.claude', '.claude/skills', '.claude/commands'])

  await start($)
  await bothLooked
  await settled(ran, () => false)

  expect([lookedFor, installs(ran)]).toEqual([[`${FOLDER}/.claude/skills`, `${FOLDER}/.claude/commands`], []])
})

// The install script refuses the home folder, a temporary folder and the desktop app's spare folders (NOT_A_PROJECT_EXIT
// in scripts/install.py); nobody asked for the install at chat start, so the refusal is no failure.
test('a chat started in a folder the install script refuses shows no failure and leaves the install idle', async ($, on) => {
  const { ran, stored } = chatStartingWith(on, [], 3)

  await start($)
  await settled(ran, found => installs(found).length > 0)
  await settled(ran, () => stored['cdd-board:install']?.value !== undefined && (stored['cdd-board:install'].value as { state: string }).state !== 'running')

  expect([stored['cdd-board:install']?.value, stored['cdd-board:failure']?.value ?? null]).toEqual([{ state: 'idle', error: null }, null])
})
