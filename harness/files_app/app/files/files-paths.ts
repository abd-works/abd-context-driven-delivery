// What the Files app's page and its server agree on: where the routes sit, the header every post carries, the
// draw.io viewer's address, and the words a link uses to name what the page shows.
export const API_ROOT = '/api'
export const FILES_HEADER = 'x-cdd-files'
// The page a .drawio file's link opens in a new tab: the Files server starts the draw.io viewer on the file and sends the
// tab on to it. A link is a navigation the browser always allows, where a tab opened from a script can be refused.
export const DRAWIO_PAGE = '/drawio/page'
export const DRAWIO_PORT = 8791
// Where the draw.io viewer sends a press on a diagram's link to a file, such as a story's own file from the story map:
// the Files server shows the file in the Files app at the heading the link names, or tells the chat it is not there.
export const DRAWIO_LINK = '/drawio/link'
// The route that shows a file or folder in the system's file browser, on the machine the Files server runs on.
export const REVEAL_PATH = '/reveal'
// Where an HTML page of the page's project finds its own scripts, styles and images: the server serves each project
// under a key of its own (app/page-files.ts), which a post to this route under the API root answers.
export const PAGE_FILES = '/page-files'
// Where a generated UX mockup loads the Story Demo scripts from (cdd_guidance/practices/ux/templates/html/mockup_shell.html).
export const STORY_DEMO_ROOT = '/practices/ux/story-demo'

export const SESSION_FOLDER_QUERY = 'session-folder'
export const WORKPATH_FOLDER_QUERY = 'workpath-folder'
export const SESSION_QUERY = 'session'
export const FILE_QUERY = 'file'
export const LINE_QUERY = 'line'
export const FILES_QUERY = 'files'
export const FIDELITY_QUERY = 'fidelity'

export const isDrawio = (path: string): boolean => path.toLowerCase().endsWith('.drawio')
// A whiteboard file, which the page draws on a canvas rather than showing its text.
export const isWhiteboard = (path: string): boolean => path.toLowerCase().endsWith('.whiteboard')

// How a diagram is opened: the project whose file it is, the chat that opened it, which a failure is told to, the ticket
// whose files the Files app lists, the Files server its links to files go through (opener), and the viewer's port.
export type DrawioOpening = { project?: string; chat?: string; ticket?: string; opener?: string; port?: number }

const namedOnly = (named: Record<string, string | undefined>): URLSearchParams =>
  new URLSearchParams(Object.entries(named).filter((entry): entry is [string, string] => Boolean(entry[1])))

// The address a .drawio file's link opens: the Files server's draw.io page on the file, naming the chat that opened the
// page so a viewer that does not start is told to that chat, as every failure of the page is, the page's project,
// whose file it is, and its ticket.
export const drawioPageOf = (path: string, opening: DrawioOpening = {}): string =>
  `${API_ROOT}${DRAWIO_PAGE}?${namedOnly({ path, chat: opening.chat, project: opening.project, ticket: opening.ticket }).toString()}`

const isWholePath = (path: string): boolean => /^([a-zA-Z]:)?[\\/]/.test(path)

// The draw.io editor on a file named from its project's root. One viewer serves every project, rooted at whichever
// started it, so a file of a named project is sent as its whole path (.claude/rules/drawio-viewer.md). The viewer
// answers on DRAWIO_PORT, unless it was started on a port of its own, as a spec's viewer is. Opened by a Files server,
// it names that server, the project, the chat and the ticket, so the diagram's links to files open in the Files app.
export const drawioEditorUrl = (path: string, opening: DrawioOpening = {}): string => {
  const project = opening.project ?? ''
  const file = project && !isWholePath(path) ? `${project.replace(/[\\/]+$/, '')}/${path}` : path
  const url = `http://127.0.0.1:${opening.port ?? DRAWIO_PORT}/edit?f=${encodeURIComponent(file)}`
  if (!opening.opener) return url
  return `${url}&${namedOnly({ opener: opening.opener, project, chat: opening.chat, ticket: opening.ticket }).toString()}`
}

// What the menu calls showing a file in the system's file browser, by the platform the page runs on, as
// navigator.platform names it: Windows Explorer, the Mac's Finder, or a desktop's file manager.
export const revealLabelOf = (platform: string): string => {
  if (/^win/i.test(platform)) return 'Open in Explorer'
  if (/^mac/i.test(platform)) return 'Reveal in Finder'
  return 'Open in file manager'
}

// What the list says of a file it names but cannot open: one the branch changed and is not there was deleted on the
// branch, such as a file main still has; any other is a file the fidelity declares that nothing has written yet.
export const missingNoteOf = (entry: { is_changed: boolean }): string => (entry.is_changed ? 'deleted on this branch' : 'not generated yet')
