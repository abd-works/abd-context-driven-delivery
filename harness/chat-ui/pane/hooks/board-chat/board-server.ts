import type { EngineInterface } from 'claude-code'

import { reasonOf } from '../failure'
import { refreshHealth } from '../health/server-health-client'
import { after, boardUrl } from './board'

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

async function boardAppFolder($: EngineInterface): Promise<string> {
  const { exitCode, stdout } = await $.process.run(['git', 'rev-parse', '--show-toplevel'])
  return exitCode === 0 ? `${stdout.trim()}/${BOARD_APP}` : ''
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

// Starts the board when nothing answers on its port, so /board always ends with a board to open. cdd's server health
// gives the board's address, so the chat names no port of the board's.
export async function openedBoard($: EngineInterface): Promise<string> {
  await refreshHealth($)
  const url = await boardUrl($)
  if (!url) return NO_ADDRESS
  if (await isBoardUp($, url)) return `The board is at ${url}.`
  const folder = await boardAppFolder($)
  if (!folder || !(await $.fs.exists(`${folder}/node_modules`)) || !(await $.fs.exists(`${folder}/dist`))) return `The board is not running and is not installed here. ${START_BY_HAND}`
  startServer($, folder)
  return (await cameUp($, url)) ? `Started the board at ${url}. It stops when this chat ends.` : `The board did not start within ${STARTED_WITHIN_MILLISECONDS / 1000} s. ${START_BY_HAND}`
}
