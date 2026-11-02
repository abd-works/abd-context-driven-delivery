import type { BoardData, HelpData } from '@cdd/harness/kanban/board'

import type { Chat } from '../chat/chat'
import type { ReportClient } from '../ticket/report-client'
import type { TicketFiles } from '../ticket/ticket'
import type { WorkspaceClient } from '../ticket/workspace-client'

export type Toast = { id: number; text: string; isFailure: boolean }
export type Region = 'board' | 'details'
export type BacklogDraft = { isOpen: boolean; title: string; text: string }

// An open action bar: on a tile, on a stage head, or across a whole opened card.
export type Tile = { ticket: string; place: string; stage: string; slugs: string[]; action: string; picked: string[]; isPinned: boolean; files: TicketFiles }

export type Activation = {
  ticket: string
  title: string
  isClosing: boolean
  leavingTitle: string
  leaving: string[]
  opening: string[]
  workspace: WorkspaceClient
}

export type ReportPanel = { kind: 'report'; ticket: string; fidelity: string; report: ReportClient; closedRules: string[]; isExpanded: boolean }
export type FilesPanel = {
  kind: 'files'
  ticket: string
  slugs: string[]
  files: TicketFiles
  mode: string
  tabs: string[]
  activeTab: string
  texts: Record<string, string>
  lines: Record<string, number>
  isExpanded: boolean
}
export type HelpPanel = { kind: 'help'; help: HelpData; isExpanded: boolean }
export type SidePanel = ReportPanel | FilesPanel | HelpPanel

export type BoardState = {
  board: BoardData | null
  serverFailure: string | null
  now: number
  selected: string | null
  openCard: string | null
  tile: Tile | null
  cardMenu: Tile | null
  activation: Activation | null
  draft: BacklogDraft
  panels: SidePanel[]
  panelWidths: Record<string, number>
  expandedRegion: Region | null
  boardHeight: number
  onlyActive: boolean
  hidesDisabled: boolean
  editingLimit: string | null
  toasts: Toast[]
  chats: Chat[]
  targetChat: string | null
}

export const EMPTY_DRAFT: BacklogDraft = { isOpen: false, title: '', text: '' }
const DEFAULT_BOARD_HEIGHT = 470
const TOAST_MILLISECONDS = 3200
const FAILURE_TOAST_MILLISECONDS = 6000
const SAVED_KEY = 'cdd-session-board'

type SavedLayout = Pick<BoardState, 'boardHeight' | 'panelWidths' | 'hidesDisabled'>

const initialState = (): BoardState => ({
  board: null,
  serverFailure: null,
  now: Date.now(),
  selected: null,
  openCard: null,
  tile: null,
  cardMenu: null,
  activation: null,
  draft: EMPTY_DRAFT,
  panels: [],
  panelWidths: {},
  expandedRegion: null,
  boardHeight: DEFAULT_BOARD_HEIGHT,
  onlyActive: true,
  hidesDisabled: false,
  editingLimit: null,
  toasts: [],
  chats: [],
  targetChat: null,
})

// Only conveniences are saved. Browser storage can be blocked or empty, and the page works the same without it.
function savedLayout(): Partial<SavedLayout> {
  try {
    return JSON.parse(globalThis.localStorage?.getItem(SAVED_KEY) ?? '{}') as Partial<SavedLayout>
  } catch {
    return {}
  }
}

function saveLayout({ boardHeight, panelWidths, hidesDisabled }: BoardState): void {
  try {
    globalThis.localStorage?.setItem(SAVED_KEY, JSON.stringify({ boardHeight, panelWidths, hidesDisabled }))
  } catch {
    // The layout simply is not remembered in this browser.
  }
}

// The page's memory: React reads it through useSyncExternalStore, and the clients read and change it between awaits.
export class BoardStore {
  state: BoardState = { ...initialState(), ...savedLayout() }
  private readonly listeners = new Set<() => void>()
  private nextToast = 1

  readonly subscribe = (listener: () => void): (() => void) => {
    this.listeners.add(listener)
    return () => this.listeners.delete(listener)
  }

  readonly read = (): BoardState => this.state

  change(change: Partial<BoardState> | ((state: BoardState) => Partial<BoardState>)): void {
    this.state = { ...this.state, ...(typeof change === 'function' ? change(this.state) : change) }
    saveLayout(this.state)
    for (const listener of this.listeners) listener()
  }

  toast(text: string, isFailure = false): void {
    if (this.state.toasts.some(toast => toast.text === text)) return
    const id = this.nextToast++
    this.change(state => ({ toasts: [...state.toasts, { id, text, isFailure }] }))
    setTimeout(() => this.dismissToast(id), isFailure ? FAILURE_TOAST_MILLISECONDS : TOAST_MILLISECONDS)
  }

  private dismissToast(shown: number): void {
    this.change(state => ({ toasts: state.toasts.filter(toast => toast.id !== shown) }))
  }
}
