import { Router } from 'express'

import type { CddConnectionNode } from '../../cdd/cdd-connection-node'
import { answer } from '../../session-board/answer'
import { BoardNode } from './board-node'

export function boardRoutes(cdd: CddConnectionNode): Router {
  const routes = Router()
  const board = new BoardNode(cdd)
  routes.get('/board', answer(() => board.show()))
  routes.post('/board/wip-limit', answer(req => board.setWipLimitRequested(req)))
  routes.get('/board/help', answer(req => board.helpRequested(req)))
  return routes
}
