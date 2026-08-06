/** Tier: server - {StoryVerbNoun}Helper backed by Supertest against the real route. */
import { describe } from "vitest";
import { create{StoryVerbNoun}Story, type {StoryVerbNoun}Helper } from "./{story_verb_noun}_story";

class ServerHelper implements {StoryVerbNoun}Helper {
  givenPrecondition(): void | Promise<void> {
    throw new Error("not implemented: givenPrecondition");
  }
  whenAction(): void | Promise<void> {
    throw new Error("not implemented: whenAction");
  }
  thenOutcome(): void | Promise<void> {
    throw new Error("not implemented: thenOutcome");
  }
}

describe("tier: server", () => {
  create{StoryVerbNoun}Story(new ServerHelper());
});
