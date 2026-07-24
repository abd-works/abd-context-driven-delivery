"""JavaScript tier-spec renderer (engineering).

Thin file that re-runs the shared story function at a given mode:

    import { describe } from "node:test";
    import { createSubmitOrderStory } from "./submit_order_story.js";

    describe("tier: isolated", () => {
      createSubmitOrderStory("isolated");
    });
"""

from __future__ import annotations

import re

from context_tools.stories.code.code_story_map import to_pascal
from context_tools.stories.story_model.nodes import Story


def render_tier_spec_file(story: Story, *, tier: str) -> str:
    fn = f"create{to_pascal(story.name)}Story"
    story_module = f"./{_snake(story.name)}_story.js"

    lines = [
        "/**",
        f" * Tier: {tier} — same {story.name} story,",
        " * ExampleFactory builds types with injected deps (isolated) or real collaborators (production).",
        " */",
        "",
        'import { describe } from "node:test";',
        f'import {{ {fn} }} from "{story_module}";',
        "",
        f'describe("tier: {tier}", () => {{',
        f'  {fn}("{tier}");',
        "});",
        "",
    ]
    return "\n".join(lines)


# Back-compat alias — old pure-data renderer callers
def render_story_spec_file(story: Story, *, relative_types_path: str = "../story-types") -> str:
    """Deprecated: explore/spec use story_file.render_story_file."""
    from context_tools.stories.code.javascript.story_file import render_story_file

    return render_story_file(story)


def _snake(name: str) -> str:
    return re.sub(r"[^0-9a-z]+", "_", name.strip().lower()).strip("_") or "story"
