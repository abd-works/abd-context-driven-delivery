/**
 * ---
 * fidelity: [engineering]
 * artifact: [test-helper]
 * format: js
 * ---
 *
 * Tier: server - {StoryVerbNoun}Helper backed by Supertest against the real route.
 * Real: domain + repository + test DB. Stubbed: nothing.
 */

import { describe } from "node:test";
import { create{StoryVerbNoun}Story } from "./{story_verb_noun}_story.js";

class ServerHelper {
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

describe("tier: server", () => {
  create{StoryVerbNoun}Story(new ServerHelper());
});
