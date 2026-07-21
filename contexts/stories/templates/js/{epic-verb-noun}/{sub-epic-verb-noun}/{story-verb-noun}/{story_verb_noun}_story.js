/**
 * ---
 * fidelity: [exploration, specification]
 * artifact: [story-file]
 * format: js
 * ---
 *
 * Story: {Story Verb-Noun} (tier-neutral).
 * Wired to ExampleFactory fakes — not a tier test.
 * Assert the public interface of I{Type} only.
 *
 * Run:  node --test …/{story_verb_noun}_story.js
 * Specs: {story_verb_noun}_spec.js (isolated); {story_verb_noun}_spec.{tier}.js (other tiers)
 */

import assert from "node:assert/strict";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { ManageCharacterSheetHelper as EpicHelper } from "../../{epic-verb-noun}-helper.js";
import { scenario, story } from "../../../story-test.js";

const helper = new EpicHelper();

/**
 * Shared scenarios. Story file runs with mode "fake".
 * Tier specs call this with "isolated" | "production".
 */
export function create{StoryVerbNoun}Story(mode) {
  story("{Story Verb-Noun}", () => {
    scenario("{main-flow outcome name}", ({ given, when, then }) => {
      let subject;

      given("a domain object from the ExampleFactory", () => {
        // helper.given…({ mode }) — fake I{Type}; values from examples[{example_key}]
        subject = null;
      });

      when("the Actor exercises a public operation", () => {
        // public seam only
      });

      then("an observable outcome is visible on the public interface", () => {
        assert.ok(subject);
      });
    });
  });
}

const thisFile = fileURLToPath(import.meta.url);
const entry = process.argv[1] && path.resolve(process.argv[1]);
if (entry && path.resolve(thisFile) === entry) {
  create{StoryVerbNoun}Story("fake");
}
