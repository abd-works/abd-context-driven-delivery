/**
 * States each behavior of Set Stage WIP Limit once. Reaches the tier only through its driver.
 * The sentences match kanban_tools_spec.py, except the last, which that spec does not state.
 */
import { shareBehavior } from 'test-utils/behavior-test/behavior-test'

export type WipLimitsDriver = {
  setWipLimit: (stage: string, limit: number) => Promise<void>
  limitOf: (stage: string) => Promise<number>
  isOverLimit: (stage: string) => Promise<boolean>
}

export const wipLimitsBehavior = shareBehavior<WipLimitsDriver>(({ describe, it, before, expect, driver }) => {
  describe('a board', () => {
    it('should give every stage a limit of 3 tickets until a person sets one', async () => {
      expect(await driver().limitOf('Specification')).toEqual(3)
    })

    it('should leave a stage holding fewer tickets than its limit within it', async () => {
      expect(await driver().isOverLimit('Specification')).toEqual(false)
    })

    describe("that sets a stage's limit below the tickets it holds", () => {
      before(() => driver().setWipLimit('Specification', 1))

      it('should show the stage over its limit', async () => {
        expect(await driver().isOverLimit('Specification')).toEqual(true)
      })
    })
  })
})
