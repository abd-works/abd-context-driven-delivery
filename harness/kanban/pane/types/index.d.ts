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
  violation_counts: Record<string, number>
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
  default_formats?: Record<string, string>
  wip_limit?: number
  is_over_limit?: boolean
  in_progress?: TicketJson[]
  done?: TicketJson[]
}

export type BoardJson = { project: string; active: string | null; columns: ColumnJson[] }

export type WorkspaceJson = { has_branch: boolean; has_worktree: boolean; leaving_has_branch: boolean }

export type FileEntryJson = { path: string; exists: boolean }

export type TicketFilesJson = Record<string, Record<string, FileEntryJson[]>>

export type FileTextJson = { path: string; text: string }

export type SourceLineJson = { number: number; text: string }

export type ViolationJson = { location: string; line: number | null; message: string; source: SourceLineJson[] }

export type ReportRuleJson = { fidelity: string; name: string; description: string; count: number; violations: ViolationJson[] }

export type ReportJson = { path: string; text: string; rules: ReportRuleJson[]; has_saved_graph: boolean }

export type HelpJson = {
  practice: string
  fidelity: string
  stage: string
  overview: string
  guidance: string
  rules: { slug: string; text: string }[]
  href: string
}

export type TicketCardJson = {
  address: string
  title: string
  meta: string
  titleColor: string
  hoverColor: string
  mutedColor: string
}

export type RegionOffsetsJson = { board: number; details: number }

export type BoardScrollbarJson = { offset: number; limit: number; shownShare: number; trackColor: string; thumbColor: string; hoverColor: string }

export type SplitGripJson = { boardRows: number; color: string; hoverColor: string }

export type PanelGripJson = { panel: string; width: number; color: string; hoverColor: string }

export type TileHoverJson = { place: string; ticket: string; stage: string; slugs: string[]; label: string; color: string; opensOnHover: boolean; menuSlugs: string[] }

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

export type ReportPanelJson = PanelFrameJson & { kind: 'report'; ticket: string; fidelity: string; report: ReportJson; closedRules: string[] }

export type FilesPanelJson = PanelFrameJson & {
  kind: 'files'
  ticket: string
  slugs: string[]
  files: TicketFilesJson
  mode: string
  tabs: string[]
  activeTab: string
  texts: Record<string, string>
  lines: Record<string, number>
}

export type HelpPanelJson = PanelFrameJson & { kind: 'help'; help: HelpJson }

export type SidePanelJson = ReportPanelJson | FilesPanelJson | HelpPanelJson

declare module 'claude-code' {
  interface PluginState {
    'cdd-board': {
      board: Shaped<BoardJson | null>
      selected: string | null
      splitLayout: SplitLayoutJson
      regionOffsets: RegionOffsetsJson
      surfaceModulesFailed: boolean
      onlyActive: boolean
      columnOffset: number
      editingLimit: string | null
      hidesDisabled: boolean
      openCard: string | null
      tile: Shaped<TileJson | null>
      activation: Shaped<ActivationJson | null>
      backlogDraft: BacklogDraftJson
      sidePanels: Shaped<SidePanelJson[]>
      panelWidths: Record<string, number>
      serverFailure: string | null
      cardOffset: number
    }
  }
}
