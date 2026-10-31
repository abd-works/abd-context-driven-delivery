from __future__ import annotations


class Condition:




    @property
    def name(self) -> object:
        ...


    @property
    def game_modifier(self) -> object:
        ...


    @property
    def supersedes(self) -> object:
        ...


    @property
    def superseded_by(self) -> object:
        ...


    @property
    def constituents(self) -> object:
        ...
