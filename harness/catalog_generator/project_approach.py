"""Generate a project-specific ``cdd-approach.html`` slide from project artifacts.

Maps each file the project holds to a practice × stage place on the approach page - the same layout as
``catalog/cdd-approach.html``, with project content in the Iterate and Learn and Product Engineering example columns.
"""
from __future__ import annotations

import html
import json
import re
import shutil
from dataclasses import dataclass, field, replace
from pathlib import Path

from harness.catalog_generator.approach_copy import APPROACH_MARKDOWN, ApproachCopy
from harness.catalog_generator.approach_page import ApproachPage
from harness.catalog_generator.brand import Brand
from harness.catalog_generator.catalog_examples import ProjectExampleSources
from harness.catalog_generator.catalog_generator import CatalogPage, CatalogPractice, GitCitation
from harness.catalog_generator.page_shell import PageShell
from harness.catalog_generator.stage_columns import STAGE_COLUMNS, BoardLabel
from harness.guidance.practice_catalogue import PracticeCatalogue
from harness.process.git import RepoConnectError

# Where a project keeps the examples it chose for its approach page.
_EXAMPLES_MANIFEST = Path(".context") / "project-approach-examples.json"
# Folders that hold generated output, dependencies, or tool state, never an example.
_NOT_EXAMPLE_FOLDERS = frozenset({".git", "node_modules", ".codeql", "dist", "build", "catalog", "catalog-fresh"})
_NOT_EXAMPLE_SUFFIXES = frozenset({".pyc", ".log"})
_DECLARED_PART = re.compile(r"(\{[^{}/]+\}/?|\*\*/|\*)")

Examples = dict[tuple[str, str], Path]


@dataclass(frozen=True)
class PracticeStage:
    practice: str
    stage: str


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
    """Which board fidelity a project file shows: the first whose declared outputs name it, read from the same
    declarations the session uses to find a fidelity's files."""

    def __init__(self, project_root: Path | None = None) -> None:
        self.project_root = project_root

    def place_of(self, path: str | Path) -> PracticeStage | None:
        """The practice and stage of the first board fidelity that declares a file at ``path``; none when no fidelity
        declares it."""
        relative = self._relative(Path(path).resolve())
        for practice in PracticeCatalogue.practices():
            for fidelity in practice.fidelities:
                if STAGE_COLUMNS.of(fidelity.stage) is None:
                    continue
                if any(pattern.search(relative) for pattern in self._declared_patterns(fidelity)):
                    return PracticeStage(practice.key, fidelity.stage)
        return None

    def _relative(self, path: Path) -> str:
        if self.project_root is not None and path.is_relative_to(self.project_root):
            return path.relative_to(self.project_root).as_posix()
        return path.as_posix()

    def _declared_patterns(self, fidelity) -> list[re.Pattern[str]]:
        """A declared folder, such as ``{module}/``, names no file, so it gives no pattern."""
        declared = [
            name
            for names in fidelity.outputs.values()
            for name in ([names] if isinstance(names, str) else names)
            if name and not name.endswith("/")
        ]
        return [DeclaredFile(name).pattern for name in declared]


class ProjectFiles:
    """A project's checkout as its approach page reads it: the example files in its tree, the examples, title, and
    repository it saved, and its git origin."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).resolve()

    @property
    def discovered(self) -> Examples:
        """The first file in the project's tree that each board fidelity declares, by practice and stage."""
        found: Examples = {}
        if not self.root.is_dir():
            return found
        classifier = ExampleClassifier(self.root)
        for path in sorted(self.root.rglob("*")):
            if not self._may_be_example(path):
                continue
            place = classifier.place_of(path)
            if place is not None:
                found.setdefault((place.practice, place.stage), path)
        return found

    @property
    def manifest(self) -> Path:
        return self.root / _EXAMPLES_MANIFEST

    @property
    def saved(self) -> dict:
        return json.loads(self.manifest.read_text(encoding="utf-8")) if self.manifest.is_file() else {}

    @property
    def saved_examples(self) -> Examples:
        return {
            (practice, stage): (self.root / relative).resolve()
            for practice, stages in (self.saved.get("examples") or {}).items()
            if isinstance(stages, dict)
            for stage, relative in stages.items()
            if STAGE_COLUMNS.of(stage) is not None
        }

    @property
    def origin(self) -> str:
        """The project's repository address; empty for a project that is not a git checkout with an origin."""
        try:
            return GitCitation.from_checkout(self.root).repo_url
        except RepoConnectError:
            return ""

    def _may_be_example(self, path: Path) -> bool:
        if not path.is_file() or path.name.startswith(".") or path.suffix.lower() in _NOT_EXAMPLE_SUFFIXES:
            return False
        return not any(part in _NOT_EXAMPLE_FOLDERS for part in path.parts)


