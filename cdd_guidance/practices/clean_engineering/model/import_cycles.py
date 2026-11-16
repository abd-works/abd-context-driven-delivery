"""The imports of one import graph that close a cycle, which the one-way-deps facts record on each folder."""

from __future__ import annotations

from typing import Iterator


class ImportCycles:
    """The groups of two or more modules of one import graph that import one another in a cycle, found with Tarjan's
    strongly connected components. Walking each path from every module is exponential on a repository-sized graph;
    this visits each module once."""

    def __init__(self, imports: dict[str, set[str]]) -> None:
        self._imports = imports
        self._index: dict[str, int] = {}
        self._lowest: dict[str, int] = {}
        self._stack: list[str] = []
        self._on_stack: set[str] = set()
        self._groups: list[set[str]] = []

    def imports_in_cycles(self) -> list[tuple[str, str, int]]:
        """Each import between two modules of one cycle, with the number of modules in that cycle, in name order."""
        return [
            (importer, imported, len(cycle))
            for cycle in self._cycles()
            for importer in sorted(cycle)
            for imported in sorted(self._imports.get(importer, set()) & cycle)
        ]

    def _cycles(self) -> list[set[str]]:
        for start in sorted(self._imports):
            if start not in self._index:
                self._walk_from(start)
        return [group for group in self._groups if len(group) > 1]

    def _walk_from(self, start: str) -> None:
        work = [self._enter(start)]
        while work:
            self._step(work)

    def _step(self, work: list[tuple[str, Iterator[str]]]) -> None:
        """Follow the next import of the module on top of the walk: leave it when it has none left, enter a module not
        yet reached, or lower its index to one still on the stack, which shares its group."""
        module, pending = work[-1]
        imported = next(pending, None)
        if imported is None:
            self._leave(work)
        elif imported not in self._index:
            work.append(self._enter(imported))
        elif imported in self._on_stack:
            self._lowest[module] = min(self._lowest[module], self._index[imported])

    def _enter(self, module: str) -> tuple[str, Iterator[str]]:
        self._index[module] = self._lowest[module] = len(self._index)
        self._stack.append(module)
        self._on_stack.add(module)
        return module, iter(sorted(self._imports.get(module, ())))

    def _leave(self, work: list[tuple[str, Iterator[str]]]) -> None:
        """Finish the module on top of the walk: hand its lowest index to the module that reached it, and close its
        group when it is the first of the group the walk entered."""
        module, _ = work.pop()
        if work:
            caller = work[-1][0]
            self._lowest[caller] = min(self._lowest[caller], self._lowest[module])
        if self._lowest[module] == self._index[module]:
            self._groups.append(self._pop_group(module))

    def _pop_group(self, root: str) -> set[str]:
        group: set[str] = set()
        while True:
            member = self._stack.pop()
            self._on_stack.discard(member)
            group.add(member)
            if member == root:
                return group
