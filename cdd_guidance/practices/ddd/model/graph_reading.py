"""How DDD takes part in the graph: its bounded contexts come from the folders that hold ``.context/bounded-context.md``,
its aggregates from the folders that hold domain classes, and its building blocks from the classes Clean Engineering
read, each seen through the DDD stereotype its declaration gives it, or, in a folder that holds a domain, its name."""

from __future__ import annotations

import os
import re
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING

from harness.agent_tools.progress import report_progress
from harness.graph.graph import Node, PracticeNodes
from harness.graph.location import Location
from harness.guidance.practice_reading import PracticeReading
from harness.graph.model_node import schema_sync_paused
from harness.graph.skipped_folders import skips_folder

from cdd_guidance.practices.clean_engineering.model.production_code import is_test_code
from cdd_guidance.practices.ddd.model.nodes import Aggregate, BoundedContext, ContextMapping
from cdd_guidance.practices.ddd.model.stereotypes import BUILDING_BLOCK_KINDS, KIND_OF_STEREOTYPE, TacticalClass, kind_named_by, marks_another_system, root_kept_by

if TYPE_CHECKING:
    from harness.guidance.guidance import PracticeGuidance

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
# The file whose folder is a bounded context: the folder holding .context/bounded-context.md.
BOUNDED_CONTEXT_MARKER = Path(".context") / "bounded-context.md"


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

    def __init__(self, practice: PracticeGuidance, tactical: TacticalClass, kind: str) -> None:
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

    def get_fact(self, key: str, default: object = None) -> object:
        """This building block's fact, else the class's own, else the nearest DDD node around it."""
        if not super().has_fact(key) and self.ooad_class.has_fact(key):
            return self.ooad_class.get_fact(key, default)
        return super().get_fact(key, default)

    @property
    def _public_operations(self) -> list:
        return [op for op in self.ooad_class.operations if op.name and not op.name.startswith("_")]


class DddReading(PracticeReading):
    """How DDD takes part in the graph: it reads, after the Clean Engineering practice it extends, the bounded contexts
    its folders mark, the aggregates its folders hold, and a building block for each class Clean Engineering read; and
    it checks its own graph rules with Clean Engineering's."""

    reads_after = ("clean_engineering",)
    class_types = (*BUILDING_BLOCK_KINDS, "Aggregate", "DomainEvent")

    @property
    def root(self) -> Path:
        """The folder the practice reads its bounded contexts and aggregates from."""
        return Path(self.in_graph.source_root)

    def own_graph_checks(self) -> dict:
        """DDD's own graph rules, then the rules of the practice it extends, whose part it holds."""
        extended = self.practice.extended
        return {**super().own_graph_checks(), **(extended.reading.graph_checks if extended is not None else {})}

    def read_working_copy(self) -> None:
        """Read the practice's folder; a folder not written yet, such as a session's code root, holds no contexts.
        Bounded contexts come from the folders that hold ``.context/bounded-context.md``, aggregates from the folders
        that hold domain classes, and building blocks from the classes Clean Engineering read, each seen through the DDD
        stereotype its declaration or name gives it."""
        if not self.root.is_dir():
            return
        with schema_sync_paused():
            report_progress("ddd · bounded contexts")
            _WorkingCopyRead(self, self._domain_classes).read()

    @property
    def _domain_classes(self) -> "_DomainClasses":
        """The classes the Clean Engineering practice DDD builds its building blocks from, when this graph holds it open;
        none in a graph without it, such as a session that works on DDD with Clean Engineering turned off."""
        extended = self.practice.extended
        clean = None if extended is None else self.graph.practices.loaded(type(extended))
        return _DomainClasses(clean.reading.in_graph if clean is not None else None)


class _DomainClasses:
    """The classes Clean Engineering read, seen by the folders that hold them: which folders hold a domain, which classes
    are building blocks, and which production classes are none. Without Clean Engineering open in the graph there are
    no classes; a folder where a class carries a DDD stereotype holds a domain."""

    def __init__(self, classes: PracticeNodes | None) -> None:
        self._classes = classes
        every = classes.nodes("OoadClass") if classes is not None else []
        self._every = every
        self._names = {cls.name for cls in every}
        self._stereotyped_folders = {folder_of(cls.source.file) for cls in every if kind_named_by(cls.get_fact("stereotypes") or [])}

    def read_now(self) -> list[Node]:
        """The production classes Clean Engineering read in this pass: a class in a spec, a test folder, or test
        support is never a domain building block, whatever its name."""
        if self._classes is None:
            return []
        return [cls for cls in self._classes.nodes_read_now("OoadClass") if not is_test_code(cls.source.file)]

    def holds_a_domain(self, folder: str) -> bool:
        return folder in self._stereotyped_folders

    def block_of(self, tactical: TacticalClass, in_domain: bool) -> tuple[TacticalClass, str] | None:
        """The class with the building-block kind it is: its stereotype's, or in a folder that holds a domain the one
        its name says, reading every class Clean Engineering holds so a root is named by its repository whichever file
        holds the repository; none for a class that is no building block."""
        kind = tactical.inferred_kind(self._names) if in_domain else tactical.kind()
        return (tactical, kind) if kind is not None else None

    def bare_in(self, folder: str, ddd_nodes: list[Node]) -> list[str]:
        """The production classes in folder that are no building block DDD holds there: the classes its aggregate's rule
        reports, by name. Sorted, so a refresh that restores some classes and reads others gives the fact a fresh build
        gives."""
        blocks = {block.name for block in ddd_nodes if block.type in _BLOCK_KINDS and folder_of(block.source.file) == folder}
        return sorted(cls.name for cls in self._every if folder_of(cls.source.file) == folder and cls.name not in blocks and self._is_domain_class(cls))

    def _is_domain_class(self, cls: Node) -> bool:
        """A production class of the domain: not a private one (`_module`, which holds a file's functions, or a helper
        named with `_`), not test code, not a React screen module's, and not one marked as another system's."""
        file = cls.source.file
        return not (
            cls.name.startswith("_") or is_test_code(file) or file.lower().endswith(_SCREEN_MODULE) or marks_another_system(cls.get_fact("stereotypes") or [])
        )


