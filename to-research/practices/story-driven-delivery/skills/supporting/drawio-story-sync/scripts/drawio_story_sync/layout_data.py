"""Backward-compatible re-export of ``LayoutData`` from the shared package."""
from . import _bootstrap  # noqa: F401

from diagram_story_sync.layout_data import LayoutData  # noqa: F401

__all__ = ['LayoutData']
