"""A project's own ``cdd-approach.html`` slide: the project's title, its repository, and the artifact that shows each
practice at each stage.

Maps each file the project holds to the board fidelity that declares it - the same layout as
``catalog/cdd-approach.html``, with project content in the Iterate and Learn and Product Engineering example columns. The
*Catalog* renders the page with the practices, brand, and approach copy it holds.
"""
from __future__ import annotations

import html
import json
import re
import shutil
from dataclasses import dataclass, field, replace
from pathlib import Path

from harness.catalog_generator.catalog_examples import CatalogFidelity, ProjectExampleSources
from harness.catalog_generator.catalog_generator import CatalogPractice, GitCitation
from harness.process.git import RepoConnectError

# Where a project keeps the examples it chose for its approach page.
_EXAMPLES_MANIFEST = Path(".context") / "project-approach-examples.json"
# Folders that hold generated output, dependencies, or tool state, never an example.
_NOT_EXAMPLE_FOLDERS = frozenset({".git", "node_modules", ".codeql", "dist", "build", "catalog", "catalog-fresh"})
_NOT_EXAMPLE_SUFFIXES = frozenset({".pyc", ".log"})
_DECLARED_PART = re.compile(r"(\{[^{}/]+\}/?|\*\*/|\*)")

Examples = dict[CatalogFidelity, Path]


class DeclaredFile:
    """A file a fidelity declares in its outputs, such as ``{bounded_context}/{aggregate}/{aggregate}.ts``, as a
    pattern that matches the end of a path. As in the session, a named folder matches folders at any depth and a named
    part of a file name matches within it; a name used twice must be the same text both times, and ``**/`` and ``*``
    keep their glob meaning."""

    def __init__(self, declared: str) -> None:
        self._declared = declared

    @property
    def pattern(self) -> re.Pattern[str]:
        named: set[str] = set()
        parts = [self._part(token, named) for token in _DECLARED_PART.split(self._declared) if token]
        return re.compile(r"(?:^|/)" + "".join(parts) + "$", re.I)

    def _part(self, token: str, named: set[str]) -> str:
        """The pattern for one part; ``named`` holds the names earlier parts of the same path used."""
        if token == "**/":
            return r"(?:[^/]+/)*"
        if token == "*":
            return r"[^/]*"
        if not token.startswith("{"):
            return re.escape(token)
        name = re.sub(r"\W", "_", token.strip("{}/"))
        folder = "/" if token.endswith("/") else ""
        if name in named:
            return f"(?P={name}){folder}"
        named.add(name)
        return f"(?P<{name}>[^/]+(?:/[^/]+)*)/" if folder else f"(?P<{name}>[^/]+)"


class ExampleClassifier:
    """Which board fidelity a project file shows: the first, in the practice catalogue's order, whose declared outputs
    name it, read from the same declarations the session uses to find a fidelity's files. Made for the project and the
    catalog's practices."""

    def __init__(self, project_root: Path, practices: list[CatalogPractice]) -> None:
        self.project_root = project_root
        self.practices = sorted(practices, key=lambda practice: practice.position)

    def place_of(self, path: str | Path) -> CatalogFidelity | None:
        """The first board fidelity that declares a file at ``path``; none when no fidelity declares it."""
        relative = self._relative(Path(path).resolve())
        for practice in self.practices:
            for shown in practice.board_fidelities:
                if any(pattern.search(relative) for pattern in self._declared_patterns(shown)):
                    return shown
        return None

    def _relative(self, path: Path) -> str:
        if path.is_relative_to(self.project_root):
            return path.relative_to(self.project_root).as_posix()
        return path.as_posix()

    def _declared_patterns(self, shown: CatalogFidelity) -> list[re.Pattern[str]]:
        """A declared folder, such as ``{module}/``, names no file, so it gives no pattern."""
        declared = [
            name
            for names in shown.fidelity.outputs.values()
            for name in ([names] if isinstance(names, str) else names)
            if name and not name.endswith("/")
        ]
        return [DeclaredFile(name).pattern for name in declared]


