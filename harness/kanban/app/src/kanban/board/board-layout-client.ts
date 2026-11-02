import type { BoardStore, Region } from './board-store'

const MINIMUM_REGION = 160
const ROOM_OVER_REGIONS = 90

// How a person has arranged the page. None of it reaches cdd.
export class BoardLayoutClient {
  constructor(private readonly store: BoardStore) {}

  toggleRegion(region: Region): void {
    this.store.change(state => ({ expandedRegion: state.expandedRegion === region ? null : region }))
  }

  // Neither the board nor the details can be dragged shut, whatever height the page has.
  setBoardHeight(wanted: number, pageHeight: number): void {
    const largest = Math.max(pageHeight - ROOM_OVER_REGIONS - MINIMUM_REGION, MINIMUM_REGION)
    this.store.change({ boardHeight: Math.min(Math.max(wanted, MINIMUM_REGION), largest) })
  }

  toggleOnlyActive(): void {
    this.store.change(state => ({ onlyActive: !state.onlyActive }))
  }

  toggleHiddenPractices(): void {
    this.store.change(state => ({ hidesDisabled: !state.hidesDisabled }))
  }

  editLimit(stage: string): void {
    this.store.change({ editingLimit: stage })
  }

  cancelLimit(): void {
    this.store.change({ editingLimit: null })
  }
}
