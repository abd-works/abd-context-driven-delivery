# @toolset-manifest python -m tools manifest generator.generator:Generator
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# Do not author behavior from this Python source.
"""Build or patch Generator domains — scaffold @generator_class_annotation toolsets."""

from __future__ import annotations

import inspect
from pathlib import Path
from typing import TypeVar
from agents.action import action
from agents.runner import ActionRunner
from primitives.instruction import Instruction
from primitives.instruction_slot import instruction
from scanners import ScannerCollection
from tools.tool import Toolset, tool

T = TypeVar("T", bound=type)


class Generator(Toolset):
    """§ Instructions"""

    def __init__(self, format: str | None = None) -> None:
        super().__init__()
        self.format = format

    @property
    def module_dir(self) -> Path:
        return Path(inspect.getfile(type(self))).resolve().parent

    @instruction
    def concepts(self) -> Instruction: ...

    @instruction(collection=True)
    def rules(self) -> Instruction: ...

    @instruction
    def domain_generate(self) -> Instruction: ...

    @instruction
    def examples(self) -> Instruction: ...

    @instruction(group="formats", filter_key="format")
    def template(self) -> Instruction: ...

    @instruction(collection=True)
    def templates(self) -> Instruction: ...

    @action
    def add_generate_header_to_generated(self) -> str:
        """Prepend the following block verbatim as the very first lines of the file you are writing — before any imports, before any code."""
        return (
            '"""\n'
            f"# @toolset-manifest {type(self).manifest_command}\n"
            '"""\n'
        )

    @action
    def generate_output(self) -> str:
        """"""
        return ""

    def _scanner_collection(self) -> ScannerCollection:
        scanner_root = self.module_dir / "scanners"
        formats_dir = self.module_dir / "formats"
        if formats_dir.is_dir() and self.format:
            scanner_root = formats_dir / self.format / "scanners"
        return ScannerCollection(self.module_dir, scanner_root)

    @action
    def generate(self) -> str:
        """base-generator/generate"""
        self.concepts
        self.rules
        self.domain_generate
        self.examples
        self.templates
        self.template
        self.generate_output()
        self.add_generate_header_to_generated()
        return "When done, run validate."

    @action
    def validate(self) -> str:
        """base-generator/validate"""
        self.concepts
        self.scan()
        return "Validation report."

    @action
    def satisfy(self) -> str:
        """base-generator/satisfy"""
        self.concepts
        self.template
        return "When done, run validate."

    @action
    def repair(self, asset: str, violation: str) -> str:
        """base-generator/repair"""
        self.scan()
        self.concepts
        self.examples
        self.template
        self.validate()
        return "Repair {asset} until validate passes."

    @tool
    def scan(self, paths: list[str]) -> str:
        """base-generator/scan"""
        files = [Path(path) for path in paths]
        report = self._scanner_collection().run(Path.cwd(), files)
        return str(report.to_dict())


Generator._is_generator = True  # type: ignore[attr-defined]
Generator._is_toolset = True  # type: ignore[attr-defined]
ActionRunner.instance().validate_toolset(Generator)


def generator_class_annotation(cls: T) -> T:
    if getattr(cls, "_is_generator", False):
        return cls
    if issubclass(cls, Generator):
        raise TypeError(
            f"{cls.__name__} must use @generator_class_annotation — do not subclass Generator directly"
        )
    merged = type(
        cls.__name__,
        (cls, Generator),
        {
            attribute_name: attribute_value
            for attribute_name, attribute_value in vars(cls).items()
            if attribute_name not in ("__dict__", "__weakref__")
        },
    )
    merged.__doc__ = cls.__doc__
    merged.__module__ = cls.__module__
    merged.__qualname__ = cls.__qualname__
    merged._is_generator = True  # type: ignore[attr-defined]
    merged._is_toolset = True  # type: ignore[attr-defined]
    ActionRunner.instance().validate_toolset(merged)
    return merged
