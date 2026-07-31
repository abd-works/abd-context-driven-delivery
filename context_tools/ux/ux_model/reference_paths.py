"""Reference path properties - ordered, de-duplicated paths to external JS artifacts."""

from __future__ import annotations

from typing import Iterable, Iterator, List, overload


class ReferencePaths:
    """Paths pointing at story or object-model JS (references only - not the modules)."""

    def __init__(self, paths: Iterable[str] | None = None) -> None:
        self._paths: List[str] = []
        if paths:
            self.replace(paths)

    def add(self, path: str) -> None:
        normalized = (path or "").strip()
        if normalized and normalized not in self._paths:
            self._paths.append(normalized)

    def replace(self, paths: Iterable[str]) -> None:
        self._paths = []
        for path in paths:
            self.add(path)

    def clear(self) -> None:
        self._paths.clear()

    def as_list(self) -> List[str]:
        return list(self._paths)

    def __iter__(self) -> Iterator[str]:
        return iter(self._paths)

    def __len__(self) -> int:
        return len(self._paths)

    def __bool__(self) -> bool:
        return bool(self._paths)

    def __contains__(self, path: object) -> bool:
        return path in self._paths

    @overload
    def __getitem__(self, index: int) -> str: ...

    @overload
    def __getitem__(self, index: slice) -> List[str]: ...

    def __getitem__(self, index: int | slice) -> str | List[str]:
        return self._paths[index]

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ReferencePaths):
            return self._paths == other._paths
        if isinstance(other, list):
            return self._paths == other
        return NotImplemented

    def __repr__(self) -> str:
        return f"ReferencePaths({self._paths!r})"
