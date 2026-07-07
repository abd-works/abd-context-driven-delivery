"""Filesystem loader — reads a skill directory and produces a Skill aggregate.

This is an adapter over the skill model. It handles:

- Walking the skill directory tree
- Parsing YAML front matter delimited by ``---`` at the top of each file
- Translating unknown/malformed front matter into Anomalies (soft-fail)
- Producing typed SkillFiles the skill model can reason about
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from ..assembly.anomaly import Anomaly
from ..assembly.fidelity import Fidelity, UnknownFidelityError
from ..assembly.front_matter import FrontMatter
from ..assembly.skill import Skill
from ..assembly.skill_file import SkillFile

_FRONT_MATTER_PATTERN = re.compile(
    r"\A---\s*\n(?P<body>.*?)\n---\s*(\n|$)",
    re.DOTALL,
)

_KNOWN_DIRECTORIES = {
    "concepts",
    "behavior",
    "rules",
    "templates",
    "examples",
    "generate-instructions",
    "grill-me-questions",
}

_INCLUDED_SUFFIXES = {".md"}


def load_skill(skill_root: Path, name: str | None = None) -> Skill:
    skill_root = skill_root.resolve()
    skill_files: list[SkillFile] = []
    anomalies: list[Anomaly] = []

    for path in sorted(skill_root.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix not in _INCLUDED_SUFFIXES:
            continue
        relative_path = path.relative_to(skill_root)
        directory = relative_path.parts[0]
        if directory not in _KNOWN_DIRECTORIES:
            continue

        file_contents = path.read_text(encoding="utf-8")
        parsed_front_matter, file_anomalies = _parse_front_matter(
            relative_path.as_posix(), file_contents
        )
        anomalies.extend(file_anomalies)

        if parsed_front_matter is None:
            continue

        skill_files.append(
            SkillFile(
                path=relative_path.as_posix(),
                directory=directory,
                front_matter=parsed_front_matter,
            )
        )

    return Skill(
        name=name or skill_root.name,
        files=tuple(skill_files),
        load_anomalies=tuple(anomalies),
    )


def _parse_front_matter(
    relative_path: str,
    file_contents: str,
) -> tuple[FrontMatter | None, list[Anomaly]]:
    match = _FRONT_MATTER_PATTERN.match(file_contents)
    if match is None:
        return None, [Anomaly(kind="missing_front_matter", file=relative_path)]

    try:
        raw_front_matter = yaml.safe_load(match.group("body")) or {}
    except yaml.YAMLError as error:
        return None, [
            Anomaly(
                kind="invalid_yaml",
                file=relative_path,
                details={"error": str(error)},
            )
        ]

    if not isinstance(raw_front_matter, dict):
        return None, [
            Anomaly(
                kind="front_matter_not_mapping",
                file=relative_path,
                details={"type": type(raw_front_matter).__name__},
            )
        ]

    fidelities, fidelity_anomalies = _parse_fidelities(
        relative_path, raw_front_matter.get("fidelity")
    )
    artifact = _parse_str_list(raw_front_matter.get("artifact"))
    raw_format = raw_front_matter.get("format")
    section = raw_front_matter.get("section")
    scanner = raw_front_matter.get("scanner")

    return (
        FrontMatter(
            fidelities=frozenset(fidelities),
            format=str(raw_format) if raw_format else None,
            section=str(section) if section else None,
            artifact=frozenset(artifact),
            scanner=str(scanner) if scanner else None,
            raw=raw_front_matter,
        ),
        fidelity_anomalies,
    )


def _parse_fidelities(
    relative_path: str,
    value: Any,
) -> tuple[list[Fidelity], list[Anomaly]]:
    if value is None:
        return [], []
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, list):
        return [], [
            Anomaly(
                kind="fidelity_not_list",
                file=relative_path,
                details={"value": repr(value)},
            )
        ]

    fidelities: list[Fidelity] = []
    anomalies: list[Anomaly] = []
    for entry in value:
        try:
            fidelities.append(Fidelity.parse(str(entry)))
        except UnknownFidelityError as error:
            anomalies.append(
                Anomaly(
                    kind="unknown_fidelity",
                    file=relative_path,
                    details={"value": error.value},
                )
            )
    return fidelities, anomalies


def _parse_str_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(entry) for entry in value]
    return []
