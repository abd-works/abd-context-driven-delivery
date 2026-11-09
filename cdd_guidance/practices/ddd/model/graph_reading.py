"""How DDD takes part in the graph: its bounded contexts come from the folders that hold ``.context/bounded-context.md``,
its aggregates from the folders that hold domain classes, and its building blocks from the classes Clean Engineering
read, each seen through the DDD stereotype its declaration gives it, or, in a folder that holds a domain, its name."""

from __future__ import annotations

import os
import re
from pathlib import Path, PurePosixPath

from harness.graph.graph import Node
from harness.guidance.guidance import PracticeGuidance
from harness.graph.model_node import schema_sync_paused
from harness.graph.skipped_folders import skips_folder

from cdd_guidance.practices.clean_engineering.model.production_code import is_test_code
from cdd_guidance.practices.ddd.model.nodes import Aggregate, BoundedContext
from cdd_guidance.practices.ddd.model.stereotypes import KIND_OF_STEREOTYPE, TacticalClass, kind_named_by, marks_another_system, root_kept_by

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
# Every kind of building block a class can be, by its stereotype or its name.
_BLOCK_KINDS = frozenset(kind for _stereotype, kind in KIND_OF_STEREOTYPE)
# A React screen module, whose classes present the domain rather than belong to it.
_SCREEN_MODULE = ".tsx"


