/**
 * ---
 * fidelity: [engineering]
 * artifact: [isolated-spec]
 * format: js
 * ---
 *
 * Isolated objects — same story, ExampleFactory builds {Type} with injected deps.
 *
 * Run:  node --test …/{story_verb_noun}_spec.js
 */

import { describe } from "node:test";
import { create{StoryVerbNoun}Story } from "./{story_verb_noun}_story.js";

describe("tier: isolated", () => {
  create{StoryVerbNoun}Story("isolated");
});
