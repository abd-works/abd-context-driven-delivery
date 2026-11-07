"""Generate a project-specific ``cdd-approach.html`` slide from project artifacts.

Maps each file the user (or the classifier) supplies to a practice × stage place on
the approach page — the same layout as ``catalog/cdd-approach.html``, with project
content in the Iterate and Learn and Product Engineering example columns.
"""
from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from harness.catalog_generator.approach_copy import APPROACH_MARKDOWN
from harness.catalog_generator.catalog_generator import Catalog, GitCitation
from harness.guidance.practice_catalogue import PracticeCatalogue
from harness.catalog_generator.foundry_chrome import (
    STAGE_COLUMNS,
    Brand,
    page_shell,
    stage_project_examples,
    write_stage_example_pages,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]

@dataclass(frozen=True)
class PracticeStage:
    practice: str
    stage: str


@dataclass
class ProjectApproach:
    project_root: Path
    project_title: str
    repo_url: str
    examples: dict[tuple[str, str], Path] = field(default_factory=dict)
    approach_md_path: Path = APPROACH_MARKDOWN

    @classmethod
    def from_paths(
        cls,
        project_root: str | Path,
        example_paths: Iterable[str | Path],
        *,
        project_title: str = "",
        repo_url: str = "",
    ) -> ProjectApproach:
        root = Path(project_root).resolve()
        resolved: dict[tuple[str, str], Path] = {}
        for raw in example_paths:
            path = _resolve_project_path(root, raw)
            place = classify_example_path(path, project_root=root)
            if place is None:
                continue
            resolved[(place.practice, place.stage)] = path
        citation = GitCitation.from_checkout(root) if root.is_dir() else GitCitation("", "")
        return cls(
            project_root=root,
            project_title=project_title or root.name.replace("-", " ").title(),
            repo_url=repo_url or citation.repo_url,
            examples=resolved,
        )

    def with_example(self, practice: str, stage: str, path: str | Path) -> ProjectApproach:
        updated = dict(self.examples)
        updated[(practice, stage)] = _resolve_project_path(self.project_root, path)
        return ProjectApproach(
            project_root=self.project_root,
            project_title=self.project_title,
            repo_url=self.repo_url,
            examples=updated,
            approach_md_path=self.approach_md_path,
        )

    def generate(self, out_root: str | Path, *, brands_root: str | Path | None = None) -> str:
        destination = Path(out_root).resolve()
        destination.mkdir(parents=True, exist_ok=True)
        Brand(collection=brands_root).copy_commons(destination)
        staged = stage_project_examples(self.project_root, self.examples, destination)
        catalog = Catalog(
            repo_url=self.repo_url,
            ref="",
            out_root=str(destination),
            approach_md_path=self.approach_md_path,
            brands_root=brands_root,
        )
        example_hrefs = write_stage_example_pages(
            destination,
            catalog.approach_copy.stages,
            example_sources=staged,
        )
        headline = html_escape(self.project_title)
        page = page_shell(
            title=f"{self.project_title} — Context Driven Delivery",
            h1=f'<span class="accent">{headline}</span> <span class="accent">Context Driven Delivery</span>',
            tagline="",
            subhead=catalog.approach_copy.subhead,
            after_subhead=(
                f'Project repo <a href="{html_escape(self.repo_url)}" '
                'target="_blank" rel="noopener noreferrer">here</a>.'
            ),
            body_inner=catalog.approach_page_body(
                example_hrefs,
                example_sources=staged,
                catalog_root=destination,
            ),
            commons_prefix="commons/",
            nav_prefix="",
            nav_current="",
            body_wrap_class="approach-wrap",
        )
        catalog.write_page("cdd-approach.html", page)
        return f"Wrote project approach slide to {destination / 'cdd-approach.html'}"


def classify_example_path(
    path: str | Path,
    *,
    project_root: Path | None = None,
) -> PracticeStage | None:
    """The practice and stage of the first board fidelity that declares a file at ``path``, read from each fidelity's
    ``outputs``, the same declarations the session uses to find a fidelity's files. None when no fidelity declares it."""
    candidate = Path(path).resolve()
    relative = _relative_posix(candidate, project_root)
    for practice in PracticeCatalogue.practices():
        for fidelity in practice.fidelities:
            if STAGE_COLUMNS.of(fidelity.stage) is None:
                continue
            if any(pattern.search(relative) for pattern in _declared_file_patterns(fidelity)):
                return PracticeStage(practice.key, fidelity.stage)
    return None


