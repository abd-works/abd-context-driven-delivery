import type { EpicData } from '@cdd/practices/stories/model/epic'
import type { ExampleData } from '@cdd/practices/stories/model/example'
import type { IncrementData } from '@cdd/practices/stories/model/increment'
import type { ScenarioData } from '@cdd/practices/stories/model/scenario'
import type { StepData } from '@cdd/practices/stories/model/step'
import type { StoryData } from '@cdd/practices/stories/model/story'
import type { StoryModelData } from '@cdd/practices/stories/model/story-model'

// What the Story UI's views draw, read from the story map the Python story model sends: each node keeps the address
// its tools name it by (its `node`) as its id, so every edit a view makes goes to that node's tool. The views keep no
// story map of their own; a new answer from Python is drawn as a new set of view models.

export type SemanticType = 'story-map' | 'epic' | 'sub-epic' | 'story' | 'scenario' | 'increment'
export type StepKeyword = 'given' | 'when' | 'then' | 'and' | 'but'
export type StepRowDto = { id: string; parent_id: string; step_type: StepKeyword; text: string; sequential_order: number }
// A scenario's examples as the story model holds them: one table, a row per example, each named by the address its own
// tools take, with its name under `example`, then its fields. A cell is edited through its example's edit_field.
export type ExampleRow = { id: string; fields: Record<string, string> }
export type ExampleTable = { columns: string[]; rows: ExampleRow[] }

// A node as Python sends it: the address its tools take, its name, and what the story map says about it.
type SentNode = { node: string; name: string; description: string }
// Where a node stands: the node it sits under, and its place among its siblings, from 1.
export type NodePlace = { parent: string | null; order: number }

export class StoryNodeViewModel {
  readonly id: string
  readonly parent_id: string | null
  readonly name: string
  readonly description: string
  readonly sequential_order: number

  constructor(sent: SentNode, readonly semantic_type: SemanticType, place: NodePlace) {
    this.id = sent.node
    this.name = sent.name
    this.description = sent.description
    this.parent_id = place.parent
    this.sequential_order = place.order
  }
}

// An increment and the stories it delivers, by their addresses.
export class IncrementViewModel extends StoryNodeViewModel {
  constructor(increment: IncrementData, place: NodePlace, readonly stories: string[]) {
    super(increment, 'increment', place)
  }

  static of(increment: IncrementData, place: NodePlace): IncrementViewModel {
    return new IncrementViewModel(increment, place, increment.stories)
  }
}

// A view model as Python sent its node, and where it stands, so a part of the map is drawn from the same nodes.
const sent = (view: StoryNodeViewModel): SentNode => ({ node: view.id, name: view.name, description: view.description })
const placeOf = (view: StoryNodeViewModel): NodePlace => ({ parent: view.parent_id, order: view.sequential_order })

const KEYWORDS: readonly StepKeyword[] = ['given', 'when', 'then', 'and', 'but']
const placesUnder = (parent: string) => (index: number): NodePlace => ({ parent, order: index + 1 })

function stepRowsOf(steps: StepData[], scenario: string): StepRowDto[] {
  return steps.flatMap(step => [step, ...step.ands]).map((step, index) => {
    const keyword = step.keyword.toLowerCase() as StepKeyword
    return { id: step.node, parent_id: scenario, step_type: KEYWORDS.includes(keyword) ? keyword : 'given', text: step.text, sequential_order: index + 1 }
  })
}

function exampleTableOf(examples: ExampleData[]): ExampleTable {
  const rows = examples.map(example => ({ id: example.node, fields: example.fields }))
  return { columns: [...new Set(rows.flatMap(row => Object.keys(row.fields)))], rows }
}

export class ScenarioViewModel extends StoryNodeViewModel {
  constructor(scenario: SentNode, place: NodePlace, readonly steps: StepRowDto[], readonly examples: ExampleTable) {
    super(scenario, 'scenario', place)
  }

  static of(scenario: ScenarioData, place: NodePlace): ScenarioViewModel {
    return new ScenarioViewModel(scenario, place, stepRowsOf(scenario.steps, scenario.node), exampleTableOf(scenario.examples))
  }
}

