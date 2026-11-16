import type { CddApi } from './cdd-shared'
import { ChatClientGenerated } from '__CHAT__'

// A thrown failure in its own words.
export const reasonOf = (failure: unknown): string => (failure instanceof Error ? failure.message : String(failure))

// What failed on a page a chat opened: shown on the page, and sent to the chat that opened it (its ?chat= link, not a
// chat picked in a chat list), which shows it on its chat bar so the person can have that chat fix it. A failure the
// page meets again, as a read every two seconds does, goes to the chat once. Each page says how it shows a failure.
export abstract class ChatToldFailures {
  // The failures already sent to the chat that opened the page.
  private readonly toldChat = new Set<string>()

  // Telling the chat goes through an api of its own, whose failures are only said on the page: sending them to the chat
  // again would fail the same way.
  private readonly chatApi: CddApi

  // apiTelling makes that api, handed what the page says when the chat could not be told.
  constructor(
    readonly chat: string,
    apiTelling: (notTold: (reason: string) => void) => CddApi,
  ) {
    this.chatApi = apiTelling(reason => this.notTold(reason))
  }

  // An arrow, so an api and the window's listeners can be handed it as it is.
  readonly fail = (failure: string, context: string): void => {
    this.show(failure)
    this.tellChat(failure, context)
  }

  // A thrown failure, said in its own words.
  readonly failWith = (failure: unknown, context: string): void => this.fail(reasonOf(failure), context)

  // Show failure on the page.
  protected abstract show(failure: string): void

  // What the page says when the chat that opened it could not be told.
  protected abstract notTold(reason: string): void

  protected tellChat(failure: string, context: string): void {
    if (!this.chat || this.toldChat.has(failure)) return
    this.toldChat.add(failure)
    const told = ChatClientGenerated.named(this.chatApi, this.chat).send('failure', JSON.stringify({ failure, context }))
    void told.catch(reason => this.notTold(reasonOf(reason)))
  }
}
