import { practiceOf } from '../board/board-brand'
import type { BoardPage } from '../board/board-page'
import type { Tile } from '../board/board-store'
import type { ColumnClient } from '../board/column-client'
import type { TicketClient } from './ticket-client'
import { cellPlace } from './tile-client'

// The opened card's bar over all its fidelities stays up while the tiles below it open and close, so it is kept apart.
export const CARD_MENU = 'menu'

// The card a person has opened over the board, and what stays open on a ticket as it changes.
export class OpenCardClient {
  constructor(private readonly page: BoardPage) {}

  private get store(): BoardPage['store'] {
    return this.page.store
  }

  // A card opens with its action bar ready, over all its fidelities, so generating needs no hover first.
  async toggle(ticket: TicketClient, stage: ColumnClient): Promise<void> {
    ticket.select()
    if (this.store.state.openCard === ticket.name) return this.closeCard()
    this.store.change({ openCard: ticket.name, cardMenu: null, tile: null })
    await this.openBar(ticket, stage)
  }

  private closeCard(): void {
    this.store.change(state => ({ openCard: null, cardMenu: null, tile: state.tile?.ticket === state.openCard ? null : state.tile }))
  }

  private async openBar(ticket: TicketClient, stage: ColumnClient): Promise<void> {
    const slugs = ticket.enabledSlugs(stage)
    if (slugs.length === 1) return this.page.tiles.open({ ticket: ticket.name, stage, place: cellPlace(stage.name, slugs[0]!), slugs }, true)
    if (!slugs.length) return
    const cardMenu = await this.page.tiles.started({ ticket: ticket.name, stage, place: CARD_MENU, slugs }, true)
    if (this.store.state.openCard === ticket.name) this.store.change({ cardMenu })
  }

  // A press on a segment opens the card on that fidelity.
  async openSegment(ticket: TicketClient, stage: ColumnClient, slug: string): Promise<void> {
    if (this.store.state.openCard !== ticket.name) await this.toggle(ticket, stage)
    await this.page.tiles.open({ ticket: ticket.name, stage, place: cellPlace(stage.name, slug), slugs: [slug] }, true)
  }

  // A ticket's address changes with its column, so the selection and an open bar go with it: the bar to the tile the
  // ticket works on next, and an opened card's bar to the fidelities of its new stage.
  async follow(moved: TicketClient): Promise<void> {
    moved.select()
    const stage = this.page.board.stageOf(moved)
    if (!stage) return
    const { tile, cardMenu } = this.store.state
    if (tile?.ticket === moved.name) await this.followBar(moved, stage)
    if (cardMenu?.ticket === moved.name) await this.openBar(moved, stage)
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
      cardMenu: state.cardMenu?.ticket === ticket ? null : state.cardMenu,
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
    this.store.change(state => ({ tile: remaining(state.tile), cardMenu: remaining(state.cardMenu) }))
  }
}
