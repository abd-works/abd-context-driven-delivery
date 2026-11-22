/**
 * Scenario template — refer to cdd_guidance/references/language-tools.md for tooling.
 *
 * ## Artifact layout (`artifacts-mirror-story-hierarchy`)
 *
 * Mirror Epic → SubEpic → Story on disk:
 *
 * ```
 * {epic-verb-noun}/                         # kebab-case folder
 *   {sub-epic-verb-noun}/
 *     {story-kebab-slug}/
 *       {story_snake}_story.test.md          # scenarios fidelity
 *       {story_snake}_story.test.ts         # acceptance_tests — not .spec.
 *
 * # Machinery — copy once per tests/ tree if missing (do not inline in skills):
 *   practices/stories/templates/ts/story-test.ts → tests/story-test.ts
 *   (into the step library folder when a pattern names one — LERN: test-utils/story-test/story-test.ts)
 * ```
 *
 * ## Path naming (`kebab-case-paths`)
 *
 * Epic, sub-epic, and story **folders**: lowercase kebab-case. The test file is `{story_snake}_story.test.ts`.
 * Exception: Python epic helper only — `{epic_slug}_helper.py` at epic root.
 *
 * ## Scenario realizations (default on unless the user says "no realizations")
 *
 * Add a ```realization``` block under each When in `{story_snake}_story.test.md`.
 * Spec data and story tests round-trip `realization` via `practices/stories/model`.
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
 * never repeat literals across scenarios. Golden layout: `practices/stories/_examples/telco-website/`.
 *
 * import { validAccountCredentials } from "./examples/account-credentials.examples";
 *
 * Pattern: GWT structure only — // test code goes here in each step callback.
 *
 * ## The sample below (`edge-and-error-cases-have-scenarios`)
 *
 * A sample story placing an order, written out so you can see a filled-in file: replace each part with your own.
 *   {Story Verb–Noun}                     → the story's name, as the story map names it
 *   the background's given                → the domain state every scenario starts from
 *   "customer places an order ..."        → the main flow: one scenario, its outcome, `.and()` for each further outcome
 *   "customer places an order ... empty"  → one scenario for each edge or error case that applies, written like any
 *                                           other scenario; keep no table or list of cases beside them
 * Add as many edge and error scenarios as the story has cases; write none for a case that does not apply.
 */

import { afterAll, beforeAll } from "vitest";
import { background, scenario, story } from "../../story-test";

story("{Story Verb–Noun}", () => {
  beforeAll(async () => {
    // infrastructure — boot / wiring (not domain Given)
  });

  afterAll(async () => {
    // infrastructure — teardown
  });

  background(({ given }) => {
    given("a customer has a cart", async () => {
      // domain state only
    });

    scenario("customer places an order for the books in the cart", ({ given, when, then }) => {
      given("the cart holds one book", async () => {
        // test code goes here
      });
      when("the customer places the order", async () => {
        // test code goes here
      });
      then("an order holds the book", async () => {
        // test code goes here
      }).and("the cart is empty", async () => {
        // chain with .and(), not a second then()
      });
    });

    scenario("customer places an order for an empty cart", ({ given, when, then }) => {
      given("the cart holds no book", async () => {
        // test code goes here
      });
      when("the customer places the order", async () => {
        // test code goes here
      });
      then("the order is refused because the cart is empty", async () => {
        // test code goes here
      }).and("no order is created", async () => {
        // test code goes here
      });
    });
  });
});
