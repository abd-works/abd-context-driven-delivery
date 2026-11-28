"""ProjectGuidelines: the guidelines one project works with, the patterns CDD ships and those the project keeps in its own
folder, each left out when the project's ``.context/config.json`` disables it."""
from __future__ import annotations

import hashlib
import importlib
import importlib.machinery
import sys
import threading
import types
from pathlib import Path
from typing import Iterable

from harness.installation.context_config import ContextConfig

DISABLED = "disabled"
# The prefix of the package each project's guidelines folder is imported as, followed by a digest of the folder's path.
PACKAGE_PREFIX = "cdd_project_guidelines_"
# The folder a project's own guideline installs under, the one CDD's shipped patterns install under
# (``cdd_guidance/patterns``), so its skill and rules sit beside theirs.
INSTALLED_UNDER = "patterns"


def guideline_name(toolset_class: type) -> str:
    """The guideline a toolset class is, such as ``lern_domain_driven``: its ``pattern``; empty for a class that is no
    guideline, as most toolsets are."""
    return str(getattr(toolset_class, "pattern", "") or "").strip()


class GuidelinesFolder:
    """The folder a project keeps its own guidelines in, each a subfolder laid out like a pattern CDD ships
    (``<name>/<name>.py`` defining the class whose ``pattern`` is ``name``, ``<name>.md``, ``practices/``,
    ``templates/``). The folder is imported as a package of its own, named from its path, so two projects' guidelines
    never share a module, and a pattern's rules are imported from its folder by package name, as a shipped pattern's
    are."""

    def __init__(self, folder: Path) -> None:
        self.folder = folder.resolve()
        self.package = PACKAGE_PREFIX + hashlib.sha1(str(self.folder).casefold().encode("utf-8")).hexdigest()[:12]
        self._classes: list[type] | None = None
        self._lock = threading.Lock()

    @property
    def classes(self) -> list[type]:
        """The guideline class each subfolder's module of the same name defines, in folder name order, each imported once
        while the process runs; a subfolder with no such module, such as one that holds only what its guidelines share,
        gives none."""
        with self._lock:
            if self._classes is None:
                self._classes = self._imported()
            return list(self._classes)

    def _imported(self) -> list[type]:
        if not self.folder.is_dir():
            return []
        self.ensure_package()
        found: list[type] = []
        for entry in sorted(self.folder.iterdir()):
            if not entry.is_dir() or entry.name.startswith((".", "_")) or not (entry / f"{entry.name}.py").is_file():
                continue
            module = importlib.import_module(f"{self.package}.{entry.name}.{entry.name}")
            found += [value for value in vars(module).values() if isinstance(value, type) and value.__module__ == module.__name__ and guideline_name(value) == entry.name]
        return found

    def ensure_package(self) -> str:
        """Make the folder importable as its package, the first time it is asked, and answer the package's name: a graph
        build's worker process asks before it imports the modules its order names."""
        if self.package not in sys.modules:
            spec = importlib.machinery.ModuleSpec(self.package, None, is_package=True)
            spec.submodule_search_locations = [str(self.folder)]
            package = types.ModuleType(self.package)
            package.__spec__ = spec
            package.__path__ = [str(self.folder)]
            package.__package__ = self.package
            sys.modules[self.package] = package
        return self.package


class ProjectGuidelines:
    """The guidelines one project works with, as its ``.context/config.json`` says: ``guidelines`` marks each
    ``enabled`` or ``disabled``, and ``guidelines_folder`` names a folder of the project holding guidelines of its own.
    A disabled guideline is left out wherever guidelines are listed, applied, chosen, or installed, so a project can
    switch off a pattern CDD ships and switch on its own copy; one the project names neither way stays in. Each project
    is read for itself: the cdd server answers several projects, and one project's guidelines never reach another's."""

    FOLDER_KEY = "guidelines_folder"

    def __init__(self, root: Path | str, held: HeldProjectGuidelines) -> None:
        self.config = ContextConfig(root)
        self._held = held

    @property
    def root(self) -> Path:
        return self.config.root

    @property
    def folder(self) -> GuidelinesFolder | None:
        """The folder the project keeps its own guidelines in, as ``guidelines_folder`` names it from the project's root
        or absolutely; none when it names none."""
        named = str(self.config.load().get(self.FOLDER_KEY) or "").strip()
        return self._held.folder_at(self.root / named) if named else None

    @property
    def own_classes(self) -> list[type]:
        """The guideline classes the project keeps in its own folder, disabled or not."""
        folder = self.folder
        return folder.classes if folder is not None else []

    def is_disabled(self, name: str) -> bool:
        return self.config.guideline(name) == DISABLED

    def chosen(self, shipped: Iterable[type]) -> list[type]:
        """The guideline classes the project works with, one for each name: the project's own copy when it keeps one,
        else the one CDD ships, never both; none the project disables."""
        by_name: dict[str, type] = {guideline_name(each): each for each in shipped}
        by_name.update({guideline_name(each): each for each in self.own_classes})
        return [each for name, each in by_name.items() if name and not self.is_disabled(name)]

    def toolsets(self, shipped: Iterable[type]) -> list[type]:
        """The toolset classes an install into the project publishes: each of shipped that is no guideline, then the
        guidelines the project works with (``chosen``)."""
        shipped = list(shipped)
        return [*(each for each in shipped if not guideline_name(each)), *self.chosen(each for each in shipped if guideline_name(each))]


class HeldProjectGuidelines:
    """The guidelines of each project the process has asked about, each made once, and each guidelines folder imported
    once: a module is imported once per process, so the folders that hold them are held once per process too."""

    def __init__(self) -> None:
        self._projects: dict[Path, ProjectGuidelines] = {}
        self._folders: dict[Path, GuidelinesFolder] = {}
        self._lock = threading.Lock()

    def of(self, root: Path | str) -> ProjectGuidelines:
        """The guidelines of the project at root; its config file is read again once it changes."""
        resolved = Path(root).resolve()
        with self._lock:
            if resolved not in self._projects:
                self._projects[resolved] = ProjectGuidelines(resolved, self)
            return self._projects[resolved]

    def installs_from(self, folder: Path) -> Path | None:
        """The folder a guideline defined in folder installs from, ``patterns/<name>`` as a shipped pattern does, when
        folder is a guideline in a project's guidelines folder; none for any other folder."""
        resolved = folder.resolve()
        with self._lock:
            held = resolved.parent in self._folders
        return Path(INSTALLED_UNDER) / resolved.name if held else None

    def folder_at(self, path: Path) -> GuidelinesFolder:
        resolved = path.resolve()
        with self._lock:
            if resolved not in self._folders:
                self._folders[resolved] = GuidelinesFolder(resolved)
            return self._folders[resolved]


PROJECT_GUIDELINES = HeldProjectGuidelines()
