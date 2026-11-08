"""The example files the catalog shows: each practice's ``catalog-examples`` and a project's own artifacts."""
from __future__ import annotations

import base64
import html
import json
import re
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING

from harness.catalog_generator.drawio_diagram import DrawioDiagram
from harness.markdown.front_matter import FrontMatter
from harness.catalog_generator.markdown_html import MarkdownHtml
from harness.catalog_generator.source_folds import Fold, SourceFolds
from harness.catalog_generator.stage_columns import STAGE_COLUMNS, BoardLabel, StageColumn

if TYPE_CHECKING:
    from harness.catalog_generator.catalog_practice import CatalogPractice

EXAMPLES_FOLDER = "catalog-examples"
# The order a fidelity's examples are shown in: prose, then code, then diagrams, then pictures.
_SUFFIX_ORDER = {
    ".md": 0, ".markdown": 0,
    ".ts": 1, ".tsx": 1, ".html": 1, ".htm": 1,
    ".drawio": 2, ".dio": 2,
    ".png": 3, ".jpg": 3, ".jpeg": 3, ".gif": 3, ".webp": 3, ".svg": 3,
}
_UNORDERED = 50
_MARKDOWN_SUFFIXES = (".md", ".markdown")
_HTML_SUFFIXES = (".html", ".htm")
_DRAWIO_SUFFIXES = (".drawio", ".dio")
_IMAGE_MIME = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
    ".svg": "image/svg+xml",
}
_MONACO_LANGUAGES = {
    ".ts": "typescript",
    ".tsx": "typescript",
    ".js": "javascript",
    ".jsx": "javascript",
    ".py": "python",
    ".html": "html",
    ".htm": "html",
}
_MONACO_LOADER = "https://cdn.jsdelivr.net/npm/monaco-editor@0.52.2/min/vs/loader.js"
# An approach panel's code viewer and a stage example page each load the viewer script at their own version.
_PANEL_MONACO_SCRIPT = "commons/catalog-monaco.js?v=cdd-109"
_STAGE_PAGE_MONACO_SCRIPT = "../commons/catalog-monaco.js?v=cdd-108"
MONACO_LOADER_SCRIPTS = f'<script src="{_MONACO_LOADER}"></script><script src="{_PANEL_MONACO_SCRIPT}"></script>'
# A static HTML example (a mockup) is shown at the width it was designed for, scrolled inside its panel.
_HTML_EXAMPLE_STYLE = "width:2700px;height:920px;max-width:none"
# The tactics example opens its code viewer at its aggregate root.
_ROOT_CLASS_LINE = "export class Customer"
_BACK_TO_APPROACH = (
    '<p class="approach-practice__back"><a href="../cdd-approach.html">← Back to the approach</a></p>'
)
_DOMAIN_TERM_IN_CODE = re.compile(r"\+\+`([^`]+)`\+\+(\.[A-Za-z][\w]*)?")
_DOMAIN_TERM = re.compile(r"\+\+([^+`][^+]*?)\+\+")
_OPERATION_PARENTHESES = re.compile(r"\*\(\*`([^`]+)`\*(\.[A-Za-z][\w]*)\)\*")


class ExampleMarkdown:
    """A markdown example: a story's scenarios, a domain model. Its settings block is dropped and the scenario
    notation (``++domain term++`` and an operation's ``*(*`Type`*.operation)*``) is unwrapped, so the HTML reads as
    prose. An example that is only an indented outline is shown as that outline."""

    def __init__(self, text: str) -> None:
        self._text = text

    @property
    def html(self) -> str:
        body = self._unwrapped(FrontMatter(self._text).content).strip()
        while body.startswith("---") and not body.startswith("----"):
            body = body[3:].lstrip("\n")
        if self._is_outline(body):
            return f'<pre class="catalog-example__tree">{html.escape(body.strip())}</pre>'
        return MarkdownHtml(body, include_tables=True).html

    def _unwrapped(self, text: str) -> str:
        text = _DOMAIN_TERM_IN_CODE.sub(lambda match: f"`{match.group(1)}`{match.group(2) or ''}", text)
        text = _DOMAIN_TERM.sub(r"**\1**", text)
        return _OPERATION_PARENTHESES.sub(r"(`\1`\2)", text)

    def _is_outline(self, body: str) -> bool:
        lines = [line for line in body.splitlines() if line.strip()]
        indented = sum(1 for line in lines if line[:1].isspace())
        has_markup = any(line.lstrip().startswith(("#", "|")) for line in lines)
        return bool(lines) and not has_markup and indented >= len(lines) / 2


