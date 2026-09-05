"""Persisted node-position cache for diagram re-renders.

Saved as JSON beside the diagram file (DrawIO) or board (Miro). Used to
preserve user-edited positions when re-rendering after a story-graph change.
"""
import json
from pathlib import Path
from typing import Optional, Dict

from .position import Position, Boundary


class LayoutData:
    """Map of ``node_key`` → ``{x, y, width, height}``."""

    def __init__(self, entries: Dict[str, Dict[str, float]] = None):
        self._entries = entries or {}

    @property
    def entries(self) -> Dict[str, Dict[str, float]]:
        return dict(self._entries)

    def position_for(self, node_key: str) -> Optional[Position]:
        entry = self._entries.get(node_key)
        if entry and 'x' in entry and 'y' in entry:
            return Position(entry['x'], entry['y'])
        return None

    def boundary_for(self, node_key: str) -> Optional[Boundary]:
        entry = self._entries.get(node_key)
        if entry and all(k in entry for k in ('x', 'y', 'width', 'height')):
            return Boundary(entry['x'], entry['y'], entry['width'], entry['height'])
        return None

    def has_entry(self, node_key: str) -> bool:
        return node_key in self._entries

    def set_entry(self, node_key: str, x: float, y: float,
                  width: float, height: float) -> None:
        self._entries[node_key] = {
            'x': x, 'y': y, 'width': width, 'height': height,
        }

    def save(self, file_path: Path) -> None:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(json.dumps(self._entries, indent=2), encoding='utf-8')

    @classmethod
    def load(cls, file_path: Path) -> Optional['LayoutData']:
        if not file_path.exists():
            return None
        content = file_path.read_text(encoding='utf-8')
        entries = json.loads(content)
        return cls(entries)
