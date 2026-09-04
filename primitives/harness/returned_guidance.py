# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""ReturnedGuidance — expand action: guidance at one fidelity; return response.instructions."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

from primitives.actions.action import _ActionExpandRequest, _ActionExpander

_LOADED_CLASSES: dict[tuple[str, str], type] = {}


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


def returned_guidance(
    path: Path | str,
    class_name: str,
    toolset: str,
    fidelity: str,
    constructor_context: dict[str, str] | None = None,
) -> str:
    """Run the context tool's guidance action at one fidelity — the run-time
    expansion path — and return response.instructions to bake into a
    ``{context_tool}-{fidelity}`` command.

    Empty string when the class has no expandable guidance or the expansion
    fails; the caller falls back to the guidance docstring.
    """
    loaded = _load_class(Path(path), class_name)
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
        tools = dict(getattr(instance, "tools", None) or {})
        expanded = _ActionExpander.instance().expand(
            _ActionExpandRequest(
                action_func=guidance_func,
                toolset_path=toolset,
                context=context,
                arguments={},
                tool_callables={
                    name: getattr(tool, "callable", tool) for name, tool in tools.items()
                },
                instance=instance,
            )
        )
    except Exception:
        return ""
    return str(expanded.get("instructions") or "").strip()
