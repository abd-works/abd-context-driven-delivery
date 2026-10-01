"""Foundry chrome for the CDD catalog - page shells, commons copy, hub board.

Mirrors the abd-skills Foundry hub: hero, CDD tour panel, scope-shape column
heads, orange policy boxes, kebab-case tickets, Actions/Utilities strips.
Stage column heads navigate to CDD fidelities (no stage filter).
"""
from __future__ import annotations

import base64
import html
import re
import shutil
import urllib.parse
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

# Stage column bullets — approach-page scope chips (Outcome / Increment / Tests).
_STAGE_POLICIES: dict[str, tuple[str, ...]] = {
    "discovery": (
        "Outcome",
        "Experience",
        "Architecture",
    ),
    "spec": (
        "Increment",
        "Prototype",
        "Reference",
    ),
    "engineer": (
        "Tests",
        "Interface",
        "Solution",
    ),
}

# Approach write-ups shown under each stage column during the tour.
_STAGE_DESCRIPTIONS: dict[str, tuple[str, ...]] = {
    "discovery": (
        "Refine context into lower-fidelity artifacts that make it easier to align on the overarching solution, catch systemic errors, and avoid failure cascading downstream.",
        "Focus on how outcomes translate to user journeys, and map those journeys to system behavior.",
        "Define enough structure to establish how domain boundaries and technology modules connect.",
    ),
    "spec": (
        "Create machine-executable specifications — one small slice of the journey at a time.",
        "Refine the business understanding needed to modularize domain validity, access, persistence, consistency, and integration.",
        "Write example-driven scenarios backed by domain-driven operations, and generate working UI prototypes that pass their tests.",
    ),
    "engineer": (
        "Build each slice onto the target stack. AI oversees deterministic tools so the same input produces results guarded by safety and quality standards.",
        "Automate scenario specifications to cover user, system, and module-connecting interfaces.",
        "Evaluate every error — technical and functional — and feed results back into the growing knowledge repository.",
    ),
}

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

# Discovery-fidelity overviews, tightened to one or two sentences for Context Storming.
_STORM_BLURBS: dict[str, str] = {
    "stories": (
        "Define the story map as Epic, Sub-Epic, and Story. "
        "Change it while the nodes are still titles, because the same move costs much more after scenarios, screens, and tests exist."
    ),
    "ddd": (
        "Draw where the language changes: context boundaries, the aggregates that protect invariants, and the dependency arcs between contexts. "
        "Names and boundaries are cheap to change here, and expensive once building blocks, stories, and code depend on them."
    ),
    "ux": (
        "Decide which screens exist and how users move between them. "
        "Name screens, regions, and transitions in the user's language before controls or brand."
    ),
    "clean_engineering": (
        "Partition the problem into modules a reader can understand on their own. "
        "Name each module, its public seam, and its one-way dependencies."
    ),
    "bdd": (
        "Name every observation as a nested describe/it signature. "
        "Leave the test bodies empty until the behavior is agreed."
    ),
}


