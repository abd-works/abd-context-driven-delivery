import type { FileText, Help, Report, TicketFiles } from './board'
import type { BoardApi } from './board-api'
import { pathPart } from './board-api'
import { FORMAT_GROUPS } from './board-brand'
import type { BoardStore, FilesPanel, ReportPanel, SidePanel } from './board-store'

const DEFAULT_WIDTH = 640
export const SMALLEST_WIDTH = 360
const LARGEST_WIDTH = 1200
const TAB_GROUPS = ['markdown', 'code', 'diagram']
const TAB_ORDER = TAB_GROUPS.flatMap(label => FORMAT_GROUPS.find(group => group.label === label)?.formats ?? [])

const replacing = (panels: SidePanel[], panel: SidePanel): SidePanel[] => [...panels.filter(entry => entry.kind !== panel.kind), panel]

// One tab per format the fidelity offers, generated or not: a story map always shows its markdown and its diagram.
export const offeredTabs = (files: TicketFiles, slugs: string[]): string[] =>
  slugs.flatMap(slug =>
    [...TAB_ORDER, ...Object.keys(files[slug] ?? {}).filter(label => !TAB_ORDER.includes(label))].flatMap(label => (files[slug]?.[label] ?? []).map(entry => entry.path)),
  )

const existsIn = (panel: FilesPanel, path: string): boolean =>
  Object.values(panel.files).some(formats => Object.values(formats).some(entries => entries.some(entry => entry.path === path && entry.exists)))

export const generatedPaths = (panel: FilesPanel): string[] =>
  panel.slugs
    .flatMap(slug => Object.values(panel.files[slug] ?? {}).flat())
    .filter(entry => entry.exists)
    .map(entry => entry.path)

export const folderGroupsOf = (paths: string[]): { root: string; entries: { path: string; name: string }[] }[] =>
  [...new Set(paths.map(path => path.split('/')[0] ?? ''))].map(root => ({
    root: `${root}/`,
    entries: paths.filter(path => path.startsWith(`${root}/`)).map(path => ({ path, name: path.slice(root.length + 1) })),
  }))

// Tabs follow what is offered now; one a person closed stays closed, and one a violation opened stays open.
function withFiles(panel: FilesPanel, files: TicketFiles): FilesPanel {
  const before = offeredTabs(panel.files, panel.slugs)
  const after = offeredTabs(files, panel.slugs)
  const kept = panel.tabs.filter(tab => after.includes(tab) || !before.includes(tab))
  const added = panel.tabs.length ? after.filter(tab => !before.includes(tab) && !kept.includes(tab)) : []
  const tabs = [...kept, ...added]
  return { ...panel, files, tabs, activeTab: tabs.includes(panel.activeTab) ? panel.activeTab : (tabs[0] ?? '') }
}

const showingTab = (panel: FilesPanel, path: string, text: string, line: number): FilesPanel => ({
  ...panel,
  mode: 'files',
  tabs: panel.tabs.includes(path) ? panel.tabs : [...panel.tabs, path],
  activeTab: path,
  texts: { ...panel.texts, [path]: text },
  lines: { ...panel.lines, [path]: line },
})

// The report, files, and help panels beside the board.
export class SidePanelClient {
  constructor(
    private readonly store: BoardStore,
    private readonly api: BoardApi,
  ) {}

  private get panels(): SidePanel[] {
    return this.store.state.panels
  }

  private get filesPanel(): FilesPanel | undefined {
    return this.panels.find((panel): panel is FilesPanel => panel.kind === 'files')
  }

  private get reportPanel(): ReportPanel | undefined {
    return this.panels.find((panel): panel is ReportPanel => panel.kind === 'report')
  }

  private show(panel: SidePanel): void {
    this.store.change(state => ({ panels: replacing(state.panels, panel) }))
  }

  private changeFiles(change: (panel: FilesPanel) => FilesPanel): void {
    this.store.change(state => ({ panels: state.panels.map(panel => (panel.kind === 'files' ? change(panel) : panel)) }))
  }

  private changeReport(change: (panel: ReportPanel) => ReportPanel): void {
    this.store.change(state => ({ panels: state.panels.map(panel => (panel.kind === 'report' ? change(panel) : panel)) }))
  }

  widthOf(kind: string): number {
    return this.store.state.panelWidths[kind] ?? DEFAULT_WIDTH
  }

  setWidth(kind: string, wanted: number): void {
    const width = Math.min(Math.max(wanted, SMALLEST_WIDTH), LARGEST_WIDTH)
    this.store.change(state => ({ panelWidths: { ...state.panelWidths, [kind]: width } }))
  }

  private readReport(ticket: string, fidelity: string): Promise<Report | null> {
    const path = `/tickets/${pathPart(ticket)}`
    return this.api.get<Report>(fidelity ? `${path}/report?fidelity=${pathPart(fidelity)}` : `${path}/violations`)
  }

