from pathlib import Path
from typing import Dict, Any, Optional, Union
import json
import sys

_INCREMENT_SCOPE_PREFIX = "increment:"


def _increment_scope_target(scope: Optional[str]) -> Optional[str]:
    if not scope or not isinstance(scope, str):
        return None
    s = scope.strip()
    if s.lower().startswith(_INCREMENT_SCOPE_PREFIX):
        rest = s[len(_INCREMENT_SCOPE_PREFIX) :].strip()
        return rest or None
    return None


def _has_increment_named(graph_data: Dict[str, Any], name: str) -> bool:
    for inc in graph_data.get("increments") or []:
        if isinstance(inc, dict) and inc.get("name") == name:
            return True
    return False


def _story_graph_ops_scripts() -> Path:
    """``skills/supporting/story-graph-ops/scripts`` next to this skill (``skills/supporting/drawio-story-sync/...``)."""
    return Path(__file__).resolve().parents[2].parent / 'story-graph-ops' / 'scripts'


_ops_scripts = _story_graph_ops_scripts()
if _ops_scripts.is_dir():
    _ops_p = str(_ops_scripts)
    if _ops_p not in sys.path:
        sys.path.insert(0, _ops_p)


def load_story_graph_json(path: Path) -> Dict[str, Any]:
    """Prefer **story-graph-ops** validated load; fall back to plain JSON."""
    ops = _story_graph_ops_scripts()
    if ops.is_dir():
        p = str(ops)
        if p not in sys.path:
            sys.path.insert(0, p)
        try:
            from story_graph_file import load_story_graph_dict

            return load_story_graph_dict(path)
        except ImportError:
            pass
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


class DrawIOSynchronizer:

    def render(self, input_path: Union[str, Path], output_path: Union[str, Path],
               renderer_command: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        from .drawio_story_map import DrawIOStoryMap
        from .layout_data import LayoutData
        from story_graph_ops.nodes import StoryMap

        input_path = Path(input_path)
        output_path = Path(output_path)

        graph_data = load_story_graph_json(input_path)

        scope = kwargs.get("scope")
        inc_target = _increment_scope_target(scope)
        if inc_target is not None and not _has_increment_named(graph_data, inc_target):
            return {
                "skipped": True,
                "skip_reason": f'Increment "{inc_target}" not found in story graph.',
                "output_path": str(output_path),
            }

        story_map = StoryMap(graph_data)

        if scope:
            filtered = story_map.filter_by_name(scope)
            if filtered is not None:
                story_map = filtered

        layout_path = output_path.parent / f"{output_path.stem}-layout.json"
        layout_data = LayoutData.load(layout_path) if layout_path.exists() else None

        drawio_map = DrawIOStoryMap()

        if renderer_command == 'render-increments':
            increments = graph_data.get('increments', [])
            summary = drawio_map.render_increments_from_story_map(
                story_map, increments, layout_data)
        elif renderer_command == 'render-exploration':
            summary = drawio_map.render_exploration_from_story_map(
                story_map, layout_data)
        else:
            summary = drawio_map.render_from_story_map(story_map, layout_data)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        drawio_map.save(output_path)

        return {
            "output_path": str(output_path),
            "summary": summary,
        }

    def save_layout(self, drawio_path: Union[str, Path]) -> Dict[str, Any]:
        from .drawio_story_map import DrawIOStoryMap

        drawio_path = Path(drawio_path)
        if not drawio_path.exists():
            return {"status": "error", "message": f"File not found: {drawio_path}"}

        drawio_map = DrawIOStoryMap.load(drawio_path)
        layout = drawio_map.extract_layout()
        layout_path = drawio_path.parent / f"{drawio_path.stem}-layout.json"
        layout.save(layout_path)

        return {"status": "success", "layout_path": str(layout_path)}
