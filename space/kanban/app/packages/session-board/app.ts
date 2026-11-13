import express, { type Express, type NextFunction, type Request, type Response } from 'express'
import { join } from 'node:path'

import type { ProjectConnections } from '@cdd/cdd-connection'
import { backlogItemRoutes } from '@cdd/space/kanban/backlog-item'
import { boardRoutes } from '@cdd/space/kanban/board'
import { fidelityProgressRoutes } from '@cdd/space/kanban/fidelity-progress'
import { stageRoutes } from '@cdd/space/kanban/stage'
import { ticketRoutes } from '@cdd/space/kanban/ticket'
import { fileCommentsRoutes } from '@cdd/space/session/file-comments'
import { practiceSessionOutputRoutes } from '@cdd/space/session/practice-session-output'
import { sessionRoutes } from '@cdd/space/session/session'
import { chatRoutes } from '@cdd/harness/chat/chat'
import { appRoutes } from '@cdd/harness/diagnostics/app'
import { cddRoutes } from '@src/session-board/cdd-routes'
import { API_ROOT } from '@src/session-board/board-server-paths'
import { answerFailure, HttpException } from '@src/session-board/http-exception'

import { STORY_MAP_PAGE } from '../../../../../cdd_guidance/practices/stories/app/story-map-page'
import { storyMapBuild, storyMapRoutes } from '../../../../../cdd_guidance/practices/stories/app/story-map-routes'

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

export function createApp(projects: ProjectConnections, port: number, staticRoot: string): Express {
  const app = express()
  app.use(onlyThisMachine(port))
  app.use(express.json())
  // The board and the Story UI editor both reach the chat routes; each route is mounted once.
  const routes = new Set([...boardRoutes, ...stageRoutes, ...ticketRoutes, ...fidelityProgressRoutes, ...sessionRoutes, ...fileCommentsRoutes, ...practiceSessionOutputRoutes, ...backlogItemRoutes, ...chatRoutes, ...appRoutes, ...storyMapRoutes])
  app.use(API_ROOT, cddRoutes(projects, [...routes]))
  // The Story UI editor answers on this server too, at its own page, so it shares the board's port and the board's
  // state: its calls are the story map's generated routes above, and its page is the one its own folder builds.
  app.use(STORY_MAP_PAGE, express.static(storyMapBuild))
  app.get(`${STORY_MAP_PAGE}/*`, (_request, response) => {
    response.sendFile(join(storyMapBuild, 'index.html'))
  })
  // The built page names its hashed script, so its index changes with every build: an open page compares the page
  // served here with the one it loaded, and reloads itself on a new one.
  app.use(express.static(staticRoot))
  app.get('*', (_request, response) => {
    response.sendFile(join(staticRoot, 'index.html'))
  })
  app.use(answerFailure)
  return app
}
