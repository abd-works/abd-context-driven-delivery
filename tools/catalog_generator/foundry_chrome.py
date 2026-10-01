"""Foundry chrome for the CDD catalog - page shells, commons copy, hub board.

Mirrors the abd-skills Foundry hub: hero, CDD tour panel, scope-shape column
heads, orange policy boxes, kebab-case tickets, Actions/Utilities strips.
Stage column heads that name a catalog example link to that example.
"""
from __future__ import annotations

import base64
import html
import json
import re
import shutil
import urllib.parse
import xml.etree.ElementTree as ET
import zlib
from pathlib import Path

_TEMPLATES = Path(__file__).resolve().parent / "templates"
_COMMONS_SRC = _TEMPLATES / "commons"
_DEFAULT_BRAND = _COMMONS_SRC / "brand"
_BRANDS_ROOT = _TEMPLATES / "brands"
_FOUNDRY_CSS_SRC = _TEMPLATES / "foundry-catalog.css"

# Stage columns — keys stay discovery/spec/engineer (code); labels are lowercase.
STAGES: tuple[tuple[str, str], ...] = (
    ("discovery", "discovery"),
    ("spec", "specification"),
    ("engineer", "implementation"),
)

# Scope shapes borrowed from Foundry: discovery←shaping, spec←exploration,
# engineer←engineering.
_STAGE_SCOPES: dict[str, dict[str, str]] = {
    "discovery": {
        "shape": "solution",
        "name": "Whole solution",
        "width": "wide / shallow",
        "bullets": "outcomes · scope · boundaries",
    },
    "spec": {
        "shape": "sprint",
        "name": "Sprint",
        "width": "narrow / deeper",
        "bullets": "behaviour · design · logic",
    },
    "engineer": {
        "shape": "story",
        "name": "Story",
        "width": "narrowest / deep",
        "bullets": "tests · code · interface",
    },
}

_STORY_EXAMPLES = (
    Path(__file__).resolve().parents[2] / "practices" / "stories" / "catalog-examples"
)


def approach_board_stages(path: str | Path | None = None) -> dict[str, dict]:
    """Stage chips and paragraphs keyed by board column, from approach markdown."""
    from catalog_generator.approach_copy import APPROACH_MARKDOWN, load_approach_copy

    source = Path(path) if path is not None else APPROACH_MARKDOWN
    copy = load_approach_copy(source)
    return {
        stage["board_key"]: stage
        for stage in copy.stages
        if stage.get("board_key")
    }


def stage_example_href(stage: dict, *, path_prefix: str = "") -> str:
    """Catalog page for a stage ``example:`` file under stories catalog-examples."""
    filename = (stage.get("example") or "").strip()
    if not filename or not (_STORY_EXAMPLES / filename).is_file():
        return ""
    return f"{path_prefix}examples/{stage['id']}.html"


def _board_stage(stages: dict[str, dict], stage_key: str) -> dict:
    return stages.get(stage_key) or {}

# Board rows under the CDD header: Stories → CE → UX → BDD → DDD.
FAMILY_ROW_ORDER: tuple[str, ...] = (
    "stories",
    "clean_engineering",
    "ux",
    "bdd",
    "ddd",
)

_FAM = {
    "cdd": "aad-fam-delivery",
    "stories": "aad-fam-sdd",
    "ddd": "aad-fam-ddd",
    "ux": "aad-fam-uxd",
    "clean_engineering": "aad-fam-arc",
    "bdd": "aad-fam-sdd",
}

_FAM_LABEL = {
    "cdd": "cdd",
    "stories": "sdd",
    "ddd": "ddd",
    "ux": "uxd",
    "clean_engineering": "arc",
    "bdd": "bdd",
}

# Kebab-case board labels (Foundry style).
_DISPLAY_LABELS: dict[str, str] = {
    "cdd": "context-driven-delivery",
    "stories": "stories",
    "clean_engineering": "clean-engineering",
    "ux": "user-experience",
    "bdd": "behavior-driven-development",
    "ddd": "domain-driven-design",
    "discovery": "discovery",
    "spec": "specification",
    "engineer": "implementation",
    "story_map": "story-map",
    "scenarios": "scenarios",
    "acceptance_tests": "acceptance-tests",
    "bounded_context": "bounded-context",
    "building_blocks": "building-blocks",
    "tactics": "tactics",
    "ia": "information-architecture",
    "mockup": "mockup",
    "front_end_code": "front-end-code",
    "modules": "modules",
    "model": "model",
    "code": "code",
    "behavior": "behavior",
    "development": "development",
}


def display_label(key: str) -> str:
    """Lowercase kebab-case for board tickets and practice rail chips."""
    if key in _DISPLAY_LABELS:
        return _DISPLAY_LABELS[key]
    return key.replace("_", "-").replace(" ", "-").strip().lower()


def family_class(toolset_name: str) -> str:
    return _FAM.get(toolset_name, "aad-fam-other")


def family_perspective(toolset_name: str) -> str:
    return _FAM_LABEL.get(toolset_name, "other")


_PRACTICE_BLURBS: dict[str, str] = {
    "stories": "Map user interactions to system behaviors, then define each through executable specifications.",
    "clean_engineering": "Highest quality software through modularized architecture and clean code that is resilient to change.",
    "ux": "Defining user impact from journey and information architecture to screen navigation.",
    "bdd": "Specify domain logic through behavioural, automated tests.",
    "ddd": "Organize the code around domain state, domain logic, and domain rules.",
}

_SPEC_BLURBS: dict[str, str] = {
    "stories": "Executable scenario-specifications with real-world examples",
    "clean_engineering": "Deep modules with explicit, narrow seams defined using code-level, type-safe contracts",
    "ux": "Interface mockups that work according to story specs and design templates",
    "bdd": "Nested describe/it behaviour tests that serve as both documentation and automated tests for domain logic",
    "ddd": "Templates that generate domain building blocks for the target architecture",
}

def approach_principle_grid(
    practices: list[dict],
    kind: str,
    *,
    approach_md_path: str | Path | None = None,
    stages: tuple[dict, ...] | list[dict] | None = None,
) -> str:
    """Static board under one approach principle. ``kind`` is descriptions, windows, spec, or tickets."""
    by_name = {t["toolset_name"]: t for t in practices}
    row_order = ("stories", "ddd", "ux", "clean_engineering", "bdd")
    rows = [by_name[name] for name in row_order if name in by_name]

    def practice_href(tool: dict) -> str:
        return tool.get("href") or f"context-tools/{tool['toolset_name']}.html"

    def label(tool: dict) -> str:
        fam = family_perspective(tool["toolset_name"])
        return (
            f'<a class="approach-grid__label approach-grid__label--{html.escape(fam)}" '
            f'href="{html.escape(practice_href(tool))}">'
            f'{html.escape(display_label(tool["toolset_name"]))}</a>'
        )

    cdd = by_name.get("cdd")
    cdd_href = html.escape(practice_href(cdd) if cdd else "context-tools/cdd.html")
    cdd_head = (
        f'<a class="approach-grid__label approach-grid__label--cdd" href="{cdd_href}">'
        "context-driven-delivery</a>"
    )

    if kind == "descriptions":
        return _product_engineering_grid(rows)

    if kind == "spec":
        body = []
        for tool in rows:
            body.append(label(tool))
            body.append(
                f'<div class="approach-grid__cell">{html.escape(_SPEC_BLURBS.get(tool["toolset_name"], ""))}</div>'
            )
        return f'<div class="approach-grid approach-grid--span">{"".join(body)}</div>'

    if kind == "windows":
        return _approach_windows_html(stages)

    if kind == "stages":
        board_stages = approach_board_stages(approach_md_path)
        heads = [cdd_head]
        details = []
        for stage_key, stage_label in STAGES:
            stage = _board_stage(board_stages, stage_key)
            fams = ("sdd", "uxd", "arc")
            chips = "".join(
                f'<li class="approach-grid__chip approach-grid__chip--{fams[i % 3]}">{html.escape(item)}</li>'
                for i, item in enumerate(stage.get("items") or ())
            )
            paras = "".join(
                f'<p>{html.escape(para)}</p>' for para in (stage.get("paras") or ())
            )
            shape = "solution" if stage_key == "discovery" else "sprint" if stage_key == "spec" else "story"
            heads.append(
                f'<div class="approach-grid__head"><span class="approach-grid__shape approach-grid__shape--{shape}"></span>'
                f'<span class="approach-grid__head-title">{html.escape(stage_label)}</span></div>'
            )
            details.append(f'<div class="approach-grid__stage"><ul>{chips}</ul>{paras}</div>')
        labels = "".join(label(tool) for tool in rows)
        return (
            '<div class="approach-grid approach-grid--stages">'
            + "".join(heads)
            + f'<div class="approach-grid__labels">{labels}</div>'
            + "".join(details)
            + "</div>"
        )

    heads = [cdd_head]
    for stage_key, stage_label in STAGES:
        shape = "solution" if stage_key == "discovery" else "sprint" if stage_key == "spec" else "story"
        heads.append(
            f'<div class="approach-grid__head"><span class="approach-grid__shape approach-grid__shape--{shape}"></span>'
            f'<span class="approach-grid__head-title">{html.escape(stage_label)}</span></div>'
        )
    body = heads
    for tool in rows:
        body.append(label(tool))
        for stage_key, _stage_label in STAGES:
            fid = (tool.get("fidelities") or {}).get(stage_key)
            if fid:
                body.append(
                    f'<a class="approach-grid__ticket approach-grid__ticket--{html.escape(family_perspective(tool["toolset_name"]))}" '
                    f'href="{html.escape(fid["href"])}">{html.escape(display_label(fid["key"]))}</a>'
                )
            else:
                body.append('<div class="approach-grid__ticket approach-grid__ticket--empty"></div>')
    return f'<div class="approach-grid approach-grid--tickets">{"".join(body)}</div>'


