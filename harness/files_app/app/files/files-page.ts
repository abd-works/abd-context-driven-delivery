import type { CddApi } from '@cdd/cdd-shared'
import { ChatClientGenerated } from '@cdd/harness/chat/chat'
import { TicketClientGenerated } from '@cdd/space/kanban/ticket'
import { SessionClientGenerated, type FileEntryData, type SessionFileData } from '@cdd/space/session/session'

import { ChatContext } from './chat-context'
import { FileBar, publishedOf } from './file-bar'
import { FileBrowser } from './file-browser'
import { FileCallouts } from './file-callouts'
import { FileCommentsActions } from './file-comments-actions'
import { FileMenu } from './file-menu'
import type { FilesLink } from './files-link'
import { FilesGraph } from './files-graph'
import { FilesFoldKeys } from './files-fold-keys'
import { FilesNotices } from './files-notices'
import { isDrawio } from './files-paths'
import { FilesStore, type FidelityFiles, type SelectedNode } from './files-state'
import { formatGlyphOf } from './format-chips'
import { GuidanceSelector } from './guidance-selector'
import { OpenFiles } from './open-files'
import { reasonOf } from './reason'

// While a comment on the open file is with a chat, the file is read again this often, so the chat's change and the
// comment's processed state show without a reload. Nothing else is read again: never the list, never a board.
export const SENT_REFRESH_MILLISECONDS = 2_000

// Each file once, in the order its fidelities and formats send them.
const eachOnce = (entries: FileEntryData[]): FileEntryData[] => entries.filter((entry, index) => entries.findIndex(other => other.path === entry.path) === index)

// The Files app's page: the files its link names, read once, and the one open, read when opened and again while a
// comment on it is with a chat. A .drawio file shows in the draw.io editor instead.
export class FilesPage {
  readonly store = new FilesStore()
  readonly session: SessionClientGenerated
  readonly comments: FileCommentsActions
  readonly fileBar = new FileBar(this.store)
  readonly guidance: GuidanceSelector
  readonly notices: FilesNotices
  readonly chatContext: ChatContext
  readonly menu: FileMenu
  readonly graph: FilesGraph
  readonly openFiles = new OpenFiles(this.store)
  readonly foldKeys: FilesFoldKeys
  readonly callouts: FileCallouts
  private refreshTimer: ReturnType<typeof setTimeout> | null = null
  // The link's line shows in the file the link opens until the person opens another file or selects a node.
  private showsLinkedLine = true

  constructor(
    readonly api: CddApi,
    readonly link: FilesLink,
  ) {
    this.session = SessionClientGenerated.named(api, link.sessionFile)
    this.notices = new FilesNotices(this.store, api, link.chat)
    this.foldKeys = new FilesFoldKeys(this.session, this.notices)
    this.callouts = new FileCallouts(this.store, this.session)
    this.chatContext = new ChatContext(this.session, link.chat, this.notices)
    this.menu = new FileMenu(this.store, this.chatContext, new FileBrowser(api, this.notices))
    this.comments = new FileCommentsActions(this)
    this.graph = new FilesGraph(this.store, this.session, this.api, this.fileBar, this.notices, selected => this.showNodes(selected))
    this.guidance = new GuidanceSelector(this)
  }

  get state() {
    return this.store.state
  }

  // Read the files the link names and open the one it names, else the first; reading the open file again whenever the
  // person comes back to the page. Answers what stops it.
  start(): () => void {
    this.fileBar.restoreWidth()
    const uncaught = (failure: unknown) => this.notices.fail(`The Files page met a failure nothing caught: ${reasonOf(failure)}`, 'An uncaught failure in the Files page')
    const onError = (event: ErrorEvent) => uncaught(event.error ?? event.message)
    const onRejection = (event: PromiseRejectionEvent) => uncaught(event.reason)
    window.addEventListener('error', onError)
    window.addEventListener('unhandledrejection', onRejection)
    void this.list()
    // A link naming no session, such as the app's bare address, has nothing to ask cdd about: list() says so.
    if (this.link.namesFiles) void this.readPlace()
    if (this.link.namesFiles) void this.foldKeys.read()
    if (this.link.namesFiles && !this.link.isFolder) void this.readRootFiles()
    const stopFollowing = this.follow()
    const reread = () => void this.refreshOpen()
    window.addEventListener('focus', reread)
    return () => {
      window.removeEventListener('error', onError)
      window.removeEventListener('unhandledrejection', onRejection)
      window.removeEventListener('focus', reread)
      stopFollowing()
      this.stopRefreshing()
    }
  }

