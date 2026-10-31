export type TicketJson = {
  name: string
  title: string
  scope: string
  parent: string
  column: string
  is_done: boolean
  next: string | null
  last_activity: string
  handoff: string
  reports?: Record<string, string>
  progress: Record<string, string>
}

export type BacklogItemJson = { title: string; path: string; last_activity: string }

export type ColumnJson = {
  name: string
  items?: BacklogItemJson[]
  tickets?: TicketJson[]
  work_required?: string[]
  in_progress?: TicketJson[]
  done?: TicketJson[]
}

export type BoardJson = { project: string; active: string | null; columns: ColumnJson[] }

export type TicketCardJson = {
  address: string
  name: string
  canMovePrevious: boolean
  canMoveNext: boolean
  title: string
  meta: string
  segments: { scope: string; color: string; skill: string }[]
  tail: { text: string; color: string } | null
  borderColor: string
  hoverColor: string
  backgroundColor: string
  titleColor: string
  mutedColor: string
}

export type SplitGripJson = { boardRows: number; color: string; hoverColor: string }

export type SplitLayoutJson = { expanded: 'board' | 'details' | null; boardRows: number | null }

declare module 'claude-code' {
  interface PluginState {
    'cdd-board': {
      board: Shaped<BoardJson | null>
      selected: string | null
      splitLayout: SplitLayoutJson
      surfaceModulesFailed: boolean
    }
  }
}
