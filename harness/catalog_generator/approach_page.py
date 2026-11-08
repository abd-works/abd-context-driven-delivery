"""The approach page (``cdd-approach.html``): the stages the approach walks, its principles with the board drawn under
each, the practice library, and the pages a stage example or a principle opens."""
from __future__ import annotations

import html
import json
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path

from harness.catalog_generator.approach_copy import ApproachCopy, PrincipleCopy, StageCopy
from harness.catalog_generator.catalog_examples import (
    MONACO_LOADER_SCRIPTS,
    CatalogFidelity,
    ExampleFile,
    ProjectExampleSources,
    StageExample,
)
from harness.catalog_generator.markdown_html import MarkdownHtml
from harness.catalog_generator.page_shell import PageShell
from harness.catalog_generator.stage_columns import STAGE_COLUMNS, StageColumn
from harness.annotations.name import Name

# The colour families the approach cycles through for a stage's first three chips.
_ITEM_FAMILIES = ("sdd", "uxd", "arc")
_ITERATE_AND_LEARN = "iterate-and-learn"
_PRODUCT_ENGINEERING = "product-engineering"
_EMPHASIS = re.compile(r"\*([^*]+)\*")
_APPROACH_SCRIPT = '<script src="commons/catalog-approach.js?v=cdd-1"></script>'
_LIBRARY_HEAD = (
    '<a class="approach-grid__label approach-grid__label--cdd" href="cdd-approach.html">'
    "context-driven-delivery</a>"
)
# The windows Iterate and Learn narrows through, from the whole solution to one story: (shape, name, reach, pace,
# what the work decides).
_WINDOWS = (
    ("solution", "Whole Solution", "wide / shallow", "", "outcomes · scope · boundaries"),
    ("increment", "Increment", "medium", "days", "interactions · experience · structure"),
    ("sprint", "Session", "narrow / deeper", "hours", "behaviour · design · logic"),
    ("story", "Story", "narrowest / deep", "minutes", "tests · code · interface"),
)
_REFINE_TRANSPORT = (
    '<div class="approach-refine__nav" role="group" aria-label="Stage examples">'
    '<button type="button" class="approach-refine__nav-btn approach-refine__nav-btn--back" '
    'data-refine-nav="-1" aria-label="Collapse last example">'
    '<span class="approach-refine__icon approach-refine__icon--back" aria-hidden="true"></span>'
    "</button>"
    '<button type="button" class="approach-refine__nav-btn approach-refine__nav-btn--fwd" '
    'data-refine-nav="1" aria-label="Expand next example">'
    '<span class="approach-refine__icon approach-refine__icon--fwd" aria-hidden="true"></span>'
    "</button>"
    "</div>"
)
_COMING_SOON = (("customer-discovery", "Customer Discovery"), ("devops", "DevOps"))
_BACK_LINK = '<p class="approach-practice__back"><a href="cdd-approach.html">← Back to the approach</a></p>'


