/**
 * Mounts the routes the installer generates. Each is a POST that runs one tool through its server adapter, so the
 * application writes no route, path, or parsing for a CDD object. One per application.
 *
 * ```
 * file: src/cdd/cdd-routes.ts
 * ```
 */
import { Router } from 'express'

import type { CddConnection } from '@cdd/cdd-connection'
import type { CddRoute } from '@cdd/cdd-shared'

export function cddRoutes(cdd: CddConnection, routes: CddRoute[]): Router {
  const router = Router()
  for (const route of routes) {
    router.post(route.path, (request, response, next) => {
      route.run(cdd, request).then(result => response.json(result), next)
    })
  }
  return router
}
