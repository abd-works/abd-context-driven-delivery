/**
 * Story: {Story Verb-Noun} (conceptual reference).
 * 
 * Refer to context_tools/language-tools.md for tool recommendations.
 * 
 * Tiers: {story_verb_noun}.{tier}.ts implements the conceptual GWT steps
 * (tier ∈ front-end | back-end | external-system).
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
