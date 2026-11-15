import type { CddApi } from '@cdd/cdd-shared'
import { ChatClientGenerated } from '@cdd/harness/chat/chat'
import { FidelityProgressClientGenerated } from '@cdd/space/kanban/fidelity-progress'
import { PracticeSessionOutputClientGenerated, type PracticeSessionOutputData } from '@cdd/space/session/practice-session-output'
import { SessionClientGenerated, type FileEntryData } from '@cdd/space/session/session'

import { FileBar } from './file-bar'
import { FileCommentsActions } from './file-comments-actions'
import type { FilesLink } from './files-link'
import { isDrawio } from './files-paths'
import { FilesStore, type FidelityFiles } from './files-state'
import { chosenFormatsOf, chosenKeyOf, FormatChips, formatGlyphOf } from './format-chips'

// While a comment on the open file is with a chat, the file is read again this often, so the chat's change and the
// comment's processed state show without a reload. Nothing else is read again: never the list, never a board.
export const SENT_REFRESH_MILLISECONDS = 2_000
// The session's practices and the chat bar's selection are read again this often while the page shows, so a practice
// turned on or off, or a fidelity selected on the chat bar, shows here: a page in a side pane is never focused again.
export const PRACTICES_REFRESH_MILLISECONDS = 1_000
const TOAST_MILLISECONDS = 8_000

// Which practices are on and which fidelities are selected, the one thing about them the file list depends on.
const onOff = (practices: PracticeSessionOutputData[], selected: string[], formats = ''): string =>
  [...practices.map(practice => `${practice.name}:${practice.enabled}`), ...selected, formats].join(',')

const reasonOf =(failure: unknown): string => (failure instanceof Error ? failure.message : String(failure))

// The practice that owns a fidelity, as each practice names its own fidelities.
const practiceOwning = (slug: string, practices: PracticeSessionOutputData[]): PracticeSessionOutputData | undefined =>
  practices.find(practice => practice.fidelity_slugs.includes(slug))

// The fidelities the chat bar selected that the page lists: while there are any, the page shows only theirs.
const selectedListed = (byFidelity: FidelityFiles[], selected: string[]): string[] => byFidelity.map(({ slug }) => slug).filter(slug => selected.includes(slug))

// The files the page shows, each once: those of the fidelities selected on the chat bar, else of the fidelities whose
// practice is on, a fidelity of no practice the session knows shown; and of those, only the ones in a format chosen,
// while any is.
export const filesShown = (fidelities: FidelityFiles[], practices: PracticeSessionOutputData[], selected: string[] = [], formats: string[] = [], listed?: string[]): FileEntryData[] => {
  const byFidelity = listed ? fidelities.filter(({ slug }) => listed.includes(slug)) : fidelities
  const chosen = selectedListed(byFidelity, selected)
  const isShown = ({ slug }: FidelityFiles) => (chosen.length ? chosen.includes(slug) : (practiceOwning(slug, practices)?.enabled ?? true))
  const inFormat = ({ entries, formatOf = {} }: FidelityFiles) => (formats.length ? entries.filter(entry => formats.includes(formatOf[entry.path] ?? '')) : entries)
  return eachOnce(byFidelity.filter(isShown).flatMap(inFormat))
}

