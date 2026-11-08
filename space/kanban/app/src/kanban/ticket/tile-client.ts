import type { FidelityGuidanceData } from '@cdd/space/kanban/board'
import type { FormatChoiceData } from '@cdd/space/kanban/ticket'

import type { BoardPage } from '../board/board-page'
import type { Tile } from '../board/board-store'
import type { ColumnClient } from '../board/column-client'
import type { TicketClient } from './ticket-client'
import { startingPicks } from './tile-formats'

const DEFAULT_ACTION = 'generate'
const HOVER_OPEN_MILLISECONDS = 500
const HOVER_CLOSE_MILLISECONDS = 250

export const cellPlace = (stage: string, fidelity: FidelityGuidanceData): string => `cell-${stage}-${fidelity.slug}`
export const headPlace = (stage: string): string => `head-${stage}`

// A command names each fidelity it acts on by its slug.
export const slugsOf = (fidelities: FidelityGuidanceData[]): string[] => fidelities.map(fidelity => fidelity.slug)

// Where a bar opens: on which ticket, in which stage, at which place, over which fidelities.
export type TileSpot = { ticket: TicketClient; stage: ColumnClient; place: string; fidelities: FidelityGuidanceData[] }

// A bar is found by its ticket's name and its place, because each board read makes new ticket clients.
export const isAt = (tile: Tile, ticket: string, place: string): boolean => tile.ticket.name === ticket && tile.place === place

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


  // The bar shows at once and its format chips fill in when Python has read the fidelities' files, because reading them
  // can take a second. Only the latest open of a place takes the chips, so a slow read from an earlier open cannot
  // change the bar shown now.
  async open(spot: TileSpot, isPinned: boolean): Promise<void> {
    const { ticket, stage, place, fidelities } = spot
    const order = ++this.opening
    this.latestOpening.set(`${ticket.name} ${place}`, order)
    const shown: Tile = { ticket, place, stage, fidelities, action: DEFAULT_ACTION, picked: [], isPinned, choices: [] }
    this.store.change(state => ({ tiles: [...this.othersKept(state.tiles, shown), shown] }))
    const choices = (await ticket.formatChoices(slugsOf(fidelities))) ?? []
    if (this.latestOpening.get(`${ticket.name} ${place}`) !== order) return
    this.change(ticket.name, place, tile => this.withChoices(tile, shown, choices))
  }

  // A bar a hover opens replaces any other bar a hover opened; pressed bars stay.
  private othersKept(tiles: Tile[], shown: Tile): Tile[] {
    const others = tiles.filter(tile => !isAt(tile, shown.ticket.name, shown.place))
    return shown.isPinned ? others : others.filter(tile => tile.isPinned)
  }

  // A person's own choice of formats stays; until they make one, the bar starts on the chips Python picks.
  private withChoices(tile: Tile, shown: Tile, choices: FormatChoiceData[]): Tile {
    return { ...tile, choices, picked: tile.picked === shown.picked ? startingPicks(choices) : tile.picked }
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
    if (this.isOpen(spot.ticket.name, spot.place)) return
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
    await Promise.all(this.store.state.tiles.map(tile => this.reloadChoices(tile)))
  }

  private async reloadChoices(tile: Tile): Promise<void> {
    const choices = await tile.ticket.formatChoices(slugsOf(tile.fidelities))
    if (choices) this.change(tile.ticket.name, tile.place, open => ({ ...open, choices }))
  }
}
