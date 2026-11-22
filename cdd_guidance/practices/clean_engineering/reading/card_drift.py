"""Where a module's card no longer says what its code does: a seam term no class or function of the module declares, a
dependency the code does not import or that is no folder at all, and a module the code imports that the card does not
name. A card that names a removed class or a dependency the code dropped sends callers to code that is gone."""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING

from cdd_guidance.practices.clean_engineering.model.base_class_model import MODULE_FUNCTION_HOLDER
from cdd_guidance.practices.clean_engineering.reading.code_read import DESCRIBED_FACT
from cdd_guidance.practices.clean_engineering.reading.folder_facts import ModuleImports, folders_of, is_under, record_fact

if TYPE_CHECKING:
    from harness.graph.graph import Node, PracticeNodes

# The fact each module keeps: each thing its card says that its code does not, as the kind and the name.
CARD_DRIFT = "card_drift"
SEAM_TERM_MISSING = "seam term no class declares"
DEPENDENCY_NOT_IMPORTED = "dependency not imported"
DEPENDENCY_NOT_A_FOLDER = "dependency no folder"
IMPORT_NOT_ON_CARD = "import not on the card"
# A seam term the code must declare: one class or function name, `CodeIndex`; a phrase or a lower-case word may be a
# concept the card explains, which only a reader can match to the code.
_CLASS_NAME = re.compile(r"^[A-Z][A-Za-z0-9]*[a-z][A-Za-z0-9]*$")
# A folder path a dependency names: words joined by slashes, `harness/graph`.
_FOLDER_PATH = re.compile(r"(?<![\w@./-])([A-Za-z_][\w-]*(?:/[\w-]+)+)/?")
_WORD = re.compile(r"^[A-Za-z_][\w-]*$")


class CardDrift:
    """Each module's card compared with the module's code (``card_drift``): its seam terms with the classes and
    functions the module's folder and the folders inside it declare, and the dependencies it names with the modules the
    module imports (``imported_modules``)."""

    def __init__(self, in_graph: "PracticeNodes") -> None:
        self._root = Path(in_graph.source_root) if in_graph.source_root else None
        self._modules = [module for module in in_graph.nodes("Module") if module.get_fact("has_module_context")]
        self._folders = {folder.source.file: folder for folder in folders_of(in_graph) if folder.source.file}
        # Each class and each function outside a class the code declares, with its file.
        self._declared: list[tuple[str, str]] = []
        self._declare(in_graph)

    def _declare(self, in_graph: "PracticeNodes") -> None:
        """Keep each class and each function outside a class the code declares, with its file."""
        classes = [node for node in in_graph.nodes("OoadClass") if not node.has_fact(DESCRIBED_FACT)]
        functions = [node for node in in_graph.nodes("Operation") if node.get_fact("owner") == MODULE_FUNCTION_HOLDER]
        self._declared = [(node.source.file or "", node.name) for node in classes + functions]

    def record(self) -> None:
        """Each module whose folders declare code. A module with none, such as one of documents alone or one still at
        the modules fidelity, whose card is written ahead of its code, has nothing to compare."""
        for module in self._modules:
            declared = {name for file, name in self._declared if is_under(file, module.source.file)}
            drift = self._drift(module, declared) if declared else []
            record_fact(module, CARD_DRIFT, drift)

    def _drift(self, module: "Node", declared: set[str]) -> list[list[str]]:
        """What the module's card says that its code, which declares the names declared, does not."""
        named = self._named_folders(module)
        return self._missing_terms(module, declared) + self._dependencies_drifted(module, named) + self._imports_unnamed(module, named)

    def _missing_terms(self, module: "Node", declared: set[str]) -> list[list[str]]:
        """Each seam term written as one class or function name that the module's code does not declare."""
        terms = [str(term).strip("`* ") for term in module.get_fact("card_seam_terms") or []]
        return [[SEAM_TERM_MISSING, term] for term in terms if _CLASS_NAME.match(term) and term not in declared]

    def _dependencies_drifted(self, module: "Node", named: list[tuple[str, list[str]]]) -> list[list[str]]:
        """Each dependency the card names that is no folder, or that the module's code does not import."""
        imported = self._imported(module)
        return [
            [DEPENDENCY_NOT_IMPORTED, token] if folders else [DEPENDENCY_NOT_A_FOLDER, token]
            for token, folders in named
            if not folders or not (self._covers(folders, module.source.file) or any(self._covers(folders, other) for other in imported))
        ]

    def _imports_unnamed(self, module: "Node", named: list[tuple[str, list[str]]]) -> list[list[str]]:
        """Each module the code imports that no dependency the card names stands for; none for a card that names no
        dependency, which says nothing to compare."""
        covered = [folder for _token, folders in named for folder in folders]
        return [[IMPORT_NOT_ON_CARD, other] for other in self._imported(module) if covered and not self._covers(covered, other)]

    def _imported(self, module: "Node") -> list[str]:
        return list(module.get_fact(ModuleImports.IMPORTED) or [])

    def _named_folders(self, module: "Node") -> list[tuple[str, list[str]]]:
        """Each folder a card's dependency names, with the folders of the code it stands for: a path from the source
        root or from the module's own folder, or a word that is the name of a folder the code holds. A path that is no
        folder or file stands for none; a word that names no folder may be prose, and is left out."""
        named: list[tuple[str, list[str]]] = []
        for term in module.get_fact("card_dependencies") or []:
            paths = [found.group(1) for found in _FOLDER_PATH.finditer(str(term))]
            named += [(token, self._folders_at(token) or self._folders_at(f"{module.source.file}/{token}")) for token in paths]
            named += [] if paths else self._word_named(str(term).strip("`* "))
        return named

    def _word_named(self, word: str) -> list[tuple[str, list[str]]]:
        """The folders a dependency written as one word names, by their last name; none for a word that is no folder."""
        folders = sorted(folder for folder in self._folders if folder.rsplit("/", 1)[-1] == word) if _WORD.match(word) else []
        return [(word, folders)] if folders else []

    def _folders_at(self, token: str) -> list[str]:
        """The folders of the code at or under token, or the folder holding the file token names; none when nothing
        is there."""
        under = [folder for folder in self._folders if is_under(folder, token)]
        if under:
            return under
        holder = token.rsplit("/", 1)[0]
        exists = self._root is not None and (self._root / token).exists()
        return [holder] if exists else []

    def _covers(self, folders: list[str], imported: str) -> bool:
        """True when one of folders is the module imported, inside it, or a folder that holds it."""
        return any(is_under(imported, folder) or is_under(folder, imported) for folder in folders)
