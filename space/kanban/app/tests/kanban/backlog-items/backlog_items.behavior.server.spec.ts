/**
 * Runs the shared behavior on BacklogItemAdapter, which calls the real cdd server on a throwaway project. Nothing is stubbed;
 * the results are checked from the object's side: what starting answered, and what the board shows.
 */
import { afterAll, beforeEach, describe, expect, it } from 'vitest'

import { BacklogItemAdapter } from '@cdd/space/kanban/backlog-item'
import { BoardAdapter } from '@cdd/space/kanban/board'
import { TicketAdapter, type TicketData } from '@cdd/space/kanban/ticket'
import { itBehavesLike } from 'test-utils/behavior-test/behavior-test'
import { CddProject } from 'test-utils/behavior-test/cdd-project'

import { backlogItemsBehavior, type BacklogItemsDriver } from './backlog_items.spec.shared'

const project = new CddProject()

class BacklogItemsAdapterDriver implements BacklogItemsDriver {
  private readonly started = new Map<string, TicketData>()

  private async items() {
    return (await new BoardAdapter(project.cdd).show()).columns.flatMap(column => column.items ?? [])
  }

  async add(title: string, text: string): Promise<void> {
    await BacklogItemAdapter.create(project.cdd, title, text)
  }

  async start(title: string): Promise<void> {
    this.started.set(title, await new BacklogItemAdapter(project.cdd, title).start())
  }

  async moveToBacklog(ticket: string): Promise<void> {
    await new TicketAdapter(project.cdd, ticket).movePrevious()
  }

  async textOf(title: string): Promise<string> {
    return (await this.items()).find(item => item.title === title)?.text ?? ''
  }

  async isInBacklog(title: string): Promise<boolean> {
    return (await this.items()).some(item => item.title === title)
  }

  async columnOfTicket(title: string): Promise<string> {
    return this.started.get(title)!.column.name
  }

  async stateOfWork(title: string, fidelity: string): Promise<string> {
    return this.started.get(title)!.progress.find(progress => progress.slug === fidelity)?.state ?? ''
  }
}

let driver: BacklogItemsAdapterDriver

beforeEach(() => {
  project.reset()
  driver = new BacklogItemsAdapterDriver()
})

afterAll(() => project.close())

itBehavesLike(backlogItemsBehavior, { describe, it, before: beforeEach, expect, driver: () => driver })
