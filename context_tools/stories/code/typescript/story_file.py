"""TypeScript runnable story-file renderer (scenario fidelity - no tier suffix).

Emits a Given/When/Then wiring that calls a helper-interface method per step -
the story file owns no assertions and no tier mechanism itself:

    export interface SubmitOrderHelper {
      givenACartWithItems(): void | Promise<void>;
      whenTheCustomerSubmitsTheOrder(): void | Promise<void>;
      thenTheOrderIsConfirmed(): void | Promise<void>;
    }

    export function createSubmitOrderStory(h: SubmitOrderHelper): void {
      story("Submit Order", () => {
        scenario("...", ({ given, when, then }) => {
          given("a cart with items", () => h.givenACartWithItems());
          when("the customer submits the order", () => h.whenTheCustomerSubmitsTheOrder());
          then("the order is confirmed", () => h.thenTheOrderIsConfirmed());
        });
      });
    }

Every tier's `{story}_test_helper.{tier}.ts` implements `SubmitOrderHelper` with
that tier's real mechanism and calls `createSubmitOrderStory(new TierHelper())`.
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
    relative_story_test_path: str = "../../story-test",
) -> str:
    fn = f"create{to_pascal(story.name)}Story"
    helper_iface = f"{to_pascal(story.name)}Helper"
    actor = (story.users[0] if story.users else "").strip()
    methods, method_for = build_helper_seam(story)

    lines: List[str] = [
        "/**",
        f" * Story: {story.name}",
    ]
    if actor:
        lines.append(f" * Actor: {actor}")
    lines.extend(
        [
            " * Calls helper-interface methods only - no assertions, no tier mechanism here.",
            f" * Tiers: {_snake(story.name)}_test_helper.{{tier}}.ts implements {helper_iface}.",
            " */",
            "",
            f'import {{ scenario, story }} from "{relative_story_test_path}";',
            "",
            f"export interface {helper_iface} {{",
        ]
    )
    for method in methods:
        lines.append(f"  {method.name}(): void | Promise<void>;")
    lines.append("}")
    lines.append("")
    lines.append(f"export function {fn}(h: {helper_iface}): void {{")
    lines.append(f"  story({_ts_string(story.name)}, () => {{")

    scenarios = list(getattr(story, "scenarios", []) or [])
    if not scenarios:
        lines.append("    // TODO: add main-flow scenario")
    for scenario_ in scenarios:
        lines.extend(_render_scenario(scenario_, method_for))

    lines.append("  });")
    lines.append("}")
    lines.append("")
    return "\n".join(lines)


def _render_scenario(scenario, method_for) -> List[str]:
    lines = [f"    scenario({_ts_string(scenario.name)}, ({{ given, when, then }}) => {{"]
    for clause in scenario.given:
        method = method_for("given", clause.text)
        lines.append(
            f"      given({_ts_string(method.display_text)}, () => h.{method.name}());"
        )
    for interaction in scenario.interactions:
        for clause in interaction.when:
            method = method_for("when", clause.text)
            lines.append(
                f"      when({_ts_string(method.display_text)}, () => h.{method.name}());"
            )
        for clause in interaction.then:
            method = method_for("then", clause.text)
            lines.append(
                f"      then({_ts_string(method.display_text)}, () => h.{method.name}());"
            )
    lines.append("    });")
    lines.append("")
    return lines


def render_test_helper_file(
    story: Story, *, tier: str, same_file: bool = False
) -> str:
    """Seam helper for `{story}.{tier}.ts`."""
    fn = f"create{to_pascal(story.name)}Story"
    helper_iface = f"{to_pascal(story.name)}Helper"
    tier_class = f"{to_pascal(tier)}Helper"
    methods, _ = build_helper_seam(story)

    lines: List[str] = [
        "/**",
        f" * Tier: {tier} - implements {helper_iface} for {story.name}.",
        " */",
        "",
        'import { describe } from "vitest";',
    ]
    if not same_file:
        lines.append(
            f'import {{ {fn}, type {helper_iface} }} from "./{_snake(story.name)}_story";'
        )
        lines.append("")
    lines.append(f"class {tier_class} implements {helper_iface} {{")
    for method in methods:
        lines.append(f"  {method.name}(): void | Promise<void> {{")
        lines.append(f'    throw new Error("not implemented: {method.name}");')
        lines.append("  }")
    lines.append("}")
    lines.append("")
    lines.append(f'describe("tier: {tier}", () => {{')
    lines.append(f"  {fn}(new {tier_class}());")
    lines.append("});")
    lines.append("")
    return "\n".join(lines)


_BOLD = re.compile(r"\*\*([^*]+)\*\*")
_ITALIC = re.compile(r"(?<!\*)\*([^*\n]+)\*(?!\*)")
_BACKTICK = re.compile(r"`([^`]+)`")


def _strip_md_emphasis(value: str) -> str:
    return _BACKTICK.sub(r"\1", _ITALIC.sub(r"\1", _BOLD.sub(r"\1", value)))


def _ts_string(value: str) -> str:
    cleaned = _strip_md_emphasis(value)
    escaped = cleaned.replace("\\", "\\\\").replace("'", "\\'")
    return f"'{escaped}'"


def _snake(name: str) -> str:
    return re.sub(r"[^0-9a-z]+", "_", name.strip().lower()).strip("_") or "story"
