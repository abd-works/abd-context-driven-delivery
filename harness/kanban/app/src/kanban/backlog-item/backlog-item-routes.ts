import { Router } from 'express'

import type { CddConnectionNode } from '../../cdd/cdd-connection-node'
import { answer } from '../../session-board/answer'
import { BacklogItemNode } from './backlog-item-node'

export function backlogItemRoutes(cdd: CddConnectionNode): Router {
  const routes = Router()
  routes.post('/backlog', answer(req => BacklogItemNode.addRequested(cdd, req)))
  routes.post('/backlog/:title/start', answer(req => BacklogItemNode.fromRequest(cdd, req).start()))
  return routes
}
