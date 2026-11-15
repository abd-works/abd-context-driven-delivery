import express, { type Express, type NextFunction, type Request, type Response } from 'express'
import { join } from 'node:path'

import type { ProjectConnections } from '@cdd/cdd-connection'
import { CddRequestError, type CddRoute } from '@cdd/cdd-shared'
import { ChatAdapter, chatRoutes } from '@cdd/harness/chat/chat'
import { fidelityProgressRoutes } from '@cdd/space/kanban/fidelity-progress'
import { ticketRoutes } from '@cdd/space/kanban/ticket'
import { fileCommentsRoutes } from '@cdd/space/session/file-comments'
import { practiceSessionOutputRoutes } from '@cdd/space/session/practice-session-output'
import { sessionRoutes } from '@cdd/space/session/session'

import { DrawioViewer } from './drawio-viewer'
import { API_ROOT, DRAWIO_PAGE, FILES_HEADER } from './files/files-paths'

const CHANGING_METHODS = ['POST', 'PUT', 'PATCH', 'DELETE']
const BAD_REQUEST = 400
const FORBIDDEN = 403
const FAILED = 500

// The chat routes the page needs: sending the chat that opened it a refresh or a failure, and reading and changing the
// one selection cdd holds for its chat bar and this page. Opening or removing chats stays with the board.
const CHAT_ROUTES = ['/chat/:chat/send', '/chat/:chat/show', '/chat/:chat/select']
// The ticket routes the page needs: reading and choosing the session's formats, the chat bar's format chips.
const TICKET_ROUTES = ['/ticket/:ticket/format-choices', '/ticket/:ticket/choose-formats']

// The Files app reads a session's files, a fidelity's files, and the comments on them, turns the session's practices on
// or off, and tells the chat that opened it; it never reads the board.
export const filesRoutes: CddRoute[] = [
  ...sessionRoutes,
  ...fileCommentsRoutes,
  ...fidelityProgressRoutes,
  ...practiceSessionOutputRoutes,
  ...chatRoutes.filter(route => CHAT_ROUTES.includes(route.path)),
  ...ticketRoutes.filter(route => TICKET_ROUTES.includes(route.path)),
]

const textOf = (failure: unknown): string => (failure instanceof Error ? failure.message : String(failure))

// This server can put a person's comments into a live chat, so only this machine's own page may reach it. The Host check
// stops a site pointing its own domain name at 127.0.0.1; the header forces a preflight, which this server never answers.
function onlyThisMachine(port: number) {
  return (request: Request, response: Response, next: NextFunction): void => {
    const isLocalHost = [`127.0.0.1:${port}`, `localhost:${port}`].includes(request.headers.host ?? '')
    const isForeignPost = CHANGING_METHODS.includes(request.method) && !request.headers[FILES_HEADER]
    if (isLocalHost && !isForeignPost) return next()
    response.status(FORBIDDEN).json({ error: 'Refused: this server answers only its own page on this machine.' })
  }
}

// A failure the server meets serving the page, sent to the chat that opened it, which shows it on its chat bar. A chat
// that cannot be told is written to the server's log beside the failure the tab already shows.
async function tellChat(projects: ProjectConnections, request: Request, failure: string, context: string): Promise<void> {
  const chat = String(request.query.chat ?? '')
  if (!chat) return
  await new ChatAdapter(projects.of(request), chat)
    .send('failure', JSON.stringify({ failure, context }))
    .catch(reason => console.error(`The chat ${chat} was not told "${failure}": ${textOf(reason)}`))
}

async function answer(projects: ProjectConnections, route: CddRoute, request: Request, response: Response): Promise<void> {
  try {
    response.json((await route.run(projects.of(request), request)) ?? null)
  } catch (failure) {
    response.status(failure instanceof CddRequestError ? BAD_REQUEST : FAILED).json({ error: textOf(failure) })
  }
}

export function createFilesApp(projects: ProjectConnections, port: number, staticRoot: string, drawio: DrawioViewer): Express {
  const app = express()
  app.use(onlyThisMachine(port))
  app.use(express.json())
  for (const route of filesRoutes) app.post(`${API_ROOT}${route.path}`, (request, response) => void answer(projects, route, request, response))
  // A .drawio file's link: start the viewer on the file and send the tab on to it. A viewer that does not start is shown
  // in the tab and told to the chat that opened the page, as the page tells every failure.
  app.get(`${API_ROOT}${DRAWIO_PAGE}`, async (request, response) => {
    const path = String(request.query.path ?? '')
    try {
      response.redirect(302, await drawio.urlOf(path))
    } catch (failure) {
      const said = `${path} did not open in the draw.io viewer: ${textOf(failure)}`
      response.status(FAILED).type('text/plain').send(said)
      await tellChat(projects, request, said, `Opening ${path} from the Files app`)
    }
  })
  app.use(express.static(staticRoot))
  app.get('*', (_request, response) => response.sendFile(join(staticRoot, 'index.html')))
  return app
}
