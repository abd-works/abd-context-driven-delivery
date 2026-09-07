/**
 * Scenario template — refer to context_tools/language-tools.md for tooling.
 *
 * ## Artifact layout (`artifacts-mirror-story-hierarchy`)
 *
 * Mirror Epic → SubEpic → Story on disk:
 *
 * ```
 * tests/
 *   {epic-verb-noun}/                    # kebab-case folder
 *     {sub-epic-verb-noun}/              # omit when the story file lives under epic/
 *       {story-kebab-slug}.ts            # one GWT file per story — no {story}/ folder
 *
 * # Machinery — copy once per tests/ tree if missing (do not inline in skills):
 *   context_tools/stories/templates/ts/story-test.ts → tests/story-test.ts
 * ```
 *
 * ## Path naming (`kebab-case-paths`)
 *
 * Epic and SubEpic folders, story file stems, tier segments: lowercase kebab-case.
 * Exception: Python epic helper only — `{epic_slug}_helper.py` at epic root.
 *
 * ## Outcome chaining (`then-and-chaining`)
 *
 * First outcome: `then(...)`. Further outcomes on the same interaction: `.and(...)`.
 *
 * ## Lifecycle hooks (`infrastructure-in-lifecycle-hooks`)
 *
 * Browser boot, app wiring, and initialize in `beforeAll` / `afterAll` — not in `given()`.
 *
 * ## Assertion helpers (`extract-assertion-helper`)
 *
 * Same assertion shape more than twice → named helper with a data bag; call sites pass values only.
 *
 * ## Example fixtures (`shared-example-fixtures`)
 *
 * Named domain fixtures under `examples/` at the lowest **shared** folder (epic, sub-epic, or story).
 * One file per domain concept (`account-credentials.examples.ts`). Import in the story file;
 * never repeat literals across scenarios. Golden layout: `context_tools/stories/examples/telco-website/`.
 *
 * import { validAccountCredentials } from "./examples/account-credentials.examples";
 *
 * Pattern: GWT structure only — // test code goes here in each step callback.
 */

import { afterAll, beforeAll } from "vitest";
import { background, scenario, story } from "../../story-test";

story("{Story Verb-Noun}", () => {
  beforeAll(async () => {
    // infrastructure — boot / wiring (not domain Given)
  });

  afterAll(async () => {
    // infrastructure — teardown
  });

  background(({ given }) => {
    given("{background given step}", async () => {
      // domain state only
    });

    scenario("{surface check — e.g. rules visible}", ({ when, then }) => {
      when("{primary when step}", async () => {
        // test code goes here
      });
      then("{observable surface outcome}", async () => {
        // test code goes here
      }).and("{further outcome on same interaction}", async () => {
        // chain with .and(), not a second then()
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
