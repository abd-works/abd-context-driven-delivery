import { chatOfPage, projectOfPage } from '@cdd/cdd-shared'
import { ChatClientGenerated } from '@cdd/harness/chat/chat'

import { BoardApi, type Send } from './board-api'
import type { BoardStore } from '../shared/board-store'

const reasonOf = (failure: unknown): string => (failure instanceof Error ? failure.message : String(failure))

// What failed on the board page: shown on the page, and sent to the chat that opened the page (its ?chat= link, not a
// chat picked in the chat list), which shows it on its chat bar so the person can have that chat fix it. A failure the
// page meets again, as the reads every two seconds do, goes to the chat once.
export class PageFailures {
  // The failures already sent to the chat that opened the page.
  private readonly toldChat = new Set<string>()
  // Telling the chat goes through an api of its own, whose failures are only shown: sending them to the chat again
  // would fail the same way.
  private readonly chatApi: BoardApi

  constructor(
    private readonly store: BoardStore,
    send: Send,
    readonly chat: string = chatOfPage(),
  ) {
    const toastNotTold = (failure: string) => store.toast(`The chat that opened the board was not told: ${failure}`, true)
    const notTold = { fail: toastNotTold, serverDown: toastNotTold }
    this.chatApi = new BoardApi(store, notTold, send, projectOfPage(), false)
  }

  // An arrow, so the window's listeners can be handed it as it is.
  readonly fail = (failure: string, context: string): void => {
    this.store.toast(failure, true)
    this.tellChat(failure, context)
  }

  // A thrown failure, said in its own words.
  readonly failWith = (failure: unknown, context: string): void => this.fail(reasonOf(failure), context)

  // A server that does not answer shows in the band across the page, not as a toast, and is told to the chat.
  serverDown(failure: string, context: string): void {
    this.store.change({ serverFailure: failure })
    this.tellChat(failure, context)
  }

  private tellChat(failure: string, context: string): void {
    if (!this.chat || this.toldChat.has(failure)) return
    this.toldChat.add(failure)
    const told = ChatClientGenerated.named(this.chatApi, this.chat).send('failure', JSON.stringify({ failure, context }))
    void told.catch(reason => this.store.toast(`The chat that opened the board was not told: ${reasonOf(reason)}`, true))
  }
}
