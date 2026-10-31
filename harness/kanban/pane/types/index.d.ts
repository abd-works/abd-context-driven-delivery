export type TicketJson = {
  name: string
  title: string
  scope: string
  parent: string
  column: string
  is_done: boolean
  next: string | null
  last_activity: string
  progress: Record<string, string>
}

export type ColumnJson = {
  name: string
  items?: { title: string; path: string }[]
  tickets?: TicketJson[]
  work_required?: string[]
  in_progress?: TicketJson[]
  done?: TicketJson[]
}

export type BoardJson = { active: string | null; columns: ColumnJson[] }

declare module 'claude-code' {
  interface PluginState {
    'cdd-board': { board: Shaped<BoardJson | null>; selected: string | null }
  }
}
