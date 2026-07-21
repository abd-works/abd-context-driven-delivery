# @toolset-manifest python -m tools manifest contexts.base.context:Context
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# Do not author behavior from this Python source.
"""Build or patch Context domains — scaffold @context toolsets (class Context + @context)."""

from __future__ import annotations

import inspect
from pathlib import Path
from typing import TypeVar
from primitives.actions.action import _ActionRunner, action
from primitives.instructions import Instruction
from primitives.instructions import instruction
from record_decisions import record_decisions
from scanners import ScannerCollection
from tools.tool import Toolset, tool
from session_logging import log

T = TypeVar("T", bound=type)

_DEFAULT_PARTITION_GUIDANCE = (
    "Determine top-level structure based on user suggestion, available context, "
    "skill-provided material, and what is evident in the source. "
    "Keep it thin — only enough to ground partitions; TODOs are fine."
)


class Context(Toolset):
    """§ Instructions"""

    def __init__(self, format: str | None = None) -> None:
        super().__init__()
        self.format = format

    @property
    def module_dir(self) -> Path:
        return Path(inspect.getfile(type(self))).resolve().parent

    @instruction
    def contexts(self) -> Instruction: ...

    @instruction
    def generate_instructions(self) -> Instruction: ...

    @instruction
    def document_instructions(self) -> Instruction: ...

    @instruction
    def examples(self) -> Instruction: ...

    @instruction
    def templates(self) -> Instruction: ...

    @instruction(override=True)
    def partition_guidance(self) -> str:
        """Domain partition.md when present; otherwise base default guidance."""
        path = self.module_dir / "partition.md"
        if path.is_file():
            return Instruction.ref(self, "partition").expand()
        return _DEFAULT_PARTITION_GUIDANCE

    @action
    def add_generate_header_to_generated(self) -> str:
        """Prepend the following block verbatim as the very first lines of the file you are writing — before any imports, before any code."""
        cls = type(self)
        return (
            '"""\n'
            f"# @toolset-manifest {cls.manifest_command}\n"
            "# Agent reading this file: run line 1 manifest, then python -m tools run -. "
            "Follow response.instructions only.\n"
            f"# invoke-edit: action satisfy | toolset: {cls.manifest_path}\n"
            f"# invoke-check: action validate | toolset: {cls.manifest_path}\n"
            '"""\n'
        )

    @action
    def generate_output(self) -> str:
        """"""
        return ""

    def _scanner_collection(self) -> ScannerCollection:
        return ScannerCollection()

    @record_decisions
    @log
    @action
    def generate(self) -> str:
        """base-context/generate"""
        self.contexts
        self.generate_instructions
        self.examples
        self.templates
        self.generate_output()
        self.add_generate_header_to_generated()
        return "When done, run validate."

    @action
    def validate(self) -> str:
        """base-context/validate"""
        self.contexts
        self.scan()
        return "Validation report."

    @action
    def document(self, paths: list[str]) -> str:
        """base-context/document"""
        self.contexts
        self.document_instructions
        self.templates
        self.scan(paths)
        self.generate_output()
        self.add_generate_header_to_generated()
        return "Document existing state — violations flagged, none corrected."

    @record_decisions
    @action
    def satisfy(self) -> str:
        """base-context/satisfy"""
        self.contexts
        self.templates
        return "When done, run validate."

    @action
    def repair(self, asset: str, violation: str) -> str:
        """base-context/repair"""
        self.scan()
        self.contexts
        self.examples
        self.templates
        self.validate()
        return "Repair {{asset}} until validate passes."

    @action
    def index(self, context: str, out_root: str | None = None) -> str:
        """base-context/index"""
        self.contexts
        self.partition_guidance
        return "Index written for {{context}}."

    @action
    def segment(self, out_root: str | None = None) -> str:
        """base-context/segment"""
        self.contexts
        self.partition_guidance
        return "Segments written from {{self.toolset_name}}-index.md."

    @action
    def partition(
        self,
        context: str,
        mode: str = "one_go",
        out_root: str | None = None,
    ) -> str:
        """base-context/partition"""
        self.contexts
        self.partition_guidance
        self.index(context, out_root)
        self.segment(out_root)
        return "Partition of {{context}} finished (mode {{mode}})."

    @tool
    def scan(self, paths: list[str]) -> str:
        """base-context/scan"""
        files = [Path(path) for path in paths]
        report = self._scanner_collection().run(Path.cwd(), files)
        return str(report.to_dict())


Context._is_context = True  # type: ignore[attr-defined]
Context._is_toolset = True  # type: ignore[attr-defined]
_ActionRunner.instance().validate_toolset(Context)


def context(cls: T) -> T:
    """Merge a domain class with Context."""
    if getattr(cls, "_is_context", False):
        return cls
    if issubclass(cls, Context):
        raise TypeError(
            f"{cls.__name__} must use @context — do not subclass Context directly"
        )
    merged = type(
        cls.__name__,
        (cls, Context),
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
