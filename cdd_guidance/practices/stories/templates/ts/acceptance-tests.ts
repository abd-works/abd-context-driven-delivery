/**
 * Acceptance tests template (TypeScript) — refer to cdd_guidance/references/language-tools.md for tooling.
 *
 * A story test is its scenarios file in code with every step's body filled in: each Given seeds state through its
 * real owner, each When calls the domain operation it tests, each Then asserts what the product answered. The files
 * this fidelity writes, one shape each below:
 *
 * ```
 * story_tests/{epic}/{sub-epic}/
 *   {story}/{story_snake}_story.test.ts          # one story, run on its own (FILE 1)
 *   {sub_epic_slug}.story.shared.ts              # scenarios every tier replays (FILE 2)
 *   {sub_epic_slug}.story.domain.spec.ts         # the shared scenarios on the domain objects (FILE 3)
 *   {sub_epic_slug}.story.server.spec.ts         # the same scenarios through the server (FILE 3, other tier)
 *   {sub_epic_slug}.story.ui.spec.ts             # the same scenarios in the browser, each step captured (FILE 5)
 * story_tests/{epic}/examples/{concept}.examples.ts   # named examples (FILE 4)
 *
 * # Machinery — copy once per tests/ tree if missing:
 *   practices/stories/templates/ts/story-test.ts → tests/story-test.ts
 *   (into the step library folder when a pattern names one — LERN: test-utils/story-test/story-test.ts)
 * ```
 *
 * Write a story as FILE 1 when one tier proves it; write FILES 2 and 3 when the sub-epic's stories run at more than
 * one tier, so each tier replays one copy of the steps.
 */

// FILE 1: story_tests/{epic}/{sub-epic}/{story}/{story_snake}_story.test.ts
import { expect } from "vitest";
import { scenario, story } from "../../../story-test";
import { {EXAMPLE}, seed{Example} } from "../../examples/{concept}.examples";
import { {ClassName}Repository, {DomainRefusal} } from "../../../../src/{module}/{family-slug}";

story("{Story Verb–Noun}", () => {
  scenario("{actor} {does the main flow}", ({ given, when, then }) => {
    let repository: {ClassName}Repository;
    let answer: {ReturnType};
    given("{the state the scenario starts from}", () => {
      repository = seed{Example}(new {ClassName}Repository());
    });
    when("{actor} {does the action}", () => {
      answer = repository.load({EXAMPLE}.identity).{operation}({EXAMPLE}.value);
    });
    then("{the outcome a person can check}", () => {
      expect(answer.{property}).toEqual({EXAMPLE}.expected);
    });
  });

  scenario("{actor} {does the action} {in the edge or error case}", ({ given, when, then }) => {
    let repository: {ClassName}Repository;
    given("{the state of that case}", () => {
      repository = seed{Example}(new {ClassName}Repository());
    });
    when("{actor} {does the action}", () => {});
    then("{the refusal names what was refused}", () => {
      expect(() => repository.load({EXAMPLE}.identity).{operation}(undefined)).toThrow({DomainRefusal});
    });
  });
});

// FILE 2: story_tests/{epic}/{sub-epic}/{sub_epic_slug}.story.shared.ts
// Steps reach the product only through the world a tier hands them, so every tier replays the same steps.
export function {storyCamel}(world: {Sub-epic}World): void {
  story("{Story Verb–Noun}", () => {
    scenario("{actor} {does the main flow}", ({ given, when, then }) => {
      given("{the state the scenario starts from}", () => world.seed({EXAMPLE}));
      when("{actor} {does the action}", async () => {
        world.answer = await world.{className}.load({EXAMPLE}.identity).{operation}({EXAMPLE}.value);
      });
      then("{the outcome a person can check}", () => {
        expect(world.answer.{property}).toEqual({EXAMPLE}.expected);
      });
    });
  });
}

// FILE 3: story_tests/{epic}/{sub-epic}/{sub_epic_slug}.story.domain.spec.ts (server: .story.server.spec.ts)
// The tier names its world: the domain objects themselves, or the same operations through the server.
import { {storyCamel} } from "./{sub_epic_slug}.story.shared";
import { {Tier}World } from "../../test-utils/{tier}-world";

{storyCamel}(new {Tier}World());

// FILE 4: story_tests/{epic}/examples/{concept}.examples.ts — one named example for each example the scenarios name.
export const {EXAMPLE} = { identity: "{id}", value: "{value}", expected: "{expected}" } as const;

/** Seed state at its real owner: the repository, or the external system's test adapter beneath it. */
export function seed{Example}(repository: {ClassName}Repository): {ClassName}Repository {
  repository.create({EXAMPLE}.identity, {EXAMPLE}.value);
  return repository;
}

// FILE 5: story_tests/{epic}/{sub-epic}/{sub_epic_slug}.story.ui.spec.ts
// Every Given, When and Then runs through step(page, '<step text>', body), which captures the settled screen.
import { test } from "@playwright/test";
import { step } from "../../test-utils/step-capture";

test("{Story Verb–Noun} › {actor} {does the main flow}", async ({ page }) => {
  await step(page, "{the state the scenario starts from}", async () => { /* seed through the real owner */ });
  await step(page, "{actor} {does the action}", async () => { /* the gesture on the screen */ });
  await step(page, "{the outcome a person can check}", async () => { /* expect what the screen shows */ });
});
