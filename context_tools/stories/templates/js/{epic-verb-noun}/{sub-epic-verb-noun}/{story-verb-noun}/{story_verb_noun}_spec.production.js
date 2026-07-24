/**
 * ---
 * fidelity: [engineering]
 * artifact: [tier-spec]
 * format: js
 * ---
 *
 * Tier: production — same story, ExampleFactory builds {Type} with real collaborators.
 *
 * Run:  node --test …/{story_verb_noun}_spec.production.js
 */

import { describe } from "node:test";
import { create{StoryVerbNoun}Story } from "./{story_verb_noun}_story.js";

describe("tier: production", () => {
  create{StoryVerbNoun}Story("production");
});
