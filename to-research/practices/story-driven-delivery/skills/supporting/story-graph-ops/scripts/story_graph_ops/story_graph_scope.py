"""Story-graph and file scoping (vendored from ``agile_bots`` ``src/scope/scope.py``).

Bot-free: no ``StoryGraph`` wrapper, no perf logging to ``.cursor``. Use
``StoryGraphScope.filtered_story_graph`` for a filtered ``dict`` or
``filters_story_graph`` on raw JSON.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)


class ScopeType(Enum):
    ALL = 'all'
    SHOW_ALL = 'showAll'
    STORY = 'story'
    INCREMENT = 'increment'
    FILES = 'files'


@dataclass
class StoryGraphFilter:
    search_terms: List[str] = field(default_factory=list)
    increments: List[Union[int, str]] = field(default_factory=list)

    def matches_node(self, node_name: str) -> bool:
        if not self.search_terms:
            return True
        return node_name in self.search_terms

    def _story_names_from_increments(self, story_graph: Dict[str, Any]) -> set:
        """Extract story names from increments matching self.increments (names or priorities)."""
        names = set()
        inc_list = story_graph.get('increments', [])
        for inc in inc_list:
            inc_name = (inc.get('name') or '').strip()
            inc_priority = inc.get('priority')
            match = False
            for v in self.increments:
                if isinstance(v, int) and inc_priority == v:
                    match = True
                    break
                if isinstance(v, str):
                    v_lower = (v or '').strip().lower()
                    inc_lower = inc_name.lower()
                    if inc_lower and (v_lower in inc_lower or inc_lower in v_lower):
                        match = True
                        break
            if match:
                for s in inc.get('stories', []):
                    sn = s.get('name', s) if isinstance(s, dict) else s
                    if sn:
                        names.add(sn)
        return names

    def filter_story_graph(self, story_graph: Dict[str, Any]) -> Dict[str, Any]:
        if not self.search_terms and not self.increments:
            return story_graph

        all_filter_names = list(self.search_terms)
        if self.increments:
            story_names = self._story_names_from_increments(story_graph)
            all_filter_names = list(story_names) if story_names else all_filter_names
            inc_list = story_graph.get('increments', [])
            filtered_inc = []
            for inc in inc_list:
                inc_name = (inc.get('name') or '').strip()
                inc_priority = inc.get('priority')
                for v in self.increments:
                    if isinstance(v, int) and inc_priority == v:
                        filtered_inc.append(inc)
                        break
                    if isinstance(v, str):
                        v_lower = (v or '').strip().lower()
                        inc_lower = inc_name.lower()
                        if inc_lower and (v_lower in inc_lower or inc_lower in v_lower):
                            filtered_inc.append(inc)
                            break
            story_graph = {**story_graph, 'increments': filtered_inc}

        filter_set = {f.strip().lower() for f in all_filter_names}
        use_exact = bool(self.increments)

        def name_matches(name: str) -> bool:
            n = (name or '').strip().lower()
            if not n:
                return False
            if use_exact:
                return n in filter_set
            return any(f in n or n in f for f in filter_set)

        def epic_matches(epic_name: str) -> bool:
            if not name_matches(epic_name):
                return False
            n = (epic_name or '').strip().lower()
            for f in filter_set:
                if f != n and '.' in f and f.startswith(n + '.'):
                    return False
            return True

        def filter_sub_epic(sub_epic: Dict[str, Any]) -> Optional[Dict[str, Any]]:
            sub_epic_name = sub_epic.get('name', '')

            if name_matches(sub_epic_name):
                return sub_epic

            matching_story_groups = []
            for story_group in sub_epic.get('story_groups', []):
                matching_stories = []
                for story in story_group.get('stories', []):
                    story_name = story.get('name', '')
                    if name_matches(story_name):
                        matching_stories.append(story)
                    else:
                        matching_scenarios = []
                        for scenario in story.get('scenarios', []):
                            scenario_name = scenario.get('name', '')
                            if name_matches(scenario_name):
                                matching_scenarios.append(scenario)

                        if matching_scenarios:
                            filtered_story = {**story, 'scenarios': matching_scenarios}
                            matching_stories.append(filtered_story)

                if matching_stories:
                    matching_story_groups.append({
                        **story_group,
                        'stories': matching_stories
                    })

            matching_direct_stories = []
            for story in sub_epic.get('stories', []):
                story_name = story.get('name', '')
                if name_matches(story_name):
                    matching_direct_stories.append(story)
                else:
                    matching_scenarios = []
                    for scenario in story.get('scenarios', []):
                        scenario_name = scenario.get('name', '')
                        if name_matches(scenario_name):
                            matching_scenarios.append(scenario)

                    if matching_scenarios:
                        filtered_story = {**story, 'scenarios': matching_scenarios}
                        matching_direct_stories.append(filtered_story)

            filtered_nested_sub_epics = []
            for nested_sub_epic in sub_epic.get('sub_epics', []):
                filtered_nested = filter_sub_epic(nested_sub_epic)
                if filtered_nested:
                    filtered_nested_sub_epics.append(filtered_nested)

            if matching_story_groups or matching_direct_stories or filtered_nested_sub_epics:
                filtered_sub_epic = {**sub_epic}
                if matching_story_groups:
                    filtered_sub_epic['story_groups'] = matching_story_groups
                if matching_direct_stories:
                    filtered_sub_epic['stories'] = matching_direct_stories
                if filtered_nested_sub_epics:
                    filtered_sub_epic['sub_epics'] = filtered_nested_sub_epics
                return filtered_sub_epic

            return None

        filtered_graph = {k: v for k, v in story_graph.items() if k != 'epics'}
        filtered_graph['epics'] = []
        epics = story_graph.get('epics', [])

        for epic in epics:
            epic_name = epic.get('name', '')

            if epic_matches(epic_name):
                filtered_graph['epics'].append(epic)
                continue

            filtered_sub_epics = []
            for sub_epic in epic.get('sub_epics', []):
                filtered_sub = filter_sub_epic(sub_epic)
                if filtered_sub:
                    filtered_sub_epics.append(filtered_sub)

            if filtered_sub_epics:
                filtered_epic = {**epic, 'sub_epics': filtered_sub_epics}
                filtered_graph['epics'].append(filtered_epic)

        return filtered_graph


@dataclass
class FileFilter:
    include_patterns: List[str] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=list)

    def matches_file(self, file_path: Path) -> bool:
        if not self.include_patterns:
            return True
        file_str = str(file_path)
        for pattern in self.include_patterns:
            if pattern in file_str:
                return True
        return False

    def filter_files(self, file_list: List[Path]) -> List[Path]:
        if not self.include_patterns and not self.exclude_patterns:
            return file_list

        from pathlib import PurePath
        filtered = []

        for file_path in file_list:
            file_str = str(file_path).replace('\\', '/')
            file_path_obj = PurePath(file_str)

            if self.include_patterns and not self._matches_include_pattern(file_path_obj, file_str):
                continue

            if self.exclude_patterns and self._matches_exclude_pattern(file_path_obj, file_str):
                continue

            filtered.append(file_path)

        return filtered

    def _matches_include_pattern(self, file_path_obj, file_str: str) -> bool:
        for pattern in self.include_patterns:
            if self._pattern_matches(file_path_obj, file_str, pattern):
                return True
        return False

    def _matches_exclude_pattern(self, file_path_obj, file_str: str) -> bool:
        for pattern in self.exclude_patterns:
            if self._pattern_matches(file_path_obj, file_str, pattern):
                return True
        return False

    def _pattern_matches(self, file_path_obj, file_str: str, pattern: str) -> bool:
        pattern_normalized = pattern.replace('\\', '/')
        try:
            if (file_path_obj.match(pattern_normalized) or
                    file_path_obj.match(f'**/{pattern_normalized}') or
                    pattern_normalized in file_str):
                return True
        except (ValueError, TypeError):
            return pattern_normalized in file_str
        return False


class StoryGraphScope:
    """Workspace scope for story graph JSON and file globs (no ``Bot`` / ``StoryGraph``)."""

    @staticmethod
    def get_parameter_description() -> str:
        return "Scope structure: {'type': 'story'|'epic'|'increment'|'all', 'value': <names|priorities>}"

    def __init__(self, workspace_directory: Path, bot_paths=None):
        self.workspace_directory = Path(workspace_directory)
        self.bot_paths = bot_paths

        self.type = ScopeType.SHOW_ALL
        self.value: List[str] = []
        self.exclude: List[str] = []
        self.skiprule: List[str] = []
        self.include_level: str = 'examples'

        self._story_graph_filter: Optional[StoryGraphFilter] = None
        self._file_filter: Optional[FileFilter] = None
        self._sg_dirty = True
        self._file_dirty = True
        self._cached_story_graph: Optional[Dict[str, Any]] = None
        self._cached_files: Optional[List[Path]] = None

    def copy(self) -> 'StoryGraphScope':
        new_scope = StoryGraphScope(self.workspace_directory, self.bot_paths)
        new_scope.type = self.type
        new_scope.value = list(self.value)
        new_scope.exclude = list(self.exclude)
        new_scope.skiprule = list(self.skiprule)
        new_scope.include_level = self.include_level
        new_scope._story_graph_filter = self._story_graph_filter
        new_scope._file_filter = self._file_filter
        new_scope._sg_dirty = True
        new_scope._file_dirty = True
        new_scope._cached_story_graph = None
        new_scope._cached_files = None
        return new_scope

    def filter(self, type: ScopeType, value: List[str] = None, exclude: List[str] = None, skiprule: List[str] = None):
        self.type = type
        self.value = value or []
        self.exclude = exclude or []
        self.skiprule = skiprule or []

        self._rebuild_filters()

        self._sg_dirty = True
        self._file_dirty = True
        self._cached_story_graph = None
        self._cached_files = None

    def clear(self):
        self.filter(ScopeType.ALL, [], [], [])

    def _rebuild_filters(self):
        self._story_graph_filter = None
        self._file_filter = None

        if self.type in (ScopeType.STORY, ScopeType.INCREMENT):
            if self.type == ScopeType.STORY:
                self._story_graph_filter = StoryGraphFilter(search_terms=self.value)
            elif self.type == ScopeType.INCREMENT:
                increments = [int(v) if isinstance(v, str) and v.isdigit() else v for v in self.value]
                self._story_graph_filter = StoryGraphFilter(increments=increments)

        if self.type == ScopeType.FILES:
            self._file_filter = FileFilter(
                include_patterns=self.value,
                exclude_patterns=self.exclude
            )

    @property
    def filtered_story_graph(self) -> Optional[Dict[str, Any]]:
        """Load ``story-graph.json``, apply story/increment filters, return a plain dict (or None)."""
        if self.type == ScopeType.FILES:
            return None
        if not self._sg_dirty:
            return self._cached_story_graph

        if self.type in (ScopeType.STORY, ScopeType.INCREMENT, ScopeType.SHOW_ALL, ScopeType.ALL):
            self._cached_story_graph = self._load_filtered_story_graph_dict()
        else:
            self._cached_story_graph = None

        self._sg_dirty = False
        return self._cached_story_graph

    @property
    def filtered_files(self) -> Optional[List[Path]]:
        if self.type != ScopeType.FILES:
            return None
        if not self._file_dirty:
            return self._cached_files
        self._cached_files = self._collect_file_paths()
        self._file_dirty = False
        return self._cached_files

    def _story_graph_path(self) -> Path:
        if self.bot_paths:
            return self.bot_paths.story_graph_paths.story_graph_path
        return self.workspace_directory / 'docs' / 'story' / 'story-graph.json'

    def _load_filtered_story_graph_dict(self) -> Optional[Dict[str, Any]]:
        story_graph_path = self._story_graph_path()
        if not story_graph_path.exists():
            return None
        try:
            graph_data = json.loads(story_graph_path.read_text(encoding='utf-8'))
            if self._story_graph_filter:
                return self._story_graph_filter.filter_story_graph(graph_data)
            return graph_data
        except Exception as e:
            logger.error('Error loading story graph: %s', e)
            return None

    def _collect_file_paths(self) -> List[Path]:
        import glob as glob_module

        all_files: List[Path] = []
        paths = self.value if isinstance(self.value, list) else [self.value]

        for path_str in paths:
            has_glob = any(char in path_str for char in ['*', '?', '['])

            if has_glob:
                matched_files = self._process_glob_pattern(path_str, glob_module)
                all_files.extend(matched_files)
            else:
                matched_files = self._process_regular_path(path_str)
                all_files.extend(matched_files)

        return all_files

    def _process_glob_pattern(self, path_str: str, glob_module) -> List[Path]:
        if not Path(path_str).is_absolute():
            pattern = str(self.workspace_directory / path_str)
        else:
            pattern = path_str

        matched_files = glob_module.glob(pattern, recursive=True)
        return [Path(match) for match in matched_files if Path(match).is_file()]

    def _process_regular_path(self, path_str: str) -> List[Path]:
        file_path = Path(path_str)
        if not file_path.is_absolute():
            file_path = self.workspace_directory / file_path

        if file_path.exists() and file_path.is_dir():
            return list(file_path.rglob('*.py'))

        if file_path.exists() and file_path.is_file():
            return [file_path]

        return []

    @property
    def story_graph_filter(self) -> Optional[StoryGraphFilter]:
        return self._story_graph_filter

    @property
    def file_filter(self) -> Optional[FileFilter]:
        return self._file_filter

    def filters_story_graph(self, story_graph: Dict[str, Any]) -> Dict[str, Any]:
        if self._story_graph_filter:
            return self._story_graph_filter.filter_story_graph(story_graph)
        return story_graph

    def filters_files(self, file_list: List[Path]) -> List[Path]:
        if self._file_filter:
            return self._file_filter.filter_files(file_list)
        return file_list

    def to_dict(self) -> Dict[str, Any]:
        return {
            'type': self.type.value,
            'value': self.value,
            'exclude': self.exclude,
            'skiprule': self.skiprule,
            'include_level': self.include_level,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], workspace_directory: Path, bot_paths=None) -> 'StoryGraphScope':
        scope = cls(workspace_directory, bot_paths)

        if not data:
            return scope

        scope_type_str = data.get('type', 'showAll')
        try:
            scope_type = ScopeType(scope_type_str)
        except ValueError:
            raise ValueError(
                f"Invalid scope type: '{scope_type_str}'. Valid types: {[t.value for t in ScopeType]}"
            )

        value = data.get('value', [])
        if not isinstance(value, list):
            value = [value] if value else []

        exclude = data.get('exclude', [])
        if not isinstance(exclude, list):
            exclude = [exclude] if exclude else []

        skiprule = data.get('skiprule', [])
        if not isinstance(skiprule, list):
            skiprule = [skiprule] if skiprule else []

        include_level = data.get('include_level', 'examples')

        scope.filter(scope_type, value, exclude, skiprule)
        scope.include_level = include_level

        return scope

    def save(self):
        scope_file = self.workspace_directory / 'scope.json'

        scope_file.parent.mkdir(parents=True, exist_ok=True)
        scope_file.write_text(json.dumps(self.to_dict(), indent=2))

    def load(self):
        scope_file = self.workspace_directory / 'scope.json'

        if not scope_file.exists():
            return

        try:
            scope_data = json.loads(scope_file.read_text())

            if scope_data:
                scope_type_str = scope_data.get('type', 'showAll')
                scope_type = ScopeType(scope_type_str)

                value = scope_data.get('value', [])
                if not isinstance(value, list):
                    value = [value] if value else []

                exclude = scope_data.get('exclude', [])
                if not isinstance(exclude, list):
                    exclude = [exclude] if exclude else []

                skiprule = scope_data.get('skiprule', [])
                if not isinstance(skiprule, list):
                    skiprule = [skiprule] if skiprule else []

                include_level = scope_data.get('include_level', 'examples')

                self.filter(scope_type, value, exclude, skiprule)
                self.include_level = include_level
        except (json.JSONDecodeError, IOError, ValueError) as e:
            logger.warning('Failed to load scope from file: %s', str(e))
