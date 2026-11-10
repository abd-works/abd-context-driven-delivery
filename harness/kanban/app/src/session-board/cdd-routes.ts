import { Router } from 'express'

import type { CddConnection } from '@cdd/cdd-connection'
import type { CddRoute } from '@cdd/cdd-shared'

import { answer } from './answer'

// Mounts the routes the installer generates: each is a POST that runs one tool through its server adapter.
export function cddRoutes(cdd: CddConnection, routes: CddRoute[]): Router {
  const router = Router()
  for (const route of routes) router.post(route.path, answer(req => route.run(cdd, req)))
  return router
}
