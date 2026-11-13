import type { FileEntryData } from '@cdd/space/kanban/fidelity-progress'
import type { SessionFileData } from '@cdd/space/session/session'

import type { BoardStore, FilesPanel, FilesSource, SidePanel } from '../shared/board-store'
import type { FidelityProgressClient } from './fidelity-progress-client'
import type { FilesByFidelity, TicketClient } from './ticket-client'

// A folder's files are read as the files of one entry, which no practice filter hides.
const FOLDER_ENTRY = 'folder'

// One tab: a file, the practice whose fidelity declares it (none in a folder), whether it is there, and whether the
// ticket's branch changed it.
export type FileTab = { path: string; practice: string; exists: boolean; isChanged: boolean }

const entriesOf = (files: FilesByFidelity, slug: string): FileEntryData[] => Object.values(files[slug] ?? {}).flat()

// Every file the panel offers, each once, in the order of the stage's fidelities and, within one, the order Python sends
// its formats in (markdown, then code, then diagrams), so a practice's tabs stay together.
export function offeredTabs(panel: Pick<FilesPanel, 'source' | 'progress' | 'files'>): FileTab[] {
  const sources = panel.source === 'fidelities' ? panel.progress.map(progress => ({ slug: progress.fidelity.slug, practice: progress.practice.key })) : [{ slug: FOLDER_ENTRY, practice: '' }]
  const tabs = sources.flatMap(({ slug, practice }) => entriesOf(panel.files, slug).map(entry => ({ path: entry.path, practice, exists: entry.exists, isChanged: entry.is_changed })))
  return tabs.filter((tab, index) => tabs.findIndex(other => other.path === tab.path) === index)
}

// The tabs a person sees: the files of the practices turned on, and with the changed filter on, only the changed ones.
export function shownTabs(panel: FilesPanel): FileTab[] {
  return offeredTabs(panel).filter(tab => (!tab.practice || panel.practicesOn.includes(tab.practice)) && (!panel.changedOnly || tab.isChanged))
}

// The practices a panel can filter on, once each, in the order of the stage's fidelities.
export const practicesOf = (panel: Pick<FilesPanel, 'progress'>): string[] => [...new Set(panel.progress.map(progress => progress.practice.key))]

const isShowable = (panel: FilesPanel, path: string): boolean => shownTabs(panel).some(tab => tab.path === path)

// The files panel beside the board: practice filters and a tab per file along its top, and the open file under them.
export class FilesPanelClient {
  constructor(private readonly store: BoardStore) {}

  get panel(): FilesPanel | undefined {
    return this.store.state.panels.find((panel): panel is FilesPanel => panel.kind === 'files')
  }

  private show(panel: FilesPanel): void {
    this.store.change(state => ({ panels: [...state.panels.filter((entry: SidePanel) => entry.kind !== panel.kind), panel] }))
  }

  private change(change: (panel: FilesPanel) => FilesPanel): void {
    this.store.change(state => ({ panels: state.panels.map(panel => (panel.kind === 'files' ? change(panel) : panel)) }))
  }

  private async read(ticket: TicketClient, source: FilesSource, progress: FidelityProgressClient[]): Promise<FilesByFidelity | null> {
    if (source === 'fidelities') return ticket.filesOf(progress)
    const entries = await (source === 'session' ? ticket.sessionClient.folderFiles() : ticket.sessionClient.workpathFiles())
    return entries && { [FOLDER_ENTRY]: { [FOLDER_ENTRY]: entries } }
  }

  // The files of every fidelity of the ticket's stage, with the filters on for the practices of the fidelities given:
  // a fidelity's files button shows its own practice's files, and the others are a toggle away.
  async openFiles(ticket: TicketClient, progress: FidelityProgressClient[]): Promise<void> {
    const offered = ticket.stageProgress.length ? ticket.stageProgress : progress
    const stage = [...offered, ...progress.filter(entry => !offered.some(shown => shown.fidelity.slug === entry.fidelity.slug))]
    await this.openPanel(ticket, 'fidelities', stage, [...new Set(progress.map(entry => entry.practice.key))])
  }

  async openSessionFolder(ticket: TicketClient): Promise<void> {
    await this.openPanel(ticket, 'session', [], [])
  }

  // The folder the session works in, as the details' workpath link opens it.
  async openWorkpath(ticket: TicketClient): Promise<void> {
    await this.openPanel(ticket, 'workpath', [], [])
  }

  // The session folder, with one of its files open, such as its latest handoff.
  async openSessionFile(ticket: TicketClient, path: string): Promise<void> {
    await this.openPanel(ticket, 'session', [], [], path)
  }

