import express, { type Express, type NextFunction, type Request, type Response } from 'express'
import { statSync } from 'node:fs'
import { join } from 'node:path'

import type { CddConnection, ProjectConnections } from '@cdd/cdd-connection'
import { CddRequestError, PROJECT_HEADER, cddProgressRoutes, type CddRoute } from '@cdd/cdd-shared'
import { ChatAdapter, chatRoutes } from '@cdd/harness/chat/chat'
import { whiteboardFileRoutes } from '@cdd/harness/whiteboard/whiteboard-file'
import { failureRoutes, type FailureData } from '@cdd/tools/error_display/failure'
import { formatAlignmentRoutes } from '@cdd/align/format-alignment'
import { fidelityProgressRoutes } from '@cdd/space/kanban/fidelity-progress'
import { ticketRoutes } from '@cdd/space/kanban/ticket'
import { fileCommentsRoutes } from '@cdd/space/session/files/file-comments'
import { practiceSessionOutputRoutes } from '@cdd/space/session/practices/practice-session-output'
import { sessionRoutes } from '@cdd/space/session/session'

import { DrawioViewer } from './drawio-viewer'
import { FileExplorer } from './file-explorer'
import { API_ROOT, DRAWIO_PAGE, FILES_HEADER, REVEAL_PATH } from './files/files-paths'

const CHANGING_METHODS = ['POST', 'PUT', 'PATCH', 'DELETE']
const BAD_REQUEST = 400
const FORBIDDEN = 403
const FAILED = 500

// The one chat route the page needs: telling the chat that opened it a failure, and sending it a failure's fix. The stages, practices and formats
// selected are the session's guidance selection, reached through its routes. Opening or removing chats stays with the board.
const CHAT_ROUTES = ['/chat/:chat/send']
// The ticket route the page lists its files through: every fidelity's files in one call.
const TICKET_ROUTES = ['/ticket/:ticket/fidelity-files', '/ticket/:ticket/root-files']

// The Files app reads a session's files, a fidelity's files, and the comments on them, follows the cdd server's progress
// while its graph view reads the graph, turns the session's practices on or off, tells the chat that opened it, and
// asks for the most common causes of a failure its Fix button sends that chat (failure.describe), and reads the board a
// whiteboard file holds (whiteboard-file.show); it never reads the CDD Kanban board.
export const filesRoutes: CddRoute[] = [
  ...sessionRoutes,
  ...formatAlignmentRoutes,
  ...cddProgressRoutes,
  ...fileCommentsRoutes,
  ...fidelityProgressRoutes,
  ...practiceSessionOutputRoutes,
  ...failureRoutes,
  ...whiteboardFileRoutes,
  ...chatRoutes.filter(route => CHAT_ROUTES.includes(route.path)),
  ...ticketRoutes.filter(route => TICKET_ROUTES.includes(route.path)),
]

// A request naming a project folder that is not there, such as a ticket's worktree removed while its Files tab stays
// open. Without it the cdd connection starts its connect script in that folder, and Node words the failure as the
// Python program not found, which sends the person to repair a Python and a cdd server that are both fine.
export class ProjectFolderMissingError extends Error {
  constructor(readonly folder: string) {
    super(`The project folder ${folder} is not there: it was moved or removed, such as a ticket's worktree closed since this page opened.`)
    this.name = 'ProjectFolderMissingError'
  }
}

// The connection of the project the request names in its header, refused when that folder is not there; the connection
// the server started with for a request naming none.
export function connectionOf(projects: ProjectConnections, request: { get(name: string): string | undefined }): CddConnection {
  const named = request.get(PROJECT_HEADER)?.trim()
  if (named && !statSync(named, { throwIfNoEntry: false })?.isDirectory()) throw new ProjectFolderMissingError(named)
  return projects.of(request)
}

const REFUSALS = [CddRequestError, ProjectFolderMissingError]

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
async function tellChat(projects: ProjectConnections, request: Request, failure: Pick<FailureData, 'failure' | 'context'>): Promise<void> {
  const chat = String(request.query.chat ?? '')
  if (!chat) return
  await new ChatAdapter(projects.of(request), chat)
    .send('failure', JSON.stringify(failure))
    .catch(reason => console.error(`The chat ${chat} was not told "${failure.failure}": ${textOf(reason)}`))
}

// What a route's operation answered, or the failure it raised, a refused request told apart from a failed one.
async function answer(running: () => Promise<unknown>, response: Response): Promise<void> {
  try {
    response.json((await running()) ?? null)
  } catch (failure) {
    response.status(REFUSALS.some(refusal => failure instanceof refusal) ? BAD_REQUEST : FAILED).json({ error: textOf(failure) })
  }
}

export function createFilesApp(projects: ProjectConnections, port: number, staticRoot: string, drawio: DrawioViewer, explorer = new FileExplorer()): Express {
  const app = express()
  app.use(onlyThisMachine(port))
  app.use(express.json())
  for (const route of filesRoutes) app.post(`${API_ROOT}${route.path}`, (request, response) => void answer(async () => route.run(connectionOf(projects, request), request), response))
  // A .drawio file's link: start the viewer on the file and send the tab on to it. A viewer that does not start is shown
  // in the tab and told to the chat that opened the page, as the page tells every failure.
  app.get(`${API_ROOT}${DRAWIO_PAGE}`, async (request, response) => {
    const path = String(request.query.path ?? '')
    try {
      response.redirect(302, await drawio.urlOf(path, String(request.query.project ?? '')))
    } catch (failure) {
      const said = `${path} did not open in the draw.io viewer: ${textOf(failure)}`
      response.status(FAILED).type('text/plain').send(said)
      await tellChat(projects, request, { failure: said, context: `Opening ${path} from the Files app` })
    }
  })
  // A file or folder the page names, from the project its header names, shown in the system's file browser here, on the
  // person's own machine, which only this machine's page reaches.
  app.post(`${API_ROOT}${REVEAL_PATH}`, (request, response) => {
    try {
      explorer.reveal(request.get(PROJECT_HEADER) || process.cwd(), String(request.body?.path ?? ''))
      response.json(null)
    } catch (failure) {
      response.status(FAILED).json({ error: textOf(failure) })
    }
  })
  app.use(express.static(staticRoot))
  app.get('*', (_request, response) => response.sendFile(join(staticRoot, 'index.html')))
  return app
}
