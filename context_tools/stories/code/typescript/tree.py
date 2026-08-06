"""TypeScript tree - `*_story.ts` per Story folder."""

from __future__ import annotations

from pathlib import Path
from typing import Dict

from context_tools.stories.code.code_story_map import to_kebab, to_pascal, to_snake
from context_tools.stories.code.example_factories import collect_example_factories
from context_tools.stories.code.typescript.story_file import render_story_file
from context_tools.stories.story_model.nodes import Epic, Story, SubEpic
from context_tools.stories.story_model.story_map import StoryMap

TEMPLATES_DIR = Path(__file__).resolve().parent / "seeds"


def render_ts_tree(
    story_map: StoryMap, *, tests_root: str = "tests", include_shared: bool = True
) -> Dict[str, str]:
    tree: Dict[str, str] = {}
    root = tests_root.strip("/") or "tests"
    if include_shared:
        test_path = TEMPLATES_DIR / "story-test.ts"
        if test_path.exists():
            tree[f"{root}/story-test.ts"] = test_path.read_text(encoding="utf-8")
        else:
            tree[f"{root}/story-test.ts"] = _default_story_test()
    for epic in getattr(story_map, "epics", []) or []:
        _render_epic(epic, root=root, tree=tree)
    return tree


def _render_epic(epic: Epic, *, root: str, tree: Dict[str, str]) -> None:
    epic_slug = to_kebab(epic.name)
    tree[f"{root}/{epic_slug}/{epic_slug}-helper.ts"] = _helper(epic)
    for sub in getattr(epic, "sub_epics", []) or []:
        _render_sub_epic(sub, parent=f"{root}/{epic_slug}", depth=2, tree=tree, epic=epic)


def _helper(epic: Epic) -> str:
    factories = collect_example_factories(epic)
    helper_class = f"{to_pascal(epic.name)}Helper"
    lines = [
        "/** Epic helper - ExampleFactory accessors; AI fills given_* bodies. */",
        "",
    ]
    if factories:
        lines.append(
            f"import {{ {', '.join(factories)} }} from '../example-factories';"
        )
        lines.append("")
    lines.append(f"export class {helper_class} {{")
    lines.append(
        "  // Shared ExampleFactory accessors. Tier test-helpers import this to build real collaborators."
    )
    for name in factories:
        method = name[0].lower() + name[1:]
        lines.append(f"  {method}() {{ return new {name}(); }}")
    if not factories:
        lines.append(f"  // No example_factories on epic {epic.name!r}")
    lines.append("}")
    lines.append("")
    return "\n".join(lines)


def _render_sub_epic(
    sub: SubEpic, *, parent: str, depth: int, tree: Dict[str, str], epic: Epic
) -> None:
    folder = f"{parent}/{to_kebab(sub.name)}"
    for nested in getattr(sub, "sub_epics", []) or []:
        _render_sub_epic(nested, parent=folder, depth=depth + 1, tree=tree, epic=epic)
    for story in getattr(sub, "stories", []) or []:
        if not story.scenarios:
            continue
        story_folder = f"{folder}/{to_kebab(story.name)}"
        relative_test = "../" * depth + "story-test"
        tree[f"{story_folder}/{to_snake(story.name)}_story.ts"] = render_story_file(
            story,
            relative_story_test_path=relative_test,
        )


def _default_story_test() -> str:
    return (
        "export function story(name: string, build: () => void): void {\n"
        "  describe(name, build);\n"
        "}\n\n"
        "export function scenario(\n"
        "  name: string,\n"
        "  build: (steps: {\n"
        "    given: (s: string, fn: () => void) => void;\n"
        "    when: (s: string, fn: () => void) => void;\n"
        "    then: (s: string, fn: () => void) => void;\n"
        "  }) => void,\n"
        "): void {\n"
        "  describe(name, () => {\n"
        "    const givens: Array<() => void> = [];\n"
        "    const whens: Array<() => void> = [];\n"
        "    const thens: Array<{ step: string; fn: () => void }> = [];\n"
        "    build({\n"
        "      given: (_s, fn) => givens.push(fn),\n"
        "      when: (_s, fn) => whens.push(fn),\n"
        "      then: (s, fn) => thens.push({ step: s, fn }),\n"
        "    });\n"
        "    beforeAll(() => {\n"
        "      for (const g of givens) g();\n"
        "      for (const w of whens) w();\n"
        "    });\n"
        "    thens.forEach(({ step, fn }, i) => {\n"
        "      it(i === 0 ? `Then ${step}` : step, fn);\n"
        "    });\n"
        "  });\n"
        "}\n"
    )
