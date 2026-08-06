"""JavaScript tier-spec renderer - back-compat shim.

The real renderer moved to `javascript/story_file.py::render_test_helper_file`
so the story file and its test-helper skeletons live next to each other and
share the same clause -> method-name derivation. This module re-exports it
under the historical name for any caller that has not migrated yet.
"""

from __future__ import annotations

from context_tools.stories.code.javascript.story_file import (
    render_story_file as render_story_spec_file,
    render_test_helper_file as render_tier_spec_file,
)

__all__ = ["render_story_spec_file", "render_tier_spec_file"]
