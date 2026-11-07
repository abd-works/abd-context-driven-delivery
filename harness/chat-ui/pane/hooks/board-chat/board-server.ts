import type { EngineInterface } from 'claude-code'

import { reasonOf } from '../failure'
import { after, BOARD_URL } from './board'

// /board opens the session board, starting its server from this repository when nothing answers on its port.
const BOARD_APP = 'space/kanban/app'
const START_BY_HAND = `Start it with: npm install, npm run build, then npm start, in ${BOARD_APP}.`
const STARTED_WITHIN_MILLISECONDS = 20_000
const STARTED_CHECK_MILLISECONDS = 500

function isBoardUp($: EngineInterface): Promise<boolean> {
  return $.http
    .fetch(`${BOARD_URL}/api/build`)
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

async function cameUp($: EngineInterface): Promise<boolean> {
  for (let waited = 0; waited < STARTED_WITHIN_MILLISECONDS; waited += STARTED_CHECK_MILLISECONDS) {
    if (await isBoardUp($)) return true
    await after($, STARTED_CHECK_MILLISECONDS, '')
  }
  return false
}

// Starts the board when nothing answers on its port, so /board always ends with a board to open.
export async function openedBoard($: EngineInterface): Promise<string> {
  if (await isBoardUp($)) return `The board is at ${BOARD_URL}.`
  const folder = await boardAppFolder($)
  if (!folder || !(await $.fs.exists(`${folder}/node_modules`)) || !(await $.fs.exists(`${folder}/dist`))) return `The board is not running and is not installed here. ${START_BY_HAND}`
  startServer($, folder)
  return (await cameUp($)) ? `Started the board at ${BOARD_URL}. It stops when this chat ends.` : `The board did not start within ${STARTED_WITHIN_MILLISECONDS / 1000} s. ${START_BY_HAND}`
}
