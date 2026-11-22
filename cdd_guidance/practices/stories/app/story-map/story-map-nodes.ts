// The story map's nodes as the Story UI holds them: each made from the node Python sent, knowing what kind of node it
// is and edited through that node's own tools, so an epic adds a story under it and a step changes its words, and an
// edit a node does not take, such as a new story under a step, cannot be written. Every edit answers the whole map,
// which the map the node belongs to takes on (StoryMapClient), and the map makes its nodes again from that answer: a
// node is never kept from one answer to the next, so a view keys it by its id, the address its tools take.
import { EpicClientGenerated, type EpicData } from '@cdd/practices/stories/model/epic'
import { ExampleClientGenerated, type ExampleData } from '@cdd/practices/stories/model/example'
import { IncrementClientGenerated, type IncrementData } from '@cdd/practices/stories/model/increment'
import { ScenarioClientGenerated, type ScenarioData } from '@cdd/practices/stories/model/scenario'
import { StepClientGenerated, type StepData } from '@cdd/practices/stories/model/step'
import { StoryClientGenerated, type StoryData } from '@cdd/practices/stories/model/story'
import type { StoryModelData } from '@cdd/practices/stories/model/story-model'

import type { StoryMapClient } from './story-map-client'

type Edit = Promise<StoryModelData | null>
export type Answer = Promise<StoryMapClient | null>

export type StepKeyword = 'given' | 'when' | 'then' | 'and' | 'but'
export const STEP_KEYWORDS: readonly StepKeyword[] = ['given', 'when', 'then', 'and', 'but']

// A node as Python sends it: the address its tools take, its name, and what the story map says about it.
type SentNode = { node: string; name: string; description: string }

// The tools every node of the map takes, each on the node's own generated client.
interface NodeTools {
  rename(name: string): Edit
  editDescription(description: string): Edit
  remove(): Edit
  moveBefore(other: string): Edit
}

// A node is added last under its parent; one asked for before another is then moved before it. created reads the
// address of the node added from the map the addition answered, and moved is that node's own tools.
export async function addedBefore(map: StoryMapClient, addition: Edit, created: (answered: StoryModelData) => string | undefined, before: StoryNodeOnPage | undefined, moved: (address: string) => NodeTools): Answer {
  const answered = await map.answerTo(addition)
  const address = answered && before ? created(answered.toJSON()) : undefined
  return before && address && address !== before.id ? map.answerTo(moved(address).moveBefore(before.id)) : answered
}

// The epic an answered map holds at address, at any depth; none once it is gone.
function epicIn(epics: EpicData[], address: string): EpicData | undefined {
  for (const epic of epics) {
    if (epic.node === address) return epic
    const nested = epicIn(epic.epics, address)
    if (nested) return nested
  }
  return undefined
}

export abstract class StoryNodeOnPage {
  constructor(
    protected readonly map: StoryMapClient,
    protected readonly sentNode: SentNode,
  ) {}

  // The address the node's tools take, which a view also keys the node by.
  get id(): string {
    return this.sentNode.node
  }

  get name(): string {
    return this.sentNode.name
  }

  // What the story map says about the node, under its heading in the map's file.
  get description(): string {
    return this.sentNode.description
  }

  rename(name: string): Answer {
    return this.map.answerTo(this.tools.rename(name))
  }

  describe(description: string): Answer {
    return this.map.answerTo(this.tools.editDescription(description))
  }

  remove(): Answer {
    return this.map.answerTo(this.tools.remove())
  }

  // Moving a node under another parent drops it before the node that follows it there.
  moveBefore(other: StoryNodeOnPage): Answer {
    return this.map.answerTo(this.tools.moveBefore(other.id))
  }

  protected abstract get tools(): NodeTools
}

// An epic. A top epic's sub-epics are the rows under it: a row of its own stories first, named for the epic and edited
// through it, then each epic nested under it, whose row shows the stories of every epic nested under that one too.
export class EpicOnPage extends StoryNodeOnPage {
  constructor(
    map: StoryMapClient,
    epic: SentNode,
    readonly subEpics: EpicOnPage[],
    readonly stories: StoryOnPage[],
  ) {
    super(map, epic)
  }

  static of(map: StoryMapClient, epic: EpicData): EpicOnPage {
    const own = epic.stories.length ? [new EpicOnPage(map, epic, [], epic.stories.map(story => StoryOnPage.of(map, story)))] : []
    const nested = epic.epics.map(subEpic => new EpicOnPage(map, subEpic, [], storiesUnder(subEpic).map(story => StoryOnPage.of(map, story))))
    return new EpicOnPage(map, epic, [...own, ...nested], epic.stories.map(story => StoryOnPage.of(map, story)))
  }

  // This epic with only the stories scope names, and only the rows that keep one; none when it keeps none. Each row it
  // keeps is still edited through its own epic.
  within(scope: ReadonlySet<string>): EpicOnPage | null {
    const rows = this.subEpics
      .map(row => new EpicOnPage(this.map, row.sentNode, [], row.stories.filter(story => scope.has(story.id))))
      .filter(row => row.stories.length)
    return rows.length ? new EpicOnPage(this.map, this.sentNode, rows, this.stories) : null
  }

  // A new sub-epic, placed before the sub-epic before names, else last.
  newSubEpic(name: string, before?: EpicOnPage): Answer {
    return addedBefore(this.map, this.tools.newEpic(name), answered => epicIn(answered.epics, this.id)?.epics.at(-1)?.node, before, address => EpicClientGenerated.named(this.map.api, address))
  }