export class StoryViewModel extends StoryNodeViewModel {
  constructor(story: SentNode, place: NodePlace, readonly story_type: string, readonly scenarios: ScenarioViewModel[], readonly acceptance_tests: string[]) {
    super(story, 'story', place)
  }

  static of(story: StoryData, place: NodePlace): StoryViewModel {
    const under = placesUnder(story.node)
    const scenarios = story.scenarios.map((scenario, index) => ScenarioViewModel.of(scenario, under(index)))
    return new StoryViewModel(story, place, story.story_type, scenarios, story.acceptance_tests)
  }
}

// A sub-epic shows the stories of every epic nested under it, each still edited through its own node.
function storiesUnder(epic: EpicData): StoryData[] {
  return [...epic.stories, ...epic.epics.flatMap(storiesUnder)]
}

export class SubEpicViewModel extends StoryNodeViewModel {
  constructor(subEpic: SentNode, place: NodePlace, readonly stories: StoryViewModel[]) {
    super(subEpic, 'sub-epic', place)
  }

  static of(subEpic: EpicData, place: NodePlace, stories: StoryData[] = storiesUnder(subEpic)): SubEpicViewModel {
    const under = placesUnder(subEpic.node)
    return new SubEpicViewModel(subEpic, place, stories.map((story, index) => StoryViewModel.of(story, under(index))))
  }
}

export class EpicViewModel extends StoryNodeViewModel {
  constructor(epic: SentNode, place: NodePlace, readonly sub_epics: SubEpicViewModel[]) {
    super(epic, 'epic', place)
  }

  // An epic's own stories, above its sub-epics, show as a row named for the epic, edited through the epic itself.
  static of(epic: EpicData, place: NodePlace): EpicViewModel {
    const under = placesUnder(epic.node)
    const own = epic.stories.length ? [SubEpicViewModel.of(epic, { parent: epic.node, order: 0 }, epic.stories)] : []
    return new EpicViewModel(epic, place, [...own, ...epic.epics.map((subEpic, index) => SubEpicViewModel.of(subEpic, under(index)))])
  }

  // This epic with only the stories scope names, and only the sub-epics that keep one; none when it keeps none.
  within(scope: ReadonlySet<string>): EpicViewModel | null {
    const subEpics = this.sub_epics
      .map(sub => new SubEpicViewModel(sent(sub), placeOf(sub), sub.stories.filter(story => scope.has(story.id))))
      .filter(sub => sub.stories.length)
    return subEpics.length ? new EpicViewModel(sent(this), placeOf(this), subEpics) : null
  }
}

export class StoryMapViewModel extends StoryNodeViewModel {
  readonly kinds: ReadonlyMap<string, SemanticType>

  constructor(storyMap: StoryModelData, readonly epics: EpicViewModel[], readonly increments: IncrementViewModel[]) {
    super({ node: storyMap.node, name: storyMap.file, description: storyMap.description }, 'story-map', { parent: null, order: 0 })
    this.kinds = new Map(this.nodes().map(node => [node.id, node.semantic_type]))
  }

  // The map as Python sent it; scoped, only the part the session's ticket covers (its `scope`), when the session names
  // any of its stories.
  static of(storyMap: StoryModelData, scoped: boolean = false): StoryMapViewModel {
    const under = placesUnder(storyMap.node)
    const scope = new Set(storyMap.scope)
    const epics = storyMap.epics.map((epic, index) => EpicViewModel.of(epic, under(index)))
    const shown = scoped && scope.size ? epics.flatMap(epic => epic.within(scope) ?? []) : epics
    return new StoryMapViewModel(storyMap, shown, storyMap.increments.map((increment, index) => IncrementViewModel.of(increment, under(index))))
  }

  // The increment that delivers story, if one does: a story is delivered by one increment at most.
  incrementOf(story: string): IncrementViewModel | undefined {
    return this.increments.find(increment => increment.stories.includes(story))
  }

  // Every node the map draws, so an edit knows which kind of node an id names.
  private nodes(): StoryNodeViewModel[] {
    const stories = this.epics.flatMap(epic => epic.sub_epics.flatMap(sub => sub.stories))
    const scenarios = stories.flatMap(story => story.scenarios)
    return [...this.epics, ...this.epics.flatMap(epic => epic.sub_epics), ...stories, ...scenarios, ...this.increments]
  }
}
