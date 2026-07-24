/**
 * # @toolset-manifest python -m tools manifest context_tools.stories.stories:Stories
 * # Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
 * # invoke-edit: action satisfy | toolset: context_tools.stories.stories:Stories
 * # invoke-check: action validate | toolset: context_tools.stories.stories:Stories
 *
 * Story: Create Character (tier-neutral) — browser-safe export for Story Demo Play.
 * Wired to ExampleFactory fakes — not a tier test.
 *
 * Run (node):  node --test sandbox/play-core-mechanics/manage-character-sheet/create-character/create_character_story.js
 * Specs: create_character_spec.js (isolated); create_character_spec.{tier}.js (other tiers)
 */

import { ManageCharacterSheetHelper } from "../manage-character-sheet-helper.js";
import { assert } from "../../../../context_tools/ux/story-demo/play-dual-runner/soft-assert.js";
import { scenario, story } from "../../../../context_tools/ux/story-demo/play-dual-runner/story-test-core.js";

const helper = new ManageCharacterSheetHelper();

/**
 * Shared scenarios. Story file runs with mode "fake".
 * Tier specs call this with "isolated" | "production".
 * Browser / Play: PlayDualRunner.collect(createCharacterStory, mode).
 */
export function createCharacterStory(mode) {
  story("Create Character", () => {
    scenario("new character has handbook abilities at rank zero", ({ given, when, then, expose }) => {
      let character;
      let bundle;

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

    scenario("new character exposes all eight named abilities", ({ given, when, then, expose }) => {
      let character;
      let bundle;

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

    scenario("new character initiative matches agility rank", ({ given, when, then, expose }) => {
      let character;
      let bundle;

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

// Node test entry — register backend then run (skipped in browser)
if (typeof process !== "undefined" && process.versions?.node) {
  const [{ fileURLToPath }, { default: path }] = await Promise.all([
    import("node:url"),
    import("node:path"),
  ]);
  await import("../../../../context_tools/ux/story-demo/play-dual-runner/story-test-node.js");
  const thisFile = fileURLToPath(import.meta.url);
  const entry = process.argv[1] && path.resolve(process.argv[1]);
  if (entry && path.resolve(thisFile) === entry) {
    createCharacterStory("fake");
  }
}