  // Follows the session's guidance selection, which a link naming a ticket's files shows, reads the graph view again
  // whenever the files it lists change, and reads the open files again whenever the file view's filters change. Answers
  // what stops all three.
  private follow(): () => void {
    const stopGuidance = this.link.isFolder || !this.link.namesFiles ? () => undefined : this.guidance.follow()
    const stopGraph = this.graph.follow()
    const stopCallouts = this.followFilters()
    return () => {
      stopGuidance()
      stopGraph()
      stopCallouts()
    }
  }

  // Reads the open files again whenever the file view's filters change, such as a practice turned off or a connector
  // left out of the graph view's node filter: which callouts each holds for them is the session's answer. While the
  // graph view reads the session's graph, the files wait for it, since what a step invokes and observes comes from that
  // graph; they are read once its trees arrive. Answers what stops it.
  private followFilters(): () => void {
    let readFor = this.callouts.readFor
    let trees = this.state.graph.trees
    return this.store.subscribe(() => {
      const { graph } = this.state
      const now = this.callouts.readFor
      if (graph.isReading || (now === readFor && graph.trees === trees)) return
      readFor = now
      trees = graph.trees
      void this.readOpenAgain()
    })
  }

  // The open file and each file open beside it, read again as the session answers them now.
  private async readOpenAgain(): Promise<void> {
    await this.refreshOpen()
    const beside = this.state.moreFiles.map(file => file.path)
    if (!beside.length) return
    const read = await Promise.all(beside.map(path => this.readBeside(path)))
    this.store.change(() => ({ moreFiles: read.filter((file): file is SessionFileData => file !== null) }))
  }

  // The header: the repository, the branch, and the session's root; the link's subject until the session answers.
  get heading(): string {
    return this.state.place || this.link.subject
  }

  // Where the files are, read once as the page opens.
  private async readPlace(): Promise<void> {
    try {
      const session = await this.session.show()
      if (session) this.store.change(() => ({ place: [session.repoName, session.branch, session.root].filter(Boolean).join(' · ') }))
    } catch (failure) {
      this.notices.fail(`The Files app did not read where the session works: ${reasonOf(failure)}`, 'Opening the Files app, calling session.show', { kind: 'session_roots' })
    }
  }

  private async list(): Promise<void> {
    if (!this.link.namesFiles) return this.store.change(() => ({ isListing: false, problem: 'This link names no files: open the Files app from the chat bar.' }))
    try {
      const byFidelity = await this.filesByFidelity(this.asked)
      this.store.change(state => ({ byFidelity, isListing: false, entries: this.shownFrom({ ...state, byFidelity }) }))
      const entries = this.state.entries
      const first = this.link.file || entries.find(entry => entry.exists && !isDrawio(entry.path) && !publishedOf(entry))?.path || ''
      // The file the link names opens as the link opened it, at the line it names.
      if (first) await this.openAt(first)
    } catch (failure) {
      this.store.change(() => ({ isListing: false, problem: `The files did not list: ${reasonOf(failure)}` }))
      this.notices.fail(`The Files app did not list the files: ${reasonOf(failure)}`, `Opening the Files app on ${this.link.subject}`, { isShownOnPage: true, kind: 'session_roots' })
    }
  }

  // The fidelities whose files the page asks for: those its link names and those the session's guidance selection
  // covers. Each file the session answers says whether the page lists it, for the selection and the link.
  get asked(): string[] {
    return [...new Set([...this.link.fidelities, ...(this.state.guidance?.fidelities ?? [])])]
  }

  // The files shown from state, each one the session says the page lists: the files of the fidelities asked for first,
  // among them those not generated yet and a design canvas at its link; then every other file under the session's root.
  // The file bar keeps the session's own work for This session.
  private shownFrom(state: FilesPage['state']): FileEntryData[] {
    const listed = (entries: FileEntryData[]) => entries.filter(entry => entry.is_listed)
    const ofFidelities = listed(state.byFidelity.flatMap(each => each.entries))
    return this.link.isFolder ? eachOnce(ofFidelities) : eachOnce([...ofFidelities, ...listed(state.rootFiles ?? [])])
  }

