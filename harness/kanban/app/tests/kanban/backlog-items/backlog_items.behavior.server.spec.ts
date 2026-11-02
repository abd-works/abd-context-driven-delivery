/**
 * Runs the shared behavior on BacklogItemNode, which calls the real cdd server on a throwaway project. Nothing is stubbed;
 * the results are checked from the object's side: what starting answered, and what the board shows.
 */
import { afterAll, beforeEach, describe, expect, it } from 'vitest'

import type { Ticket } from '@cdd/harness/kanban/ticket'
import { BacklogItemNode } from '@src/kanban/backlog-item/backlog-item-node'
import { BoardNode } from '@src/kanban/board/board-node'
import { TicketNode } from '@src/kanban/ticket/ticket-node'
import { itBehavesLike } from 'test-utils/behavior-test/behavior-test'
import { CddProject } from 'test-utils/behavior-test/cdd-project'

import { backlogItemsBehavior, type BacklogItemsDriver } from './backlog_items.spec.shared'

const project = new CddProject()

class BacklogItemsNodeDriver implements BacklogItemsDriver {
  private readonly started = new Map<string, Ticket>()

  private async items() {
    return (await new BoardNode(project.cdd).show()).columns.flatMap(column => column.items ?? [])
  }

  async add(title: string, text: string): Promise<void> {
    await BacklogItemNode.add(project.cdd, title, text)
  }

  async start(title: string): Promise<void> {
    this.started.set(title, await new BacklogItemNode(project.cdd, title).start())
  }

  async moveToBacklog(ticket: string): Promise<void> {
    await new TicketNode(project.cdd, ticket).movePrevious()
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

let driver: BacklogItemsNodeDriver

beforeEach(() => {
  project.reset()
  driver = new BacklogItemsNodeDriver()
})

afterAll(() => project.close())

itBehavesLike(backlogItemsBehavior, { describe, it, before: beforeEach, expect, driver: () => driver })
