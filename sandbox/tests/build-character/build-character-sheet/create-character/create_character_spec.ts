/**
 * # @toolset-manifest python -m tools manifest context_tools.stories.stories:Stories
 * Isolated — same Create Character story.
 */

import { describe } from "node:test";
import { createCharacterStory } from "./create_character_story.js";

describe("tier: isolated", () => {
  createCharacterStory("isolated");
});