  // Every file under the session's root, read once as the page opens: what All session files lists, and This session
  // the changed ones of.
  private async readRootFiles(): Promise<void> {
    try {
      const rootFiles = (await TicketClientGenerated.named(this.api, this.link.ticket).rootFiles(this.link.fidelities)) ?? []
      this.store.change(state => ({ rootFiles, entries: this.shownFrom({ ...state, rootFiles }) }))
    } catch (failure) {
      this.notices.fail(`The Files app did not list the files under the session's root: ${reasonOf(failure)}`, 'Opening the Files app, calling ticket.root_files', { kind: 'session_roots' })
    }
  }

  // A session folder is one list of no fidelity; a ticket's fidelities are kept apart, so a practice can hide its own.
  private async filesByFidelity(slugs: string[]): Promise<FidelityFiles[]> {
    if (this.link.isFolder) return [{ slug: '', entries: (await (this.link.folder === 'workpath' ? this.session.workpathFiles() : this.session.folderFiles())) ?? [] }]
    if (!slugs.length) return []
    // One call for every fidelity, which shares one look at what the branch changed.
    const bySlug = (await TicketClientGenerated.named(this.api, this.link.ticket).fidelityFiles(slugs, this.link.fidelities)) ?? {}
    return slugs.map(slug => ({ slug, entries: Object.values(bySlug[slug] ?? {}).flat() }))
  }

  // A selection changed, here or anywhere: the session says again which files the page lists for it, so the list is
  // read again, the fidelities it asks for and every file under the session's root.
  async showSelected(): Promise<void> {
    if (this.state.isListing) return
    await this.listAgain()
  }

  // This session lists the files the branch changed; All session files lists every file of the fidelities listed, older
  // work included. The stages, practices and formats selected filter both. Each press reads the files again, so one
  // renamed, added or deleted on disk since the page opened is listed as it is now.
  showScope(scope: 'session' | 'all'): void {
    this.store.change(() => ({ scope }))
    if (this.link.namesFiles && !this.link.isFolder && !this.state.isListing) void this.listAgain()
  }

  // The files of the fidelities the page asks for and every file under the session's root, read again and shown.
  private async listAgain(): Promise<void> {
    try {
      const byFidelity = await this.filesByFidelity(this.link.isFolder ? [] : this.asked)
      this.store.change(state => ({ byFidelity, entries: this.shownFrom({ ...state, byFidelity }) }))
    } catch (failure) {
      this.notices.fail(`The Files app did not list the files again: ${reasonOf(failure)}`, 'Pressing This session or All session files, calling ticket.fidelity_files', { kind: 'session_roots' })
    }
    if (!this.link.isFolder) await this.readRootFiles()
  }

  // Why the list is empty: the formats selected hold none of the files of the fidelities listed, such as code at a stage
  // whose fidelities write only documents and diagrams; else there are no files yet.
  get emptyReason(): string {
    const chosen = (this.state.guidance?.formats ?? []).filter(format => format.is_selected).map(format => formatGlyphOf(format.label))
    const anyFiles = this.state.byFidelity.some(each => each.entries.length > 0)
    if (chosen.length && anyFiles) return `None of these files is in the formats chosen (${chosen.join(' ')}): press a chosen format to show every format.`
    return 'No files here yet.'
  }

  // Turns on or off the open file's own rules: it is read on its own and only its rules run, under a second. The open
  // file is read again with them.
  async toggleRules(): Promise<void> {
    this.store.change(({ reads }) => ({ reads: { ...reads, rules: !reads.rules } }))
    await this.refreshOpen()
  }

  // Turns on or off the rules only the whole working copy finds in the open file, linking files and practices, which
  // takes far longer; apart from its own rules, which Rules turns on.
  async toggleCrossFile(): Promise<void> {
    this.store.change(({ reads }) => ({ reads: { ...reads, crossFile: !reads.crossFile } }))
    await this.refreshOpen()
  }

  // A file a person chooses from the list opens alone, leaving the nodes selected in the graph view.
  async open(path: string): Promise<void> {
    this.showsLinkedLine = false
    this.store.change(({ graph }) => ({ moreFiles: [], graph: { ...graph, selected: [] } }))
    await this.openAt(path)
  }

