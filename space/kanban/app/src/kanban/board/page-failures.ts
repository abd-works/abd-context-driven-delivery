import { chatOfPage, projectOfPage } from '@cdd/cdd-shared'
import { ChatToldFailures } from '@cdd/cdd-page-failures'

import { BoardApi, type Send } from './board-api'
import type { BoardStore } from '../shared/board-store'

// What failed on the board page: shown on the page as a toast, and sent to the chat that opened the page, once each.
export class PageFailures extends ChatToldFailures {
  constructor(
    private readonly store: BoardStore,
    send: Send,
    chat: string = chatOfPage(),
  ) {
    super(chat, notTold => new BoardApi(store, { fail: notTold, serverDown: notTold }, send, projectOfPage(), false))
  }

  // A server that does not answer shows in the band across the page, not as a toast, and is told to the chat.
  serverDown(failure: string, context: string): void {
    this.store.change({ serverFailure: failure })
    this.tellChat(failure, context)
  }

  protected show(failure: string): void {
    this.store.toast(failure, true)
  }

  protected notTold(reason: string): void {
    this.store.toast(`The chat that opened the board was not told: ${reason}`, true)
  }
}