class PrincipleBullets:
    """A principle's bullets as the page writes them: ``*emphasis*`` in italics, and a ``phrase | so what`` bullet as a
    bold phrase over its italic so-what."""

    def __init__(self, items: tuple[str, ...]) -> None:
        self.items = items

    @property
    def paragraphs_html(self) -> str:
        return "".join(f'<p class="approach-practice__para">{self._formatted(item)}</p>' for item in self.items)

    @property
    def list_html(self) -> str:
        items = "".join(f"<li>{self._formatted(item)}</li>" for item in self.items)
        return f'<ul class="approach-principle__bullets">{items}</ul>' if items else ""

    def so_what_html(self, modifier: str = "") -> str:
        """The bullets in columns, orange dots between them."""
        parts: list[str] = []
        for index, item in enumerate(self.items):
            phrase, separator, why = item.partition(" | ")
            why_html = f'<p class="approach-so__why">{self._formatted(why)}</p>' if separator else ""
            parts.append(
                '<li class="approach-so__item">'
                f'<p class="approach-so__phrase">{self._formatted(phrase)}</p>'
                f"{why_html}</li>"
            )
            if index < len(self.items) - 1:
                parts.append('<li class="approach-so__between" aria-hidden="true"><span class="approach-so__dot"></span></li>')
        classes = f"approach-so {modifier}" if modifier else "approach-so"
        return f'<ul class="{classes}">{"".join(parts)}</ul>'

    @property
    def product_engineering_html(self) -> str:
        """A centred lead, three phrase and so-what columns, then a closing line of its own."""
        if not self.items:
            return ""
        lead, *rest = self.items
        parts = [
            '<div class="approach-pe-intro">',
            f'<p class="approach-principle__lead approach-principle__lead--center">{self._formatted(lead)}</p>',
        ]
        if len(rest) >= 3:
            parts.append(PrincipleBullets(tuple(rest[:3])).so_what_html("approach-so--pe-row"))
        closing = rest[3:] if len(rest) >= 3 else rest
        if closing:
            parts.append(PrincipleBullets(tuple(closing)).so_what_html("approach-so--solo"))
        parts.append("</div>")
        return "".join(parts)

    def _formatted(self, text: str) -> str:
        return _EMPHASIS.sub(r"<em>\1</em>", html.escape(text))


@dataclass(frozen=True)
class RefineBoard:
    """A context rail, the rewind and play buttons, and the three stage columns that open one at a time: the layout
    Iterate and Learn and each Product Engineering practice share. ``panels`` and ``openings`` hold each stage's
    example and the opening of its fidelity, by stage."""

    host_id: str
    rail_label: str
    panels: dict[str, str]
    openings: dict[str, str] = field(default_factory=dict)
    extra_content: str = ""
    extra_classes: str = ""
    rail_family: str = ""
    aria_label: str = ""
    role: str = "region"

    @property
    def html(self) -> str:
        classes = " ".join(part for part in ("approach-refine-row", "approach-stage-examples", self.extra_classes) if part)
        family = f" approach-grid__label--{html.escape(self.rail_family)}" if self.rail_family else ""
        return (
            f'<div class="{classes}" id="{html.escape(self.host_id)}" role="{html.escape(self.role)}" '
            f'aria-label="{html.escape(self.aria_label or f"{self.rail_label} refine stages")}">'
            '<div class="approach-refine__layout">'
            '<div class="approach-refine__context">'
            f'<button type="button" class="approach-window__stage approach-window__stage--context{family}" '
            'data-stage-id="context" aria-pressed="false">'
            f'<span class="approach-window__context-label">{html.escape(self.rail_label)}</span>'
            "</button></div>"
            '<div class="approach-refine__content">'
            f"{self.extra_content}"
            '<div class="approach-refine__board">'
            f"{_REFINE_TRANSPORT}"
            '<div class="approach-refine__stages">'
            f'<div class="approach-refine__heads">{"".join(self._head(column) for column in STAGE_COLUMNS)}</div>'
            f'<div class="approach-refine__openings">{"".join(self._opening(column) for column in STAGE_COLUMNS)}</div>'
            f'<div class="approach-refine__examples">{"".join(self._example(column) for column in STAGE_COLUMNS)}</div>'
            "</div></div></div></div></div>"
        )

    def _head(self, column: StageColumn) -> str:
        return (
            f'<button type="button" class="approach-window__stage" '
            f'data-stage-id="{html.escape(column.stage.name)}" aria-pressed="false" '
            f'aria-expanded="false">'
            f"{html.escape(column.stage.title)}</button>"
        )

    def _opening(self, column: StageColumn) -> str:
        opening = self.openings.get(column.stage.name, "")
        body = f'<div class="practice-fidelity__opening">{MarkdownHtml(opening).html}</div>' if opening else ""
        return f'<div class="approach-refine__opening" data-stage-id="{html.escape(column.stage.name)}">{body}</div>'

    def _example(self, column: StageColumn) -> str:
        stage = html.escape(column.stage.name)
        return self.panels.get(column.stage.name) or f'<div class="approach-refine__placeholder" data-stage-id="{stage}"></div>'


