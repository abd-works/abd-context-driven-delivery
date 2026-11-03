/**
 * Runs the shared behavior on BacklogItemNodeAdapter, which calls the real cdd server on a throwaway project. Nothing is stubbed;
 * the results are checked from the object's side: what starting answered, and what the board shows.
 */
import { afterAll, beforeEach, describe, expect, it } from 'vitest'

import { BacklogItemNodeAdapter } from '@cdd/harness/kanban/backlog-item-node-adapter'
import { BoardNodeAdapter } from '@cdd/harness/kanban/board-node-adapter'
import type { TicketData } from '@cdd/harness/kanban/ticket'
import { TicketNodeAdapter } from '@cdd/harness/kanban/ticket-node-adapter'
import { itBehavesLike } from 'test-utils/behavior-test/behavior-test'
import { CddProject } from 'test-utils/behavior-test/cdd-project'

import { backlogItemsBehavior, type BacklogItemsDriver } from './backlog_items.spec.shared'

const project = new CddProject()

class BacklogItemsNodeAdapterDriver implements BacklogItemsDriver {
  private readonly started = new Map<string, TicketData>()

  private async items() {
    return (await new BoardNodeAdapter(project.cdd).show()).columns.flatMap(column => column.items ?? [])
  }

  async add(title: string, text: string): Promise<void> {
    await BacklogItemNodeAdapter.add(project.cdd, title, text)
  }

  async start(title: string): Promise<void> {
    this.started.set(title, await new BacklogItemNodeAdapter(project.cdd, title).start())
  }

  async moveToBacklog(ticket: string): Promise<void> {
    await new TicketNodeAdapter(project.cdd, ticket).movePrevious()
  }

  async textOf(title: string): Promise<string> {
    return (await this.items()).find(item => item.title === title)?.text ?? ''
  }

  async isInBacklog(title: string): Promise<boolean> {
    return (await this.items()).some(item => item.title === title)
  }

  async columnOfTicket(title: string): Promise<string> {
    return this.started.get(title)!.column
  }

  async stateOfWork(title: string, fidelity: string): Promise<string> {
    return this.started.get(title)!.progress[fidelity] ?? ''
  }
}

let driver: BacklogItemsNodeAdapterDriver

beforeEach(() => {
  project.reset()
  driver = new BacklogItemsNodeAdapterDriver()
})

afterAll(() => project.close())

itBehavesLike(backlogItemsBehavior, { describe, it, before: beforeEach, expect, driver: () => driver })
