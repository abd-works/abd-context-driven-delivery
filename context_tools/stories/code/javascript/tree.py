"""JavaScript tree renderer - full file tree for a Workspace.

Story folder layout (explore / specification):

    {epic}/{sub-epic}/{story}/{story_snake}_story.js

Shared: story-types.js (legacy), story-test.js (GWT helpers).
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple

from context_tools.stories.code.code_story_map import to_kebab, to_pascal, to_snake
from context_tools.stories.code.example_factories import collect_example_factories
from context_tools.stories.code.javascript.example_factories import (
    render_js_factory_accessors,
    render_js_factory_imports,
)
from context_tools.stories.code.javascript.story_file import render_story_file
from context_tools.stories.story_model.nodes import Epic, Story, SubEpic
from context_tools.stories.story_model.story_map import StoryMap


TEMPLATES_DIR = Path(__file__).resolve().parent / "seeds"


def render_js_tree(
    story_map: StoryMap,
    *,
    tests_root: str = "tests",
    include_shared: bool = True,
) -> Dict[str, str]:
    tree: Dict[str, str] = {}
    root = tests_root.strip("/") or "tests"

    if include_shared:
        _types_body, test_body = _read_shared_templates()
        tree[f"{root}/story-test.js"] = test_body

    for epic in getattr(story_map, "epics", []) or []:
        _render_epic(epic, root=root, tree=tree)
    return tree


def _render_epic(epic: Epic, *, root: str, tree: Dict[str, str]) -> None:
    epic_slug = to_kebab(epic.name)
    helper = _render_epic_helper(epic)
    if helper is not None:
        tree[f"{root}/{epic_slug}/{epic_slug}-helper.js"] = helper
    for sub in getattr(epic, "sub_epics", []) or []:
        _render_sub_epic(
            sub,
            parent=f"{root}/{epic_slug}",
            depth=2,
            tree=tree,
            epic=epic,
        )


def _render_epic_helper(epic: Epic) -> str | None:
    """Epic helper with ExampleFactory imports when factories are declared."""
    factories = collect_example_factories(epic)
    helper_class = f"{to_pascal(epic.name)}Helper"
    lines: list[str] = []
    lines.extend(render_js_factory_imports(factories))
    lines.append(f"export class {helper_class} {{")
    lines.append(
        "  /** Shared given/when/then helpers. Call ExampleFactory methods - do not invent Fakes. */"
    )
    lines.append("  /** Shared ExampleFactory accessors. Tier test-helpers import this to build real collaborators. */")
    lines.append("")
    lines.extend(render_js_factory_accessors(factories))
    if not factories:
        lines.append(f"  // No example_factories declared on epic {epic.name!r}")
        lines.append("")
    lines.append("}")
    lines.append("")
    return "\n".join(lines)


def _render_sub_epic(
    sub: SubEpic,
    *,
    parent: str,
    depth: int,
    tree: Dict[str, str],
    epic: Epic,
) -> None:
    sub_slug = to_kebab(sub.name)
    folder = f"{parent}/{sub_slug}"
    for nested in getattr(sub, "sub_epics", []) or []:
        _render_sub_epic(
            nested, parent=folder, depth=depth + 1, tree=tree, epic=epic
        )
    for story in getattr(sub, "stories", []) or []:
        _render_story(
            story, parent=folder, depth=depth + 1, tree=tree, epic=epic
        )


def _render_story(
    story: Story,
    *,
    parent: str,
    depth: int,
    tree: Dict[str, str],
    epic: Epic,
) -> None:
    if not getattr(story, "scenarios", None):
        return
    story_slug = to_kebab(story.name)
    story_snake = to_snake(story.name)
    story_folder = f"{parent}/{story_slug}"
    relative_story_test = "../" * depth + "story-test.js"
    tree[f"{story_folder}/{story_snake}_story.js"] = render_story_file(
        story,
        relative_story_test_path=relative_story_test,
    )


def _read_shared_templates() -> Tuple[str, str]:
    types_path = TEMPLATES_DIR / "story-types.js"
    test_path = TEMPLATES_DIR / "story-test.js"
    types_body = types_path.read_text(encoding="utf-8") if types_path.exists() else ""
    if test_path.exists():
        test_body = test_path.read_text(encoding="utf-8")
    else:
        # fallback copy of sandbox GWT helpers
        test_body = (
            'import { before, describe, it } from "node:test";\n\n'
            "export function story(name, build) {\n  describe(name, build);\n}\n\n"
            "export function scenario(name, build) {\n"
            "  describe(name, () => {\n"
            "    const givens = [];\n    const whens = [];\n    const thens = [];\n"
            "    build({\n"
            "      given(step, fn) { givens.push({ step, fn }); },\n"
            "      when(step, fn) { whens.push({ step, fn }); },\n"
            "      then(step, fn) {\n"
            "        thens.push({ step, fn });\n"
            "        const chain = {\n"
            "          and(s, f) { thens.push({ step: s, fn: f }); return chain; },\n"
            "        };\n"
            "        return chain;\n"
            "      },\n"
            "    });\n"
            "    before(() => {\n"
            "      for (const g of givens) g.fn();\n"
            "      for (const w of whens) w.fn();\n"
            "    });\n"
            "    thens.forEach(({ step, fn }, i) => {\n"
            "      it(i === 0 ? `Then ${step}` : step, fn);\n"
            "    });\n"
            "  });\n}\n"
        )
    return types_body, test_body
