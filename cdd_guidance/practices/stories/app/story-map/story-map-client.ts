import type { CddApi } from '@cdd/cdd-shared'
import { EpicClientGenerated } from '@cdd/practices/stories/model/epic'
import { ScenarioClientGenerated } from '@cdd/practices/stories/model/scenario'
import { StepClientGenerated } from '@cdd/practices/stories/model/step'
import { StoryClientGenerated } from '@cdd/practices/stories/model/story'
import { StoryModelClientGenerated, type StoryModelData } from '@cdd/practices/stories/model/story-model'
import { FidelitySessionOutputClientGenerated } from '@cdd/space/session/fidelity-session-output'

import type { SemanticType, StepKeyword } from './story-map-view-models'

type NodeClient = EpicClientGenerated | StoryClientGenerated | ScenarioClientGenerated | StepClientGenerated
type Edit = Promise<StoryModelData | null>

// The story map the Story UI shows: the one the Python story model holds in its file, which every edit changes through
// that node's own tool and answers again. What only the page knows is here: which kind of node an id the views hand
// back names, and how a drag the views report as a new order becomes one move before a sibling.
export class StoryMapClient extends StoryModelClientGenerated {
  // The story map of the session open in the project: the page with no file to open follows it, so a ticket activated
  // on the board shows its own map on the next read.
  static async inOpenSession(api: CddApi): Promise<StoryMapClient | null> {
    const state = await StoryModelClientGenerated.openInSession(api)
    return state ? new StoryMapClient(api, state) : null
  }

  async read(): Promise<this | null> {
    return this.show()
  }

  // The map another client of the same file read, taken on here, so the views holding this client draw it.
  takeOn(read: StoryModelClientGenerated): this {
    return this.changed(read.toJSON())
  }

  // The answer an edit gives is the whole map as its file now holds it; a failed edit keeps the map as it was.
  private async took(edit: Edit): Promise<this | null> {
    const state = await edit
    return state ? this.changed(state) : null
  }

  private nodeOf(id: string, kind: SemanticType): NodeClient {
    if (kind === 'story') return StoryClientGenerated.named(this.api, id)
    if (kind === 'scenario') return ScenarioClientGenerated.named(this.api, id)
    return EpicClientGenerated.named(this.api, id)
  }

  renameNode(id: string, kind: SemanticType, name: string): Promise<this | null> {
    return this.took(this.nodeOf(id, kind).rename(name))
  }

  removeNode(id: string, kind: SemanticType): Promise<this | null> {
    return this.took(this.nodeOf(id, kind).remove())
  }

  // A drag reports the order the siblings take: the node dropped goes before the one now after it. Dropped last, every
  // sibling it passed goes before it in turn, since a node moves only before another.
  async reorder(before: string[], after: string[], kind: SemanticType): Promise<this | null> {
    const without = (ids: string[], id: string) => ids.filter(each => each !== id).join('\n')
    const moved = after.find((id, index) => id !== before[index] && without(before, id) === without(after, id))
    if (!moved) return this
    const next = after[after.indexOf(moved) + 1]
    if (next) return this.took(this.nodeOf(moved, kind).moveBefore(next))
    let answered: this | null = this
    for (const passed of before.slice(before.indexOf(moved) + 1)) answered = await this.took(this.nodeOf(passed, kind).moveBefore(moved))
    return answered
  }

  // Moving a node under another parent drops it before the node that follows it there.
  moveBeforeNode(id: string, kind: SemanticType, before: string): Promise<this | null> {
    return this.took(this.nodeOf(id, kind).moveBefore(before))
  }

  newTopEpic(name: string): Promise<this | null> {
    return this.newEpic(name)
  }

  newSubEpic(epic: string, name: string): Promise<this | null> {
    return this.took(EpicClientGenerated.named(this.api, epic).newEpic(name))
  }

  newStory(epic: string, name: string): Promise<this | null> {
    return this.took(EpicClientGenerated.named(this.api, epic).newStory(name))
  }

  newScenario(story: string, name: string): Promise<this | null> {
    return this.took(StoryClientGenerated.named(this.api, story).newScenario(name))
  }

  newStep(scenario: string, keyword: StepKeyword, text: string): Promise<this | null> {
    const stepType = keyword === 'and' || keyword === 'but' ? 'then' : keyword
    return this.took(ScenarioClientGenerated.named(this.api, scenario).newStep(stepType, text))
  }

  editStep(step: string, text: string): Promise<this | null> {
    return this.took(StepClientGenerated.named(this.api, step).editText(text))
  }

  removeStep(step: string): Promise<this | null> {
    return this.took(StepClientGenerated.named(this.api, step).remove())
  }

  // A format turned on or off here is the session's choice for the fidelity, the one the chat bar's chips show, and the
  // next edit renders to it.
  async chooseFormat(format: string, isChosen: boolean): Promise<this | null> {
    const formats = new FidelitySessionOutputClientGenerated(this.api, this.formats)
    return (await formats.chooseFormat(format, isChosen)) ? this.read() : null
  }
}
