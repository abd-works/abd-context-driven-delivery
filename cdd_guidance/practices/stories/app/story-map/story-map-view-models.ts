import type { EpicData } from '@cdd/practices/stories/model/epic'
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
// The Python story model sends no examples or increments to the editor yet, so the views draw none.
export type ExampleFieldDto = { name: string; sequential_order: number }
export type ExampleRowDto = { id: string; example_id: string; values: Record<string, string>; sequential_order: number }
export type ExampleDto = { id: string; parent_id: string; name: string; sequential_order: number; fields: ExampleFieldDto[]; rows: ExampleRowDto[] }

// A node as Python sends it: the address its tools take, and its name.
type SentNode = { node: string; name: string }
// Where a node stands: the node it sits under, and its place among its siblings, from 1.
export type NodePlace = { parent: string | null; order: number }

export class StoryNodeViewModel {
  readonly id: string
  readonly parent_id: string | null
  readonly name: string
  readonly sequential_order: number

  constructor(sent: SentNode, readonly semantic_type: SemanticType, place: NodePlace) {
    this.id = sent.node
    this.name = sent.name
    this.parent_id = place.parent
    this.sequential_order = place.order
  }
}

export class IncrementViewModel extends StoryNodeViewModel {
  readonly stories: string[] = []
}

const KEYWORDS: readonly StepKeyword[] = ['given', 'when', 'then', 'and', 'but']
const placesUnder = (parent: string) => (index: number): NodePlace => ({ parent, order: index + 1 })

function stepRowsOf(steps: StepData[], scenario: string): StepRowDto[] {
  return steps.flatMap(step => [step, ...step.ands]).map((step, index) => {
    const keyword = step.keyword.toLowerCase() as StepKeyword
    return { id: step.node, parent_id: scenario, step_type: KEYWORDS.includes(keyword) ? keyword : 'given', text: step.text, sequential_order: index + 1 }
  })
}

export class ScenarioViewModel extends StoryNodeViewModel {
  readonly examples: ExampleDto[] = []

  constructor(scenario: SentNode, place: NodePlace, readonly steps: StepRowDto[]) {
    super(scenario, 'scenario', place)
  }

  static of(scenario: ScenarioData, place: NodePlace): ScenarioViewModel {
    return new ScenarioViewModel(scenario, place, stepRowsOf(scenario.steps, scenario.node))
  }
}

export class StoryViewModel extends StoryNodeViewModel {
  readonly users: string[] = []

  constructor(story: SentNode, place: NodePlace, readonly story_type: string, readonly scenarios: ScenarioViewModel[]) {
    super(story, 'story', place)
  }

  static of(story: StoryData, place: NodePlace): StoryViewModel {
    const under = placesUnder(story.node)
    return new StoryViewModel(story, place, story.story_type, story.scenarios.map((scenario, index) => ScenarioViewModel.of(scenario, under(index))))
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
}

export class StoryMapViewModel extends StoryNodeViewModel {
  readonly increments: IncrementViewModel[] = []
  readonly kinds: ReadonlyMap<string, SemanticType>

  constructor(storyMap: StoryModelData, readonly epics: EpicViewModel[]) {
    super({ node: storyMap.node, name: storyMap.file }, 'story-map', { parent: null, order: 0 })
    this.kinds = new Map(this.nodes().map(node => [node.id, node.semantic_type]))
  }

  static of(storyMap: StoryModelData): StoryMapViewModel {
    const under = placesUnder(storyMap.node)
    return new StoryMapViewModel(storyMap, storyMap.epics.map((epic, index) => EpicViewModel.of(epic, under(index))))
  }

  // Every node the map draws, so an edit knows which kind of node an id names.
  private nodes(): StoryNodeViewModel[] {
    const stories = this.epics.flatMap(epic => epic.sub_epics.flatMap(sub => sub.stories))
    const scenarios = stories.flatMap(story => story.scenarios)
    return [...this.epics, ...this.epics.flatMap(epic => epic.sub_epics), ...stories, ...scenarios]
  }
}