class _ContextFolders:
    """The bounded contexts read so far, each by the folder that holds it, from the practice's root: `.` for the whole
    folder's."""

    def __init__(self) -> None:
        self._by_folder: dict[str, Node] = {}

    def add(self, folder: str, context: Node) -> None:
        self._by_folder[folder] = context

    def at(self, folder: str) -> Node:
        return self._by_folder[folder]

    def around(self, folder: str) -> Node | None:
        """The innermost bounded context whose folder holds folder; the whole folder's context when one marks it."""
        holding = [candidate for candidate in self._by_folder if candidate == "." or folder == candidate or folder.startswith(candidate + "/")]
        innermost = max(holding, key=lambda candidate: 0 if candidate == "." else len(candidate), default="")
        return self._by_folder.get(innermost) or self._by_folder.get(".")


class _WorkingCopyRead:
    """One read of the practice's folder into its part of the graph: the bounded contexts its folders mark, the
    aggregates its folders hold with their building blocks, the links between the blocks, and each context mapping."""

    def __init__(self, reading: DddReading, domain: _DomainClasses) -> None:
        self._reading = reading
        self._graph = reading.graph
        self._in_graph = reading.in_graph
        self._root = reading.root
        self._domain = domain
        self._contexts = _ContextFolders()

    def read(self) -> None:
        marked = self._bounded_contexts()
        self._read_contexts(marked or [(".", self._unmarked_context(), ".")])
        for folder, held in sorted(self._members_by_folder(bool(marked)).items()):
            self._read_aggregate_folder(folder, held)
        self._link_blocks()
        self._map_contexts(marked)

    def _bounded_contexts(self) -> list[tuple[str, BoundedContext, str]]:
        """Each folder that holds ``.context/bounded-context.md`` is a bounded context, read by the DDD model: the
        folder, the context, and its file."""
        found = []
        for dirpath, dirnames, _filenames in os.walk(self._root):
            dirnames[:] = [name for name in dirnames if not skips_folder(name)]
            marker = Path(dirpath) / BOUNDED_CONTEXT_MARKER
            if marker.is_file():
                found.append(self._bounded_context(Path(dirpath), marker))
        return sorted(found, key=lambda item: item[0])

    def _bounded_context(self, folder: Path, marker: Path) -> tuple[str, BoundedContext, str]:
        context = BoundedContext(sequential_order=1)
        context.load_context_folder(folder)
        return ("." if folder == self._root else self._from_root(folder), context, self._from_root(marker))

    def _unmarked_context(self) -> BoundedContext:
        """The one bounded context of a folder where no folder marks a context: the whole folder."""
        context = BoundedContext("bounded context", 1)
        context.load_folder_facts(self._root)
        return context

    def _read_contexts(self, found: list[tuple[str, BoundedContext, str]]) -> None:
        """Each bounded context by its folder, under the context of the folder around it."""
        for rel, context, markdown in found:
            node = self._in_graph.add(context, f"ddd:BoundedContext:{rel}:{context.name}", Location(markdown, 1, context.context_file_lines))
            parent = self._contexts.around(folder_of(rel)) if rel != "." else None
            self._graph.edges.link("owns", parent or self._in_graph.root, node)
            if parent is not None:
                self._graph.edges.relate("belongsTo", node, parent)
            self._contexts.add(rel, node)

    def _members_by_folder(self, marked: bool) -> dict[str, list[tuple[TacticalClass, str]]]:
        """The production classes the Clean Engineering practice read now, by folder, each building block among them
        with its kind; a folder whose classes read now are none of them holds an empty list. A class's DDD stereotype
        always names its kind. Its name names one only in a folder that holds a domain: one a marked bounded context
        covers, or one where a class carries a DDD stereotype; elsewhere a name such as `AgentOperation` or
        `MarkdownRepository` says nothing about the business. A refresh reads only the files it names, and the building
        blocks of every other class stay as DDD built them before."""
        members: dict[str, list[tuple[TacticalClass, str]]] = {}
        for cls in self._domain.read_now():
            folder = folder_of(cls.source.file)
            in_domain = self._domain.holds_a_domain(folder) or (marked and self._contexts.around(folder) is not None)
            block = self._domain.block_of(TacticalClass(cls), in_domain)
            members.setdefault(folder, []).extend([block] if block else [])
        return members

    def _read_aggregate_folder(self, folder: str, held: list[tuple[TacticalClass, str]]) -> None:
        """The aggregate a folder holds, made from its building blocks when it holds some, and the production classes in
        it that are none."""
        aggregate = self._aggregate(folder, held) if held else self._in_graph.node(self._aggregate_id(folder))
        if aggregate is not None:
            aggregate.set_fact("bare_classes", self._domain.bare_in(folder, self._in_graph.nodes()))

    def _aggregate(self, folder: str, members: list[tuple[TacticalClass, str]]) -> Node:
        context = self._contexts.around(folder) or self._in_graph.root
        aggregate = Aggregate(Path(folder).name, 1)
        aggregate.load_folder_facts(self._root / folder)
        node = self._in_graph.add(aggregate, self._aggregate_id(folder), Location(folder, 1, 1))
        self._graph.edges.link("owns", context, node)
        self._graph.edges.relate("belongsTo", node, context)
        for tactical, kind in members:
            self._block(node, tactical, kind)
        return node

    def _block(self, aggregate: Node, tactical: TacticalClass, kind: str) -> None:
        source = tactical.oclass.source
        block = self._in_graph.add(BuildingBlock(self._reading.practice, tactical, kind), f"ddd:{kind}:{source.file}:{tactical.oclass.name}", Location(source.file, source.start_line, source.end_line))
        self._graph.edges.link("root" if kind == "EntityRoot" else "owns", aggregate, block)
        self._graph.edges.relate("belongsTo", block, aggregate)

    def _link_blocks(self) -> None:
        """Link the building blocks DDD holds, those read now and those it built before: each repository accesses the
        root its name says it keeps, and each entity root associates with every other root it holds a reference to,
        which it names with a ``// foreign Name`` comment. Both read only a block's name and its lines, which a block
        read back from a saved graph holds too, so a refreshed root is linked again to the blocks no file in the
        refresh holds."""
        blocks = [node for node in self._in_graph.nodes() if node.type in _BLOCK_KINDS]
        by_name = {block.name: block for block in blocks}
        for block in blocks:
            self._link_kept_root(block, by_name)
            self._link_foreign_roots(block, by_name)

    def _link_kept_root(self, block: Node, by_name: dict[str, Node]) -> None:
        root = by_name.get(root_kept_by(block.name) or "") if block.type == "Repository" else None
        if root is not None:
            self._graph.edges.relate("accesses", block, root)

    def _link_foreign_roots(self, block: Node, by_name: dict[str, Node]) -> None:
        if block.type != "EntityRoot":
            return
        for other in _FOREIGN_KEY.findall(block.source.text):
            if other in by_name and other != block.name:
                self._graph.edges.relate("associates", block, by_name[other])

    def _map_contexts(self, marked: list[tuple[str, BoundedContext, str]]) -> None:
        """Each context mapping a bounded context's file lists, under that context, and linked to the aggregates its two
        sides name. A refresh reads every context's file again, so the mappings of a graph opened from its save are the
        ones its files list now."""
        aggregates: dict[str, Node] = {}
        for aggregate in self._in_graph.nodes("Aggregate"):
            aggregates.setdefault(aggregate.name, aggregate)
        for rel, context, markdown in marked:
            for mapping in context.mappings:
                node = self._mapping_node(mapping, self._contexts.at(rel), markdown)
                self._link_sides(node, mapping, aggregates)

    def _mapping_node(self, mapping: ContextMapping, context: Node, markdown: str) -> Node:
        """The mapping on the graph, under its context, at the line of the context's file that lists it."""
        line = mapping.sequential_order
        node = self._in_graph.add(mapping, f"ddd:ContextMapping:{markdown}:{line}", Location(markdown, line, line))
        self._graph.edges.link("mappedTo", context, node)
        return node

    def _link_sides(self, node: Node, mapping: ContextMapping, aggregates: dict[str, Node]) -> None:
        for side, name in mapping.aggregate_names.items():
            if name in aggregates:
                self._graph.edges.relate(side, node, aggregates[name])

    def _from_root(self, path: Path) -> str:
        """path as a path from the practice's root, with forward slashes."""
        return path.relative_to(self._root).as_posix()

    def _aggregate_id(self, folder: str) -> str:
        """The graph's id of the aggregate a folder holds."""
        return f"ddd:Aggregate:{folder}"


def folder_of(file: str) -> str:
    """The folder that holds file, from the practice's root, with forward slashes: `.` for a file at the root."""
    return str(PurePosixPath(file.replace("\\", "/")).parent)
