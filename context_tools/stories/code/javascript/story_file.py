"""JavaScript runnable story-file renderer (explore / specification).

Emits Given / When / Then against factory fakes — not pure data.

    export function createSubmitOrderStory(mode) {
      story("Submit Order", () => {
        scenario("…", ({ given, when, then }) => {
          given("…", () => { /* helper → ExampleFactory fake */ });
          when("…", () => { /* public operations */ });
          then("…", () => { /* assert public interface of I{Type} */ });
        });
      });
    }

    // fake only when this file is the test entry
    if (entry && path.resolve(thisFile) === entry) {
      createSubmitOrderStory("fake");
    }
"""

from __future__ import annotations

import re
from typing import List

from context_tools.stories.code.code_story_map import to_pascal
from context_tools.stories.story_model.nodes import Story


def render_story_file(
    story: Story,
    *,
    relative_story_test_path: str = "../../story-test.js",
    relative_helper_path: str | None = None,
    helper_class: str | None = None,
) -> str:
    fn = f"create{to_pascal(story.name)}Story"
    actor = (story.users[0] if story.users else "").strip()

    lines: List[str] = []
    lines.append("/**")
    lines.append(f" * Story: {story.name} (tier-neutral).")
    if actor:
        lines.append(f" * Actor: {actor}")
    lines.append(" * Wired to ExampleFactory fakes — not a tier test.")
    lines.append(" * Assert the public interface of I{Type} only.")
    lines.append(" *")
    lines.append(
        f" * Specs: {_snake(story.name)}_spec.js (isolated); "
        f"{_snake(story.name)}_spec.{{tier}}.js (other tiers)"
    )
    lines.append(" */")
    lines.append("")
    lines.append('import assert from "node:assert/strict";')
    lines.append('import path from "node:path";')
    lines.append('import { fileURLToPath } from "node:url";')
    if relative_helper_path and helper_class:
        lines.append(f'import {{ {helper_class} }} from "{relative_helper_path}";')
    lines.append(f'import {{ scenario, story }} from "{relative_story_test_path}";')
    lines.append("")
    if relative_helper_path and helper_class:
        lines.append(f"const helper = new {helper_class}();")
        lines.append("")
    lines.append(f"export function {fn}(mode) {{")
    lines.append(f'  story({_js_string(story.name)}, () => {{')

    scenarios = list(getattr(story, "scenarios", []) or [])
    if not scenarios:
        lines.append('    // TODO: add main-flow scenario')
    for scenario in scenarios:
        lines.extend(_render_scenario(scenario))

    lines.append("  });")
    lines.append("}")
    lines.append("")
    lines.append(
        "// Story path — fake only when this file is the test entry (not when a tier imports it)"
    )
    lines.append("const thisFile = fileURLToPath(import.meta.url);")
    lines.append("const entry = process.argv[1] && path.resolve(process.argv[1]);")
    lines.append("if (entry && path.resolve(thisFile) === entry) {")
    lines.append(f'  {fn}("fake");')
    lines.append("}")
    lines.append("")
    return "\n".join(lines)


def _render_scenario(scenario) -> List[str]:
    lines: List[str] = []
    lines.append(f'    scenario({_js_string(scenario.name)}, ({{ given, when, then }}) => {{')

    for clause in scenario.given:
        lines.append(f'      given({_js_string(clause.text)}, () => {{')
        lines.append(
            "        // helper.given…({ mode }) — fake I{Type} from ExampleFactory"
        )
        lines.append("      });")
        lines.append("")

    for interaction in scenario.interactions:
        for clause in interaction.when:
            lines.append(f'      when({_js_string(clause.text)}, () => {{')
            lines.append("        // exercise public operations on I{Type}")
            lines.append("      });")
            lines.append("")
        for clause in interaction.then:
            lines.append(f'      then({_js_string(clause.text)}, () => {{')
            lines.append(
                "        // assert.equal / assert.ok on public interface only"
            )
            lines.append("        assert.ok(true); // replace with public-seam assertion")
            lines.append("      });")
            lines.append("")

    lines.append("    });")
    lines.append("")
    return lines


_BOLD = re.compile(r"\*\*([^*]+)\*\*")
_ITALIC = re.compile(r"(?<!\*)\*([^*\n]+)\*(?!\*)")
_BACKTICK = re.compile(r"`([^`]+)`")


def _strip_md_emphasis(value: str) -> str:
    return _BACKTICK.sub(r"\1", _ITALIC.sub(r"\1", _BOLD.sub(r"\1", value)))


def _js_string(value: str) -> str:
    cleaned = _strip_md_emphasis(value)
    escaped = cleaned.replace("\\", "\\\\").replace("'", "\\'")
    return f"'{escaped}'"


def _snake(name: str) -> str:
    return re.sub(r"[^0-9a-z]+", "_", name.strip().lower()).strip("_") or "story"
