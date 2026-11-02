/**
 * Runs the shared behavior on the node object, which calls what it really calls: its lowdb store, or the MCP tool
 * of a CDD-backed domain. Nothing is stubbed; the results are checked from the object's side.
 *
 * ```
 * file: tests/{epicSlug}/{subEpicSlug}/{snake}.behavior.server.spec.ts
 * ```
 */
import { beforeEach, describe, expect, it } from 'vitest'

import { {Domain}Node } from '@src/{boundedContext}/{aggregate}/{aggregate}-node'
import { itBehavesLike } from 'test-utils/behavior-test/behavior-test'
import { {snake}Behavior, type {Domain}Driver } from './{snake}.spec.shared'

class {Domain}NodeDriver implements {Domain}Driver {
  async {operation}({identity}: string): Promise<void> {
    await (await {Domain}Node.load({identity})).{operation}()
  }

  async {reading}Of({identity}: string): Promise<string> {
    return (await {Domain}Node.load({identity})).{reading}
  }
}

itBehavesLike({snake}Behavior, { describe, it, before: beforeEach, expect, driver: () => new {Domain}NodeDriver() })
