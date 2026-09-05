"""High-level synchronizer entrypoint analogous to ``DrawIOSynchronizer``.

Wires together graph loading (via **story-graph-ops** when available),
render, and transport flush. Future ``report`` and ``apply-report`` commands
plug into the same shape.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Union

from . import _bootstrap  # noqa: F401

from .miro_story_map import MiroStoryMap
from .miro_transport import InMemoryMiroTransport, MiroTransport


__all__ = ['MiroSynchronizer', 'load_story_graph_json']


def _story_graph_ops_scripts() -> Path:
    """``skills/supporting/story-graph-ops/scripts`` next to this skill folder."""
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


class MiroSynchronizer:
    """One-shot ``render`` to a Miro board.

    The transport is supplied by the caller so a CLI can swap between
    ``RestMiroTransport`` (real board) and ``InMemoryMiroTransport``
    (``--dry-run``).
    """

    def __init__(self, transport: Optional[MiroTransport] = None) -> None:
        self._transport = transport or InMemoryMiroTransport()

    @property
    def transport(self) -> MiroTransport:
        return self._transport

    def render(self, input_path: Union[str, Path], *,
               renderer_command: Optional[str] = 'render-outline',
               **kwargs: Any) -> Dict[str, Any]:
        """Render ``story-graph.json`` to the configured Miro board.

        Returns a summary dict shaped like ``DrawIOSynchronizer.render``: a
        ``summary`` field (RenderSummary as dict), the board id when
        applicable, and the count of items pushed to the transport.
        """
        from story_graph_ops.nodes import StoryMap

        OUTLINE_COMMANDS = {None, 'render-outline', 'outline'}
        EXPLORATION_COMMANDS = {'render-exploration', 'exploration', 'acceptance-criteria'}

        input_path = Path(input_path)
        graph_data = load_story_graph_json(input_path)
        story_map = StoryMap(graph_data)

        scope = kwargs.get('scope')
        if scope:
            filtered = story_map.filter_by_name(scope)
            if filtered is not None:
                story_map = filtered

        if renderer_command in OUTLINE_COMMANDS:
            miro_map = MiroStoryMap(self._transport, diagram_type='outline')
            summary = miro_map.render_from_story_map(story_map, layout_data=None)
        elif renderer_command in EXPLORATION_COMMANDS:
            from .miro_story_map import MiroExplorationMap
            pruned_data = MiroExplorationMap.prune_graph_for_exploration(graph_data)
            story_map = StoryMap(pruned_data)
            if scope:
                filtered = story_map.filter_by_name(scope)
                if filtered is not None:
                    story_map = filtered
            miro_map = MiroExplorationMap(self._transport)
            summary = miro_map.render(story_map, layout_data=None)
        else:
            raise NotImplementedError(
                f'Renderer command {renderer_command!r} is not yet implemented. '
                'Use: render-outline, render-exploration.'
            )
        items = miro_map.flush()

        return {
            'summary': summary.to_dict() if hasattr(summary, 'to_dict') else summary,
            'item_count': len(items),
            'board_id': getattr(self._transport, 'board_id', None),
            'transport': type(self._transport).__name__,
        }
