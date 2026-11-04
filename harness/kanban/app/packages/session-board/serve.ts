import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { CddConnection } from '@cdd/cdd-connection'

import { createApp } from './app'

const DEFAULT_PORT = 8778
const HOST = '127.0.0.1'

const here = dirname(fileURLToPath(import.meta.url))
const appRoot = resolve(here, '..', '..')
const port = Number(process.env.BOARD_PORT ?? DEFAULT_PORT)
// The board's project defaults to the checkout cdd was installed from.
const cdd = new CddConnection(process.env.BOARD_PROJECT)
const app = createApp(cdd, port, join(appRoot, 'dist'))

const server = app.listen(port, HOST, () => {
  console.log(`Session board at http://${HOST}:${port}`)
})

for (const signal of ['SIGINT', 'SIGTERM'] as const) {
  process.on(signal, () => {
    server.close()
    void cdd.close().finally(() => process.exit(0))
  })
}