class Brand:
    """Named brand overlay for catalog commons."""

    def __init__(
        self,
        collection: Path | None = None,
        folder: Path | None = None,
    ) -> None:
        self.collection = Path(collection) if collection is not None else _BRANDS_ROOT
        self.folder = Path(folder) if folder is not None else None

    def folders(self) -> dict[str, Path]:
        folders = {"abd-works": _DEFAULT_BRAND}
        if not self.collection.is_dir():
            return folders
        for child in sorted(self.collection.iterdir()):
            if child.is_dir() and not child.name.startswith("."):
                folders[child.name] = child
        return folders

    def resolve(self, name: str) -> Path | None:
        if not name:
            return None
        candidate = Path(name)
        if candidate.is_dir():
            return candidate
        folders = self.folders()
        if name in folders:
            return folders[name]
        known = ", ".join(sorted(folders))
        raise ValueError(f"Unknown brand {name!r}. Known brands: {known}")

    def apply(self, commons_dest: Path) -> Path:
        source = self.folder if self.folder is not None else _DEFAULT_BRAND
        dest = Path(commons_dest) / "brand"
        dest.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, dest, dirs_exist_ok=True)
        return dest

    def apply_named(self, out_root: Path, name: str) -> Path:
        commons = Path(out_root) / "commons"
        commons.mkdir(parents=True, exist_ok=True)
        self.folder = self.resolve(name)
        return self.apply(commons)

    def copy_commons(self, out_root: Path) -> Path:
        dest = out_root / "commons"
        dest.mkdir(parents=True, exist_ok=True)
        shutil.copytree(_COMMONS_SRC, dest, dirs_exist_ok=True)
        shutil.copy2(_FOUNDRY_CSS_SRC, dest / "foundry-catalog.css")
        shutil.copy2(_TEMPLATES / "cdd-board.css", dest / "cdd-board.css")
        self.apply(dest)
        return dest


def page_shell(
    *,
    title: str,
    h1: str,
    tagline: str,
    body_inner: str,
    commons_prefix: str = "commons/",
    nav_prefix: str = "",
    nav_current: str = "",
    kanban_embed: str = "",
    extra_head: str = "",
    pre_hero: str = "",
    site_base: str = "https://abd.works/",
    show_hero: bool = True,
    body_wrap_class: str = "",
    after_tagline: str = "",
    subhead: str = "",
    after_subhead: str = "",
) -> str:
    """Wrap content in the Foundry catalog page chrome (nav + hero + scripts).

    Fidelity pages set ``show_hero=False`` so the board leads and the title /
    invoke / guidance sit in ``body_inner`` under the kanban (Foundry skill
    detail pattern).
    """
    hero = ""
    if show_hero:
        lead = f'\n          <p class="body-lead">{tagline}</p>' if tagline.strip() else ""
        if subhead.strip():
            lead += (
                f'\n          <p class="page-hero__subhead">{html.escape(subhead)}</p>'
            )
        if after_subhead.strip():
            lead += (
                f'\n          <p class="body-lead page-hero__repo">{after_subhead}</p>'
            )
        after = after_tagline.strip()
        title_bar = (
            f'\n          <div class="page-hero__title-bar">'
            f'\n            <h1 class="page-headline">{h1}</h1>'
            f'\n            {after}'
            f"\n          </div>"
            if after
            else f'\n          <h1 class="page-headline">{h1}</h1>'
        )
        hero = f"""
<div class="page-hero page-hero--foundry">
  <div class="wrap">
    <table class="page-hero__table" role="presentation">
      <tr>
        <td class="page-hero__cell page-hero__cell--title">{title_bar}{lead}
        </td>
      </tr>
    </table>
  </div>
</div>
"""
    body_wrap = "wrap"
    if body_wrap_class:
        body_wrap = f"wrap {body_wrap_class.strip()}"
    drawio_script = ""
    if (
        "data-mxgraph" in body_inner
        or "approach-stage-examples" in body_inner
        or "approach-refine-row" in body_inner
    ):
        drawio_script = (
            f'<script src="{commons_prefix}catalog-drawio.js?v=cdd-117"></script>'
        )
        if "data-mxgraph" in body_inner:
            drawio_script = (
                '<script src="https://viewer.diagrams.net/js/viewer-static.min.js"></script>'
                + drawio_script
            )
        if "approach-refine-row" in body_inner or "approach-stage-examples" in body_inner:
            drawio_script += (
                f'<script src="{commons_prefix}catalog-refine-row.js?v=cdd-2"></script>'
            )
    return f"""<!DOCTYPE html>
<html lang="en" data-theme="engineering" data-abd-theme="engineering">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<script>
(function(){{try{{if('scrollRestoration' in history)history.scrollRestoration='manual';var r=new URLSearchParams(location.search).get('kanbanScroll');if(!r)return;var y=parseFloat(r);if(isNaN(y))return;window.__foundryPendingScrollY=y;document.documentElement.classList.add('foundry-scroll-pending');}}catch(e){{}}}})();
</script>
<title>{html.escape(title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{commons_prefix}site.css?v=foundry-33">
<link rel="stylesheet" href="{commons_prefix}foundry-catalog.css?v=cdd-133">
<link rel="stylesheet" href="{commons_prefix}cdd-board.css?v=cdd-31">
{extra_head}
<script src="{commons_prefix}catalog-nav.js?v=foundry-13"></script>
</head>
<body data-nav-prefix="{html.escape(nav_prefix)}" data-nav-current="{html.escape(nav_current)}" data-nav-site-base="{html.escape(site_base)}">
<main id="main-content">
{pre_hero}
{hero}
{kanban_embed}
<div class="catalog-body">
<div class="{html.escape(body_wrap)}">
{body_inner}
</div>
</div>
</main>
<script src="{commons_prefix}catalog-foundry-skill-nav.js?v=cdd-16"></script>
{drawio_script}
</body>
</html>
"""


def _ticket(
    label: str,
    href: str,
    fam: str,
    *,
    stage: str = "",
    perspective: str = "",
    current: bool = False,
) -> str:
    classes = f"kb-ticket aad-skill {fam}"
    if current:
        classes += " kb-ticket--current"
    data = ""
    if stage:
        data += f' data-stage="{html.escape(stage)}"'
    if perspective:
        data += f' data-perspective="{html.escape(perspective)}"'
    safe_label = html.escape(label)
    return (
        f'<a class="{classes}"{data} href="{html.escape(href)}">'
        f'<span class="kb-skill-tooltip-wrap">{safe_label}'
        f'<span class="kb-col-shape-tooltip kb-skill-tooltip" role="tooltip">'
        f'<span class="kb-col-shape-tooltip__name">{safe_label}</span>'
        f"</span></span></a>"
    )


def _family_toggle(display_name: str, toolset_name: str, href: str, *, header: bool = False) -> str:
    """Practice-rail chip — opens that practice page. Does not filter the board."""
    fam = family_class(toolset_name)
    persp = family_perspective(toolset_name)
    extra = " foundry-practice-col__card--header" if header else ""
    return (
        f'<a class="kb-ticket aad-skill {fam} foundry-practice-col__card '
        f'foundry-perspective-label foundry-family-toggle foundry-perspective-label--{persp}{extra}" '
        f'data-family="{html.escape(toolset_name)}" data-perspective="{persp}" '
        f'href="{html.escape(href)}" aria-pressed="false">{html.escape(display_name)}</a>'
    )


def _scope_shape_html(stage_key: str) -> str:
    scope = _STAGE_SCOPES[stage_key]
    shape = scope["shape"]
    name = scope["name"]
    width = scope["width"]
    bullets = scope["bullets"]
    title = f"{name} — {width} — {bullets}"
    aria = f"{name}. {width}. {bullets.replace(' · ', ', ')}"
    return (
        f'<span class="kb-col-scope-shape-wrap">'
        f'<span class="kb-col-scope-shape kb-col-scope-shape--{html.escape(shape)}" '
        f'title="{html.escape(title)}" aria-label="{html.escape(aria)}"></span>'
        f'<span class="kb-col-shape-tooltip" role="tooltip">'
        f'<span class="kb-col-shape-tooltip__name">{html.escape(name)}</span>'
        f'<span class="kb-col-shape-tooltip__width">{html.escape(width)}</span>'
        f'<span class="kb-col-shape-tooltip__bullets">{html.escape(bullets)}</span>'
        f"</span></span>"
    )


