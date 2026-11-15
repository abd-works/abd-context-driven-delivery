import type { CddApi } from '@cdd/cdd-shared'
import { ChatClientGenerated } from '@cdd/harness/chat/chat'
import { TicketClientGenerated } from '@cdd/space/kanban/ticket'
import { SessionClientGenerated, type FileEntryData, type GuidanceSelectionData } from '@cdd/space/session/session'

import { FileBar } from './file-bar'
import { FileCommentsActions } from './file-comments-actions'
import type { FilesLink } from './files-link'
import { isDrawio, REVEAL_PATH } from './files-paths'
import { FilesStore, type FidelityFiles } from './files-state'
import { formatGlyphOf } from './format-chips'
import { GuidanceSelector } from './guidance-selector'

// While a comment on the open file is with a chat, the file is read again this often, so the chat's change and the
// comment's processed state show without a reload. Nothing else is read again: never the list, never a board.
export const SENT_REFRESH_MILLISECONDS = 2_000
const TOAST_MILLISECONDS = 8_000

const reasonOf = (failure: unknown): string => (failure instanceof Error ? failure.message : String(failure))

// The fidelities whose files the page lists: those the session's guidance selection lists, its stages selected by its
// practices selected, none selected meaning every one; before any stage was selected, the ones the link names.
export const listedBy = (selection: GuidanceSelectionData | null, linked: string[]): string[] =>
  selection?.is_stage_chosen ? selection.fidelities : linked

// The formats of the format groups selected, each once; none selected, every format shows.
export const selectedFormatsOf = (selection: GuidanceSelectionData | null): string[] =>
  [...new Set((selection?.formats ?? []).filter(format => format.is_selected).flatMap(format => format.formats))]

// The files the page shows, each once: of the fidelities listed, only the ones in a format selected while any is.
export const filesShown = (byFidelity: FidelityFiles[], listed: string[], formats: string[] = []): FileEntryData[] => {
  const inFormat = ({ entries, formatOf = {} }: FidelityFiles) => (formats.length ? entries.filter(entry => formats.includes(formatOf[entry.path] ?? '')) : entries)
  return eachOnce(byFidelity.filter(({ slug }) => !slug || listed.includes(slug)).flatMap(inFormat))
}

// The files under the session's root a page shows: in a format selected while any is, and belonging to a fidelity listed.
// A file no fidelity declares, such as a practice's example, belongs to no practice, so it shows only while no practice
// is selected, which filters no practice; Stories selected shows Stories' files alone.
export const rootFilesShown = (rootFiles: FileEntryData[], listed: string[], formats: string[], withUnclaimed: boolean): FileEntryData[] =>
  rootFiles.filter(entry => (!formats.length || formats.includes(entry.format)) && (entry.fidelities.length ? entry.fidelities.some(slug => listed.includes(slug)) : withUnclaimed))

