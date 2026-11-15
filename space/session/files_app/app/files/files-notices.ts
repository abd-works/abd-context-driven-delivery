import type { CddApi } from '@cdd/cdd-shared'
import { ChatClientGenerated } from '@cdd/harness/chat/chat'

import type { FilesStore } from './files-state'

const TOAST_MILLISECONDS = 8_000

const reasonOf = (failure: unknown): string => (failure instanceof Error ? failure.message : String(failure))

// What the page tells the person: a toast for what happened, and every failure, which also goes to the chat that opened
// the page, so the chat bar shows it as it shows its own and the person can have the chat fix it.
export class FilesNotices {
  // The failures already shown here and sent to the chat that opened the page.
  private readonly toldChat = new Set<string>()

  constructor(
    private readonly store: FilesStore,
    private readonly api: CddApi,
    private readonly chat: string,
  ) {}

  // A failure the page already shows in its problem line gets no toast as well. Each failure is shown and sent once,
  // however often a read every few seconds or a return to the page meets it again.
  fail(failure: string, context: string, { isShownOnPage = false } = {}): void {
    if (this.toldChat.has(failure)) return
    this.toldChat.add(failure)
    if (!isShownOnPage) this.toast(failure)
    this.tellChat(failure, context)
  }

  // A toast already showing is not shown twice: toasts are known by their text, and two alike confuse the list.
  toast(text: string): void {
    if (this.store.state.toasts.includes(text)) return
    this.store.change(state => ({ toasts: [...state.toasts, text] }))
    setTimeout(() => this.store.change(state => ({ toasts: state.toasts.filter(shown => shown !== text) })), TOAST_MILLISECONDS)
  }

  // A failure that cannot reach the chat stays on the page, since telling the chat again would fail the same way.
  private tellChat(failure: string, context: string): void {
    if (!this.chat) return
    const told = ChatClientGenerated.named(this.api, this.chat).send('failure', JSON.stringify({ failure, context }))
    void told.catch(reason => this.toast(`The chat was not told: ${reasonOf(reason)}`))
  }
}
