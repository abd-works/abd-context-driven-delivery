"""How DDD takes part in the graph: its bounded contexts come from the folders that hold ``.context/bounded-context.md``,
its aggregates from the folders that hold domain classes, and its building blocks from the classes Clean Engineering
read, each seen through the DDD stereotype its declaration or name gives it."""

from __future__ import annotations

import os
import re
from pathlib import Path

from harness.graph.bound_node import schema_sync_paused
from harness.graph.graph import Node, PracticeGraph
from harness.graph.graph_practice import GraphPractice, GraphPractices
from harness.graph.skipped_folders import skips_folder

_PACKAGE = "cdd_guidance.practices.ddd"
# A helper class in a test folder is never a domain aggregate, whatever its name suggests.
_TEST_FOLDERS = ("tests/", "test-utils/")
_FOREIGN_KEY = "//\\s*foreign\\s+(\\w+)"


class DddGraph(GraphPractice):
    """DDD's nodes, read after Clean Engineering's classes, and its rules with Clean Engineering's."""

    reads_after = ("clean_engineering",)

    def own_rules(self) -> dict:
        return {**super().own_rules(), **GraphPractices.named("clean_engineering").rules()}

    def read(self, practice: PracticeGraph) -> None:
        with schema_sync_paused():
            _DddReading(practice).read()


class _DddReading:
    """One read of a working copy into the DDD practice graph."""

    def __init__(self, practice: PracticeGraph) -> None:
        self.practice = practice
        self.root = Path(practice.source_root)
        self._texts: dict[str, str] = {}
        self._blocks: dict[str, Node] = {}

    def read(self) -> None:
        self.practice.graph.report_progress("ddd · bounded contexts")
        contexts = self._contexts()
        for folder, members in sorted(self._members_by_folder().items()):
            self._aggregate(folder, members, _context_for(folder, contexts) or self.practice.root_node)

    def _contexts(self) -> dict[str, Node]:
        """Each bounded context by its folder, under the context of the folder around it."""
        found = _bounded_contexts(self.root) or [(".", _unmarked_context(self.root), ".")]
        contexts: dict[str, Node] = {}
        for rel, context, markdown in found:
            node = self.practice.add(context, f"ddd:BoundedContext:{rel}:{context.name}", markdown, 1, context.context_file_lines)
            parent = _context_for(str(Path(rel).parent).replace("\\", "/"), contexts) if rel != "." else None
            self.practice.link("owns", parent or self.practice.root_node, node)
            if parent is not None:
                self.practice.link("belongsTo", node, parent, "relationship")
            contexts[rel] = node
        return contexts

    def _members_by_folder(self) -> dict[str, list[tuple[Node, str]]]:
        """The classes Clean Engineering read that DDD names a building block, by folder, each with its kind."""
        from cdd_guidance.practices.ddd.model.stereotypes import class_declaration_decorated_name, inferred_tactical_kind

        clean = self.practice.graph.practices.get("clean_engineering")
        classes = clean.nodes.get("OoadClass", []) if clean is not None else []
        names = {cls.name for cls in classes}
        members: dict[str, list[tuple[Node, str]]] = {}
        for cls in classes:
            folder = str(Path(cls.source.file).parent).replace("\\", "/")
            kind = inferred_tactical_kind(class_declaration_decorated_name(self._text(cls), cls.name), names)
            if kind is not None and not f"{folder}/".startswith(_TEST_FOLDERS):
                members.setdefault(folder, []).append((cls, kind))
        return members

    def _aggregate(self, folder: str, members: list[tuple[Node, str]], context: Node) -> None:
        from cdd_guidance.practices.ddd.model.nodes import Aggregate

        aggregate = Aggregate(Path(folder).name, 1)
        aggregate.load_folder_facts(self.root / folder)
        node = self.practice.add(aggregate, f"ddd:Aggregate:{folder}", folder, 1, 1)
        self.practice.link("owns", context, node)
        self.practice.link("belongsTo", node, context, "relationship")
        for cls, kind in members:
            self._block(node, cls, kind)
        for cls, kind in members:
            if kind == "EntityRoot":
                self._associate(cls)

    def _block(self, aggregate: Node, cls: Node, kind: str) -> Node:
        node = self._block_node(cls, kind)
        node.set_fact("folder", cls.get_fact("folder"))
        self._blocks[cls.name] = node
        self.practice.link("root" if kind == "EntityRoot" else "owns", aggregate, node)
        self.practice.link("belongsTo", node, aggregate, "relationship")
        root = self._blocks.get(cls.name[: -len("Repository")]) if kind == "Repository" and cls.name.endswith("Repository") else None
        if root is not None:
            self.practice.link("accesses", node, root, "relationship")
        return node

    def _block_node(self, cls: Node, kind: str) -> Node:
        """The building block the class is; a kind DDD has no block for keeps the class's facts on a node of that kind."""
        node_id = f"ddd:{kind}:{cls.source.file}:{cls.name}"
        block = _tactical_block(cls, kind, self._text(cls))
        if block is not None:
            return self.practice.add(block, node_id, cls.source.file, cls.source.start_line, cls.source.end_line)
        node = self.practice.add_named(kind, node_id, cls.name, cls.source)
        node.data.update(cls.facts)
        return node

    def _associate(self, cls: Node) -> None:
        """An entity root names each other root it holds a reference to with a ``// foreign Name`` comment."""
        for other in re.findall(_FOREIGN_KEY, self._text(cls)):
            if other in self._blocks and other != cls.name:
                self.practice.link("associates", self._blocks[cls.name], self._blocks[other], "relationship")

    def _text(self, cls: Node) -> str:
        file = cls.source.file
        if file not in self._texts:
            path = self.root / file
            self._texts[file] = path.read_text(encoding="utf-8") if path.is_file() else ""
        return self._texts[file]