def _stage_col_detail_html(stage_key: str, stages: dict[str, dict]) -> str:
    """Approach chips + write-ups shown inside each column during tour stage 1."""
    stage = _board_stage(stages, stage_key)
    fams = ("sdd", "uxd", "arc")
    chips = "".join(
        f'<li class="tour-stage-detail__chip tour-stage-detail__chip--{fams[i % 3]}">'
        f"{html.escape(item)}</li>"
        for i, item in enumerate(stage.get("items") or ())
    )
    paras = "".join(
        f'<p class="tour-stage-detail__desc">{html.escape(para)}</p>'
        for para in (stage.get("paras") or ())
    )
    return (
        f'<div class="tour-stage-detail" data-stage-detail="{html.escape(stage_key)}">'
        f'<ul class="tour-stage-detail__chips">{chips}</ul>'
        f'{paras}'
        f"</div>"
    )


def _stage_questions_html(
    practices: list[dict],
    stages: dict[str, dict],
    *,
    path_prefix: str = "",
) -> str:
    by_name = {t["toolset_name"]: t for t in practices}
    cdd = by_name.get("cdd") or {}
    cells = [
        '<div class="kanban-stage-questions__spacer">'
        '<button type="button" class="policy-boxes-toggle" aria-expanded="false" '
        'aria-label="Show stage policies">'
        '<svg viewBox="0 0 16 16" width="14" height="14" aria-hidden="true">'
        '<path d="M3 6l5 5 5-5" fill="none" stroke="currentColor" '
        'stroke-width="1.75" stroke-linecap="square" stroke-linejoin="miter"/>'
        "</svg></button></div>"
    ]
    for stage_key, _ in STAGES:
        stage = _board_stage(stages, stage_key)
        items = "".join(
            f'<li class="kanban-stage-questions__item">{html.escape(item)}</li>'
            for item in (stage.get("items") or ())
        )
        paras = "".join(
            f'<p class="kanban-stage-questions__desc">{html.escape(para)}</p>'
            for para in (stage.get("paras") or ())
        )
        fid = (cdd.get("fidelities") or {}).get(stage_key)
        href = path_prefix + (fid["href"] if fid else f"fidelities/cdd-{stage_key}.html")
        cells.append(
            f'<a class="kanban-stage-questions__cell" data-stage="{html.escape(stage_key)}" '
            f'href="{html.escape(href)}">'
            f'<ul class="kanban-stage-questions__list">{items}</ul>'
            f'{paras}'
            f"</a>"
        )
    return (
        '<div class="kanban-stage-questions kanban-stage-questions--foundry '
        'kanban-stage-questions--cdd is-collapsed" data-id="stage-questions">'
        + "".join(cells)
        + "</div>"
    )


def _cdd_tour_panel_html() -> str:
    return """
  <div class="foundry-travel-ring" id="travel-ring" aria-hidden="true"></div>
  <div class="foundry-cdd-panel" id="foundry-guide">
    <div class="foundry-cdd-panel__head">
      <button type="button" class="foundry-cdd-btn" id="cdd-toggle" aria-label="Start Context-Driven Delivery tour">Start tour</button>
      <button type="button" class="foundry-cdd-advance" id="tour-advance" aria-label="Advance tour">→</button>
      <span class="foundry-cdd-panel__hint" id="guide-tag">to advance</span>
    </div>
    <div class="foundry-cdd-intro" id="cdd-intro">
      <p class="foundry-cdd-intro__line1">Speed is not governed by coding speed. It is governed by <strong>coordination cost</strong> and <strong>cognitive load</strong>.</p>
      <p class="foundry-cdd-intro__line2"><strong>Context-Driven Delivery</strong> is the practice of transforming organizational knowledge into assets that are machine-readable and machine executable.</p>
    </div>
    <div class="foundry-guide__body" id="guide-text" aria-live="polite"></div>
  </div>
"""


def render_hub_board(
    practices: list[dict],
    actions: list[dict],
    utilities: list[dict],
    *,
    highlight_tool: str | None = None,
    highlight_fidelity: str | None = None,
    path_prefix: str = "",
    initial_family: str | None = None,
    approach_md_path: str | Path | None = None,
) -> str:
    """Build the Foundry-style stage×tool kanban + policies + Actions/Utilities."""
    board_stages = approach_board_stages(approach_md_path)
    by_name = {t["toolset_name"]: t for t in practices}
    ordered = [by_name[n] for n in FAMILY_ROW_ORDER if n in by_name]
    for t in practices:
        if t["toolset_name"] == "cdd":
            continue
        if t["toolset_name"] not in {x["toolset_name"] for x in ordered}:
            ordered.append(t)

    cdd_tool = by_name.get("cdd")
    cdd_tool_href = path_prefix + (cdd_tool["href"] if cdd_tool else "context-tools/cdd.html")

    practice_bits = [
        _family_toggle(
            display_label(tool["toolset_name"]),
            tool["toolset_name"],
            path_prefix + tool["href"],
            header=False,
        )
        for tool in ordered
    ]

    cols = []
    for stage_key, stage_label in STAGES:
        rows = []
        for tool in ordered:
            fid = tool["fidelities"].get(stage_key)
            fam = family_class(tool["toolset_name"])
            persp = family_perspective(tool["toolset_name"])
            if fid:
                current = (
                    highlight_tool == tool["toolset_name"]
                    and highlight_fidelity == fid["key"]
                )
                ticket = _ticket(
                    display_label(fid["key"]),
                    path_prefix + fid["href"],
                    fam,
                    stage=stage_key,
                    perspective=persp,
                    current=current,
                )
                empty = ""
            else:
                ticket = ""
                empty = " aad-skill-row--empty"
            rows.append(
                f'<div class="aad-skill-row {fam}{empty}" '
                f'data-family="{html.escape(tool["toolset_name"])}">{ticket}</div>'
            )
        active = ""
        cdd_fid = (cdd_tool or {}).get("fidelities", {}).get(stage_key)
        if highlight_tool == "cdd" and highlight_fidelity and cdd_fid:
            if cdd_fid.get("key") == highlight_fidelity:
                active = " active"
        elif highlight_tool and highlight_fidelity:
            hit = (by_name.get(highlight_tool) or {}).get("fidelities", {}).get(stage_key)
            if hit and hit.get("key") == highlight_fidelity:
                active = " active"

        stage_current = " kb-col-head--current" if active else ""
        stage_meta = _board_stage(board_stages, stage_key)
        example_href = stage_example_href(stage_meta, path_prefix=path_prefix)
        label = html.escape(stage_label)
        if example_href:
            title = (
                f'<a class="kb-col-head-title__link" href="{html.escape(example_href)}">{label}</a>'
            )
        else:
            title = f"<span>{label}</span>"
        cols.append(
            f'<div class="kb-col{active}" data-id="col-{stage_key}" data-stage="{stage_key}">'
            f'<div class="kb-col-head{stage_current}">'
            f'<div class="kb-col-head-row">'
            f"{_scope_shape_html(stage_key)}"
            f'<span class="kb-col-head-title">{title}</span>'
            f"</div></div>"
            f"{_stage_col_detail_html(stage_key, board_stages)}"
            f'{"".join(rows)}'
            f"</div>"
        )

    action_tickets = "".join(
        _ticket(display_label(a["name"]), path_prefix + a["href"], "aad-fam-supporting")
        for a in actions
    )
    utility_tickets = "".join(
        _ticket(display_label(u["name"]), path_prefix + u["href"], "aad-fam-foundational")
        for u in utilities
    )

    attrs = ' data-cdd-always-expanded="1" data-cdd-no-stage-filter="1"'
    if initial_family and initial_family != "cdd":
        attrs += f' data-initial-family="{html.escape(initial_family)}"'
    if highlight_fidelity and highlight_tool and highlight_tool != "cdd":
        for stage_key, _ in STAGES:
            hit = (by_name.get(highlight_tool) or {}).get("fidelities", {}).get(stage_key)
            if hit and hit.get("key") == highlight_fidelity:
                attrs += f' data-initial-stage="{html.escape(stage_key)}"'
                break

    cdd_head = (
        f'<a class="kb-ticket aad-skill aad-fam-delivery foundry-practice-col__card '
        f'foundry-practice-col__card--header foundry-practice-col__cdd-head '
        f'foundry-perspective-label foundry-perspective-label--cdd" '
        f'data-perspective="cdd" '
        f'href="{html.escape(cdd_tool_href)}">{html.escape(display_label("cdd"))}</a>'
    )
    practice_col = (
        '<div class="foundry-practice-col" aria-label="Context tools">'
        + cdd_head
        + "".join(practice_bits)
        + "</div>"
    )

    stage_questions = _stage_questions_html(
        practices, board_stages, path_prefix=path_prefix
    )

    return f"""
<div class="wrap">
<div class="foundry-kanban-shell" id="kanban-shell">
<section class="foundry-kanban-surface foundry-skills-expanded catalog-kanban-embed foundry-kanban-surface--cdd-always-expanded" id="catalog-kanban" aria-label="CDD catalog board"{attrs}>
  <div class="foundry-board-grid foundry-board-grid--cdd" id="board">
    {practice_col}
    {"".join(cols)}
  </div>
  {stage_questions}
  <div class="foundry-skills-extra">
    <div class="foundry-skills-extra__inner">
      <div class="aad-delivery-crosscut-stack" data-id="crosscut">
        <section class="aad-delivery-crosscut-section aad-delivery-crosscut-section--supporting is-filter-visible">
          <h3 class="aad-delivery-crosscut-section-title">Actions</h3>
          <div class="aad-delivery-crosscut-section-body">
            <div class="aad-delivery-crosscut-row aad-crosscut-tier--practice is-filter-visible" data-crosscut-group="kanban" data-family="kanban">
              <span class="aad-delivery-crosscut-row-label aad-delivery-crosscut-row-label--spacer" aria-hidden="true"></span>
              <div class="aad-delivery-crosscut-skills is-skills-visible">{action_tickets}</div>
            </div>
          </div>
        </section>
        <section class="aad-delivery-crosscut-section aad-delivery-crosscut-section--foundational is-filter-visible">
          <h3 class="aad-delivery-crosscut-section-title">Utilities</h3>
          <div class="aad-delivery-crosscut-section-body">
            <div class="aad-delivery-crosscut-row aad-crosscut-tier--foundational is-filter-visible" data-crosscut-group="tools">
              <span class="aad-delivery-crosscut-row-label aad-delivery-crosscut-row-label--spacer" aria-hidden="true"></span>
              <div class="aad-delivery-crosscut-skills is-skills-visible">{utility_tickets}</div>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</section>
</div>
</div>
"""


