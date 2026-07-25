/**
 * # @toolset-manifest python -m tools manifest context_tools.stories.stories:Stories
 * Story: Create Character (tier-neutral).
 */

import { BuildCharacterHelper } from "../../build-character-helper.js";
import { assert, scenario, story } from "../../../story-test.js";

const helper = new BuildCharacterHelper();

export function createCharacterStory(mode: string): void {
  story("Create Character", () => {
    scenario("new character has handbook abilities at rank zero", ({ given, when, then, expose }: any) => {
      let character: any;
      let bundle: any;

      given("no Character yet", () => {
        character = null;
        bundle = null;
      });

      when("the Player creates a Character", () => {
        bundle = helper.givenHandbookSheetAtRankZero({ mode });
        character = bundle.character;
      });

      then("a Character is present", () => {
        assert.ok(character);
      });

      then("And each of the eight Abilities has rank from the example", () => {
        assert.equal(bundle.abilityNames.length, 8);
        for (const name of bundle.abilityNames) {
          assert.equal(character.abilities[name].rank, bundle.abilityRanks[name]);
        }
      });

      expose(() => ({ character, bundle }));
    });

    scenario("new character exposes all eight named abilities", ({ given, when, then, expose }: any) => {
      let character: any;
      let bundle: any;

      given("no Character yet", () => {
        character = null;
        bundle = null;
      });

      when("the Player creates a Character", () => {
        bundle = helper.givenHandbookSheetAtRankZero({ mode });
        character = bundle.character;
      });

      then("the Character Abilities include every handbook name from the example", () => {
        assert.deepEqual(bundle.abilityNames, [
          "strength",
          "stamina",
          "agility",
          "dexterity",
          "fighting",
          "intellect",
          "awareness",
          "presence",
        ]);
        for (const name of bundle.abilityNames) {
          assert.ok(character.abilities[name]);
        }
      });

      expose(() => ({ character, bundle }));
    });

    scenario("new character initiative matches agility rank", ({ given, when, then, expose }: any) => {
      let character: any;
      let bundle: any;

      given("no Character yet", () => {
        character = null;
        bundle = null;
      });

      when("the Player creates a Character", () => {
        bundle = helper.givenHandbookSheetAtRankZero({ mode });
        character = bundle.character;
      });

      then("Character initiative equals Abilities agility rank from the example", () => {
        assert.equal(character.initiative, character.abilities.agility.rank);
        assert.equal(character.initiative, bundle.abilityRanks.agility);
      });

      then("And refreshPointTotals updates PointTotals from Abilities", () => {
        character.refreshPointTotals();
        assert.equal(character.pointTotals.total, 0);

        character.abilities.strength.rank = 2;
        character.refreshPointTotals();
        assert.equal(character.pointTotals.total, 4);
      });

      expose(() => ({ character, bundle }));
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
    createCharacterStory("fake");
  }
}