  // The files of the nodes selected in the graph view, each once, in the order they were selected: the first is the open
  // file, the others open beside it. Each is read with its folds, which unfold to the nodes selected in it.
  async showNodes(selected: SelectedNode[]): Promise<void> {
    const [first, ...others] = [...new Set(selected.map(node => node.lines.path))]
    if (!first) return
    this.showsLinkedLine = false
    if (this.state.openPath === first && this.state.file) await this.refreshOpen()
    else await this.openAt(first)
    const read = await Promise.all(others.map(path => this.readBeside(path)))
    this.store.change(() => ({ moreFiles: read.filter((file): file is SessionFileData => file !== null) }))
  }

  // A file opened below the first: one that does not read, or answers no file, is shown and told, and the others open.
  private async readBeside(path: string): Promise<SessionFileData | null> {
    try {
      return this.withRulesAsked(await this.callouts.file(path, true, this.state.reads.crossFile))
    } catch (failure) {
      this.notices.fail(`The Files app did not open ${path}: ${reasonOf(failure)}`, `Opening ${path} in the Files app`, { kind: 'file_display' })
      return null
    }
  }

  // The lines of the file at path asked to show, which unfold and scroll into view: those of the nodes selected in the
  // graph view that sit in it, else the line the page's link names, such as a violation's, while the link's file is the
  // one it opened.
  linesShownIn(path: string): { start: number; end: number }[] {
    const selected = this.state.graph.selected.filter(node => node.lines.path === path).map(node => ({ start: node.lines.start_line, end: node.lines.end_line }))
    return selected.length || !this.showsLinkedLine ? selected : this.link.linesIn(path)
  }

  private async openAt(path: string): Promise<void> {
    this.store.change(() => ({ openPath: path, file: null }))
    // A .drawio file shows in the draw.io editor beside the file list, which reads the file itself.
    if (isDrawio(path)) return this.stopRefreshing()
    await this.refreshOpen()
  }

  // The open file read again through the session: its text, comments, folds, violations and the chat's changes.
  private async refreshOpen(): Promise<void> {
    const path = this.state.openPath
    if (!path) return
    this.stopRefreshing()
    try {
      const { rules, crossFile } = this.state.reads
      // A file opened from the graph view needs the folds its graph places, which only a read with rules answers.
      const file = this.withRulesAsked(await this.callouts.file(path, rules || this.state.graph.selected.length > 0, crossFile))
      if (this.state.openPath !== path) return
      this.store.change(() => ({ file, problem: '' }))
      if (file) this.notices.fixes.showMissingLinksOf(file)
      if (file?.comments.some(comment => comment.state === 'sent')) this.refreshTimer = setTimeout(() => void this.refreshOpen(), SENT_REFRESH_MILLISECONDS)
    } catch (failure) {
      this.store.change(() => ({ problem: `${path} did not open: ${reasonOf(failure)}` }))
      this.notices.fail(`The Files app did not open ${path}: ${reasonOf(failure)}`, `Opening ${path} in the Files app, calling session.file`, { isShownOnPage: true, kind: 'file_display' })
    }
  }

  // The file as the page shows it: a file opened from the graph is read with its rules for the folds the graph places,
  // and its broken rules show only while Rules or Cross-file is on.
  private withRulesAsked(file: SessionFileData | null): SessionFileData | null {
    const { rules, crossFile } = this.state.reads
    return file && !rules && !crossFile ? { ...file, violations: [] } : file
  }

  private stopRefreshing(): void {
    if (this.refreshTimer) clearTimeout(this.refreshTimer)
    this.refreshTimer = null
  }

  // Open a whiteboard or design canvas in Claude Desktop's artifact panel, beside the chat: the page cannot reach that
  // panel itself, so it asks the chat that opened it to open the board there. Answers false when no chat opened the
  // page, so the view opens the link in a browser instead.
  async openPublished(entry: FileEntryData): Promise<boolean> {
    const published = publishedOf(entry)
    if (!published?.link || !this.link.chat) return false
    const ask = `Open the ${published.kind} ${published.name} (${entry.path}) in the artifact panel: ${published.link}`
    const asked = await this.attempt(`The ${published.kind} ${published.name} did not open`, () => ChatClientGenerated.named(this.api, this.link.chat).send('submit', ask))
    if (asked) this.notices.toast(`Opening ${published.name} in Claude's artifact panel`)
    return asked
  }

  async attempt(what: string, work: () => Promise<unknown>): Promise<boolean> {
    try {
      await work()
      return true
    } catch (failure) {
      this.notices.fail(`${what}: ${reasonOf(failure)}`, 'A press on a comment in the Files app')
      return false
    } finally {
      await this.refreshOpen()
    }
  }
}