def details_block(title: str, body: str, *, open_default: bool = False) -> str:
    op = " open" if open_default else ""
    return f"<details{op}><summary>{html.escape(title)}</summary>\n{body}\n</details>"


_GUIDANCE_BODY_RE = re.compile(
    r"(<h[1-4]>Guidance</h[1-4]>)(.*?)(?=<h[1-4]>|\Z)",
    re.DOTALL,
)


def wrap_guidance_body(html_text: str) -> str:
    """Mark the Guidance section so its bold lead-ins can be colored apart from Rules."""

    def repl(match: re.Match) -> str:
        return (
            f"{match.group(1)}"
            f'<div class="fidelity-guidance-body">{match.group(2)}</div>'
        )

    return _GUIDANCE_BODY_RE.sub(repl, html_text)


def catalog_examples_html(module_dir: Path, fidelity_key: str) -> str:
    """Collapsible Examples block for ``{practice}/catalog-examples/{fidelity}.*``.

    Every file with that stem is shown. Markdown renders as HTML, Draw.io
    opens in the diagrams.net viewer, images render as ``<img>``, and other
    text files stay as source.
    """
    folder = Path(module_dir) / "catalog-examples"
    if not folder.is_dir() or not fidelity_key:
        return ""
    files = sorted(
        (path for path in folder.iterdir() if path.is_file() and path.stem == fidelity_key),
        key=lambda path: (_EXAMPLE_SUFFIX_ORDER.get(path.suffix.lower(), 50), path.name),
    )
    if not files:
        return ""
    parts = [_render_catalog_example(path) for path in files]
    return (
        '<details class="catalog-examples">'
        "<summary>Examples</summary>"
        f'<div class="catalog-examples__body">{"".join(parts)}</div>'
        "</details>"
    )


_EXAMPLE_SUFFIX_ORDER = {
    ".md": 0,
    ".markdown": 0,
    ".ts": 1,
    ".tsx": 1,
    ".html": 1,
    ".htm": 1,
    ".drawio": 2,
    ".dio": 2,
    ".png": 3,
    ".jpg": 3,
    ".jpeg": 3,
    ".gif": 3,
    ".webp": 3,
    ".svg": 3,
}

_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
_IMAGE_MIME = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
    ".svg": "image/svg+xml",
}


def _render_catalog_example(path: Path) -> str:
    suffix = path.suffix.lower()
    name = html.escape(path.name)
    if suffix in (".md", ".markdown"):
        body = _render_example_markdown(path.read_text(encoding="utf-8"))
        inner = f'<div class="skill-md-preview">{body}</div>'
    elif suffix in (".html", ".htm"):
        srcdoc = html.escape(path.read_text(encoding="utf-8"), quote=True)
        inner = (
            f'<iframe class="catalog-example__frame" title="{name}" '
            f'sandbox="" srcdoc="{srcdoc}"></iframe>'
        )
    elif suffix in (".drawio", ".dio"):
        src = html.escape(_drawio_viewer_url(path.read_text(encoding="utf-8")), quote=True)
        inner = (
            f'<iframe class="catalog-drawio-frame" title="{name}" loading="lazy" src="{src}"></iframe>'
        )
    elif suffix in _IMAGE_SUFFIXES:
        mime = _IMAGE_MIME[suffix]
        payload = base64.b64encode(path.read_bytes()).decode("ascii")
        inner = (
            f'<img class="catalog-example__image" alt="{name}" '
            f'src="data:{mime};base64,{payload}">'
        )
    else:
        lang = html.escape(suffix.lstrip(".") or "text")
        source = html.escape(path.read_text(encoding="utf-8"))
        inner = (
            '<div class="skill-code-preview">'
            f'<div class="skill-code-lang">{lang}</div>'
            f"<pre><code>{source}</code></pre>"
            "</div>"
        )
    return (
        '<figure class="catalog-example">'
        f'<figcaption class="catalog-example__name">{name}</figcaption>'
        f"{inner}"
        "</figure>"
    )


def _render_example_markdown(text: str) -> str:
    body = _strip_markdown_frontmatter(text).strip()
    while body.startswith("---") and not body.startswith("----"):
        body = body[3:].lstrip("\n")
    lines = [line for line in body.splitlines() if line.strip()]
    indented = sum(1 for line in lines if line[:1].isspace())
    has_markup = any(line.lstrip().startswith(("#", "|")) for line in lines)
    if lines and not has_markup and indented >= len(lines) / 2:
        return f'<pre class="catalog-example__tree">{html.escape(body.strip())}</pre>'
    return markdown_to_html(body, include_tables=True)


def _strip_markdown_frontmatter(text: str) -> str:
    if not text.startswith("---"):
        return text
    end = text.find("\n---", 3)
    if end == -1:
        return text
    return text[end + 4 :].lstrip("\n")


_DRAWIO_FRAME_MARGIN = 20


def _drawio_page_size(xml: str) -> tuple[int, int]:
    try:
        model = ET.fromstring(xml).find(".//mxGraphModel")
    except ET.ParseError:
        return 1080, 919
    if model is None:
        return 1080, 919
    width = int(float(model.get("pageWidth") or 1080))
    height = int(float(model.get("pageHeight") or 919))
    return width, height


def _drawio_content_size(xml: str, margin: int = _DRAWIO_FRAME_MARGIN) -> tuple[int, int]:
    """Native pixel box that covers every placed cell and the page."""
    page_w, page_h = _drawio_page_size(xml)
    try:
        root = ET.fromstring(xml)
    except ET.ParseError:
        return page_w, page_h
    xs: list[float] = [0.0, float(page_w)]
    ys: list[float] = [0.0, float(page_h)]
    for cell in root.iter("mxCell"):
        geom = cell.find("mxGeometry")
        if geom is None or geom.get("x") is None:
            continue
        left = float(geom.get("x") or 0)
        top = float(geom.get("y") or 0)
        xs.extend((left, left + float(geom.get("width") or 0)))
        ys.extend((top, top + float(geom.get("height") or 0)))
    width = int(max(xs) - min(xs) + margin * 2)
    height = int(max(ys) - min(ys) + margin * 2)
    return max(page_w, width), max(page_h, height)



def _drawio_frame_viewport(xml: str, margin: int = _DRAWIO_FRAME_MARGIN) -> str:
    """Park diagram cells on the top-left page edge and resize the page to fit."""
    try:
        root = ET.fromstring(xml)
    except ET.ParseError:
        return xml
    placed: list[ET.Element] = []
    for cell in root.iter("mxCell"):
        cell_id = cell.get("id") or ""
        if cell_id in ("0", "1"):
            continue
        geom = cell.find("mxGeometry")
        if geom is None or geom.get("x") is None:
            continue
        placed.append(geom)
    if not placed:
        return xml
    left = min(float(geom.get("x") or 0) for geom in placed)
    top = min(float(geom.get("y") or 0) for geom in placed)
    right = max(float(geom.get("x") or 0) + float(geom.get("width") or 0) for geom in placed)
    bottom = max(float(geom.get("y") or 0) + float(geom.get("height") or 0) for geom in placed)
    shift_x = margin - left
    shift_y = margin - top
    for geom in placed:
        geom.set("x", str(int(float(geom.get("x") or 0) + shift_x)))
        geom.set("y", str(int(float(geom.get("y") or 0) + shift_y)))
    model = root.find(".//mxGraphModel")
    if model is not None:
        model.set("pageWidth", str(int(right - left + margin * 2)))
        model.set("pageHeight", str(int(bottom - top + margin * 2)))
    return ET.tostring(root, encoding="unicode")


