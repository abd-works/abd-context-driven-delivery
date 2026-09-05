"""PythonStoryMap — renders each leaf SubEpic to a `<sub_epic_snake>.py` file of
pytest-shaped acceptance tests matching the abd-story-acceptance-test Python template.
"""

from __future__ import annotations

import re
from typing import List, Optional

from src.core.stories.nodes import AcceptanceCriteria, Epic, Story, SubEpic
from src.formats.code.code_story_map import CodeStoryMap, to_kebab, to_pascal, to_snake


class PythonStoryMap(CodeStoryMap):
    LEAF_EXTENSION = ".py"
    LANGUAGE_LINE_COMMENT = "#"

    def _epic_helper_path(self, epic_root: str, epic: Epic) -> str:
        return f"{epic_root}/{to_snake(epic.name)}_helper.py"

    def _render_epic_helper(self, epic: Epic) -> Optional[str]:
        helper_class = f"{to_pascal(epic.name)}Helper"
        lines = [
            "import pytest  # noqa: F401",
            "",
            f"class {helper_class}:",
            '    """Shared given/when/then helpers for every Story in this Epic."""',
            "",
        ]
        seen: set = set()
        for sub_epic in self._walk_leaf_sub_epics(epic.sub_epics):
            for story in sub_epic.stories:
                for ac in story.acceptance_criteria:
                    slug = to_snake(ac.text or ac.name)
                    for prefix in ("given", "when", "then"):
                        name = f"{prefix}_{slug}"
                        if name in seen:
                            continue
                        seen.add(name)
                        lines.append(f"    def {name}(self):")
                        lines.append(
                            f'        """Placeholder helper generated for {ac.text or ac.name!r}."""'
                        )
                        lines.append("        pass")
                        lines.append("")
        return "\n".join(lines).rstrip() + "\n"

    def _walk_leaf_sub_epics(self, siblings):
        for sub in siblings:
            if sub.sub_epics:
                yield from self._walk_leaf_sub_epics(sub.sub_epics)
            else:
                yield sub

    def _render_leaf_file(self, sub_epic: SubEpic, owning_epic: Epic) -> str:
        epic_helper = f"{to_pascal(owning_epic.name)}Helper"
        module = f"..{to_snake(owning_epic.name)}_helper"
        lines: List[str] = [
            "import pytest",
            f"from {module} import {epic_helper}",
            "",
        ]
        for story in sub_epic.stories:
            lines.extend(self._render_story_class(story, epic_helper))
            lines.append("")
        return "\n".join(lines).rstrip() + "\n"

    def _render_story_class(self, story: Story, epic_helper: str) -> List[str]:
        class_name = f"Test{to_pascal(story.name)}"
        lines = [
            f"class {class_name}({epic_helper}):",
            f'    """{story.name}"""',
        ]
        for ac in story.acceptance_criteria:
            slug = to_snake(ac.text or ac.name)
            lines.append("")
            lines.append(f"    def test_{slug}(self):")
            lines.append(f'        """')
            lines.append(f"        SCENARIO: {ac.name}")
            lines.append(f"        GIVEN: state is set up")
            lines.append(f"        WHEN: {ac.text or ac.name}")
            lines.append(f"        THEN: expected outcome")
            lines.append(f'        """')
            lines.append(f"        # Given")
            lines.append(f"        self.given_{slug}()")
            lines.append(f"        # When")
            lines.append(f"        self.when_{slug}()")
            lines.append(f"        # Then")
            lines.append(f"        self.then_{slug}()")
        return lines

    def _hydrate_leaf_sub_epic_from_content(
        self, current_sub_epic: SubEpic, file_name: str, content: str
    ) -> None:
        if not file_name.endswith(self.LEAF_EXTENSION):
            return
        if file_name.endswith("_helper.py"):
            return
        if current_sub_epic.stories:
            return

        class_blocks = re.finditer(
            r"class\s+Test[A-Za-z0-9_]+\([^)]*\):\s*\n\s+\"\"\"([^\"]+)\"\"\"([\s\S]*?)(?=\nclass\s+Test|\Z)",
            content,
        )
        for match in class_blocks:
            story_name = match.group(1).strip()
            body = match.group(2)
            story = Story(story_name, len(current_sub_epic.stories) + 1)

            methods = re.finditer(
                r"def\s+test_[A-Za-z0-9_]+\(\s*self\s*\):([\s\S]*?)(?=\n\s+def\s+test_|\Z)",
                body,
            )
            for i, method in enumerate(methods, start=1):
                method_body = method.group(1)
                scenario_name = f"AC {i}"
                scenario_match = re.search(r"SCENARIO:\s*(.+)", method_body)
                when_match = re.search(r"WHEN:\s*(.+)", method_body)
                if scenario_match:
                    scenario_name = scenario_match.group(1).strip()
                when_text = when_match.group(1).strip() if when_match else scenario_name
                story.acceptance_criteria.append(
                    AcceptanceCriteria(
                        name=scenario_name,
                        sequential_order=i,
                        text=when_text,
                    )
                )

            current_sub_epic.stories.append(story)
