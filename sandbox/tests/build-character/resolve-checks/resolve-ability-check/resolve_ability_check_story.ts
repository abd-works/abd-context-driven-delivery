/**
 * # @toolset-manifest python -m tools manifest context_tools.stories.stories:Stories
 * Story: Resolve Ability Check (tier-neutral).
 */

import { BuildCharacterHelper } from "../../build-character-helper.js";
import { assert, scenario, story } from "../../../story-test.js";

const helper = new BuildCharacterHelper();

export function resolveAbilityCheckStory(mode: string): void {
  story("Resolve Ability Check", () => {
    scenario("ability check reports die total degree and success", ({ given, when, then }: any) => {
      let bundle: any;
      let result: any;

      given("a Check from helper.givenStrengthCheckFaceEight", () => {
        bundle = helper.givenStrengthCheckFaceEight({ mode });
      });

      when("the Player resolves that Check", () => {
        result = bundle.check.resolve([], bundle.routine);
      });

      then("Check die_roll equals die face from the example", () => {
        assert.equal(bundle.check.dieRoll ?? result.dieFace, bundle.dieFace);
      });

      then("And CheckResult matches helper.expectedStrengthCheckSucceededDegreeOne", () => {
        const expected = helper.expectedStrengthCheckSucceededDegreeOne({ mode });
        assert.equal(result.total, expected.total);
        assert.equal(result.succeeded, expected.succeeded);
        assert.equal(result.degree, expected.degree);
      });
    });

    scenario("ability check failure reports negative degree", ({ given, when, then }: any) => {
      let bundle: any;
      let result: any;

      given("a Check from helper.givenStrengthCheckFailsFaceOne", () => {
        bundle = helper.givenStrengthCheckFailsFaceOne({ mode });
      });

      when("the Player resolves that Check", () => {
        result = bundle.check.resolve([], bundle.routine);
      });

      then("Check die_roll equals die face from the example", () => {
        assert.equal(bundle.check.dieRoll ?? result.dieFace, bundle.dieFace);
      });

      then("And CheckResult matches helper.expectedStrengthCheckFailedDegreeNegOne", () => {
        const expected = helper.expectedStrengthCheckFailedDegreeNegOne({ mode });
        assert.equal(result.total, expected.total);
        assert.equal(result.succeeded, expected.succeeded);
        assert.equal(result.degree, expected.degree);
      });
    });

    scenario("natural twenty adds degree and can flip near miss", ({ given, when, then }: any) => {
      let bundle: any;
      let result: any;

      given("a Check from helper.givenCriticalNaturalTwentyNearMiss", () => {
        bundle = helper.givenCriticalNaturalTwentyNearMiss({ mode });
      });

      when("the Player resolves that Check", () => {
        result = bundle.check.resolve([], bundle.routine);
      });

      then("Check die_roll equals die face from the example", () => {
        assert.equal(bundle.check.dieRoll ?? result.dieFace, bundle.dieFace);
      });

      then("And CheckResult matches helper.expectedCriticalSucceededDegreeOne", () => {
        const expected = helper.expectedCriticalSucceededDegreeOne({ mode });
        assert.equal(result.total, expected.total);
        assert.equal(result.succeeded, expected.succeeded);
        assert.equal(result.degree, expected.degree);
      });
    });

    scenario("routine check treats die as ten", ({ given, when, then }: any) => {
      let bundle: any;
      let result: any;

      given("a Check from helper.givenRoutineStrengthCheck", () => {
        bundle = helper.givenRoutineStrengthCheck({ mode });
      });

      when("the Player resolves that Check as routine", () => {
        result = bundle.check.resolve([], true);
      });

      then("Check die_roll equals ten", () => {
        assert.equal(bundle.check.dieRoll ?? result.dieFace, 10);
      });

      then("And CheckResult matches helper.expectedRoutineSucceededDegreeTwo", () => {
        const expected = helper.expectedRoutineSucceededDegreeTwo({ mode });
        assert.equal(result.total, expected.total);
        assert.equal(result.succeeded, expected.succeeded);
        assert.equal(result.degree, expected.degree);
      });
    });
  });
}

// Node test entry
if (typeof process !== "undefined" && process.versions?.node) {
  const [{ fileURLToPath }, { default: path }] = await Promise.all([
    import("node:url"),
    import("node:path"),
  ]);
  const thisFile = fileURLToPath(import.meta.url);
  const entry = process.argv[1] && path.resolve(process.argv[1]);
  if (entry && path.resolve(thisFile) === entry) {
    resolveAbilityCheckStory("fake");
  }
}
