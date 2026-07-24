/**
 * Story: {Story Verb-Noun} (tier-neutral).
 * Specs: {story_verb_noun}_spec.ts (isolated); {story_verb_noun}_spec.{tier}.ts
 */

import { scenario, story } from "../../../story-test";
import { EpicVerbNounHelper } from "../../{epic-verb-noun}-helper";

const helper = new EpicVerbNounHelper();

export function create{StoryVerbNoun}Story(mode: string): void {
  story("{Story Verb-Noun}", () => {
    scenario("{main-flow outcome}", ({ given, when, then }) => {
      given("a domain object from the ExampleFactory", () => {
        // helper.given…({ mode }) — AI fills
      });
      when("the Actor exercises a public operation", () => {
        // AI fills
      });
      then("an observable outcome is visible on the public interface", () => {
        // AI fills
      });
    });
  });
}

create{StoryVerbNoun}Story("fake");
