// What the cdd board tools return, and what is read from it. Framework-free: the browser and Node tiers share it.
export type ActionStates = { generate: string; validate: string; review: string }

export type Ticket = {
  name: string
  title: string
  scope: string
  parent: string
  column: string
  is_done: boolean
  can_move_next: boolean
  next: string | null
  next_action: string
  last_activity: string
  handoff: string
  reports: Record<string, string>
  violation_counts: Record<string, number>
  practices: Record<string, boolean>
  progress: Record<string, string>
  actions: Record<string, ActionStates>
  allowed_actions: Record<string, string[]>
}

export type BacklogItem = { title: string; text: string; path: string; last_activity: string }

export type Column = {
  name: string
  items?: BacklogItem[]
  tickets?: Ticket[]
  work_required?: string[]
  formats?: Record<string, string[]>
  default_formats?: Record<string, string>
  wip_limit?: number
  is_over_limit?: boolean
  in_progress?: Ticket[]
  done?: Ticket[]
}

export type BoardData = { project: string; active: string | null; columns: Column[] }

export type Workspace = { has_branch: boolean; has_worktree: boolean; leaving_has_branch: boolean }
export type FileEntry = { path: string; exists: boolean }
export type TicketFiles = Record<string, Record<string, FileEntry[]>>
export type FileText = { path: string; text: string }
export type SourceLine = { number: number; text: string }
export type Violation = { location: string; line: number | null; message: string; source: SourceLine[] }
export type ReportRule = { fidelity: string; name: string; description: string; count: number; violations: Violation[] }
export type Report = { path: string; text: string; rules: ReportRule[]; has_saved_graph: boolean }
export type Help = {
  practice: string
  fidelity: string
  stage: string
  overview: string
  guidance: string
  rules: { slug: string; text: string }[]
  href: string
}

export const ticketsOf = (column: Column): Ticket[] => [...(column.in_progress ?? []), ...(column.done ?? []), ...(column.tickets ?? [])]

export const allTickets = (board: BoardData): Ticket[] => board.columns.flatMap(ticketsOf)

export const activeTicket = (board: BoardData): Ticket | undefined => allTickets(board).find(ticket => ticket.name === board.active)

export const violationsOf = (ticket: Ticket): string[] =>
  Object.entries(ticket.progress)
    .filter(([, state]) => state === 'violations')
    .map(([slug]) => slug)

export const guidanceSlug = (slug: string): string => slug.replaceAll('_', '-')

// A session can sit in closed/ under the name of an open one, so a column and name together say which ticket is meant.
export const ticketAddress = (ticket: Ticket): string => `${ticket.column}/${ticket.name}`
