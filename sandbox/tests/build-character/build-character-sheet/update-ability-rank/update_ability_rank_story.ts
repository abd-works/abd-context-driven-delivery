/**
 * # @toolset-manifest python -m tools manifest context_tools.stories.stories:Stories
 * Story: Update Ability Rank (tier-neutral).
 */

import { BuildCharacterHelper } from "../../build-character-helper.js";
import { assert, scenario, story } from "../../../story-test.js";

const helper = new BuildCharacterHelper();

export function updateAbilityRankStory(mode: string): void {
  story("Update Ability Rank", () => {
    scenario("ability rank changes on the sheet", ({ given, when, then, expose }: any) => {
      let character: any;
      let ability: any;
      let expected: any;

      given("a Character from handbook sheet at rank zero", () => {
        character = helper.givenHandbookSheetAtRankZero({ mode }).character;
        ability = character.abilities.strength;
        expected = helper.givenStrengthAtRankFive({ mode });
      });

      when("the Player updates that Ability rank to five", () => {
        ability.rank = expected.rank;
      });

      then("that Ability rank matches strength at rank five from the example", () => {
        assert.equal(ability.rank, expected.rank);
        assert.equal(ability.rank, expected.ability.rank);
      });

      expose(() => ({ character, ability, expected }));
    });

    scenario("ability rank can drop below zero", ({ given, when, then, expose }: any) => {
      let character: any;
      let ability: any;
      let expected: any;

      given("a Character from handbook sheet at rank zero", () => {
        character = helper.givenHandbookSheetAtRankZero({ mode }).character;
        ability = character.abilities.strength;
        expected = helper.givenStrengthAtRankNegOne({ mode });
      });

      when("the Player updates that Ability rank to negative one", () => {
        ability.rank = expected.rank;
      });

      then("that Ability rank matches strength at rank neg one from the example", () => {
        assert.equal(ability.rank, expected.rank);
        assert.equal(ability.rank, expected.ability.rank);
      });

      then("And that Ability is not debilitated", () => {
        assert.equal(ability.debilitated, expected.ability.debilitated);
        assert.equal(ability.debilitated, false);
      });

      expose(() => ({ character, ability, expected }));
    });

    scenario("ability becomes debilitated below negative five", ({ given, when, then, expose }: any) => {
      let character: any;
      let ability: any;
      let expected: any;

      given("a Character with strength at rank negative five", () => {
        character = helper.givenHandbookSheetAtRankZero({ mode }).character;
        ability = character.abilities.strength;
        ability.rank = -5;
        expected = helper.givenStrengthDebilitated({ mode });
      });

      when("the Player updates that Ability rank to negative six", () => {
        ability.rank = expected.rank;
      });

      then("that Ability rank matches strength debilitated from the example", () => {
        assert.equal(ability.rank, expected.rank);
        assert.equal(ability.rank, expected.ability.rank);
      });

      then("And that Ability is debilitated", () => {
        assert.equal(ability.debilitated, expected.ability.debilitated);
        assert.equal(ability.debilitated, true);
      });

      expose(() => ({ character, ability, expected }));
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
    updateAbilityRankStory("fake");
  }
}
