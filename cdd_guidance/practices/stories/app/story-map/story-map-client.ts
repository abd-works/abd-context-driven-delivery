import type { CddApi } from '@cdd/cdd-shared'
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
type Answer = Promise<StoryMapClient | null>

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
  async answerTo(edit: Edit): Answer {
    const state = await edit
    return state ? this.changed(state) : null
  }

  // The node an address names, edited through its own tools.
  nodeAt(address: string, kind: NodeKind): StoryMapNode {
    return new StoryMapNode(this, address, kind)
  }

  exampleAt(address: string): StoryMapExample {
    return new StoryMapExample(this, address)
  }

  incrementAt(address: string): StoryMapIncrement {
    return new StoryMapIncrement(this, address)
  }

  // A drag reports the order the siblings take: the node dropped goes before the one now after it. Dropped last, every
  // sibling it passed goes before it in turn, since a node moves only before another.
  async reorder(before: string[], after: string[], kind: NodeKind): Answer {
    const without = (nodes: string[], node: string) => nodes.filter(each => each !== node).join('\n')
    const moved = after.find((node, index) => node !== before[index] && without(before, node) === without(after, node))
    if (!moved) return this
    const next = after[after.indexOf(moved) + 1]
    if (next) return this.nodeAt(moved, kind).moveBefore(next)
    let answered: StoryMapClient | null = this
    for (const passed of before.slice(before.indexOf(moved) + 1)) answered = await this.nodeAt(passed, kind).moveBefore(moved)
    return answered
  }

  // A format turned on or off here is the session's choice for the fidelity, the one the chat bar's chips show, and the
  // next edit renders to it.
  async chooseFormat(format: string, isChosen: boolean): Promise<this | null> {
    const formats = new FidelitySessionOutputClientGenerated(this.api, this.formats)
    return (await formats.chooseFormat(format, isChosen)) ? this.show() : null
  }
}

// An epic, sub-epic, story, scenario, step or increment of the map, by the address its tools take. Every edit answers
// the whole map, which the map it belongs to takes on.
export class StoryMapNode {
  constructor(
    private readonly map: StoryMapClient,
    readonly address: string,
    readonly kind: NodeKind,
  ) {}

  rename(name: string): Answer {
    return this.map.answerTo(this.client().rename(name))
  }

  // What the story map says about the node, under its heading in the map's file.
  describe(description: string): Answer {
    return this.map.answerTo(this.client().editDescription(description))
  }

  remove(): Answer {
    return this.map.answerTo(this.client().remove())
  }

  // Moving a node under another parent drops it before the node that follows it there.
  moveBefore(other: string): Answer {
    return this.map.answerTo(this.client().moveBefore(other))
  }

  newSubEpic(name: string): Answer {
    return this.map.answerTo(EpicClientGenerated.named(this.map.api, this.address).newEpic(name))
  }

  newStory(name: string): Answer {
    return this.map.answerTo(EpicClientGenerated.named(this.map.api, this.address).newStory(name))
  }

  newScenario(name: string): Answer {
    return this.map.answerTo(StoryClientGenerated.named(this.map.api, this.address).newScenario(name))
  }

  newStep(keyword: StepKeyword, text: string): Answer {
    const stepType = keyword === 'and' || keyword === 'but' ? 'then' : keyword
    return this.map.answerTo(ScenarioClientGenerated.named(this.map.api, this.address).newStep(stepType, text))
  }

  editText(text: string): Answer {
    return this.map.answerTo(StepClientGenerated.named(this.map.api, this.address).editText(text))
  }

  private client(): NodeClient {
    const api = this.map.api
    if (this.kind === 'story') return StoryClientGenerated.named(api, this.address)
    if (this.kind === 'scenario') return ScenarioClientGenerated.named(api, this.address)
    if (this.kind === 'step') return StepClientGenerated.named(api, this.address)
    if (this.kind === 'increment') return IncrementClientGenerated.named(api, this.address)
    return EpicClientGenerated.named(api, this.address)
  }
}

// One example of a scenario, a row of its table, edited cell by cell through its own tools.
export class StoryMapExample {
  constructor(
    private readonly map: StoryMapClient,
    readonly address: string,
  ) {}

  // A cell of the example's row; the column that names it renames it.
  editField(field: string, cellText: string): Answer {
    return this.map.answerTo(ExampleClientGenerated.named(this.map.api, this.address).editField(field, cellText))
  }

  remove(): Answer {
    return this.map.answerTo(ExampleClientGenerated.named(this.map.api, this.address).remove())
  }
}

// An increment and the stories it delivers.
export class StoryMapIncrement {
  constructor(
    private readonly map: StoryMapClient,
    readonly address: string,
  ) {}

  // A story given to an increment leaves the increment that delivered it, as the story model keeps it in one at most.
  deliver(story: string): Answer {
    return this.map.answerTo(IncrementClientGenerated.named(this.map.api, this.address).addStory(story))
  }

  stopDelivering(story: string): Answer {
    return this.map.answerTo(IncrementClientGenerated.named(this.map.api, this.address).removeStory(story))
  }
}
