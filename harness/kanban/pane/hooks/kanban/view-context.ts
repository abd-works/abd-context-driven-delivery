import type { ElementTable } from 'claude-code'

import type { ActivationJson, BacklogDraftJson, RegionOffsetsJson, SidePanelJson, SplitLayoutJson, TileJson } from '../../types'
import type { BoardClient } from './board-client'

// What one drawing of the pane reads, gathered once, so each view takes it whole.
export type ViewContext = {
  elements: ElementTable
  board: BoardClient
  address: string | null
  now: number
  bodyColumns: number
  bodyRows: number
  hasSurfaceModules: boolean
  hasPictures: boolean
  hasInputs: boolean
  onlyActive: boolean
  openCard: string | null
  tile: TileJson | null
  activation: ActivationJson | null
  draft: BacklogDraftJson
  panels: SidePanelJson[]
  columnOffset: number
  editingLimit: string | null
  hidesDisabled: boolean
  serverFailure: string | null
  cardOffset: number
  regionOffsets: RegionOffsetsJson
  layout: SplitLayoutJson
}

const MINUTE = 60_000
const MINUTES_PER_HOUR = 60
const HOURS_PER_DAY = 24

export const ageOf = (now: number, stamp: string): string => {
  if (!stamp) return 'no activity yet'
  const minutes = Math.floor((now - Date.parse(stamp)) / MINUTE)
  if (minutes < 1) return 'just now'
  if (minutes < MINUTES_PER_HOUR) return `${minutes} min ago`
  const hours = Math.floor(minutes / MINUTES_PER_HOUR)
  if (hours < HOURS_PER_DAY) return `${hours} hours ago`
  const days = Math.floor(hours / HOURS_PER_DAY)
  return days === 1 ? 'yesterday' : `${days} days ago`
}

const SMALLEST_MAIN_COLUMNS = 40

const totalOf = (widths: number[]): number => widths.reduce((total, width) => total + width, 0)

const fitted = (widths: number[], room: number): number[] => {
  const total = totalOf(widths)
  return total <= room ? widths : widths.map(width => Math.max(Math.floor((width * room) / total), 1))
}

// Each open panel's width: they share what the board must keep, and an expanded panel takes what the others leave.
export function panelWidthsOf({ bodyColumns, panels }: ViewContext): number[] {
  const room = Math.max(bodyColumns - SMALLEST_MAIN_COLUMNS, 1)
  const expanded = panels.find(panel => panel.isExpanded)
  const others = panels.filter(panel => panel !== expanded)
  const widths = fitted(others.map(panel => panel.width), room)
  const shared = new Map(others.map((panel, index) => [panel.kind, widths[index] ?? 0]))
  return panels.map(panel => shared.get(panel.kind) ?? bodyColumns - totalOf(widths))
}

// What the panels leave for the board and the details.
export const mainColumnsOf = (view: ViewContext): number => Math.max(view.bodyColumns - totalOf(panelWidthsOf(view)), 0)

// Commands run in the active session, so with Active session only on, a ticket that is not active cannot start one.
export const isLocked = ({ onlyActive, board }: ViewContext, ticket: string): boolean => onlyActive && ticket !== board.active