def _relative_posix(path: Path, project_root: Path | None) -> str:
    if project_root is not None and path.is_relative_to(project_root):
        return path.relative_to(project_root).as_posix()
    return path.as_posix()


def _declared_file_patterns(fidelity) -> list[re.Pattern[str]]:
    """Each file the fidelity declares, as a pattern that matches the end of a path. A declared folder, such as
    ``{module}/``, names no file, so it matches none."""
    declared = [
        name
        for names in fidelity.outputs.values()
        for name in ([names] if isinstance(names, str) else names)
        if name and not name.endswith("/")
    ]
    return [_declared_file_pattern(name) for name in declared]


def _declared_file_pattern(declared: str) -> re.Pattern[str]:
    """A declared path such as ``{bounded_context}/{aggregate}/{aggregate}.ts`` as a pattern. As in the session, a named
    folder matches folders at any depth and a named part of a file name matches within it; a name used twice must be
    the same text both times, and ``**/`` and ``*`` keep their glob meaning."""
    seen: set[str] = set()
    parts: list[str] = []
    for token in re.split(r"(\{[^{}/]+\}/?|\*\*/|\*)", declared):
        if not token:
            continue
        if token == "**/":
            parts.append(r"(?:[^/]+/)*")
        elif token == "*":
            parts.append(r"[^/]*")
        elif token.startswith("{"):
            name = re.sub(r"\W", "_", token.strip("{}/"))
            folder = token.endswith("/")
            if name in seen:
                parts.append(f"(?P={name})" + ("/" if folder else ""))
            else:
                seen.add(name)
                parts.append(f"(?P<{name}>[^/]+(?:/[^/]+)*)/" if folder else f"(?P<{name}>[^/]+)")
        else:
            parts.append(re.escape(token))
    return re.compile(r"(?:^|/)" + "".join(parts) + "$", re.I)


def discover_project_examples(project_root: str | Path) -> dict[tuple[str, str], Path]:
    root = Path(project_root).resolve()
    found: dict[tuple[str, str], Path] = {}
    if not root.is_dir():
        return found
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.name.startswith("."):
            continue
        if path.suffix.lower() in {".pyc", ".log"}:
            continue
        if any(
            part in {".git", "node_modules", ".codeql", "dist", "build", "catalog", "catalog-fresh"}
            for part in path.parts
        ):
            continue
        place = classify_example_path(path, project_root=root)
        if place is None:
            continue
        key = (place.practice, place.stage)
        if key not in found:
            found[key] = path
    return found


def load_examples_manifest(project_root: str | Path) -> dict[tuple[str, str], Path]:
    root = Path(project_root).resolve()
    manifest = root / ".context" / "project-approach-examples.json"
    if not manifest.is_file():
        return {}
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    examples = payload.get("examples") or {}
    resolved: dict[tuple[str, str], Path] = {}
    for practice, stages in examples.items():
        if not isinstance(stages, dict):
            continue
        for stage, relative in stages.items():
            if STAGE_COLUMNS.of(stage) is None:
                continue
            resolved[(practice, stage)] = _resolve_project_path(root, relative)
    return resolved


def save_examples_manifest(
    project_root: str | Path,
    examples: dict[tuple[str, str], Path],
    *,
    project_title: str = "",
    repo_url: str = "",
) -> Path:
    root = Path(project_root).resolve()
    manifest = root / ".context" / "project-approach-examples.json"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    nested: dict[str, dict[str, str]] = {practice: {} for practice in PracticeCatalogue.keys()}
    for (practice, stage), path in sorted(examples.items()):
        nested.setdefault(practice, {})[stage] = path.relative_to(root).as_posix()
    payload = {
        "project": project_title or root.name,
        "repo_url": repo_url,
        "examples": nested,
    }
    manifest.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return manifest


def html_escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _resolve_project_path(project_root: Path, raw: str | Path) -> Path:
    path = Path(raw)
    if not path.is_absolute():
        path = project_root / path
    return path.resolve()


def merge_example_sources(
    project_root: str | Path,
    explicit: Iterable[str | Path] | None = None,
) -> dict[tuple[str, str], Path]:
    root = Path(project_root).resolve()
    merged = discover_project_examples(root)
    for key, path in load_examples_manifest(root).items():
        merged[key] = path
    if explicit:
        for raw in explicit:
            path = _resolve_project_path(root, raw)
            place = classify_example_path(path, project_root=root)
            if place:
                merged[(place.practice, place.stage)] = path
    return merged
