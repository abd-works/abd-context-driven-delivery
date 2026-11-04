import express, { type Express, type NextFunction, type Request, type Response } from 'express'
import { createHash } from 'node:crypto'
import { existsSync, readFileSync } from 'node:fs'
import { join } from 'node:path'

import type { CddConnection } from '@cdd/cdd-connection'
import { backlogItemRoutes } from '@cdd/harness/kanban/backlog-item'
import { boardRoutes } from '@cdd/harness/kanban/board'
import { ticketRoutes } from '@cdd/harness/kanban/ticket'
import { chatRoutes } from '@cdd/tools/chat/chat'
import { cddRoutes } from '@src/session-board/cdd-routes'
import { ClaudeLink } from '@src/session-board/claude-link'
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

export function createApp(cdd: CddConnection, port: number, staticRoot: string, claudeLink = new ClaudeLink()): Express {
  const app = express()
  app.use(onlyThisMachine(port))
  app.use(express.json())
  // The one cdd server keeps the code it started with, so a person restarts it to pick up changed Python. It reloads in
  // place, so every chat connected to it gets the new code too.
  app.post('/api/cdd/restart', async (_request, response) => {
    response.json(await cdd.call<{ is_restarted: boolean }>('cdd.restart', {}))
  })
  app.post('/api/claude/open', (request, response) => {
    claudeLink.open(request.body?.link)
    response.json({ is_opened: true })
  })
  // The built page names its hashed script, so the text of index.html changes with every build. An open page compares it
  // with the build it loaded and reloads itself on a new one.
  app.get('/api/build', (_request, response) => {
    const index = join(staticRoot, 'index.html')
    const build = existsSync(index) ? createHash('sha256').update(readFileSync(index)).digest('hex') : ''
    response.json({ build })
  })
  app.use('/api', cddRoutes(cdd, [...boardRoutes, ...ticketRoutes, ...backlogItemRoutes, ...chatRoutes]))
  app.use(express.static(staticRoot))
  app.get('*', (_request, response) => {
    response.sendFile(join(staticRoot, 'index.html'))
  })
  app.use(answerFailure)
  return app
}
