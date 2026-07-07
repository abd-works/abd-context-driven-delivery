"""PythonStoryMap — renders each leaf SubEpic to a `<sub_epic_snake>.py` file of
pytest-shaped acceptance tests matching the abd-story-acceptance-test Python template.
"""

from __future__ import annotations

import re
from typing import List, Optional

from stories.src.stories.model.nodes import Story, SubEpic
from stories.src.stories.model.scenario import Scenario
from stories.src.stories.code.code_story_map import CodeStoryMap, to_kebab, to_pascal, to_snake
from stories.src.stories.code.python.nodes import PythonEpic, PythonStoryMap as _PythonStoryMap, PythonSubEpic


class PythonStoryMap(CodeStoryMap):

    def _make_story_map(self) -> _PythonStoryMap:
        return _PythonStoryMap()

    def _make_epic(self, name: str, order: int) -> PythonEpic:
        return PythonEpic(name, order)

    def _make_sub_epic(self, name: str, order: int) -> PythonSubEpic:
        return PythonSubEpic(name, order)
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
                for scenario in story.scenarios:
                    slug = to_snake(scenario.name)
                    for prefix in ("given", "when", "then"):
                        name = f"{prefix}_{slug}"
                        if name in seen:
                            continue
                        seen.add(name)
                        lines.append(f"    def {name}(self):")
                        lines.append(
                            f'        """Placeholder helper generated for {scenario.name!r}."""'
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
        for scenario in story.scenarios:
            slug = to_snake(scenario.name)
            lines.append("")
            lines.append(f"    def test_{slug}(self):")
            lines.append(f'        """')
            lines.append(f"        SCENARIO: {scenario.name}")
            given_text = scenario.given[0].text if scenario.given else "state is set up"
            when_text = (
                scenario.interactions[0].when[0].text
                if scenario.interactions and scenario.interactions[0].when
                else scenario.name
            )
            then_text = (
                scenario.interactions[0].then[0].text
                if scenario.interactions and scenario.interactions[0].then
                else "expected outcome"
            )
            lines.append(f"        GIVEN: {given_text}")
            lines.append(f"        WHEN: {when_text}")
            lines.append(f"        THEN: {then_text}")
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
                scenario_name = f"Scenario {i}"
                scenario_match = re.search(r"SCENARIO:\s*(.+)", method_body)
                if scenario_match:
                    scenario_name = scenario_match.group(1).strip()
                story.scenarios.append(
                    Scenario(
                        name=scenario_name,
                        sequential_order=i,
                    )
                )

            current_sub_epic.stories.append(story)