def _drawio_viewer_url(xml: str) -> str:
    compressor = zlib.compressobj(9, zlib.DEFLATED, -15)
    raw = compressor.compress(xml.encode("utf-8")) + compressor.flush()
    token = urllib.parse.quote(base64.b64encode(raw).decode("ascii"), safe="")
    return (
        "https://viewer.diagrams.net/?lightbox=1&nav=1&layers=1&toolbar=zoom"
        f"&edit=_blank#R{token}"
    )


def _drawio_framed_viewer_url(xml: str) -> str:
    compressor = zlib.compressobj(9, zlib.DEFLATED, -15)
    raw = compressor.compress(xml.encode("utf-8")) + compressor.flush()
    token = urllib.parse.quote(base64.b64encode(raw).decode("ascii"), safe="")
    return (
        "https://viewer.diagrams.net/?lightbox=1&nav=0&layers=1&toolbar=0"
        f"&edit=_blank#R{token}"
    )


def _drawio_story_map_viewer_url(xml: str) -> str:
    compressor = zlib.compressobj(9, zlib.DEFLATED, -15)
    raw = compressor.compress(xml.encode("utf-8")) + compressor.flush()
    token = urllib.parse.quote(base64.b64encode(raw).decode("ascii"), safe="")
    return (
        "https://viewer.diagrams.net/?lightbox=1&nav=0&layers=1&toolbar=0"
        f"&edit=_blank#R{token}"
    )


def _drawio_iframe(path: Path, *, zoom_left: bool = False) -> str:
    xml = path.read_text(encoding="utf-8")
    name = html.escape(path.name)
    display_xml = _drawio_frame_viewport(xml) if path.stem == "story_map" else xml
    viewer_url = (
        _drawio_story_map_viewer_url(display_xml)
        if path.stem == "story_map"
        else _drawio_framed_viewer_url(display_xml)
    )
    src = html.escape(viewer_url, quote=True)
    kind = (
        " approach-stage-drawio--story-map"
        if path.stem == "story_map"
        else " approach-stage-drawio--framed"
    )
    page_w, page_h = (
        _drawio_page_size(display_xml)
        if path.stem == "story_map"
        else _drawio_content_size(display_xml)
    )
    return (
        f'<div class="approach-stage-drawio-zoom skill-drawio-wrap approach-stage-drawio{kind}" '
        f'data-page-w="{page_w}" data-page-h="{page_h}">'
        f'<div class="approach-stage-drawio__scale">'
        f'<iframe class="catalog-drawio-frame" title="{name}" '
        f'width="{page_w}" height="{page_h}" '
        f'style="width:{page_w}px;height:{page_h}px;max-width:none" '
        f'data-src="{src}"></iframe>'
        "</div></div>"
    )


def _stories_stage_overview(stage_id: str) -> str:
    stage_key = {"discovery": "discovery", "specification": "spec", "implementation": "engineer"}.get(stage_id, "")
    if not stage_key:
        return ""
    guide = Path(__file__).resolve().parents[2] / "practices" / "stories" / "stories.md"
    if not guide.is_file():
        return ""
    for item in _practice_fidelities(guide.read_text(encoding="utf-8")):
        if item["stage"] == stage_key:
            return item["opening"]
    return ""


_STEP_LINE = re.compile(r"^\s*(?:given|when|then|\.(?:and|but))\s*\(")
_MONACO_LANG = {
    ".ts": "typescript",
    ".tsx": "typescript",
    ".js": "javascript",
    ".jsx": "javascript",
    ".py": "python",
    ".html": "html",
    ".htm": "html",
}


def step_fold_ranges(source: str) -> list[tuple[int, int]]:
    """1-based inclusive line ranges for Given/When/Then/And/But callback bodies.

    The start line is the step signature. The end line closes the callback.
    A step that fits on one line is left unfolded.
    """
    lines = source.splitlines()
    ranges: list[tuple[int, int]] = []
    index = 0
    while index < len(lines):
        if not _STEP_LINE.match(lines[index]):
            index += 1
            continue
        end = _callback_end_line(lines, index)
        if end is not None and end > index:
            ranges.append((index + 1, end + 1))
            index = end + 1
        else:
            index += 1
    return ranges


_STORY_LINE = re.compile(r"^\s*story\s*\(")
_SCENARIO_LINE = re.compile(r"^\s*scenario\s*\(")
_STORY_COMMENT = re.compile(r"\*\s*Story:")


def scenario_step_fold_ranges(source: str) -> list[tuple[int, int]]:
    """Fold acceptance-test scaffolding and step bodies; keep story, scenario, and steps visible."""
    lines = source.splitlines()
    ranges = list(step_fold_ranges(source))

    story_idx = next((i for i, line in enumerate(lines) if _STORY_LINE.match(line)), None)
    scenario_idx = next((i for i, line in enumerate(lines) if _SCENARIO_LINE.match(line)), None)
    first_step_idx = next((i for i, line in enumerate(lines) if _STEP_LINE.match(line)), None)

    if story_idx is not None:
        story_comment_idx = next(
            (i for i in range(story_idx) if _STORY_COMMENT.search(lines[i])),
            None,
        )
        if story_comment_idx is not None and story_comment_idx < story_idx - 1:
            ranges.append((story_comment_idx + 2, story_idx))
        elif story_idx > 0:
            ranges.append((1, story_idx))

    if (
        scenario_idx is not None
        and first_step_idx is not None
        and first_step_idx > scenario_idx + 1
    ):
        ranges.append((scenario_idx + 1, first_step_idx))

    last_step_end = None
    index = 0
    while index < len(lines):
        if not _STEP_LINE.match(lines[index]):
            index += 1
            continue
        end = _callback_end_line(lines, index)
        if end is not None:
            last_step_end = end
            index = end + 1
        else:
            index += 1
    return sorted({(start, end) for start, end in ranges if end >= start})


def _acceptance_test_folds(source: str) -> list[tuple[int, int]] | None:
    lines = source.splitlines()
    has_story = any(_STORY_LINE.match(line) for line in lines)
    has_scenario = any(_SCENARIO_LINE.match(line) for line in lines)
    if has_story and has_scenario:
        return scenario_step_fold_ranges(source)
    return None


_CLASS_LINE = re.compile(r"^export class (\w+)")
_CONST_OBJECT_LINE = re.compile(r"^export const \w+ = \{")
_INTERFACE_LINE = re.compile(r"^export interface \w+")
_FUNCTION_LINE = re.compile(r"^function \w+")
_METHOD_LINE = re.compile(
    r"^\s+(?:public |private |protected |readonly |static |async |get |set )*"
    r"(?:constructor|[A-Za-z_]\w*)\s*(?:<[^>\n]*>)?\s*\("
)
_OPEN_TYPE_NAMES = {"Customer", "AccountCredentials"}


def ddd_class_fold_ranges(source: str) -> list[tuple[int, int]]:
    """Fold a DDD tactics file to open aggregates and collapsed neighbors.

    ``Customer`` and ``AccountCredentials`` stay open at the class level, with
    each operation body folded. Other classes, const objects, interfaces, and
    helpers fold to their declaration.
    """
    lines = source.splitlines()
    ranges: list[tuple[int, int]] = []
    for index, line in enumerate(lines):
        class_match = _CLASS_LINE.match(line)
        foldable = bool(
            class_match or _CONST_OBJECT_LINE.match(line) or _INTERFACE_LINE.match(line) or _FUNCTION_LINE.match(line)
        )
        if not foldable:
            continue
        end = _brace_end_line(lines, index)
        if end is None or end <= index:
            continue
        name = class_match.group(1) if class_match else ""
        previous = lines[index - 1].strip() if index else ""
        keep_open = name in _OPEN_TYPE_NAMES or (class_match is not None and "Root" in previous)
        if keep_open:
            cursor = index + 1
            while cursor < end:
                if _METHOD_LINE.match(lines[cursor]):
                    method_end = _brace_end_line(lines, cursor)
                    if method_end is not None and method_end > cursor:
                        ranges.append((cursor + 1, method_end + 1))
                        cursor = method_end + 1
                        continue
                cursor += 1
        else:
            ranges.append((index + 1, end + 1))
    return ranges


def _brace_end_line(lines: list[str], start: int) -> int | None:
    text = "\n".join(lines[start:])
    opened = _first_brace(text)
    if opened is None:
        return None
    closed = _matching_brace(text, opened)
    if closed is None:
        return None
    return start + text.count("\n", 0, closed)


def _first_brace(text: str) -> int | None:
    index = 0
    length = len(text)
    while index < length:
        char = text[index]
        if char in "'\"`":
            index = _skip_string(text, index)
            continue
        if char == "/" and index + 1 < length and text[index + 1] == "/":
            newline = text.find("\n", index)
            index = length if newline == -1 else newline + 1
            continue
        if char == "{":
            return index
        index += 1
    return None


def _callback_end_line(lines: list[str], start: int) -> int | None:
    text = "\n".join(lines[start:])
    opened = _arrow_body_open(text)
    if opened is None:
        return None
    closed = _matching_brace(text, opened)
    if closed is None:
        return None
    return start + text.count("\n", 0, closed)


