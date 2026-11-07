import type { FidelityGuidanceData } from '@cdd/space/kanban/board'

import type { BoardPage } from '../board/board-page'
import type { Tile } from '../board/board-store'
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
    ticket.select()
    if (this.store.state.openCard === ticket.name) return this.closeCard()
    this.store.change(state => ({ openCard: ticket.name, tiles: withoutBarsOf(withoutBarsOf(state.tiles, state.openCard), ticket.name) }))
  }

  private closeCard(): void {
    this.store.change(state => ({ openCard: null, tiles: withoutBarsOf(state.tiles, state.openCard) }))
  }

  // A press on a segment opens the card on that fidelity.
  async openSegment(ticket: TicketClient, stage: ColumnClient, fidelity: FidelityGuidanceData): Promise<void> {
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

  private async followBars(moved: TicketClient, stage: ColumnClient): Promise<void> {
    this.store.change(state => ({ tiles: withoutBarsOf(state.tiles, moved.name) }))
    const progress = moved.progressIn(stage)
    const fidelity = (progress.find(entry => entry.state !== 'done') ?? progress[0])?.fidelity
    if (fidelity) await this.page.tiles.open({ ticket: moved, stage, place: cellPlace(stage.name, fidelity), fidelities: [fidelity] }, true)
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
      const fidelities = tile.fidelities.filter(fidelity => this.page.board.practiceOf(fidelity.slug)?.key !== practice)
      return fidelities.length ? { ...tile, fidelities } : null
    }
    this.store.change(state => ({ tiles: state.tiles.map(remaining).filter((tile): tile is Tile => tile !== null) }))
  }
}
