import { atom, read, update } from 'claude-code'
import type { EngineInterface } from 'claude-code'

import type { ServerHealthData } from '@cdd/harness/diagnostics/server-health'

import type { HealthViewJson, InstallJson, ServerHealthJson } from '../../types'

// The cdd plugin declares the server, and Claude Code names a plugin's server plugin:{plugin}:{server}.
export const SERVER = 'plugin:cdd:cdd'
export const REPORT_TOOL = 'server-health.report'
export const RECONNECT_TRIES = 3
// Its tools are named mcp__plugin_{plugin}_{server}__{tool}.
const TOOL_PREFIX = 'mcp__plugin_cdd_cdd__'
const RECONNECT_WAIT_MS = 2000
const INSTALL_TIMEOUT_MS = 600000
const FIRST_LOOK_WAIT_MS = 5000
const ERROR_LINES_SHOWN = 1

const serverHealth = atom({ plugin: 'cdd-board', key: 'serverHealth' } as const, {
  connection: 'reconnecting',
  report: null,
  toolCount: 0,
  problem: null,
  attempt: 0,
} as ServerHealthJson)
const healthView = atom({ plugin: 'cdd-board', key: 'healthView' } as const, { areDetailsOpen: false } as HealthViewJson)
const install = atom({ plugin: 'cdd-board', key: 'install' } as const, { state: 'idle', error: null } as InstallJson)

type Answer = Pick<ServerHealthJson, 'connection' | 'report' | 'problem'>

export class ServerHealthClient {
  constructor(private readonly json: ServerHealthData | null) {}

  get kanbanAppPort(): number | null {
    return this.json?.kanban_app_port ?? null
  }

  // Where a chat reaches the session board, whether or not it answers yet; empty before cdd has reported.
  get kanbanAppUrl(): string {
    return this.json?.kanban_app_url ?? ''
  }

  get graphAppPort(): number | null {
    return this.json?.graph_app_port ?? null
  }

  get isHookServerRunning(): boolean {
    return this.json?.is_hook_server_running ?? false
  }
}

export function currentServerHealth($: EngineInterface) {
  return read($, serverHealth)
}

export function currentHealthView($: EngineInterface) {
  return read($, healthView)
}

export function currentInstall($: EngineInterface) {
  return read($, install)
}

// The server may still be connecting as the session starts, so the first look waits a moment.
export function refreshHealthSoon($: EngineInterface): void {
  $.clock.after(FIRST_LOOK_WAIT_MS, () => void refreshHealth($))
}

export async function refreshHealth($: EngineInterface): Promise<void> {
  const { connection, attempt } = await read($, serverHealth)
  if (connection === 'reconnecting' && attempt > 0) return
  await recordAnswer($, await askServer($))
}

// A plugin can connect only servers its own manifest lists, and cdd is installed at user level, so this
// asks cdd again and leaves Claude Code to dial it, which it does on a call to a server not yet connected.
export async function reconnect($: EngineInterface, onRestored: () => Promise<void>, attempt = 1): Promise<void> {
  await update($, serverHealth, health => ({ ...health, connection: 'reconnecting', attempt }))
  const answer = await askServer($)
  if (answer.connection === 'disconnected' && attempt < RECONNECT_TRIES) {
    $.clock.after(RECONNECT_WAIT_MS, () => void reconnect($, onRestored, attempt + 1))
    return
  }
  await recordAnswer($, answer)
  if (answer.connection === 'connected') await onRestored()
}

export async function openDetails($: EngineInterface): Promise<void> {
  await update($, healthView, () => ({ areDetailsOpen: true }))
}

export async function hideDetails($: EngineInterface): Promise<void> {
  await update($, healthView, view => ({ ...view, areDetailsOpen: false }))
}

// The MCP host may be what is broken, so the install runs from here and not through a cdd tool.
export async function runInstall($: EngineInterface): Promise<void> {
  await update($, install, () => ({ state: 'running', error: null }))
  try {
    const folder = await $.session.root()
    const run = await $.process.run([...(await installCommand($)), folder], { cwd: folder, timeoutMs: INSTALL_TIMEOUT_MS })
    await update($, install, () => (run.exitCode === 0 ? { state: 'installed', error: null } : { state: 'failed', error: lastLines(run.stderr) }))
  } catch (failure) {
    await update($, install, () => ({ state: 'failed', error: String(failure) }))
  }
}

async function askServer($: EngineInterface): Promise<Answer> {
  let result
  try {
    result = await $.mcp.call(SERVER, REPORT_TOOL, {})
  } catch (failure) {
    return { connection: 'disconnected', report: null, problem: String(failure) }
  }
  const text = result.content[0]?.text
  const report = result.isError ? null : reportFrom(text)
  if (report === null) return { connection: 'tools-missing', report: null, problem: text ?? `${REPORT_TOOL} sent back nothing` }
  return { connection: 'connected', report, problem: null }
}

// A server from another checkout has no such tool, and answers in words: KeyError: 'server-health.report'.
function reportFrom(text: string | undefined): ServerHealthData | null {
  if (text === undefined) return null
  try {
    return JSON.parse(text) as ServerHealthData
  } catch {
    return null
  }
}

async function recordAnswer($: EngineInterface, answer: Answer): Promise<void> {
  const tools = await $.tool.list()
  const toolCount = tools.filter(tool => tool.name.startsWith(TOOL_PREFIX)).length
  await update($, serverHealth, () => ({ ...answer, toolCount, attempt: 0 }))
}

// The cdd home publishes this mod with the command that installs for a chat's folder: the served checkout's install
// script on the server's Python, which installs from the chat's folder when that is a CDD checkout.
async function installCommand($: EngineInterface): Promise<string[]> {
  const published = `${$.plugin.root}/install.json`
  if (!(await $.fs.exists(published))) throw new Error(`this board mod was not published by a cdd home, so it has no install command; run python scripts/install.py --ide Claude in a CDD checkout`)
  return (JSON.parse(await $.fs.read(published)) as { command: string[] }).command
}

const lastLines = (text: string): string => text.trim().split('\n').slice(-ERROR_LINES_SHOWN).join('\n')
