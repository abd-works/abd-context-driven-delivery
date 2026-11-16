import { ChatToldFailures } from '@cdd/cdd-page-failures'

// What failed on the Story UI page: shown on the page until the person dismisses it, and sent to the chat that opened
// the page, once each, through the StoryMapApi the page makes for it (main.tsx).
export class StoryMapFailures extends ChatToldFailures {
  private shownFailure: string | null = null
  private readonly listeners = new Set<() => void>()

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