// Whether no practice is selected, so no practice filters the files; with no selection read yet, none is.
export const isNoPracticeSelected = (selection: GuidanceSelectionData | null): boolean => !(selection?.practices ?? []).some(practice => practice.is_selected)

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
  private refreshTimer: ReturnType<typeof setTimeout> | null = null
  // The failures already shown here and sent to the chat that opened the page.
  private readonly toldChat = new Set<string>()

  constructor(
    readonly api: CddApi,
    readonly link: FilesLink,
  ) {
    this.session = SessionClientGenerated.named(api, link.sessionFile)
    this.comments = new FileCommentsActions(this)
    this.guidance = new GuidanceSelector(this.session, this.store, () => this.showSelected(), (failure, context) => this.fail(failure, context))
  }

  get state() {
    return this.store.state
  }

  // Read the files the link names and open the one it names, else the first; reading the open file again whenever the
  // person comes back to the page. Answers what stops it.
  start(): () => void {
    const uncaught = (failure: unknown) => this.fail(`The Files page met a failure nothing caught: ${reasonOf(failure)}`, 'An uncaught failure in the Files page')
    const onError = (event: ErrorEvent) => uncaught(event.error ?? event.message)
    const onRejection = (event: PromiseRejectionEvent) => uncaught(event.reason)
    window.addEventListener('error', onError)
    window.addEventListener('unhandledrejection', onRejection)
    void this.list()
    // A link naming no session, such as the app's bare address, has nothing to ask cdd about: list() says so.
    if (this.link.namesFiles) void this.readPlace()
    if (this.link.namesFiles && !this.link.isSessionFolder) void this.readRootFiles()
    const stopFollowing = this.link.isSessionFolder || !this.link.namesFiles ? () => undefined : this.guidance.follow()
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
      this.fail(`The Files app did not read where the session works: ${reasonOf(failure)}`, 'Opening the Files app, calling session.show')
    }
  }

  private async list(): Promise<void> {
    if (!this.link.namesFiles) return this.store.change(() => ({ isListing: false, problem: 'This link names no files: open the Files app from the chat bar.' }))
    try {
      const byFidelity = await this.filesByFidelity(this.listed)
      this.store.change(state => ({ byFidelity, isListing: false, entries: this.shownFrom({ ...state, byFidelity }) }))
      const entries = this.state.entries
      const first = this.link.file || entries.find(entry => entry.exists && !isDrawio(entry.path))?.path || ''
      if (first) await this.open(first)
    } catch (failure) {
      this.store.change(() => ({ isListing: false, problem: `The files did not list: ${reasonOf(failure)}` }))
      this.fail(`The Files app did not list the files: ${reasonOf(failure)}`, `Opening the Files app on ${this.link.subject}`, { isShownOnPage: true })
    }
  }

  // The fidelities whose files the page lists, as the session's guidance selection covers them.
  get listed(): string[] {
    return listedBy(this.state.guidance, this.link.fidelities)
  }

  // The files shown from state, in the formats selected: the files of the fidelities listed first, among them those not
  // generated yet and a design canvas at its link; then every other file under the session's root that belongs to a
  // fidelity listed or to none. The file bar keeps the changed ones for This session.
  private shownFrom(state: FilesPage['state']): FileEntryData[] {
    const formats = selectedFormatsOf(state.guidance)
    if (this.link.isSessionFolder) return filesShown(state.byFidelity, [''], formats)
    const listed = listedBy(state.guidance, this.link.fidelities)
    return eachOnce([...filesShown(state.byFidelity, listed, formats), ...rootFilesShown(state.rootFiles ?? [], listed, formats, isNoPracticeSelected(state.guidance))])
  }

  // Every file under the session's root, read once as the page opens: what All session files lists, and This session
  // the changed ones of.
  private async readRootFiles(): Promise<void> {
    try {
      const rootFiles = (await TicketClientGenerated.named(this.api, this.link.ticket).rootFiles()) ?? []
      this.store.change(state => ({ rootFiles, entries: this.shownFrom({ ...state, rootFiles }) }))
    } catch (failure) {
      this.fail(`The Files app did not list the files under the session's root: ${reasonOf(failure)}`, 'Opening the Files app, calling ticket.root_files')
    }
  }

  // A session folder is one list of no fidelity; a ticket's fidelities are kept apart, so a practice can hide its own.
  private async filesByFidelity(slugs: string[]): Promise<FidelityFiles[]> {
    if (this.link.isSessionFolder) return [{ slug: '', entries: (await this.session.folderFiles()) ?? [] }]
    if (!slugs.length) return []
    // One call for every fidelity, which shares one look at what the branch changed.
    const bySlug = (await TicketClientGenerated.named(this.api, this.link.ticket).fidelityFiles(slugs)) ?? {}
    return slugs.map(slug => {
      const byFormat = Object.entries(bySlug[slug] ?? {})
      const formatOf = Object.fromEntries(byFormat.flatMap(([format, entries]) => entries.map(entry => [entry.path, format])))
      return { slug, entries: byFormat.flatMap(([, entries]) => entries), formatOf }
    })
  }

  // A selection drawn: the list shows its fidelities' files at once, then reads the files of any it shows for the first
  // time, such as a stage just selected, and shows them too.
  private async showSelected(): Promise<void> {
    this.store.change(state => ({ entries: this.shownFrom(state) }))
    const missing = this.listed.filter(slug => !this.state.byFidelity.some(each => each.slug === slug))
    if (this.link.isSessionFolder || this.state.isListing || !missing.length) return
    try {
      const read = await this.filesByFidelity(missing)
      this.store.change(state => ({ byFidelity: [...state.byFidelity, ...read.filter(each => !state.byFidelity.some(held => held.slug === each.slug))] }))
      this.store.change(state => ({ entries: this.shownFrom(state) }))
    } catch (failure) {
      this.fail(`The Files app did not list the files of ${missing.join(', ')}: ${reasonOf(failure)}`, 'Showing the stages and practices selected')
    }
  }

  // This session lists the files the branch changed; All session files lists every file of the fidelities listed, older
  // work included. The stages, practices and formats selected filter both.
  showScope(scope: 'session' | 'all'): void {
    this.store.change(() => ({ scope }))
  }

  // A press on a stage, practice, or format button: the session's one guidance selection, which the chat bar's buttons
  // show too.
  toggleStage(name: string): Promise<void> {
    return this.guidance.toggleStage(name)
  }

  togglePractice(key: string): Promise<void> {
    return this.guidance.togglePractice(key)
  }

  toggleFormat(label: string): Promise<void> {
    return this.guidance.toggleFormat(label)
  }

  // Why the list is empty: the formats selected hold none of the files of the fidelities listed, such as code at a stage
  // whose fidelities write only documents and diagrams; else there are no files yet.
  get emptyReason(): string {
    const chosen = (this.state.guidance?.formats ?? []).filter(format => format.is_selected).map(format => formatGlyphOf(format.label))
    const anyFiles = filesShown(this.state.byFidelity, this.listed).length > 0
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

  // A right-click on a file or folder shows its menu where the person clicked.
  openMenu(path: string, x: number, y: number): void {
    this.store.change(() => ({ menu: { path, x, y } }))
  }

  closeMenu(): void {
    this.store.change(() => ({ menu: null }))
  }

  // The file the menu is on, added whole to the context of the chat that opened the page.
  async addToContext(): Promise<void> {
    const path = this.state.menu?.path
    this.closeMenu()
    if (path) await this.addLinesToContext(path)
  }

  // A file, or lines of it, added to the context of the chat that opened the page: the session puts them in its prompt
  // box, to go with the person's next prompt, as Claude's own file viewer does.
  async addLinesToContext(path: string, lines?: { start: number; end: number }): Promise<void> {
    const name = path.split('/').at(-1) ?? path
    try {
      await this.session.addToChatContext(this.link.chat, path, lines?.start, lines?.end)
      this.toast(`${name} added to the chat's context`)
    } catch (failure) {
      this.fail(`${name} was not added to the chat's context: ${reasonOf(failure)}`, `Adding ${path} to the chat's context`)
    }
  }

  // The file or folder the menu is on, shown in the system's file browser by the Files server, on this machine.
  async reveal(): Promise<void> {
    const path = this.state.menu?.path
    this.closeMenu()
    if (!path) return
    try {
      await this.api.post(REVEAL_PATH, { path })
    } catch (failure) {
      this.fail(`${path} did not open in the file browser: ${reasonOf(failure)}`, `Opening ${path} in the file browser`)
    }
  }

  async open(path: string): Promise<void> {
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
      const file = await this.session.file(path, rules, crossFile)
      if (this.state.openPath !== path) return
      this.store.change(() => ({ file, problem: '' }))
      if (file?.comments.some(comment => comment.state === 'sent')) this.refreshTimer = setTimeout(() => void this.refreshOpen(), SENT_REFRESH_MILLISECONDS)
    } catch (failure) {
      this.store.change(() => ({ problem: `${path} did not open: ${reasonOf(failure)}` }))
      this.fail(`The Files app did not open ${path}: ${reasonOf(failure)}`, `Opening ${path} in the Files app`, { isShownOnPage: true })
    }
  }

  private stopRefreshing(): void {
    if (this.refreshTimer) clearTimeout(this.refreshTimer)
    this.refreshTimer = null
  }

  // Every failure in the page goes through here: it is shown here and sent to the chat that opened the page, which shows
  // it on its chat bar as it shows its own, so the person can have the chat fix it. A failure the page already shows in
  // its problem line gets no toast as well. Each failure is shown and sent once, however often a read every few seconds
  // or a return to the page meets it again.
  fail(failure: string, context: string, { isShownOnPage = false } = {}): void {
    if (this.toldChat.has(failure)) return
    this.toldChat.add(failure)
    if (!isShownOnPage) this.toast(failure)
    this.tellChat(failure, context)
  }

  // A failure that cannot reach the chat stays on the page, since telling the chat again would fail the same way.
  private tellChat(failure: string, context: string): void {
    if (!this.link.chat) return
    const told = ChatClientGenerated.named(this.api, this.link.chat).send('failure', JSON.stringify({ failure, context }))
    void told.catch(reason => this.toast(`The chat was not told: ${reasonOf(reason)}`))
  }

  // A toast already showing is not shown twice: toasts are known by their text, and two alike confuse the list.
  toast(text: string): void {
    if (this.state.toasts.includes(text)) return
    this.store.change(state => ({ toasts: [...state.toasts, text] }))
    setTimeout(() => this.store.change(state => ({ toasts: state.toasts.filter(shown => shown !== text) })), TOAST_MILLISECONDS)
  }

  async attempt(what: string, work: () => Promise<unknown>): Promise<boolean> {
    try {
      await work()
      return true
    } catch (failure) {
      this.fail(`${what}: ${reasonOf(failure)}`, 'A press on a comment in the Files app')
      return false
    } finally {
      await this.refreshOpen()
    }
  }
}
