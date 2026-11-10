// E2E helper: serve the Session Board from space/kanban/app against a sandbox project, with the Update button disabled.
// Run from space/kanban/app so tsconfig paths resolve:  npx tsx <this file>
// Env: BOARD_PORT (default 8790), BOARD_PROJECT (sandbox repo), BOARD_DIST (built page).
import { CddConnection } from '@cdd/cdd-connection'

import { createApp } from '../../../space/kanban/app/packages/session-board/app'

const port = Number(process.env.BOARD_PORT ?? 8790)
const cdd = new CddConnection(process.env.BOARD_PROJECT)
const noUpdate = {
  update: async () => {
    throw new Error('Update is disabled in the e2e sandbox')
  },
  restart: () => undefined,
} as never
const app = createApp(cdd, port, process.env.BOARD_DIST ?? '', noUpdate)
const server = app.listen(port, '127.0.0.1', () => console.log(`E2E session board at http://127.0.0.1:${port} for ${process.env.BOARD_PROJECT}`))
for (const signal of ['SIGINT', 'SIGTERM'] as const) process.on(signal, () => { server.close(); void cdd.close().finally(() => process.exit(0)) })
