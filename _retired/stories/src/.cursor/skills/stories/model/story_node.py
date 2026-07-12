"""StoryNode — abstract base for every node in every format.

Defines the FINAL translate_from algorithm and reconcileCollection helper. Subclasses
override update_self, child_collections, and one create_child_xxx per child type.
"""

from __future__ import annotations

from typing import List, Optional

from .update_report import (
    ChildCollectionPair,
    NodeSnapshot,
    TranslationError,
    UpdateReport,
)


class StoryNode:
    """Abstract base. Subclasses declare `_semantic_type_name` so cross-format nodes
    (e.g. MarkdownEpic vs JsonEpic) share one semantic axis and translate cleanly."""

    _semantic_type_name: str = "StoryNode"

    def __init__(self, name: str, sequential_order: int):
        self.name = name
        self.sequential_order = sequential_order

    def semantic_type(self) -> str:
        return self._semantic_type_name

    def translate_from(self, source: "StoryNode") -> UpdateReport:
        if self.semantic_type() != source.semantic_type():
            raise TranslationError(
                f"Cannot translate from {source.semantic_type()} into "
                f"{self.semantic_type()}"
            )
        report = UpdateReport()
        report.capture_snapshot(self)
        self.update_self(source)
        for pair in self.child_collections(source):
            self._reconcile_collection(pair, report)
        return report

    def update_self(self, source: "StoryNode") -> None:
        raise NotImplementedError(
            f"{type(self).__name__} must implement update_self"
        )

    def child_collections(self, source: "StoryNode") -> List[ChildCollectionPair]:
        raise NotImplementedError(
            f"{type(self).__name__} must implement child_collections"
        )

    def children(self) -> List["StoryNode"]:
        # WHY: NodeSnapshot walks the tree without knowing shape; pull children from
        # the same pairs that translate_from reconciles, using self as its own source.
        result: List[StoryNode] = []
        try:
            for pair in self.child_collections(self):
                result.extend(pair.self_children)
        except NotImplementedError:
            pass
        return result

    def snapshot_fields(self) -> dict:
        # WHY: allow subclasses to include type-specific fields in the snapshot;
        # base returns empty and leaf classes override.
        return {}

    def restore_snapshot_fields(self, fields: dict) -> None:
        for key, value in fields.items():
            setattr(self, key, value)

    def reverse(self, report: UpdateReport) -> None:
        report.reverse_on(self)

    def _reconcile_collection(
        self, pair: ChildCollectionPair, report: UpdateReport
    ) -> None:
        consumed_ids: set = set()
        reconciled: List[StoryNode] = []

        for source_child in pair.source_children:
            match = self._find_match(source_child, pair.self_children, consumed_ids)
            if match is not None:
                old_name = match.name
                consumed_ids.add(id(match))
                match.translate_from(source_child)
                reconciled.append(match)
                if old_name == source_child.name:
                    report.add_exact_match(match.name, source_child.name)
                else:
                    report.add_rename(old_name, source_child.name, confidence=1.0)
            else:
                new_child = pair.create_child(source_child)
                new_child.translate_from(source_child)
                reconciled.append(new_child)
                report.add_new(new_child, parent_name=self.name)

        for existing in pair.self_children:
            if id(existing) not in consumed_ids:
                report.add_removed(existing, parent_name=self.name)

        previous_kept_order = [c for c in pair.self_children if id(c) in consumed_ids]
        for i, node in enumerate(reconciled):
            if i >= len(previous_kept_order):
                break
            if previous_kept_order[i] is not node:
                report.add_reorder(previous_kept_order[i].name, node.name)
                break

        pair.self_children[:] = reconciled

    @staticmethod
    def _find_match(
        source_child: "StoryNode",
        candidates: List["StoryNode"],
        consumed_ids: set,
    ) -> Optional["StoryNode"]:
        for candidate in candidates:
            if id(candidate) in consumed_ids:
                continue
            if candidate.name == source_child.name:
                return candidate
        for candidate in candidates:
            if id(candidate) in consumed_ids:
                continue
            if candidate.sequential_order == source_child.sequential_order:
                return candidate
        return None
