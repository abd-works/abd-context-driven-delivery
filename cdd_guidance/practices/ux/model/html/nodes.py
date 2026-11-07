"""HTML(+JS[+CSS]) channel - one channel; fidelity deepens brand/css."""

from __future__ import annotations

import html
import json
from pathlib import Path
from cdd_guidance.practices.ux.model.json.nodes import JsonUxMap
from cdd_guidance.practices.ux.model.nodes import Control, Region, Screen, StoryDemoControl, StoryStep
from cdd_guidance.practices.ux.model.ux_map import UxMap

_SHELL_PATH = Path(__file__).resolve().parents[2] / "templates" / "html" / "mockup_shell.html"
_MODEL_MARKER = "<!-- ux-map-json:"
_COMMENT_END = "-->"


class UxMapNotEmbedded(ValueError):
    """The HTML holds no UX map to read. Only a page this format rendered carries one, as JSON in a ux-map-json
    comment; any other HTML is a mockup to look at, not a source to parse."""


class HtmlUxMap(UxMap):
    """Render a review shell: mockup on the left, story explorer on the right. Parse reads back the map the shell
    carries; HTML written any other way is not a parse source."""

    workspace_files = ("{folder}.html", "index.html", "mockup.html", "ux.html", "*.html")

    def parse(self, content: str) -> UxMap:
        start = content.find(_MODEL_MARKER)
        end = content.find(_COMMENT_END, start + len(_MODEL_MARKER)) if start >= 0 else -1
        if end < 0:
            raise UxMapNotEmbedded("This HTML has no ux-map-json comment; render the map to HTML to read it back.")
        return JsonUxMap.create().parse(content[start + len(_MODEL_MARKER):end].strip())

    def render(self, ux_map: UxMap) -> str:
        shell = _SHELL_PATH.read_text(encoding="utf-8")
        for marker, value in self._shell_values(ux_map).items():
            shell = shell.replace(marker, value)
        return shell

    def _shell_values(self, ux_map: UxMap) -> dict[str, str]:
        screens = "".join(self._screen_html(screen, index) for index, screen in enumerate(ux_map.screens))
        return {
            "@@TITLE@@": _text(ux_map.scope or ux_map.name),
            "@@SCREENS@@": screens or "<p>No screens yet.</p>",
            "@@STORY_OUTLINE@@": _script_json(getattr(ux_map, "story_outline", None) or []),
            "@@SCREEN_STORIES@@": _script_json([
                {"name": screen.name, "stories": [{"name": story} for story in screen.story_names]}
                for screen in ux_map.screens
            ]),
            "@@ENSURE_HINT@@": self._ensure_hint(ux_map),
            "@@STORY_IMPORTS@@": _module_imports(ux_map.story_references, "data-ux-story-ref"),
            "@@OBJECT_IMPORTS@@": _module_imports(ux_map.object_references, "data-ux-object-ref"),
            "@@TRANSITIONS_JS@@": ",\n".join(
                "    " + _script_json({"from": _name_of(t.from_screen), "to": _name_of(t.to_screen), "trigger": t.trigger})
                for t in ux_map.transitions
            ),
            # ">" is written as its JSON escape, so no value can close the comment the map is carried in.
            "@@MODEL_JSON@@": JsonUxMap.create().render(ux_map).replace(">", "\\u003e"),
        }

    def _ensure_hint(self, ux_map: UxMap) -> str:
        if ux_map.story_references or ux_map.object_references:
            return ""
        return (
            "  <!-- Link story/object JS via Ux.ensure_javascript "
            "(Stories/CE transform to javascript) then set story_references / "
            "object_references on the UxMap. -->\n"
        )

    def _screen_html(self, screen: Screen, index: int) -> str:
        hidden = " hidden" if index else ""
        regions = "".join(self._region_html(region) for region in screen.regions)
        stories_attr = ""
        if screen.story_names:
            joined = _text(", ".join(screen.story_names))
            stories_attr = f' data-stories="{joined}" data-for-story="{joined}"'
        layout_attr = f' data-layout="{_text(screen.layout)}"' if screen.layout else ""
        return (
            f'<article class="screen" data-slug="{_text(screen.slug)}"'
            f"{stories_attr}{layout_attr}{hidden}>"
            f"<h2>{_text(screen.name)}</h2>"
            f'<p class="layout">{_text(screen.layout) or "-"}</p>'
            f'<div class="regions">{regions}</div>'
            f'<p class="screen-stories">Stories: {_text(" . ".join(screen.story_names)) or "-"}</p>'
            f"</article>"
        )

    def _region_html(self, region: Region) -> str:
        controls = "".join(_render_control(control) for control in region.controls)
        placeholder = f'<p class="region-placeholder">{_text(region.name)}</p>'
        return (
            f'<section class="region" data-area="{_text(region.area)}" data-region="{_text(region.name)}">'
            f"<h3>{_text(region.name)}</h3>{controls or placeholder}</section>"
        )


