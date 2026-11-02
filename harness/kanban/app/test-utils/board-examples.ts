import type { BacklogItemData } from '@cdd/harness/kanban/backlog-item'
import type { BoardData, ColumnData } from '@cdd/harness/kanban/board'
import type { TicketData } from '@cdd/harness/kanban/ticket'

export const DISCOVERY_SLUGS = ['stories-story_map', 'ddd-bounded_context']
const STAGE_SLUGS: Record<string, string[]> = { Discovery: DISCOVERY_SLUGS, Specification: ['stories-scenarios'], Implementation: ['stories-acceptance_tests'] }

export const ticketJson = (name: string, change: Partial<TicketData> = {}): TicketData => ({
  name,
  title: name,
  scope: 'feature',
  parent: '',
  column: 'Discovery',
  is_done: false,
  can_move_next: true,
  next: 'stories-story_map',
  next_action: 'generate',
  last_activity: '2026-11-01T10:00:00Z',
  handoff: '',
  reports: {},
  violation_counts: {},
  practices: { stories: true, ddd: true, ux: true, clean_engineering: true, bdd: true },
  progress: { 'stories-story_map': 'not_started', 'ddd-bounded_context': 'not_started' },
  actions: {},
  allowed_actions: { 'stories-story_map': ['generate'], 'ddd-bounded_context': ['generate'] },
  ...change,
})

export const itemJson = (title: string, text = ''): BacklogItemData => ({ title, text, path: `.sessions/_backlog/${title}.md`, last_activity: '2026-11-01T10:00:00Z' })

export const discovery = (inProgress: TicketData[] = [], done: TicketData[] = []): ColumnData => ({
  name: 'Discovery',
  work_required: DISCOVERY_SLUGS,
  formats: { 'stories-story_map': ['markdown', 'drawio'], 'ddd-bounded_context': ['markdown'] },
  default_formats: { 'stories-story_map': 'markdown', 'ddd-bounded_context': 'markdown' },
  wip_limit: 3,
  is_over_limit: false,
  in_progress: inProgress,
  done,
})

export const boardJson = (columns: ColumnData[], active: string | null = null, items: BacklogItemData[] = []): BoardData => ({
  project: 'pet-clinic',
  active,
  columns: [{ name: 'Backlog', items }, ...columns, { name: 'Complete', tickets: [] }],
})

const titleOf = (name: string): string => {
  const words = name.replaceAll('-', ' ')
  return `${words.charAt(0).toUpperCase()}${words.slice(1)}`
}

// A ticket as the board tools answer it, placed in a column: named `move-me`, titled `Move me`, as the fixture repository has them.
export const placedTicket = (name: string, column: string, change: Partial<TicketData> = {}): TicketData => ticketJson(name, { title: titleOf(name), column, ...change })

const stageHolding = (name: string, tickets: TicketData[]): ColumnData => ({
  ...discovery(tickets.filter(ticket => !ticket.is_done), tickets.filter(ticket => ticket.is_done)),
  name,
  work_required: STAGE_SLUGS[name] ?? [],
})

// The whole board holding these tickets, each in its own column.
export function boardHolding(tickets: TicketData[], items: BacklogItemData[] = [], active: string | null = null): BoardData {
  const inColumn = (name: string) => tickets.filter(ticket => ticket.column === name)
  const stages = Object.keys(STAGE_SLUGS).map(name => stageHolding(name, inColumn(name)))
  return { project: 'pet-clinic', active, columns: [{ name: 'Backlog', items }, ...stages, { name: 'Complete', tickets: inColumn('Complete') }] }
}
