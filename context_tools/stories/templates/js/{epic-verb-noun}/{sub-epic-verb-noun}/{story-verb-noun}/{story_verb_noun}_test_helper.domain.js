/**
 * ---
 * fidelity: [engineering]
 * artifact: [test-helper]
 * format: js
 * ---
 *
 * Tier: domain - {StoryVerbNoun}Helper backed by direct domain-class calls.
 * Real: domain-core class. Stubbed: nothing.
 */

import { describe } from "node:test";
import { create{StoryVerbNoun}Story } from "./{story_verb_noun}_story.js";

class DomainHelper {
  givenPrecondition() {
    throw new Error("not implemented: givenPrecondition");
  }
  whenAction() {
    throw new Error("not implemented: whenAction");
  }
  thenOutcome() {
    throw new Error("not implemented: thenOutcome");
  }
}

describe("tier: domain", () => {
  create{StoryVerbNoun}Story(new DomainHelper());
});
