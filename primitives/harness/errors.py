"""Harness run errors — YAML request/response failures."""
from __future__ import annotations

from typing import Any


class RunError(Exception):
    def __init__(self, message: str, *, response: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self._response = response or {"ok": False, "error": message}

    @property
    def response(self) -> dict[str, Any]:
        return self._response
