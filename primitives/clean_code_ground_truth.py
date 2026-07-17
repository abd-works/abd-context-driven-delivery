"""Ground-truth loaders for clean-code.md concepts — shared by primitive and CLI specs."""

from __future__ import annotations

import re
from pathlib import Path

from primitives.instruction import Instruction

CONCEPT_RULE_PATTERN = re.compile(r"\*\*`([^`]+)`\*\*")
CONCEPT_SUBSECTION_PATTERN = re.compile(r"^## .+$", re.MULTILINE)


def load_concepts_section(clean_code_dir: Path) -> str:
    return Instruction("§ Concepts", clean_code_dir).expand()


def load_examples(clean_code_dir: Path) -> str:
    return Instruction("examples", clean_code_dir).expand()


def load_python_template(clean_code_dir: Path) -> str:
    return Instruction("formats/python/clean-code-templates.py", clean_code_dir).expand()


def concept_rule_slugs(concepts_text: str) -> list[str]:
    return CONCEPT_RULE_PATTERN.findall(concepts_text)


def concept_bullet_lines(concepts_text: str) -> list[str]:
    return [
        line.strip()
        for line in concepts_text.splitlines()
        if CONCEPT_RULE_PATTERN.search(line)
    ]


def concept_subsection_headings(concepts_text: str) -> list[str]:
    return CONCEPT_SUBSECTION_PATTERN.findall(concepts_text)


def format_subdirectory_names(clean_code_dir: Path) -> list[str]:
    formats_dir = clean_code_dir / "formats"
    return sorted(entry.name for entry in formats_dir.iterdir() if entry.is_dir())
