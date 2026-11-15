import type { CddApi } from '@cdd/cdd-shared'
import { ChatClientGenerated } from '@cdd/harness/chat/chat'
import { FidelityProgressClientGenerated } from '@cdd/space/kanban/fidelity-progress'
import { PracticeSessionOutputClientGenerated, type PracticeSessionOutputData } from '@cdd/space/session/practice-session-output'
import { SessionClientGenerated, type FileEntryData } from '@cdd/space/session/session'

import { FileBar } from './file-bar'
import { FileCommentsActions } from './file-comments-actions'
import type { FilesLink } from './files-link'
import { DRAWIO_PATH, isDrawio } from './files-paths'
import { FilesStore, type FidelityFiles } from './files-state'

// While a comment on the open file is with a chat, the file is read again this often, so the chat's change and the
// comment's processed state show without a reload. Nothing else is read again: never the list, never a board.
export const SENT_REFRESH_MILLISECONDS = 2_000
// The session's practices and the chat bar's selection are read again this often while the page shows, so a practice
// turned on or off, or a fidelity selected on the chat bar, shows here: a page in a side pane is never focused again.
export const PRACTICES_REFRESH_MILLISECONDS = 1_000
const TOAST_MILLISECONDS = 8_000

// Which practices are on and which fidelities are selected, the one thing about them the file list depends on.
const onOff = (practices: PracticeSessionOutputData[], selected: string[]): string =>
  [...practices.map(practice => `${practice.name}:${practice.enabled}`), ...selected].join(',')

// The tab a .drawio file opens in: sent to the viewer once its address is known, closed when it never comes.
export type DrawioTab = { location: { href: string }; close(): void }

const reasonOf =(failure: unknown): string => (failure instanceof Error ? failure.message : String(failure))

// The practice that owns a fidelity, as each practice names its own fidelities.
const practiceOwning = (slug: string, practices: PracticeSessionOutputData[]): PracticeSessionOutputData | undefined =>
  practices.find(practice => practice.fidelity_slugs.includes(slug))

// The fidelities the chat bar selected that the page lists: while there are any, the page shows only theirs.
const selectedListed = (byFidelity: FidelityFiles[], selected: string[]): string[] => byFidelity.map(({ slug }) => slug).filter(slug => selected.includes(slug))

