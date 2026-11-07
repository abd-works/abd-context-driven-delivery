"""The map's transitions, content types, and nav components: ordered lists the map owns on its graph."""

from __future__ import annotations

from typing import Iterator, List, overload

from harness.graph.model_node import ModelChildren

from .nodes import ContentType, NavComponent, Transition, UxComponent
from .ux_node import UxNode


class UxComponentCollection:
    """One kind of UxComponent on the map, with append / remove / find. Appending records the map's edge to it."""

    _item_type: type[UxComponent] = UxComponent
    _edge_kind = ""

    def __init__(self, owner: UxNode) -> None:
        self._owner = owner
        self._items = ModelChildren(owner, self._edge_kind)

    def append(self, component: UxComponent) -> None:
        if not isinstance(component, self._item_type):
            raise TypeError(
                f"{type(self).__name__} expects {self._item_type.__name__}, "
                f"got {type(component).__name__}"
            )
        self._items.append(component)
        self._owner._renumber(self._items)

    def remove(self, name: str) -> UxComponent:
        for index, item in enumerate(self._items):
            if item.name == name:
                removed = self._items.pop(index)
                self._owner._renumber(self._items)
                return removed
        raise KeyError(f"{self._item_type.__name__} {name!r} not found in {self._edge_kind}")

    def find(self, name: str) -> UxComponent:
        for item in self._items:
            if item.name == name:
                return item
        raise KeyError(f"{self._item_type.__name__} {name!r} not found in {self._edge_kind}")

    def __iter__(self) -> Iterator[UxComponent]:
        return iter(self._items)

    def __len__(self) -> int:
        return len(self._items)

    @overload
    def __getitem__(self, index: int) -> UxComponent: ...

    @overload
    def __getitem__(self, index: slice) -> List[UxComponent]: ...

    def __getitem__(self, index: int | slice) -> UxComponent | List[UxComponent]:
        return self._items[index]

    def __bool__(self) -> bool:
        return bool(self._items)


class Transitions(UxComponentCollection):
    _item_type = Transition
    _edge_kind = "transitions"


class ContentTypes(UxComponentCollection):
    _item_type = ContentType
    _edge_kind = "contentTypes"


class NavComponents(UxComponentCollection):
    _item_type = NavComponent
    _edge_kind = "navComponents"