@dataclass(frozen=True)
class ProjectApproach:
    """A project's own approach page: its title, its repository, and the artifact that shows each practice at each
    stage."""

    project_root: Path
    project_title: str
    repo_url: str
    examples: Examples = field(default_factory=dict)
    approach_md_path: Path = APPROACH_MARKDOWN

    @classmethod
    def for_project(cls, project_root: str | Path, project_title: str = "") -> ProjectApproach:
        """The project's approach: the examples found in its tree, overridden by the ones it saved, under
        ``project_title`` (or the title it saved, or its folder's name), linking its own repository."""
        files = ProjectFiles(project_root)
        saved = files.saved
        return cls(
            project_root=files.root,
            project_title=project_title or saved.get("project") or files.root.name.replace("-", " ").title(),
            repo_url=saved.get("repo_url") or files.origin,
            examples={**files.discovered, **files.saved_examples},
        )

    def with_examples_json(self, examples_json: str) -> ProjectApproach:
        """The approach with the examples a JSON mapping of practice → stage → path names put over its own."""
        if not examples_json.strip():
            return self
        payload = json.loads(examples_json)
        chosen = {
            (practice, stage): (self.project_root / str(relative)).resolve()
            for practice, stages in (payload.get("examples") or payload).items()
            if isinstance(stages, dict)
            for stage, relative in stages.items()
        }
        return replace(self, examples={**self.examples, **chosen})

    def save_examples(self) -> Path:
        """Save the examples, title, and repository in the project's ``.context``, for the next run to start from."""
        manifest = ProjectFiles(self.project_root).manifest
        manifest.parent.mkdir(parents=True, exist_ok=True)
        nested: dict[str, dict[str, str]] = {practice: {} for practice in PracticeCatalogue.keys()}
        for (practice, stage), path in sorted(self.examples.items()):
            nested.setdefault(practice, {})[stage] = path.relative_to(self.project_root).as_posix()
        payload = {"project": self.project_title, "repo_url": self.repo_url, "examples": nested}
        manifest.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return manifest

    def generate(self, out_root: str | Path, *, brands_root: str | Path | None = None) -> str:
        destination = Path(out_root).resolve()
        destination.mkdir(parents=True, exist_ok=True)
        Brand(collection=brands_root).copy_commons(destination)
        copy = ApproachCopy.load(self.approach_md_path)
        page = ApproachPage(copy, CatalogPractice.load_all(), destination, self._stage_examples(destination))
        page.write_stage_example_pages()
        title = html.escape(self.project_title)
        shell = PageShell(
            title=f"{self.project_title} — Context Driven Delivery",
            h1=f'<span class="accent">{title}</span> <span class="accent">Context Driven Delivery</span>',
            tagline="",
            subhead=copy.subhead,
            after_subhead=(
                f'Project repo <a href="{html.escape(self.repo_url)}" target="_blank" rel="noopener noreferrer">here</a>.'
            ),
            body_inner=page.body,
            body_wrap_class="approach-wrap",
        )
        CatalogPage(destination).write("cdd-approach.html", shell.html)
        return f"Wrote project approach slide to {destination / 'cdd-approach.html'}"

    def _stage_examples(self, out_root: Path) -> ProjectExampleSources:
        """Copy each artifact into ``out_root/examples/{practice}`` under the board label of the practice's fidelity at
        that stage, so every project's examples land under the same names."""
        staged: dict[tuple[str, str], Path] = {}
        for (practice, stage), source in sorted(self.examples.items()):
            if not Path(source).is_file():
                continue
            name = self._catalog_name(practice, stage, Path(source))
            folder = out_root / "examples" / practice
            folder.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, folder / name)
            staged[(practice, stage)] = Path("examples") / practice / name
        return ProjectExampleSources(staged=staged)

    def _catalog_name(self, practice: str, stage: str, source: Path) -> str:
        fidelities = PracticeCatalogue.practice(practice).fidelities if PracticeCatalogue.has(practice) else ()
        fidelity = next((fidelity for fidelity in fidelities if fidelity.stage == stage), None)
        stem = str(BoardLabel(fidelity.name)) if fidelity is not None else source.stem.lower().replace(" ", "-")
        return f"{stem}{source.suffix.lower()}"
