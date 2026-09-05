"""Backward-compatible re-export of ``Position`` / ``Boundary`` from the
shared ``diagram_story_sync`` package.

The geometric primitives moved into ``common/diagram_story_sync`` so that
``miro-story-sync`` and any future backend can use the same types. Existing
imports of ``drawio_story_sync.story_io_position`` continue to work.
"""
from . import _bootstrap  # noqa: F401

from diagram_story_sync.position import Position, Boundary  # noqa: F401

__all__ = ['Position', 'Boundary']
