"""Foundry chrome for the CDD catalog - page shells, commons copy, hub board.

Mirrors the abd-skills Foundry hub: hero, CDD tour panel, scope-shape column
heads, orange policy boxes, kebab-case tickets, Actions/Utilities strips.
Stage column heads navigate to CDD fidelities (no stage filter).
"""
from __future__ import annotations

import html
import re
import shutil
from pathlib import Path

_TEMPLATES = Path(__file__).resolve().parent / "templates"
_COMMONS_SRC = _TEMPLATES / "commons"
_FOUNDRY_CSS_SRC = _TEMPLATES / "foundry-catalog.css"

# Stage columns — keys stay discovery/spec/engineer (code); labels are lowercase.
STAGES: tuple[tuple[str, str], ...] = (
    ("discovery", "discovery"),
    ("spec", "specification"),
    ("engineer", "engineering"),
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

# Orange policy boxes — Foundry discovery/specification/engineering with CDD edits.
_STAGE_POLICIES: dict[str, tuple[str, ...]] = {
    "discovery": (
        "system interactions",
        "modules",
        "user navigation",
        "Boundaries",
    ),
    "spec": (
        "behavior",
        "model",
        "mockups",
        "building blocks",
    ),
    "engineer": (
        "tests",
        "code",
        "Interface",
        "architecture code",
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
    "engineer": "engineering",
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


def copy_commons(out_root: Path) -> Path:
    """Copy Foundry commons + catalog CSS into ``{out_root}/commons/``."""
    dest = out_root / "commons"
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copytree(_COMMONS_SRC, dest, dirs_exist_ok=True)
    shutil.copy2(_FOUNDRY_CSS_SRC, dest / "foundry-catalog.css")
    shutil.copy2(_TEMPLATES / "cdd-board.css", dest / "cdd-board.css")
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
) -> str:
    """Wrap content in the Foundry catalog page chrome (nav + hero + scripts).

    Fidelity pages set ``show_hero=False`` so the board leads and the title /
    invoke / guidance sit in ``body_inner`` under the kanban (Foundry skill
    detail pattern).
    """
    hero = ""
    if show_hero:
        hero = f"""
<div class="page-hero page-hero--foundry">
  <div class="wrap">
    <table class="page-hero__table" role="presentation">
      <tr>
        <td class="page-hero__cell page-hero__cell--title">
          <h1 class="page-headline">{h1}</h1>
          <p class="body-lead">{tagline}</p>
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
<html lang="en">
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
<link rel="stylesheet" href="{commons_prefix}foundry-catalog.css?v=cdd-13">
<link rel="stylesheet" href="{commons_prefix}cdd-board.css?v=cdd-13">
{extra_head}
<script src="{commons_prefix}catalog-nav.js?v=foundry-11"></script>
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
<script src="{commons_prefix}catalog-foundry-tour.js?v=cdd-13"></script>
<script src="{commons_prefix}catalog-foundry-skill-nav.js?v=cdd-13"></script>
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


def _family_toggle(display_name: str, toolset_name: str, *, header: bool = False) -> str:
    """Practice-rail chip — button that filters the board (row header only)."""
    fam = family_class(toolset_name)
    persp = family_perspective(toolset_name)
    extra = " foundry-practice-col__card--header" if header else ""
    return (
        f'<button type="button" class="kb-ticket aad-skill {fam} foundry-practice-col__card '
        f'foundry-perspective-label foundry-family-toggle foundry-perspective-label--{persp}{extra}" '
        f'data-family="{html.escape(toolset_name)}" data-perspective="{persp}" '
        f'aria-pressed="false">{html.escape(display_name)}</button>'
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


def _stage_questions_html(
    context_tools: list[dict],
    *,
    path_prefix: str = "",
) -> str:
    by_name = {t["toolset_name"]: t for t in context_tools}
    cdd = by_name.get("cdd") or {}
    cells = ['<div class="kanban-stage-questions__spacer" aria-hidden="true"></div>']
    for stage_key, _ in STAGES:
        items = "".join(
            f'<li class="kanban-stage-questions__item">{html.escape(item)}</li>'
            for item in _STAGE_POLICIES[stage_key]
        )
        fid = (cdd.get("fidelities") or {}).get(stage_key)
        href = path_prefix + (fid["href"] if fid else f"fidelities/cdd-{stage_key}.html")
        cells.append(
            f'<a class="kanban-stage-questions__cell" data-stage="{html.escape(stage_key)}" '
            f'href="{html.escape(href)}">'
            f'<ul class="kanban-stage-questions__list">{items}</ul></a>'
        )
    return (
        '<div class="kanban-stage-questions kanban-stage-questions--foundry '
        'kanban-stage-questions--cdd" data-id="stage-questions">'
        + "".join(cells)
        + "</div>"
    )


def _cdd_tour_panel_html() -> str:
    return """
  <div class="foundry-travel-ring" id="travel-ring" aria-hidden="true"></div>
  <div class="foundry-cdd-panel" id="foundry-guide">
    <div class="foundry-cdd-panel__head">
      <button type="button" class="foundry-cdd-btn" id="cdd-toggle" aria-label="Start Context-Driven Delivery overview">Context-driven delivery</button>
      <span class="foundry-cdd-panel__tag" id="guide-tag">Click for overview</span>
    </div>
    <div class="foundry-cdd-intro" id="cdd-intro">
      <p class="foundry-cdd-intro__line1">Speed is not governed by coding speed. It is governed by <strong>coordination cost</strong> and <strong>cognitive load</strong>.</p>
      <p class="foundry-cdd-intro__line2"><strong>Context-Driven Delivery</strong> is the practice that turns organizational knowledge into executable, machine-readable context AI can generate from accurately.</p>
    </div>
    <div class="foundry-guide__body" id="guide-text" aria-live="polite"></div>
  </div>
"""


def render_hub_board(
    context_tools: list[dict],
    actions: list[dict],
    utilities: list[dict],
    *,
    highlight_tool: str | None = None,
    highlight_fidelity: str | None = None,
    path_prefix: str = "",
    initial_family: str | None = None,
) -> str:
    """Build the Foundry-style stage×tool kanban + policies + Actions/Utilities."""
    by_name = {t["toolset_name"]: t for t in context_tools}
    ordered = [by_name[n] for n in FAMILY_ROW_ORDER if n in by_name]
    for t in context_tools:
        if t["toolset_name"] == "cdd":
            continue
        if t["toolset_name"] not in {x["toolset_name"] for x in ordered}:
            ordered.append(t)

    cdd_tool = by_name.get("cdd")
    cdd_tool_href = path_prefix + (cdd_tool["href"] if cdd_tool else "context-tools/cdd.html")

    practice_bits = [
        _family_toggle(display_label(tool["toolset_name"]), tool["toolset_name"], header=False)
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

        if cdd_fid:
            stage_href = path_prefix + cdd_fid["href"]
        else:
            stage_href = path_prefix + f"fidelities/cdd-{stage_key}.html"
        stage_current = " kb-col-head--current" if active else ""
        cols.append(
            f'<div class="kb-col{active}" data-id="col-{stage_key}" data-stage="{stage_key}">'
            f'<a class="kb-col-head{stage_current}" href="{html.escape(stage_href)}">'
            f'<div class="kb-col-head-row">'
            f"{_scope_shape_html(stage_key)}"
            f'<span class="kb-col-head-title"><span>{html.escape(stage_label)}</span></span>'
            f"</div></a>"
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

    stage_questions = _stage_questions_html(context_tools, path_prefix=path_prefix)

    return f"""
<div class="wrap">
<div class="foundry-kanban-shell" id="kanban-shell">
<section class="foundry-kanban-surface foundry-skills-expanded catalog-kanban-embed foundry-kanban-surface--cdd-always-expanded" id="catalog-kanban" aria-label="CDD catalog board"{attrs}>
{_cdd_tour_panel_html()}
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
            <div class="aad-delivery-crosscut-row aad-crosscut-tier--foundational is-filter-visible" data-crosscut-group="utilities">
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
    if in_code:
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
