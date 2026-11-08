import type { BacklogItemData } from '@cdd/space/kanban/backlog-item'
import type { BoardData, FidelityGuidanceData, HelpData } from '@cdd/space/kanban/board'
import type { FormatChoiceData } from '@cdd/space/kanban/ticket'

import type { ChatData, ChatMessageData } from '@cdd/harness/chat/chat'
import type { FidelityProgressClient } from '../ticket/fidelity-progress-client'
import type { ReportClient } from '../ticket/report-client'
import type { ColumnClient } from './column-client'
import type { FilesByFidelity, TicketClient } from '../ticket/ticket-client'

export type Toast = { id: number; text: string; isFailure: boolean }
export type Region = 'board' | 'details'
export type BacklogDraft = { isOpen: boolean; title: string; text: string }

// An open action bar: on a tile or on a stage head. One ticket and place hold at most one bar, and the bar holds its
// ticket, whose tools its controls call, its stage, and the fidelities it acts on, whose progress is read from the
// ticket as the board shows it now.
export type Tile = { ticket: TicketClient; place: string; stage: ColumnClient; fidelities: FidelityGuidanceData[]; action: string; picked: string[]; isPinned: boolean; choices: FormatChoiceData[] }

// A dialog or panel holds the ticket it is about, so its actions reach that ticket's tools without looking it up again.
export type Activation = {
  ticket: TicketClient
  isClosing: boolean
  leavingTitle: string
  // What a person has ticked, starting from what Python chooses at first.
  leaving: string[]
  opening: string[]
  // What the dialog offers: on leaving, what the ticket left can do with its work now; on opening, what the ticket does
  // not have yet. The branch the work left is on, empty while nothing checked out is its own, and whether the ticket
  // opened has its own branch.
  offeredLeaving: string[]
  offeredOpening: string[]
  leavingBranch: string
  hasBranch: boolean
}

// The roots dialog: the ticket's workpath on top and each practice's practice root under it. Starting a backlog item asks for its workpath
// first, so until it starts there is no ticket yet, only the item.
export type RootChoice = {
  ticket: TicketClient | null
  startingItem: BacklogItemData | null
  browsing: { target: string; path: string; folders: string[] } | null
}

// A report panel holds the progress whose report it shows, or none for the violations of every fidelity of its ticket.
export type ReportPanel = { kind: 'report'; ticket: TicketClient; progress: FidelityProgressClient | null; report: ReportClient; closedRules: string[]; isExpanded: boolean }
export type FilesPanel = {
  kind: 'files'
  ticket: TicketClient
  // A session folder's files, or the files of the fidelities whose progress it holds.
  isSession: boolean
  progress: FidelityProgressClient[]
  files: FilesByFidelity
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
  dragged: string | null
  tiles: Tile[]
  activation: Activation | null
  rootChoice: RootChoice | null
  draft: BacklogDraft
  panels: SidePanel[]
  panelWidths: Record<string, number>
  expandedRegion: Region | null
  boardHeight: number
  onlyActive: boolean
  hidesDisabled: boolean
  editingLimit: string | null
  toasts: Toast[]
  chats: ChatData[]
  targetChat: string | null
  // The chat a person chose, kept while it is away so it is chosen again when it reconnects.
  pickedChat: string | null
  // When each ticket's new chat was opened, by ticket name, so a person clicking again does not open a second one.
  startingChats: Record<string, number>
  // The latest messages sent to the target chat, newest first, and whether the list of them is open.
  messages: ChatMessageData[]
  isMessagesOpen: boolean
  // The server serves a newer build than the page was loaded from.
  isNewBuild: boolean
  // An update is getting the latest code, rebuilding, and re-pinning cdd, which takes a while; one press at a time.
  isUpdating: boolean
}

export const EMPTY_DRAFT: BacklogDraft = { isOpen: false, title: '', text: '' }
const DEFAULT_BOARD_HEIGHT = 470
const TOAST_MILLISECONDS = 3200
const FAILURE_TOAST_MILLISECONDS = 6000
const SAVED_KEY = 'cdd-session-board'

type SavedLayout = Pick<BoardState, 'boardHeight' | 'panelWidths' | 'hidesDisabled' | 'pickedChat'>

const initialState = (): BoardState => ({
  board: null,
  serverFailure: null,
  now: Date.now(),
  selected: null,
  openCard: null,
  dragged: null,
  tiles: [],
  activation: null,
  rootChoice: null,
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
  pickedChat: null,
  startingChats: {},
  messages: [],
  isMessagesOpen: false,
  isNewBuild: false,
  isUpdating: false,
})

// Only conveniences are saved. Browser storage can be blocked or empty, and the page works the same without it.
function savedLayout(): Partial<SavedLayout> {
  try {
    return JSON.parse(globalThis.localStorage?.getItem(SAVED_KEY) ?? '{}') as Partial<SavedLayout>
  } catch {
    return {}
  }
}

function saveLayout({ boardHeight, panelWidths, hidesDisabled, pickedChat }: BoardState): void {
  try {
    globalThis.localStorage?.setItem(SAVED_KEY, JSON.stringify({ boardHeight, panelWidths, hidesDisabled, pickedChat }))
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
