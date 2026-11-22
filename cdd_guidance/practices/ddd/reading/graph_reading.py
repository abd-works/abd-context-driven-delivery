"""How DDD takes part in the graph: its bounded contexts come from the folders that hold ``.context/bounded-context.md``,
its aggregates from the folders that hold domain classes, and its building blocks from the classes Clean Engineering
read from code, each seen through the DDD stereotype its declaration gives it, or, in a folder that holds a domain, its
name; and from the bounded-context map and each domain model document, the contexts, aggregates, classes, integrations
and events they describe. A class a document describes and the class in code that implements it are two nodes, joined
by an edge; a building block read from code is joined to the Clean Engineering class it is."""

from __future__ import annotations

import os
import posixpath
import re
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING

from harness.agent_tools.progress import report_progress
from harness.annotations.name import Name
from harness.graph.graph import Node, PracticeNodes
from harness.graph.saved_graph import NodeIdentity
from harness.graph.saved_graph import FactValue
from harness.graph.location import Location
from harness.graph.practice_reading import PracticeReading
from cdd_guidance.practices.clean_engineering.clean_engineering import CleanEngineering
from harness.markdown.markdown import MarkdownText
from harness.graph.model_node import schema_sync_paused
from harness.graph.skipped_folders import skips_folder

from cdd_guidance.practices.clean_engineering.reading.code_read import CODE_FIDELITY, DESCRIBED_FACT, MODEL_FIDELITY
from cdd_guidance.practices.clean_engineering.model import Relationship
from cdd_guidance.practices.clean_engineering.reading.card_lines import CardLines
from cdd_guidance.practices.source_code import is_test_code
from cdd_guidance.practices.ddd.model.markdown.nodes import MarkdownBoundedContextMap
from cdd_guidance.practices.ddd.model.building_blocks import DomainEvent
from cdd_guidance.practices.ddd.model.nodes import TARGET_SEGMENT, Aggregate, AggregateLink, BoundedContext, ContextMapping, Integration
from cdd_guidance.practices.ddd.model.stereotypes import BUILDING_BLOCK_KINDS, KIND_OF_STEREOTYPE, TacticalClass, kind_named_by, marks_another_system, root_kept_by

if TYPE_CHECKING:
    from harness.guidance.guidance import PracticeGuidance

    from cdd_guidance.practices.clean_engineering.model import OoadClass

# DDD's code fidelity, which a building block whose class has a body is read at.
TACTICS_FIDELITY = "tactics"
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
# The words a document's name holds when it is a domain model, written with a hyphen or an underscore.
DOMAIN_MODEL_NAMES = ("domain-model", "domain_model")
# The words a document's name holds when it is the bounded-context map.
CONTEXT_MAP_NAMES = ("bounded-context-map", "bounded_context_map")
# What a doc comment or a comment line opens with in Python or TypeScript, before the words it writes.
_COMMENT_MARKS = "*#/ \t"
_CONTEXT_FOLDER = ".context"
# The parts a mapping's side writes when it names the context before the aggregate: `Catalogue · Book`.
_PLACED_SIDE_PARTS = 2
# A run of the characters a class name is spelled with: a member's type names a class when its name is one whole run.
_TYPE_WORD = re.compile(r"[A-Za-z0-9_]+")


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
        super().__init__(practice, NodeIdentity(type=kind, node_id="", name=oclass.name), oclass.source)
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

    def get_fact(self, key: str, default: FactValue = None) -> FactValue:
        """This building block's fact, else the class's own, else the nearest DDD node around it."""
        if not super().has_fact(key) and self.ooad_class.has_fact(key):
            return self.ooad_class.get_fact(key, default)
        return super().get_fact(key, default)

    @property
    def _public_operations(self) -> list:
        return [op for op in self.ooad_class.operations if op.name and not op.name.startswith("_")]


