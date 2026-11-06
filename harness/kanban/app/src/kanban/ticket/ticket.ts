import { FidelityProgressClientGenerated, type FileEntryData } from '@cdd/harness/kanban/fidelity-progress'
import type { BoardData } from '@cdd/harness/kanban/board'
import type { CddApi } from '@cdd/cdd-shared'

// The files several fidelities of a ticket declare: for each fidelity, for each format, the files that format offers.
export type TicketFiles = Record<string, Record<string, FileEntryData[]>>

// Each fidelity answers for its own files, so a tile or panel over several fidelities reads them side by side; none
// when any read failed, because the page has already shown that failure.
export async function filesOf(api: CddApi, ticket: string, slugs: string[]): Promise<TicketFiles | null> {
  const read = await Promise.all(slugs.map(slug => FidelityProgressClientGenerated.named(api, ticket, slug).files()))
  if (read.some(files => !files)) return null
  return Object.fromEntries(slugs.map((slug, index) => [slug, read[index]!]))
}

// The session.json of a ticket on the board, which names it to the session tools.
export const sessionFileOf = (board: BoardData | null, ticket: string): string =>
  board?.columns.flatMap(column => column.tickets ?? []).find(shown => shown.name === ticket)?.session.session_file ?? ''
