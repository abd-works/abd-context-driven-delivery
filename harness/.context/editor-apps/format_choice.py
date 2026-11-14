"""Module: space/kanban. Model delta (clean-engineering-model, python): *FormatChoice*.
Canonical: harness/.context/editor-apps/.context/editor-apps-model.md#formatchoice-extended
Deleted: starts_picked."""
from __future__ import annotations

from harness.installation.data_class import data_field


class FormatChoice:
    @property
    @data_field
    def is_chosen(self) -> bool:
        # -> fidelity.session_output.chosen_formats (every fidelity in the chip)
        ...
