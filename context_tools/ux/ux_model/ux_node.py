"""UxNode - abstract base for every node in every format."""

from __future__ import annotations

from typing import List, Optional

from .update_report import ChildCollectionPair, TranslationError, UpdateReport


class UxNode:
    """Subclasses declare `_semantic_type_name` so cross-format nodes translate cleanly."""

    _semantic_type_name: str = "UxNode"

    def __init__(self, name: str, sequential_order: int) -> None:
        self.name = name
        self.sequential_order = sequential_order

    def semantic_type(self) -> str:
        return self._semantic_type_name

    def translate_from(self, source: "UxNode") -> UpdateReport:
        if self.semantic_type() != source.semantic_type():
            raise TranslationError(
                f"Cannot translate from {source.semantic_type()} into {self.semantic_type()}"
            )
        report = UpdateReport()
        self.update_self(source)
        for pair in self.child_collections(source):
            self._reconcile_collection(pair, report)
        return report

    def update_self(self, source: "UxNode") -> None:
        raise NotImplementedError(f"{type(self).__name__} must implement update_self")

    def child_collections(self, source: "UxNode") -> List[ChildCollectionPair]:
        raise NotImplementedError(f"{type(self).__name__} must implement child_collections")

    def children(self) -> List["UxNode"]:
        result: List[UxNode] = []
        try:
            for pair in self.child_collections(self):
                result.extend(pair.self_children)
        except NotImplementedError:
            pass
        return result

    def snapshot_fields(self) -> dict:
        return {}

    def _reconcile_collection(self, pair: ChildCollectionPair, report: UpdateReport) -> None:
        consumed_ids: set = set()
        reconciled: List[UxNode] = []

        for source_child in pair.source_children:
            match = self._find_match(source_child, pair.self_children, consumed_ids)
            if match is not None:
                consumed_ids.add(id(match))
                match.translate_from(source_child)
                reconciled.append(match)
                report.add_exact_match(match.name)
            else:
                new_child = pair.create_child(source_child)
                new_child.translate_from(source_child)
                reconciled.append(new_child)
                report.add_new(new_child, parent_name=self.name)

        for existing in pair.self_children:
            if id(existing) not in consumed_ids:
                report.add_removed(existing, parent_name=self.name)

        pair.self_children[:] = reconciled

    @staticmethod
    def _find_match(
        source: "UxNode",
        candidates: List["UxNode"],
        consumed_ids: set,
    ) -> Optional["UxNode"]:
        for candidate in candidates:
            if id(candidate) not in consumed_ids and candidate.name == source.name:
                return candidate
        for candidate in candidates:
            if (
                id(candidate) not in consumed_ids
                and candidate.sequential_order == source.sequential_order
            ):
                return candidate
        return None

    @staticmethod
    def _renumber(nodes: List["UxNode"]) -> None:
        for index, node in enumerate(nodes):
            node.sequential_order = index