  // With no fidelity, a report panel holds the violations of every fidelity of its ticket.
  async openReport(ticket: string, fidelity: string): Promise<void> {
    const report = await this.readReport(ticket, fidelity)
    if (report) this.show({ kind: 'report', ticket, fidelity, report, closedRules: [], isExpanded: false })
  }

  // rule is its fidelity and name, because one report can list a rule on two fidelities.
  toggleRule(rule: string): void {
    this.changeReport(panel => {
      const isClosed = panel.closedRules.includes(rule)
      return { ...panel, closedRules: isClosed ? panel.closedRules.filter(name => name !== rule) : [...panel.closedRules, rule] }
    })
  }

  async openFiles(ticket: string, slugs: string[], mode: string): Promise<void> {
    const files = await this.api.post<TicketFiles>(`/tickets/${pathPart(ticket)}/files`, { fidelities: slugs })
    if (!files) return
    this.show({ kind: 'files', ticket, slugs, files, mode, tabs: [], activeTab: '', texts: {}, lines: {}, isExpanded: false })
    if (mode === 'files') await this.chooseMode(mode)
  }

  async chooseMode(mode: string): Promise<void> {
    const panel = this.filesPanel
    if (!panel) return
    const tabs = mode === 'files' && !panel.tabs.length ? offeredTabs(panel.files, panel.slugs) : panel.tabs
    const activeTab = panel.activeTab || (tabs[0] ?? '')
    this.changeFiles(entry => ({ ...entry, mode, tabs, activeTab }))
    if (mode === 'files' && activeTab) await this.openTab(activeTab)
  }

  private async textOf(ticket: string, path: string, isOnDisk: boolean): Promise<string> {
    if (!isOnDisk) return ''
    return (await this.api.get<FileText>(`/tickets/${pathPart(ticket)}/file?path=${pathPart(path)}`))?.text ?? ''
  }

  async openTab(path: string): Promise<void> {
    const panel = this.filesPanel
    if (!panel) return
    const text = await this.textOf(panel.ticket, path, existsIn(panel, path) || Boolean(panel.texts[path]))
    this.changeFiles(entry => showingTab(entry, path, text, entry.lines[path] ?? 0))
  }

  // A violation can name a file its fidelity does not declare, so its text is read whatever the panel lists.
  async openFileAtLine(ticket: string, fidelity: string, path: string, line: number): Promise<void> {
    if (this.filesPanel?.ticket !== ticket) await this.openFiles(ticket, [fidelity], 'list')
    const text = await this.textOf(ticket, path, true)
    this.changeFiles(entry => showingTab(entry, path, text, line))
  }

  closeTab(path: string): void {
    this.changeFiles(entry => {
      const tabs = entry.tabs.filter(tab => tab !== path)
      return { ...entry, tabs, mode: tabs.length ? 'files' : 'list', activeTab: entry.activeTab === path ? (tabs[0] ?? '') : entry.activeTab }
    })
  }

  async openHelp(practice: string, fidelity: string): Promise<void> {
    const help = await this.api.get<Help>(`/board/help?practice=${pathPart(practice)}&fidelity=${pathPart(fidelity)}`)
    if (help) this.show({ kind: 'help', help, isExpanded: false })
  }

  close(kind: string): void {
    this.store.change(state => ({ panels: state.panels.filter(panel => panel.kind !== kind) }))
  }

  closeTicketPanels(ticket: string): void {
    this.store.change(state => ({ panels: state.panels.filter(panel => panel.kind === 'help' || panel.ticket !== ticket) }))
  }

  // One panel is expanded at a time.
  toggleExpanded(kind: string): void {
    this.store.change(state => ({ panels: state.panels.map(panel => ({ ...panel, isExpanded: panel.kind === kind && !panel.isExpanded })) }))
  }

  // A fix changes the report on disk and generating changes what exists, so open panels are read again with the board.
  async reload(): Promise<void> {
    await Promise.all([this.reloadReport(), this.reloadFiles()])
    await this.reloadFileText()
  }

  private async reloadReport(): Promise<void> {
    const open = this.reportPanel
    if (!open) return
    const report = await this.readReport(open.ticket, open.fidelity)
    if (report) this.changeReport(panel => ({ ...panel, report }))
  }

  private async reloadFiles(): Promise<void> {
    const panel = this.filesPanel
    if (!panel) return
    const files = await this.api.post<TicketFiles>(`/tickets/${pathPart(panel.ticket)}/files`, { fidelities: panel.slugs })
    if (files) this.changeFiles(entry => withFiles(entry, files))
  }

  private async reloadFileText(): Promise<void> {
    const panel = this.filesPanel
    if (panel?.mode !== 'files' || !panel.activeTab) return
    const path = panel.activeTab
    const text = await this.textOf(panel.ticket, path, existsIn(panel, path) || Boolean(panel.texts[path]))
    this.changeFiles(entry => ({ ...entry, texts: { ...entry.texts, [path]: text } }))
  }
}
