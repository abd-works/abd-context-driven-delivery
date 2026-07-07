"""Manifest — files selected for a run, grouped by top-level directory."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .anomaly import Anomaly
from .fidelity import Fidelity
from .phase import Phase
from .skill_file import SkillFile


@dataclass(frozen=True)
class Manifest:
    phase: Phase
    fidelities: tuple[Fidelity, ...]
    format: str
    files_by_directory: dict[str, tuple[SkillFile, ...]] = field(default_factory=dict)
    anomalies: tuple[Anomaly, ...] = ()

    def files(self) -> tuple[SkillFile, ...]:
        return tuple(
            skill_file
            for group in self.files_by_directory.values()
            for skill_file in group
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "phase": self.phase.value,
            "fidelities": [f.value for f in self.fidelities],
            "format": self.format,
            "files_by_directory": {
                directory: [skill_file.path for skill_file in group]
                for directory, group in self.files_by_directory.items()
            },
        }
