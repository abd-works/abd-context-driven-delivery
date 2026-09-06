"""Backward-compatible re-export of ``RenderSummary`` from the shared package."""
from . import _bootstrap  # noqa: F401

from diagram_story_sync.render_summary import RenderSummary  # noqa: F401

__all__ = ['RenderSummary']
