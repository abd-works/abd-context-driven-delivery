import type { RequiredFidelity } from '../board/column-client'

import type { BoardPage } from '../board/board-page'
import type { Tile } from '../shared/board-store'
import type { ColumnClient } from '../board/column-client'
import type { TicketClient } from './ticket-client'
import { cellPlace } from './tile-client'

const withoutBarsOf = (tiles: Tile[], ticket: string | null): Tile[] => tiles.filter(tile => tile.ticket.name !== ticket)

// The card a person has opened over the board, and what stays open on a ticket as it changes.
export class OpenCardClient {
  constructor(private readonly page: BoardPage) {}

  private get store(): BoardPage['store'] {
    return this.page.store
  }

  // A card opens with its tiles only; each tile opens its own action bar when hovered or pressed. The card it replaces
  // takes its bars with it.
  toggle(ticket: TicketClient): void {
    ticket.choose()
    if (this.store.state.openCard === ticket.name) return this.closeCard()
    this.store.change(state => ({ openCard: ticket.name, tiles: withoutBarsOf(withoutBarsOf(state.tiles, state.openCard), ticket.name) }))
  }

  // A press on an empty area of a card chooses its ticket and opens its card; pressing again leaves it open.
  open(ticket: TicketClient): void {
    if (this.store.state.openCard !== ticket.name) return this.toggle(ticket)
    ticket.choose()
  }

  // A parent shows its child rows until a person folds it to its own card.
  showsChildrenOf(parent: TicketClient): boolean {
    return !this.store.state.foldedParents.includes(parent.name)
  }

  toggleChildrenOf(parent: TicketClient): void {
    const folded = this.store.state.foldedParents.filter(name => name !== parent.name)
    this.store.change({ foldedParents: this.showsChildrenOf(parent) ? [...folded, parent.name] : folded })
  }

  private closeCard(): void {
    this.store.change(state => ({ openCard: null, tiles: withoutBarsOf(state.tiles, state.openCard) }))
  }

  // A press on a segment opens the card on that fidelity.
  async openSegment(ticket: TicketClient, stage: ColumnClient, fidelity: RequiredFidelity): Promise<void> {
    if (this.store.state.openCard !== ticket.name) this.toggle(ticket)
    await this.page.tiles.open({ ticket, stage, place: cellPlace(stage.name, fidelity), fidelities: [fidelity] }, true)
  }

  // A ticket's address changes with its column, so the selection goes with it, and its open bars give way to one bar
  // on the tile the ticket works on next.
  async follow(moved: TicketClient): Promise<void> {
    moved.select()
    const stage = this.page.board.stageOf(moved)
    if (!stage) return
    if (this.store.state.tiles.some(tile => tile.ticket.name === moved.name)) await this.followBars(moved, stage)
  }

  // The bar opens on the fidelity Python names as the ticket's next, in its own stage; a ticket done in its stage has
  // none, so the bar opens on the stage's first fidelity.
  private async followBars(moved: TicketClient, stage: ColumnClient): Promise<void> {
    this.store.change(state => ({ tiles: withoutBarsOf(state.tiles, moved.name) }))
    const next = moved.nextProgress
    const shown = (next && this.page.board.stageNamed(next.stage.name)) ?? stage
    const fidelity = next?.fidelity ?? moved.progressIn(stage)[0]?.fidelity
    if (fidelity) await this.page.tiles.open({ ticket: moved, stage: shown, place: cellPlace(shown.name, fidelity), fidelities: [fidelity] }, true)
  }

  releaseTicket(ticket: string): void {
    this.store.change(state => ({
      openCard: state.openCard === ticket ? null : state.openCard,
      tiles: withoutBarsOf(state.tiles, ticket),
    }))
  }

  // A practice turned off has no tile to act on, so each open bar on the ticket lets go of it.
  dropPractice(ticket: string, practice: string): void {
    const remaining = (tile: Tile): Tile | null => {
      if (tile.ticket.name !== ticket) return tile
      const fidelities = tile.fidelities.filter(fidelity => this.page.board.fidelityShown(fidelity.slug)?.practice.key !== practice)
      return fidelities.length ? { ...tile, fidelities } : null
    }
    this.store.change(state => ({ tiles: state.tiles.map(remaining).filter((tile): tile is Tile => tile !== null) }))
  }
}
