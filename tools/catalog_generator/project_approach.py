"""Generate a project-specific ``cdd-approach.html`` slide from project artifacts.

Maps each file the user (or the classifier) supplies to a practice × stage slot on
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

from catalog_generator.approach_copy import APPROACH_MARKDOWN, load_approach_copy
from catalog_generator.catalog_generator import Catalog, GitCitation, load_registry
from catalog_generator.foundry_chrome import (
    Brand,
    page_shell,
    stage_project_examples,
    write_stage_example_pages,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_STAGE_IDS = ("discovery", "specification", "implementation")
_PRACTICES = ("stories", "ddd", "ux", "clean_engineering", "bdd")

_PATH_HINTS: tuple[tuple[tuple[str, str], re.Pattern[str]], ...] = (
    (("stories", "discovery"), re.compile(r"story[-_]?map", re.I)),
    (("stories", "specification"), re.compile(r"(?:story[-_])?scenarios", re.I)),
    (
        ("stories", "implementation"),
        re.compile(r"(?:story|acceptance)[-_]?(?:test|tests)|_story\.test\.", re.I),
    ),
    (("ddd", "discovery"), re.compile(r"bounded[-_]?context", re.I)),
    (
        ("ddd", "specification"),
        re.compile(r"building[-_]?blocks|ce-domain-model|domain-model", re.I),
    ),
    (
        ("ddd", "implementation"),
        re.compile(r"(?:^|/)(?:client|offer|product)[-_]?model\.(?:ts|py)$|tactics", re.I),
    ),
    (("ux", "discovery"), re.compile(r"information[-_]?architecture|(?:^|/)ia[./]", re.I)),
    (("ux", "specification"), re.compile(r"mockup", re.I)),
    (
        ("ux", "implementation"),
        re.compile(r"front[-_]?end(?:[-_]?code)?|(?:^|/)components?/", re.I),
    ),
    (("clean_engineering", "discovery"), re.compile(r"modules?[-_]?map|module[-_]?context", re.I)),
    (("clean_engineering", "specification"), re.compile(r"[-_]model\.(?:md|drawio)$", re.I)),
    (("clean_engineering", "implementation"), re.compile(r"module[-_]?map|clean[-_]?engineering", re.I)),
    (("bdd", "specification"), re.compile(r"behavior|behaviour", re.I)),
    (("bdd", "implementation"), re.compile(r"bdd[-_]?development|development\.test", re.I)),
)

_FOLDER_HINTS: tuple[tuple[tuple[str, str], str], ...] = (
    (("stories", "discovery"), "stories"),
    (("ddd", "discovery"), "domain"),
    (("ux", "discovery"), "ux"),
)


@dataclass(frozen=True)
class ApproachExampleSlot:
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
            slot = classify_example_path(path, project_root=root)
            if slot is None:
                continue
            resolved[(slot.practice, slot.stage)] = path
        citation = GitCitation.from_checkout(root) if root.is_dir() else GitCitation("", "")
        return cls(
            project_root=root,
            project_title=project_title or root.name.replace("-", " ").title(),
            repo_url=repo_url or citation.repo_url,
            examples=resolved,
        )

    def with_slot(self, practice: str, stage: str, path: str | Path) -> ProjectApproach:
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
        context_entries, _utilities = load_registry()
        catalog = Catalog(
            repo_url=self.repo_url,
            ref="",
            out_root=str(destination),
            approach_md_path=self.approach_md_path,
            brands_root=brands_root,
        )
        catalog._context_tool_entries = context_entries
        catalog._board_tools = catalog._board_tool_entries()
        example_hrefs = write_stage_example_pages(
            destination,
            catalog._approach_copy().stages,
            example_sources=staged,
        )
        headline = html_escape(self.project_title)
        page = page_shell(
            title=f"{self.project_title} — Context Driven Delivery",
            h1=f'<span class="accent">{headline}</span> <span class="accent">Context Driven Delivery</span>',
            tagline="",
            subhead=load_approach_copy(self.approach_md_path).subhead,
            after_subhead=(
                f'Project repo <a href="{html_escape(self.repo_url)}" '
                'target="_blank" rel="noopener noreferrer">here</a>.'
            ),
            body_inner=catalog._approach_page_body(
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
) -> ApproachExampleSlot | None:
    candidate = Path(path).resolve()
    text = "/".join(candidate.parts).lower()
    name = candidate.name.lower()
    for (practice, stage), pattern in _PATH_HINTS:
        if pattern.search(name) or pattern.search(text):
            return ApproachExampleSlot(practice, stage)
    if candidate.suffix.lower() in {".drawio", ".dio"}:
        for (practice, stage), folder in _FOLDER_HINTS:
            if f"/{folder}/" in text or text.endswith(f"/{folder}/{name}"):
                return ApproachExampleSlot(practice, stage)
    if project_root and candidate.suffix.lower() in {".ts", ".tsx"}:
        rel = candidate.relative_to(project_root).as_posix().lower()
        if rel.startswith("stories/") and "test" in name:
            return ApproachExampleSlot("stories", "implementation")
        if rel.startswith("domain/") and name.endswith("-model.ts"):
            return ApproachExampleSlot("ddd", "implementation")
    return None


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
        slot = classify_example_path(path, project_root=root)
        if slot is None:
            continue
        key = (slot.practice, slot.stage)
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
            if stage not in _STAGE_IDS:
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
    nested: dict[str, dict[str, str]] = {practice: {} for practice in _PRACTICES}
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
            slot = classify_example_path(path, project_root=root)
            if slot:
                merged[(slot.practice, slot.stage)] = path
    return merged
