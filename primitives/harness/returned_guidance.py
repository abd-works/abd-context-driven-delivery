# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""ReturnedGuidance — expand action: guidance at one fidelity; return response.instructions."""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path
from typing import Any

from primitives.actions.action import _ActionExpander

_LOADED_CLASSES: dict[tuple[str, str], type] = {}

_TEMPLATE_TAGS = ("Mu", "Md", "L", "S", "C")
_FIDELITY_TAG = {
    "modules": "Mu",
    "model": "Md",
    "specification": "S",
    "code": "C",
}


def _load_class(path: Path, class_name: str) -> type | None:
    """Load one class from its file so generate expands the source run time imports."""
    key = (str(path), class_name)
    if key in _LOADED_CLASSES:
        return _LOADED_CLASSES[key]
    if not class_name or not path.is_file():
        return None
    module_name = f"harness_returned_{len(_LOADED_CLASSES)}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    # Register before exec so inspect.getfile works on loaded classes
    # (BaseContextTool.module_dir and _expand_docstring both need it).
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        del sys.modules[module_name]
        return None
    loaded = getattr(module, class_name, None)
    if not isinstance(loaded, type):
        return None
    _LOADED_CLASSES[key] = loaded
    return loaded


def _guidance_function(cls: type) -> Any | None:
    """The class's @agent_instructions guidance member, or None."""
    func = getattr(cls, "guidance", None)
    if not callable(func):
        return None
    target = getattr(func, "__func__", func)
    if not getattr(target, "_is_agent_instructions", False):
        return None
    return func


def _fidelity_section(text: str, fidelity: str) -> str:
    """Select one exact ``## fidelity`` section from markdown."""
    lines = text.splitlines()
    heading = re.compile(rf"^##\s+{re.escape(fidelity)}(?:\s|$)", re.IGNORECASE)
    start = next((index for index, line in enumerate(lines) if heading.match(line)), None)
    if start is None:
        return ""
    end = len(lines)
    for index in range(start + 1, len(lines)):
        if re.match(r"^#{1,2}\s+", lines[index]):
            end = index
            break
    selected = "\n".join(lines[start:end]).strip()
    return f"# Contexts\n\n{selected}" if selected else ""


def _line_tags(line: str) -> tuple[set[str], bool]:
    """Return fidelity tags and whether they annotate a markdown section."""
    html = re.search(r"<!--\s*([^>]+?)\s*-->", line)
    if html:
        annotation = html.group(1).strip()
        if re.match(r"^(?:Mu|Md|L|S|C)(?:\b|\s*/)", annotation):
            return set(re.findall(r"\b(?:Mu|Md|L|S|C)\b", annotation)), True
    if "#" not in line:
        return set(), False
    annotation = line.rsplit("#", 1)[-1].strip()
    if re.fullmatch(
        r"(?:Mu|Md|L|S|C)(?:\s*/\s*(?:Mu|Md|L|S|C))*", annotation
    ):
        return set(re.findall(r"\b(?:Mu|Md|L|S|C)\b", annotation)), False
    return set(), False


def _filter_annotated_template(text: str, fidelity: str) -> str:
    """Keep only template lines/sections annotated for the requested fidelity.

    HTML comments annotate markdown sections; trailing ``# Md/S``-style tags
    annotate individual code lines. The legend and all other fidelities are
    mechanically excluded before the compound reaches the model.
    """
    target = _FIDELITY_TAG.get(fidelity)
    tagged = [_line_tags(line) for line in text.splitlines()]
    if not target or not any(tags for tags, _section in tagged):
        return text.strip()

    section_annotations = any(section for tags, section in tagged if tags)
    selected: list[str] = []
    active_section: set[str] = set()
    for line, (tags, section) in zip(text.splitlines(), tagged):
        if section_annotations:
            if section:
                active_section = tags
            include = target in (tags if tags else active_section)
        else:
            include = target in tags
        if include:
            selected.append(line.rstrip())
        elif selected and not line.strip():
            selected.append("")

    while selected and not selected[-1]:
        selected.pop()
    compact: list[str] = []
    for line in selected:
        if not line and compact and not compact[-1]:
            continue
        compact.append(line)
    return "\n".join(compact).strip()


def _strip_invocation_prose(text: str) -> str:
    """Drop run-time invocation text from already-expanded guidance assets."""
    omitted = (
        "Pipe the fence to stdin",
        "Run: python -m tools run -",
        ".\\tools.ps1 run -",
    )
    return "\n".join(
        line for line in text.splitlines() if not any(item in line for item in omitted)
    ).strip()


def compound_guidance(
    path: Path | str,
    class_name: str,
    fidelity: str,
    constructor_context: dict[str, str] | None = None,
) -> str:
    """Compile fidelity-only guidance without any run-time invocation prose."""
    source_path = Path(path)
    loaded = _load_class(source_path, class_name)
    if loaded is None:
        return ""
    guidance_func = _guidance_function(loaded)
    if guidance_func is None:
        return ""
    context: dict[str, Any] = {"fidelity": fidelity}
    for param, value in (constructor_context or {}).items():
        context.setdefault(param, value)
    try:
        instance = loaded(**context)
        parts = list(
            _ActionExpander.instance().parse_body(guidance_func, instance).prose_parts
        )
    except Exception:
        return ""
    if len(parts) < 3:
        return ""

    selected_context = _fidelity_section(parts[2], fidelity) or parts[2].strip()

    selected = [selected_context]
    for part in parts[3:]:
        if part.lstrip().startswith("Separate tools run"):
            continue
        filtered = _strip_invocation_prose(
            _filter_annotated_template(part, fidelity)
        )
        if filtered:
            selected.append(filtered)
    return "\n\n".join(part for part in selected if part).strip()