class DddReading(PracticeReading):
    """How DDD takes part in the graph: it reads, after the Clean Engineering practice it extends, the bounded contexts
    its folders mark, the aggregates its folders hold, a building block for each class Clean Engineering read from
    code, and the aggregates its domain model documents describe; and it checks its own graph rules with Clean
    Engineering's."""

    reads_after = (CleanEngineering,)
    class_types = (*BUILDING_BLOCK_KINDS, "Aggregate", "DomainEvent")

    @property
    def root(self) -> Path:
        """The folder the practice reads its bounded contexts and aggregates from."""
        return Path(self.in_graph.source_root)

    def reads_model_document(self, file: Path) -> bool:
        """A domain model in a ``.context`` folder, ``domain-model.md``, which DDD reads in its own markdown format."""
        return self._is_context_document(file, DOMAIN_MODEL_NAMES)

    def describes_the_domain(self, file: Path) -> bool:
        """Whether file is a document DDD reads contexts and aggregates from: a domain model or the bounded-context
        map, in a ``.context`` folder."""
        return self._is_context_document(file, (*DOMAIN_MODEL_NAMES, *CONTEXT_MAP_NAMES))

    def _is_context_document(self, file: Path, words: tuple[str, ...]) -> bool:
        name = file.name.lower()
        return file.parent.name == _CONTEXT_FOLDER and file.suffix == ".md" and any(word in name for word in words)

    def own_graph_checks(self) -> dict:
        """DDD's own graph rules, then the rules of the practice it extends, whose part it holds."""
        extended = self.practice.working_set.extended
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
        extended = self.practice.working_set.extended
        clean = None if extended is None else self.graph.practices.loaded(type(extended))
        return _DomainClasses(clean.reading.in_graph if clean is not None else None)


class _DomainClasses:
    """The classes Clean Engineering read from code, seen by the folders that hold them: which folders hold a domain,
    which classes are building blocks, and which production classes are none. Without Clean Engineering open in the
    graph there are no classes; a folder where a class carries a DDD stereotype holds a domain. A class Clean
    Engineering read from its own model document is no building block: DDD reads the domain's design from its own
    domain model documents."""

    def __init__(self, classes: PracticeNodes | None) -> None:
        self._classes = classes
        # Clean Engineering's module or package node of each folder, read once when first asked for.
        self._folder_nodes: dict[Path, Node] | None = None
        every = [cls for cls in classes.nodes("OoadClass") if not cls.has_fact(DESCRIBED_FACT)] if classes is not None else []
        self._every = every
        self._names = {cls.name for cls in every}
        self._stereotyped_folders = {folder_of(cls.source.file) for cls in every if kind_named_by(cls.get_fact("stereotypes") or [])}

    def read_now(self) -> list[Node]:
        """The production classes Clean Engineering read in this pass: a class in a spec, a test folder, or test
        support is never a domain building block, whatever its name."""
        if self._classes is None:
            return []
        read_now = self._classes.nodes_read_now("OoadClass")
        return [cls for cls in read_now if not is_test_code(cls.source.file) and not cls.has_fact(DESCRIBED_FACT)]

    def holds_a_domain(self, folder: str) -> bool:
        return folder in self._stereotyped_folders

    def folder_node(self, folder: Path) -> Node | None:
        """The node Clean Engineering holds for folder: its Module when the folder has a module card, else its Package
        when it holds only source; none for a folder it read nothing from, or without Clean Engineering."""
        if self._classes is None:
            return None
        if self._folder_nodes is None:
            root = Path(self._classes.source_root).resolve()
            held = [node for kind in ("Package", "Module") for node in self._classes.nodes(kind)]
            self._folder_nodes = {(root / node.source.file).resolve(): node for node in held if node.source is not None and node.source.file}
        return self._folder_nodes.get(folder.resolve())

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


