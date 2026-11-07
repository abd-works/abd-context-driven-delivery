"""The Foundry chrome every catalog page is wrapped in: navigation, hero, board, and the scripts its body needs."""
from __future__ import annotations

import html
from dataclasses import dataclass

_SITE = "https://abd.works/"
_DRAWIO_VIEWER_SCRIPT = '<script src="https://viewer.diagrams.net/js/viewer-static.min.js"></script>'
# A body that embeds a live draw.io diagram (data-mxgraph) needs the viewer; a body with approach example columns needs
# the scripts that size them and open them one stage at a time.
_DIAGRAM_MARK = "data-mxgraph"
_EXAMPLE_COLUMN_MARKS = ("approach-stage-examples", "approach-refine-row")


@dataclass(frozen=True)
class PageShell:
    """One catalog page's chrome around its body. ``commons_prefix`` and ``nav_prefix`` lead from the page's folder to
    the catalog's shared files and pages (``../`` for a page one folder down). A page without ``show_hero`` leads with
    its board, and its title sits in the body under it."""

    title: str
    h1: str
    tagline: str
    body_inner: str
    commons_prefix: str = "commons/"
    nav_prefix: str = ""
    nav_current: str = ""
    kanban_embed: str = ""
    show_hero: bool = True
    body_wrap_class: str = ""
    after_tagline: str = ""
    subhead: str = ""
    after_subhead: str = ""

    @property
    def html(self) -> str:
        return f"""<!DOCTYPE html>
<html lang="en" data-theme="engineering" data-abd-theme="engineering">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<script>
(function(){{try{{if('scrollRestoration' in history)history.scrollRestoration='manual';var r=new URLSearchParams(location.search).get('kanbanScroll');if(!r)return;var y=parseFloat(r);if(isNaN(y))return;window.__foundryPendingScrollY=y;document.documentElement.classList.add('foundry-scroll-pending');}}catch(e){{}}}})();
</script>
<title>{html.escape(self.title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{self.commons_prefix}site.css?v=foundry-33">
<link rel="stylesheet" href="{self.commons_prefix}foundry-catalog.css?v=cdd-133">
<link rel="stylesheet" href="{self.commons_prefix}cdd-board.css?v=cdd-31">

<script src="{self.commons_prefix}catalog-nav.js?v=foundry-13"></script>
</head>
<body data-nav-prefix="{html.escape(self.nav_prefix)}" data-nav-current="{html.escape(self.nav_current)}" data-nav-site-base="{html.escape(_SITE)}">
<main id="main-content">

{self._hero}
{self.kanban_embed}
<div class="catalog-body">
<div class="{html.escape(self._body_wrap)}">
{self.body_inner}
</div>
</div>
</main>
<script src="{self.commons_prefix}catalog-foundry-skill-nav.js?v=cdd-16"></script>
{self._body_scripts}
</body>
</html>
"""

    @property
    def _hero(self) -> str:
        if not self.show_hero:
            return ""
        return f"""
<div class="page-hero page-hero--foundry">
  <div class="wrap">
    <table class="page-hero__table" role="presentation">
      <tr>
        <td class="page-hero__cell page-hero__cell--title">{self._title_bar}{self._lead}
        </td>
      </tr>
    </table>
  </div>
</div>
"""

    @property
    def _title_bar(self) -> str:
        after = self.after_tagline.strip()
        if not after:
            return f'\n          <h1 class="page-headline">{self.h1}</h1>'
        return (
            f'\n          <div class="page-hero__title-bar">'
            f'\n            <h1 class="page-headline">{self.h1}</h1>'
            f'\n            {after}'
            f"\n          </div>"
        )

    @property
    def _lead(self) -> str:
        lead = f'\n          <p class="body-lead">{self.tagline}</p>' if self.tagline.strip() else ""
        if self.subhead.strip():
            lead += f'\n          <p class="page-hero__subhead">{html.escape(self.subhead)}</p>'
        if self.after_subhead.strip():
            lead += f'\n          <p class="body-lead page-hero__repo">{self.after_subhead}</p>'
        return lead

    @property
    def _body_wrap(self) -> str:
        return f"wrap {self.body_wrap_class.strip()}" if self.body_wrap_class else "wrap"

    @property
    def _body_scripts(self) -> str:
        has_diagram = _DIAGRAM_MARK in self.body_inner
        has_columns = any(mark in self.body_inner for mark in _EXAMPLE_COLUMN_MARKS)
        if not (has_diagram or has_columns):
            return ""
        scripts = _DRAWIO_VIEWER_SCRIPT if has_diagram else ""
        scripts += f'<script src="{self.commons_prefix}catalog-drawio.js?v=cdd-117"></script>'
        if has_columns:
            scripts += f'<script src="{self.commons_prefix}catalog-refine-row.js?v=cdd-2"></script>'
        return scripts
