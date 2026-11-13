import { Router } from 'express'

import type { ProjectConnections } from '@cdd/cdd-connection'
import type { CddRoute } from '@cdd/cdd-shared'

import { answer } from './answer'

// Mounts the routes the installer generates: each is a POST that runs one tool through its server adapter, on the cdd
// connection of the repository the request names.
export function cddRoutes(projects: ProjectConnections, routes: CddRoute[]): Router {
  const router = Router()
  for (const route of routes) router.post(route.path, answer(req => route.run(projects.of(req), req)))
  return router
}
