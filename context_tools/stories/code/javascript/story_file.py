"""JavaScript runnable story-file renderer (scenario fidelity - no tier suffix).

Emits a Given/When/Then wiring that calls a helper-object method per step -
the story file owns no assertions and no tier mechanism itself. JavaScript has
no static interfaces, so the seam is documented via a JSDoc `@typedef` and
enforced only by duck-typing:

    /**
     * @typedef {object} SubmitOrderHelper
     * @property {function(): (void|Promise<void>)} givenACartWithItems
     * @property {function(): (void|Promise<void>)} whenTheCustomerSubmitsTheOrder
     * @property {function(): (void|Promise<void>)} thenTheOrderIsConfirmed
     */

    /** @param {SubmitOrderHelper} h */
    export function createSubmitOrderStory(h) {
      story("Submit Order", () => {
        scenario("...", ({ given, when, then }) => {
          given("a cart with items", () => h.givenACartWithItems());
          when("the customer submits the order", () => h.whenTheCustomerSubmitsTheOrder());
          then("the order is confirmed", () => h.thenTheOrderIsConfirmed());
        });
      });
    }

Every tier's `{story}_test_helper.{tier}.js` implements the same method names
on a plain class and calls `createSubmitOrderStory(new TierHelper())`.
"""

from __future__ import annotations

import re
from typing import List

from context_tools.stories.code.code_story_map import to_pascal
from context_tools.stories.code.helper_interface import build_helper_seam
from context_tools.stories.story_model.nodes import Story


def render_story_file(
    story: Story,
    *,
    relative_story_test_path: str = "../../story-test.js",
) -> str:
    fn = f"create{to_pascal(story.name)}Story"
    helper_iface = f"{to_pascal(story.name)}Helper"
    actor = (story.users[0] if story.users else "").strip()
    methods, method_for = build_helper_seam(story)

    lines: List[str] = []
    lines.append("/**")
    lines.append(f" * Story: {story.name} (scenario fidelity - tier-neutral).")
    if actor:
        lines.append(f" * Actor: {actor}")
    lines.append(" * Calls helper-object methods only - no assertions, no tier mechanism here.")
    lines.append(
        f" * Tiers: {_snake(story.name)}_test_helper.{{tier}}.js implements {helper_iface}."
    )
    lines.append(" *")
    lines.append(f" * @typedef {{object}} {helper_iface}")
    for method in methods:
        lines.append(f" * @property {{function(): (void|Promise<void>)}} {method.name}")
    lines.append(" */")
    lines.append("")
    lines.append(f'import {{ scenario, story }} from "{relative_story_test_path}";')
    lines.append("")
    lines.append(f"/** @param {{{helper_iface}}} h */")
    lines.append(f"export function {fn}(h) {{")
    lines.append(f'  story({_js_string(story.name)}, () => {{')

    scenarios = list(getattr(story, "scenarios", []) or [])
    if not scenarios:
        lines.append("    // TODO: add main-flow scenario")
    for scenario_ in scenarios:
        lines.extend(_render_scenario(scenario_, method_for))

    lines.append("  });")
    lines.append("}")
    lines.append("")
    return "\n".join(lines)


def render_test_helper_file(story: Story, *, tier: str) -> str:
    """Write-once skeleton for `{story}_test_helper.{tier}.js`.

    Scaffolds a plain class with `not implemented` stub methods (code path).
    The AI/human path fills each stub with that tier's real mechanism.
    """
    fn = f"create{to_pascal(story.name)}Story"
    tier_class = f"{to_pascal(tier)}Helper"
    methods, _ = build_helper_seam(story)

    lines: List[str] = [
        "/**",
        f" * Tier: {tier} - implements {to_pascal(story.name)}Helper for {story.name}.",
        " */",
        "",
        'import { describe } from "node:test";',
        f'import {{ {fn} }} from "./{_snake(story.name)}_story.js";',
        "",
        f"class {tier_class} {{",
    ]
    for method in methods:
        lines.append(f"  {method.name}() {{")
        lines.append(f'    throw new Error("not implemented: {method.name}");')
        lines.append("  }")
    lines.append("}")
    lines.append("")
    lines.append(f'describe("tier: {tier}", () => {{')
    lines.append(f"  {fn}(new {tier_class}());")
    lines.append("});")
    lines.append("")
    return "\n".join(lines)


def _render_scenario(scenario, method_for) -> List[str]:
    lines: List[str] = []
    lines.append(f'    scenario({_js_string(scenario.name)}, ({{ given, when, then }}) => {{')
    for clause in scenario.given:
        method = method_for("given", clause.text)
        lines.append(
            f'      given({_js_string(method.display_text)}, () => h.{method.name}());'
        )
    for interaction in scenario.interactions:
        for clause in interaction.when:
            method = method_for("when", clause.text)
            lines.append(
                f'      when({_js_string(method.display_text)}, () => h.{method.name}());'
            )
        for clause in interaction.then:
            method = method_for("then", clause.text)
            lines.append(
                f'      then({_js_string(method.display_text)}, () => h.{method.name}());'
            )
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
