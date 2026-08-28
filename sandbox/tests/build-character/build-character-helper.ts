/**
 * # @toolset-manifest python -m tools manifest context_tools.stories.stories:Stories
 * # Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
 * # invoke-edit: action satisfy | toolset: context_tools.stories.stories:Stories
 * # invoke-check: action validate | toolset: context_tools.stories.stories:Stories
 */

import { AbilityExampleFactory } from "../../src/character/ability_example_factory.js";
import { CharacterExampleFactory } from "../../src/character/character_example_factory.js";
import { CheckExampleFactory } from "../../src/checks/check_example_factory.js";
import { CheckResultExampleFactory } from "../../src/checks/check_result_example_factory.js";
import { DifficultyClassExampleFactory } from "../../src/checks/difficulty_class_example_factory.js";
import { TraitExampleFactory } from "../../src/checks/trait_example_factory.js";

type ModeOpts = { mode?: string };

/**
 * Epic helper — ExampleFactory accessors; AI fills given_* bodies.
 * Explore/spec default: mode "fake". Tiers pass isolated|production.
 */
export class BuildCharacterHelper {
  characterExampleFactory() {
    return new CharacterExampleFactory();
  }

  abilityExampleFactory() {
    return new AbilityExampleFactory();
  }

  checkExampleFactory() {
    return new CheckExampleFactory();
  }

  traitExampleFactory() {
    return new TraitExampleFactory();
  }

  difficultyClassExampleFactory() {
    return new DifficultyClassExampleFactory();
  }

  checkResultExampleFactory() {
    return new CheckResultExampleFactory();
  }

  givenHandbookSheetAtRankZero({ mode }: ModeOpts = { mode: "fake" }) {
    return this.characterExampleFactory().loadHandbookSheetAtRankZero({ mode });
  }

  givenStrengthAtRankZero({ mode }: ModeOpts = { mode: "fake" }) {
    return this.abilityExampleFactory().loadStrengthAtRankZero({ mode });
  }

  givenStrengthAtRankFive({ mode }: ModeOpts = { mode: "fake" }) {
    return this.abilityExampleFactory().loadStrengthAtRankFive({ mode });
  }

  givenStrengthAtRankNegOne({ mode }: ModeOpts = { mode: "fake" }) {
    return this.abilityExampleFactory().loadStrengthAtRankNegOne({ mode });
  }

  givenStrengthDebilitated({ mode }: ModeOpts = { mode: "fake" }) {
    return this.abilityExampleFactory().loadStrengthDebilitated({ mode });
  }

  givenStrengthCheckFaceEight({ mode }: ModeOpts = { mode: "fake" }) {
    return this.checkExampleFactory().loadStrengthCheckFaceEight({ mode });
  }

  givenStrengthCheckFailsFaceOne({ mode }: ModeOpts = { mode: "fake" }) {
    return this.checkExampleFactory().loadStrengthCheckFailsFaceOne({ mode });
  }

  givenCriticalNaturalTwentyNearMiss({ mode }: ModeOpts = { mode: "fake" }) {
    return this.checkExampleFactory().loadCriticalNaturalTwentyNearMiss({ mode });
  }

  givenRoutineStrengthCheck({ mode }: ModeOpts = { mode: "fake" }) {
    return this.checkExampleFactory().loadRoutineStrengthCheck({ mode });
  }

  givenStrengthAbilityAtRankFive({ mode }: ModeOpts = { mode: "fake" }) {
    return this.abilityExampleFactory().loadStrengthAtRankFive({ mode });
  }

  givenDifficultyTargetTen({ mode }: ModeOpts = { mode: "fake" }) {
    return this.difficultyClassExampleFactory().loadTargetTen({ mode });
  }

  expectedStrengthCheckSucceededDegreeOne({ mode }: ModeOpts = { mode: "fake" }) {
    return this.checkResultExampleFactory().loadStrengthCheckSucceededDegreeOne({ mode });
  }

  expectedStrengthCheckFailedDegreeNegOne({ mode }: ModeOpts = { mode: "fake" }) {
    return this.checkResultExampleFactory().loadStrengthCheckFailedDegreeNegOne({ mode });
  }

  expectedCriticalSucceededDegreeOne({ mode }: ModeOpts = { mode: "fake" }) {
    return this.checkResultExampleFactory().loadCriticalSucceededDegreeOne({ mode });
  }

  expectedRoutineSucceededDegreeTwo({ mode }: ModeOpts = { mode: "fake" }) {
    return this.checkResultExampleFactory().loadRoutineSucceededDegreeTwo({ mode });
  }
}
