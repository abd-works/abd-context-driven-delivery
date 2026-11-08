"""How DDD takes part in the graph: its bounded contexts come from the folders that hold ``.context/bounded-context.md``,
its aggregates from the folders that hold domain classes, and its building blocks from the classes Clean Engineering
read, each seen through the DDD stereotype its declaration or name gives it."""

from __future__ import annotations

import os
import re
from pathlib import Path

from harness.graph.graph import Node
from harness.guidance.guidance import PracticeGuidance
from harness.graph.model_node import schema_sync_paused
from harness.graph.skipped_folders import skips_folder

from cdd_guidance.practices.ddd.model.nodes import Aggregate, BoundedContext
from cdd_guidance.practices.ddd.model.stereotypes import TacticalClass

# A helper class in a test folder is never a domain aggregate, whatever its name suggests.
_TEST_FOLDERS = ("tests/", "test-utils/")
_FOREIGN_KEY = re.compile(r"//\s*foreign\s+(\w+)")
_DERIVE_PREFIX = re.compile(r"^derive\w*", re.IGNORECASE)
_ONLY_DELEGATES = re.compile(r"return\s+\w+\.\w+\s*\(")
_LOAD_NAMES = frozenset({"load", "get", "find", "fetch"})
# A load with no identity is fine when it returns the one record its store holds; it is wrong when it finds the
# identity in ambient state (the session, the request, a cookie, the signed-in user, the browser).
_AMBIENT_STATE = re.compile(
    r"(?<![A-Za-z])(?:[Ss]ession|[Cc]urrent|[Rr]eq(?:uest)?|[Cc]ookies?|[Aa]uth|[Ll]ogged|[Cc]tx|[Cc]ontext"
    r"|localStorage|sessionStorage|window|process\.env)(?![a-z])"
)
_REPOSITORY_LIFECYCLE = re.compile(r"^(?:add|remove|delete|find|get|load|save|store|fetch|by_id|find_by)", re.IGNORECASE)
_UI_METHODS = frozenset({"open", "isshowing", "close", "show", "hide", "select"})
_SCREEN_NAME = re.compile(r"^(Select|Screen|Dialog|Modal|View|Page)\w*$")


class BuildingBlock(Node):
    """A class Clean Engineering read, seen as the DDD building block its stereotypes or its name make it. It holds
    that class rather than a copy of it: the class's own facts are the class's, and the tactical facts DDD's rules read
    are this block's, worked out from the class's operations."""

    graph_facts = (
        "peer_private_operations",
        "public_derive_operations",
        "delegating_operations",
        "identity_free_loads",
        "tactical_stereotype",
        "named_for_its_kind",
        "public_operation_names",
        "lifecycle_operations",
        "drives_a_screen",
        "in_screen_module",
    )

    def __init__(self, practice, tactical: TacticalClass, kind: str) -> None:
        oclass = tactical.oclass
        super().__init__(practice, kind, "", oclass.name, oclass.source)
        self.tactical = tactical

    @property
    def ooad_class(self):
        """The class Clean Engineering read, which this building block is."""
        return self.tactical.oclass

    @property
    def peer_private_operations(self) -> list[str]:
        return [op.name for op in self.ooad_class.operations if op.peer_private_access]

    @property
    def public_derive_operations(self) -> list[str]:
        return [op.name for op in self._public_operations if _DERIVE_PREFIX.match(op.name)]

    @property
    def delegating_operations(self) -> list[str]:
        return [op.name for op in self._public_operations if _ONLY_DELEGATES.search(op.body.text)]

    @property
    def identity_free_loads(self) -> list[str]:
        """Each load, get, find, or fetch with no parameter that finds its identity in ambient state."""
        return [
            op.name
            for op in self.ooad_class.operations
            if op.name.lower() in _LOAD_NAMES and not op.parameters and _AMBIENT_STATE.search(op.body.text)
        ]

    @property
    def tactical_stereotype(self) -> bool:
        """Whether the class carries a DDD stereotype, or its name says the building block it is."""
        return self.tactical.declares_stereotype(self.type)

    @property
    def named_for_its_kind(self) -> bool:
        """Whether the class's name follows the naming convention of the building block it is."""
        return self.tactical.name_says(self.type)

    @property
    def public_operation_names(self) -> list[str]:
        return [op.name for op in self._public_operations]

    @property
    def lifecycle_operations(self) -> list[str]:
        """The public operations that add to, find in, or remove from a collection."""
        return [name for name in self.public_operation_names if _REPOSITORY_LIFECYCLE.search(name)]

    @property
    def drives_a_screen(self) -> bool:
        """Whether the class behaves like a screen: it opens and shows, or its name is a screen's."""
        public = {name.lower() for name in self.public_operation_names}
        return bool(public & _UI_METHODS and ("open" in public or "isshowing" in public)) or bool(_SCREEN_NAME.search(self.name))

    @property
    def in_screen_module(self) -> bool:
        """Whether the class sits in a React screen module, which is not a DDD building block in code."""
        return (self.source.file or "").replace("\\", "/").lower().endswith(".tsx")

    @property
    def foreign_names(self) -> list[str]:
        """The other roots the class names with a ``// foreign Name`` comment in its own lines."""
        return _FOREIGN_KEY.findall(self.ooad_class.source.text)

    @property
    def facts(self) -> dict:
        """The class's own facts, then this building block's."""
        return {**self.ooad_class.facts, **super().facts}

    def has_fact(self, key: str) -> bool:
        return super().has_fact(key) or self.ooad_class.has_fact(key)

    def get_fact(self, key: str, default=None):
        """This building block's fact, else the class's own, else the nearest DDD node around it."""
        if not super().has_fact(key) and self.ooad_class.has_fact(key):
            return self.ooad_class.get_fact(key, default)
        return super().get_fact(key, default)

    @property
    def _public_operations(self) -> list:
        return [op for op in self.ooad_class.operations if op.name and not op.name.startswith("_")]


