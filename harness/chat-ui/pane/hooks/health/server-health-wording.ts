import type { AppData } from '@cdd/harness/diagnostics/app'
import type { ServerHealthData } from '@cdd/harness/diagnostics/server-health'

import type { AppOpeningJson, E2eReviewJson, InstallJson, ServerHealthJson, TestRunJson } from '../../types'
import { BRAND } from '../shared/brand'
import { SERVER } from '../shared/cdd-tool'
import { RECONNECT_TRIES, REPORT_TOOL, ServerHealthClient } from './server-health-client'

// The server health panel's words: what each part reads, the headline, the details and the install line. The panel's
// view paints them; ServerHealthClient carries the report they are read from.

// app: the label of the app a press on the part opens; none for a part that is not an app. isDown: a part the chat
// cannot work without, stopped.
export type Part = { icon: string; label: string; value: string; isUp: boolean; isDown?: boolean; app?: string }

// A part shows as its icon alone: green while it runs or passed, red when the MCP host is down or a scheduled test run
// failed, grey while an app does not run or a test run has not ended.
export function colourOf(part: Part): string {
  if (part.isUp) return BRAND.success
  return part.isDown ? BRAND.error : BRAND.muted
}

// What hovering a part's icon shows, its name and how it stands: Files: running :8783.
export function tooltipOf(part: Part): string {
  return `${part.label}: ${part.value}`
}

// Each app's mark in the status row; an app registered later shows the plain one.
const APP_ICONS: Record<string, string> = { Kanban: '▦', Graph: '◈', 'Story UI': '✎' }
const APP_ICON = '▣'
const RUNNING: AppData['status'] = 'running'

// An app reads its status, and the port it answers on while it runs: running :8778, not running, not installed.
function appPartOf(app: AppData): Part {
  const isUp = app.status === RUNNING
  return { icon: APP_ICONS[app.label] ?? APP_ICON, label: app.label, value: isUp ? `${app.status} :${app.port}` : app.status, isUp, app: app.label }
}

// The MCP host and the tools it loaded are one part: running with 236 tools, or down.
function hostPartOf({ connection, toolCount }: ServerHealthJson): Part {
  const isUp = connection === 'connected'
  const value = isUp ? `running with ${toolCount} tools` : connection === 'disconnected' ? 'down' : connection === 'tools-missing' ? `running, ${REPORT_TOOL} missing from its ${toolCount} tools` : 'connecting'
  return { icon: '⬢', label: 'MCP host', value, isUp, isDown: connection === 'disconnected' }
}

// A scheduled test tier reads how its latest run on main ended: Heavy tests: passed, started 2026-11-15T12:00. It is
// green once passed, red once failed, and grey while it runs or was abandoned.
function testRunPartOf(run: TestRunJson): Part {
  const label = `${run.name === 'e2e' ? 'E2e' : 'Heavy'} tests`
  return { icon: run.name === 'e2e' ? '◎' : '◉', label, value: `${run.state}, started ${run.started.slice(0, 16)}`, isUp: run.state === 'passed', isDown: run.state === 'failed' }
}

// The latest scheduled e2e run's screen review: E2e screens: run-2026-11-17-06-00-00, 3 changed, 1 missed, 0 not
// judged. Green with nothing missed or unjudged, red once a step is missed by the tests, grey while steps await a verdict.
function e2eReviewPartOf(review: E2eReviewJson): Part {
  const missed = review.missed_steps.length
  const unjudged = review.unjudged_steps.length
  const value = `${review.run}, ${review.changed_steps.length} changed, ${missed} missed, ${unjudged} not judged`
  return { icon: '⧉', label: 'E2e screens', value, isUp: missed === 0 && unjudged === 0, isDown: missed > 0 }
}

export function partsOf(health: ServerHealthJson): Part[] {
  const client = new ServerHealthClient(health.report as ServerHealthData | null)
  const { apps, isHookServerRunning: isHookRunning, e2eReview } = client
  return [
    hostPartOf(health),
    ...apps.map(appPartOf),
    { icon: '↪', label: 'Hook server', value: isHookRunning ? 'running' : 'not installed', isUp: isHookRunning },
    ...client.testRuns.map(testRunPartOf),
    ...(e2eReview ? [e2eReviewPartOf(e2eReview)] : []),
  ]
}

// Opening the Story UI., or what failed and how to fix it, once a person pressed an app; nothing otherwise.
export function appLineOf({ label, state, error }: AppOpeningJson): string {
  if (state === 'opening') return `Opening the ${label}.`
  return state === 'failed' ? error ?? `The ${label} did not open.` : ''
}

export function headlineOf({ connection, attempt, toolCount }: ServerHealthJson): { title: string; detail: string } {
  if (connection === 'connected') return { title: '', detail: '' }
  if (connection === 'disconnected') return { title: 'Disconnected', detail: `${SERVER} stopped.` }
  if (connection === 'tools-missing') return { title: 'Tools missing', detail: `${toolCount} loaded, ${REPORT_TOOL} is not one of them.` }
  if (attempt === 0) return { title: 'Connecting', detail: `Waiting for ${SERVER} to answer.` }
  return { title: 'Reconnecting', detail: `Waiting for ${SERVER} to answer. Try ${attempt} of ${RECONNECT_TRIES}.` }
}

export function detailsOf({ connection, problem }: ServerHealthJson, install: InstallJson): [string, string][] {
  const fix = connection === 'tools-missing' ? 'Press Run install, then open a new session.' : 'Press Reconnect. If that fails, press Run install.'
  return [
    ['tool', REPORT_TOOL],
    ['error', install.error ?? problem ?? ''],
    ['server', SERVER],
    ['fix', fix],
  ].filter((row): row is [string, string] => Boolean(row[1]))
}

export function installLineOf({ state }: InstallJson): string {
  if (state === 'running') return 'Installing.'
  if (state === 'installed') return 'Installed. Open a new session to pick it up.'
  return state === 'failed' ? 'Install failed. See the error in Details.' : ''
}
