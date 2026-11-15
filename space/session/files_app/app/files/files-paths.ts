// What the Files app's page and its server agree on: where the routes sit, the header every post carries, the
// draw.io viewer's address, and the words a link uses to name what the page shows.
export const API_ROOT = '/api'
export const FILES_HEADER = 'x-cdd-files'
// The page a .drawio file's link opens in a new tab: the Files server starts the draw.io viewer on the file and sends the
// tab on to it. A link is a navigation the browser always allows, where a tab opened from a script can be refused.
export const DRAWIO_PAGE = '/drawio/page'
export const DRAWIO_PORT = 8791

export const SESSION_FOLDER_QUERY = 'session-folder'
export const SESSION_QUERY = 'session'
export const FILE_QUERY = 'file'
export const FILES_QUERY = 'files'
export const FIDELITY_QUERY = 'fidelity'

export const isDrawio = (path: string): boolean => path.toLowerCase().endsWith('.drawio')

// The address a .drawio file's link opens: the Files server's draw.io page on the file, naming the chat that opened the
// page so a viewer that does not start is told to that chat, as every failure of the page is.
export const drawioPageOf = (path: string, chat: string): string => {
  const query = new URLSearchParams({ path, ...(chat ? { chat } : {}) })
  return `${API_ROOT}${DRAWIO_PAGE}?${query.toString()}`
}

// The draw.io editor on a file named from the repository's root (.claude/rules/drawio-viewer.md).
export const drawioEditorUrl = (path: string): string => `http://127.0.0.1:${DRAWIO_PORT}/edit?f=${encodeURIComponent(path)}`
