import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { CddConnection, ProjectConnections } from '@cdd/cdd-connection'

import { createApp } from './app'
// The board's port, written once for this server and for the Python that reports it to a chat.
import ports from './ports.json'

const HOST = '127.0.0.1'

const here = dirname(fileURLToPath(import.meta.url))
const appRoot = resolve(here, '..', '..')
const port = Number(process.env.BOARD_PORT ?? ports.board[0])
// A call that names no project is about BOARD_PROJECT, which defaults to the checkout cdd was installed from.
const projects = new ProjectConnections(new CddConnection(process.env.BOARD_PROJECT))
const app = createApp(projects, port, join(appRoot, 'dist'))

const server = app.listen(port, HOST, () => {
  console.log(`Session board at http://${HOST}:${port}`)
})

for (const signal of ['SIGINT', 'SIGTERM'] as const) {
  process.on(signal, () => {
    server.close()
    void projects.close().finally(() => process.exit(0))
  })
}