class _LinkedAggregates:
    """The aggregates each bounded context's own file names as links to their headings in a domain model. A link says
    which aggregate the context means by the heading it opens, so a context that writes links holds exactly the
    aggregates its links open, and a name its mappings write means the aggregate the link of that name opens. A
    context that names its aggregates in plain words writes none, and is read by name."""

    def __init__(self) -> None:
        # Each link with the context that writes it and the document it opens, named from the practice's root.
        self._written: list[tuple[Node, AggregateLink, str]] = []
        # The aggregate each link opens, by the context that writes it and the words the link shows.
        self._opened: dict[tuple[str, str], Node] = {}

    def add(self, context: Node, file: str, links: list[AggregateLink]) -> None:
        """Hold the links the context's file, at file from the practice's root, writes."""
        folder = folder_of(file)
        self._written.extend((context, link, posixpath.normpath(posixpath.join(folder, link.file))) for link in links)

    def written_by(self, context: Node) -> bool:
        return any(writer is context for writer, _link, _document in self._written)

    def opening(self, document: "_DomainDocument", start: int) -> tuple[Node, AggregateLink] | None:
        """The link that opens the heading at line start of document, with the context that writes it; none when no
        link does."""
        found = ((context, link) for context, link, opened in self._written if opened == document.relative and document.line_anchored(link.anchor) == start)
        return next(found, None)

    def hold(self, context: Node, link: AggregateLink, aggregate: Node) -> None:
        """Hold the aggregate read at the heading the context's link opens, under the words the link shows."""
        self._opened[(context.node_id, Name(link.name).snake)] = aggregate

    def aggregate_named(self, context: Node, name: str) -> Node | None:
        """The aggregate the context means by name: the one its link showing that name opens; none without such a link."""
        return self._opened.get((context.node_id, Name(name).snake))


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
        self._links = _LinkedAggregates()
        self._blocks = _AggregateBlocks(reading)

    def read(self) -> None:
        """Bounded contexts come from the folders that mark one, else from the headings of the documents that describe
        the domain, else the whole folder is one."""
        marked = self._bounded_contexts()
        described = _DescribedDomain(self._reading, self._contexts, self._documents(), self._links)
        self._read_contexts(marked)
        if not marked and not described.read_contexts():
            self._read_contexts([(".", self._unmarked_context(), ".")])
        for folder, held in sorted(self._members_by_folder(bool(marked)).items()):
            self._read_aggregate_folder(folder, held)
        described.read()
        self._link_blocks()
        self._map_contexts(marked)
        self._join_folders()

    def _join_folders(self) -> None:
        """Join each bounded context and each aggregate a folder holds to the Clean Engineering module or package of
        that folder (``isA``), as a building block is joined to its class: they are read from one folder and stay two
        nodes. One a document describes, which no folder holds, is joined to none."""
        for node in [*self._in_graph.nodes("BoundedContext"), *self._in_graph.nodes("Aggregate")]:
            folder = self._folder_held_by(node)
            held = self._domain.folder_node(folder) if folder is not None else None
            if held is not None:
                self._graph.edges.relate("isA", node, held)

    def _folder_held_by(self, node: Node) -> Path | None:
        """The folder a bounded context or an aggregate was read from: the folder its source names, or the one whose
        ``.context/bounded-context.md`` marks the context; none for one read from a document's heading."""
        named = self._root / node.source.file
        if named.is_dir():
            return named
        if named.is_file() and PurePosixPath(node.source.file).as_posix().endswith(BOUNDED_CONTEXT_MARKER.as_posix()):
            return named.parent.parent
        return None

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
        context.source_facts.load_folder(self._root)
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
            self._links.add(node, markdown, context.aggregate_links)

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

    def _documents(self) -> list["_DomainDocument"]:
        """Each document that describes the domain, in a ``.context`` folder under the practice's root: the domain
        models first, whose aggregates hold classes, then the bounded-context maps."""
        found = []
        for dirpath, dirnames, filenames in os.walk(self._root):
            dirnames[:] = [name for name in dirnames if not skips_folder(name) or name == _CONTEXT_FOLDER]
            found.extend(Path(dirpath) / name for name in filenames if self._reading.describes_the_domain(Path(dirpath) / name))
        models_first = sorted(found, key=lambda file: (not self._reading.reads_model_document(file), file))
        return [_DomainDocument(self._from_root(file), file.read_text(encoding="utf-8")) for file in models_first]

    def _aggregate(self, folder: str, members: list[tuple[TacticalClass, str]]) -> Node:
        context = self._contexts.around(folder) or self._in_graph.root
        aggregate = Aggregate(Path(folder).name, 1)
        aggregate.source_facts.load_folder(self._root / folder)
        node = self._in_graph.add(aggregate, self._aggregate_id(folder), Location(folder, 1, 1))
        self._graph.edges.link("owns", context, node)
        self._graph.edges.relate("belongsTo", node, context)
        for tactical, kind in members:
            source = tactical.oclass.source
            block = self._blocks.add(node, tactical, kind, Location(source.file, source.start_line, source.end_line))
            self._graph.edges.relate("isA", block, tactical.oclass)
        return node

    def _link_blocks(self) -> None:
        """Link the building blocks DDD holds, those read now and those it built before: each repository accesses the
        root its name says it keeps, and each entity root associates with every other root it holds a reference to,
        which it names with a ``// foreign Name`` comment or reaches by an integration its doc comment keeps. All read
        only a block's name, its file and its lines, which a block read back from a saved graph holds too, so a
        refreshed root is linked again to the blocks no file in the refresh holds. Of several blocks with one name,
        such as a root written in two languages, a block is linked to the one nearest it."""
        blocks = _NamedBlocks([node for node in self._in_graph.nodes() if node.type in _BLOCK_KINDS])
        for block in blocks.every:
            self._link_kept_root(block, blocks)
            self._link_foreign_roots(block, blocks)

    def _link_kept_root(self, block: Node, blocks: "_NamedBlocks") -> None:
        root = blocks.nearest(block, root_kept_by(block.name) or "") if block.type == "Repository" else None
        if root is not None:
            self._graph.edges.relate("accesses", block, root)

    def _link_foreign_roots(self, block: Node, blocks: "_NamedBlocks") -> None:
        if block.type != "EntityRoot":
            return
        reached = [(other, "") for other in _FOREIGN_KEY.findall(block.source.text)] + self._integrations_kept_by(block)
        for other, aggregate in reached:
            root = blocks.nearest(block, other, aggregate)
            if root is not None and root is not block:
                self._graph.edges.relate("associates", block, root)

    def _integrations_kept_by(self, block: Node) -> list[tuple[str, str]]:
        """Each integration the doc comment of a root's class keeps as a dependency with its target's parts under it
        (`---<<Customer/Supplier>>--> Book`, then `aggregate: Book`): the class it reaches, and the aggregate that
        holds that class. A block read now asks its class; a block read back from a saved graph holds only its lines,
        which write the same dependency."""
        if isinstance(block, BuildingBlock):
            dependencies = list(block.ooad_class.dependencies)
        else:
            lines = [line.strip().lstrip(_COMMENT_MARKS).rstrip('"').strip() for line in block.source.text.splitlines()]
            dependencies = Relationship.read_lines(lines)
        kept = [item for item in dependencies if any(item.details.get(part) for part in Integration.PARTS)]
        return [(item.details.get("entity") or item.target, item.details.get("aggregate", "")) for item in kept]

    def _map_contexts(self, marked: list[tuple[str, BoundedContext, str]]) -> None:
        """Each context mapping a bounded context's file lists, under that context, and linked to the aggregates its two
        sides name. A refresh reads every context's file again, so the mappings of a graph opened from its save are the
        ones its files list now."""
        aggregates: dict[str, Node] = {}
        every = self._in_graph.nodes("Aggregate")
        for aggregate in sorted(every, key=lambda node: node.source.file.endswith(".md")):
            aggregates.setdefault(Name(aggregate.name).snake, aggregate)
        for rel, context, markdown in marked:
            for mapping in context.mappings:
                node = self._mapping_node(mapping, self._contexts.at(rel), markdown)
                self._link_sides(node, mapping, self._contexts.at(rel), aggregates)

    def _mapping_node(self, mapping: ContextMapping, context: Node, markdown: str) -> Node:
        """The mapping on the graph, under its context, at the line of the context's file that lists it."""
        line = mapping.sequential_order
        node = self._in_graph.add(mapping, f"ddd:ContextMapping:{markdown}:{line}", Location(markdown, line, line))
        self._graph.edges.link("mappedTo", context, node)
        return node

    def _link_sides(self, node: Node, mapping: ContextMapping, context: Node, aggregates: dict[str, Node]) -> None:
        """Each side to the aggregate it names. Where the context a side speaks of links its aggregates, the side means
        the aggregate the link of that name opens. Else it means the aggregate of that name, whichever case the side
        and the aggregate's folder spell it in: a map writes `Cart` and the folder that holds the aggregate is `cart`,
        and a folder's aggregate comes before one a document describes."""
        for side, name in mapping.aggregate_names.items():
            spoken_of = self._context_a_side_names(getattr(mapping, side)) or context
            aggregate = self._links.aggregate_named(spoken_of, name) or aggregates.get(Name(name).snake)
            if aggregate is not None:
                self._graph.edges.relate(side, node, aggregate)

    def _context_a_side_names(self, written: str) -> Node | None:
        """The bounded context a mapping's side names before its aggregate (`Catalogue · Book`); none for a side that
        names its aggregate alone, which speaks of the context that lists the mapping."""
        parts = [part.strip() for part in TARGET_SEGMENT.split(written)]
        if len(parts) < _PLACED_SIDE_PARTS:
            return None
        return next((node for node in self._in_graph.nodes("BoundedContext") if node.name == parts[-_PLACED_SIDE_PARTS]), None)

    def _from_root(self, path: Path) -> str:
        """path as a path from the practice's root, with forward slashes."""
        return path.relative_to(self._root).as_posix()

    def _aggregate_id(self, folder: str) -> str:
        """The graph's id of the aggregate a folder holds."""
        return f"ddd:Aggregate:{folder}"


