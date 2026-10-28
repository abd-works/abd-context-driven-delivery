"""JavaStoryModel - runnable `{Story}Story.java` per Story."""

from __future__ import annotations

from typing import Dict, List, Optional

from cdd_guidance.practices.stories.model.code_story_model import CodeStoryModel, CodeStoryModelError
from cdd_guidance.practices.stories.model.java.nodes import JavaEpic, JavaScenario, JavaStory
from cdd_guidance.practices.stories.model.story_model import Epic, Story


class JavaStoryModel(CodeStoryModel):
    LEAF_EXTENSION = "Story.java"
    LANGUAGE_LINE_COMMENT = "//"
    epic_type = JavaEpic
    story_type = JavaStory

    def save(self) -> Dict[str, str]:
        return self.write_epics({})

    def file_name(self, epic: Epic) -> str:
        return f"{epic.pascal()}Story.java"

    def file_header(self, epic: Epic, parent: str) -> List[str]:
        return [f"// Epic: {epic.name}", f"// Orders: {epic.order_path()}", ""]

    def story_lines(self, story: Story) -> List[str]:
        """A Java story is a doc comment: names and steps, no code, so there is no body to carry."""
        actor = (story.actors[0] if story.actors else "").strip()
        lines = [f"/** Story: {story.name}"]
        if actor:
            lines.append(f" * Actor: {actor}")
        example_line = self.story_type.background_example_line(story, " * ")
        if example_line:
            lines.append(example_line)
        for background in story.backgrounds:
            lines.append(f" * BACKGROUND: {background.name}")
            for step in background.steps:
                if step.keyword != "Given":
                    continue
                lines.append(f" * GIVEN: {step.text}")
                for extra in step.ands:
                    lines.append(f" * {extra.keyword.upper()}: {extra.text}")
        for scenario in story.scenarios:
            lines.extend(JavaScenario.create(scenario))
        lines.append(" */")
        return lines

    def leaf_files_of(self, tree: Dict[str, str]) -> List[str]:
        return sorted(
            p
            for p in tree
            if p.endswith(self.LEAF_EXTENSION) and not p.endswith("Helper.java")
        )

    def load(self, external: Dict[str, str]) -> "JavaStoryModel":
        if not isinstance(external, dict):
            raise CodeStoryModelError("Java story map parse expects a path->content dict")
        self.epics.clear()
        for path in self._ordered_paths(external):
            content = external[path]
            if not path.endswith(self.LEAF_EXTENSION) or path.endswith("Helper.java"):
                continue
            if "Spec" in path.split("/")[-1]:
                continue
            parts = path.strip("/").split("/")
            if parts and parts[0] == self.tests_root:
                parts = parts[1:]
            if self.take_sub_epic_file(parts, content, path):
                continue
            if len(parts) < 4:
                continue
            epic_slug, story_slug, sub_slugs = parts[0], parts[-2], parts[1:-2]
            if not sub_slugs:
                continue
            epic = self.epic_for(epic_slug)
            sub = self.sub_epic_for(epic, sub_slugs)
            sub.append_story(self.story_type.load(content, story_slug))
        return self
