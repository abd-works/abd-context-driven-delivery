/**
 * # @toolset-manifest python -m tools manifest context_tools.stories.stories:Stories
 * Isolated — same Update Ability Rank story.
 */

import { describe } from "node:test";
import { updateAbilityRankStory } from "./update_ability_rank_story.js";

describe("tier: isolated", () => {
  updateAbilityRankStory("isolated");
});
