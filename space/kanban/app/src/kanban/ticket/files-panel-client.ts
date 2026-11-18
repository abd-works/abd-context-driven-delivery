import type { FileEntryData } from '@cdd/space/kanban/fidelity-progress'
import type { SessionFileData } from '@cdd/space/session/session'

import { DEFAULT_FILE_READS } from '../shared/board-store'
import type { BoardStore, FileReads, FilesPanel, FilesSource } from '../shared/board-store'
import type { FidelityProgressClient } from './fidelity-progress-client'
import { OpenFileComments } from './open-file-comments'
import type { TicketClient } from './ticket-client'
import type { FilesByFidelity } from './ticket-work'

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

// Which files a panel shows: where they come from, the fidelities they are read for, and the practices filtered on.
type FilesChoice = Pick<FilesPanel, 'source' | 'progress' | 'practicesOn'>

// A line of a file, such as the one a violation names.
export type FileLine = { path: string; line: number }

// The files panel beside the board: practice filters and a tab per file along its top, and the open file under them.
export class FilesPanelClient {
  readonly comments: OpenFileComments = new OpenFileComments(this)

  constructor(private readonly store: BoardStore) {}

  get panel(): FilesPanel | undefined {
    return this.store.panelOf('files')
  }

  private change(change: (panel: FilesPanel) => FilesPanel): void {
    this.store.changePanel('files', change)
  }

  private async read(ticket: TicketClient, { source, progress }: Pick<FilesChoice, 'source' | 'progress'>): Promise<FilesByFidelity | null> {
    if (source === 'fidelities') return ticket.work.filesOf(progress)
    const entries = await (source === 'session' ? ticket.sessionClient.folderFiles() : ticket.sessionClient.workpathFiles())
    return entries && { [FOLDER_ENTRY]: { [FOLDER_ENTRY]: entries } }
  }

  // The files of every fidelity of the ticket's stage, with the filters on for the practices of the fidelities given:
  // a fidelity's files button shows its own practice's files, and the others are a toggle away.
  async openFiles(ticket: TicketClient, progress: FidelityProgressClient[]): Promise<void> {
    const offered = ticket.work.stageProgress.length ? ticket.work.stageProgress : progress
    const stage = [...offered, ...progress.filter(entry => !offered.some(shown => shown.fidelity.slug === entry.fidelity.slug))]
    await this.openPanel(ticket, { source: 'fidelities', progress: stage, practicesOn: [...new Set(progress.map(entry => entry.practice.key))] })
  }

  // The ticket's session folder, or the folder the session works in as the details' workpath link opens it, with one of
  // its files open when path names one, such as its latest handoff.
  async openFolder(ticket: TicketClient, source: Exclude<FilesSource, 'fidelities'>, path: string = ''): Promise<void> {
    await this.openPanel(ticket, folderOf(source), path)
  }

  private async openPanel(ticket: TicketClient, choice: FilesChoice, tab: string = ''): Promise<void> {
    const files = await this.read(ticket, choice)
    if (!files) return
    const reads = this.panel?.reads ?? DEFAULT_FILE_READS
    const panel: FilesPanel = { kind: 'files', ticket, ...choice, files, changedOnly: false, reads, activeTab: '', shown: null, lines: {}, isExpanded: false }
    this.store.showPanel(panel)
    await this.openTab(tab || (shownTabs(panel)[0]?.path ?? ''))
  }

  async togglePractice(practice: string): Promise<void> {
    this.change(panel => ({ ...panel, practicesOn: panel.practicesOn.includes(practice) ? panel.practicesOn.filter(on => on !== practice) : [...panel.practicesOn, practice] }))
    await this.keepATabShown()
  }

  // Turns the open file's folds or its broken rules on or off, each apart from the other, and reads the file again.
  async toggleRead(read: keyof FileReads): Promise<void> {
    this.change(panel => ({ ...panel, reads: { ...panel.reads, [read]: !panel.reads[read] } }))
    await this.refreshShown()
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
    const { folds, rules } = this.panel?.reads ?? DEFAULT_FILE_READS
    return ticket.sessionClient.file(path, rules, false, folds)
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
  async openFileAtLine(ticket: TicketClient, progress: FidelityProgressClient | undefined, { path, line }: FileLine): Promise<void> {
    if (this.panel?.ticket.name !== ticket.name) await this.openFiles(ticket, progress ? [progress] : [])
    const shown = await this.fileOf(ticket, path, true)
    this.change(entry => ({ ...entry, activeTab: path, shown, lines: { ...entry.lines, [path]: line } }))
  }

  // Generating changes what exists, so an open panel is read again with the board.
  async reload(): Promise<void> {
    const panel = this.panel
    if (!panel) return
    const files = await this.read(panel.ticket, panel)
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
}

// A folder's files, with no fidelity read and no practice filtered on.
function folderOf(source: Exclude<FilesSource, 'fidelities'>): FilesChoice {
  return { source, progress: [], practicesOn: [] }
}
