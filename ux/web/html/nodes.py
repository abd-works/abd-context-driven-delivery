"""HTML(+JS[+CSS]) channel — one channel; fidelity deepens brand/css."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from ux.document.json.nodes import JsonUxMap
from ux.ux_model.ux_map import UxMap

_SHELL_PATH = Path(__file__).resolve().parents[2] / "templates" / "html" / "mockup_shell.html"


class HtmlUxMap(UxMap):
    """Render a review shell: mockup on the left, story names at the bottom."""

    @classmethod
    def parse(cls, content: str) -> UxMap:
        """Scaffold parse: if JSON embedded in a comment marker, reuse JsonUxMap."""
        marker = "<!-- ux-map-json:"
        if marker in content:
            start = content.index(marker) + len(marker)
            end = content.index("-->", start)
            return JsonUxMap.parse(content[start:end].strip())
        ux_map = cls()
        ux_map.context.notes.append("html parse stub — structural DOM parser later")
        return ux_map

    @classmethod
    def render(cls, ux_map: UxMap) -> str:
        story_names = ux_map.all_story_names()
        story_imports = "\n".join(
            f'  <script type="module" src="{path}" data-ux-story-ref></script>'
            for path in ux_map.story_references
        )
        object_imports = "\n".join(
            f'  <script type="module" src="{path}" data-ux-object-ref></script>'
            for path in ux_map.object_references
        )
        ensure_hint = ""
        if not ux_map.story_references and not ux_map.object_references:
            ensure_hint = (
                "  <!-- Bind story/object JS via Ux.ensure_javascript "
                "(Stories/CE transform to javascript) then set story_references / "
                "object_references on the UxMap. -->\n"
            )
        screens_html = []
        for screen in ux_map.screens:
            hidden = " hidden" if screen != ux_map.screens[0] else ""
            regions = []
            for region in screen.regions:
                controls = "".join(
                    _render_control(control) for control in region.controls
                ) or f'<p class="region-placeholder">{region.name}</p>'
                regions.append(
                    f'<section class="region" data-slot="{region.slot}" '
                    f'data-region="{region.name}">'
                    f"<h3>{region.name}</h3>{controls}</section>"
                )
            story_trace = " · ".join(screen.story_names)
            layout_attr = f' data-layout="{screen.layout}"' if screen.layout else ""
            screens_html.append(
                f'<article class="screen" data-slug="{screen.slug}"'
                f"{layout_attr}{hidden}>"
                f"<h2>{screen.name}</h2>"
                f'<p class="layout">{screen.layout or "—"}</p>'
                f'<div class="regions">{"".join(regions)}</div>'
                f'<p class="screen-stories">Stories: {story_trace or "—"}</p>'
                f"</article>"
            )
        stories_list = (
            "".join(f"<li>{name}</li>" for name in story_names)
            or "<li>(waiting for story JS modules)</li>"
        )
        model_json = JsonUxMap.render(ux_map).replace("-->", "")
        transitions_js = ",\n".join(
            f'    {{from: "{t.from_screen}", to: "{t.to_screen}", '
            f'trigger: "{t.trigger}"}}'
            for t in ux_map.transitions
        )
        shell = _SHELL_PATH.read_text(encoding="utf-8")
        return (
            shell.replace("@@TITLE@@", ux_map.scope or ux_map.name)
            .replace("@@SCREENS@@", "".join(screens_html) or "<p>No screens yet.</p>")
            .replace("@@STORIES_LIST@@", stories_list)
            .replace("@@ENSURE_HINT@@", ensure_hint)
            .replace("@@STORY_IMPORTS@@", story_imports)
            .replace("@@OBJECT_IMPORTS@@", object_imports)
            .replace("@@TRANSITIONS_JS@@", transitions_js)
            .replace("@@MODEL_JSON@@", model_json)
        )

    @classmethod
    def from_workspace(cls, root: Path) -> Optional[UxMap]:
        root = Path(root)
        preferred = [
            root / f"{root.name}.html",
            root / "index.html",
            root / "mockup.html",
            root / "ux.html",
        ]
        for candidate in preferred:
            if candidate.is_file():
                return cls.parse(candidate.read_text(encoding="utf-8"))
        html_files = sorted(p for p in root.glob("*.html") if p.is_file())
        if html_files:
            return cls.parse(html_files[0].read_text(encoding="utf-8"))
        return None


def _interaction_attrs(control) -> str:
    goto = ""
    trigger = ""
    effect = ""
    for interaction in control.interactions:
        if interaction.destination_screen:
            goto = f' data-goto="{interaction.destination_screen}"'
        if interaction.trigger:
            trigger = f' data-trigger="{interaction.trigger}"'
        if interaction.effect:
            effect = f' data-effect="{interaction.effect}"'
    return f"{goto}{trigger}{effect}"


def _render_control(control) -> str:
    """Render a control as a visible affordance (sketch glyphs → HTML)."""
    ctype = (control.control_type or "").lower()
    label = control.label or control.name
    name = control.name
    states = {state.lower() for state in control.states}
    visual = {
        s
        for s in states
        if s
        in {
            "selected",
            "disabled",
            "primary",
            "expanded",
            "collapsed",
            "hidden",
            "checked",
            "error",
        }
    }
    selected = " selected" if "selected" in visual else ""
    disabled = " disabled" if "disabled" in visual else ""
    hidden = " hidden" if "hidden" in visual else ""
    attrs = _interaction_attrs(control)
    name_attr = f' data-name="{name}"'

    if ctype in {"button", "button-bar"}:
        primary = " primary" if "primary" in visual else ""
        return (
            f'<button type="button" class="control button{primary}{selected}{disabled}"'
            f"{name_attr}{attrs}{hidden}>{label}</button>"
        )
    if ctype in {"text", "input"}:
        return (
            f'<label class="control{disabled}"{name_attr}{hidden}>{label} '
            f'<input type="text" value="" placeholder="________" /></label>'
        )
    if ctype in {"dropdown", "select"}:
        options = [s for s in control.states if s.lower() not in visual]
        if not options:
            options = [label]
        opts = "".join(
            f'<option value="{opt.lower()}">{opt}</option>' for opt in options
        )
        return (
            f'<label class="control{disabled}"{name_attr}{hidden}>{label} '
            f"<select>{opts}</select></label>"
        )
    if ctype in {"checkbox", "check"}:
        checked = " checked" if "checked" in visual or "selected" in visual else ""
        return (
            f'<label class="control{disabled}"{name_attr}{hidden}>'
            f'<input type="checkbox"{checked}{disabled} /> {label}</label>'
        )
    if ctype == "tree":
        twist = "▼" if "expanded" in visual else "▶" if "collapsed" in visual else "·"
        role = (
            ' data-role="folder"'
            if "expanded" in visual or "collapsed" in visual
            else ""
        )
        return (
            f'<div class="tree-node{selected}" data-type="tree"{name_attr}{role}{attrs}{hidden}>'
            f'<span class="twist">{twist}</span>{label}</div>'
        )
    if ctype in {"list", "listbox"}:
        return (
            f'<div class="control{selected}{disabled}" data-type="list"'
            f"{name_attr}{attrs}{hidden}>{label}</div>"
        )
    if ctype == "error" or "error" in visual:
        return f'<div class="control error"{name_attr}{hidden}>! {label}</div>'
    return (
        f'<div class="control{selected}{disabled}" data-type="{ctype or "unknown"}"'
        f"{name_attr}{hidden}>{label}</div>"
    )
