import express, { type Express, type NextFunction, type Request, type Response } from 'express'
import { join } from 'node:path'

import type { CddConnectionNode } from '@src/cdd/cdd-connection-node'
import { backlogItemRoutes } from '@src/kanban/backlog-item/backlog-item-routes'
import { boardRoutes } from '@src/kanban/board/board-routes'
import type { ChatsNode } from '@src/kanban/chat/chat-node'
import { chatRoutes } from '@src/kanban/chat/chat-routes'
import { ticketRoutes } from '@src/kanban/ticket/ticket-routes'
import { answerFailure, HttpException } from '@src/session-board/http-exception'

// The header forces a preflight, which this server never answers, so a page on another site cannot post here.
export const BOARD_HEADER = 'x-cdd-board'
const CHANGING_METHODS = ['POST', 'PUT', 'PATCH', 'DELETE']
const FORBIDDEN = 403

// This server can put prompts into a live chat, so only this machine's own page and mod may reach it. The Host check
// stops a site pointing its own domain name at 127.0.0.1.
const onlyThisMachine = (port: number) => (request: Request, _response: Response, next: NextFunction) => {
  const isLocalHost = [`127.0.0.1:${port}`, `localhost:${port}`].includes(request.headers.host ?? '')
  const isForeignPost = CHANGING_METHODS.includes(request.method) && !request.headers[BOARD_HEADER]
  next(isLocalHost && !isForeignPost ? undefined : new HttpException(FORBIDDEN, 'Refused: this server answers only its own page and mod on this machine.'))
}

export function createApp(cdd: CddConnectionNode, chats: ChatsNode, port: number, staticRoot: string): Express {
  const app = express()
  app.use(onlyThisMachine(port))
  app.use(express.json())
  app.use('/api', boardRoutes(cdd), ticketRoutes(cdd), backlogItemRoutes(cdd), chatRoutes(chats))
  app.use(express.static(staticRoot))
  app.get('*', (_request, response) => {
    response.sendFile(join(staticRoot, 'index.html'))
  })
  app.use(answerFailure)
  return app
}