class BuildingBlock(Node):
    """A class Clean Engineering read, seen as the DDD building block its stereotypes or its name make it. It holds
    that class rather than a copy of it: the class's own facts are the class's, and the tactical facts DDD's rules read
    are this block's, worked out from the class's operations."""

    graph_facts = (
        "peer_private_operations",
        "public_derive_operations",
        "delegating_operations",
        "identity_free_loads",
        "named_for_its_kind",
        "public_operation_names",
        "lifecycle_operations",
        "drives_a_screen",
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

    def read(self) -> None:
        """Read the practice's folder; a folder not written yet, such as a session's code root, holds no contexts."""
        if not self.root.is_dir():
            return
        with schema_sync_paused():
            self.graph.report_progress("ddd · bounded contexts")
            marked = self._bounded_contexts()
            contexts = self._contexts(marked)
            members = self._members_by_folder(contexts if marked else {})
            for folder, held in sorted(members.items()):
                context = _context_for(folder, contexts) or self.practice.in_graph.root
                aggregate = self._aggregate(folder, held, context) if held else self.practice.in_graph.node(_aggregate_id(folder))
                if aggregate is not None:
                    held_classes = self.practice.extended.in_graph.nodes("OoadClass")
                    aggregate.set_fact("bare_classes", _bare_classes(folder, self.practice.in_graph.nodes(), held_classes))
            self._link_blocks()

    def _contexts(self, marked: list[tuple]) -> dict[str, Node]:
        """Each bounded context by its folder, under the context of the folder around it: the marked ones, else the
        whole folder's."""
        found = marked or [(".", self._unmarked_context(), ".")]
        contexts: dict[str, Node] = {}
        for rel, context, markdown in found:
            node = self.practice.in_graph.add(context, f"ddd:BoundedContext:{rel}:{context.name}", markdown, 1, context.context_file_lines)
            parent = _context_for(_folder_of(rel), contexts) if rel != "." else None
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
            context = BoundedContext(sequential_order=1)
            context.load_context_folder(folder)
            found.append(("." if folder == self.root else folder.relative_to(self.root).as_posix(), context, marker.relative_to(self.root).as_posix()))
        return sorted(found, key=lambda item: item[0])

    def _unmarked_context(self) -> BoundedContext:
        """The one bounded context of a folder where no folder marks a context: the whole folder."""
        context = BoundedContext("bounded context", 1)
        context.load_folder_facts(self.root)
        return context

    def _members_by_folder(self, marked_contexts: dict[str, Node]) -> dict[str, list[tuple[TacticalClass, str]]]:
        """The production classes the Clean Engineering practice read now, by folder, each building block among them
        with its kind; a folder whose classes read now are none of them holds an empty list. A class's DDD stereotype
        always names its kind. Its name names one only in a folder that holds a domain: one a marked bounded context
        covers (one of marked_contexts), or one where a class carries a DDD stereotype; elsewhere a name such as
        `AgentOperation` or `MarkdownRepository` says nothing about the business. A refresh reads only the files it
        names, and the building blocks of every other class stay as DDD built them before; whether a folder holds a
        domain, and which root a repository names, both read every class Clean Engineering holds, restored ones too,
        so a root is named by its repository whichever file holds the repository."""
        clean = self.practice.extended
        if clean is None:
            return {}
        every = clean.in_graph.nodes("OoadClass")
        names = {cls.name for cls in every}
        modelled = _modelled_folders(every)
        members: dict[str, list[tuple[TacticalClass, str]]] = {}
        for cls in clean.in_graph.nodes_read_now("OoadClass"):
            # A class in a spec, a test folder, or test support is never a domain building block, whatever its name.
            if is_test_code(cls.source.file):
                continue
            folder = _folder_of(cls.source.file)
            block = _block_of(TacticalClass(cls), names, folder in modelled or _context_for(folder, marked_contexts) is not None)
            members.setdefault(folder, []).extend([block] if block else [])
        return members

    def _aggregate(self, folder: str, members: list[tuple[TacticalClass, str]], context: Node) -> Node:
        aggregate = Aggregate(Path(folder).name, 1)
        aggregate.load_folder_facts(self.root / folder)
        node = self.practice.in_graph.add(aggregate, _aggregate_id(folder), folder, 1, 1)
        self.graph.link("owns", context, node)
        self.graph.link("belongsTo", node, context, "relationship")
        for tactical, kind in members:
            self._block(node, tactical, kind)
        return node

    def _block(self, aggregate: Node, tactical: TacticalClass, kind: str) -> None:
        source = tactical.oclass.source
        block = self.practice.in_graph.add(BuildingBlock(self.practice, tactical, kind), f"ddd:{kind}:{source.file}:{tactical.oclass.name}", source.file, source.start_line, source.end_line)
        self.graph.link("root" if kind == "EntityRoot" else "owns", aggregate, block)
        self.graph.link("belongsTo", block, aggregate, "relationship")

    def _link_blocks(self) -> None:
        """Link the building blocks DDD holds, those read now and those it built before: each repository accesses the
        root its name says it keeps, and each entity root associates with every other root it holds a reference to,
        which it names with a ``// foreign Name`` comment. Both read only a block's name and its lines, which a block
        read back from a saved graph holds too, so a refreshed root is linked again to the blocks no file in the
        refresh holds."""
        blocks = [node for node in self.practice.in_graph.nodes() if node.type in _BLOCK_KINDS]
        by_name = {block.name: block for block in blocks}
        for block in blocks:
            if block.type == "Repository":
                root = by_name.get(root_kept_by(block.name) or "")
                if root is not None:
                    self.graph.link("accesses", block, root, "relationship")
            elif block.type == "EntityRoot":
                for other in _FOREIGN_KEY.findall(block.source.text):
                    if other in by_name and other != block.name:
                        self.graph.link("associates", block, by_name[other], "relationship")


def _bare_classes(folder: str, ddd_nodes: list[Node], classes: list[Node]) -> list[str]:
    """The production classes in folder that are no building block DDD holds there: the classes its aggregate's rule
    reports, by name. Sorted, so a refresh that restores some classes and reads others gives the fact a fresh build
    gives."""
    blocks = {block.name for block in ddd_nodes if block.type in _BLOCK_KINDS and _folder_of(block.source.file) == folder}
    return sorted(cls.name for cls in classes if _folder_of(cls.source.file) == folder and cls.name not in blocks and _is_domain_class(cls))


def _modelled_folders(classes: list[Node]) -> set[str]:
    """The folders where a class carries a DDD stereotype, which says the folder holds a domain."""
    return {_folder_of(cls.source.file) for cls in classes if kind_named_by(cls.get_fact("stereotypes") or [])}


def _block_of(tactical: TacticalClass, names: set[str], in_domain: bool) -> tuple[TacticalClass, str] | None:
    """The class with the building-block kind it is: its stereotype's, or in a folder that holds a domain the one
    its name says; none for a class that is no building block."""
    kind = tactical.inferred_kind(names) if in_domain else tactical.kind()
    return (tactical, kind) if kind is not None else None


def _is_domain_class(cls: Node) -> bool:
    """A production class of the domain: not a private one (`_module`, which holds a file's functions, or a helper
    named with `_`), not test code, not a React screen module's, and not one marked as another system's."""
    file = cls.source.file
    return not (
        cls.name.startswith("_") or is_test_code(file) or file.lower().endswith(_SCREEN_MODULE) or marks_another_system(cls.get_fact("stereotypes") or [])
    )


def _folder_of(file: str) -> str:
    """The folder that holds file, from the practice's root, with forward slashes: `.` for a file at the root."""
    return str(PurePosixPath(file.replace("\\", "/")).parent)


def _aggregate_id(folder: str) -> str:
    """The graph's id of the aggregate a folder holds."""
    return f"ddd:Aggregate:{folder}"


def _context_for(folder: str, contexts: dict[str, Node]) -> Node | None:
    """The innermost bounded context whose folder holds folder; the whole folder's context when one marks it."""
    best = ""
    for candidate in contexts:
        if candidate == "." or folder == candidate or folder.startswith(candidate + "/"):
            if candidate == "." or len(candidate) > len(best):
                best = candidate
    return contexts.get(best) or contexts.get(".")
