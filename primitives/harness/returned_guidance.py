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
    *,
    toolset: str = "",
) -> str:
    """Compile fidelity guidance by running the tool via the CLI and returning instructions."""
    import subprocess
    import yaml as _yaml

    ts = toolset.strip()
    if not ts:
        # Derive toolset from path + class_name
        source_path = Path(path)
        parts = list(source_path.with_suffix("").parts)
        ts = ".".join(parts) + ":" + class_name

    ctx_lines = f"  fidelity: {fidelity}"
    for k, v in (constructor_context or {}).items():
        if k != "fidelity":
            ctx_lines += f"\n  {k}: {v}"

    yaml_input = f"toolset: {ts}\ncontext:\n{ctx_lines}\naction: guidance\n"

    env = {**__import__("os").environ, "PYTHONIOENCODING": "utf-8"}
    try:
        result = subprocess.run(
            [__import__("sys").executable, "-m", "tools", "run", "-"],
            input=yaml_input,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=env,
        )
        output = result.stdout.strip()
    except Exception:
        return ""

    # Strip fenced yaml block markers
    if output.startswith("```yaml"):
        output = output[len("```yaml"):].lstrip("\n")
    if output.endswith("```"):
        output = output[:-3].rstrip()

    try:
        data = _yaml.safe_load(output)
    except Exception:
        return ""

    if not isinstance(data, dict) or not data.get("ok"):
        return ""

    instructions = (data.get("instructions") or "").strip()
    instructions = _strip_invocation_prose(instructions)

    # Strip the leading agent-instructions preamble (method docstring +
    # "Provide guidance from contexts, examples, and templates.") so only
    # the actual domain content (# Contexts, examples, templates) remains.
    _BASE_MARKER = "Provide guidance from contexts, examples, and templates."
    idx = instructions.find(_BASE_MARKER)
    if idx >= 0:
        instructions = instructions[idx + len(_BASE_MARKER):].lstrip("\n")

    # Strip trailing tool-manifest boilerplate ("Separate tools run…" onwards).
    _SEP = "Separate tools run"
    sep_idx = instructions.find(_SEP)
    if sep_idx >= 0:
        instructions = instructions[:sep_idx].rstrip()

    # Cut off everything from the first file-path heading (examples + inlined
    # templates from the CLI).  We replace them with path references instead.
    import re as _re
    source_path = Path(path)
    module_dir = source_path.parent

    file_heading = _re.compile(
        r"(^## (?:[^\n]*/[^\n]*|[^\n]+\.[a-zA-Z]{2,4})$)", _re.MULTILINE
    )
    first_file = file_heading.search(instructions)
    contexts = instructions[:first_file.start()].rstrip() if first_file else instructions.rstrip()

    result = contexts

    # Templates — inline a direct Python call (no manifest/YAML).
    templates_dir = module_dir / "templates"
    if templates_dir.is_dir():
        # Derive short class import path from toolset string
        module_import = ts.rsplit(":", 1)[0] if ":" in ts else ts
        class_import = ts.rsplit(":", 1)[1] if ":" in ts else class_name
        ctx_args = f'fidelity="{fidelity}"'
        if constructor_context:
            extra = ", ".join(f'{k}="{v}"' for k, v in constructor_context.items() if k != "fidelity")
            if extra:
                ctx_args += f", {extra}"
        result += (
            f"\n\n## Templates\n\n"
            f"Call `load_template` directly with your active format and fidelity:\n\n"
            f"```python\n"
            f"from {module_import} import {class_import}\n"
            f"{class_import}({ctx_args}).load_template(format=\"<your_format>\", fidelity=\"{fidelity}\")\n"
            f"```"
        )

    # Examples — reference only.
    examples_dir = module_dir / "examples"
    if examples_dir.is_dir():
        try:
            rel_ex = examples_dir.relative_to(Path(__file__).resolve().parents[2])
        except ValueError:
            rel_ex = examples_dir
        result += f"\n\nSee examples in `{rel_ex.as_posix()}/` if needed."

    return result


def _inline_templates(
    source_path: Path,
    class_name: str,
    fidelity: str,
    constructor_context: dict[str, str] | None,
) -> list[str]:
    """Directly call load_template on the class for every supported format."""
    import sys as _sys

    repo_root = source_path.resolve().parents[2]
    for extra in ("context_tools/actions", "context_tools", "utilities", "primitives"):
        p = str(repo_root / extra)
        if p not in _sys.path:
            _sys.path.insert(0, p)

    cls = _load_class(source_path, class_name)
    if cls is None:
        return []

    supported: list[str] = sorted(
        str(f) for f in getattr(cls, "supported_formats", None) or []
    )
    fidelity_defaults: dict[str, str] = getattr(cls, "_fidelity_format_defaults", {}) or {}
    default_fmt = fidelity_defaults.get(fidelity, "")
    if not supported:
        supported = [default_fmt] if default_fmt else []

    base_ctx: dict[str, Any] = {"fidelity": fidelity}
    for k, v in (constructor_context or {}).items():
        base_ctx.setdefault(k, v)

    blocks: list[str] = []
    seen: set[str] = set()
    for fmt in supported:
        try:
            instance = cls(**{**base_ctx, "format": fmt})
            content = instance.load_template(format=fmt)
        except Exception:
            continue
        if not content or "No template found" in content or content in seen:
            continue
        seen.add(content)
        blocks.append(f"### {fmt}\n\n{content}")

    return blocks