def _arrow_body_open(text: str) -> int | None:
    index = 0
    length = len(text)
    while index < length:
        char = text[index]
        if char in "'\"`":
            index = _skip_string(text, index)
            continue
        if char == "/" and index + 1 < length and text[index + 1] == "/":
            newline = text.find("\n", index)
            index = length if newline == -1 else newline + 1
            continue
        if text.startswith("=>", index):
            cursor = index + 2
            while cursor < length and text[cursor] in " \t\r\n":
                cursor += 1
            if cursor < length and text[cursor] == "{":
                return cursor
            return None
        index += 1
    return None


def _matching_brace(text: str, open_at: int) -> int | None:
    depth = 0
    index = open_at
    length = len(text)
    while index < length:
        char = text[index]
        if char in "'\"`":
            index = _skip_string(text, index)
            continue
        if char == "/" and index + 1 < length and text[index + 1] == "/":
            newline = text.find("\n", index)
            index = length if newline == -1 else newline + 1
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return index
        index += 1
    return None


def _skip_string(text: str, start: int) -> int:
    quote = text[start]
    index = start + 1
    length = len(text)
    while index < length:
        if text[index] == "\\":
            index += 2
            continue
        if text[index] == quote:
            return index + 1
        if quote == "`" and text.startswith("${", index):
            closed = _matching_brace(text, index + 1)
            index = length if closed is None else closed + 1
            continue
        index += 1
    return length


def write_stage_example_pages(out_root: Path, stages) -> dict[str, str]:
    """Copy each stage example into ``out_root/examples`` and write its catalog page."""
    hrefs: dict[str, str] = {}
    dest_dir = Path(out_root) / "examples"
    for stage in stages:
        href = stage_example_href(stage)
        if not href:
            continue
        source = _STORY_EXAMPLES / stage["example"].strip()
        dest_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest_dir / source.name)
        page = page_shell(
            title=f"{stage['label']} — ABD Context Driven Delivery",
            h1=html.escape(stage["label"]),
            tagline=html.escape(source.name),
            body_inner=_stage_example_body(stage, source),
            commons_prefix="../commons/",
            nav_prefix="../",
            nav_current="",
            body_wrap_class="approach-wrap",
        )
        (dest_dir / f"{stage['id']}.html").write_text(page, encoding="utf-8")
        hrefs[stage["id"]] = href
    return hrefs


def _stage_example_body(stage: dict, source: Path) -> str:
    back = (
        '<p class="approach-practice__back">'
        '<a href="../cdd-approach.html">← Back to the approach</a></p>'
    )
    suffix = source.suffix.lower()
    if suffix in _IMAGE_SUFFIXES:
        name = html.escape(source.name)
        return (
            f"{back}"
            '<figure class="catalog-example">'
            f'<img class="catalog-example__image" alt="{name}" src="{name}">'
            "</figure>"
        )
    text = source.read_text(encoding="utf-8")
    if suffix in (".md", ".markdown"):
        return f'{back}<div class="skill-md-preview">{_render_example_markdown(text)}</div>'
    language = _MONACO_LANG.get(suffix, "plaintext")
    return back + _monaco_example_html(
        text,
        language,
        script_src="../commons/catalog-monaco.js?v=cdd-108",
        folds=_acceptance_test_folds(text),
    )


def _monaco_start_line(source: str) -> int | None:
    for number, line in enumerate(source.splitlines(), start=1):
        if line.startswith("export class Customer"):
            return number
    return None


def _monaco_example_html(
    source: str,
    language: str,
    *,
    script_src: str,
    editor_id: str = "catalog-monaco",
    folds: list[tuple[int, int]] | None = None,
    include_script: bool = True,
    start_line: int | None = None,
) -> str:
    ranges = step_fold_ranges(source) if folds is None else folds
    payload = json.dumps(source).replace("<", "\\u003c")
    fold_attr = html.escape(
        json.dumps([{"start": start, "end": end} for start, end in ranges]),
        quote=True,
    )
    source_id = f"{editor_id}-source"
    start_attr = f' data-start-line="{start_line}"' if start_line else ""
    body = (
        f'<div id="{html.escape(editor_id)}" class="catalog-monaco" '
        f'data-language="{html.escape(language)}" data-folds="{fold_attr}" '
        f'data-source-id="{html.escape(source_id)}"{start_attr}></div>'
        f'<script type="application/json" id="{html.escape(source_id)}">{payload}</script>'
    )
    if not include_script:
        return body
    return (
        body
        + '<script src="https://cdn.jsdelivr.net/npm/monaco-editor@0.52.2/min/vs/loader.js"></script>'
        + f'<script src="{html.escape(script_src)}"></script>'
    )


def _refine_example_panel(stage_id: str, opening: str, inline: str) -> str:
    """One expandable stage example, matching the Iterate and Learn column body."""
    if not inline:
        return ""
    return (
        f'<div class="approach-stage-column approach-stage-example" '
        f'data-stage-id="{html.escape(stage_id)}">'
        '<div class="approach-stage-column__body">'
        f"{inline}"
        "</div></div>"
    )


def _refine_opening(stage_id: str, opening: str) -> str:
    body = (
        f'<div class="practice-fidelity__opening">{markdown_to_html(opening)}</div>'
        if opening
        else ""
    )
    return (
        f'<div class="approach-refine__opening" data-stage-id="{html.escape(stage_id)}">'
        f"{body}</div>"
    )


def _stage_example_panel_html(stage: dict) -> tuple[str, bool]:
    """Example body for one refine stage, or empty when no catalog example exists."""
    filename = (stage.get("example") or "").strip()
    if not filename:
        return "", False
    source = _STORY_EXAMPLES / filename
    if not source.is_file():
        return "", False
    inline = _stage_example_inline(source, include_monaco_script=False)
    return (
        _refine_example_panel(stage["id"], _stories_stage_overview(stage["id"]), inline),
        "catalog-monaco" in inline,
    )


_REFINE_STAGES = (
    ("discovery", "Discovery"),
    ("specification", "Specification"),
    ("implementation", "Implementation"),
)


