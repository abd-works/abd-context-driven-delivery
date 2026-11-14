import type { AppData } from '@cdd/harness/diagnostics/app'
import type { ServerHealthData } from '@cdd/harness/diagnostics/server-health'

import type { AppOpeningJson, InstallJson, ServerHealthJson } from '../../types'
import { BRAND } from '../shared/brand'
import { RECONNECT_TRIES, REPORT_TOOL, SERVER, ServerHealthClient } from './server-health-client'

// The server health panel's words: what each part reads, the headline, the details and the install line. The panel's
// view paints them; ServerHealthClient carries the report they are read from.

// app: the label of the app a press on the part opens; none for a part that is not an app.
export type Part = { icon: string; label: string; value: string; isUp: boolean; app?: string }

// A part reads green while it runs and grey while it does not.
export function colourOf(part: Part): string {
  return part.isUp ? BRAND.success : BRAND.muted
}

// Each app's mark in the status row; an app registered later shows the plain one.
const APP_ICONS: Record<string, string> = { Kanban: '▦', Files: '▤', Graph: '◈', 'Story UI': '✎' }
const APP_ICON = '▣'
const RUNNING: AppData['status'] = 'running'

// An app reads its status, and the port it answers on while it runs: running :8778, not running, not installed.
function appPartOf(app: AppData): Part {
  const isUp = app.status === RUNNING
  return { icon: APP_ICONS[app.label] ?? APP_ICON, label: app.label, value: isUp ? `${app.status} :${app.port}` : app.status, isUp, app: app.label }
}

export function partsOf({ report, toolCount }: ServerHealthJson): Part[] {
  const { apps, isHookServerRunning: isHookRunning } = new ServerHealthClient(report as ServerHealthData | null)
  return [
    { icon: '⬢', label: 'MCP host', value: 'running', isUp: true },
    { icon: '⚒', label: 'Tools', value: `${toolCount} loaded`, isUp: true },
    ...apps.map(appPartOf),
    { icon: '↪', label: 'Hook server', value: isHookRunning ? 'running' : 'not installed', isUp: isHookRunning },
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