class ApproachGrids:
    """The boards drawn under the approach's principles and in its library, for a catalog's practices in the order of
    the practice catalogue, which each practice keeps as its position. On a project's approach page the examples are
    the project's own, under ``catalog_root``."""

    def __init__(
        self,
        practices: list,
        stages: tuple[StageCopy, ...],
        catalog_root: Path | None,
        project_examples: ProjectExampleSources | None = None,
    ) -> None:
        self.practices = sorted(practices, key=lambda practice: practice.position)
        self.stages = stages
        self.catalog_root = catalog_root
        self.project_examples = project_examples

    def html(self, kind: str) -> str:
        """The board a principle of ``kind`` draws: ``windows``, ``descriptions``, ``spec``, or ``tickets``."""
        if kind == "windows":
            return self.iterate_and_learn
        if kind == "descriptions":
            return self.product_engineering
        if kind == "spec":
            return self.spec
        return self.tickets

    @property
    def tickets(self) -> str:
        """Each practice's fidelities in the stage columns, each opening its fidelity page."""
        cells = [_LIBRARY_HEAD, *(self._column_head(column) for column in STAGE_COLUMNS)]
        for practice in self.practices:
            cells.append(self._label(practice))
            cells.extend(self._ticket(practice, column) for column in STAGE_COLUMNS)
        return f'<div class="approach-grid approach-grid--tickets">{"".join(cells)}</div>'

    @property
    def spec(self) -> str:
        cells = []
        for practice in self.practices:
            cells.append(self._label(practice))
            cells.append(f'<div class="approach-grid__cell">{html.escape(practice.spec_blurb)}</div>')
        return f'<div class="approach-grid approach-grid--span">{"".join(cells)}</div>'

    @property
    def iterate_and_learn(self) -> str:
        """The narrowing windows, with each stage's Stories example opening beneath them."""
        stages = {stage.id: stage for stage in self.stages}
        panels: dict[str, str] = {}
        openings: dict[str, str] = {}
        for stage_id in STAGE_COLUMNS.stages:
            panel = self._stage_panel(stages[stage_id]) if stage_id in stages else ""
            if panel:
                panels[stage_id] = panel
                openings[stage_id] = self._stories_opening(stage_id)
        board = RefineBoard(
            host_id="approach-stage-examples",
            rail_label="Context",
            panels=panels,
            openings=openings,
            extra_content=f'<div class="approach-windows__row">{self._windows}</div>',
            extra_classes="approach-windows",
            aria_label="Context feeds a narrowing window from Whole Solution to Story",
            role="img",
        )
        return board.html + self._monaco_scripts(panels)

    @property
    def product_engineering(self) -> str:
        """One refine board per practice, each stage column holding the practice's example at that stage."""
        boards: list[str] = []
        all_panels: dict[str, str] = {}
        for practice in self.practices:
            label = practice.product_engineering_label
            panels, openings = self._practice_panels(practice)
            all_panels.update({f"{practice.key}-{stage}": panel for stage, panel in panels.items()})
            boards.append(
                RefineBoard(
                    host_id=f"refine-row-{practice.key}",
                    rail_label=label,
                    rail_family=practice.perspective,
                    panels=panels,
                    openings=openings,
                    aria_label=f"{label} discovery, specification, and implementation",
                ).html
            )
        return f'<div class="approach-pe-rows" id="pe-engineering">{"".join(boards)}{self._monaco_scripts(all_panels)}</div>'

    @property
    def _windows(self) -> str:
        parts: list[str] = []
        for index, (shape, name, reach, pace, decides) in enumerate(_WINDOWS):
            if index:
                parts.append('<div class="approach-window__arrow" aria-hidden="true"></div>')
            bracket = f"{reach} - {pace}" if pace else reach
            parts.append(
                f'<div class="approach-window approach-window--{shape}">'
                '<div class="approach-window__shape"></div>'
                f'<div class="approach-window__name">{html.escape(name)}</div>'
                f'<div class="approach-window__width">({html.escape(bracket)})</div>'
                f'<div class="approach-window__detail">{html.escape(decides)}</div>'
                "</div>"
            )
        return "".join(parts)

    def _stage_panel(self, stage: StageCopy) -> str:
        example = StageExample(stage, self.project_examples)
        source = example.file(self.catalog_root)
        if source is None or not source.is_file():
            return ""
        return self._panel(stage.id, ExampleFile(source).panel_html(catalog_href=example.catalog_path))

    def _practice_panels(self, practice) -> tuple[dict[str, str], dict[str, str]]:
        panels: dict[str, str] = {}
        openings: dict[str, str] = {}
        for shown in practice.board_fidelities:
            relative = self.project_examples.file_for(practice.key, shown.stage) if self.project_examples else None
            examples = "".join(
                ExampleFile(path).panel_html(editor_id=self._editor_id(practice, path), catalog_href=relative)
                for path in self._practice_files(shown, relative)
            )
            panel = self._panel(shown.stage, examples)
            if panel:
                panels[shown.stage] = panel
                openings[shown.stage] = shown.opening
        return panels, openings

    def _editor_id(self, practice, path: Path) -> str:
        """Each code viewer on the page needs its own element id, made from its practice and file."""
        suffix = path.suffix.lstrip(".")
        return f"monaco-{Name(f'{practice.key}-{path.stem}-{suffix}').title_slug}"

    def _practice_files(self, shown: CatalogFidelity, relative: Path | None) -> list[Path]:
        if self.project_examples and self.catalog_root is not None:
            return [Path(self.catalog_root) / relative] if relative else []
        return shown.panel_example_files

    def _panel(self, stage_id: str, examples: str) -> str:
        """One stage's examples in an expandable column; empty when there are none."""
        if not examples:
            return ""
        return (
            f'<div class="approach-stage-column approach-stage-example" data-stage-id="{html.escape(stage_id)}">'
            f'<div class="approach-stage-column__body">{examples}</div></div>'
        )

    def _stories_opening(self, stage_id: str) -> str:
        """The opening of the fidelity at ``stage_id`` of the practice whose card says the approach's stage examples
        are its artifacts (Stories), among the practices the grids show."""
        stories = next((practice for practice in self.practices if practice.gives_stage_examples), None)
        shown = next((each for each in stories.shown_fidelities if each.stage == stage_id), None) if stories else None
        return shown.opening if shown is not None else ""

    def _monaco_scripts(self, panels: dict[str, str]) -> str:
        return MONACO_LOADER_SCRIPTS if any("catalog-monaco" in panel for panel in panels.values()) else ""

    def _label(self, practice) -> str:
        return (
            f'<a class="approach-grid__label approach-grid__label--{html.escape(practice.perspective)}" '
            f'href="{html.escape(practice.href)}">'
            f"{html.escape(practice.label)}</a>"
        )

    def _column_head(self, column: StageColumn) -> str:
        return (
            f'<div class="approach-grid__head"><span class="approach-grid__shape approach-grid__shape--{column.scope.shape}"></span>'
            f'<span class="approach-grid__head-title">{html.escape(column.label)}</span></div>'
        )

    def _ticket(self, practice, column: StageColumn) -> str:
        fidelity = practice.fidelity_in(column)
        if fidelity is None:
            return '<div class="approach-grid__ticket approach-grid__ticket--empty"></div>'
        return (
            f'<a class="approach-grid__ticket approach-grid__ticket--{html.escape(practice.perspective)}" '
            f'href="{html.escape(practice.fidelity_href(fidelity.fidelity))}">{html.escape(fidelity.label)}</a>'
        )


