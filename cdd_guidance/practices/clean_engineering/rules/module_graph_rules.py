"""Module / package graph rules — folder shape and public seam markdown."""

from __future__ import annotations

import re
from pathlib import Path

from harness.graph.practice_rule import PracticeGraphRule
from cdd_guidance.practices.clean_engineering.model.module_context_files import ModuleContextFiles

_INTERNAL_MARKDOWN = re.compile(r"^##\s+Internal\b", re.MULTILINE | re.IGNORECASE)


class NamedSeamAndConstraint(PracticeGraphRule):
    slug = "named-seam-and-constraint"
    node_types = ("Module",)

    def check(self, node, context) -> list[str]:
        folder = context.module_folder(node)
        if folder is None:
            return []
        marker = folder / ".context" / "module-context.md"
        if marker.is_file():
            return []
        return [f"Module '{node.name}' is missing .context/module-context.md."]


class PublicSeamOnly(PracticeGraphRule):
    slug = "public-seam-only"
    node_types = ("Module", "Package")

    def check(self, node, context) -> list[str]:
        text = _module_source_text(context, node)
        if not text:
            return []
        if _INTERNAL_MARKDOWN.search(text):
            return [f"Module '{node.name}' exposes internal design in a public source file."]
        if "## Internal" in text or "_ holds " in text:
            return [f"Module '{node.name}' mixes internal design into the public seam."]
        return []


def _module_source_text(context, node) -> str:
    if context.source_root is None:
        return ""
    folder = context.module_folder(node)
    if folder is None or not folder.is_dir():
        return ""
    chunks: list[str] = []
    for path in sorted(folder.glob("*.py")):
        if path.name.startswith("_"):
            continue
        try:
            chunks.append(path.read_text(encoding="utf-8"))
        except OSError:
            continue
    return "\n".join(chunks)


def _class_py_path(context, node) -> Path | None:
    if context.source_root is None or not node.source.file:
        return None
    path = context.source_root / node.source.file
    return path if path.suffix.lower() == ".py" and path.is_file() else None


def _context_row(node, context) -> dict:
    path = _class_py_path(context, node)
    return {"name": node.name, "message": str(path) if path else "", "contributor": node.name}


class MissingModuleContext(PracticeGraphRule):
    slug = "missing-module-context"
    node_types = ("OoadClass",)

    def check(self, node, context) -> list[str]:
        if _class_py_path(context, node) is None:
            return []
        hits = ModuleContextFiles().rows_for_missing_module_context([_context_row(node, context)])
        return [hit["message"] for hit in hits]


class LanguageModulesOneSection(PracticeGraphRule):
    slug = "language-modules-one-section"
    node_types = ("OoadClass",)

    def check(self, node, context) -> list[str]:
        if _class_py_path(context, node) is None:
            return []
        hits = ModuleContextFiles().rows_for_language_modules_one_section([_context_row(node, context)])
        return [hit["message"] for hit in hits]


class ModulesNotModelBlocks(PracticeGraphRule):
    slug = "modules-not-model-blocks"
    node_types = ("OoadClass",)

    def check(self, node, context) -> list[str]:
        if _class_py_path(context, node) is None:
            return []
        hits = ModuleContextFiles().rows_for_modules_not_model_blocks([_context_row(node, context)])
        return [hit["message"] for hit in hits]
