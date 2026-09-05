/**
 * Scenario template — refer to context_tools/language-tools.md for tooling.
 *
 * ```
 * # Params — fill before writing code
 * epic:       {epic-verb-noun}           # kebab folder under tests/
 * sub_epic:   {sub-epic-verb-noun}       # kebab folder under epic/ (omit level if story hangs off epic)
 * story:      {story-verb-noun}          # Verb Noun title from the story map
 * story_file: {story-kebab-slug}         # kebab file slug, e.g. sign-up-create-account
 * tier:       e2e | front-end | back-end | {system}
 *
 * # Artifact layout (artifacts-mirror-story-hierarchy)
 * tests/
 *   {epic-verb-noun}/
 *     {sub-epic-verb-noun}/              # omit when the story file lives under epic/
 *       {story-kebab-slug}.{tier}.ts     # one GWT file per story per tier
 *
 * # Machinery (copy once per tests/ tree — full source inlined below)
 * story-test: tests/story-test.ts
 *
 * # Naming rules
 * - Epic / SubEpic folders → kebab-case verb-noun (Sign Up → sign-up)
 * - Story test file        → {story-kebab-slug}.{tier}.ts at epic or sub-epic — NO {story}/ folder
 * - Tier                   → file extension segment (.e2e.ts, .front-end.ts, .back-end.ts)
 * - Forbidden              → {story}/ folders, *_story.*, *_test_helper.* splits
 * ```
 *
 * Pattern: GWT structure only — // test code goes here in each step callback.
 */

import { afterAll, beforeAll } from "vitest";
import { background, scenario, story } from "../../story-test";

story("{Story Verb-Noun}", () => {
  beforeAll(async () => {
    // boot — test code goes here
  });

  afterAll(async () => {
    // teardown — test code goes here
  });

  background(({ given }) => {
    given("{background given step}", async () => {
      // test code goes here
    });

    scenario("{surface check — e.g. rules visible}", ({ when, then }) => {
      when("{primary when step}", async () => {
        // test code goes here
      });
      then("{observable surface outcome}", async () => {
        // test code goes here
      });
    });

    scenario("{validation branch while typing}", ({ when, then }) => {
      when("{primary when step}", async () => {
        // test code goes here
      }).and("{follow-on when step}", async () => {
        // test code goes here
      });
      then("{validation message on domain object}", () => {
        // test code goes here
      });
    });

    scenario("{validation clears when input conforms}", ({ when, then }) => {
      when("{primary when step}", async () => {
        // test code goes here
      }).and("{prior invalid state}", async () => {
        // test code goes here
      });
      when("{corrective action}", async () => {
        // test code goes here
      });
      then("{error cleared on domain object}", () => {
        // test code goes here
      });
    });

    scenario("{main-flow outcome}", ({ when, then }) => {
      when("{primary when step}", async () => {
        // test code goes here
      });
      when("{submit operation on domain object}", async () => {
        // test code goes here
      });
      then("{post-condition on loaded aggregate}", async () => {
        // test code goes here
      });
    });
  });
});