def folder_of(file: str) -> str:
    """The folder that holds file, from the practice's root, with forward slashes: `.` for a file at the root."""
    return str(PurePosixPath(file.replace("\\", "/")).parent)


class _AggregateBlocks:
    """The building blocks of the aggregates in DDD's part of the graph, each added under its aggregate."""

    def __init__(self, reading: DddReading) -> None:
        self._reading = reading

    def add(self, aggregate: Node, tactical: TacticalClass, kind: str, location: Location) -> Node:
        """The building block a class is, at location, in the aggregate: its root, or one of its parts."""
        block = BuildingBlock(self._reading.practice, tactical, kind)
        added = self._reading.in_graph.add(block, f"ddd:{kind}:{location.file}:{tactical.oclass.name}", location)
        # The fidelity goes by what the class holds, in any format: tactics once one of its operations has a body, as
        # Clean Engineering read it at code, else the model, so a rule only tactics holds leaves a class with no bodies out.
        added.read_at(TACTICS_FIDELITY if tactical.oclass.is_read_at(CODE_FIDELITY) else MODEL_FIDELITY)
        self._reading.graph.edges.link("root" if kind == "EntityRoot" else "owns", aggregate, added)
        self._reading.graph.edges.relate("belongsTo", added, aggregate)
        return added


