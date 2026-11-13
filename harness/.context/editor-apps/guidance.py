"""Module: harness/guidance. Model delta (clean-engineering-model, python): *PracticeGuidance*, *FidelityGuidance*.
Canonical: harness/.context/editor-apps/.context/editor-apps-model.md#harnessguidance"""
from __future__ import annotations

from pathlib import Path
from typing import Any, ClassVar

from harness.diagnostics.app import App
from harness.markdown.format import Format


class PracticeGuidance:
    # a class field: the editor belongs to the practice's kind, set once by space/kanban for Stories
    # (Stories.editor = STORY_UI_APP), so no practice imports space
    editor: ClassVar[App | None] = None

    @property
    def session_root(self) -> Path | None:
        # -> self._session_output.folder; none outside a session
        ...

    def work_in(self, session_output: Any) -> None:
        # session_output is space/session's PracticeSessionOutput, typed Any as today: harness imports nothing from space
        # keeps session_output, then gives each fidelity its own
        # -> FidelityGuidance.work_in
        ...


class FidelityGuidance:
    @property
    def format(self) -> Format:
        # -> self.session_output.chosen_formats (the first), else the default
        ...

    @format.setter
    def format(self, value: str | None) -> None:
        # -> self.session_output.choose_format(value, True)
        ...
