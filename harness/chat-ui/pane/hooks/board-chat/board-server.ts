import type { EngineInterface } from 'claude-code'

import { reasonOf } from '../shared/failure'
import { refreshHealth } from '../health/server-health-client'
import { after, boardPageUrl, boardUrl, repositoryFolder } from './board'

// /board opens the session board, starting its server from this repository when nothing answers on its port.
const BOARD_APP = 'space/kanban/app'
const START_BY_HAND = `Start it with: npm install, npm run build, then npm start, in ${BOARD_APP}.`
const NO_ADDRESS = 'cdd has not said where the board answers yet: reconnect cdd from the chat bar, then run /board again.'
const STARTED_WITHIN_MILLISECONDS = 20_000
const STARTED_CHECK_MILLISECONDS = 500

function isBoardUp($: EngineInterface, url: string): Promise<boolean> {
  return $.http
    .fetch(`${url}/api/build`)
    .then(answer => answer.ok)
    .catch(() => false)
}

// The board app in the repository's own folder, so a chat in a ticket's worktree, which holds no build, starts it too.
async function boardAppFolder($: EngineInterface): Promise<string> {
  const repository = await repositoryFolder($)
  return repository ? `${repository}/${BOARD_APP}` : ''
}

// The board lives as long as this chat's mod: leaving the loop, or the module unloading, ends the server.
function startServer($: EngineInterface, folder: string): void {
  void (async () => {
    const server = $.process.spawn({ argv: ['node', '--import', 'tsx', 'packages/session-board/serve.ts'], cwd: folder })
    for await (const { text } of server) $.ui.log(text, { to: 'debug' })
  })().catch(error => $.ui.log(`The session board stopped: ${reasonOf(error)}`, { to: 'debug' }))
}

async function cameUp($: EngineInterface, url: string): Promise<boolean> {
  for (let waited = 0; waited < STARTED_WITHIN_MILLISECONDS; waited += STARTED_CHECK_MILLISECONDS) {
    if (await isBoardUp($, url)) return true
    await after($, STARTED_CHECK_MILLISECONDS, '')
  }
  return false
}

// The board's address once it answers, or why there is none: cdd has not said where it answers, it is not installed
// in the repository's own folder, or it did not start. wasStarted says this call started it.
export type BoardStart = { url: string; wasStarted: boolean; problem: string }

export async function startedBoard($: EngineInterface): Promise<BoardStart> {
  await refreshHealth($)
  const url = await boardUrl($)
  if (!url) return { url: '', wasStarted: false, problem: NO_ADDRESS }
  if (await isBoardUp($, url)) return { url, wasStarted: false, problem: '' }
  const folder = await boardAppFolder($)
  if (!folder || !(await $.fs.exists(`${folder}/node_modules`)) || !(await $.fs.exists(`${folder}/dist`))) return { url: '', wasStarted: false, problem: `The board is not running and is not installed here. ${START_BY_HAND}` }
  startServer($, folder)
  if (await cameUp($, url)) return { url, wasStarted: true, problem: '' }
  return { url: '', wasStarted: false, problem: `The board did not start within ${STARTED_WITHIN_MILLISECONDS / 1000} s. ${START_BY_HAND}` }
}

// The board's address once it answers, starting it from this repository when nothing answers on its port; empty when
// cdd has not said where it answers or it does not start.
export async function runningBoardUrl($: EngineInterface): Promise<string> {
  return (await startedBoard($)).url
}

// Opens a page in the person's browser with the system's own opener, since mods have no call that opens a link.
export async function openInBrowser($: EngineInterface, url: string): Promise<boolean> {
  const openers = [['rundll32', 'url.dll,FileProtocolHandler', url], ['open', url], ['xdg-open', url]]
  for (const argv of openers) {
    const opened = await $.process.run(argv).catch(() => null)
    if (opened?.exitCode === 0) return true
  }
  return false
}

// The Claude desktop app's own browser pane, as /mcp lists it, and its call that opens a tab at a URL.
const BROWSER_PANE = 'Claude_Browser'
const OPEN_TAB = 'preview_start'

// Opens a page in a tab of the Claude desktop app's browser pane, beside the chat; where the chat has no pane, such as
// in a terminal, or the pane refuses, in the person's browser instead.
export async function openInBrowserPane($: EngineInterface, url: string): Promise<boolean> {
  const opened = await $.mcp.call(BROWSER_PANE, OPEN_TAB, { url }).catch(() => null)
  if (opened && !opened.isError) return true
  return openInBrowser($, url)
}

// Starts the board when nothing answers on its port, so /board always ends with a board to open. cdd's server health
// gives the board's address, so the chat names no port of the board's. The link names this chat's repository, so the
// page shows this chat's tickets whichever repository the server was started from.
export async function openedBoard($: EngineInterface): Promise<string> {
  const { url, wasStarted, problem } = await startedBoard($)
  if (!url) return problem
  const page = await boardPageUrl($, url)
  return wasStarted ? `Started the board at ${page}. It stops when this chat ends.` : `The board is at ${page}.`
}
