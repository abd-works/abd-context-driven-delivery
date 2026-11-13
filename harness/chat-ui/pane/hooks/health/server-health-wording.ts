import type { ServerHealthData } from '@cdd/harness/diagnostics/server-health'

import type { InstallJson, ServerHealthJson } from '../../types'
import { BRAND } from '../shared/brand'
import type { AppName } from './open-app-client'
import { RECONNECT_TRIES, REPORT_TOOL, SERVER, ServerHealthClient } from './server-health-client'

// The server health panel's words: what each part reads, the headline, the details and the install line. The panel's
// view paints them; ServerHealthClient carries the report they are read from.

// app names the app a press on the part opens, starting it first when it is not running; null for a part with no app.
export type Part = { icon: string; label: string; value: string; isUp: boolean; app: AppName | null }

// A part reads green while it runs and grey while it does not.
export function colourOf(part: Part): string {
  return part.isUp ? BRAND.success : BRAND.muted
}

const runningOn = (port: number | null): string => (port === null ? 'not running' : `running :${port}`)

export function partsOf({ report, toolCount }: ServerHealthJson): Part[] {
  const { kanbanAppPort, graphAppPort, isHookServerRunning: isHookRunning } = new ServerHealthClient(report as ServerHealthData | null)
  return [
    { icon: '⬢', label: 'MCP host', value: 'running', isUp: true, app: null },
    { icon: '⚒', label: 'Tools', value: `${toolCount} loaded`, isUp: true, app: null },
    { icon: '▦', label: 'Kanban app', value: runningOn(kanbanAppPort), isUp: kanbanAppPort !== null, app: 'Kanban app' },
    { icon: '◈', label: 'Graph app', value: runningOn(graphAppPort), isUp: graphAppPort !== null, app: 'Graph app' },
    { icon: '↪', label: 'Hook server', value: isHookRunning ? 'running' : 'not installed', isUp: isHookRunning, app: null },
  ]
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
