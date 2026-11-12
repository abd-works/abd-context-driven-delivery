import { spawn } from 'node:child_process'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { CddConnection } from '@cdd/cdd-connection'
import { BoardUpdate } from '@src/session-board/board-update'
import { ProjectConnections } from '@src/session-board/project-connections'

import { createApp } from './app'
// The board's port, written once for this server and for the Python that reports it to a chat.
import ports from './ports.json'

const HOST = '127.0.0.1'
const SERVE_ARGUMENTS = ['--import', 'tsx', 'packages/session-board/serve.ts']

const here = dirname(fileURLToPath(import.meta.url))
const appRoot = resolve(here, '..', '..')
const port = Number(process.env.BOARD_PORT ?? ports.board[0])
// A call that names no project is about BOARD_PROJECT, which defaults to the checkout cdd was installed from.
const projects = new ProjectConnections(new CddConnection(process.env.BOARD_PROJECT))
const app = createApp(projects, port, join(appRoot, 'dist'), new BoardUpdate(appRoot, () => restartOnNewCode()))

const server = app.listen(port, HOST, () => {
  console.log(`Session board at http://${HOST}:${port}`)
})

// A running server keeps the routes it loaded, so after an update a new one starts on the new code once this one has let
// go of the port. The open page keeps polling and reconnects to it.
function restartOnNewCode(): void {
  server.closeAllConnections()
  server.close(() => {
    spawn(process.execPath, SERVE_ARGUMENTS, { cwd: appRoot, detached: true, stdio: 'ignore', windowsHide: true }).unref()
    void projects.close().finally(() => process.exit(0))
  })
}

for (const signal of ['SIGINT', 'SIGTERM'] as const) {
  process.on(signal, () => {
    server.close()
    void projects.close().finally(() => process.exit(0))
  })
}
