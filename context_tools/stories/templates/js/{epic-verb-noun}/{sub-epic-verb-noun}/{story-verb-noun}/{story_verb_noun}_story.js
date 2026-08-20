/**
 * ---
 * fidelity: [exploration, specification]
 * artifact: [story-file]
 * format: js
 * ---
 *
 * Story: {Story Verb-Noun} (scenario fidelity - tier-neutral).
 * Calls helper-object methods only - no assertions, no tier mechanism here.
 *
 * Tiers: {story_verb_noun}_test_helper.{tier}.js implements {StoryVerbNoun}Helper
 * (tier ∈ domain | client | server | e2e | project-specific, e.g. api, db).
 *
 * @typedef {object} {StoryVerbNoun}Helper
 * @property {function(): (void|Promise<void>)} givenPrecondition
 * @property {function(): (void|Promise<void>)} whenAction
 * @property {function(): (void|Promise<void>)} thenOutcome
 * @property {function(): (void|Promise<void>)} thenAndOutcome
 */

import { scenario, story } from "../../../story-test.js";

/** @param {{StoryVerbNoun}Helper} h */
export function create{StoryVerbNoun}Story(h) {
  story("{Story Verb-Noun}", () => {
    scenario("{main-flow outcome name}", ({ given, when, then }) => {
      given("{given step text}", () => h.givenPrecondition());
      when("{when step text}", () => h.whenAction());
      then("{then step text}", () => h.thenOutcome())
        .and("{and step text}", () => h.thenAndOutcome());
    });
  });
}