// The fidelities of the stages shown, in the board's order, none when every stage is turned off; before the chat bar or
// the page chose, those the link names, the stage the page was opened on.
export const fidelitiesOfStages = (stages: Record<string, string[]>, shown: string[], linked: string[], isChosen = true): string[] => {
  if (!isChosen || !Object.keys(stages).length) return linked
  return Object.keys(stages).filter(stage => shown.includes(stage)).flatMap(stage => stages[stage] ?? [])
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
  readonly formatChips: FormatChips
  private refreshTimer: ReturnType<typeof setTimeout> | null = null
  // The failures already shown here and sent to the chat that opened the page.
  private readonly toldChat = new Set<string>()

  constructor(
    readonly api: CddApi,
    readonly link: FilesLink,
  ) {
    this.session = SessionClientGenerated.named(api, link.sessionFile)
    this.comments = new FileCommentsActions(this)
    this.formatChips = new FormatChips(api, link, this.store)
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
      await this.readPractices()
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

  // The fidelities whose files the page lists: those of the stages shown, else the ones the link names.
  get listed(): string[] {
    return fidelitiesOfStages(this.state.stages, this.state.shownStages, this.link.fidelities, this.state.isStageChosen)
  }

  // The files shown from state: of the fidelities listed, their practices or the chat bar's selection, and the formats
  // chosen.
  private shownFrom(state: FilesPage['state']): FileEntryData[] {
    const listed = fidelitiesOfStages(state.stages, state.shownStages, this.link.fidelities, state.isStageChosen)
    return filesShown(state.byFidelity, state.practices, state.selectedFidelities, chosenFormatsOf(state.formatChoices), this.link.isSessionFolder ? undefined : listed)
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

  // The session's practices, on and off, with their colours; read again while the page shows and when the person comes
  // back to it, so a practice turned on or off on the chat bar or the board shows here. The list changes only when a
  // practice did; a read that fails goes to the chat once and is tried again on the next.
  private async readPractices({ isQuiet = false } = {}): Promise<void> {
    try {
      const [shown, chat] = await Promise.all([this.session.show(), this.chatShown()])
      const practices = Object.values(shown?.practices ?? {})
      const listed = fidelitiesOfStages(chat.stages, chat.shownStages, this.link.fidelities, chat.isStageChosen)
      const formatChoices = await this.formatChips.read(this.worked(listed, practices))
      const now = { practices, selectedFidelities: chat.selectedFidelities, formatChoices, stages: chat.stages, shownStages: chat.shownStages, isStageChosen: chat.isStageChosen }
      if (this.state.practices.length && this.isUnchanged(now) && !this.missing(listed).length) return
      // The buttons redraw at once; a stage's files read the first time it shows come after.
      this.store.change(state => ({ ...now, entries: this.shownFrom({ ...state, ...now }) }))
      await this.loadMissing(listed)
      this.store.change(state => ({ entries: this.shownFrom(state) }))
    } catch (failure) {
      this.fail(`The Files app did not read the session's practices, formats, stages or the chat bar's selection: ${reasonOf(failure)}`, isQuiet ? 'Reading them again every second while the page shows' : 'Opening the Files app')
    }
  }

  private isUnchanged(now: Pick<FilesPage['state'], 'practices' | 'selectedFidelities' | 'formatChoices' | 'stages' | 'shownStages' | 'isStageChosen'>): boolean {
    const was = this.state
    const key = (of: typeof now) => [onOff(of.practices, of.selectedFidelities, chosenKeyOf(of.formatChoices)), of.formatChoices.length, JSON.stringify(of.stages), of.shownStages.join(','), of.isStageChosen].join('|')
    return key(now) === key(was)
  }

  // The fidelities listed whose practice the session works on: those the chat bar's dots show, which the format chips are
  // read and chosen for on both, so a chip reads the same here and on the bar.
  private worked(listed: string[], practices: PracticeSessionOutputData[]): string[] {
    return listed.filter(slug => practiceOwning(slug, practices)?.enabled ?? true)
  }

  // The fidelities listed whose files the page has not read yet.
  private missing(listed: string[]): string[] {
    if (this.link.isSessionFolder || this.state.isListing) return []
    return listed.filter(slug => !this.state.byFidelity.some(each => each.slug === slug))
  }

  // The files of the fidelities listed that the page has not read yet, such as a stage turned on for the first time.
  private async loadMissing(listed: string[]): Promise<void> {
    if (this.link.isSessionFolder || this.state.isListing) return
    const missing = this.missing(listed)
    if (!missing.length) return
    const read = await this.filesByFidelity(missing)
    this.store.change(state => ({ byFidelity: [...state.byFidelity, ...read] }))
  }

  // What cdd holds for the chat that opened the page: the fidelities selected and the stages shown, the chat bar's and
  // this page's alike; none for a page no chat opened.
  private async chatShown(): Promise<{ selectedFidelities: string[]; shownStages: string[]; stages: Record<string, string[]>; isStageChosen: boolean }> {
    if (!this.link.chat) return { selectedFidelities: [], shownStages: [], stages: {}, isStageChosen: false }
    const chat = await ChatClientGenerated.named(this.api, this.link.chat).show()
    return { selectedFidelities: chat?.selectedFidelities ?? [], shownStages: chat?.shownStages ?? [], stages: chat?.stages ?? {}, isStageChosen: chat?.isStageChosen ?? false }
  }

  // A press on a stage button shows that stage's files beside those shown, or no longer, here and on the chat bar, the
  // one choice cdd holds; none left, none shows.
  async toggleStage(stage: string): Promise<void> {
    if (!this.link.chat) return
    const shown = this.shownStageNames
    const next = shown.includes(stage) ? shown.filter(each => each !== stage) : [...shown, stage]
    // The button redraws at once; cdd's answer and the stage's files follow.
    this.store.change(() => ({ shownStages: next, isStageChosen: true }))
    await this.attemptQuietly(`The ${stage} stage was not shown`, () => ChatClientGenerated.named(this.api, this.link.chat).showStages(next))
    await this.readPractices()
  }

  // The stages whose files show: those turned on, none included; before the chat bar or this page chose, the stage the
  // link's fidelities are in.
  get shownStageNames(): string[] {
    const { stages, shownStages, isStageChosen } = this.state
    if (isStageChosen) return shownStages
    return Object.keys(stages).filter(stage => (stages[stage] ?? []).some(slug => this.link.fidelities.includes(slug)))
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

  // Why the list is empty: the formats chosen hold none of the files the practices shown have, such as code at a stage
  // whose fidelities write only documents and diagrams; else there are no files yet.
  get emptyReason(): string {
    const chosen = this.state.formatChoices.filter(choice => choice.is_chosen).map(choice => formatGlyphOf(choice.label))
    const anyFiles = filesShown(this.state.byFidelity, this.state.practices, this.state.selectedFidelities, [], this.listed).length > 0
    if (chosen.length && anyFiles) return `None of these files is in the formats chosen (${chosen.join(' ')}): press a chosen format to show every format.`
    return 'No files here yet.'
  }

  // A press on a format chip at the top of the page chooses that format in the session, or no longer, for every fidelity
  // the page lists, as the chat bar's chip does, and the list shows only the files in the formats chosen; the chat that
  // opened the page reads its chips again.
  async toggleFormat(label: string): Promise<void> {
    const fidelities = this.worked(this.listed, this.state.practices)
    const chip = this.state.formatChoices.find(choice => choice.label === label)
    if (!chip) return
    let answered: Awaited<ReturnType<FormatChips['toggle']>> = null
    const isChosen = await this.attemptQuietly(`The ${label} format was not chosen`, async () => {
      answered = await this.formatChips.toggle(label, fidelities)
    })
    const formatChoices = answered as Awaited<ReturnType<FormatChips['toggle']>>
    if (!isChosen || !formatChoices) return
    this.store.change(state => ({ formatChoices, entries: this.shownFrom({ ...state, formatChoices }) }))
    if (this.link.chat) await this.attemptQuietly('The chat bar was not told to show the format', () => ChatClientGenerated.named(this.api, this.link.chat).send('refresh', 'formats'))
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
