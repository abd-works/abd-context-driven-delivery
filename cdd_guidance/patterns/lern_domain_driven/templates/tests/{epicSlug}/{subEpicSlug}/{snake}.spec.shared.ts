/**
 * States each behavior once. Reaches the tier only through its driver, so every tier runs these same signatures.
 *
 * ```
 * file: tests/{epicSlug}/{subEpicSlug}/{snake}.spec.shared.ts
 * ```
 */
import { shareBehavior } from 'test-utils/behavior-test/behavior-test'

export type {Domain}Driver = {
  {operation}: ({identity}: string) => Promise<void>
  {reading}Of: ({identity}: string) => Promise<string>
}

export const {snake}Behavior = shareBehavior<{Domain}Driver>(({ describe, it, before, expect, driver }) => {
  describe('a {domain}', () => {
    describe('that has been {eventPastParticiple}', () => {
      before(() => driver().{operation}('{example}'))

      it('should {observableOutcome}', async () => {
        expect(await driver().{reading}Of('{example}')).toEqual('{expected}')
      })
    })
  })
})
