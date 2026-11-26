"""Which class definition each class reference names: the class of that name in the file its module is, or, when that
file re-exports the name, the class the re-export names in turn. A module named from the source root (`a.b`, `'a/b'`)
is looked for there first, then under each folder above the file that names it, as an import root such as a fixture's
folder or a package folder on the import path would make it. A script's import of a generated language adapter
(`@cdd/...`) names the Python class the adapter is generated from."""

from __future__ import annotations

from typing import TYPE_CHECKING, Iterable, Optional

from cdd_guidance.practices.source_code import STAR, ClassReference

if TYPE_CHECKING:
    from harness.graph.graph import Node


class ImportedClasses:
    """The class definitions references resolve to. It holds the classes by the file that defines each and its name,
    and the references each production file makes by the file's path, through which a package's ``__init__.py`` or a
    script's ``index.ts`` re-exports a class it imports. A reference to a module outside the source root, a name the
    module defines as no class, or a star import names no class of ours, so it resolves to none."""

    def __init__(self, classes: Iterable["Node"], references: dict[str, list[ClassReference]]) -> None:
        self._defined = {(node.source.file, node.name): node for node in classes}
        self._references = references

    def resolve(self, reference: ClassReference, importer: str) -> Optional["Node"]:
        """The class definition reference, made by the file at importer, names; none when it names no class of ours."""
        if reference.name == STAR:
            return None
        for name in reference.names():
            found = self._resolved(reference._replace(name=name), importer, set())
            if found is not None:
                return found
        return None

    def _resolved(self, reference: ClassReference, importer: str, seen: set[str]) -> Optional["Node"]:
        for file in self._files_of(reference, importer):
            found = self._defined.get((file, reference.name)) or self._re_exported(file, reference.name, seen)
            if found is not None:
                return found
        return None

    def _files_of(self, reference: ClassReference, importer: str) -> list[str]:
        """The files the module reference names it from may be: from the source root, then under each folder above
        importer, from the top down."""
        folders = importer.split("/")[:-1]
        roots = [""] + ["/".join(folders[: depth + 1]) + "/" for depth in range(len(folders))]
        return [f"{root}{file}" for root in roots for file in reference.files()]

    def _re_exported(self, file: str, name: str, seen: set[str]) -> Optional["Node"]:
        """The class file passes on as name: one it imports or re-exports by that name, or through a star import; each
        file is followed once, so a cycle of re-exports ends."""
        if file in seen or file not in self._references:
            return None
        seen.add(file)
        for passed in self._references[file]:
            if passed.name in (name, STAR):
                found = self._resolved(ClassReference(passed.source, name), file, seen)
                if found is not None:
                    return found
        return None
