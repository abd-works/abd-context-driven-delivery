// What the Files app's page and its server agree on: where the routes sit, the header every post carries, the
// draw.io viewer's address, and the words a link uses to name what the page shows.
export const API_ROOT = '/api'
export const FILES_HEADER = 'x-cdd-files'
// The page a .drawio file's link opens in a new tab: the Files server starts the draw.io viewer on the file and sends the
// tab on to it. A link is a navigation the browser always allows, where a tab opened from a script can be refused.
export const DRAWIO_PAGE = '/drawio/page'
export const DRAWIO_PORT = 8791
// The route that shows a file or folder in the system's file browser, on the machine the Files server runs on.
export const REVEAL_PATH = '/reveal'

export const SESSION_FOLDER_QUERY = 'session-folder'
export const SESSION_QUERY = 'session'
export const FILE_QUERY = 'file'
export const FILES_QUERY = 'files'
export const FIDELITY_QUERY = 'fidelity'

export const isDrawio = (path: string): boolean => path.toLowerCase().endsWith('.drawio')

// The address a .drawio file's link opens: the Files server's draw.io page on the file, naming the chat that opened the
// page so a viewer that does not start is told to that chat, as every failure of the page is, and the page's project,
// whose file it is.
export const drawioPageOf = (path: string, chat: string, project = ''): string => {
  const query = new URLSearchParams({ path, ...(chat ? { chat } : {}), ...(project ? { project } : {}) })
  return `${API_ROOT}${DRAWIO_PAGE}?${query.toString()}`
}

const isWholePath = (path: string): boolean => /^([a-zA-Z]:)?[\\/]/.test(path)

// The draw.io editor on a file named from its project's root. One viewer serves every project, rooted at whichever
// started it, so a file of a named project is sent as its whole path (.claude/rules/drawio-viewer.md). The viewer
// answers on DRAWIO_PORT, unless it was started on a port of its own, as a spec's viewer is.
export const drawioEditorUrl = (path: string, project = '', port = DRAWIO_PORT): string => {
  const file = project && !isWholePath(path) ? `${project.replace(/[\\/]+$/, '')}/${path}` : path
  return `http://127.0.0.1:${port}/edit?f=${encodeURIComponent(file)}`
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
