"""Fidelity — the five levels of maturity a skill's content is tagged for."""

from __future__ import annotations

from enum import Enum


class UnknownFidelityError(ValueError):
    """Raised when a fidelity string is not one of the five known values."""

    def __init__(self, value: str):
        super().__init__(f"Unknown fidelity: {value!r}")
        self.value = value


class Fidelity(str, Enum):
    SHAPING = "shaping"
    DISCOVERY = "discovery"
    EXPLORATION = "exploration"
    SPECIFICATION = "specification"
    ENGINEERING = "engineering"

    @classmethod
    def parse(cls, value: str) -> "Fidelity":
        try:
            return cls(value)
        except ValueError as error:
            raise UnknownFidelityError(value) from error

    @classmethod
    def all(cls) -> tuple["Fidelity", ...]:
        return tuple(cls)