def refine_stage_row(
    *,
    host_id: str,
    rail_label: str,
    panels: dict[str, str],
    extra_content: str = "",
    extra_classes: str = "",
    rail_family: str = "",
    openings: dict[str, str] | None = None,
    aria_label: str = "",
    role: str = "region",
) -> str:
    """Context rail + rewind/play + three stacked stage columns."""
    overviews = openings or {}
    transport = (
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
    heads: list[str] = []
    copies: list[str] = []
    examples: list[str] = []
    for stage_id, label in _REFINE_STAGES:
        heads.append(
            f'<button type="button" class="approach-window__stage" '
            f'data-stage-id="{html.escape(stage_id)}" aria-pressed="false" '
            f'aria-expanded="false">'
            f"{html.escape(label)}</button>"
        )
        copies.append(_refine_opening(stage_id, overviews.get(stage_id, "")))
        examples.append(
            panels.get(stage_id)
            or (
                f'<div class="approach-refine__placeholder" '
                f'data-stage-id="{html.escape(stage_id)}"></div>'
            )
        )
    classes = " ".join(
        part
        for part in ("approach-refine-row", "approach-stage-examples", extra_classes)
        if part
    )
    label_attr = html.escape(aria_label or f"{rail_label} refine stages")
    return (
        f'<div class="{classes}" id="{html.escape(host_id)}" role="{html.escape(role)}" '
        f'aria-label="{label_attr}">'
        '<div class="approach-refine__layout">'
        '<div class="approach-refine__context">'
        f'<button type="button" class="approach-window__stage approach-window__stage--context'
        f'{(" approach-grid__label--" + html.escape(rail_family)) if rail_family else ""}" '
        'data-stage-id="context" aria-pressed="false">'
        f'<span class="approach-window__context-label">{html.escape(rail_label)}</span>'
        "</button></div>"
        '<div class="approach-refine__content">'
        f"{extra_content}"
        '<div class="approach-refine__board">'
        f"{transport}"
        '<div class="approach-refine__stages">'
        f'<div class="approach-refine__heads">{"".join(heads)}</div>'
        f'<div class="approach-refine__openings">{"".join(copies)}</div>'
        f'<div class="approach-refine__examples">{"".join(examples)}</div>'
        "</div></div></div></div></div>"
    )


def _monaco_loader_scripts() -> str:
    return (
        '<script src="https://cdn.jsdelivr.net/npm/monaco-editor@0.52.2/min/vs/loader.js"></script>'
        '<script src="commons/catalog-monaco.js?v=cdd-109"></script>'
    )


def _approach_windows_html(stages: tuple[dict, ...] | list[dict] | None) -> str:
    """Narrowing-window diagram with context left and stacked stage columns."""
    stage_by_id = {stage["id"]: stage for stage in (stages or ())}
    panels: dict[str, str] = {}
    openings: dict[str, str] = {}
    needs_monaco = False
    for stage_id, _label in _REFINE_STAGES:
        stage = stage_by_id.get(stage_id, {})
        panel, panel_monaco = _stage_example_panel_html(stage) if stage else ("", False)
        needs_monaco = needs_monaco or panel_monaco
        if panel:
            panels[stage_id] = panel
            openings[stage_id] = _stories_stage_overview(stage_id)
    windows = (
        ("solution", "Whole Solution", "wide / shallow", "", "outcomes · scope · boundaries"),
        ("increment", "Increment", "medium", "days", "interactions · experience · structure"),
        ("sprint", "Session", "narrow / deeper", "hours", "behaviour · design · logic"),
        ("story", "Story", "narrowest / deep", "minutes", "tests · code · interface"),
    )
    parts: list[str] = []
    for index, (shape, name, width, when, detail) in enumerate(windows):
        if index:
            parts.append('<div class="approach-window__arrow" aria-hidden="true"></div>')
        bracket = f"{width} - {when}" if when else width
        parts.append(
            f'<div class="approach-window approach-window--{shape}">'
            '<div class="approach-window__shape"></div>'
            f'<div class="approach-window__name">{html.escape(name)}</div>'
            f'<div class="approach-window__width">({html.escape(bracket)})</div>'
            f'<div class="approach-window__detail">{html.escape(detail)}</div>'
            "</div>"
        )
    extra = '<div class="approach-windows__row">' + "".join(parts) + "</div>"
    return refine_stage_row(
        host_id="approach-stage-examples",
        rail_label="Context",
        panels=panels,
        openings=openings,
        extra_content=extra,
        extra_classes="approach-windows",
        aria_label="Context feeds a narrowing window from Whole Solution to Story",
        role="img",
    ) + (_monaco_loader_scripts() if needs_monaco else "")


def approach_stage_examples_html(stages) -> str:
    """Deprecated: examples are embedded in ``_approach_windows_html``."""
    return ""


def _stage_example_inline(
    source: Path,
    *,
    include_monaco_script: bool = True,
    editor_id: str | None = None,
) -> str:
    suffix = source.suffix.lower()
    name = html.escape(source.name)
    if suffix in (".drawio", ".dio"):
        return _drawio_iframe(source, zoom_left=source.stem == "story_map")
    if suffix in (".html", ".htm"):
        srcdoc = html.escape(source.read_text(encoding="utf-8"), quote=True)
        return (
            '<figure class="catalog-example catalog-example--scroll">'
            f'<iframe class="catalog-example__frame" title="{name}" sandbox="" '
            f'style="width:2700px;height:920px;max-width:none" srcdoc="{srcdoc}"></iframe>'
            "</figure>"
        )
    if suffix in _IMAGE_SUFFIXES:
        if source.parent.name == "catalog-examples":
            href = f"examples/{html.escape(source.parent.parent.name)}/{name}"
        else:
            href = f"examples/{name}"
        classes = ["catalog-example", "catalog-example--scroll"]
        if source.stem == "bounded-context":
            classes.append("catalog-example--fit")
        if source.stem in {"building-blocks", "front-end-code"}:
            classes.append("catalog-example--zoom-2")
        if source.stem == "story_map":
            classes.append("catalog-example--story-map")
        return (
            f'<figure class="{" ".join(classes)}">'
            f'<img class="catalog-example__image" alt="{name}" src="{href}">'
            "</figure>"
        )
    text = source.read_text(encoding="utf-8")
    if suffix in (".md", ".markdown"):
        return f'<div class="skill-md-preview">{_render_example_markdown(text)}</div>'
    language = _MONACO_LANG.get(suffix, "plaintext")
    folds = (
        ddd_class_fold_ranges(text)
        if "Root" in text and "export class " in text
        else _acceptance_test_folds(text)
    )
    return _monaco_example_html(
        text,
        language,
        script_src="commons/catalog-monaco.js?v=cdd-109",
        editor_id=editor_id or "catalog-monaco",
        folds=folds,
        include_script=include_monaco_script,
        start_line=_monaco_start_line(text),
    )


_PRACTICE_GUIDES = {
    "stories": "stories",
    "ddd": "ddd",
    "ux": "ux",
    "clean_engineering": "clean_engineering",
    "bdd": "bdd",
}
_STAGE_FROM_META = {
    "discovery": "discovery",
    "specification": "spec",
    "spec": "spec",
    "implementation": "engineer",
    "engineer": "engineer",
}
_BOOKEND_TABS = (
    (
        "customer-discovery",
        "customer-discovery",
        "Validate customer impact by delivering the smallest increment that enables them, and pivot to measure and learn.",
    ),
    (
        "devops",
        "devops",
        "Merge development and operations by treating infrastructure as code and testing and deploying continuously.",
    ),
)


def copy_practice_examples(out_root: Path) -> None:
    """Copy ``{practice}/catalog-examples`` files into the catalog."""
    practices = Path(__file__).resolve().parents[2] / "practices"
    if not practices.is_dir():
        return
    for practice in practices.iterdir():
        folder = practice / "catalog-examples"
        if not folder.is_dir():
            continue
        dest = Path(out_root) / "examples" / practice.name
        for path in folder.iterdir():
            if path.is_file() and not path.name.startswith("."):
                dest.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, dest / path.name)


_STAGE_ID_FROM_KEY = {
    "discovery": "discovery",
    "spec": "specification",
    "engineer": "implementation",
}

_FIDELITY_STEM_ALIASES = {
    ("ux", "ia"): ("information-architecture",),
}


def _product_engineering_grid(practices: list[dict]) -> str:
    """One refine row per practice, reusing the Iterate and Learn stage architecture."""
    rows: list[str] = []
    needs_monaco = False
    for tool in practices:
        name = tool["toolset_name"]
        label = _PE_TAB_LABELS.get(name, name.replace("_", "-"))
        panels, openings, panel_monaco = _practice_refine_panels(name)
        needs_monaco = needs_monaco or panel_monaco
        rows.append(
            refine_stage_row(
                host_id=f"refine-row-{name}",
                rail_label=label,
                rail_family=family_perspective(name),
                panels=panels,
                openings=openings,
                aria_label=f"{label} discovery, specification, and implementation",
            )
        )
    return (
        '<div class="approach-pe-rows" id="pe-engineering">'
        + "".join(rows)
        + (_monaco_loader_scripts() if needs_monaco else "")
        + "</div>"
    )


def _practice_refine_panels(practice: str) -> tuple[dict[str, str], dict[str, str], bool]:
    panels: dict[str, str] = {}
    openings: dict[str, str] = {}
    needs_monaco = False
    guide_name = _PRACTICE_GUIDES.get(practice)
    if not guide_name:
        return panels, openings, False
    guide = Path(__file__).resolve().parents[2] / "practices" / guide_name / f"{guide_name}.md"
    if not guide.is_file():
        return panels, openings, False
    for item in _practice_fidelities(guide.read_text(encoding="utf-8")):
        stage_id = _STAGE_ID_FROM_KEY.get(item["stage"])
        if not stage_id:
            continue
        files = _fidelity_example_files(practice, item["key"])
        if not files:
            continue
        parts: list[str] = []
        for path in files:
            slug = re.sub(
                r"[^a-z0-9]+",
                "-",
                f"{practice}-{path.stem}-{path.suffix.lstrip('.')}".lower(),
            ).strip("-")
            inline = _stage_example_inline(
                path,
                include_monaco_script=False,
                editor_id=f"monaco-{slug}",
            )
            needs_monaco = needs_monaco or "catalog-monaco" in inline
            parts.append(inline)
        panel = _refine_example_panel(stage_id, item["opening"], "".join(parts))
        if panel:
            panels[stage_id] = panel
            openings[stage_id] = item["opening"]
    return panels, openings, needs_monaco


_PE_TAB_LABELS = {
    "customer-discovery": "customer-discovery",
    "stories": "stories",
    "ddd": "Domain-driven design",
    "ux": "ux",
    "clean_engineering": "clean-engineering",
    "bdd": "bdd",
    "devops": "devops",
}


def _practice_fidelities(text: str) -> list[dict]:
    match = re.search(r"(?m)^## Fidelities\s*$", text)
    if not match:
        return []
    body = text[match.end() :]
    nxt = re.search(r"(?m)^## ", body)
    if nxt:
        body = body[: nxt.start()]
    found = []
    for chunk in re.split(r"(?m)^### ", body)[1:]:
        title, _, rest = chunk.partition("\n")
        stage_match = re.search(r"(?m)^stage:\s*(\S+)", rest)
        if not stage_match:
            continue
        stage = _STAGE_FROM_META.get(stage_match.group(1).strip().lower())
        if not stage:
            continue
        found.append(
            {
                "key": title.strip(),
                "stage": stage,
                "opening": _overview_paragraph(rest),
            }
        )
    return found


def _overview_paragraph(section: str) -> str:
    marker = "#### Overview"
    index = section.find(marker)
    body = section[index + len(marker) :] if index >= 0 else section
    lines: list[str] = []
    started = False
    fence = False
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            if started:
                break
            fence = not fence
            continue
        if fence or stripped.startswith("#"):
            if started:
                break
            continue
        if not stripped:
            if started:
                break
            continue
        started = True
        lines.append(line.rstrip("\r"))
    return "\n".join(lines).strip()


