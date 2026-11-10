// story-runner.js — generic runner for JS tier tests.
//
// Runtime step-key validation: every step in a scenario must have a matching
// entry in the tier's `given`/`when`/`then` dispatch table. First step of each
// phase is unprefixed; continuation steps carry `"And "` / `"But "` inside
// their string, matching the tier's dispatch key.

const label = (kw, i, s) => (i === 0 ? `${kw} ${s}` : s)

const dispatch = async (step, table, phase) => {
  const fn = table[step]
  if (typeof fn !== 'function') {
    throw new Error(
      `Tier is missing a '${phase}' implementation for step ${JSON.stringify(step)}. ` +
      `Add it to tier.${phase}[${JSON.stringify(step)}].`,
    )
  }
  await fn()
}

/**
 * @param {string} storyName
 * @param {import('./story-types').Scenario} scenario
 * @param {() => import('./story-types').TierImpl} makeTier
 */
export function runScenario(storyName, scenario, makeTier) {
  describe(storyName, () => {
    describe(scenario.name, () => {
      let tier

      beforeAll(async () => {
        tier = makeTier()
        for (const s of scenario.given) await dispatch(s, tier.given, 'given')
        for (const { when } of scenario.interactions) {
          for (const s of when) await dispatch(s, tier.when, 'when')
        }
      })

      afterAll(async () => {
        if (tier) await tier.cleanup()
      })

      for (const { then } of scenario.interactions) {
        then.forEach((s, i) => {
          it(label('Then', i, s), async () => {
            await dispatch(s, tier.then, 'then')
          })
        })
      }
    })
  })
}
