// What the Files app's page and its server agree on: where the routes sit, the header every post carries, the
// draw.io viewer's address, and the words a link uses to name what the page shows.
export const API_ROOT = '/api'
export const FILES_HEADER = 'x-cdd-files'
export const DRAWIO_PATH = '/drawio/open'
export const DRAWIO_PORT = 8791

export const SESSION_FOLDER_QUERY = 'session-folder'
export const SESSION_QUERY = 'session'
export const FILE_QUERY = 'file'
export const FILES_QUERY = 'files'
export const FIDELITY_QUERY = 'fidelity'

export const isDrawio = (path: string): boolean => path.toLowerCase().endsWith('.drawio')

// The draw.io editor on a file named from the repository's root (.claude/rules/drawio-viewer.md).
export const drawioEditorUrl = (path: string): string => `http://127.0.0.1:${DRAWIO_PORT}/edit?f=${encodeURIComponent(path)}`
