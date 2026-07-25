# @toolset-manifest python -m tools manifest context_tools.base.context_tool:ContextTool
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# Do not author behavior from this Python source.
"""ContextTool composer — merges peer kits; shared domain face + kit-local action prose + @context_tool."""

from __future__ import annotations

import inspect
from pathlib import Path
from typing import TypeVar

from context_tools.base.artifact_lifecycle.artifact_lifecycle import ArtifactLifecycle
from partition_pipeline.partition_pipeline import PartitionPipeline
from primitives.actions.action import _ActionRunner
from primitives.instructions import Instruction
from primitives.instructions import instruction
from repair.repair import Repair
from scanners.scan import Scan
from tools.tool import Toolset
from sessions import WorkspaceSession

T = TypeVar("T", bound=type)


class ContextTool(
    ArtifactLifecycle,
    PartitionPipeline,
    Repair,
    Scan,
    WorkspaceSession,
    Toolset,
):
    """§ Instructions"""

    @property
    def module_dir(self) -> Path:
        return Path(inspect.getfile(type(self))).resolve().parent

    @instruction
    def contexts(self) -> Instruction: ...


ContextTool._is_context = True  # type: ignore[attr-defined]
ContextTool._is_toolset = True  # type: ignore[attr-defined]
_ActionRunner.instance().validate_toolset(ContextTool)


def context_tool(cls: T) -> T:
    """Merge a domain class with ContextTool."""
    if getattr(cls, "_is_context", False):
        return cls
    if issubclass(cls, ContextTool):
        raise TypeError(
            f"{cls.__name__} must use @context_tool — do not subclass ContextTool directly"
        )
    merged = type(
        cls.__name__,
        (cls, ContextTool),
        {
            attribute_name: attribute_value
            for attribute_name, attribute_value in vars(cls).items()
            if attribute_name not in ("__dict__", "__weakref__")
        },
    )
    merged.__doc__ = cls.__doc__
    merged.__module__ = cls.__module__
    merged.__qualname__ = cls.__qualname__
    merged._is_context = True  # type: ignore[attr-defined]
    merged._is_toolset = True  # type: ignore[attr-defined]
    _ActionRunner.instance().validate_toolset(merged)
    return merged