@dataclass(frozen=True)
class MonacoViewer:
    """A code example in the Monaco editor, with the folds it opens with. Several viewers on one page share one set of
    loader scripts, so a panel's viewer leaves them out and the page adds them once."""

    source: str
    language: str
    script_source: str
    editor_id: str = "catalog-monaco"
    folds: list[Fold] | None = None
    includes_scripts: bool = True
    start_line: int | None = None

    @property
    def html(self) -> str:
        ranges = SourceFolds(self.source).steps if self.folds is None else self.folds
        payload = json.dumps(self.source).replace("<", "\\u003c")
        folds = html.escape(json.dumps([{"start": start, "end": end} for start, end in ranges]), quote=True)
        source_id = f"{self.editor_id}-source"
        start = f' data-start-line="{self.start_line}"' if self.start_line else ""
        body = (
            f'<div id="{html.escape(self.editor_id)}" class="catalog-monaco" '
            f'data-language="{html.escape(self.language)}" data-folds="{folds}" '
            f'data-source-id="{html.escape(source_id)}"{start}></div>'
            f'<script type="application/json" id="{html.escape(source_id)}">{payload}</script>'
        )
        if not self.includes_scripts:
            return body
        return body + f'<script src="{_MONACO_LOADER}"></script><script src="{html.escape(self.script_source)}"></script>'