def _fidelity_example_files(practice: str, fidelity: str) -> list[Path]:
    folder = Path(__file__).resolve().parents[2] / "practices" / practice / "catalog-examples"
    if not folder.is_dir():
        return []
    names = {fidelity, fidelity.replace("_", "-"), fidelity.replace("-", "_")}
    names.update(_FIDELITY_STEM_ALIASES.get((practice, fidelity), ()))
    files = sorted(
        (
            path
            for path in folder.iterdir()
            if path.is_file() and not path.name.startswith(".") and path.stem in names
        ),
        key=lambda path: (_EXAMPLE_SUFFIX_ORDER.get(path.suffix.lower(), 50), path.name),
    )
    chosen: list[Path] = []
    stems: dict[str, list[Path]] = {}
    for path in files:
        stems.setdefault(path.stem, []).append(path)
    for group in stems.values():
        images = [path for path in group if path.suffix.lower() in _IMAGE_SUFFIXES]
        if images:
            chosen.extend(images)
            continue
        drawios = [path for path in group if path.suffix.lower() in (".drawio", ".dio")]
        if drawios:
            chosen.extend(drawios)
            continue
        others = [
            path
            for path in group
            if path.suffix.lower() not in {".md", ".markdown"}
        ]
        if others:
            chosen.extend(others)
            continue
        chosen.extend(group)
    return sorted(chosen, key=lambda path: (_EXAMPLE_SUFFIX_ORDER.get(path.suffix.lower(), 50), path.name))


def fence(lang: str, text: str) -> str:
    return f'<pre class="code-fence"><code class="language-{html.escape(lang)}">{html.escape(text)}</code></pre>'


def markdown_to_html(text: str, *, include_tables: bool = False) -> str:
    """Minimal markdown → HTML for fidelity/overview panels (stdlib only).

    Set ``include_tables=True`` to render pipe tables (workflow page); default
    skips them so fidelity overview index tables stay out of page bodies.
    """
    if not text or text == "Guidance missing":
        return f"<p>{html.escape(text or '')}</p>"

    lines = text.replace("\r\n", "\n").split("\n")
    out: list[str] = []
    i = 0
    in_list: str | None = None  # "ul" | "ol"
    in_code = False
    code_lang = ""
    code_buf: list[str] = []
    _ul_re = re.compile(r"^\s*[-*]\s+")
    _ol_re = re.compile(r"^\s*\d+\.\s+")
    # Guides often use ❌/✅ as the bullet itself (no leading "- ").
    _emoji_ul_re = re.compile(r"^\s*([❌✅])\s+")
    _block_start_re = re.compile(
        r"^(#{1,4}\s+|```|\s*[-*]\s+|\s*\d+\.\s+|\s*[❌✅]\s+|\s*\|)"
    )
    _link_re = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
    _table_sep_re = re.compile(r"^\s*\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)+\|?\s*$")

    def close_list() -> None:
        nonlocal in_list
        if in_list:
            out.append(f"</{in_list}>")
            in_list = None

    def open_list(kind: str) -> None:
        nonlocal in_list
        if in_list != kind:
            close_list()
            out.append(f"<{kind}>")
            in_list = kind

    def _hard_break_after(raw: str) -> bool:
        return bool(re.search(r"  +$", raw.rstrip("\r")))

    def _join_paragraph_lines(para: list[str], format_inline) -> str:
        parts: list[str] = []
        for index, raw in enumerate(para):
            if index:
                parts.append("<br>" if _hard_break_after(para[index - 1]) else " ")
            parts.append(format_inline(raw.strip()))
        return "".join(parts)

    def inline(s: str) -> str:
        links: list[tuple[str, str]] = []

        def _save_link(m: re.Match) -> str:
            links.append((m.group(1), m.group(2)))
            return f"\x00L{len(links) - 1}\x00"

        s = _link_re.sub(_save_link, s)
        s = html.escape(s)
        s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
        s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
        s = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", s)

        def _restore_link(m: re.Match) -> str:
            text, href = links[int(m.group(1))]
            # Link text may itself contain code/bold — run the same inline pass
            # without re-entering link extraction (text has no markdown links left).
            label = html.escape(text)
            label = re.sub(r"`([^`]+)`", r"<code>\1</code>", label)
            label = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", label)
            label = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", label)
            return f'<a href="{html.escape(href, quote=True)}">{label}</a>'

        return re.sub(r"\x00L(\d+)\x00", _restore_link, s)
    def _split_row(row: str) -> list[str]:
        body = row.strip().strip("|")
        return [c.strip() for c in body.split("|")]

    while i < len(lines):
        line = lines[i]
        if in_code:
            if line.strip().startswith("```"):
                # Fidelity and rule files keep format, stage, and glob metadata in
                # yaml fences. That metadata stays in the markdown; the catalog HTML shows the prose.
                if code_lang.lower() not in ("yaml", "yml"):
                    body = html.escape("\n".join(code_buf))
                    lang_attr = f' class="language-{html.escape(code_lang)}"' if code_lang else ""
                    out.append(f"<pre><code{lang_attr}>{body}</code></pre>")
                in_code = False
                code_buf = []
                code_lang = ""
            else:
                code_buf.append(line)
            i += 1
            continue

        if line.strip().startswith("```"):
            close_list()
            in_code = True
            code_lang = line.strip()[3:].strip()
            i += 1
            continue

        if re.match(r"^\s*\|", line):
            close_list()
            if not include_tables:
                while i < len(lines) and (re.match(r"^\s*\|", lines[i]) or not lines[i].strip()):
                    i += 1
                continue
            rows: list[list[str]] = []
            while i < len(lines) and re.match(r"^\s*\|", lines[i]):
                rows.append(_split_row(lines[i]))
                i += 1
            data_rows = [r for r in rows if not _table_sep_re.match("|" + "|".join(r) + "|")]
            if not data_rows:
                continue
            out.append('<table class="catalog-md-table">')
            header, *body_rows = data_rows
            out.append("<thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in header) + "</tr></thead>")
            if body_rows:
                out.append("<tbody>")
                for row in body_rows:
                    # Pad/truncate to header width
                    cells = (row + [""] * len(header))[: len(header)]
                    out.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in cells) + "</tr>")
                out.append("</tbody>")
            out.append("</table>")
            continue

        m = re.match(r"^(#{1,4})\s+(.*)$", line)
        if m:
            close_list()
            level = len(m.group(1))
            out.append(f"<h{level}>{inline(m.group(2).strip())}</h{level}>")
            i += 1
            continue

        if _ul_re.match(line):
            open_list("ul")
            item = _ul_re.sub("", line, count=1)
            i += 1
            cont: list[str] = []
            while (
                i < len(lines)
                and lines[i].startswith(("  ", "\t"))
                and lines[i].strip()
                and not _ul_re.match(lines[i])
                and not _ol_re.match(lines[i])
            ):
                cont.append(lines[i].strip())
                i += 1
            if cont:
                body = "<br>".join(inline(chunk) for chunk in [item, *cont])
                out.append(f"<li>{body}</li>")
            else:
                out.append(f"<li>{inline(item)}</li>")
            continue

        if _emoji_ul_re.match(line):
            open_list("ul")
            # Keep the emoji marker in the item text.
            out.append(f"<li>{inline(line.strip())}</li>")
            i += 1
            continue

        if _ol_re.match(line):
            open_list("ol")
            item = _ol_re.sub("", line, count=1)
            i += 1
            cont = []
            while (
                i < len(lines)
                and lines[i].startswith(("  ", "\t"))
                and lines[i].strip()
                and not _ul_re.match(lines[i])
                and not _ol_re.match(lines[i])
            ):
                cont.append(lines[i].strip())
                i += 1
            if cont:
                body = "<br>".join(inline(chunk) for chunk in [item, *cont])
                out.append(f"<li>{body}</li>")
            else:
                out.append(f"<li>{inline(item)}</li>")
            continue
        if not line.strip():
            close_list()
            i += 1
            continue

        if re.match(r"^\s*-{3,}\s*$", line):
            close_list()
            out.append("<hr>")
            i += 1
            continue

        close_list()
        para = [line]
        i += 1
        while (
            i < len(lines)
            and lines[i].strip()
            and not _block_start_re.match(lines[i])
            and not re.match(r"^\s*-{3,}\s*$", lines[i])
        ):
            para.append(lines[i])
            i += 1
        out.append(f"<p>{_join_paragraph_lines(para, inline)}</p>")

    close_list()
    if in_code and code_lang.lower() not in ("yaml", "yml"):
        out.append(f"<pre><code>{html.escape(chr(10).join(code_buf))}</code></pre>")
    return "\n".join(out)


def cap_card(title: str, href: str, summary: str, label: str = "Catalog") -> str:
    return (
        f'<a class="cap-card" href="{html.escape(href)}">'
        f'<p class="cap-card__title">{html.escape(title)}</p>'
        f'<p class="cap-card__label">{html.escape(label)}</p>'
        f'<p class="cap-card__summary">{html.escape(summary)}</p>'
        f'<p class="cap-card__more">Open →</p></a>'
    )
