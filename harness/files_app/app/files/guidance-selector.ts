import type { GuidanceSelectionData } from '@cdd/space/session/session'

import type { FilesPage } from './files-page'
import { reasonOf } from './reason'

// The part of the selection a press toggles, as Session.toggle_guidance names it.
export type SelectionPart = 'stage' | 'practice' | 'format'

// How long the page waits before reading the selection again after a read failed, so a cdd server restarting for a
// repin is not asked many times a second.
const RETRY_MILLISECONDS = 1_000

const wait = (milliseconds: number) => new Promise(resolve => setTimeout(resolve, milliseconds))

// The session's guidance selection as the page shows and changes it: the stages, practices, and formats selected, the
// one selection the chat bar's buttons show too. The session holds it; the page follows it with one waiting read
// (Session.guidance_selection_after), so a change made anywhere draws here in a fraction of a second. A press sends one
// toggle (Session.toggle_guidance) and draws its answer; any answer older than the version drawn is ignored, so a late
// read never undoes a press.
// The page it belongs to holds the session, the store it draws into, and the notices a failure is told through, and
// reads the files of fidelities it shows for the first time once a selection is drawn.
export class GuidanceSelector {
  private drawnVersion = -1
  private isFollowing = false
  private isPressing = false

  constructor(private readonly page: FilesPage) {}

  get selection(): GuidanceSelectionData | null {
    return this.page.store.state.guidance
  }

  // Follow the selection until the answer stops it: read it now, then wait for each change.
  follow(): () => void {
    this.isFollowing = true
    void this.keepFollowing()
    return () => {
      this.isFollowing = false
    }
  }

  // A press on a stage, a practice's toggle, or a format chip: the session works out the selection it leaves, which can
  // take a while with many files to filter, so the page says what it is filtering by until the list is read again, and a
  // second press while a press is filtering starts nothing. A press made while the page reads the list for a selection
  // it was given, as it does as it opens, is still sent: only a press of the person's own holds the next one back.
  async toggle(part: SelectionPart, name: string): Promise<void> {
    if (this.isPressing) return
    this.isPressing = true
    this.page.store.change(() => ({ filtering: name }))
    try {
      const answer = await this.page.session.toggleGuidance(part, name)
      if (answer) await this.accept(answer)
    } catch (failure) {
      this.page.notices.fail(`The ${name} ${part} was not changed: ${reasonOf(failure)}`, 'A press in the Files app')
    } finally {
      this.isPressing = false
      this.page.store.change(() => ({ filtering: '' }))
    }
  }

  private async keepFollowing(): Promise<void> {
    while (this.isFollowing) {
      try {
        const answer = this.drawnVersion < 0 ? await this.page.session.guidanceSelection() : await this.page.session.guidanceSelectionAfter(this.drawnVersion)
        if (answer) await this.accept(answer)
      } catch (failure) {
        this.page.notices.fail(`The Files app did not read the session's guidance selection: ${reasonOf(failure)}`, 'Following the stages, practices and formats selected')
        await wait(RETRY_MILLISECONDS)
      }
    }
  }

  // An answer older than the version drawn is one a press has already moved past.
  private async accept(answer: GuidanceSelectionData): Promise<void> {
    if (answer.version < this.drawnVersion) return
    this.drawnVersion = answer.version
    this.draw(answer)
    await this.page.showSelected()
  }

  private draw(selection: GuidanceSelectionData): void {
    this.page.store.change(() => ({ guidance: selection }))
  }
}

