import type { CddApi } from '@cdd/cdd-shared'
import { ChatClientGenerated } from '@cdd/harness/chat/chat'
import { FidelityProgressClientGenerated } from '@cdd/space/kanban/fidelity-progress'
import { PracticeSessionOutputClientGenerated, type PracticeSessionOutputData } from '@cdd/space/session/practice-session-output'
import { SessionClientGenerated, type FileEntryData } from '@cdd/space/session/session'

import { FileCommentsActions } from './file-comments-actions'
import type { FilesLink } from './files-link'
import { DRAWIO_PATH, isDrawio } from './files-paths'
import { FilesStore, type FidelityFiles } from './files-state'

// While a comment on the open file is with a chat, the file is read again this often, so the chat's change and the
// comment's processed state show without a reload. Nothing else is read again: never the list, never a board.
export const SENT_REFRESH_MILLISECONDS = 2_000
const TOAST_MILLISECONDS = 8_000

// The tab a .drawio file opens in: sent to the viewer once its address is known, closed when it never comes.
export type DrawioTab = { location: { href: string }; close(): void }

const reasonOf =(failure: unknown): string => (failure instanceof Error ? failure.message : String(failure))

// The practice that owns a fidelity, as each practice names its own fidelities.
const practiceOwning = (slug: string, practices: PracticeSessionOutputData[]): PracticeSessionOutputData | undefined =>
  practices.find(practice => practice.fidelity_slugs.includes(slug))

// The files of the fidelities whose practice is on, each once; a fidelity of no practice the session knows is shown.
export const filesShown = (byFidelity: FidelityFiles[], practices: PracticeSessionOutputData[]): FileEntryData[] =>
  eachOnce(byFidelity.filter(({ slug }) => practiceOwning(slug, practices)?.enabled ?? true).flatMap(({ entries }) => entries))

// Each file once, in the order its fidelities and formats send them.
const eachOnce = (entries: FileEntryData[]): FileEntryData[] => entries.filter((entry, index) => entries.findIndex(other => other.path === entry.path) === index)

// The Files app's page: the files its link names, read once, and the one open, read when opened and again while a
// comment on it is with a chat. A .drawio file opens in the draw.io viewer instead.
export class FilesPage {
  readonly store = new FilesStore()
  readonly session: SessionClientGenerated
  readonly comments: FileCommentsActions
  private refreshTimer: ReturnType<typeof setTimeout> | null = null

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
    void this.list()
    const reread = () => void Promise.all([this.refreshOpen(), this.readPractices()])
    window.addEventListener('focus', reread)
    return () => {
      window.removeEventListener('focus', reread)
      this.stopRefreshing()
    }
  }

  private async list(): Promise<void> {
    if (!this.link.namesFiles) return this.store.change(() => ({ isListing: false, problem: 'This link names no files: open the Files app from the chat bar.' }))
    try {
      const [byFidelity] = await Promise.all([this.filesByFidelity(), this.readPractices()])
      this.store.change(state => ({ byFidelity, entries: filesShown(byFidelity, state.practices), isListing: false }))
      const entries = this.state.entries
      // A .drawio file opens in a tab of its own only on a click, so a link naming one opens the first other file here.
      const named = isDrawio(this.link.file) ? '' : this.link.file
      const first = named || entries.find(entry => entry.exists && !isDrawio(entry.path))?.path || ''
      if (first) await this.open(first)
    } catch (failure) {
      this.store.change(() => ({ isListing: false, problem: `The files did not list: ${reasonOf(failure)}` }))
    }
  }

  // A session folder is one list of no fidelity; a ticket's fidelities are kept apart, so a practice can hide its own.
  private async filesByFidelity(): Promise<FidelityFiles[]> {
    if (this.link.isSessionFolder) return [{ slug: '', entries: (await this.session.folderFiles()) ?? [] }]
    return Promise.all(
      this.link.fidelities.map(async slug => ({ slug, entries: Object.values((await FidelityProgressClientGenerated.named(this.api, this.link.ticket, slug).files()) ?? {}).flat() })),
    )
  }

  // The session's practices, on and off, with their colours; read again when the person comes back to the page, so a
  // practice turned on or off on the chat bar or the board shows here.
  async readPractices(): Promise<void> {
    try {
      const shown = await this.session.show()
      const practices = Object.values(shown?.practices ?? {})
      this.store.change(state => ({ practices, entries: filesShown(state.byFidelity, practices) }))
    } catch (failure) {
      this.toast(`The session's practices did not load: ${reasonOf(failure)}`)
    }
  }

  // The practices toggled at the top of the page are the practices the session works on: a press turns one on or off
  // for the session, the list shows or hides its files, and the chat that opened the page reads the board again, so its
  // chat bar shows the same practices.
  async togglePractice(name: string): Promise<void> {
    const practice = this.state.practices.find(each => each.name === name)
    if (!practice) return
    const isTurnedOn = await this.attemptQuietly(`${practice.short_name} was not turned ${practice.enabled ? 'off' : 'on'}`, () =>
      PracticeSessionOutputClientGenerated.named(this.api, this.link.sessionFile, name).enable(!practice.enabled),
    )
    if (!isTurnedOn) return
    await this.readPractices()
    if (this.link.chat) await this.attemptQuietly('The chat bar was not told to show the change', () => ChatClientGenerated.named(this.api, this.link.chat).send('refresh', 'practices'))
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
      const file = await this.session.file(path)
      if (this.state.openPath !== path) return
      this.store.change(() => ({ file, problem: '' }))
      if (file?.comments.some(comment => comment.state === 'sent')) this.refreshTimer = setTimeout(() => void this.refreshOpen(), SENT_REFRESH_MILLISECONDS)
    } catch (failure) {
      this.store.change(() => ({ problem: `${path} did not open: ${reasonOf(failure)}` }))
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
      if (!tab) return this.toast(`${path} did not open in the draw.io viewer: the browser refused a new tab`)
      tab.location.href = opened.url
    } catch (failure) {
      tab?.close()
      this.toast(`${path} did not open in the draw.io viewer: ${reasonOf(failure)}`)
    }
  }

  toast(text: string): void {
    this.store.change(state => ({ toasts: [...state.toasts, text] }))
    setTimeout(() => this.store.change(state => ({ toasts: state.toasts.filter(shown => shown !== text) })), TOAST_MILLISECONDS)
  }

  // A call whose failure is shown as a toast, with nothing read again after it.
  private async attemptQuietly(what: string, work: () => Promise<unknown>): Promise<boolean> {
    try {
      await work()
      return true
    } catch (failure) {
      this.toast(`${what}: ${reasonOf(failure)}`)
      return false
    }
  }

  async attempt(what: string, work: () => Promise<unknown>): Promise<boolean> {
    try {
      await work()
      return true
    } catch (failure) {
      this.toast(`${what}: ${reasonOf(failure)}`)
      return false
    } finally {
      await this.refreshOpen()
    }
  }
}
