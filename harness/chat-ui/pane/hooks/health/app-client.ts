import { atom, read, update } from 'claude-code'
import type { EngineInterface } from 'claude-code'

import type { AppData } from '@cdd/harness/diagnostics/app'

import type { AppOpeningJson } from '../../types'
import { openInBrowser } from '../shared/browser'
import { reasonOf } from '../shared/failure'
import { refreshHealth, SERVER } from './server-health-client'

// A press on an app in the status row: Python's App.open installs it while it is not installed, launches it while it is
// not running, and answers it with its url, or refuses saying which step failed and how to fix it. The status row only
// shows what that answer says. Atom appOpening, declared in pane/types/index.d.ts.
const OPEN_TOOL = 'app.open'
// The Browser pane beside the chat in the Claude desktop app; where a session has none, the app opens in the browser.
const SIDE_PANEL_SERVER = 'Claude_Browser'
const SIDE_PANEL_TOOL = 'preview_start'

const appOpening = atom({ plugin: 'cdd-board', key: 'appOpening' } as const, { label: '', state: 'idle', error: null } as AppOpeningJson)

export class AppNotOpened extends Error {}

export function currentAppOpening($: EngineInterface) {
  return read($, appOpening)
}

// The app labelled label, ready: installed, running, and answering at its url.
export async function openApp($: EngineInterface, label: string): Promise<AppData> {
  const result = await $.mcp.call(SERVER, OPEN_TOOL, { app: label })
  const text = result.content[0]?.text ?? ''
  if (result.isError) throw new AppNotOpened(text || `${OPEN_TOOL} failed for ${label}`)
  return JSON.parse(text) as AppData
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
