/**
 * Story: {Story Verb-Noun} (scenario fidelity - tier-neutral).
 * Calls helper-interface methods only - no assertions, no tier mechanism here.
 *
 * Tiers: {story_verb_noun}_test_helper.{tier}.ts implements {StoryVerbNoun}Helper
 * (tier ∈ domain | client | server | e2e | project-specific, e.g. api, db).
 */

import { scenario, story } from "../../../story-test";

export interface {StoryVerbNoun}Helper {
  givenPrecondition(): void | Promise<void>;
  whenAction(): void | Promise<void>;
  thenOutcome(): void | Promise<void>;
}

export function create{StoryVerbNoun}Story(h: {StoryVerbNoun}Helper): void {
  story("{Story Verb-Noun}", () => {
    scenario("{main-flow outcome}", ({ given, when, then }) => {
      given("{given step text}", () => h.givenPrecondition());
      when("{when step text}", () => h.whenAction());
      then("{then step text}", () => h.thenOutcome());
    });
  });
}
