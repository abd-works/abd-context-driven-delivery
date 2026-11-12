"""Module: space/kanban. Model delta (clean-engineering-model, python): *Board*.
Canonical: harness/.context/editor-apps/.context/editor-apps-model.md#board-extended"""
from __future__ import annotations

from harness.installation.data_class import data_field


class Board:
    @property
    @data_field
    def last_activated(self) -> Ticket | None:
        # kept in .sessions/_board.json: activation changes no open session, so it cannot be read from the work
        ...

    def keep_activated(self, ticket: Ticket) -> None:
        ...
