// Spec support for the Files app story tests in a real browser (story_tests/review-generated-work-in-file-viewer/files_app_browser.py): the Files server as serve.ts starts it, serving a page the
// spec built into a folder of its own, on a port of its own, so an e2e run never rebuilds or serves the app's own dist
// and never takes the port a person's Files app answers on. It talks to the cdd server its CDD_HOME names, the spec's
// throwaway one. A draw.io port names the spec's own draw.io viewer, so a diagram the page opens never reaches the
// person's viewer on 8791.
//   npx tsx spec-files-server.ts <built page folder> <port> <project> [draw.io port]
import { CddConnection, ProjectConnections } from '@cdd/cdd-connection'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { DrawioViewer } from './drawio-viewer'
import { DRAWIO_PORT } from './files/files-paths'
import { createFilesApp } from './files-server'

const HOST = '127.0.0.1'
const repository = resolve(dirname(fileURLToPath(import.meta.url)), '..', '..', '..')
const [built, portText, project, drawioPortText] = process.argv.slice(2)
if (!built || !portText || !project) throw new Error('usage: npx tsx spec-files-server.ts <built page folder> <port> <project> [draw.io port]')
const port = Number(portText)
const projects = new ProjectConnections(new CddConnection(project))
const drawio = new DrawioViewer(repository, process.env.PYTHON || 'python', drawioPortText ? Number(drawioPortText) : DRAWIO_PORT)
const server = createFilesApp(projects, port, resolve(built), drawio).listen(port, HOST, () => {
  console.log(`Files at http://${HOST}:${port}`)
})

for (const signal of ['SIGINT', 'SIGTERM'] as const) {
  process.on(signal, () => {
    server.close()
    void projects.close().finally(() => process.exit(0))
  })
}