  // A new story of this epic's own, placed before the story before names, else last.
  newStory(name: string, before?: StoryOnPage): Answer {
    return addedBefore(this.map, this.tools.newStory(name), answered => epicIn(answered.epics, this.id)?.stories.at(-1)?.node, before, address => StoryClientGenerated.named(this.map.api, address))
  }

  // Every story the epic's rows show, which opening the epic opens.
  get storiesShown(): StoryOnPage[] {
    return this.subEpics.flatMap(row => row.stories)
  }

  protected get tools(): EpicClientGenerated {
    return EpicClientGenerated.named(this.map.api, this.id)
  }
}

// A row shows the stories of every epic nested under its own.
function storiesUnder(epic: EpicData): StoryData[] {
  return [...epic.stories, ...epic.epics.flatMap(storiesUnder)]
}

export class StoryOnPage extends StoryNodeOnPage {
  constructor(
    map: StoryMapClient,
    private readonly story: StoryData,
    readonly scenarios: ScenarioOnPage[],
  ) {
    super(map, story)
  }

  static of(map: StoryMapClient, story: StoryData): StoryOnPage {
    return new StoryOnPage(map, story, story.scenarios.map(scenario => ScenarioOnPage.of(map, scenario)))
  }

  get storyType(): string {
    return this.story.story_type
  }

  // The story's acceptance-test files, which open in the chat bar's file viewer.
  get acceptanceTests(): string[] {
    return this.story.acceptance_tests
  }

  // The increment that delivers the story, if one does: a story is delivered by one increment at most.
  get increment(): IncrementOnPage | undefined {
    return this.map.incrementsOnPage.find(increment => increment.delivers(this))
  }

  newScenario(name: string): Answer {
    return this.map.answerTo(this.tools.newScenario(name))
  }

  // The story's scenarios in the order a drag left them.
  reorderScenarios(order: string[]): Answer {
    return this.map.reorder(this.scenarios, order)
  }

  protected get tools(): StoryClientGenerated {
    return StoryClientGenerated.named(this.map.api, this.id)
  }
}

export class ScenarioOnPage extends StoryNodeOnPage {
  constructor(
    map: StoryMapClient,
    scenario: SentNode,
    readonly steps: StepOnPage[],
    readonly examples: ExampleOnPage[],
  ) {
    super(map, scenario)
  }

  // A scenario's steps in order, each And or But step after the step it follows.
  static of(map: StoryMapClient, scenario: ScenarioData): ScenarioOnPage {
    const steps = scenario.steps.flatMap(step => [step, ...step.ands]).map(step => new StepOnPage(map, step))
    return new ScenarioOnPage(map, scenario, steps, scenario.examples.map(example => new ExampleOnPage(map, example)))
  }

  // The columns of the scenario's one table of examples: every field any example has, in the order they first appear.
  get exampleColumns(): string[] {
    return [...new Set(this.examples.flatMap(example => Object.keys(example.fields)))]
  }

  // A new step; an And or But step is written as a Then.
  newStep(keyword: StepKeyword, text: string): Answer {
    const stepType = keyword === 'and' || keyword === 'but' ? 'then' : keyword
    return this.map.answerTo(this.tools.newStep(stepType, text))
  }

  // The scenario's steps in the order a drag left them.
  reorderSteps(order: string[]): Answer {
    return this.map.reorder(this.steps, order)
  }

  protected get tools(): ScenarioClientGenerated {
    return ScenarioClientGenerated.named(this.map.api, this.id)
  }
}

export class StepOnPage extends StoryNodeOnPage {
  constructor(
    map: StoryMapClient,
    private readonly step: StepData,
  ) {
    super(map, step)
  }

  // The step's keyword; one the page does not know reads as Given.
  get keyword(): StepKeyword {
    const keyword = this.step.keyword.toLowerCase() as StepKeyword
    return STEP_KEYWORDS.includes(keyword) ? keyword : 'given'
  }

  get text(): string {
    return this.step.text
  }

  editText(text: string): Answer {
    return this.map.answerTo(this.tools.editText(text))
  }

  protected get tools(): StepClientGenerated {
    return StepClientGenerated.named(this.map.api, this.id)
  }
}

// One example of a scenario, a row of its table, edited cell by cell through its own tools.
export class ExampleOnPage {
  constructor(
    private readonly map: StoryMapClient,
    private readonly example: ExampleData,
  ) {}

  get id(): string {
    return this.example.node
  }

  // The example's fields by column, its name under `example`.
  get fields(): Record<string, string> {
    return this.example.fields
  }

  // A cell of the example's row; the column that names it renames it.
  editField(field: string, cellText: string): Answer {
    return this.map.answerTo(this.tools.editField(field, cellText))
  }

  remove(): Answer {
    return this.map.answerTo(this.tools.remove())
  }

  private get tools(): ExampleClientGenerated {
    return ExampleClientGenerated.named(this.map.api, this.id)
  }
}

// An increment and the stories it delivers.
export class IncrementOnPage extends StoryNodeOnPage {
  constructor(
    map: StoryMapClient,
    private readonly increment: IncrementData,
  ) {
    super(map, increment)
  }

  delivers(story: StoryOnPage): boolean {
    return this.increment.stories.includes(story.id)
  }

  // A story given to an increment leaves the increment that delivered it, as the story model keeps it in one at most.
  deliver(story: StoryOnPage): Answer {
    return this.map.answerTo(this.tools.addStory(story.id))
  }

  stopDelivering(story: StoryOnPage): Answer {
    return this.map.answerTo(this.tools.removeStory(story.id))
  }

  protected get tools(): IncrementClientGenerated {
    return IncrementClientGenerated.named(this.map.api, this.id)
  }
}
