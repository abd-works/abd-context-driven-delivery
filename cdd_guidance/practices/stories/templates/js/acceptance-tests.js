/**
 * Acceptance tests template (JavaScript) — refer to cdd_guidance/references/language-tools.md for tooling.
 *
 * A story test is its scenarios file in code with every step's body filled in: each Given seeds state through its
 * real owner, each When calls the domain operation it tests, each Then asserts what the product answered. The files
 * this fidelity writes, one shape each below; they are named as the TypeScript ones are, with `.js`:
 *
 * ```
 * story_tests/{epic}/{sub-epic}/
 *   {story}/{story_snake}_story.test.js          # one story, run on its own (FILE 1)
 *   {sub_epic_slug}.story.shared.js              # scenarios every tier replays, registered once (FILE 2)
 *   {sub_epic_slug}.story.domain.spec.js         # the shared scenarios on the domain objects (FILE 3)
 *   {sub_epic_slug}.story.server.spec.js         # the same scenarios through the server (FILE 3, other tier)
 *   {sub_epic_slug}.story.ui.spec.js             # the same scenarios in the browser, each step captured
 * story_tests/{epic}/examples/{concept}.examples.js   # named examples (FILE 4)
 *
 * # Machinery — copy once per tests/ tree if missing, and import it with its extension:
 *   practices/stories/templates/js/story-test.js → tests/story-test.js
 * ```
 *
 * Write a story as FILE 1 when one tier proves it; write FILES 2 and 3 when the sub-epic's stories run at more than
 * one tier, so each tier replays one copy of the steps.
 */

// FILE 1: story_tests/{epic}/{sub-epic}/{story}/{story_snake}_story.test.js
import { expect } from "vitest";
import { scenario, story } from "../../../story-test.js";
import { STORED_{EXAMPLE}, seed{Example} } from "../../examples/{concept}.examples.js";
import { {ClassName}Repository, {DomainRefusal} } from "../../../../src/{module}/{family-slug}.js";

story("{Story Verb–Noun}", () => {
  scenario("{actor} {does the main flow}", ({ given, when, then }) => {
    let repository;
    let answer;
    given("{the state the scenario starts from}", () => {
      repository = seed{Example}(new {ClassName}Repository());
    });
    when("{actor} {does the action}", () => {
      answer = repository.load(STORED_{EXAMPLE}.identity).{operation}(STORED_{EXAMPLE}.value);
    });
    then("{the outcome a person can check}", () => {
      expect(answer.{property}).toEqual(STORED_{EXAMPLE}.expected);
    });
  });

  scenario("{actor} {does the action} {in the edge or error case}", ({ given, when, then }) => {
    let repository;
    given("{the state of that case}", () => {
      repository = seed{Example}(new {ClassName}Repository());
    });
    when("{actor} {does the action}", () => {});
    then("{the refusal names what was refused}", () => {
      expect(() => repository.load(STORED_{EXAMPLE}.identity).{operation}(undefined)).toThrow({DomainRefusal});
    });
  });
});

// FILE 2: story_tests/{epic}/{sub-epic}/{sub_epic_slug}.story.shared.js
// Register the stories once; steps reach the product only through the world a tier hands them.
import { createStorySuite, scenario as sharedScenario } from "../../story-test.js";

export function {subEpicCamel}Stories(world) {
  const suite = createStorySuite();
  suite.defineStory("{Story Verb–Noun}", () => {
    sharedScenario("{actor} {does the main flow}", ({ given, when, then }) => {
      given("{the state the scenario starts from}", () => world.seed(STORED_{EXAMPLE}));
      when("{actor} {does the action}", async () => {
        world.answer = await world.{className}.load(STORED_{EXAMPLE}.identity).{operation}(STORED_{EXAMPLE}.value);
      });
      then("{the outcome a person can check}", () => {
        expect(world.answer.{property}).toEqual(STORED_{EXAMPLE}.expected);
      });
    });
  });
  return suite;
}

// FILE 3: story_tests/{epic}/{sub-epic}/{sub_epic_slug}.story.domain.spec.js (server: .story.server.spec.js)
// The tier names its world: the domain objects themselves, or the same operations through the server.
import { {subEpicCamel}Stories } from "./{sub_epic_slug}.story.shared.js";
import { {Tier}World } from "../../test-utils/{tier}-world.js";

{subEpicCamel}Stories(new {Tier}World()).runAllStories();

// FILE 4: story_tests/{epic}/examples/{concept}.examples.js — one named example for each example the scenarios name.
export const STORED_{EXAMPLE} = Object.freeze({ identity: "{id}", value: "{value}", expected: "{expected}" });

/** Seed state at its real owner: the repository, or the external system's test adapter beneath it. */
export function seed{Example}(repository) {
  repository.create(STORED_{EXAMPLE}.identity, STORED_{EXAMPLE}.value);
  return repository;
}
