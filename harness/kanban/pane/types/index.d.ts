// These types are exactly what the Python to_json() operations and MCP tools return, plus what the pane keeps for itself.
export type ActionStatesJson = { generate: string; validate: string; review: string }

export type TicketJson = {
  name: string
  title: string
  scope: string
  parent: string
  column: string
  is_done: boolean
  can_move_next: boolean
  next: string | null
  next_action: string
  last_activity: string
  handoff: string
  reports: Record<string, string>
  practices: Record<string, boolean>
  progress: Record<string, string>
  actions: Record<string, ActionStatesJson>
  allowed_actions: Record<string, string[]>
}

export type BacklogItemJson = { title: string; text: string; path: string; last_activity: string }

export type ColumnJson = {
  name: string
  items?: BacklogItemJson[]
  tickets?: TicketJson[]
  work_required?: string[]
  formats?: Record<string, string[]>
  wip_limit?: number
  is_over_limit?: boolean
  in_progress?: TicketJson[]
  done?: TicketJson[]
}

export type BoardJson = { project: string; active: string | null; columns: ColumnJson[] }

export type WorkspaceJson = { has_branch: boolean; has_worktree: boolean }

export type FileEntryJson = { path: string; exists: boolean }

export type TicketFilesJson = Record<string, Record<string, FileEntryJson[]>>

export type FileTextJson = { path: string; text: string }

export type ViolationJson = { location: string; message: string }

export type ReportRuleJson = { name: string; count: number; violations: ViolationJson[] }

export type ReportJson = { path: string; text: string; rules: ReportRuleJson[]; has_saved_graph: boolean }

export type HelpJson = {
  title: string
  overview: string
  guidance: string
  rules: { slug: string; text: string }[]
  href: string
}

export type TicketCardJson = {
  address: string
  title: string
  meta: string
  segments: { scope: string; color: string; isDim: boolean; skill: string }[]
  tail: { text: string; color: string } | null
  titleColor: string
  mutedColor: string
}

export type SplitGripJson = { boardRows: number; color: string; hoverColor: string }

export type PanelGripJson = { panel: string; width: number; color: string; hoverColor: string }

export type TileHoverJson = { place: string; ticket: string; stage: string; slugs: string[]; label: string; mark: string; color: string }

export type SplitLayoutJson = { expanded: 'board' | 'details' | null; boardRows: number | null }

export type TileJson = {
  ticket: string
  place: string
  stage: string
  slugs: string[]
  action: string
  picked: string[]
  isPinned: boolean
  files: TicketFilesJson
}

export type ActivationJson = {
  ticket: string
  title: string
  isClosing: boolean
  leavingTitle: string
  leaving: string[]
  opening: string[]
  workspace: WorkspaceJson
}

export type BacklogDraftJson = { isOpen: boolean; title: string; text: string }

export type PanelFrameJson = { kind: string; width: number; isExpanded: boolean }

export type ReportPanelJson = PanelFrameJson & { kind: 'report'; ticket: string; fidelity: string; report: ReportJson }

export type FilesPanelJson = PanelFrameJson & {
  kind: 'files'
  ticket: string
  slugs: string[]
  files: TicketFilesJson
  mode: string
  tabs: string[]
  activeTab: string
  texts: Record<string, string>
}

export type HelpPanelJson = PanelFrameJson & { kind: 'help'; help: HelpJson }

export type SidePanelJson = ReportPanelJson | FilesPanelJson | HelpPanelJson

declare module 'claude-code' {
  interface PluginState {
    'cdd-board': {
      board: Shaped<BoardJson | null>
      selected: string | null
      splitLayout: SplitLayoutJson
      surfaceModulesFailed: boolean
      onlyActive: boolean
      columnOffset: number
      openCard: string | null
      tile: Shaped<TileJson | null>
      activation: Shaped<ActivationJson | null>
      backlogDraft: BacklogDraftJson
      sidePanels: Shaped<SidePanelJson[]>
    }
  }
}
