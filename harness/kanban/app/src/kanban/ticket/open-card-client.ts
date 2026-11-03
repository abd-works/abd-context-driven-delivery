import { practiceOf } from '../board/board-brand'
import type { BoardPage } from '../board/board-page'
import type { Tile } from '../board/board-store'
import type { ColumnClient } from '../board/column-client'
import type { TicketClient } from './ticket-client'
import { cellPlace } from './tile-client'

// The card a person has opened over the board, and what stays open on a ticket as it changes.
export class OpenCardClient {
  constructor(private readonly page: BoardPage) {}

  private get store(): BoardPage['store'] {
    return this.page.store
  }

  // A card opens with its tiles only; each tile opens its own action bar when hovered or pressed.
  toggle(ticket: TicketClient): void {
    ticket.select()
    if (this.store.state.openCard === ticket.name) return this.closeCard()
    this.store.change({ openCard: ticket.name, tile: null })
  }

  private closeCard(): void {
    this.store.change(state => ({ openCard: null, tile: state.tile?.ticket === state.openCard ? null : state.tile }))
  }

  // A press on a segment opens the card on that fidelity.
  async openSegment(ticket: TicketClient, stage: ColumnClient, slug: string): Promise<void> {
    if (this.store.state.openCard !== ticket.name) this.toggle(ticket)
    await this.page.tiles.open({ ticket: ticket.name, stage, place: cellPlace(stage.name, slug), slugs: [slug] }, true)
  }

  // A ticket's address changes with its column, so the selection and an open bar go with it, to the tile the ticket
  // works on next.
  async follow(moved: TicketClient): Promise<void> {
    moved.select()
    const stage = this.page.board.stageOf(moved)
    if (!stage) return
    if (this.store.state.tile?.ticket === moved.name) await this.followBar(moved, stage)
  }

  private async followBar(moved: TicketClient, stage: ColumnClient): Promise<void> {
    const slugs = moved.enabledSlugs(stage)
    const slug = slugs.find(entry => moved.stateOf(entry).key !== 'done') ?? slugs[0]
    if (slug) await this.page.tiles.open({ ticket: moved.name, stage, place: cellPlace(stage.name, slug), slugs: [slug] }, true)
    else this.page.tiles.close()
  }

  releaseTicket(ticket: string): void {
    this.store.change(state => ({
      openCard: state.openCard === ticket ? null : state.openCard,
      tile: state.tile?.ticket === ticket ? null : state.tile,
    }))
  }

  // A practice turned off has no tile to act on, so an open bar lets go of it.
  dropPractice(ticket: string, practice: string): void {
    const remaining = (tile: Tile | null): Tile | null => {
      if (tile?.ticket !== ticket) return tile
      const slugs = tile.slugs.filter(slug => practiceOf(slug)?.key !== practice)
      return slugs.length ? { ...tile, slugs } : null
    }
    this.store.change(state => ({ tile: remaining(state.tile) }))
  }
}
