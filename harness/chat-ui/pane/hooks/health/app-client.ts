import { atom, read, update } from 'claude-code'
import type { EngineInterface } from 'claude-code'

import type { AppData, AppServerData } from '@cdd/harness/diagnostics/app'

import type { AppOpeningJson } from '../../types'
import { after } from '../board-chat/board'
import { openInBrowserPane } from '../shared/browser-pane'
import { reasonOf, showFailure, shownAsFailure } from '../error-display/failure-client'
import { refreshHealth, SERVER } from './server-health-client'

// A press on an app in the status row: Python's App.open installs it while it is not installed and answers it with its
// url and its server, or refuses saying what failed and how to fix it. While it is not running, this chat starts its
// server, which lives as long as the chat's mod, as /board's did: the chat's end stops it, and an app the chat did not
// start keeps running. Atom appOpening, declared in pane/types/index.d.ts.
const OPEN_TOOL = 'app.open'
const STARTED_WITHIN_MILLISECONDS = 20_000
const STARTED_CHECK_MILLISECONDS = 500
const appOpening = atom({ plugin: 'cdd-board', key: 'appOpening' } as const, { label: '', state: 'idle', error: null, url: null } as AppOpeningJson)

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

// An install runs npm and can outlast the seconds the server waits on a call: it then answers that the call is still
// running, and an identical call waits for that same run. Each call waits about ten seconds, so this allows npm fifteen
// minutes, the install's own limit, before saying it did not finish.
const STILL_RUNNING = `${OPEN_TOOL} is still running`
const STILL_RUNNING_CALLS = 90

async function installedApp($: EngineInterface, label: string): Promise<AppData> {
  for (let call = 0; call < STILL_RUNNING_CALLS; call += 1) {
    const result = await $.mcp.call(SERVER, OPEN_TOOL, { app: label })
    const text = result.content[0]?.text ?? ''
    if (result.isError) throw new AppNotOpened(text || `${OPEN_TOOL} failed for ${label}`)
    if (!text.startsWith(STILL_RUNNING)) return JSON.parse(text) as AppData
  }
  throw new AppNotOpened(`The ${label} is still installing after fifteen minutes; press it again to wait for that install.`)
}

// The server lives as long as this chat's mod: leaving the loop, or the module unloading, ends it.
function startServer($: EngineInterface, server: AppServerData): void {
  void (async () => {
    const running = $.process.spawn({ argv: server.command, cwd: server.folder })
    for await (const { text } of running) $.ui.log(text, { to: 'debug' })
  })().catch(shownAsFailure($, `The app server stopped: ${server.command.join(' ')}`, `Running the app server in ${server.folder}`))
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
// The app's url stays in the panel as a link either way, so a page neither the side panel nor the browser took is one
// click away.
export async function openAppBesideChat($: EngineInterface, label: string, pageUrlOf: (url: string) => Promise<string>): Promise<void> {
  await update($, appOpening, () => ({ label, state: 'opening', error: null, url: null }))
  let url: string | null = null
  try {
    url = await pageUrlOf((await openApp($, label)).url)
    await openInSidePanel($, url)
    await update($, appOpening, () => ({ label, state: 'idle', error: null, url }))
  } catch (failure) {
    await update($, appOpening, () => ({ label, state: 'failed', error: reasonOf(failure), url }))
    await showFailure($, `The ${label} did not open`, `Pressing the ${label} on the health panel, calling ${OPEN_TOOL}${url ? ` and opening ${url} in Claude's Browser pane` : ''}`, failure)
  }
  await refreshHealth($)
}

// The app opens only in Claude's Browser pane, never in the person's own browser; a refusal says the pane's reason.
async function openInSidePanel($: EngineInterface, url: string): Promise<void> {
  const why = await openInBrowserPane($, url)
  if (why) throw new AppNotOpened(`${url} is running, but Claude's Browser pane did not open it: ${why}`)
}
