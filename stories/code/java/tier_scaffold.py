"""Java tier scaffolder — emits ONE write-once file per (story, tier).

For each Story with attached scenarios, emits:

    <story-slug>/
        <StoryPascalCase><TierPascalCase>Tier.java   — implements TierImpl,
            wires every scenario through StoryRunner.runScenario()

WRITE-ONCE POLICY: same as the TS/PY scaffolders — any path already present
in `existing_tree` is skipped. Hand-authored implementations are never
overwritten.

Java package is derived the same way as tree.py:
  `<tests-root>.<epic-snake>.<sub-epic-snake>.<story-snake>`
"""

from __future__ import annotations

import re
from typing import Dict, List, Sequence

from stories.code.java.spec_file import _pascal, _camel
from stories.story_model.nodes import Epic, Story, SubEpic
from stories.story_model.story_map import StoryMap


def scaffold_java_tier_tree(
    story_map: StoryMap,
    tiers: Sequence[str],
    *,
    tests_root: str = "tests",
    existing_tree: Dict[str, str] | None = None,
) -> Dict[str, str]:
    """Return `{path: content}` for every tier file that should be scaffolded.

    Files already present in `existing_tree` are skipped (write-once).
    """
    existing = existing_tree or {}
    tree: Dict[str, str] = {}
    root = tests_root.strip("/") or "tests"

    for epic in getattr(story_map, "epics", []) or []:
        _scaffold_epic(
            epic,
            tiers=tiers,
            root=root,
            tree=tree,
            existing=existing,
        )

    return {path: body for path, body in tree.items() if path not in existing}


def _scaffold_epic(
    epic: Epic,
    *,
    tiers: Sequence[str],
    root: str,
    tree: Dict[str, str],
    existing: Dict[str, str],
) -> None:
    epic_slug = _snake(epic.name)
    for sub in getattr(epic, "sub_epics", []) or []:
        _scaffold_sub_epic(
            sub,
            tiers=tiers,
            package_parts=[root, epic_slug],
            parent=f"{root}/{epic_slug}",
            tree=tree,
            existing=existing,
        )


def _scaffold_sub_epic(
    sub: SubEpic,
    *,
    tiers: Sequence[str],
    package_parts: List[str],
    parent: str,
    tree: Dict[str, str],
    existing: Dict[str, str],
) -> None:
    sub_slug = _snake(sub.name)
    folder = f"{parent}/{sub_slug}"
    new_pkg = package_parts + [sub_slug]
    for nested in getattr(sub, "sub_epics", []) or []:
        _scaffold_sub_epic(
            nested,
            tiers=tiers,
            package_parts=new_pkg,
            parent=folder,
            tree=tree,
            existing=existing,
        )
    for story in getattr(sub, "stories", []) or []:
        if not getattr(story, "scenarios", None):
            continue
        story_slug = _snake(story.name)
        story_folder = f"{folder}/{story_slug}"
        pkg = new_pkg + [story_slug]
        for tier in tiers:
            _scaffold_tier_file(
                story,
                tier=tier,
                package_parts=pkg,
                story_folder=story_folder,
                tree=tree,
            )


def _scaffold_tier_file(
    story: Story,
    *,
    tier: str,
    package_parts: List[str],
    story_folder: str,
    tree: Dict[str, str],
) -> None:
    story_pascal = _pascal(story.name)
    tier_pascal = _pascal(tier)
    class_name = f"{story_pascal}{tier_pascal}Tier"
    file_path = f"{story_folder}/{class_name}.java"
    pkg = ".".join(package_parts)
    stories_class = f"{story_pascal}Stories"
    scenarios = list(getattr(story, "scenarios", []) or [])

    lines: List[str] = [
        f"package {pkg};",
        "",
        f"import {pkg.rsplit('.', 1)[0]}.{stories_class};",
        "import stories.StoryRunner;",
        "import stories.StoryTypes.TierImpl;",
        "import stories.StoryTypes.Scenario;",
        "import java.util.List;",
        "import java.util.Map;",
        "import org.junit.jupiter.api.DynamicTest;",
        "import org.junit.jupiter.api.TestFactory;",
        "",
        f"class {class_name} implements TierImpl {{",
        "",
        "    @Override",
        "    public Map<String, Runnable> given() {",
        "        return Map.of(",
        "            // TODO: implement given steps",
        "        );",
        "    }",
        "",
        "    @Override",
        "    public Map<String, Runnable> when() {",
        "        return Map.of(",
        "            // TODO: implement when steps",
        "        );",
        "    }",
        "",
        "    @Override",
        "    public Map<String, Runnable> then() {",
        "        return Map.of(",
        "            // TODO: implement then steps",
        "        );",
        "    }",
        "",
        "    @Override",
        "    public void cleanup() {}",
        "",
    ]

    for scenario in scenarios:
        method_name = _camel(scenario.name)
        lines.append("    @TestFactory")
        lines.append(
            f"    List<DynamicTest> {method_name}() {{"
        )
        lines.append(
            f"        Scenario scenario = {stories_class}.STORY.scenarios()"
            f".get(\"{_camel(scenario.name)}\");"
        )
        lines.append(
            f"        return StoryRunner.runScenario("
            f"\"{story.name}\", scenario, {class_name}::new);"
        )
        lines.append("    }")
        lines.append("")

    lines.append("}")
    lines.append("")
    tree[file_path] = "\n".join(lines)


def _snake(name: str) -> str:
    words = [w for w in re.split(r"[^0-9A-Za-z]+", name) if w]
    return "_".join(w.lower() for w in words) or "stories"
