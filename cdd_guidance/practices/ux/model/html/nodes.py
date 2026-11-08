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


_VISUAL_STATES = frozenset({"selected", "disabled", "primary", "expanded", "collapsed", "hidden", "checked", "error"})


class HtmlControl(Control):
    """A control in the review page: a visible affordance for its control type, with the data attributes the
    mockup's scripts read to follow its interactions."""

    def html(self) -> str:
        ctype = (self.control_type or "").lower()
        visual = {state.lower() for state in self.states} & _VISUAL_STATES
        writer = _CONTROL_WRITERS.get(ctype)
        if writer is not None:
            return writer(self, visual)
        if ctype == "error" or "error" in visual:
            return f'<div class="control error"{self._name_attr()}{_flag(visual, "hidden")}>! {_text(self.label)}</div>'
        return (
            f'<div class="control{_flag(visual, "selected")}{_flag(visual, "disabled")}" data-type="{ctype or "unknown"}"'
            f'{self._name_attr()}{_flag(visual, "hidden")}>{_text(self.label)}</div>'
        )

    def data_attributes(self) -> str:
        """Where its interactions go, then the Story Demo runner's attributes."""
        return f"{self._interaction_attrs()}{self._demo_attrs()}"

    def input_key(self) -> str:
        """The field a number input fills: its bound field, else its name."""
        return self.bound_field or self.name

    def _name_attr(self) -> str:
        return f' data-name="{_text(self.name)}"'

    def _interaction_attrs(self) -> str:
        goto = trigger = effect = ""
        for interaction in self.interactions:
            if interaction.destination is not None:
                goto = f' data-goto="{_text(interaction.destination.name)}"'
            if interaction.trigger:
                trigger = f' data-trigger="{_text(interaction.trigger)}"'
            if interaction.effect:
                effect = f' data-effect="{_text(interaction.effect)}"'
        return f"{goto}{trigger}{effect}"

    def _demo_values(self) -> dict:
        return {"data-bound-field": self.bound_field}

    def _demo_attrs(self) -> str:
        """The data attributes the Story Demo runner reads to fill and run a generated mockup's controls."""
        return "".join(f' {attribute}="{_text(value)}"' for attribute, value in self._demo_values().items() if value)

    def _button(self, visual: set) -> str:
        return (
            f'<button type="button" class="control button{_flag(visual, "primary")}{_flag(visual, "selected")}'
            f'{_flag(visual, "disabled")}"{self._name_attr()}{self.data_attributes()}{_flag(visual, "hidden")}>'
            f"{_text(self.label)}</button>"
        )

    def _text_input(self, visual: set) -> str:
        return (
            f'<label class="control{_flag(visual, "disabled")}"{self._name_attr()}{_flag(visual, "hidden")}>{_text(self.label)} '
            f'<input type="text" value="" placeholder="________" /></label>'
        )

    def _number_input(self, visual: set) -> str:
        return (
            f'<label class="control{_flag(visual, "disabled")}"{self._name_attr()}{_flag(visual, "hidden")}>{_text(self.label)} '
            f'<input type="number" min="1" step="1" value="1" '
            f'data-input-field="{_text(self.input_key())}" /></label>'
        )

    def _bound_list(self, visual: set) -> str:
        # Domain-agnostic list: the mount script paints one item per entry at the bound_field expose path.
        # item_story_steps => clicking an item runs its When; else set_input => clicking an item only selects it.
        return (
            f'<div class="control" data-type="bound-list" data-bound-list'
            f'{self._name_attr()}{self.data_attributes()}{_flag(visual, "hidden")}>'
            f'<div class="field dimmed">(list loads with story)</div></div>'
        )

    def _dropdown(self, visual: set) -> str:
        options = [state for state in self.states if state.lower() not in visual] or [self.label]
        choices = "".join(f'<option value="{_text(option.lower())}">{_text(option)}</option>' for option in options)
        return (
            f'<label class="control{_flag(visual, "disabled")}"{self._name_attr()}{_flag(visual, "hidden")}>{_text(self.label)} '
            f"<select>{choices}</select></label>"
        )

    def _checkbox(self, visual: set) -> str:
        checked = " checked" if visual & {"checked", "selected"} else ""
        return (
            f'<label class="control{_flag(visual, "disabled")}"{self._name_attr()}{_flag(visual, "hidden")}>'
            f'<input type="checkbox"{checked}{_flag(visual, "disabled")} /> {_text(self.label)}</label>'
        )

    def _tree(self, visual: set) -> str:
        twist = "v" if "expanded" in visual else ">" if "collapsed" in visual else "."
        role = ' data-role="folder"' if visual & {"expanded", "collapsed"} else ""
        return (
            f'<div class="tree-node{_flag(visual, "selected")}" data-type="tree"{self._name_attr()}{role}'
            f'{self.data_attributes()}{_flag(visual, "hidden")}><span class="twist">{twist}</span>{_text(self.label)}</div>'
        )

    def _list(self, visual: set) -> str:
        return (
            f'<div class="control{_flag(visual, "selected")}{_flag(visual, "disabled")}" data-type="list"'
            f'{self._name_attr()}{self.data_attributes()}{_flag(visual, "hidden")}>{_text(self.label)}</div>'
        )