class DddReading:
    """One read of a working copy into the graph that holds the DDD practice: the bounded contexts its folders mark,
    the aggregates its folders hold, and a building block for each class the Clean Engineering practice it extends
    read."""

    def __init__(self, practice: PracticeGuidance) -> None:
        self.practice = practice
        self.graph = practice.graph
        self.root = Path(practice.in_graph.source_root)
        self._blocks: dict[str, BuildingBlock] = {}

    def read(self) -> None:
        """Read the practice's folder; a folder not written yet, such as a session's code root, holds no contexts."""
        if not self.root.is_dir():
            return
        with schema_sync_paused():
            self.graph.report_progress("ddd · bounded contexts")
            contexts = self._contexts()
            for folder, members in sorted(self._members_by_folder().items()):
                self._aggregate(folder, members, _context_for(folder, contexts) or self.practice.in_graph.root)

    def _contexts(self) -> dict[str, Node]:
        """Each bounded context by its folder, under the context of the folder around it."""
        found = self._bounded_contexts() or [(".", self._unmarked_context(), ".")]
        contexts: dict[str, Node] = {}
        for rel, context, markdown in found:
            node = self.practice.in_graph.add(context, f"ddd:BoundedContext:{rel}:{context.name}", markdown, 1, context.context_file_lines)
            parent = _context_for(str(Path(rel).parent).replace("\\", "/"), contexts) if rel != "." else None
            self.graph.link("owns", parent or self.practice.in_graph.root, node)
            if parent is not None:
                self.graph.link("belongsTo", node, parent, "relationship")
            contexts[rel] = node
        return contexts

    def _bounded_contexts(self) -> list[tuple]:
        """Each folder that holds ``.context/bounded-context.md`` is a bounded context, read by the DDD model: the
        folder, the context, and its file."""
        found = []
        for dirpath, dirnames, _filenames in os.walk(self.root):
            dirnames[:] = [name for name in dirnames if not skips_folder(name)]
            marker = Path(dirpath) / ".context" / "bounded-context.md"
            if not marker.is_file():
                continue
            folder = Path(dirpath)
            context = BoundedContext(sequential_order=1, graph=self.graph)
            context.load_context_folder(folder)
            found.append(("." if folder == self.root else folder.relative_to(self.root).as_posix(), context, marker.relative_to(self.root).as_posix()))
        return sorted(found, key=lambda item: item[0])

    def _unmarked_context(self) -> BoundedContext:
        """The one bounded context of a folder where no folder marks a context: the whole folder."""
        context = BoundedContext("bounded context", 1, graph=self.graph)
        context.load_folder_facts(self.root)
        return context

    def _members_by_folder(self) -> dict[str, list[tuple[TacticalClass, str]]]:
        """The classes the Clean Engineering practice read that DDD names a building block, by folder, each with its
        kind."""
        clean = self.practice.extended
        classes = clean.in_graph.nodes("OoadClass") if clean is not None else []
        names = {cls.name for cls in classes}
        members: dict[str, list[tuple[TacticalClass, str]]] = {}
        for cls in classes:
            folder = str(Path(cls.source.file).parent).replace("\\", "/")
            tactical = TacticalClass(cls)
            kind = tactical.inferred_kind(names)
            if kind is not None and not f"{folder}/".startswith(_TEST_FOLDERS):
                members.setdefault(folder, []).append((tactical, kind))
        return members

    def _aggregate(self, folder: str, members: list[tuple[TacticalClass, str]], context: Node) -> None:
        aggregate = Aggregate(Path(folder).name, 1, graph=self.graph)
        aggregate.load_folder_facts(self.root / folder)
        node = self.practice.in_graph.add(aggregate, f"ddd:Aggregate:{folder}", folder, 1, 1)
        self.graph.link("owns", context, node)
        self.graph.link("belongsTo", node, context, "relationship")
        blocks = [(self._block(node, tactical, kind), kind) for tactical, kind in members]
        for block, kind in blocks:
            if kind == "EntityRoot" and isinstance(block, BuildingBlock):
                self._associate(block)

    def _block(self, aggregate: Node, tactical: TacticalClass, kind: str) -> Node:
        source = tactical.oclass.source
        block = self.practice.in_graph.add(BuildingBlock(self.practice, tactical, kind), f"ddd:{kind}:{source.file}:{tactical.oclass.name}", source.file, source.start_line, source.end_line)
        self._blocks[tactical.oclass.name] = block
        self.graph.link("root" if kind == "EntityRoot" else "owns", aggregate, block)
        self.graph.link("belongsTo", block, aggregate, "relationship")
        root = self._blocks.get(tactical.kept_root_name) if kind == "Repository" else None
        if root is not None:
            self.graph.link("accesses", block, root, "relationship")
        return block

    def _associate(self, block: BuildingBlock) -> None:
        """An entity root names each other root it holds a reference to with a ``// foreign Name`` comment."""
        for other in block.foreign_names:
            if other in self._blocks and other != block.name:
                self.graph.link("associates", block, self._blocks[other], "relationship")


def _context_for(folder: str, contexts: dict[str, Node]) -> Node | None:
    """The innermost bounded context whose folder holds folder; the whole folder's context when one marks it."""
    best = ""
    for candidate in contexts:
        if candidate == "." or folder == candidate or folder.startswith(candidate + "/"):
            if candidate == "." or len(candidate) > len(best):
                best = candidate
    return contexts.get(best) or contexts.get(".")
