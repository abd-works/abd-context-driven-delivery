/**
 * Runs the shared behavior on TicketNodeAdapter, which calls the real cdd server on a throwaway project. Nothing is stubbed;
 * the results are checked from the object's side: what a move answered, and what the board shows.
 */
import { afterAll, beforeEach, describe, expect, it } from 'vitest'

import { BoardNodeAdapter } from '@cdd/harness/kanban/board-node-adapter'
import type { TicketData } from '@cdd/harness/kanban/ticket'
import { TicketNodeAdapter } from '@cdd/harness/kanban/ticket-node-adapter'
import { itBehavesLike } from 'test-utils/behavior-test/behavior-test'
import { CddProject } from 'test-utils/behavior-test/cdd-project'

import { moveTicketBehavior, type MoveTicketDriver, type TicketPlace } from './move_ticket.spec.shared'

const project = new CddProject()

class MoveTicketNodeNodeAdapterDriver implements MoveTicketDriver {
  private readonly moved = new Map<string, TicketData>()

  private ticket(name: string): TicketNodeAdapter {
    return new TicketNodeAdapter(project.cdd, name)
  }

  async moveNext(ticket: string): Promise<void> {
    this.moved.set(ticket, (await this.ticket(ticket).moveNext()).toJSON())
  }

  async dragTo(ticket: string, stage: string, done: boolean): Promise<void> {
    this.moved.set(ticket, (await this.ticket(ticket).moveTo(stage, done)).toJSON())
  }

  async movePrevious(ticket: string): Promise<void> {
    this.moved.set(ticket, (await this.ticket(ticket).movePrevious()) as TicketData)
  }

  async placeOf(ticket: string): Promise<TicketPlace> {
    const { column, is_done: isDone } = this.moved.get(ticket)!
    return { column, isDone }
  }

  private async columns() {
    return (await new BoardNodeAdapter(project.cdd).show()).columns
  }

  async isOnTheStages(ticket: string): Promise<boolean> {
    const stages = (await this.columns()).filter(column => column.work_required)
    return stages.flatMap(stage => [...(stage.in_progress ?? []), ...(stage.done ?? [])]).some(shown => shown.name === ticket)
  }

  async backlogTitles(): Promise<string[]> {
    return (await this.columns()).flatMap(column => column.items ?? []).map(item => item.title)
  }
}

let driver: MoveTicketNodeNodeAdapterDriver

beforeEach(() => {
  project.reset()
  driver = new MoveTicketNodeNodeAdapterDriver()
})

afterAll(() => project.close())

itBehavesLike(moveTicketBehavior, { describe, it, before: beforeEach, expect, driver: () => driver })
