"""Centralized path resolution for story graph and documentation outputs."""

from pathlib import Path
from typing import List, Optional


class StoryGraphPaths:
    """Centralized path resolution for story graph and documentation outputs.
    
    Provides a single source of truth for all documentation paths:
    - docs/story/ for story_bot outputs
    - docs/domain/ for domain model outputs
    - Behavior-specific subfolders (shape, exploration, scenarios, etc.)
    """

    def __init__(self, workspace_directory: Path, bot_name: str = "story") -> None:
        self._workspace_directory = workspace_directory
        self._bot_name = bot_name

    @property
    def workspace_directory(self) -> Path:
        return self._workspace_directory

    @property
    def bot_name(self) -> str:
        return self._bot_name

    @property
    def docs_root(self) -> Path:
        return self._workspace_directory / "docs"

    @property
    def story_graph_path(self) -> Path:
        return self.docs_root / "stories" / "story-graph.json"

    @property
    def story_graph_cache_path(self) -> Path:
        return self.docs_root / "stories" / ".story-graph-cache.json"

    def behavior_path(self, behavior: str) -> Path:
        return self.docs_root / self._bot_name / behavior

    @property
    def bot_workspace_config_path(self) -> Path:
        return self._workspace_directory / f"{self._bot_name}_config.json"

    @property
    def scenarios_path(self) -> Path:
        return self.docs_root / self._bot_name / "scenarios"

    def ensure_folders(self, behaviors: Optional[List[str]] = None) -> None:
        self.docs_root.mkdir(parents=True, exist_ok=True)
        (self.docs_root / "stories").mkdir(parents=True, exist_ok=True)
        if behaviors:
            for behavior in behaviors:
                self.behavior_path(behavior).mkdir(parents=True, exist_ok=True)