class HtmlStoryDemoControl(StoryDemoControl, HtmlControl):
    """A Story Demo control in the review page: it also carries the steps it runs and the input it fills."""

    def input_key(self) -> str:
        """The scenario input it fills, else its bound field, else its name."""
        return self.set_input or super().input_key()

    def _demo_values(self) -> dict:
        return {
            **super()._demo_values(),
            "data-story-steps": _steps_json(self.story_steps),
            "data-set-input": self.set_input,
            "data-item-story-steps": _steps_json(self.item_story_steps),
            "data-item-value": self.item_value,
            "data-item-label": self.item_label,
        }


_CONTROL_WRITERS = {
    **dict.fromkeys(("button", "button-bar"), HtmlControl._button),
    **dict.fromkeys(("text", "input"), HtmlControl._text_input),
    **dict.fromkeys(("number", "quantity"), HtmlControl._number_input),
    **dict.fromkeys(("bound-list", "list-host"), HtmlControl._bound_list),
    **dict.fromkeys(("dropdown", "select"), HtmlControl._dropdown),
    **dict.fromkeys(("checkbox", "check"), HtmlControl._checkbox),
    "tree": HtmlControl._tree,
    **dict.fromkeys(("list", "listbox"), HtmlControl._list),
}


class HtmlUxMap(JsonUxMap):
    """Render a review shell: mockup on the left, story explorer on the right. The shell carries the map's JSON
    document, so this is the JSON format inside a page: parse reads back the document the shell carries; HTML
    written any other way is not a parse source. Its controls are HtmlControls, which write their own markup."""

    workspace_files = ("{folder}.html", "index.html", "mockup.html", "ux.html", "*.html")
    control_type = HtmlControl
    story_demo_control_type = HtmlStoryDemoControl

    def parse(self, content: str) -> UxMap:
        start = content.find(_MODEL_MARKER)
        end = content.find(_COMMENT_END, start + len(_MODEL_MARKER)) if start >= 0 else -1
        if end < 0:
            raise UxMapNotEmbedded("This HTML has no ux-map-json comment; render the map to HTML to read it back.")
        return super().parse(content[start + len(_MODEL_MARKER):end].strip())

    def save(self) -> str:
        shell = _SHELL_PATH.read_text(encoding="utf-8")
        for marker, value in self._shell_values().items():
            shell = shell.replace(marker, value)
        return shell

    def _shell_values(self) -> dict[str, str]:
        screens = "".join(self._screen_html(screen, index) for index, screen in enumerate(self.screens))
        return {
            "@@TITLE@@": _text(self.scope or self.name),
            "@@SCREENS@@": screens or "<p>No screens yet.</p>",
            "@@STORY_OUTLINE@@": _script_json(self.story_outline()),
            "@@SCREEN_STORIES@@": _script_json([
                {"name": screen.name, "stories": [{"name": story} for story in screen.story_keys]}
                for screen in self.screens
            ]),
            "@@ENSURE_HINT@@": self._ensure_hint(),
            "@@STORY_IMPORTS@@": _module_imports(self.story_references, "data-ux-story-ref"),
            "@@OBJECT_IMPORTS@@": _module_imports(self.object_references, "data-ux-object-ref"),
            "@@TRANSITIONS_JS@@": ",\n".join(
                "    " + _script_json({"from": _name_of(t.from_screen), "to": _name_of(t.to_screen), "trigger": t.trigger})
                for t in self.transitions
            ),
            # ">" is written as its JSON escape, so no value can close the comment the map is carried in.
            "@@MODEL_JSON@@": super().save().replace(">", "\\u003e"),
        }

    def _ensure_hint(self) -> str:
        if self.story_references or self.object_references:
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
        if screen.story_keys:
            joined = _text(", ".join(screen.story_keys))
            stories_attr = f' data-stories="{joined}" data-for-story="{joined}"'
        layout_attr = f' data-layout="{_text(screen.layout)}"' if screen.layout else ""
        return (
            f'<article class="screen" data-slug="{_text(screen.slug)}"'
            f"{stories_attr}{layout_attr}{hidden}>"
            f"<h2>{_text(screen.name)}</h2>"
            f'<p class="layout">{_text(screen.layout) or "-"}</p>'
            f'<div class="regions">{regions}</div>'
            f'<p class="screen-stories">Stories: {_text(" . ".join(screen.story_keys)) or "-"}</p>'
            f"</article>"
        )

    def _region_html(self, region: Region) -> str:
        controls = "".join(control.html() for control in region.controls)
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


def _flag(visual: set, state: str) -> str:
    """The class or attribute a visual state adds: ` selected` for a selected control, nothing when it is not."""
    return f" {state}" if state in visual else ""


def _steps_json(steps: list[StoryStep]) -> str:
    return json.dumps([step.as_dict() for step in steps], separators=(",", ":")) if steps else ""
