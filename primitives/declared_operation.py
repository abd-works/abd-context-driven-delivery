from __future__ import annotations

import inspect
from typing import Any, Callable

from .declared_member import DeclaredMember


class DeclaredOperation(DeclaredMember):
    def __init__(
        self,
        name: str | None = None,
        *,
        label: str | None = None,
        target: str | None = None,
    ) -> None:
        super().__init__(name=name or "", label=label, target=target)
        self._name_from_attribute = name is None

    def __set_name__(self, owner: type[Any], attribute_name: str) -> None:
        if self._name_from_attribute:
            object.__setattr__(self, "name", attribute_name)

    def __get__(self, instance: Any, owner: type[Any] | None = None) -> DeclaredOperation | Callable[[], str]:
        if instance is None:
            return self
        return self._docstring_callable(instance)

    def route(self, instance: Any) -> Callable[..., Any] | None:
        if not self.target:
            return None
        operation = getattr(instance, self.target, None)
        return operation if callable(operation) else None

    def _docstring_callable(self, instance: Any) -> Callable[[], str]:
        def docstring() -> str:
            operation = self.route(instance)
            if operation is None:
                return ""
            return (inspect.getdoc(operation) or "").strip()

        return docstring