def _tactical_block(cls: Node, kind: str, text: str):
    """The DDD building block for a class, with its tactical facts loaded; none when DDD has no block for its kind."""
    from cdd_guidance.practices.ddd.model.nodes import DomainService, Entity, Factory, Repository, Specification, ValueObject

    block_types = {
        "EntityRoot": Entity,
        "Entity": Entity,
        "ValueObject": ValueObject,
        "Repository": Repository,
        "DomainService": DomainService,
        "Factory": Factory,
        "Specification": Specification,
    }
    block_type = block_types.get(kind)
    if block_type is None:
        return None
    block = block_type(name=cls.name, sequential_order=1)
    block.type = kind
    block.is_root = kind == "EntityRoot"
    block.load_tactical_facts(cls, text)
    return block


def _bounded_contexts(root: Path) -> list[tuple]:
    """Each folder that holds ``.context/bounded-context.md`` is a bounded context, read by the DDD model: the folder,
    the context, and its file."""
    from cdd_guidance.practices.ddd.model.nodes import BoundedContext

    found = []
    for dirpath, dirnames, _filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if not skips_folder(name)]
        marker = Path(dirpath) / ".context" / "bounded-context.md"
        if not marker.is_file():
            continue
        folder = Path(dirpath)
        context = BoundedContext(sequential_order=1)
        context.load_context_folder(folder)
        found.append(("." if folder == root else folder.relative_to(root).as_posix(), context, marker.relative_to(root).as_posix()))
    return sorted(found, key=lambda item: item[0])


def _unmarked_context(root: Path):
    """The one bounded context of a folder where no folder marks a context: the whole folder."""
    from cdd_guidance.practices.ddd.model.nodes import BoundedContext

    context = BoundedContext("bounded context", 1)
    context.load_folder_facts(root)
    return context


def _context_for(folder: str, contexts: dict[str, Node]) -> Node | None:
    """The innermost bounded context whose folder holds folder; the whole folder's context when one marks it."""
    best = ""
    for candidate in contexts:
        if candidate == "." or folder == candidate or folder.startswith(candidate + "/"):
            if candidate == "." or len(candidate) > len(best):
                best = candidate
    return contexts.get(best) or contexts.get(".")


GraphPractices.register(DddGraph("ddd", _PACKAGE))
