// Spec support for harness/files_app/files_app_e2e_spec.py: the Files server as serve.ts starts it, serving a page the
// spec built into a folder of its own, on a port of its own, so an e2e run never rebuilds or serves the app's own dist
// and never takes the port a person's Files app answers on. It talks to the cdd server its CDD_HOME names, the spec's
// throwaway one.
//   npx tsx spec-files-server.ts <built page folder> <port> <project>
import { CddConnection, ProjectConnections } from '@cdd/cdd-connection'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { DrawioViewer } from './drawio-viewer'
import { createFilesApp } from './files-server'

const HOST = '127.0.0.1'
const repository = resolve(dirname(fileURLToPath(import.meta.url)), '..', '..', '..')
const [built, portText, project] = process.argv.slice(2)
if (!built || !portText || !project) throw new Error('usage: npx tsx spec-files-server.ts <built page folder> <port> <project>')
const port = Number(portText)
const projects = new ProjectConnections(new CddConnection(project))
const server = createFilesApp(projects, port, resolve(built), new DrawioViewer(repository)).listen(port, HOST, () => {
  console.log(`Files at http://${HOST}:${port}`)
})

for (const signal of ['SIGINT', 'SIGTERM'] as const) {
  process.on(signal, () => {
    server.close()
    void projects.close().finally(() => process.exit(0))
  })
}
