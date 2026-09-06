"""JavaStoryMap — renders each leaf SubEpic to a `<SubEpicPascalCase>Test.java` file
of JUnit 5 tests matching the abd-story-acceptance-test Java template.
"""

from __future__ import annotations

import re
from typing import List

from src.core.stories.nodes import AcceptanceCriteria, Epic, Story, SubEpic
from src.formats.code.code_story_map import (
    CodeStoryMap,
    to_camel,
    to_kebab,
    to_pascal,
    to_snake,
)


class JavaStoryMap(CodeStoryMap):
    LEAF_EXTENSION = "Test.java"
    LANGUAGE_LINE_COMMENT = "//"

    def _leaf_file_name(self, sub_epic: SubEpic) -> str:
        return f"{to_pascal(sub_epic.name)}{self.LEAF_EXTENSION}"

    def _render_sub_epic(
        self,
        sub_epic: SubEpic,
        sibling_sub_epics: List[SubEpic],
        parent_path: str,
        owning_epic: Epic,
        tree,
        previous_tree,
    ) -> None:
        # WHY: Java requires PascalCase filenames instead of the shared kebab-slug.
        folder = f"{parent_path}/{self._folder_slug(sub_epic, sibling_sub_epics)}"
        if sub_epic.sub_epics:
            for nested in sub_epic.sub_epics:
                self._render_sub_epic(
                    nested,
                    sub_epic.sub_epics,
                    folder,
                    owning_epic,
                    tree,
                    previous_tree,
                )
        if sub_epic.stories or not sub_epic.sub_epics:
            leaf_path = f"{folder}/{self._leaf_file_name(sub_epic)}"
            generated = self._render_leaf_file(sub_epic, owning_epic)
            previous = previous_tree.get(leaf_path)
            if previous is not None:
                generated = self._preserve_hand_written(previous, generated)
            tree[leaf_path] = generated

    def _render_leaf_file(self, sub_epic: SubEpic, owning_epic: Epic) -> str:
        class_name = f"{to_pascal(sub_epic.name)}Test"
        package_parts = [
            to_snake(self.tests_root),
            to_snake(owning_epic.name),
            to_snake(sub_epic.name),
        ]
        package = ".".join(package_parts)
        lines: List[str] = [
            f"package {package};",
            "",
            "import org.junit.jupiter.api.Test;",
            "import org.junit.jupiter.api.DisplayName;",
            "import org.junit.jupiter.api.Nested;",
            "import org.junit.jupiter.api.BeforeEach;",
            "import org.junit.jupiter.api.AfterEach;",
            "import static org.junit.jupiter.api.Assertions.*;",
            "",
            f'@DisplayName("{sub_epic.name}")',
            f"class {class_name} {{",
        ]
        helper_bodies = self._helper_stubs(sub_epic)
        for helper in helper_bodies:
            lines.append(f"    {helper}")
        for story in sub_epic.stories:
            lines.extend(self._render_story_class(story))
        lines.append("}")
        return "\n".join(lines) + "\n"

    def _helper_stubs(self, sub_epic: SubEpic) -> List[str]:
        stubs: List[str] = []
        seen: set = set()
        for story in sub_epic.stories:
            for ac in story.acceptance_criteria:
                slug = to_camel(ac.text or ac.name)
                for prefix in ("given", "when", "then"):
                    method = f"{prefix}{to_pascal(ac.text or ac.name)}"
                    if method in seen:
                        continue
                    seen.add(method)
                    stubs.append(f"private static void {method}() {{ /* helper */ }}")
        return stubs

    def _render_story_class(self, story: Story) -> List[str]:
        story_class = f"{to_pascal(story.name)}Tests"
        lines: List[str] = [
            "",
            "    @Nested",
            f'    @DisplayName("{story.name}")',
            f"    class {story_class} {{",
        ]
        for ac in story.acceptance_criteria:
            method_name = f"{to_camel(ac.text or ac.name)}"
            lines.append("")
            lines.append("        @Test")
            lines.append(f'        @DisplayName("{ac.name}")')
            lines.append(f"        void {method_name}() {{")
            lines.append(f"            // Given")
            lines.append(f"            {to_camel('given ' + (ac.text or ac.name))}();")
            lines.append(f"            // When")
            lines.append(f"            {to_camel('when ' + (ac.text or ac.name))}();")
            lines.append(f"            // Then")
            lines.append(f"            {to_camel('then ' + (ac.text or ac.name))}();")
            lines.append("        }")
        lines.append("    }")
        return lines

    def _hydrate_leaf_sub_epic_from_content(
        self, current_sub_epic: SubEpic, file_name: str, content: str
    ) -> None:
        if not file_name.endswith(self.LEAF_EXTENSION):
            return
        if current_sub_epic.stories:
            return

        lines = content.splitlines()
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line != "@Nested":
                i += 1
                continue

            story_name = ""
            j = i + 1
            while j < len(lines):
                display_match = re.match(r'@DisplayName\("(.+)"\)', lines[j].strip())
                class_match = re.search(r"class\s+\w+Tests\s*\{", lines[j])
                if display_match:
                    story_name = display_match.group(1).strip()
                if class_match:
                    break
                j += 1
            if j >= len(lines):
                break

            if not story_name:
                story_name = current_sub_epic.name
            story = Story(story_name, len(current_sub_epic.stories) + 1)

            brace_depth = lines[j].count("{") - lines[j].count("}")
            k = j + 1
            pending_display: str | None = None
            while k < len(lines) and brace_depth > 0:
                stripped = lines[k].strip()
                display_match = re.match(r'@DisplayName\("(.+)"\)', stripped)
                if display_match:
                    pending_display = display_match.group(1).strip()
                if pending_display and re.search(r"\bvoid\s+\w+\s*\(", stripped):
                    index = len(story.acceptance_criteria) + 1
                    story.acceptance_criteria.append(
                        AcceptanceCriteria(
                            name=pending_display,
                            sequential_order=index,
                            text=pending_display,
                        )
                    )
                    pending_display = None
                brace_depth += lines[k].count("{") - lines[k].count("}")
                k += 1

            current_sub_epic.stories.append(story)
            i = k
