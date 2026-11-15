import type { CddApi } from '@cdd/cdd-shared'
import { ChatClientGenerated } from '@cdd/harness/chat/chat'
import { FidelityProgressClientGenerated } from '@cdd/space/kanban/fidelity-progress'
import { SessionClientGenerated, type FileEntryData, type GuidanceSelectionData } from '@cdd/space/session/session'

import { FileBar } from './file-bar'
import { FileCommentsActions } from './file-comments-actions'
import type { FilesLink } from './files-link'
import { isDrawio } from './files-paths'
import { FilesStore, type FidelityFiles } from './files-state'
import { formatGlyphOf } from './format-chips'
import { GuidanceSelector } from './guidance-selector'

// While a comment on the open file is with a chat, the file is read again this often, so the chat's change and the
// comment's processed state show without a reload. Nothing else is read again: never the list, never a board.
export const SENT_REFRESH_MILLISECONDS = 2_000
const TOAST_MILLISECONDS = 8_000

const reasonOf = (failure: unknown): string => (failure instanceof Error ? failure.message : String(failure))

// The fidelities whose files the page lists: those the session's guidance selection covers, its stages selected by its
// practices selected; before any stage was selected, the ones the link names.
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

// Each file once, in the order its fidelities and formats send them.
const eachOnce = (entries: FileEntryData[]): FileEntryData[] => entries.filter((entry, index) => entries.findIndex(other => other.path === entry.path) === index)

// The Files app's page: the files its link names, read once, and the one open, read when opened and again while a
// comment on it is with a chat. A .drawio file opens in the draw.io viewer instead.
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
    const stopFollowing = this.link.isSessionFolder ? () => undefined : this.guidance.follow()
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

  private async list(): Promise<void> {
    if (!this.link.namesFiles) return this.store.change(() => ({ isListing: false, problem: 'This link names no files: open the Files app from the chat bar.' }))
    try {
      const byFidelity = await this.filesByFidelity(this.listed)
      this.store.change(state => ({ byFidelity, isListing: false, entries: this.shownFrom({ ...state, byFidelity }) }))
      const entries = this.state.entries
      // A .drawio file opens in a tab of its own only on a click, so a link naming one opens the first other file here.
      const named = isDrawio(this.link.file) ? '' : this.link.file
      const first = named || entries.find(entry => entry.exists && !isDrawio(entry.path))?.path || ''
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

  // The files shown from state: of the fidelities listed, those in the formats selected.
  private shownFrom(state: FilesPage['state']): FileEntryData[] {
    return filesShown(state.byFidelity, this.link.isSessionFolder ? [''] : listedBy(state.guidance, this.link.fidelities), selectedFormatsOf(state.guidance))
  }

  // A session folder is one list of no fidelity; a ticket's fidelities are kept apart, so a practice can hide its own.
  private async filesByFidelity(slugs: string[]): Promise<FidelityFiles[]> {
    if (this.link.isSessionFolder) return [{ slug: '', entries: (await this.session.folderFiles()) ?? [] }]
    return Promise.all(
      slugs.map(async slug => {
        const byFormat = Object.entries((await FidelityProgressClientGenerated.named(this.api, this.link.ticket, slug).files()) ?? {})
        const formatOf = Object.fromEntries(byFormat.flatMap(([format, entries]) => entries.map(entry => [entry.path, format])))
        return { slug, entries: byFormat.flatMap(([, entries]) => entries), formatOf }
      }),
    )
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

  async open(path: string): Promise<void> {
    // A .drawio file is a link to the draw.io viewer, which opens in a tab of its own; this tab keeps its file list.
    if (isDrawio(path)) return
    this.store.change(() => ({ openPath: path, file: null }))
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