  private async openPanel(ticket: TicketClient, source: FilesSource, progress: FidelityProgressClient[], practicesOn: string[], tab = ''): Promise<void> {
    const files = await this.read(ticket, source, progress)
    if (!files) return
    const panel: FilesPanel = { kind: 'files', ticket, source, progress, files, practicesOn, changedOnly: false, activeTab: '', shown: null, lines: {}, isExpanded: false }
    this.show(panel)
    await this.openTab(tab || (shownTabs(panel)[0]?.path ?? ''))
  }

  async togglePractice(practice: string): Promise<void> {
    this.change(panel => ({ ...panel, practicesOn: panel.practicesOn.includes(practice) ? panel.practicesOn.filter(on => on !== practice) : [...panel.practicesOn, practice] }))
    await this.keepATabShown()
  }

  async filterChanged(changedOnly: boolean): Promise<void> {
    this.change(panel => ({ ...panel, changedOnly }))
    await this.keepATabShown()
  }

  // A filter that hides the open tab opens the first one still shown.
  private async keepATabShown(): Promise<void> {
    const panel = this.panel
    if (!panel || isShowable(panel, panel.activeTab)) return
    await this.openTab(shownTabs(panel)[0]?.path ?? '')
  }

  // A file that is not there yet is shown as not generated, without asking the session for it.
  private async fileOf(ticket: TicketClient, path: string, isOnDisk: boolean): Promise<SessionFileData | null> {
    if (!path || !isOnDisk) return null
    return ticket.sessionClient.file(path)
  }

  private isOnDisk(panel: FilesPanel, path: string): boolean {
    const tab = offeredTabs(panel).find(entry => entry.path === path)
    return tab ? tab.exists : true
  }

  async openTab(path: string): Promise<void> {
    const panel = this.panel
    if (!panel) return
    const shown = await this.fileOf(panel.ticket, path, this.isOnDisk(panel, path))
    this.change(entry => ({ ...entry, activeTab: path, shown }))
  }

  // A violation can name a file its fidelity does not declare, so its file is read whatever the panel lists.
  async openFileAtLine(ticket: TicketClient, progress: FidelityProgressClient | undefined, path: string, line: number): Promise<void> {
    if (this.panel?.ticket.name !== ticket.name) await this.openFiles(ticket, progress ? [progress] : [])
    const shown = await this.fileOf(ticket, path, true)
    this.change(entry => ({ ...entry, activeTab: path, shown, lines: { ...entry.lines, [path]: line } }))
  }

  // Generating changes what exists, so an open panel is read again with the board.
  async reload(): Promise<void> {
    const panel = this.panel
    if (!panel) return
    const files = await this.read(panel.ticket, panel.source, panel.progress)
    if (files) this.change(entry => ({ ...entry, files }))
    await this.refreshShown()
  }

  // The open file read again: a chat working on a sent comment can change it and mark the comment processed.
  async refreshShown(): Promise<void> {
    const panel = this.panel
    if (!panel?.activeTab) return
    const path = panel.activeTab
    const shown = await this.fileOf(panel.ticket, path, this.isOnDisk(panel, path))
    this.change(entry => (entry.activeTab === path ? { ...entry, shown } : entry))
  }

  // Saving writes the whole edited text through the session, then shows the file as saved.
  async save(text: string): Promise<void> {
    const panel = this.panel
    if (!panel?.shown) return
    const saved = await panel.ticket.sessionClient.writeFile(panel.shown.path, text)
    if (saved) await this.refreshShown()
  }

  async addComment(startLine: number, endLine: number, text: string): Promise<void> {
    const panel = this.panel
    if (!panel?.shown) return
    await panel.ticket.fileComments.add(panel.shown.path, startLine, endLine, text)
    await this.refreshShown()
  }

  async removeComment(anchor: string): Promise<void> {
    await this.panel?.ticket.fileComments.remove(anchor)
    await this.refreshShown()
  }

  // A comment goes to the chat working on the ticket; one the chat cannot take stays not sent, and the toast says why.
  async sendComment(anchor: string): Promise<void> {
    const panel = this.panel
    if (!panel) return
    await panel.ticket.fileComments.send(anchor, panel.ticket.chat.id)
    await this.refreshShown()
  }

  async sendOpenComments(): Promise<void> {
    const panel = this.panel
    if (!panel) return
    await panel.ticket.fileComments.sendOpen(panel.ticket.chat.id)
    await this.refreshShown()
  }

  async clearProcessedComments(): Promise<void> {
    await this.panel?.ticket.fileComments.clearProcessed()
    await this.refreshShown()
  }
}
