"""Module: space/session. Model delta (clean-engineering-model, python): *Session*.
Canonical: harness/.context/editor-apps/.context/editor-apps-model.md#session-extended"""
from __future__ import annotations

from harness.installation.data_class import data_field


class Session:
    @property
    @data_field
    def design_view(self) -> str:
        # -> CanvasVersions.in_practice_root(output.folder).link(latest), for each enabled practice output
        # empty when no link is recorded
        ...
