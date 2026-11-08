import type { BoardStore, FilesPanel, SidePanel } from '../shared/board-store'
import type { FidelityProgressClient } from './fidelity-progress-client'
import type { FilesByFidelity, TicketClient } from './ticket-client'

const SESSION_ENTRY = 'session'

// The entries a panel's files are read under: the session folder's one, or each fidelity's slug.
const entriesOf = (panel: Pick<FilesPanel, 'isSession' | 'progress'>): string[] => (panel.isSession ? [SESSION_ENTRY] : panel.progress.map(progress => progress.fidelity.slug))

// One tab per format the fidelity offers, generated or not: a story map always shows its markdown and its diagram.
// Tabs follow the order Python sends the formats in (markdown, then code, then diagrams).
export const offeredTabs = (files: FilesByFidelity, slugs: string[]): string[] =>
  slugs.flatMap(slug => Object.values(files[slug] ?? {}).flatMap(entries => entries.map(entry => entry.path)))

const existsIn = (panel: FilesPanel, path: string): boolean =>
  Object.values(panel.files).some(formats => Object.values(formats).some(entries => entries.some(entry => entry.path === path && entry.exists)))

export const generatedPaths = (panel: FilesPanel): string[] =>
  entriesOf(panel)
    .flatMap(slug => Object.values(panel.files[slug] ?? {}).flat())
    .filter(entry => entry.exists)
    .map(entry => entry.path)

export const folderGroupsOf = (paths: string[]): { root: string; entries: { path: string; name: string }[] }[] =>
  [...new Set(paths.map(path => path.split('/')[0] ?? ''))].map(root => ({
    root: `${root}/`,
    entries: paths.filter(path => path.startsWith(`${root}/`)).map(path => ({ path, name: path.slice(root.length + 1) })),
  }))

// Tabs follow what is offered now; one a person closed stays closed, and one a violation opened stays open.
function withFiles(panel: FilesPanel, files: FilesByFidelity): FilesPanel {
  const before = offeredTabs(panel.files, entriesOf(panel))
  const after = offeredTabs(files, entriesOf(panel))
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

// The files panel beside the board: its list, its folders, and the tabs of open files.
export class FilesPanelClient {
  constructor(private readonly store: BoardStore) {}

  private get panel(): FilesPanel | undefined {
    return this.store.state.panels.find((panel): panel is FilesPanel => panel.kind === 'files')
  }

  private show(panel: FilesPanel): void {
    this.store.change(state => ({ panels: [...state.panels.filter((entry: SidePanel) => entry.kind !== panel.kind), panel] }))
  }

  private change(change: (panel: FilesPanel) => FilesPanel): void {
    this.store.change(state => ({ panels: state.panels.map(panel => (panel.kind === 'files' ? change(panel) : panel)) }))
  }

  // A session folder's files are shown as the files of one entry, so the list, folder, and tabs read them the same way.
  private async read(ticket: TicketClient, progress: FidelityProgressClient[], isSession: boolean): Promise<FilesByFidelity | null> {
    if (!isSession) return ticket.filesOf(progress)
    const entries = await ticket.sessionClient.folderFiles()
    return entries && { [SESSION_ENTRY]: { [SESSION_ENTRY]: entries } }
  }

  async openFiles(ticket: TicketClient, progress: FidelityProgressClient[], mode: string): Promise<void> {
    await this.openPanel(ticket, progress, mode, false)
  }

  async openSessionFolder(ticket: TicketClient): Promise<void> {
    await this.openPanel(ticket, [], 'folder', true)
  }

  // The session folder, with one of its files open, such as its latest handoff.
  async openSessionFile(ticket: TicketClient, path: string): Promise<void> {
    await this.openPanel(ticket, [], 'folder', true)
    await this.openTab(path)
  }

  private async openPanel(ticket: TicketClient, progress: FidelityProgressClient[], mode: string, isSession: boolean): Promise<void> {
    const files = await this.read(ticket, progress, isSession)
    if (!files) return
    this.show({ kind: 'files', ticket, isSession, progress, files, mode, tabs: [], activeTab: '', texts: {}, lines: {}, isExpanded: false })
    if (mode === 'files') await this.chooseMode(mode)
  }

  async chooseMode(mode: string): Promise<void> {
    const panel = this.panel
    if (!panel) return
    const tabs = mode === 'files' && !panel.tabs.length ? offeredTabs(panel.files, entriesOf(panel)) : panel.tabs
    const activeTab = panel.activeTab || (tabs[0] ?? '')
    this.change(entry => ({ ...entry, mode, tabs, activeTab }))
    if (mode === 'files' && activeTab) await this.openTab(activeTab)
  }

  private async textOf(ticket: TicketClient, path: string, isOnDisk: boolean): Promise<string> {
    if (!isOnDisk) return ''
    return (await ticket.sessionClient.readFile(path))?.text ?? ''
  }

  async openTab(path: string): Promise<void> {
    const panel = this.panel
    if (!panel) return
    const text = await this.textOf(panel.ticket, path, existsIn(panel, path) || Boolean(panel.texts[path]))
    this.change(entry => showingTab(entry, path, text, entry.lines[path] ?? 0))
  }

  // A violation can name a file its fidelity does not declare, so its text is read whatever the panel lists.
  async openFileAtLine(ticket: TicketClient, progress: FidelityProgressClient | undefined, path: string, line: number): Promise<void> {
    if (this.panel?.ticket.name !== ticket.name) await this.openFiles(ticket, progress ? [progress] : [], 'folder')
    const text = await this.textOf(ticket, path, true)
    this.change(entry => showingTab(entry, path, text, line))
  }

  closeTab(path: string): void {
    this.change(entry => {
      const tabs = entry.tabs.filter(tab => tab !== path)
      return { ...entry, tabs, mode: tabs.length ? 'files' : 'folder', activeTab: entry.activeTab === path ? (tabs[0] ?? '') : entry.activeTab }
    })
  }

  // Generating changes what exists, so an open panel is read again with the board.
  async reload(): Promise<void> {
    await this.reloadFiles()
    await this.reloadFileText()
  }

  private async reloadFiles(): Promise<void> {
    const panel = this.panel
    if (!panel) return
    const files = await this.read(panel.ticket, panel.progress, panel.isSession)
    if (files) this.change(entry => withFiles(entry, files))
  }

  private async reloadFileText(): Promise<void> {
    const panel = this.panel
    if (panel?.mode !== 'files' || !panel.activeTab) return
    const path = panel.activeTab
    const text = await this.textOf(panel.ticket, path, existsIn(panel, path) || Boolean(panel.texts[path]))
    this.change(entry => ({ ...entry, texts: { ...entry.texts, [path]: text } }))
  }
}
