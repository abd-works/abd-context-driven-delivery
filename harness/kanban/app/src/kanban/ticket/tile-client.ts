import { pathPart } from '../board/board-api'
import type { BoardPage } from '../board/board-page'
import type { Tile } from '../board/board-store'
import type { ColumnClient } from '../board/column-client'
import type { TicketFiles } from './ticket'
import type { TicketClient } from './ticket-client'
import { defaultPicks } from './tile-formats'

const DEFAULT_ACTION = 'generate'
const HOVER_OPEN_MILLISECONDS = 500
const HOVER_CLOSE_MILLISECONDS = 250

export const cellPlace = (stage: string, slug: string): string => `cell-${stage}-${slug}`
export const headPlace = (stage: string): string => `head-${stage}`

// Where a bar opens: on which ticket, in which stage, at which place, over which fidelities.
export type TileSpot = { ticket: string; stage: ColumnClient; place: string; slugs: string[] }

// Which action bar is open. A hover only looks, and a press keeps it.
export class TileClient {
  private hoverOpenTimer: ReturnType<typeof setTimeout> | undefined
  private hoverCloseTimer: ReturnType<typeof setTimeout> | undefined
  private opening = 0

  constructor(private readonly page: BoardPage) {}

  private get store(): BoardPage['store'] {
    return this.page.store
  }

  private readFiles(ticket: string, slugs: string[]): Promise<TicketFiles | null> {
    return this.page.api.post<TicketFiles>(`/tickets/${pathPart(ticket)}/files`, { fidelities: slugs })
  }

  async started(spot: TileSpot, isPinned: boolean): Promise<Tile> {
    const { ticket, stage, place, slugs } = spot
    const files = (await this.readFiles(ticket, slugs)) ?? {}
    return { ticket, place, stage: stage.name, slugs, action: DEFAULT_ACTION, picked: defaultPicks(stage, slugs, files), isPinned, files }
  }

  // Only the latest open wins, so a slow read for a tile the pointer has left cannot replace the one under it.
  async open(spot: TileSpot, isPinned: boolean): Promise<void> {
    const order = ++this.opening
    const tile = await this.started(spot, isPinned)
    if (order === this.opening) this.store.change({ tile })
  }

  isOpen(ticket: string, place: string): boolean {
    const { tile } = this.store.state
    return tile?.ticket === ticket && tile.place === place
  }

  close(): void {
    this.store.change({ tile: null })
  }

  pin(): void {
    this.store.change(state => ({ tile: state.tile ? { ...state.tile, isPinned: true } : null }))
  }

  // The first press on a tile a hover opened keeps it open; the next closes it.
  async toggle(ticket: TicketClient, spot: TileSpot): Promise<void> {
    clearTimeout(this.hoverOpenTimer)
    ticket.select()
    if (!this.isOpen(ticket.name, spot.place)) return this.open(spot, true)
    if (this.store.state.tile?.isPinned) this.close()
    else this.pin()
  }

  // A hover only looks, so it leaves a bar a person pressed open.
  hoverIn(spot: TileSpot): void {
    clearTimeout(this.hoverOpenTimer)
    clearTimeout(this.hoverCloseTimer)
    if (this.isOpen(spot.ticket, spot.place) || this.store.state.tile?.isPinned) return
    this.hoverOpenTimer = setTimeout(() => void this.open(spot, false), HOVER_OPEN_MILLISECONDS)
  }

  hoverOut(place: string): void {
    clearTimeout(this.hoverOpenTimer)
    clearTimeout(this.hoverCloseTimer)
    this.hoverCloseTimer = setTimeout(() => {
      const { tile } = this.store.state
      if (tile?.place === place && !tile.isPinned) this.close()
    }, HOVER_CLOSE_MILLISECONDS)
  }

  // What a bar shows was generated can change under it, so it is read again with the board.
  async reload(): Promise<void> {
    const { tile, cardMenu } = this.store.state
    if (tile) await this.reloadFiles(tile, files => this.store.change(state => ({ tile: state.tile?.place === tile.place ? { ...state.tile, files } : state.tile })))
    if (cardMenu) await this.reloadFiles(cardMenu, files => this.store.change(state => ({ cardMenu: state.cardMenu ? { ...state.cardMenu, files } : null })))
  }

  private async reloadFiles(tile: Tile, keep: (files: TicketFiles) => void): Promise<void> {
    const files = await this.readFiles(tile.ticket, tile.slugs)
    if (files) keep(files)
  }
}
