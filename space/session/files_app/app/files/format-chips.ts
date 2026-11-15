import type { CddApi } from '@cdd/cdd-shared'
import { TicketClientGenerated, type FormatChoiceData } from '@cdd/space/kanban/ticket'

import type { FilesLink } from './files-link'
import type { FilesStore } from './files-state'

// The chat bar's glyph for each group of formats (harness/chat-ui/pane/hooks/chat-bar/bar-columns.ts FORMAT_GLYPHS), so
// a format looks the same on the bar and here.
const FORMAT_GLYPHS: Record<string, string> = { markdown: 'M↓', diagram: '◇', code: '</>', canvas: '▦' }

export const formatGlyphOf = (label: string): string => FORMAT_GLYPHS[label] ?? label

// The formats of the chips chosen, each once; none chosen, every format is shown.
export const chosenFormatsOf = (choices: FormatChoiceData[]): string[] => [...new Set(choices.filter(choice => choice.is_chosen).flatMap(choice => choice.formats))]

// Which chips are chosen, the one thing about them the file list depends on.
export const chosenKeyOf = (choices: FormatChoiceData[]): string => choices.filter(choice => choice.is_chosen).map(choice => choice.label).join(',')

// The format chips of the Files app: a chip for each group of formats the link's fidelities offer, chosen or not in the
// session, as the chat bar's format chips are. They are the session's choice (ticket.format_choices,
// ticket.choose_formats), so a chip pressed here is pressed on the chat bar too, and the page keeps no pick of its own.
export class FormatChips {
  private readonly ticket: TicketClientGenerated | null

  constructor(
    api: CddApi,
    private readonly link: FilesLink,
    private readonly store: FilesStore,
  ) {
    this.ticket = link.isSessionFolder || !link.ticket ? null : TicketClientGenerated.named(api, link.ticket)
  }

  // The chips of the fidelities listed, as the session holds them now; none for a session folder, which has no
  // fidelities.
  async read(fidelities: string[]): Promise<FormatChoiceData[]> {
    if (!this.ticket || !fidelities.length) return []
    return (await this.ticket.formatChoices(fidelities)) ?? []
  }

  // A press on a chip chooses it in the session for every fidelity the page lists, or no longer; the page shows the chips
  // cdd answers.
  async toggle(label: string, fidelities: string[]): Promise<FormatChoiceData[] | null> {
    const chip = this.store.state.formatChoices.find(choice => choice.label === label)
    if (!chip || !this.ticket) return null
    return (await this.ticket.chooseFormats(fidelities, label, !chip.is_chosen)) ?? []
  }
}
