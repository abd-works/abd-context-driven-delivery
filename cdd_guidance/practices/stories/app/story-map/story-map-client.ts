import type { CddApi } from '@cdd/cdd-shared'
import { ChatClientGenerated } from '@cdd/harness/chat/chat'
import { EpicClientGenerated } from '@cdd/practices/stories/model/epic'
import { ExampleClientGenerated } from '@cdd/practices/stories/model/example'
import { IncrementClientGenerated } from '@cdd/practices/stories/model/increment'
import { ScenarioClientGenerated } from '@cdd/practices/stories/model/scenario'
import { StepClientGenerated } from '@cdd/practices/stories/model/step'
import { StoryClientGenerated } from '@cdd/practices/stories/model/story'
import { StoryModelClientGenerated, type StoryModelData } from '@cdd/practices/stories/model/story-model'
import { FidelitySessionOutputClientGenerated } from '@cdd/space/session/fidelity-session-output'

import type { SemanticType, StepKeyword } from './story-map-view-models'

// The kind of node an edit names, which picks the generated client of that node's own tools.
export type NodeKind = Exclude<SemanticType, 'story-map'> | 'step'

type NodeClient = EpicClientGenerated | StoryClientGenerated | ScenarioClientGenerated | StepClientGenerated | IncrementClientGenerated
type Edit = Promise<StoryModelData | null>

// The story map the Story UI shows: the one the Python story model holds in its file, which every edit changes through
// that node's own tool and answers again. What only the page knows is here: which kind of node an address the views
// hand back names, and how a drag the views report as a new order becomes one move before a sibling.
export class StoryMapClient extends StoryModelClientGenerated {
  // The story map of the session open in the project: the page with no file to open follows it, so a ticket activated
  // on the board shows its own map on the next read.
  static async inOpenSession(api: CddApi): Promise<StoryMapClient | null> {
    const state = await StoryModelClientGenerated.openInSession(api)
    return state ? new StoryMapClient(api, state) : null
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

  private nodeOf(node: string, kind: NodeKind): NodeClient {
    if (kind === 'story') return StoryClientGenerated.named(this.api, node)
    if (kind === 'scenario') return ScenarioClientGenerated.named(this.api, node)
    if (kind === 'step') return StepClientGenerated.named(this.api, node)
    if (kind === 'increment') return IncrementClientGenerated.named(this.api, node)
    return EpicClientGenerated.named(this.api, node)
  }

  renameNode(node: string, kind: NodeKind, name: string): Promise<this | null> {
    return this.took(this.nodeOf(node, kind).rename(name))
  }

  // What the story map says about a node, under its heading in the map's file.
  describeNode(node: string, kind: NodeKind, description: string): Promise<this | null> {
    return this.took(this.nodeOf(node, kind).editDescription(description))
  }

  removeNode(node: string, kind: NodeKind): Promise<this | null> {
    return this.took(this.nodeOf(node, kind).remove())
  }

  // A drag reports the order the siblings take: the node dropped goes before the one now after it. Dropped last, every
  // sibling it passed goes before it in turn, since a node moves only before another.
  async reorder(before: string[], after: string[], kind: NodeKind): Promise<this | null> {
    const without = (nodes: string[], node: string) => nodes.filter(each => each !== node).join('\n')
    const moved = after.find((node, index) => node !== before[index] && without(before, node) === without(after, node))
    if (!moved) return this
    const next = after[after.indexOf(moved) + 1]
    if (next) return this.moveBeforeNode(moved, kind, next)
    let answered: this | null = this
    for (const passed of before.slice(before.indexOf(moved) + 1)) answered = await this.moveBeforeNode(passed, kind, moved)
    return answered
  }

  // Moving a node under another parent drops it before the node that follows it there.
  moveBeforeNode(node: string, kind: NodeKind, before: string): Promise<this | null> {
    return this.took(this.nodeOf(node, kind).moveBefore(before))
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

  // A cell of an example's row, changed through that example's own tool; the column that names it renames it.
  editExample(example: string, field: string, value: string): Promise<this | null> {
    return this.took(ExampleClientGenerated.named(this.api, example).editField(field, value))
  }

  removeExample(example: string): Promise<this | null> {
    return this.took(ExampleClientGenerated.named(this.api, example).remove())
  }

  // A story's acceptance-test file is read in the chat bar's file viewer of the chat this page was opened beside, never
  // here: the chat takes it at its next check-in. True once the chat has it waiting.
  async showInChat(chat: string, file: string): Promise<boolean> {
    return (await ChatClientGenerated.named(this.api, chat).send('open_file', file)) !== null
  }

  // A story given to an increment leaves the increment that delivered it, as the story model keeps it in one at most.
  deliverIn(increment: string, story: string): Promise<this | null> {
    return this.took(IncrementClientGenerated.named(this.api, increment).addStory(story))
  }

  stopDelivering(increment: string, story: string): Promise<this | null> {
    return this.took(IncrementClientGenerated.named(this.api, increment).removeStory(story))
  }

  // A format turned on or off here is the session's choice for the fidelity, the one the chat bar's chips show, and the
  // next edit renders to it.
  async chooseFormat(format: string, isChosen: boolean): Promise<this | null> {
    const formats = new FidelitySessionOutputClientGenerated(this.api, this.formats)
    return (await formats.chooseFormat(format, isChosen)) ? this.show() : null
  }
}
