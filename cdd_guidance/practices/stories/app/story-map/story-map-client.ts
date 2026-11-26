import type { CddApi } from '@cdd/cdd-shared'
import { EpicClientGenerated } from '@cdd/practices/stories/model/epic'
import { StoryMapClientGenerated, type StoryMapData } from '@cdd/practices/stories/model/story-map'
import { FidelitySessionOutputClientGenerated } from '@cdd/space/session/practices/fidelity-session-output'

import { EpicOnPage, IncrementOnPage, addedBefore, type Answer, type StoryNodeOnPage } from './story-map-nodes'

type Edit = Promise<StoryMapData | null>

// The story map the Story UI shows: the one the Python story model holds in its file, which every edit changes through
// that node's own tool and answers again. The map holds its nodes, made once from each answer, each knowing its kind
// and its own edits (story-map-nodes.ts); what only the page knows is here: the part of the map a ticket's scope shows,
// and how a drag the views report as a new order becomes one move before a sibling.
export class StoryMapClient extends StoryMapClientGenerated {
  private made: { state: StoryMapData; epics: EpicOnPage[]; increments: IncrementOnPage[] } | null = null

  // The story map of the session open in the project: the page with no file to open follows it, so a ticket activated
  // on the board shows its own map on the next read.
  static async inOpenSession(api: CddApi): Promise<StoryMapClient | null> {
    const state = await StoryMapClientGenerated.openInSession(api)
    return state ? new StoryMapClient(api, state) : null
  }

  // The map another client of the same file read, taken on here, so the views holding this client draw it.
  takeOn(read: StoryMapClientGenerated): this {
    return this.changed(read.toJSON())
  }

  // The answer an edit gives is the whole map as its file now holds it; a failed edit keeps the map as it was.
  async answerTo(edit: Edit): Answer {
    const state = await edit
    return state ? this.changed(state) : null
  }

  // The epics of the map as nodes, each with its rows and their stories, made once from each answer.
  get epicsOnPage(): EpicOnPage[] {
    return this.nodes().epics
  }

  get incrementsOnPage(): IncrementOnPage[] {
    return this.nodes().increments
  }

  // The epics the page shows: scoped, only the part the session's ticket covers (its `scope`) when the session names any
  // of its stories, each part still edited through its own node; else every epic.
  epicsShown(scoped: boolean): EpicOnPage[] {
    const scope = new Set(this.scope)
    return scoped && scope.size ? this.epicsOnPage.flatMap(epic => epic.within(scope) ?? []) : this.epicsOnPage
  }

  // A new epic, placed before the epic before names, else last.
  addEpic(name: string, before?: EpicOnPage): Answer {
    return addedBefore(this, this.newEpic(name).then(map => map?.toJSON() ?? null), answered => answered.epics.at(-1)?.node, before, address => EpicClientGenerated.named(this.api, address))
  }

  addIncrement(name: string): Answer {
    return this.answerTo(this.newIncrement(name).then(map => map?.toJSON() ?? null))
  }

  // A drag reports the order the siblings take: the node dropped goes before the one now after it. Dropped last, every
  // sibling it passed goes before it in turn, since a node moves only before another.
  async reorder(siblings: StoryNodeOnPage[], order: string[]): Answer {
    const before = siblings.map(node => node.id)
    const byId = new Map(siblings.map(node => [node.id, node]))
    const without = (nodes: string[], node: string) => nodes.filter(each => each !== node).join('\n')
    const moved = byId.get(order.find((node, index) => node !== before[index] && without(before, node) === without(order, node)) ?? '')
    if (!moved) return this
    const next = byId.get(order[order.indexOf(moved.id) + 1] ?? '')
    if (next) return moved.moveBefore(next)
    let answered: StoryMapClient | null = this
    for (const passed of before.slice(before.indexOf(moved.id) + 1)) answered = await byId.get(passed)!.moveBefore(moved)
    return answered
  }

  // The nodes made from the answer the map holds now, made again only once another answer arrives.
  private nodes(): { epics: EpicOnPage[]; increments: IncrementOnPage[] } {
    const state = this.toJSON()
    if (this.made?.state !== state) {
      this.made = { state, epics: state.epics.map(epic => EpicOnPage.of(this, epic)), increments: state.increments.map(increment => new IncrementOnPage(this, increment)) }
    }
    return this.made
  }

  // A format turned on or off here is the session's choice for the fidelity, the one the chat bar's chips show, and the
  // next edit renders to it.
  async chooseFormat(format: string, isChosen: boolean): Promise<this | null> {
    const formats = new FidelitySessionOutputClientGenerated(this.api, this.formats)
    return (await formats.chooseFormat(format, isChosen)) ? this.show() : null
  }
}