def _text(value: str) -> str:
    """Text and attribute values escaped for HTML."""
    return html.escape(value or "", quote=True)


def _script_json(value) -> str:
    """JSON for a script element; "<" is escaped so no value can close the script."""
    return json.dumps(value).replace("<", "\\u003c")


def _module_imports(paths, marker: str) -> str:
    return "\n".join(f'  <script type="module" src="{_text(path)}" {marker}></script>' for path in paths)


def _name_of(screen) -> str:
    return screen.name if screen is not None else ""


def _interaction_attrs(control: Control) -> str:
    goto = ""
    trigger = ""
    effect = ""
    for interaction in control.interactions:
        if interaction.destination is not None:
            goto = f' data-goto="{_text(interaction.destination.name)}"'
        if interaction.trigger:
            trigger = f' data-trigger="{_text(interaction.trigger)}"'
        if interaction.effect:
            effect = f' data-effect="{_text(interaction.effect)}"'
    return f"{goto}{trigger}{effect}"


def _story_demo_attrs(control: Control) -> str:
    """The data attributes the Story Demo runner reads to fill and run a generated mockup's controls."""
    values = {"data-bound-field": control.bound_field}
    if isinstance(control, StoryDemoControl):
        values.update({
            "data-story-steps": _steps_json(control.story_steps),
            "data-set-input": control.set_input,
            "data-item-story-steps": _steps_json(control.item_story_steps),
            "data-item-value": control.item_value,
            "data-item-label": control.item_label,
        })
    return "".join(f' {attribute}="{_text(value)}"' for attribute, value in values.items() if value)


def _steps_json(steps: list[StoryStep]) -> str:
    return json.dumps([step.as_dict() for step in steps], separators=(",", ":")) if steps else ""


def _render_control(control) -> str:
    """Render a control as a visible affordance (sketch glyphs -> HTML)."""
    ctype = (control.control_type or "").lower()
    label = _text(control.label)
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
    attrs = f"{_interaction_attrs(control)}{_story_demo_attrs(control)}"
    name_attr = f' data-name="{_text(name)}"'

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
    if ctype in {"number", "quantity"}:
        # Interactive reads via data-input-field; prefer set_input, then bound_field, then name.
        set_input = control.set_input if isinstance(control, StoryDemoControl) else ""
        input_key = _text(set_input or control.bound_field or name)
        return (
            f'<label class="control{disabled}"{name_attr}{hidden}>{label} '
            f'<input type="number" min="1" step="1" value="1" '
            f'data-input-field="{input_key}" /></label>'
        )
    if ctype in {"bound-list", "list-host"}:
        # Domain-agnostic list: the mount script paints one item per entry at the bound_field expose path.
        # item_story_steps => clicking an item runs its When; else set_input => clicking an item only selects it.
        return (
            f'<div class="control" data-type="bound-list" data-bound-list'
            f"{name_attr}{attrs}{hidden}>"
            f'<div class="field dimmed">(list loads with story)</div></div>'
        )
    if ctype in {"dropdown", "select"}:
        options = [s for s in control.states if s.lower() not in visual]
        if not options:
            options = [control.label]
        opts = "".join(
            f'<option value="{_text(opt.lower())}">{_text(opt)}</option>' for opt in options
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
        twist = "v" if "expanded" in visual else ">" if "collapsed" in visual else "."
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