class _NamedBlocks:
    """Building blocks by name, several to a name when a class is written in two languages or described in a document
    as well as declared in code."""

    def __init__(self, blocks: list[Node]) -> None:
        self.every = blocks
        self._named: dict[str, list[Node]] = {}
        for block in blocks:
            self._named.setdefault(block.name, []).append(block)

    def nearest(self, block: Node, name: str, aggregate: str = "") -> Node | None:
        """The block called name nearest block: in the folder aggregate names when one is given and some block is
        there, then in block's own file, else written in its language, else in its folder; none when no block is
        called name. A block a document describes is near only another block of a document, and code only code."""
        described = block.has_fact(DESCRIBED_FACT)
        named = [other for other in self._named.get(name, []) if other.has_fact(DESCRIBED_FACT) == described]
        placed = [other for other in named if aggregate and Name(Path(folder_of(other.source.file)).name).snake == Name(aggregate).snake]
        return min(placed or named, key=lambda other: self._distance(block, other), default=None)

    def _distance(self, block: Node, other: Node) -> tuple[bool, bool, bool]:
        file, other_file = block.source.file, other.source.file
        return (other_file != file, Path(other_file).suffix != Path(file).suffix, folder_of(other_file) != folder_of(file))


class _DomainDocument:
    """One document that describes the domain, a domain model or the bounded-context map: where it is from the
    practice's root, the map DDD's markdown format reads from it, and the lines its headings and entries sit on."""

    def __init__(self, relative: str, text: str) -> None:
        self.relative = relative
        self.cards = CardLines(text)
        self.map = MarkdownBoundedContextMap().parse(text)
        self._lines = text.splitlines()
        self._text = MarkdownText(text)

    def context_lines(self, name: str) -> tuple[int, int]:
        """The first and last line of the bounded context called name: its `## Name | owner` heading through the line
        before the next `## ` heading; the document's first line when no heading names it."""
        headings = [number for number, line in enumerate(self._lines, start=1) if line.startswith("## ")]
        start = next((number for number in headings if self._lines[number - 1][3:].split("|", 1)[0].strip() == name), None)
        if start is None:
            return (1, 1)
        return (start, next((number - 1 for number in headings if number > start), len(self._lines)))

    def aggregate_lines(self, name: str) -> tuple[int, int]:
        return self.cards.section_of(name) or (1, 1)

    def line_anchored(self, anchor: str) -> int | None:
        """The line of the heading a link names by anchor, as the Files app opens it; none when no heading has it."""
        found = self._text.anchored_lines(anchor)
        return found[0] if found is not None else None

    def line_of(self, entry: str, within: tuple[int, int]) -> int:
        """The first line within the lines given that opens with entry, once its indent is gone; else their first."""
        first, last = within
        found = (number for number in range(first, last + 1) if self._lines[number - 1].strip().startswith(entry))
        return next(found, first)

    @property
    def last_line(self) -> int:
        return max(1, len(self._lines))


