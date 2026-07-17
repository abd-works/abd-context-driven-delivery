"""UxComponent collections — Transitions, ContentTypes, NavComponents."""

from __future__ import annotations

from typing import Iterator, List, TypeVar, overload

from .nodes import ContentType, NavComponent, Transition, UxComponent
from .update_report import ChildCollectionPair
from .ux_node import UxNode

T = TypeVar("T", bound=UxComponent)


class UxComponentCollection(UxNode):
    """Named collection of UxComponent items with append / remove / find."""

    _semantic_type_name = "UxComponentCollection"
    _item_type: type[UxComponent] = UxComponent

    def __init__(self, name: str, sequential_order: int = 0) -> None:
        super().__init__(name, sequential_order)
        self.items: List[UxComponent] = []

    def append(self, component: UxComponent) -> None:
        if not isinstance(component, self._item_type):
            raise TypeError(
                f"{type(self).__name__} expects {self._item_type.__name__}, "
                f"got {type(component).__name__}"
            )
        self.items.append(component)
        self._renumber(self.items)

    def remove(self, name: str) -> UxComponent:
        for index, item in enumerate(self.items):
            if item.name == name:
                removed = self.items.pop(index)
                self._renumber(self.items)
                return removed
        raise KeyError(f"{self._item_type.__name__} {name!r} not found in {self.name}")

    def find(self, name: str) -> UxComponent:
        for item in self.items:
            if item.name == name:
                return item
        raise KeyError(f"{self._item_type.__name__} {name!r} not found in {self.name}")

    def update_self(self, source: "UxComponentCollection") -> None:
        self.name = source.name
        self.sequential_order = source.sequential_order

    def child_collections(
        self, source: "UxComponentCollection"
    ) -> List[ChildCollectionPair]:
        return [
            ChildCollectionPair(
                self_children=self.items,
                source_children=source.items,
                create_child=self.create_child_component,
            )
        ]

    def create_child_component(self, source: UxComponent) -> UxComponent:
        raise NotImplementedError

    def __iter__(self) -> Iterator[UxComponent]:
        return iter(self.items)

    def __len__(self) -> int:
        return len(self.items)

    @overload
    def __getitem__(self, index: int) -> UxComponent: ...

    @overload
    def __getitem__(self, index: slice) -> List[UxComponent]: ...

    def __getitem__(self, index: int | slice) -> UxComponent | List[UxComponent]:
        return self.items[index]

    def __bool__(self) -> bool:
        return bool(self.items)


class Transitions(UxComponentCollection):
    _semantic_type_name = "Transitions"
    _item_type = Transition

    def __init__(self, sequential_order: int = 0) -> None:
        super().__init__("transitions", sequential_order)

    def append(self, transition: Transition) -> None:  # type: ignore[override]
        super().append(transition)

    def create_child_component(self, source: UxComponent) -> Transition:
        assert isinstance(source, Transition)
        return Transition(
            source.name,
            source.sequential_order,
            source.from_screen,
            source.to_screen,
            source.trigger,
            source.nav_type,
        )


class ContentTypes(UxComponentCollection):
    _semantic_type_name = "ContentTypes"
    _item_type = ContentType

    def __init__(self, sequential_order: int = 0) -> None:
        super().__init__("content_types", sequential_order)

    def append(self, content_type: ContentType) -> None:  # type: ignore[override]
        super().append(content_type)

    def create_child_component(self, source: UxComponent) -> ContentType:
        assert isinstance(source, ContentType)
        return ContentType(source.name, source.sequential_order, source.hierarchy)


class NavComponents(UxComponentCollection):
    _semantic_type_name = "NavComponents"
    _item_type = NavComponent

    def __init__(self, sequential_order: int = 0) -> None:
        super().__init__("nav_components", sequential_order)

    def append(self, nav_component: NavComponent) -> None:  # type: ignore[override]
        super().append(nav_component)

    def create_child_component(self, source: UxComponent) -> NavComponent:
        assert isinstance(source, NavComponent)
        return NavComponent(source.name, source.sequential_order, source.ux_type)