// The files the page shows, each once: those of the fidelities selected on the chat bar, else of the fidelities whose
// practice is on; a fidelity of no practice the session knows is shown.
export const filesShown = (byFidelity: FidelityFiles[], practices: PracticeSessionOutputData[], selected: string[] = []): FileEntryData[] => {
  const chosen = selectedListed(byFidelity, selected)
  const isShown = ({ slug }: FidelityFiles) => (chosen.length ? chosen.includes(slug) : (practiceOwning(slug, practices)?.enabled ?? true))
  return eachOnce(byFidelity.filter(isShown).flatMap(({ entries }) => entries))
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
  private refreshTimer: ReturnType<typeof setTimeout> | null = null
  // The failures already shown here and sent to the chat that opened the page.
  private readonly toldChat = new Set<string>()

  constructor(
    readonly api: CddApi,
    readonly link: FilesLink,
    private readonly openTab: () => DrawioTab | null = () => window.open('', '_blank'),
  ) {
    this.session = SessionClientGenerated.named(api, link.sessionFile)
    this.comments = new FileCommentsActions(this)
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
    const reread = () => void Promise.all([this.refreshOpen(), this.readPractices()])
    window.addEventListener('focus', reread)
    const practicesTimer = setInterval(() => {
      if (document.visibilityState === 'visible') void this.readPractices({ isQuiet: true })
    }, PRACTICES_REFRESH_MILLISECONDS)
    return () => {
      window.removeEventListener('error', onError)
      window.removeEventListener('unhandledrejection', onRejection)
      window.removeEventListener('focus', reread)
      clearInterval(practicesTimer)
      this.stopRefreshing()
    }
  }

  private async list(): Promise<void> {
    if (!this.link.namesFiles) return this.store.change(() => ({ isListing: false, problem: 'This link names no files: open the Files app from the chat bar.' }))
    try {
      const [byFidelity] = await Promise.all([this.filesByFidelity(), this.readPractices()])
      this.store.change(state => ({ byFidelity, entries: filesShown(byFidelity, state.practices, state.selectedFidelities), isListing: false }))
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

  // A session folder is one list of no fidelity; a ticket's fidelities are kept apart, so a practice can hide its own.
  private async filesByFidelity(): Promise<FidelityFiles[]> {
    if (this.link.isSessionFolder) return [{ slug: '', entries: (await this.session.folderFiles()) ?? [] }]
    return Promise.all(
      this.link.fidelities.map(async slug => ({ slug, entries: Object.values((await FidelityProgressClientGenerated.named(this.api, this.link.ticket, slug).files()) ?? {}).flat() })),
    )
  }

  // The session's practices, on and off, with their colours; read again while the page shows and when the person comes
  // back to it, so a practice turned on or off on the chat bar or the board shows here. The list changes only when a
  // practice did; a read that fails goes to the chat once and is tried again on the next.
  private async readPractices({ isQuiet = false } = {}): Promise<void> {
    try {
      const [shown, selectedFidelities] = await Promise.all([this.session.show(), this.selectedOnChatBar()])
      const practices = Object.values(shown?.practices ?? {})
      if (this.state.practices.length && onOff(practices, selectedFidelities) === onOff(this.state.practices, this.state.selectedFidelities)) return
      this.store.change(state => ({ practices, selectedFidelities, entries: filesShown(state.byFidelity, practices, selectedFidelities) }))
    } catch (failure) {
      this.fail(`The Files app did not read the session's practices or the chat bar's selection: ${reasonOf(failure)}`, isQuiet ? 'Reading them again every second while the page shows' : 'Opening the Files app')
    }
  }

  // The fidelities selected for the chat that opened the page, as cdd holds them for its chat bar and this page alike;
  // none for a page no chat opened.
  private async selectedOnChatBar(): Promise<string[]> {
    if (!this.link.chat) return []
    return (await ChatClientGenerated.named(this.api, this.link.chat).show())?.selectedFidelities ?? []
  }

  // Whether the page follows the chat bar's selection: while any fidelity it lists is selected there, the toggles show
  // the selected fidelities' practices, and the chat bar's dots change them.
  get isFollowingChatBar(): boolean {
    return selectedListed(this.state.byFidelity, this.state.selectedFidelities).length > 0
  }

  // Whether a practice's files are shown: one of its fidelities selected on the chat bar, else the practice turned on.
  isShown(practice: PracticeSessionOutputData): boolean {
    if (!this.isFollowingChatBar) return practice.enabled
    return practice.fidelity_slugs.some(slug => this.state.selectedFidelities.includes(slug))
  }

  // A press on a practice at the top of the page. A practice the session does not work on is turned on for it, and the
  // chat that opened the page reads the board again. A practice it works on shows or hides its files by selecting or
  // clearing its dots on that chat's chat bar, so the bar and the page always show the same fidelities.
  async togglePractice(name: string): Promise<void> {
    const practice = this.state.practices.find(each => each.name === name)
    if (!practice) return
    if (!practice.enabled || !this.link.chat) return this.enable(practice)
    await this.select(this.selectionToggling(practice))
  }

  // The session works on practice from now on, or no longer, for a page no chat opened.
  private async enable(practice: PracticeSessionOutputData): Promise<void> {
    const isTurnedOn = await this.attemptQuietly(`${practice.short_name} was not turned ${practice.enabled ? 'off' : 'on'}`, () =>
      PracticeSessionOutputClientGenerated.named(this.api, this.link.sessionFile, practice.name).enable(!practice.enabled),
    )
    if (!isTurnedOn) return
    await this.readPractices()
    if (this.link.chat) await this.attemptQuietly('The chat bar was not told to show the change', () => ChatClientGenerated.named(this.api, this.link.chat).send('refresh', 'practices'))
  }

  // The chat bar's selection with practice's listed fidelities taken out while they show, or put in while they do not. A
  // selection of every practice the session works on is no selection: the bar shows them all.
  private selectionToggling(practice: PracticeSessionOutputData): string[] {
    const listed = this.state.byFidelity.map(({ slug }) => slug)
    const working = listed.filter(slug => practiceOwning(slug, this.state.practices)?.enabled ?? true)
    const shown = this.isFollowingChatBar ? selectedListed(this.state.byFidelity, this.state.selectedFidelities) : working
    const own = listed.filter(slug => practice.fidelity_slugs.includes(slug))
    const next = own.some(slug => shown.includes(slug)) ? shown.filter(slug => !own.includes(slug)) : [...shown, ...own]
    const kept = this.state.selectedFidelities.filter(slug => !listed.includes(slug))
    return next.length === working.length && working.every(slug => next.includes(slug)) ? kept : [...kept, ...next]
  }

  // Saves the selection with cdd, which holds the one selection the chat bar's dots and this page both show, and shows
  // what cdd answered; the chat bar draws it at its next check-in.
  private async select(selectedFidelities: string[]): Promise<void> {
    let held: string[] | null = null
    const isSaved = await this.attemptQuietly('The selection was not saved', async () => {
      held = (await ChatClientGenerated.named(this.api, this.link.chat).select(selectedFidelities))?.selectedFidelities ?? []
    })
    const answered = held as string[] | null
    if (!isSaved || answered === null) return
    this.store.change(state => ({ selectedFidelities: answered, entries: filesShown(state.byFidelity, state.practices, answered) }))
  }

  // Turns on or off reading the open file's folds and broken rules from the session's graph (a second or two for a
  // changed file), and reading them with the graph holding the whole working copy (far longer); the open file is read
  // again with them. Cross-file reads the rules too.
  async toggleRules(): Promise<void> {
    this.store.change(({ reads }) => ({ reads: { rules: !reads.rules, crossFile: reads.rules ? false : reads.crossFile } }))
    await this.refreshOpen()
  }

  async toggleCrossFile(): Promise<void> {
    this.store.change(({ reads }) => ({ reads: { rules: !reads.crossFile || reads.rules, crossFile: !reads.crossFile } }))
    await this.refreshOpen()
  }

  async open(path: string): Promise<void> {
    if (isDrawio(path)) return this.openDrawio(path)
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

  // The new tab opens while the person's click is still running, before the viewer's address comes back: a tab opened
  // after a wait is no longer the click's, and the browser pane then loads the viewer in this tab instead, so the file
  // list was lost. This tab keeps the list; the new one is sent to the viewer once its address arrives.
  private async openDrawio(path: string): Promise<void> {
    const tab = this.openTab()
    try {
      const opened = await this.api.post<{ url: string }>(DRAWIO_PATH, { path })
      if (!opened?.url) throw new Error('the viewer sent back no address')
      if (!tab) return this.fail(`${path} did not open in the draw.io viewer: the browser refused a new tab`, `Opening ${path} from the Files app`)
      tab.location.href = opened.url
    } catch (failure) {
      tab?.close()
      this.fail(`${path} did not open in the draw.io viewer: ${reasonOf(failure)}`, `Opening ${path} from the Files app`)
    }
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

  // A call whose failure is shown as a toast, with nothing read again after it.
  private async attemptQuietly(what: string, work: () => Promise<unknown>): Promise<boolean> {
    try {
      await work()
      return true
    } catch (failure) {
      this.fail(`${what}: ${reasonOf(failure)}`, 'A press in the Files app')
      return false
    }
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