class _DescribedDomain:
    """What the documents under the practice's root describe, read into DDD's part of the graph: the bounded contexts
    they head, each aggregate once, under its context, with a building block for each class a domain model draws, the
    context mappings their integrations write, the events their event maps list, and the edges between them. A block a
    document describes stays beside the block code declares, and the code's block is joined to it."""

    def __init__(self, reading: DddReading, contexts: _ContextFolders, documents: list[_DomainDocument], links: _LinkedAggregates) -> None:
        self._reading = reading
        self._in_graph = reading.in_graph
        self._edges = reading.graph.edges
        self._contexts = contexts
        self._documents = documents
        self._links = links
        self._blocks = _AggregateBlocks(reading)
        # Each aggregate described, by its context's name and its own, and the root block a domain model draws for it.
        self._aggregates: dict[tuple[str, str], Node] = {}
        self._roots: dict[tuple[str, str], Node] = {}
        # Each building block described, with its aggregate's name and the class names its card relates it to.
        self._described: list[tuple[Node, str, set[str]]] = []

    def read_contexts(self) -> bool:
        """Hold each bounded context the documents head, once, at the first heading that names it, and known by the
        folder its name spells, so code in that folder sits under it; whether the documents head any."""
        seen: set[str] = set()
        for document in self._documents:
            for described in document.map.every_context:
                if described.name not in seen:
                    seen.add(described.name)
                    self._read_context(document, described)
        return bool(seen)

    def _read_context(self, document: _DomainDocument, described: BoundedContext) -> None:
        context = BoundedContext(described.name, described.sequential_order)
        context.owner = described.owner
        location = Location(document.relative, *document.context_lines(described.name))
        node = self._in_graph.add(context, f"ddd:BoundedContext:{document.relative}:{described.name}", location)
        self._edges.link("owns", self._in_graph.root, node)
        self._contexts.add(Name(described.name).snake, node)

    def read(self) -> None:
        """Once the contexts and the code's aggregates are read: the aggregates the documents describe, then the edges
        between what they describe, and from the code that implements it."""
        for document in self._documents:
            for described in document.map.every_aggregate:
                key = (described.parent.name, described.name)
                if key not in self._aggregates:
                    self._aggregates[key] = self._read_aggregate(document, described)
        self._relate_blocks()
        for document in self._documents:
            self._read_integrations(document)
            self._read_events(document)
        self._join_implementations()

    def _context_of(self, document: _DomainDocument, name: str) -> Node:
        """The bounded context an aggregate no context's file links sits under: the one called name, unless its file
        links its aggregates, which then leaves this one out; else the one around the folder the document describes,
        else the root."""
        named = next((node for node in self._in_graph.nodes("BoundedContext") if node.name == name and not self._links.written_by(node)), None)
        return named or self._contexts.around(folder_of(folder_of(document.relative))) or self._in_graph.root

    def _read_aggregate(self, document: _DomainDocument, described: Aggregate) -> Node:
        """The aggregate at the document's section for it, under the bounded context whose own file links that section,
        else under the context its heading names, holding a building block for each class the document draws in it,
        each at its card and marked as described by the document."""
        start, end = document.aggregate_lines(described.name)
        linked = self._links.opening(document, start)
        context = linked[0] if linked is not None else self._context_of(document, described.parent.name)
        node = self._in_graph.add(Aggregate(described.name, 1), f"ddd:Aggregate:{document.relative}:{described.name}", Location(document.relative, start, end))
        if linked is not None:
            self._links.hold(*linked, node)
        self._edges.link("owns", context, node)
        self._edges.relate("belongsTo", node, context)
        names = [oclass.name for oclass in described.classes]
        for oclass in described.classes:
            tactical = TacticalClass(oclass)
            kind = tactical.inferred_kind(names)
            if kind is not None:
                self._read_block(document, node, tactical, kind, (described.parent.name, described.name))
        return node

    def _read_block(self, document: _DomainDocument, aggregate: Node, tactical: TacticalClass, kind: str, key: tuple[str, str]) -> None:
        oclass = tactical.oclass
        document.cards.place(oclass)
        start = aggregate.source.start_line
        block = self._blocks.add(aggregate, tactical, kind, Location(document.relative, oclass.line or start, oclass.end_line or start))
        block.set_fact(DESCRIBED_FACT, True)
        self._described.append((block, key[1], self._named_in_card(oclass)))
        if kind == "EntityRoot":
            self._roots[key] = block

    def _named_in_card(self, oclass: OoadClass) -> set[str]:
        """The class names a card relates its class to: each whole word of its properties' types, a collection's
        included, and of what its operations return, the classes its operations call, and the classes it extends."""
        hints = [member.type_hint for member in oclass.properties if getattr(member, "type_hint", "")]
        hints += [operation.return_type for operation in oclass.operations if operation.return_type]
        called = {callee.strip().partition(".")[0].partition("(")[0].strip() for operation in oclass.operations for callee in operation.callees}
        return {word for hint in hints for word in _TYPE_WORD.findall(hint)} | called | set(oclass.bases)

    def _relate_blocks(self) -> None:
        """Each building block a document describes depends on every other described block its card relates it to, as
        a class read from code depends on each class its properties' types name: the classes it composes, aggregates,
        or associates with, the classes its other members are typed by, the classes its operations call, and the
        classes it extends. They are linked once every document is read, so a card can name a class in another
        aggregate."""
        by_name = {block.name: block for block, _aggregate, _names in self._described}
        for block, _aggregate, names in self._described:
            for name in sorted(names):
                other = by_name.get(name)
                if other is not None and other is not block:
                    self._edges.relate("dependsOn", block, other)

    def _read_integrations(self, document: _DomainDocument) -> None:
        """Each integration the document writes under an aggregate, as a context mapping from that aggregate to the
        aggregate it reaches, once for the two; and the root of the first associates with the root of the second."""
        for described in document.map.every_aggregate:
            local = (described.parent.name, described.name)
            for integration in described.integrations:
                target = document.map.aggregate_reached_by(integration)
                remote = (target.parent.name, target.name) if target is not None else None
                if remote in self._aggregates and remote != local:
                    self._read_mapping(document, local, remote, integration)

    def _read_mapping(self, document: _DomainDocument, local: tuple[str, str], remote: tuple[str, str], integration: Integration) -> None:
        mapping = ContextMapping(" · ".join(local), " · ".join(remote), pattern=integration.pattern)
        entry = f"- {integration.target}"
        line = document.line_of(entry, document.aggregate_lines(local[1]))
        if any(self._reaches(node, local, remote) for node in self._in_graph.nodes("ContextMapping")):
            return
        node = self._in_graph.add(mapping, f"ddd:ContextMapping:{document.relative}:{line}", Location(document.relative, line, line))
        self._edges.link("mappedTo", self._edges.direct_parent(self._aggregates[local]) or self._in_graph.root, node)
        self._edges.relate("local", node, self._aggregates[local])
        self._edges.relate("remote", node, self._aggregates[remote])
        if local in self._roots and remote in self._roots:
            self._edges.relate("associates", self._roots[local], self._roots[remote])

    def _reaches(self, mapping: Node, local: tuple[str, str], remote: tuple[str, str]) -> bool:
        """Whether a mapping already held joins the two described aggregates."""
        sides = [[edge.child for edge in self._edges.from_parent(side, mapping)] for side in ("local", "remote")]
        return sides == [[self._aggregates[local]], [self._aggregates[remote]]]

    def _read_events(self, document: _DomainDocument) -> None:
        """Each event the document's aggregates emit, once, under the aggregate that emits it, with that aggregate as
        its producer and each aggregate its event map says consumes it as a consumer."""
        for described in document.map.every_aggregate:
            producer = self._aggregates[(described.parent.name, described.name)]
            for event in described.events:
                self._read_event(document, producer, event)

    def _read_event(self, document: _DomainDocument, producer: Node, event: DomainEvent) -> None:
        line = document.line_of(f"- {event.name}:", (1, document.last_line))
        node = self._in_graph.add(DomainEvent(event.name, 1), f"ddd:DomainEvent:{document.relative}:{event.name}", Location(document.relative, line, line))
        self._edges.link("owns", producer, node)
        self._edges.relate("belongsTo", node, producer)
        self._edges.relate("producer", node, producer)
        consumers = {consumer.name for consumer in event.consumers}
        for (_context, name), aggregate in self._aggregates.items():
            if name in consumers:
                self._edges.relate("consumers", node, aggregate)

    def _join_implementations(self) -> None:
        """Join each building block code declares to the described block it implements: the block of the same name in
        the aggregate the code's folder names, as generate saves an aggregate's code in a folder named for it."""
        declared = [node for node in self._in_graph.nodes() if node.type in _BLOCK_KINDS and not node.has_fact(DESCRIBED_FACT)]
        for block, aggregate, _names in self._described:
            folder = Name(aggregate).snake
            for code in declared:
                if code.name == block.name and Name(Path(folder_of(code.source.file)).name).snake == folder:
                    self._edges.relate("implements", code, block)
