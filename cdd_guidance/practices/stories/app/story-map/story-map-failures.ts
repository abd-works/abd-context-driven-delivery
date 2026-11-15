import { ChatClientGenerated } from '@cdd/harness/chat/chat'

import { StoryMapApi, type Send } from './story-map-api'

const reasonOf = (failure: unknown): string => (failure instanceof Error ? failure.message : String(failure))

// What failed on the Story UI page: shown on the page until the person dismisses it, and sent to the chat that opened
// the page (its ?chat= link), which shows it on its chat bar so the person can have that chat fix it. A failure the page
// meets again, as the read every two seconds does, goes to the chat once.
export class StoryMapFailures {
  private shownFailure: string | null = null
  private readonly listeners = new Set<() => void>()
  // The failures already sent to the chat that opened the page.
  private readonly toldChat = new Set<string>()
  // Telling the chat goes through an api of its own, whose failures are only shown: sending them to the chat again
  // would fail the same way.
  private readonly chatApi: StoryMapApi

  constructor(
    readonly chat: string,
    send?: Send,
  ) {
    this.chatApi = new StoryMapApi(failure => this.show(`The chat that opened the Story UI was not told: ${failure}`), send)
  }

  get shown(): string | null {
    return this.shownFailure
  }

  readonly subscribe = (listener: () => void): (() => void) => {
    this.listeners.add(listener)
    return () => this.listeners.delete(listener)
  }

  // An arrow, so the api and the window's listeners can be handed it as it is.
  readonly fail = (failure: string, context: string): void => {
    this.show(failure)
    this.tellChat(failure, context)
  }

  // A thrown failure, said in its own words.
  readonly failWith = (failure: unknown, context: string): void => this.fail(reasonOf(failure), context)

  dismiss(): void {
    this.show(null)
  }

  private tellChat(failure: string, context: string): void {
    if (!this.chat || this.toldChat.has(failure)) return
    this.toldChat.add(failure)
    const told = ChatClientGenerated.named(this.chatApi, this.chat).send('failure', JSON.stringify({ failure, context }))
    void told.catch(reason => this.show(`The chat that opened the Story UI was not told: ${reasonOf(reason)}`))
  }

  private show(failure: string | null): void {
    this.shownFailure = failure
    for (const listener of this.listeners) listener()
  }
}
