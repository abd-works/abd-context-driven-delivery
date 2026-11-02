import { Router } from 'express'

import { answer } from '../../session-board/answer'
import type { ChatsNode } from './chat-node'

export function chatRoutes(chats: ChatsNode): Router {
  const routes = Router()
  routes.get('/chats', answer(() => chats.connected))
  routes.post('/chats/:chat/commands', answer(req => chats.sendRequested(req)))
  routes.post('/chats/:chat/next', answer(req => chats.nextRequested(req)))
  return routes
}
