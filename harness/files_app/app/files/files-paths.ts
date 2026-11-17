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
// page so a viewer that does not start is told to that chat, as every failure of the page is.
export const drawioPageOf = (path: string, chat: string): string => {
  const query = new URLSearchParams({ path, ...(chat ? { chat } : {}) })
  return `${API_ROOT}${DRAWIO_PAGE}?${query.toString()}`
}

// The draw.io editor on a file named from the repository's root (.claude/rules/drawio-viewer.md).
export const drawioEditorUrl = (path: string): string => `http://127.0.0.1:${DRAWIO_PORT}/edit?f=${encodeURIComponent(path)}`

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
