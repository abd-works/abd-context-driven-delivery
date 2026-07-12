"""Skill — a bag of SkillFiles that can be assembled into a Manifest for a run."""

from __future__ import annotations

from dataclasses import dataclass, field

from .anomaly import Anomaly
from .fidelity import Fidelity
from .manifest import Manifest
from .phase import Phase
from .skill_file import SkillFile


@dataclass(frozen=True)
class Skill:
    name: str
    files: tuple[SkillFile, ...] = ()
    load_anomalies: tuple[Anomaly, ...] = field(default_factory=tuple)

    def assemble(
        self,
        fidelities: frozenset[Fidelity],
        format: str,
        phase: Phase,
    ) -> Manifest:
        scope = set(phase.directories())
        matched: dict[str, list[SkillFile]] = {directory: [] for directory in scope}

        for skill_file in self.files:
            if skill_file.directory not in scope:
                continue
            if not skill_file.matches(fidelities, format):
                continue
            matched[skill_file.directory].append(skill_file)

        for directory in matched:
            matched[directory].sort(key=lambda skill_file: skill_file.path)

        files_by_directory = {
            directory: tuple(group) for directory, group in matched.items() if group
        }

        return Manifest(
            phase=phase,
            fidelities=tuple(f for f in Fidelity.all() if f in fidelities),
            format=format,
            files_by_directory=files_by_directory,
            anomalies=self.load_anomalies,
        )
