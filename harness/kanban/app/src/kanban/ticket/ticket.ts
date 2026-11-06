import type { FileEntryData } from '@cdd/harness/kanban/fidelity-progress'

// The files several fidelities of a ticket declare: for each fidelity, for each format, the files that format offers.
export type TicketFiles = Record<string, Record<string, FileEntryData[]>>