class ProjectFiles:
    """A project's checkout as its approach page reads it, for the catalog's practices: the example files in its tree,
    the examples, title, and repository it saved, and its git origin."""

    def __init__(self, root: str | Path, practices: list[CatalogPractice]) -> None:
        self.root = Path(root).resolve()
        self.practices = practices
        self.classifier = ExampleClassifier(self.root, practices)

    @property
    def discovered(self) -> Examples:
        """The first file in the project's tree that each board fidelity declares."""
        found: Examples = {}
        if not self.root.is_dir():
            return found
        for path in sorted(self.root.rglob("*")):
            if not self._may_be_example(path):
                continue
            place = self.classifier.place_of(path)
            if place is not None:
                found.setdefault(place, path)
        return found

    @property
    def manifest(self) -> Path:
        return self.root / _EXAMPLES_MANIFEST

    @property
    def saved(self) -> dict:
        return json.loads(self.manifest.read_text(encoding="utf-8")) if self.manifest.is_file() else {}

    @property
    def saved_examples(self) -> Examples:
        return self.placed(self.saved.get("examples") or {})

    def placed(self, mapping: dict) -> Examples:
        """The examples a mapping of practice key → stage → path from the project names, each under the board fidelity
        it names; a practice or stage the board does not show is left out. The mapping comes from the project's saved
        manifest or from a person, so its keys are the names they wrote."""
        return {
            shown: (self.root / str(relative)).resolve()
            for practice_key, stages in mapping.items()
            if isinstance(stages, dict)
            for stage, relative in stages.items()
            for shown in [self._fidelity_at(practice_key, stage)]
            if shown is not None
        }

    @property
    def origin(self) -> str:
        """The project's repository address; empty for a project that is not a git checkout with an origin."""
        try:
            return GitCitation.from_checkout(self.root).repo_url
        except RepoConnectError:
            return ""

    def _fidelity_at(self, practice_key: str, stage: str) -> CatalogFidelity | None:
        return next(
            (
                shown
                for practice in self.practices if practice.key == practice_key
                for shown in practice.board_fidelities if shown.stage == stage
            ),
            None,
        )

    def _may_be_example(self, path: Path) -> bool:
        if not path.is_file() or path.name.startswith(".") or path.suffix.lower() in _NOT_EXAMPLE_SUFFIXES:
            return False
        return not any(part in _NOT_EXAMPLE_FOLDERS for part in path.parts)


@dataclass(frozen=True)
class ProjectApproach:
    """A project's own approach page: its files, its title, its repository, and the artifact that shows each board
    fidelity. The *Catalog* renders it with the practices, brand, and approach copy it holds."""

    files: ProjectFiles
    project_title: str
    repo_url: str
    examples: Examples = field(default_factory=dict)

    @classmethod
    def for_project(cls, files: ProjectFiles, project_title: str = "") -> ProjectApproach:
        """The project's approach: the examples found in its tree, overridden by the ones it saved, under
        ``project_title`` (or the title it saved, or its folder's name), linking its own repository."""
        saved = files.saved
        return cls(
            files=files,
            project_title=project_title or saved.get("project") or files.root.name.replace("-", " ").title(),
            repo_url=saved.get("repo_url") or files.origin,
            examples={**files.discovered, **files.saved_examples},
        )

    @property
    def project_root(self) -> Path:
        return self.files.root

    @property
    def page_title(self) -> str:
        return f"{self.project_title} — Context Driven Delivery"

    @property
    def headline(self) -> str:
        title = html.escape(self.project_title)
        return f'<span class="accent">{title}</span> <span class="accent">Context Driven Delivery</span>'

    @property
    def repo_link(self) -> str:
        return f'Project repo <a href="{html.escape(self.repo_url)}" target="_blank" rel="noopener noreferrer">here</a>.'

    def with_examples_json(self, examples_json: str) -> ProjectApproach:
        """The approach with the examples a JSON mapping of practice → stage → path names put over its own."""
        if not examples_json.strip():
            return self
        payload = json.loads(examples_json)
        return replace(self, examples={**self.examples, **self.files.placed(payload.get("examples") or payload)})

    def save_examples(self) -> Path:
        """Save the examples, title, and repository in the project's ``.context``, for the next run to start from."""
        manifest = self.files.manifest
        manifest.parent.mkdir(parents=True, exist_ok=True)
        ordered = sorted(self.files.practices, key=lambda practice: practice.position)
        nested: dict[str, dict[str, str]] = {practice.key: {} for practice in ordered}
        for (practice_key, stage), path in sorted((self._place_of(shown), path) for shown, path in self.examples.items()):
            nested.setdefault(practice_key, {})[stage] = path.relative_to(self.project_root).as_posix()
        payload = {"project": self.project_title, "repo_url": self.repo_url, "examples": nested}
        manifest.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return manifest

    def staged_into(self, out_root: Path) -> ProjectExampleSources:
        """Copy each artifact into ``out_root/examples/{practice}`` under the board label of its fidelity, so every
        project's examples land under the same names."""
        staged: dict[tuple[str, str], Path] = {}
        for shown, source in self.examples.items():
            if not Path(source).is_file():
                continue
            practice_key, stage = self._place_of(shown)
            name = f"{shown.label}{Path(source).suffix.lower()}"
            folder = Path(out_root) / "examples" / practice_key
            folder.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, folder / name)
            staged[(practice_key, stage)] = Path("examples") / practice_key / name
        return ProjectExampleSources(staged=staged)

    def _place_of(self, shown: CatalogFidelity) -> tuple[str, str]:
        return shown.fidelity.practice_guidance.key, shown.stage