class ExampleFile:
    """One example file and the ways the catalog shows it: as a figure on a fidelity page, inside an approach panel,
    and as a stage example's own page."""

    def __init__(self, path: Path) -> None:
        self.path = path

    @property
    def suffix(self) -> str:
        return self.path.suffix.lower()

    @property
    def is_image(self) -> bool:
        return self.suffix in _IMAGE_MIME

    @property
    def figure_html(self) -> str:
        """The example on a fidelity page: markdown as HTML, draw.io in the viewer, a picture embedded in the page, and
        any other file as its source."""
        name = html.escape(self.path.name)
        return (
            '<figure class="catalog-example">'
            f'<figcaption class="catalog-example__name">{name}</figcaption>'
            f"{self._figure_inner(name)}"
            "</figure>"
        )

    def panel_html(self, *, editor_id: str = "catalog-monaco", catalog_href: Path | str | None = None) -> str:
        """The example inside an approach panel. ``catalog_href`` is where a project's staged picture sits in the
        catalog; a practice's own picture sits under ``examples/{practice}``."""
        if self.suffix in _DRAWIO_SUFFIXES:
            return DrawioDiagram.load(self.path).panel_html
        if self.suffix in _HTML_SUFFIXES:
            return self._scrolled_page_html()
        if self.is_image:
            return self._panel_image_html(catalog_href)
        text = self.path.read_text(encoding="utf-8")
        if self.suffix in _MARKDOWN_SUFFIXES:
            return f'<div class="skill-md-preview">{ExampleMarkdown(text).html}</div>'
        return MonacoViewer(
            text,
            self._language,
            _PANEL_MONACO_SCRIPT,
            editor_id=editor_id,
            folds=SourceFolds(text).for_example,
            includes_scripts=False,
            start_line=self._root_class_line(text),
        ).html

    @property
    def stage_page_html(self) -> str:
        """The body of a stage example's own page, under a link back to the approach."""
        if self.is_image:
            name = html.escape(self.path.name)
            return (
                f"{_BACK_TO_APPROACH}"
                '<figure class="catalog-example">'
                f'<img class="catalog-example__image" alt="{name}" src="{name}">'
                "</figure>"
            )
        text = self.path.read_text(encoding="utf-8")
        if self.suffix in _MARKDOWN_SUFFIXES:
            return f'{_BACK_TO_APPROACH}<div class="skill-md-preview">{ExampleMarkdown(text).html}</div>'
        viewer = MonacoViewer(text, self._language, _STAGE_PAGE_MONACO_SCRIPT, folds=SourceFolds(text).acceptance_test)
        return _BACK_TO_APPROACH + viewer.html

    @property
    def _language(self) -> str:
        return _MONACO_LANGUAGES.get(self.suffix, "plaintext")

    def _figure_inner(self, name: str) -> str:
        if self.suffix in _MARKDOWN_SUFFIXES:
            return f'<div class="skill-md-preview">{ExampleMarkdown(self.path.read_text(encoding="utf-8")).html}</div>'
        if self.suffix in _HTML_SUFFIXES:
            page = html.escape(self.path.read_text(encoding="utf-8"), quote=True)
            return f'<iframe class="catalog-example__frame" title="{name}" sandbox="" srcdoc="{page}"></iframe>'
        if self.suffix in _DRAWIO_SUFFIXES:
            viewer = html.escape(DrawioDiagram.load(self.path).viewer_url(with_toolbar=True), quote=True)
            return f'<iframe class="catalog-drawio-frame" title="{name}" loading="lazy" src="{viewer}"></iframe>'
        if self.is_image:
            payload = base64.b64encode(self.path.read_bytes()).decode("ascii")
            return f'<img class="catalog-example__image" alt="{name}" src="data:{_IMAGE_MIME[self.suffix]};base64,{payload}">'
        language = html.escape(self.suffix.lstrip(".") or "text")
        source = html.escape(self.path.read_text(encoding="utf-8"))
        return (
            '<div class="skill-code-preview">'
            f'<div class="skill-code-lang">{language}</div>'
            f"<pre><code>{source}</code></pre>"
            "</div>"
        )

    def _scrolled_page_html(self) -> str:
        page = html.escape(self.path.read_text(encoding="utf-8"), quote=True)
        return (
            '<figure class="catalog-example catalog-example--scroll">'
            f'<iframe class="catalog-example__frame" title="{html.escape(self.path.name)}" sandbox="" '
            f'style="{_HTML_EXAMPLE_STYLE}" srcdoc="{page}"></iframe>'
            "</figure>"
        )

    def _panel_image_html(self, catalog_href: Path | str | None) -> str:
        name = html.escape(self.path.name)
        if catalog_href is not None:
            href = html.escape(str(catalog_href).replace("\\", "/"))
        elif self.path.parent.name == EXAMPLES_FOLDER:
            href = f"examples/{html.escape(self.path.parent.parent.name)}/{name}"
        else:
            href = f"examples/{name}"
        return (
            f'<figure class="{" ".join(self._panel_image_classes)}">'
            f'<img class="catalog-example__image" alt="{name}" src="{href}">'
            "</figure>"
        )

    @property
    def _panel_image_classes(self) -> list[str]:
        """A bounded-context map fits its panel, a model or screen picture opens magnified, and a story map gets the
        story map's frame."""
        stem = self.path.stem
        classes = ["catalog-example", "catalog-example--scroll"]
        if stem == "bounded-context":
            classes.append("catalog-example--fit")
        if stem in {"model", "front-end-code"}:
            classes.append("catalog-example--zoom-2")
        if stem.replace("-", "_") == "story_map":
            classes.append("catalog-example--story-map")
        return classes

    def _root_class_line(self, text: str) -> int | None:
        return next(
            (number for number, line in enumerate(text.splitlines(), start=1) if line.startswith(_ROOT_CLASS_LINE)), None
        )


