/**
 * Runs the shared behavior on BoardNodeAdapter, which calls the real cdd server on a throwaway project. Nothing is stubbed.
 */
import { afterAll, beforeEach, describe, expect, it } from 'vitest'

import type { ColumnData } from '@cdd/harness/kanban/board'
import { BoardNodeAdapter } from '@cdd/harness/kanban/board-node-adapter'
import { itBehavesLike } from 'test-utils/behavior-test/behavior-test'
import { CddProject } from 'test-utils/behavior-test/cdd-project'

import { wipLimitsBehavior, type WipLimitsDriver } from './wip_limits.spec.shared'

const project = new CddProject()

class WipLimitsNodeAdapterDriver implements WipLimitsDriver {
  private readonly board = new BoardNodeAdapter(project.cdd)

  private async stage(name: string): Promise<ColumnData> {
    return (await this.board.show()).columns.find(column => column.name === name)!
  }

  async setWipLimit(stage: string, limit: number): Promise<void> {
    await this.board.setWipLimit(stage, limit)
  }

  async limitOf(stage: string): Promise<number> {
    return (await this.stage(stage)).wip_limit ?? 0
  }

  async isOverLimit(stage: string): Promise<boolean> {
    return (await this.stage(stage)).is_over_limit ?? false
  }
}

let driver: WipLimitsNodeAdapterDriver

beforeEach(() => {
  project.reset()
  driver = new WipLimitsNodeAdapterDriver()
})

afterAll(() => project.close())

itBehavesLike(wipLimitsBehavior, { describe, it, before: beforeEach, expect, driver: () => driver })
