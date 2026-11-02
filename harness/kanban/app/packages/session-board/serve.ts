import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { CddConnectionNode, locateCdd } from '@src/cdd/cdd-connection-node'
import { ChatsNode } from '@src/kanban/chat/chat-node'

import { createApp } from './app'

const DEFAULT_PORT = 8778
const HOST = '127.0.0.1'

const here = dirname(fileURLToPath(import.meta.url))
const appRoot = resolve(here, '..', '..')
const sourceRoot = resolve(appRoot, '..', '..', '..')
const port = Number(process.env.BOARD_PORT ?? DEFAULT_PORT)
const cdd = new CddConnectionNode(locateCdd(sourceRoot, process.env))
const app = createApp(cdd, new ChatsNode(), port, join(appRoot, 'dist'))

const server = app.listen(port, HOST, () => {
  console.log(`Session board at http://${HOST}:${port}`)
})

for (const signal of ['SIGINT', 'SIGTERM'] as const) {
  process.on(signal, () => {
    server.close()
    void cdd.close().finally(() => process.exit(0))
  })
}
