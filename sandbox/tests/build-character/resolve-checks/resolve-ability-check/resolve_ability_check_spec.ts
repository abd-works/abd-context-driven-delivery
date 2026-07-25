/**
 * # @toolset-manifest python -m tools manifest context_tools.stories.stories:Stories
 * Isolated — same Resolve Ability Check story.
 */

import { describe } from "node:test";
import { resolveAbilityCheckStory } from "./resolve_ability_check_story.js";

describe("tier: isolated", () => {
  resolveAbilityCheckStory("isolated");
});
