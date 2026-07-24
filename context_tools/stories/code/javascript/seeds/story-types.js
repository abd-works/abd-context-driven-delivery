// story-types.js — shape documentation only.
//
// JavaScript is dynamically typed, so we can't produce a compile-time analogue
// of TypeScript's `TierImpl<S>`. Instead the runner (`story-runner.js`) does
// runtime step-key assertions: every step string in a scenario must map to a
// callable in `tier.given` / `tier.when` / `tier.then`; missing keys fail with
// a clear error naming the missing string and phase.

/**
 * @typedef {Object} Interaction
 * @property {readonly string[]} when — first when unprefixed; continuations start with "And "/"But ".
 * @property {readonly string[]} then — first then unprefixed; continuations start with "And "/"But ".
 */

/**
 * @typedef {Object} ScenarioExample
 * Points at a CE ExampleFactory load — concrete values live in examples[{example_key}], not in the story file.
 * @property {string} factory — e.g. 'CharacterExampleFactory'
 * @property {string} load — e.g. 'loadHandbookSheetAtRankZero'
 * @property {'fake'|'isolated'|'production'} [mode] — explore/spec default: fake
 */

/**
 * @typedef {Object} Scenario
 * @property {string} name
 * @property {readonly string[]} [background]
 * @property {readonly string[]} given
 * @property {readonly Interaction[]} interactions
 * @property {ScenarioExample} [example] — specification+: load from CE ExampleFactory (not an inline data table)
 * @property {readonly ScenarioExample[]} [examples] — outline variations = multiple factory loads
 */

/**
 * @typedef {Object} StoryBase
 * @property {string} story
 * @property {string} actor
 * @property {readonly string[]} domainTerms
 * @property {readonly string[]} evidence
 * @property {readonly string[]} [background] — shared Given across scenarios when applicable
 */

/**
 * @typedef {StoryBase & Object.<string, Scenario | string | readonly string[]>} Story
 */

/**
 * @typedef {() => (void | Promise<void>)} StepFn
 */

/**
 * @typedef {Object} TierImpl
 * @property {Object.<string, StepFn>} given
 * @property {Object.<string, StepFn>} when
 * @property {Object.<string, StepFn>} then
 * @property {StepFn} cleanup
 */

export const __types = /** @type {Story} */ ({})