class ApproachPage:
    """The approach page's body and the pages it opens, for one catalog's practices. ``catalog_root`` is the catalog's
    folder; on a project's approach page the stage examples are the project's own, staged there."""

    def __init__(
        self,
        copy: ApproachCopy,
        practices: list,
        catalog_root: Path,
        project_examples: ProjectExampleSources | None = None,
    ) -> None:
        self.copy = copy
        self.catalog_root = Path(catalog_root)
        self.project_examples = project_examples
        self.grids = ApproachGrids(practices, copy.stages, catalog_root, project_examples)

    @property
    def body(self) -> str:
        """The page body; its stage examples' pages must already be written (``write_stage_example_pages``)."""
        first = self.copy.stages[0]
        details = "".join(f"<li>{html.escape(para)}</li>" for para in first.paras)
        cards = "".join(self._principle_card(number, principle) for number, principle in enumerate(self.copy.principles, 1))
        return (
            '<div class="approach-page" id="approach-page" tabindex="0" '
            f'data-stages="{self._stages_data}">'
            '<div class="approach-main" id="approach-main">'
            f'<div class="approach-stage-row" role="list">{"".join(self._stage_buttons)}</div>'
            '<section class="approach-detail" id="approach-detail" aria-live="polite">'
            f'<h2 class="approach-detail__title" id="approach-detail-title">'
            f"{html.escape(first.title)}</h2>"
            f'<ul class="approach-detail__body" id="approach-detail-body">{details}</ul>'
            "</section>"
            "</div>"
            '<aside class="approach-principles" id="approach-principles" aria-labelledby="approach-principles-heading">'
            '<h2 class="approach-principles__title" id="approach-principles-heading">'
            f"{html.escape(self.copy.principles_heading)}"
            "</h2>"
            f'<div class="approach-principles__list">{cards}</div>'
            "</aside>"
            '<section class="approach-library" aria-labelledby="approach-library-heading">'
            '<h2 class="approach-library__title" id="approach-library-heading">'
            f"{html.escape(self.copy.library_heading)}"
            "</h2>"
            f"{self.grids.tickets}"
            "</section>"
            "</div>"
            f"{_APPROACH_SCRIPT}"
        )

    def write_stage_example_pages(self) -> None:
        """Write each stage example's own page into ``examples/``, copying a practice example beside it."""
        folder = self.catalog_root / "examples"
        for stage in self.copy.stages:
            example = StageExample(stage, self.project_examples)
            if not example.exists:
                continue
            source = example.file(self.catalog_root)
            if self.project_examples is None:
                folder.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, folder / source.name)
            page = PageShell(
                title=f"{stage.title} — ABD Context Driven Delivery",
                h1=html.escape(stage.title),
                tagline=html.escape(source.name),
                body_inner=ExampleFile(source).stage_page_html,
                commons_prefix="../commons/",
                nav_prefix="../",
                body_wrap_class="approach-wrap",
            )
            (folder / f"{stage.id}.html").write_text(page.html, encoding="utf-8")

    @property
    def principle_pages(self) -> dict[str, str]:
        """Each principle's own page, and a coming-soon page for each practice the approach names but the catalog does
        not yet hold, by file name."""
        pages = {f"cdd-{principle.slug}.html": self._principle_page(principle) for principle in self.copy.principles}
        coming_soon = '<p class="approach-practice__para">Coming soon.</p>'
        pages.update({f"{slug}.html": self._article_page(title, coming_soon) for slug, title in _COMING_SOON})
        return pages

    def _principle_page(self, principle: PrincipleCopy) -> str:
        caption = f'<p class="approach-practice__para">{principle.caption}</p>' if principle.caption else ""
        paragraphs = PrincipleBullets(principle.bullets).paragraphs_html + caption
        return self._article_page(principle.title, f'<div class="approach-practice__body">{paragraphs}</div>')

    @property
    def _stage_buttons(self) -> list[str]:
        return [self._stage_button(index, stage) for index, stage in enumerate(self.copy.stages)]

    def _stage_button(self, index: int, stage: StageCopy) -> str:
        items = "".join(
            f'<li class="approach-stage__item kb-ticket aad-skill aad-fam-{html.escape(family)}">{html.escape(item)}</li>'
            for item, family in zip(stage.items, _ITEM_FAMILIES)
        )
        scope = stage.scope
        shape = (
            '<span class="kb-col-scope-shape-wrap approach-stage__scope">'
            f'<span class="kb-col-scope-shape kb-col-scope-shape--{html.escape(scope.shape)}" '
            f'aria-label="{html.escape(scope.name)}. {html.escape(scope.reach)}"></span>'
            '<span class="kb-col-shape-tooltip" role="tooltip">'
            f'<span class="kb-col-shape-tooltip__name">{html.escape(scope.name)}</span>'
            f'<span class="kb-col-shape-tooltip__width">{html.escape(scope.reach)}</span>'
            "</span></span>"
        )
        first = index == 0
        return (
            f'<div class="approach-stage{" is-active" if first else ""}" role="button" tabindex="0" '
            f'data-stage-index="{index}" data-stage-id="{html.escape(stage.id)}" '
            f'aria-pressed="{"true" if first else "false"}">'
            f'<span class="approach-stage__head">'
            f"{shape}"
            f'<span class="approach-stage__label">{html.escape(stage.title)}</span>'
            f"</span>"
            f'<ul class="approach-stage__items">{items}</ul>'
            "</div>"
        )

    @property
    def _stages_data(self) -> str:
        """The stages the page's script walks, with each stage example's page."""
        stages = [
            {
                "id": stage.id,
                "label": stage.title,
                "detail_title": stage.title,
                "items": list(stage.items),
                "paras": list(stage.paras),
                "example_href": StageExample(stage, self.project_examples).href(),
            }
            for stage in self.copy.stages
        ]
        return html.escape(json.dumps(stages), quote=True)

    def _principle_card(self, number: int, principle: PrincipleCopy) -> str:
        grid = self.grids.html(principle.kind)
        caption = (
            f'<aside class="approach-principle__caption"><p class="approach-principle__caption-body">{principle.caption}</p></aside>'
            if principle.caption
            else ""
        )
        return (
            f'<section class="approach-principle" data-principle="{html.escape(principle.slug)}">'
            f'<button type="button" class="approach-principle__toggle" aria-expanded="false">'
            f'<span class="approach-principle__num" aria-hidden="true">{number}</span>'
            f'<span class="approach-principle__copy">'
            f'<h3 class="approach-principle__title">{html.escape(principle.title)}</h3>'
            f"</span></button>"
            f'<div class="approach-principle__panel"><div class="approach-principle__panel-inner">'
            f"{self._bullets_html(principle)}{grid}{caption}</div></div>"
            "</section>"
        )

    def _bullets_html(self, principle: PrincipleCopy) -> str:
        bullets = PrincipleBullets(principle.bullets)
        if principle.slug == _ITERATE_AND_LEARN and principle.bullets:
            return (
                '<div class="approach-refine__layout approach-refine__layout--bullets">'
                '<div class="approach-refine__context" aria-hidden="true"></div>'
                f'{bullets.so_what_html("approach-so--stages")}'
                "</div>"
            )
        if principle.slug == _PRODUCT_ENGINEERING and principle.bullets:
            return bullets.product_engineering_html
        return bullets.list_html

    def _article_page(self, title: str, content: str) -> str:
        body = (
            '<article class="approach-practice">'
            f"{_BACK_LINK}"
            f'<h2 class="approach-practice__title">{html.escape(title)}</h2>'
            f"{content}"
            "</article>"
        )
        return PageShell(
            title=f"{title} — ABD Context Driven Delivery",
            h1=f'<span class="accent">{html.escape(title)}</span>',
            tagline="",
            body_inner=body,
            body_wrap_class="approach-wrap",
        ).html