class CatalogFidelity:
    """A fidelity as the catalog shows it: its board column, its board label, the opening of its overview, and its
    example files, the files in its practice's ``catalog-examples`` folder named for the fidelity in any spelling or by
    its board label. Its practice in the catalog makes one for each fidelity it shows and keeps it, so every page, board
    ticket, and approach panel reads the same one. The fidelity page and the approach panel both start from these
    files, so a file shown on one is never missing from the other."""

    def __init__(self, fidelity) -> None:
        self.fidelity = fidelity

    @property
    def name(self) -> str:
        return self.fidelity.name

    @property
    def stage(self) -> str:
        return self.fidelity.stage

    @cached_property
    def column(self) -> StageColumn | None:
        """The board column the fidelity's stage sits in; none for a stage the board has no column for."""
        return STAGE_COLUMNS.of(self.fidelity.approach_stage)

    @property
    def label(self) -> str:
        return str(BoardLabel(self.fidelity.name))

    @property
    def opening(self) -> str:
        """The first paragraph of the fidelity's overview: the outline a reader sees before its rules."""
        lines: list[str] = []
        in_fence = False
        for line in (self.fidelity.overview or self.fidelity.section).splitlines():
            stripped = line.strip()
            if stripped.startswith("```"):
                if lines:
                    break
                in_fence = not in_fence
            elif in_fence:
                continue
            elif not stripped or stripped.startswith("#"):
                if lines:
                    break
            else:
                lines.append(line)
        return "\n".join(lines).strip()

    @property
    def examples_folder(self) -> Path:
        return Path(self.fidelity.practice_guidance.module_dir) / EXAMPLES_FOLDER

    @property
    def example_files(self) -> list[Path]:
        if not self.examples_folder.is_dir():
            return []
        name = self.fidelity.name
        names = {name, name.replace("_", "-"), name.replace("-", "_"), self.label}
        found = (
            path for path in self.examples_folder.iterdir()
            if path.is_file() and not path.name.startswith(".") and path.stem in names
        )
        return sorted(found, key=self._display_order)

    @property
    def panel_example_files(self) -> list[Path]:
        """The files an approach panel shows: of each group sharing a name, a picture or diagram over the source it was
        drawn from, because the panel has room for one view of each example."""
        groups: dict[str, list[Path]] = {}
        for path in self.example_files:
            groups.setdefault(path.stem, []).append(path)
        chosen = [path for group in groups.values() for path in self._preferred(group)]
        return sorted(chosen, key=self._display_order)

    @property
    def examples_html(self) -> str:
        """The collapsible Examples block on the fidelity and practice pages; empty when the fidelity has none."""
        if not self.example_files:
            return ""
        figures = "".join(ExampleFile(path).figure_html for path in self.example_files)
        return (
            '<details class="catalog-examples">'
            "<summary>Examples</summary>"
            f'<div class="catalog-examples__body">{figures}</div>'
            "</details>"
        )

    def _display_order(self, path: Path) -> tuple[int, str]:
        return _SUFFIX_ORDER.get(path.suffix.lower(), _UNORDERED), path.name

    def _preferred(self, group: list[Path]) -> list[Path]:
        pictures = [path for path in group if ExampleFile(path).is_image]
        if pictures:
            return pictures
        diagrams = [path for path in group if path.suffix.lower() in _DRAWIO_SUFFIXES]
        if diagrams:
            return diagrams
        return [path for path in group if path.suffix.lower() not in _MARKDOWN_SUFFIXES] or group


@dataclass(frozen=True)
class ProjectExampleSources:
    """A project's own artifacts, copied into the catalog's ``examples/`` folder, by the board fidelity each shows."""

    staged: dict[CatalogFidelity, Path]

    def file_for(self, shown: CatalogFidelity | None) -> Path | None:
        """Where the artifact of fidelity ``shown`` sits in the catalog, relative to the catalog's folder; none when the
        project gave none for it."""
        return self.staged.get(shown) if shown is not None else None


class StageExample:
    """The example an approach stage names in its copy (``example:``), from the examples of the practice whose stage
    examples the approach shows (Stories); for a project's approach page, the project's own artifact of that practice's
    fidelity at the stage."""

    def __init__(
        self, stage, stories: CatalogPractice | None, project_examples: ProjectExampleSources | None = None
    ) -> None:
        self.stage = stage
        self._stories = stories
        self._project_examples = project_examples

    @property
    def catalog_path(self) -> Path | None:
        """Where a project's artifact sits in the catalog; none for a practice example."""
        if self._project_examples is None or self._stories is None:
            return None
        return self._project_examples.file_for(self._stories.fidelity_at(self.stage.id))

    @property
    def exists(self) -> bool:
        if self._project_examples:
            return self.catalog_path is not None
        practice_file = self._practice_file
        return practice_file is not None and practice_file.is_file()

    def href(self, path_prefix: str = "") -> str:
        """The example's own page; empty when the stage has no example."""
        return f"{path_prefix}examples/{self.stage.id}.html" if self.exists else ""

    def file(self, catalog_root: Path | None) -> Path | None:
        """The example file: a project's under ``catalog_root``, else the practice's own example."""
        if self._project_examples:
            relative = self.catalog_path
            return Path(catalog_root) / relative if relative and catalog_root is not None else None
        return self._practice_file

    @property
    def _practice_file(self) -> Path | None:
        if not self.stage.example or self._stories is None:
            return None
        return self._stories.examples_folder / self.stage.example
