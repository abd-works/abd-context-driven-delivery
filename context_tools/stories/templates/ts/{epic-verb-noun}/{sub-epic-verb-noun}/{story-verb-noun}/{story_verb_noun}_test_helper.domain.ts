/** Tier: domain - {StoryVerbNoun}Helper backed by direct domain-class calls. */
import { describe } from "vitest";
import { create{StoryVerbNoun}Story, type {StoryVerbNoun}Helper } from "./{story_verb_noun}_story";

class DomainHelper implements {StoryVerbNoun}Helper {
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

describe("tier: domain", () => {
  create{StoryVerbNoun}Story(new DomainHelper());
});
