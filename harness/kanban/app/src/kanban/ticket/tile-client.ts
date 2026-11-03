import { TicketClientGenerated } from '@cdd/harness/kanban/ticket'

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

export const isAt = (tile: Tile, ticket: string, place: string): boolean => tile.ticket === ticket && tile.place === place

// Which action bars are open. A press keeps a bar open, and several can be kept at once; a hover only looks, so it
// opens one bar that is not kept and closes it again when the pointer leaves.
export class TileClient {
  private hoverOpenTimer: ReturnType<typeof setTimeout> | undefined
  private hoverCloseTimer: ReturnType<typeof setTimeout> | undefined
  private opening = 0
  private readonly latestOpening = new Map<string, number>()

  constructor(private readonly page: BoardPage) {}

  private get store(): BoardPage['store'] {
    return this.page.store
  }

  private readFiles(ticket: string, slugs: string[]): Promise<TicketFiles | null> {
    return TicketClientGenerated.named(this.page.api, ticket).files(slugs)
  }

  // The bar shows at once and its files fill in when they are read, because reading them can take a second. Only the
  // latest open of a place takes the files, so a slow read from an earlier open cannot change the bar shown now.
  async open(spot: TileSpot, isPinned: boolean): Promise<void> {
    const { ticket, stage, place, slugs } = spot
    const order = ++this.opening
    this.latestOpening.set(`${ticket} ${place}`, order)
    const shown: Tile = { ticket, place, stage: stage.name, slugs, action: DEFAULT_ACTION, picked: defaultPicks(stage, slugs, {}), isPinned, files: {} }
    this.store.change(state => ({ tiles: [...this.othersKept(state.tiles, shown), shown] }))
    const files = (await this.readFiles(ticket, slugs)) ?? {}
    if (this.latestOpening.get(`${ticket} ${place}`) !== order) return
    this.change(ticket, place, tile => this.withFiles(tile, shown, files, stage))
  }

  // A bar a hover opens replaces any other bar a hover opened; pressed bars stay.
  private othersKept(tiles: Tile[], shown: Tile): Tile[] {
    const others = tiles.filter(tile => !isAt(tile, shown.ticket, shown.place))
    return shown.isPinned ? others : others.filter(tile => tile.isPinned)
  }

  // A person's own choice of formats stays; until they make one, the defaults follow what is already generated.
  private withFiles(tile: Tile, shown: Tile, files: TicketFiles, stage: ColumnClient): Tile {
    return { ...tile, files, picked: tile.picked === shown.picked ? defaultPicks(stage, tile.slugs, files) : tile.picked }
  }

  // Changes the one open bar on that ticket at that place, and leaves every other bar as it is.
  change(ticket: string, place: string, changed: (tile: Tile) => Tile): void {
    this.store.change(state => ({ tiles: state.tiles.map(tile => (isAt(tile, ticket, place) ? changed(tile) : tile)) }))
  }

  openOn(ticket: string, place: string): Tile | undefined {
    return this.store.state.tiles.find(tile => isAt(tile, ticket, place))
  }

  isOpen(ticket: string, place: string): boolean {
    return this.openOn(ticket, place) !== undefined
  }

  close(ticket: string, place: string): void {
    this.store.change(state => ({ tiles: state.tiles.filter(tile => !isAt(tile, ticket, place)) }))
  }

  pin(ticket: string, place: string): void {
    this.change(ticket, place, tile => ({ ...tile, isPinned: true }))
  }

  // The first press on a tile a hover opened keeps it open; the next closes it.
  async toggle(ticket: TicketClient, spot: TileSpot): Promise<void> {
    clearTimeout(this.hoverOpenTimer)
    ticket.select()
    const open = this.openOn(ticket.name, spot.place)
    if (!open) return this.open(spot, true)
    if (open.isPinned) this.close(ticket.name, spot.place)
    else this.pin(ticket.name, spot.place)
  }

  // A hover only looks, so it leaves every bar a person pressed open.
  hoverIn(spot: TileSpot): void {
    clearTimeout(this.hoverOpenTimer)
    clearTimeout(this.hoverCloseTimer)
    if (this.isOpen(spot.ticket, spot.place)) return
    this.hoverOpenTimer = setTimeout(() => void this.open(spot, false), HOVER_OPEN_MILLISECONDS)
  }

  hoverOut(ticket: string, place: string): void {
    clearTimeout(this.hoverOpenTimer)
    clearTimeout(this.hoverCloseTimer)
    this.hoverCloseTimer = setTimeout(() => {
      if (this.openOn(ticket, place)?.isPinned === false) this.close(ticket, place)
    }, HOVER_CLOSE_MILLISECONDS)
  }

  // What a bar shows was generated can change under it, so every open bar is read again with the board.
  async reload(): Promise<void> {
    await Promise.all(this.store.state.tiles.map(tile => this.reloadFiles(tile)))
  }

  private async reloadFiles(tile: Tile): Promise<void> {
    const files = await this.readFiles(tile.ticket, tile.slugs)
    if (files) this.change(tile.ticket, tile.place, open => ({ ...open, files }))
  }
}
