import { Router, type Request } from 'express'

import type { CddConnectionNode } from '../../cdd/cdd-connection-node'
import { answer } from '../../session-board/answer'
import { TicketNode } from './ticket-node'

export function ticketRoutes(cdd: CddConnectionNode): Router {
  const routes = Router()
  const ticket = (req: Request): TicketNode => TicketNode.fromRequest(cdd, req)
  routes.post('/tickets/:ticket/move-next', answer(req => ticket(req).moveNext()))
  routes.post('/tickets/:ticket/move-previous', answer(req => ticket(req).movePrevious()))
  routes.post('/tickets/:ticket/archive', answer(req => ticket(req).archive()))
  routes.post('/tickets/:ticket/close', answer(req => ticket(req).closeRequested(req)))
  routes.post('/tickets/:ticket/activate', answer(req => ticket(req).activateRequested(req)))
  routes.post('/tickets/:ticket/practice', answer(req => ticket(req).enablePracticeRequested(req)))
  routes.post('/tickets/:ticket/generate-commands', answer(req => ticket(req).generateCommandsRequested(req)))
  routes.post('/tickets/:ticket/files', answer(req => ticket(req).filesRequested(req)))
  routes.get('/tickets/:ticket/workspace', answer(req => ticket(req).workspace()))
  routes.get('/tickets/:ticket/file', answer(req => ticket(req).readFileRequested(req)))
  routes.get('/tickets/:ticket/report', answer(req => ticket(req).reportRequested(req)))
  routes.get('/tickets/:ticket/violations', answer(req => ticket(req).violations()))
  return routes
}
