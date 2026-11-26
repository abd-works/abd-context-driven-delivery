import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { CddConnection, ProjectConnections } from '@cdd/cdd-connection'

import { serveLaneHome, servePort } from '@graph-app/serve-port'

import { DrawioViewer } from './drawio-viewer'
import { createFilesApp } from './files-server'
// The app's port, written once for this server and for the Python that reports it to a chat.
import ports from './ports.json'

const HOST = '127.0.0.1'

const here = dirname(fileURLToPath(import.meta.url))
// harness/files_app/app sits three folders below the repository's root.
const repository = resolve(here, '..', '..', '..')
serveLaneHome(process.argv)
const port = servePort(process.argv, Number(process.env.FILES_PORT ?? ports.files[0]))
// A call that names no project is about FILES_PROJECT, which defaults to the checkout cdd was installed from.
const projects = new ProjectConnections(new CddConnection(process.env.FILES_PROJECT))
const app = createFilesApp(projects, port, join(here, 'dist'), new DrawioViewer(repository))

const server = app.listen(port, HOST, () => {
  console.log(`Files at http://${HOST}:${port}`)
})

for (const signal of ['SIGINT', 'SIGTERM'] as const) {
  process.on(signal, () => {
    server.close()
    projects
      .close()
      .catch(failure => console.error(`The Files server did not close its cdd connections: ${failure instanceof Error ? failure.stack : String(failure)}`))
      .finally(() => process.exit(0))
  })
}
