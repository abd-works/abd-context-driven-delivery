import express, { type Express, type NextFunction, type Request, type Response } from 'express'
import { join } from 'node:path'

import type { ProjectConnections } from '@cdd/cdd-connection'
import { CddRequestError, type CddRoute } from '@cdd/cdd-shared'
import { fidelityProgressRoutes } from '@cdd/space/kanban/fidelity-progress'
import { fileCommentsRoutes } from '@cdd/space/session/file-comments'
import { sessionRoutes } from '@cdd/space/session/session'

import { DrawioViewer } from './drawio-viewer'
import { API_ROOT, DRAWIO_PATH, FILES_HEADER } from './files/files-paths'

const CHANGING_METHODS = ['POST', 'PUT', 'PATCH', 'DELETE']
const BAD_REQUEST = 400
const FORBIDDEN = 403
const FAILED = 500

// The Files app reads a session's files, a fidelity's files, and the comments on them; it never reads the board.
export const filesRoutes: CddRoute[] = [...sessionRoutes, ...fileCommentsRoutes, ...fidelityProgressRoutes]

const textOf = (failure: unknown): string => (failure instanceof Error ? failure.message : String(failure))

// This server can put a person's comments into a live chat, so only this machine's own page may reach it. The Host check
// stops a site pointing its own domain name at 127.0.0.1; the header forces a preflight, which this server never answers.
function onlyThisMachine(port: number) {
  return (request: Request, response: Response, next: NextFunction): void => {
    const isLocalHost = [`127.0.0.1:${port}`, `localhost:${port}`].includes(request.headers.host ?? '')
    const isForeignPost = CHANGING_METHODS.includes(request.method) && !request.headers[FILES_HEADER]
    if (isLocalHost && !isForeignPost) return next()
    response.status(FORBIDDEN).json({ error: 'Refused: this server answers only its own page on this machine.' })
  }
}

async function answer(projects: ProjectConnections, route: CddRoute, request: Request, response: Response): Promise<void> {
  try {
    response.json((await route.run(projects.of(request), request)) ?? null)
  } catch (failure) {
    response.status(failure instanceof CddRequestError ? BAD_REQUEST : FAILED).json({ error: textOf(failure) })
  }
}

export function createFilesApp(projects: ProjectConnections, port: number, staticRoot: string, drawio: DrawioViewer): Express {
  const app = express()
  app.use(onlyThisMachine(port))
  app.use(express.json())
  for (const route of filesRoutes) app.post(`${API_ROOT}${route.path}`, (request, response) => void answer(projects, route, request, response))
  app.post(`${API_ROOT}${DRAWIO_PATH}`, async (request, response) => {
    try {
      response.json({ url: await drawio.urlOf(String(request.body?.path ?? '')) })
    } catch (failure) {
      response.status(FAILED).json({ error: textOf(failure) })
    }
  })
  app.use(express.static(staticRoot))
  app.get('*', (_request, response) => response.sendFile(join(staticRoot, 'index.html')))
  return app
}
