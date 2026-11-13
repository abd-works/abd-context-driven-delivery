// Where the board page reaches its server: every call is a POST under /api. The generated routes of the CDD domain answer
// there, and so do the two the board server answers itself, which reach no domain tool: Update, which rebuilds and
// restarts this server and re-pins cdd, a job a cdd call cannot do while cdd restarts under it; and claude/open, which
// hands a new chat's link to the Claude app, as a page in the app's Browser pane cannot.
export const API_ROOT = '/api'
export const UPDATE_PATH = '/update'
export const CLAUDE_OPEN_PATH = '/claude/open'
export const BOARD_SERVER_PATHS = [UPDATE_PATH, CLAUDE_OPEN_PATH]
