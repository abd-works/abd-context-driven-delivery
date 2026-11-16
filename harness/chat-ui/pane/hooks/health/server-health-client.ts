import { atom, read, update } from 'claude-code'
import type { EngineInterface } from 'claude-code'

import type { AppData } from '@cdd/harness/diagnostics/app'
import type { ServerHealthData } from '@cdd/harness/diagnostics/server-health'

import type { HealthViewJson, InstallJson, ServerHealthJson, TestRunJson, ToastedRunsJson } from '../../types'
import { showFailure, shownAsFailure } from '../error-display/failure-client'
import { callTool, CddToolFailed } from '../shared/cdd-tool'

export const REPORT_TOOL = 'server-health.report'
// The CDD Kanban's label, which App.load takes as its identity: the board the chat checks in with.
export const KANBAN = 'Kanban'
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
const toastedRuns = atom({ plugin: 'cdd-board', key: 'toastedRuns' } as const, { runIds: [] } as ToastedRunsJson)
// How many toasted runs the chat remembers; older ones have long since been replaced by newer runs.
const TOASTED_RUNS_KEPT = 20
const install = atom({ plugin: 'cdd-board', key: 'install' } as const, { state: 'idle', error: null } as InstallJson)

type Answer = Pick<ServerHealthJson, 'connection' | 'report' | 'problem'>

export class ServerHealthClient {
  constructor(private readonly json: ServerHealthData | null) {}

  // Every app a module registered, each with its status, port and url; none before cdd has reported.
  get apps(): AppData[] {
    return this.json?.apps ?? []
  }

  // The app the status row and the board's chat routes name by its label, its identity.
  appLabelled(label: string): AppData | undefined {
    return this.apps.find(app => app.label === label)
  }

  get isHookServerRunning(): boolean {
    return this.json?.is_hook_server_running ?? false
  }

  // The latest heavy and e2e run the cdd server ran on main, each that has run.
  get testRuns(): TestRunJson[] {
    return ((this.json as { test_runs?: TestRunJson[] } | null)?.test_runs) ?? []
  }

  // A run that failed after its tier's run before passed: the chat raises a toast for it.
  get newFailures(): TestRunJson[] {
    return this.testRuns.filter(run => run.state === 'failed' && run.is_new_failure)
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
    if (run.exitCode !== 0) await showFailure($, `The install failed: ${lastLines(run.stderr)}`, `Install on the health panel, running ${(await installCommand($)).join(' ')} in ${folder}`)
  } catch (failure) {
    await update($, install, () => ({ state: 'failed', error: String(failure) }))
    await shownAsFailure($, 'The install did not run', 'Install on the health panel')(failure)
  }
}

// A server that cannot be reached is disconnected. One from another checkout has no such tool, and answers in words
// (KeyError: 'server-health.report') or with isError: its tools are missing.
async function askServer($: EngineInterface): Promise<Answer> {
  try {
    return { connection: 'connected', report: await callTool<ServerHealthData>($, REPORT_TOOL, {}), problem: null }
  } catch (failure) {
    if (failure instanceof CddToolFailed) return { connection: 'tools-missing', report: null, problem: failure.message }
    return { connection: 'disconnected', report: null, problem: String(failure) }
  }
}

async function recordAnswer($: EngineInterface, answer: Answer): Promise<void> {
  const tools = await $.tool.list()
  const toolCount = tools.filter(tool => tool.name.startsWith(TOOL_PREFIX)).length
  await update($, serverHealth, () => ({ ...answer, toolCount, attempt: 0 }))
  await toastNewFailures($, new ServerHealthClient(answer.report))
}

// Each new failure of a scheduled test run is raised once, in the chat that reads the report first after it ends.
async function toastNewFailures($: EngineInterface, health: ServerHealthClient): Promise<void> {
  const { runIds } = await read($, toastedRuns)
  const fresh = health.newFailures.filter(run => !runIds.includes(run.run_id))
  if (fresh.length === 0) return
  for (const run of fresh) $.ui.toast(`The scheduled ${run.name} tests failed on main: ${lastLines(run.summary)}`)
  await update($, toastedRuns, held => ({ runIds: [...held.runIds, ...fresh.map(run => run.run_id)].slice(-TOASTED_RUNS_KEPT) }))
}

// The cdd home publishes this mod with the command that installs for a chat's folder: the served checkout's install
// script on the server's Python, which installs from the chat's folder when that is a CDD checkout.
async function installCommand($: EngineInterface): Promise<string[]> {
  const published = `${$.plugin.root}/install.json`
  if (!(await $.fs.exists(published))) throw new Error(`this board mod was not published by a cdd home, so it has no install command; run python scripts/install.py --ide Claude in a CDD checkout`)
  return commandIn(await $.fs.read(published))
}

// The install command install.json holds, as the cdd home writes it.
function commandIn(installJson: string): string[] {
  return (JSON.parse(installJson) as { command: string[] }).command
}

const lastLines = (text: string): string => text.trim().split('\n').slice(-ERROR_LINES_SHOWN).join('\n')
