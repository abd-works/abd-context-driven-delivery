/**
 * # @toolset-manifest python -m tools manifest contexts.stories.stories:Stories
 * # Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
 * # invoke-edit: action satisfy | toolset: contexts.stories.stories:Stories
 * # invoke-check: action validate | toolset: contexts.stories.stories:Stories
 *
 * Isolated objects — same Create Character story, ExampleFactory builds Character with injected deps.
 *
 * Run:  node --test sandbox/play-core-mechanics/manage-character-sheet/create-character/create_character_spec.js
 */

import { describe } from "node:test";
import "../../../../contexts/ux/story-demo/play-dual-runner/story-test-node.js";
import { createCharacterStory } from "./create_character_story.js";

describe("tier: isolated", () => {
  createCharacterStory("isolated");
});
