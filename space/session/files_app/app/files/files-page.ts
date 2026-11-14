import type { CddApi } from '@cdd/cdd-shared'
import { FidelityProgressClientGenerated } from '@cdd/space/kanban/fidelity-progress'
import { SessionClientGenerated, type FileEntryData } from '@cdd/space/session/session'

import { FileCommentsActions } from './file-comments-actions'
import type { FilesLink } from './files-link'
import { DRAWIO_PATH, isDrawio } from './files-paths'
import { FilesStore } from './files-state'

// While a comment on the open file is with a chat, the file is read again this often, so the chat's change and the
// comment's processed state show without a reload. Nothing else is read again: never the list, never a board.
export const SENT_REFRESH_MILLISECONDS = 2_000
const TOAST_MILLISECONDS = 8_000

const reasonOf = (failure: unknown): string => (failure instanceof Error ? failure.message : String(failure))

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
    private readonly openWindow: (url: string) => void = url => void window.open(url, '_blank'),
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
    const reread = () => void this.refreshOpen()
    window.addEventListener('focus', reread)
    return () => {
      window.removeEventListener('focus', reread)
      this.stopRefreshing()
    }
  }

  private async list(): Promise<void> {
    if (!this.link.namesFiles) return this.store.change(() => ({ isListing: false, problem: 'This link names no files: open the Files app from the chat bar.' }))
    try {
      const entries = eachOnce(await this.entries())
      this.store.change(() => ({ entries, isListing: false }))
      const first = this.link.file || entries.find(entry => entry.exists && !isDrawio(entry.path))?.path || ''
      if (first) await this.open(first)
    } catch (failure) {
      this.store.change(() => ({ isListing: false, problem: `The files did not list: ${reasonOf(failure)}` }))
    }
  }

  private async entries(): Promise<FileEntryData[]> {
    if (this.link.isSessionFolder) return (await this.session.folderFiles()) ?? []
    const byFidelity = await Promise.all(this.link.fidelities.map(slug => FidelityProgressClientGenerated.named(this.api, this.link.ticket, slug).files()))
    return byFidelity.flatMap(formats => Object.values(formats ?? {}).flat())
  }

  async open(path: string): Promise<void> {
    if (isDrawio(path)) return this.openDrawio(path)
    this.store.change(() => ({ openPath: path, file: null }))
    await this.refreshOpen()
  }

  // The open file read again through the session: its text, comments, folds, violations and the chat's changes.
  async refreshOpen(): Promise<void> {
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

  private async openDrawio(path: string): Promise<void> {
    try {
      const opened = await this.api.post<{ url: string }>(DRAWIO_PATH, { path })
      if (opened?.url) this.openWindow(opened.url)
    } catch (failure) {
      this.toast(`${path} did not open in the draw.io viewer: ${reasonOf(failure)}`)
    }
  }

  toast(text: string): void {
    this.store.change(state => ({ toasts: [...state.toasts, text] }))
    setTimeout(() => this.store.change(state => ({ toasts: state.toasts.filter(shown => shown !== text) })), TOAST_MILLISECONDS)
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
