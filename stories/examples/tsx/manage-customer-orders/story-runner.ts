// story-runner.ts — the ONLY test-framework glue; every tier reuses it.
//
// First step of each phase gets the phase keyword; continuation steps already
// carry their own `And ` / `But ` prefix in the string.
import type { Scenario, TierImpl } from './story-types'

const label = (kw: 'Given' | 'When' | 'Then', i: number, s: string): string =>
  i === 0 ? `${kw} ${s}` : s

export function runScenario<S extends Scenario>(
  storyName: string,
  scenario: S,
  makeTier: () => TierImpl<S>,
): void {
  describe(storyName, () => {
    describe(scenario.name, () => {
      let tier: TierImpl<S>

      beforeAll(async () => {
        tier = makeTier()
        for (const s of scenario.given) await tier.given[s as never]()
        for (const { when } of scenario.interactions)
          for (const s of when) await tier.when[s as never]()
      })

      afterAll(() => tier.cleanup())

      for (const { then } of scenario.interactions)
        then.forEach((s, i) =>
          it(label('Then', i, s), () => tier.then[s as never]()),
        )
    })
  })
}
