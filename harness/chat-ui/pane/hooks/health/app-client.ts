import { atom, read, update } from 'claude-code'
import type { EngineInterface } from 'claude-code'

import type { AppData, AppServerData } from '@cdd/harness/diagnostics/app'

import type { AppOpeningJson } from '../../types'
import { after } from '../board-chat/board'
import { reasonOf } from '../shared/failure'
import { refreshHealth, SERVER } from './server-health-client'

// A press on an app in the status row: Python's App.open installs it while it is not installed and answers it with its
// url and its server, or refuses saying what failed and how to fix it. While it is not running, this chat starts its
// server, which lives as long as the chat's mod, as /board's did: the chat's end stops it, and an app the chat did not
// start keeps running. Atom appOpening, declared in pane/types/index.d.ts.
const OPEN_TOOL = 'app.open'
const STARTED_WITHIN_MILLISECONDS = 20_000
const STARTED_CHECK_MILLISECONDS = 500
// The Browser pane beside the chat in the Claude desktop app, the only place an app opens.
const SIDE_PANEL_SERVER = 'Claude_Browser'
const SIDE_PANEL_TOOL = 'preview_start'
// The pane's tabs, each with its origin, and the call that brings one to the front.
const TABS_TOOL = 'tabs_context'
const SELECT_TAB_TOOL = 'tabs_select'
const NAVIGATE_TOOL = 'navigate'
type PaneTabs = { browserOpen: boolean; tabs: { tabId: string; origin: string; isActive: boolean }[] }
// The desktop app's view tools: show_pane brings the Browser pane, its "preview", beside the conversation.
const VIEW_SERVER = 'ccd_view'
const SHOW_PANE_TOOL = 'show_pane'
const PREVIEW_PANE = 'preview'

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
  }
  await refreshHealth($)
}

// The app opens only in Claude's Browser pane, never in the person's own browser; a refusal says the pane's reason. A
// tab already on the app's origin is brought to the front rather than opening another.
async function openInSidePanel($: EngineInterface, url: string): Promise<void> {
  let panelWhy: string
  try {
    const open = await tabOn($, new URL(url).origin)
    // The open tab goes to url too, so a page opened for another session's folder loads this one's.
    const shown = open
      ? await $.mcp.call(SIDE_PANEL_SERVER, NAVIGATE_TOOL, { url, tabId: open }).then(() => $.mcp.call(SIDE_PANEL_SERVER, SELECT_TAB_TOOL, { tabId: open }))
      : await $.mcp.call(SIDE_PANEL_SERVER, SIDE_PANEL_TOOL, { url })
    if (!shown.isError) {
      // Neither call shows a hidden pane, so the pane is shown after it.
      await $.mcp.call(VIEW_SERVER, SHOW_PANE_TOOL, { pane: PREVIEW_PANE }).catch(() => null)
      return
    }
    panelWhy = shown.content[0]?.text ?? 'it answered with an error'
  } catch (failure) {
    panelWhy = reasonOf(failure)
  }
  throw new AppNotOpened(`${url} is running, but Claude's Browser pane did not open it: ${panelWhy}`)
}

// The pane's tab on origin, the active one first; none while the pane is closed or the answer cannot be read. The
// answer is the tabs as JSON followed by a sentence about the pane, so the JSON is read up to its last brace.
async function tabOn($: EngineInterface, origin: string): Promise<string | null> {
  const answer = await $.mcp.call(SIDE_PANEL_SERVER, TABS_TOOL, {}).catch(() => null)
  const text = answer && !answer.isError ? answer.content[0]?.text ?? '' : ''
  try {
    const { browserOpen, tabs } = JSON.parse(text.slice(text.indexOf('{'), text.lastIndexOf('}') + 1)) as PaneTabs
    if (!browserOpen) return null
    const onOrigin = tabs.filter(tab => tab.origin === origin)
    return (onOrigin.find(tab => tab.isActive) ?? onOrigin[0])?.tabId ?? null
  } catch {
    return null
  }
}
