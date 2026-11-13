import { atom, read, update } from 'claude-code'
import type { EngineInterface } from 'claude-code'

import type { AppData, AppServerData } from '@cdd/harness/diagnostics/app'

import type { AppOpeningJson } from '../../types'
import { after } from '../board-chat/board'
import { openInBrowser } from '../shared/browser'
import { reasonOf } from '../shared/failure'
import { refreshHealth, SERVER } from './server-health-client'

// A press on an app in the status row: Python's App.open installs it while it is not installed and answers it with its
// url and its server, or refuses saying what failed and how to fix it. While it is not running, this chat starts its
// server, which lives as long as the chat's mod, as /board's did: the chat's end stops it, and an app the chat did not
// start keeps running. Atom appOpening, declared in pane/types/index.d.ts.
const OPEN_TOOL = 'app.open'
const STARTED_WITHIN_MILLISECONDS = 20_000
const STARTED_CHECK_MILLISECONDS = 500
// The Browser pane beside the chat in the Claude desktop app; where a session has none, the app opens in the browser.
const SIDE_PANEL_SERVER = 'Claude_Browser'
const SIDE_PANEL_TOOL = 'preview_start'

const appOpening = atom({ plugin: 'cdd-board', key: 'appOpening' } as const, { label: '', state: 'idle', error: null } as AppOpeningJson)

export class AppNotOpened extends Error {}

export function currentAppOpening($: EngineInterface) {
  return read($, appOpening)
}

// The app labelled label, ready: installed, running, and answering at its url; its server started by this chat when
// nothing answered.
export async function openApp($: EngineInterface, label: string): Promise<AppData> {
  const app = await installedApp($, label)
  if (app.status === 'running') return app
  startServer($, app.server)
  if (await cameUp($, app.url)) return app
  const { port } = new URL(app.url)
  throw new AppNotOpened(`The ${label} did not start: nothing answered on port ${port}. Run ${app.server.command.join(' ')} in ${app.server.folder}.`)
}

async function installedApp($: EngineInterface, label: string): Promise<AppData> {
  const result = await $.mcp.call(SERVER, OPEN_TOOL, { app: label })
  const text = result.content[0]?.text ?? ''
  if (result.isError) throw new AppNotOpened(text || `${OPEN_TOOL} failed for ${label}`)
  return JSON.parse(text) as AppData
}

// The server lives as long as this chat's mod: leaving the loop, or the module unloading, ends it.
function startServer($: EngineInterface, server: AppServerData): void {
  void (async () => {
    const running = $.process.spawn({ argv: server.command, cwd: server.folder })
    for await (const { text } of running) $.ui.log(text, { to: 'debug' })
  })().catch(error => $.ui.log(`${server.command.join(' ')} stopped: ${reasonOf(error)}`, { to: 'debug' }))
}

function answers($: EngineInterface, url: string): Promise<boolean> {
  return $.http
    .fetch(url)
    .then(() => true)
    .catch(() => false)
}

async function cameUp($: EngineInterface, url: string): Promise<boolean> {
  for (let waited = 0; waited < STARTED_WITHIN_MILLISECONDS; waited += STARTED_CHECK_MILLISECONDS) {
    if (await answers($, url)) return true
    await after($, STARTED_CHECK_MILLISECONDS, '')
  }
  return false
}

// A press on an app in the status row opens it in the side panel, readied first; a refusal stays in the server health
// panel, and the side panel stays closed.
export async function openAppBesideChat($: EngineInterface, label: string, pageUrlOf: (url: string) => Promise<string>): Promise<void> {
  await update($, appOpening, () => ({ label, state: 'opening', error: null }))
  try {
    const app = await openApp($, label)
    await openInSidePanel($, await pageUrlOf(app.url))
    await update($, appOpening, () => ({ label, state: 'idle', error: null }))
  } catch (failure) {
    await update($, appOpening, () => ({ label, state: 'failed', error: reasonOf(failure) }))
  }
  await refreshHealth($)
}

async function openInSidePanel($: EngineInterface, url: string): Promise<void> {
  const shown = await $.mcp.call(SIDE_PANEL_SERVER, SIDE_PANEL_TOOL, { url }).catch(() => null)
  if (shown && !shown.isError) return
  if (!(await openInBrowser($, url))) throw new AppNotOpened(`${url} did not open: no side panel or browser took it`)
}
