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

export class StoryNodeViewModel {
  constructor(
    public readonly id: string,
    public readonly parent_id: string | null,
    public readonly name: string,
    public readonly semantic_type: SemanticType,
    public readonly sequential_order: number,
  ) {}
}

export class IncrementViewModel extends StoryNodeViewModel {
  readonly stories: string[] = []
}

const KEYWORDS: readonly StepKeyword[] = ['given', 'when', 'then', 'and', 'but']

function stepRowsOf(steps: StepData[], parent: string): StepRowDto[] {
  return steps.flatMap(step => [step, ...step.ands]).map((step, index) => {
    const keyword = step.keyword.toLowerCase() as StepKeyword
    return { id: step.node, parent_id: parent, step_type: KEYWORDS.includes(keyword) ? keyword : 'given', text: step.text, sequential_order: index + 1 }
  })
}

export class ScenarioViewModel extends StoryNodeViewModel {
  readonly steps: StepRowDto[]
  readonly examples: ExampleDto[] = []

  constructor(data: ScenarioData, parent: string, order: number) {
    super(data.node, parent, data.name, 'scenario', order)
    this.steps = stepRowsOf(data.steps, data.node)
  }
}

export class StoryViewModel extends StoryNodeViewModel {
  readonly story_type: string
  readonly users: string[] = []
  readonly scenarios: ScenarioViewModel[]

  constructor(data: StoryData, parent: string, order: number) {
    super(data.node, parent, data.name, 'story', order)
    this.story_type = data.story_type
    this.scenarios = data.scenarios.map((scenario, index) => new ScenarioViewModel(scenario, data.node, index + 1))
  }
}

// A sub-epic shows the stories of every epic nested under it, each still edited through its own node.
function storiesUnder(epic: EpicData): StoryData[] {
  return [...epic.stories, ...epic.epics.flatMap(storiesUnder)]
}

export class SubEpicViewModel extends StoryNodeViewModel {
  readonly stories: StoryViewModel[]

  constructor(data: EpicData, parent: string, order: number, stories: StoryData[] = storiesUnder(data)) {
    super(data.node, parent, data.name, 'sub-epic', order)
    this.stories = stories.map((story, index) => new StoryViewModel(story, data.node, index + 1))
  }
}

export class EpicViewModel extends StoryNodeViewModel {
  readonly sub_epics: SubEpicViewModel[]

  // An epic's own stories, above its sub-epics, show as a row named for the epic, edited through the epic itself.
  constructor(data: EpicData, parent: string, order: number) {
    super(data.node, parent, data.name, 'epic', order)
    const own = data.stories.length ? [new SubEpicViewModel(data, data.node, 0, data.stories)] : []
    this.sub_epics = [...own, ...data.epics.map((epic, index) => new SubEpicViewModel(epic, data.node, index + 1))]
  }
}

export class StoryMapViewModel extends StoryNodeViewModel {
  readonly epics: EpicViewModel[]
  readonly increments: IncrementViewModel[] = []
  readonly kinds: ReadonlyMap<string, SemanticType>

  constructor(data: StoryModelData) {
    super(data.node, null, data.file, 'story-map', 0)
    this.epics = data.epics.map((epic, index) => new EpicViewModel(epic, data.node, index + 1))
    this.kinds = new Map(this.nodes().map(node => [node.id, node.semantic_type]))
  }

  // Every node the map draws, so an edit knows which kind of node an id names.
  private nodes(): StoryNodeViewModel[] {
    const stories = this.epics.flatMap(epic => epic.sub_epics.flatMap(sub => sub.stories))
    const scenarios = stories.flatMap(story => story.scenarios)
    return [...this.epics, ...this.epics.flatMap(epic => epic.sub_epics), ...stories, ...scenarios]
  }
}
