import type { GuidanceSelectionData } from '@cdd/space/session/session'

import type { FilesPage } from './files-page'

// How long the page waits before reading the selection again after a read failed, so a cdd server restarting for a
// repin is not asked many times a second.
const RETRY_MILLISECONDS = 1_000

const reasonOf = (failure: unknown): string => (failure instanceof Error ? failure.message : String(failure))
const wait = (milliseconds: number) => new Promise(resolve => setTimeout(resolve, milliseconds))

// The session's guidance selection as the page shows and changes it: the stages, practices, and formats selected, the
// one selection the chat bar's buttons show too. The session holds it; the page follows it with one waiting read
// (Session.guidance_selection_after), so a change made anywhere draws here in a fraction of a second. A press draws at
// once, then sends one update; any answer older than the version drawn is ignored, so a late read never undoes a press.
// The page it belongs to holds the session, the store it draws into, and the notices a failure is told through, and
// reads the files of fidelities it shows for the first time once a selection is drawn.
export class GuidanceSelector {
  private drawnVersion = -1
  private isFollowing = false

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

  async toggleStage(name: string): Promise<void> {
    const selection = this.selection
    if (!selection) return
    const stages = toggled(selection.stages.filter(stage => stage.is_selected).map(stage => stage.name), name)
    this.draw({ ...selection, is_stage_chosen: true, stages: selection.stages.map(stage => (stage.name === name ? { ...stage, is_selected: !stage.is_selected } : stage)) })
    await this.update(`The ${name} stage was not ${stages.includes(name) ? 'selected' : 'cleared'}`, { stages })
  }

  async togglePractice(key: string): Promise<void> {
    const selection = this.selection
    if (!selection) return
    const practices = toggled(selection.practices.filter(practice => practice.is_selected).map(practice => practice.key), key)
    this.draw({ ...selection, practices: selection.practices.map(practice => (practice.key === key ? { ...practice, is_selected: !practice.is_selected } : practice)) })
    await this.update(`The ${key} practice was not turned ${practices.includes(key) ? 'on' : 'off'}`, { practices })
  }

  async toggleFormat(label: string): Promise<void> {
    const selection = this.selection
    if (!selection) return
    const formats = toggled(selection.formats.filter(format => format.is_selected).map(format => format.label), label)
    this.draw({ ...selection, formats: selection.formats.map(format => (format.label === label ? { ...format, is_selected: !format.is_selected } : format)) })
    await this.update(`The ${label} format was not ${formats.includes(label) ? 'chosen' : 'cleared'}`, { formats })
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

  private async update(what: string, change: { stages?: string[]; practices?: string[]; formats?: string[] }): Promise<void> {
    try {
      const answer = await this.page.session.updateGuidanceSelection(change.stages ?? null, change.practices ?? null, change.formats ?? null)
      if (answer) await this.accept(answer)
    } catch (failure) {
      this.page.notices.fail(`${what}: ${reasonOf(failure)}`, 'A press in the Files app')
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

// The names with name taken out while it is in them, else put in.
const toggled = (names: string[], name: string): string[] => (names.includes(name) ? names.filter(each => each !== name) : [...names, name])
