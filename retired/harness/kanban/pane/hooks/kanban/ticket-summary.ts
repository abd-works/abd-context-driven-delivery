import type { BoardJson, ColumnJson, TicketJson } from '../../types'

// What the status line, the system prompt, and the toasts say about a ticket, read from its JSON alone, so that
// both the board client and the ticket client can use it.
export const ticketsOf = (column: ColumnJson): TicketJson[] => [
  ...(column.in_progress ?? []),
  ...(column.done ?? []),
  ...(column.tickets ?? []),
]

export const allTickets = (shown: BoardJson): TicketJson[] => shown.columns.flatMap(ticketsOf)

export const activeTicketJson = (shown: BoardJson): TicketJson | undefined =>
  allTickets(shown).find(ticket => ticket.name === shown.active)

export const violationsOf = (ticket: TicketJson): string[] =>
  Object.entries(ticket.progress)
    .filter(([, state]) => state === 'violations')
    .map(([slug]) => slug)

export const guidanceSlug = (slug: string): string => slug.replaceAll('_', '-')

export const countOf = (count: number, noun: string): string => `${count} ${count === 1 ? noun : `${noun}s`}`

export const statusOf = (ticket: TicketJson): string => {
  const violations = violationsOf(ticket).length
  return [
    ticket.name,
    ticket.column,
    ticket.next ? `next: ${ticket.next}` : ticket.is_done ? 'done' : '',
    violations ? countOf(violations, 'violation') : '',
  ]
    .filter(Boolean)
    .join(' · ')
}
