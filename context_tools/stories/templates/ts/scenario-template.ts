/**
 * Scenario template — refer to context_tools/language-tools.md for tooling.
 *
 * ```
 * # Artifact layout (artifacts-mirror-story-hierarchy)
 * tests/
 *   {epic-verb-noun}/
 *     {sub-epic-verb-noun}/              # omit when the story file lives under epic/
 *       {story-kebab-slug}.{tier}.ts     # one GWT file per story per tier
 *
 * # Machinery — copy once per tests/ tree if missing (do not inline in skills):
 *   context_tools/stories/templates/ts/story-test.ts → tests/story-test.ts
 * story-test: tests/story-test.ts
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
