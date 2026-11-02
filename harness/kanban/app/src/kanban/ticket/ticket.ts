import type { FileEntryData } from '@cdd/harness/kanban/ticket'

// What ticket.files answers: for each fidelity, for each format, the files that format offers.
export type TicketFiles = Record<string, Record<string, FileEntryData[]>>
