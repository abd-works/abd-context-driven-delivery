import { ChatToldFailures } from '@cdd/cdd-page-failures'

import { StoryMapApi, type Send } from './story-map-api'

// What failed on the Story UI page: shown on the page until the person dismisses it, and sent to the chat that opened
// the page, once each.
export class StoryMapFailures extends ChatToldFailures {
  private shownFailure: string | null = null
  private readonly listeners = new Set<() => void>()

  constructor(chat: string, send?: Send) {
    super(chat, notTold => new StoryMapApi(notTold, send))
  }

  get shown(): string | null {
    return this.shownFailure
  }

  readonly subscribe = (listener: () => void): (() => void) => {
    this.listeners.add(listener)
    return () => this.listeners.delete(listener)
  }

  dismiss(): void {
    this.showOnly(null)
  }

  protected show(failure: string): void {
    this.showOnly(failure)
  }

  protected notTold(reason: string): void {
    this.showOnly(`The chat that opened the Story UI was not told: ${reason}`)
  }

  private showOnly(failure: string | null): void {
    this.shownFailure = failure
    for (const listener of this.listeners) listener()
  }
}
