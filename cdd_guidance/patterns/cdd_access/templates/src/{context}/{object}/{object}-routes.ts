/**
 * Each route asks the {Object}Node for one operation. It never calls a tool. The object serializes through toJSON().
 *
 * ```
 * file: src/{context}/{object}/{object}-routes.ts
 * ```
 */
import { Router } from 'express'

import type { CddConnectionNode } from '../../cdd/cdd-connection-node'
import { {Object}Node } from './{object}-node'

export function {object}Routes(cdd: CddConnectionNode): Router {
  const routes = Router()
  routes.post('/{object}s/:{object}/{operation-slug}', async (request, response, next) => {
    await {Object}Node.fromRequest(cdd, request).{operation}().then(result => response.json(result), next)
  })
  return routes
}
