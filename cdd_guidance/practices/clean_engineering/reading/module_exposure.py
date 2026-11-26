"""How much of each module's whole subtree leaves it: the class definitions code outside the subtree names, registers,
or publishes, and the operations of its classes, public and private, and those on the classes that leave it."""

from __future__ import annotations

from typing import TYPE_CHECKING

from cdd_guidance.practices.clean_engineering.model.base_class_model import MODULE_FUNCTION_HOLDER
from cdd_guidance.practices.clean_engineering.reading.folder_facts import folders_of
from cdd_guidance.practices.clean_engineering.measures.read_facts import is_under
from cdd_guidance.practices.clean_engineering.reading.imported_classes import ImportedClasses
from cdd_guidance.practices.clean_engineering.reading.operation_counts import operation_count
from cdd_guidance.practices.clean_engineering.reading.public_routes import NAMED, PublicRoutes
from cdd_guidance.practices.source_code import ClassReference

if TYPE_CHECKING:
    from harness.graph.graph import Node, PracticeNodes

    from cdd_guidance.practices.clean_engineering.reading.production_classes import ProductionClasses


class ModuleExposure:
    """What of each module's whole subtree leaves it. A module is measured over its own files, its packages, and the
    modules nested in it; each nested module is measured again over its own subtree.

    A class definition is public for a module when it leaves the subtree by a route: ``named``, when production code
    outside the subtree imports it or reaches it as ``module.Class``, each import resolved to the definition it names
    (*ImportedClasses*), so a class that shares its name with another is public only when that one definition is
    named; ``registered``, when a package registers it with a framework registry; or ``published``, when the installer
    publishes it as a toolset (*PublicRoutes*). Each module keeps the count of the production class definitions in its
    subtree (``subtree_class_count``), the public ones, each as ``file:Name`` with the routes that reach it
    (``public_classes``), and how many are public and private (``public_class_count``, ``private_class_count``). A
    private record, such as a parser's ``_Section``, is neither seam nor hidden design, so it is not counted; a name
    starting with ``_`` is never public; tests, test support, examples, and test doubles (the reading's ``test_code``) neither
    count nor name a class.

    Beside the classes it keeps their operations (*OperationCount*), the module functions of its production files
    included: every one (``operations_total``), those public by their visibility and the private rest
    (``operations_public``, ``operations_private``), and the public ones on its public classes, which is what the module
    exposes to other modules (``seam_operations``). A constructor counts in the total and the private, never in the
    seam."""

    def __init__(self, in_graph: "PracticeNodes", classes: "ProductionClasses", routes: PublicRoutes) -> None:
        self._in_graph = in_graph
        self._classes = classes
        self._routes = routes
        self._test_code = in_graph.practice.reading.test_code

    def record(self) -> None:
        counted = [
            each.node
            for each in self._classes
            if not self._test_code.is_example_code(each.file) and not (each.name.startswith("_") and not each.has_behavior)
        ]
        holders = [
            node
            for node in self._in_graph.nodes("OoadClass")
            if node.name == MODULE_FUNCTION_HOLDER and not self._test_code.is_example_code(node.source.file)
        ]
        namers = ClassNamers(self._in_graph, [each.node for each in self._classes]).by_class()
        for module in self._in_graph.nodes("Module"):
            folder = module.source.file or ""
            inside = [node for node in counted if is_under(node.source.file, folder)]
            public = {node.node_id: self._public_routes(node, folder, namers) for node in inside}
            public = {node_id: routes for node_id, routes in public.items() if routes}
            module.set_facts(self._facts(inside, public, [node for node in holders if is_under(node.source.file, folder)]))

    def _facts(self, inside: list["Node"], public: dict[str, dict], functions: list["Node"]) -> dict:
        counts = {node.node_id: operation_count(node) for node in [*inside, *functions]}
        total = sum(count.total for count in counts.values())
        visible = sum(count.public for count in counts.values())
        return {
            "subtree_class_count": len(inside),
            "public_classes": dict(sorted((f"{node.source.file}:{node.name}", public[node.node_id]) for node in inside if node.node_id in public)),
            "public_class_count": len(public),
            "private_class_count": len(inside) - len(public),
            "operations_total": total,
            "operations_public": visible,
            "operations_private": total - visible,
            "seam_operations": sum(counts[node_id].public for node_id in public),
        }

    def _public_routes(self, node: "Node", folder: str, namers: dict[str, set[str]]) -> dict:
        """The routes by which the class node leaves the module at folder; none for a class that stays inside."""
        if node.name.startswith("_"):
            return {}
        routes: dict = self._routes.of(node, self._classes.operations_of(node))
        outside = sorted(namer for namer in namers.get(node.node_id, set()) if not is_under(namer, folder))
        if outside:
            routes = {NAMED: outside, **routes}
        return routes


class ClassNamers:
    """The folders whose production code names each class definition: what each folder's files import, which the read
    kept on the folder by file (``imported_classes_by_file``), and what the files outside an edited-file scope import,
    which it kept on the practice's root with the module that holds each (``imported_classes_outside``), each resolved
    to the definition it names."""

    def __init__(self, in_graph: "PracticeNodes", classes: list["Node"]) -> None:
        self._in_graph = in_graph
        self._classes = classes
        self._test_code = in_graph.practice.reading.test_code

    def by_class(self) -> dict[str, set[str]]:
        """The folders that name each class definition, by its node id."""
        references, namer_of = self._references()
        resolved = ImportedClasses(self._classes, references)
        namers: dict[str, set[str]] = {}
        for file, made in references.items():
            for reference in made:
                found = resolved.resolve(reference, file)
                if found is not None:
                    namers.setdefault(found.node_id, set()).add(namer_of[file])
        return namers

    def _references(self) -> tuple[dict[str, list[ClassReference]], dict[str, str]]:
        """The classes each production file names, by its path, and the folder each file names them for."""
        references: dict[str, list[ClassReference]] = {}
        namer_of: dict[str, str] = {}
        for folder in folders_of(self._in_graph):
            by_file = folder.get_fact("imported_classes_by_file") if folder.has_fact("imported_classes_by_file") else {}
            for file, made in by_file.items():
                if not self._test_code.is_example_code(file):
                    references[file] = [ClassReference(*item) for item in made]
                    namer_of[file] = folder.source.file or ""
        root = self._in_graph.root
        outside = root.get_fact("imported_classes_outside") if root.has_fact("imported_classes_outside") else {}
        for file, kept in outside.items():
            if self._test_code.is_example_code(file):
                continue
            references[file] = [ClassReference(*item) for item in kept["classes"]]
            namer_of[file] = kept["module"]
        return references, namer_of