def approach_principle_grid(practices: list[dict], kind: str) -> str:
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
        # Customer discovery and DevOps sit on this grid only. They are not catalog practices.
        bookends = (
            (
                "customer-discovery",
                "customer-discovery",
                "Validate customer impact by delivering the smallest increment that enables them, and pivot to measure and learn.",
                "customer-discovery.html",
            ),
            (
                "devops",
                "devops",
                "Merge development and operations by treating infrastructure as code and testing and deploying continuously.",
                "devops.html",
            ),
        )

        def plain_row(name: str, fam: str, blurb: str, href: str) -> list[str]:
            return [
                f'<a class="approach-grid__label approach-grid__label--{html.escape(fam)}" '
                f'href="{html.escape(href)}">{html.escape(name)}</a>',
                f'<div class="approach-grid__cell">{html.escape(blurb)}</div>',
            ]

        body = plain_row(*bookends[0])
        for tool in rows:
            body.append(label(tool))
            body.append(
                f'<div class="approach-grid__cell">{html.escape(_PRACTICE_BLURBS.get(tool["toolset_name"], ""))}</div>'
            )
        body.extend(plain_row(*bookends[1]))
        return f'<div class="approach-grid approach-grid--span">{"".join(body)}</div>'

    if kind == "spec":
        body = []
        for tool in rows:
            body.append(label(tool))
            body.append(
                f'<div class="approach-grid__cell">{html.escape(_SPEC_BLURBS.get(tool["toolset_name"], ""))}</div>'
            )
        return f'<div class="approach-grid approach-grid--span">{"".join(body)}</div>'

    if kind == "storm":
        body = []
        for tool in rows:
            body.append(label(tool))
            body.append(
                f'<div class="approach-grid__cell">{html.escape(_STORM_BLURBS.get(tool["toolset_name"], ""))}</div>'
            )
        return f'<div class="approach-grid approach-grid--span">{"".join(body)}</div>'

    if kind == "windows":
        stages = ("Context", "Discovery", "Specification", "Implementation")
        stage_bar = '<div class="approach-window__stages">' + "".join(
            f'<div class="approach-window__stage">{html.escape(label)}</div>' for label in stages
        ) + "</div>"
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
        return (
            '<div class="approach-windows" role="img" '
            'aria-label="Context window narrows from Whole Solution to Story">'
            + stage_bar
            + '<div class="approach-windows__row">'
            + "".join(parts)
            + "</div></div>"
        )

    if kind == "stages":
        heads = [cdd_head]
        details = []
        for stage_key, stage_label in STAGES:
            fams = ("sdd", "uxd", "arc")
            chips = "".join(
                f'<li class="approach-grid__chip approach-grid__chip--{fams[i % 3]}">{html.escape(item)}</li>'
                for i, item in enumerate(_STAGE_POLICIES.get(stage_key, ()))
            )
            paras = "".join(
                f'<p>{html.escape(para)}</p>' for para in _STAGE_DESCRIPTIONS.get(stage_key, ())
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
<link rel="stylesheet" href="{commons_prefix}foundry-catalog.css?v=cdd-76">
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


def _stage_col_detail_html(stage_key: str) -> str:
    """Approach chips + write-ups shown inside each column during tour stage 1."""
    fams = ("sdd", "uxd", "arc")
    chips = "".join(
        f'<li class="tour-stage-detail__chip tour-stage-detail__chip--{fams[i % 3]}">'
        f"{html.escape(item)}</li>"
        for i, item in enumerate(_STAGE_POLICIES.get(stage_key, ()))
    )
    paras = "".join(
        f'<p class="tour-stage-detail__desc">{html.escape(para)}</p>'
        for para in _STAGE_DESCRIPTIONS.get(stage_key, ())
    )
    return (
        f'<div class="tour-stage-detail" data-stage-detail="{html.escape(stage_key)}">'
        f'<ul class="tour-stage-detail__chips">{chips}</ul>'
        f'{paras}'
        f"</div>"
    )


def _stage_questions_html(
    practices: list[dict],
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
        items = "".join(
            f'<li class="kanban-stage-questions__item">{html.escape(item)}</li>'
            for item in _STAGE_POLICIES[stage_key]
        )
        paras = "".join(
            f'<p class="kanban-stage-questions__desc">{html.escape(para)}</p>'
            for para in _STAGE_DESCRIPTIONS.get(stage_key, ())
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
) -> str:
    """Build the Foundry-style stage×tool kanban + policies + Actions/Utilities."""
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
        cols.append(
            f'<div class="kb-col{active}" data-id="col-{stage_key}" data-stage="{stage_key}">'
            f'<div class="kb-col-head{stage_current}">'
            f'<div class="kb-col-head-row">'
            f"{_scope_shape_html(stage_key)}"
            f'<span class="kb-col-head-title"><span>{html.escape(stage_label)}</span></span>'
            f"</div></div>"
            f"{_stage_col_detail_html(stage_key)}"
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

    stage_questions = _stage_questions_html(practices, path_prefix=path_prefix)

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


def _drawio_viewer_url(xml: str) -> str:
    compressor = zlib.compressobj(9, zlib.DEFLATED, -15)
    raw = compressor.compress(xml.encode("utf-8")) + compressor.flush()
    token = urllib.parse.quote(base64.b64encode(raw).decode("ascii"), safe="")
    return (
        "https://viewer.diagrams.net/?lightbox=1&nav=1&layers=1&toolbar=zoom"
        f"&edit=_blank#R{token}"
    )


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
        out.append(f"<p>{inline(' '.join(p.strip() for p in para))}</p>")

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
