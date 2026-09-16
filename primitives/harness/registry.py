"""Deploy registry — hosts registered for Harness.write_deploy."""
from __future__ import annotations

from typing import Any


class Registry:
    _hosts: list[Any] = []

    @classmethod
    def register(cls, host: Any) -> None:
        cls._hosts.append(host)

    @classmethod
    def load(cls) -> list[Any]:
        return list(cls._hosts)

    @classmethod
    def reset(cls) -> None:
        cls._hosts.clear()
