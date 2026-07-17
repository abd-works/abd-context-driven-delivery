"""Markdown channel for the CleanEngineering model.

Format (language fidelity, module-first):

    # ModuleName

    *ModuleName* is [description — what it is, its boundary, collaborators, seam, constraint].

    ## ClassName

    *ClassName* is [intent]

    - [bullet about the class]
    - **Invariant:** [rule]

Top-level `#` headings are modules; `##` headings are classes within a module.
When the text contains only `#` headings (no `##`), each `#` is treated as a
module with no named classes (description-only, e.g. a language-fidelity narrative).

Section separators (model / specification fidelity inside a `##` class block):
    ------  (6 dashes)  constructor / properties boundary
    ----    (4 dashes)  properties / operations boundary
    -       (prefix)    private operation
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import List, Optional

_repo = Path(__file__).resolve().parents[2]
if str(_repo) not in sys.path:
    sys.path.insert(0, str(_repo))

from clean_engineering.class_model.base_class_model import OoadNode
from clean_engineering.class_model.base_class_model import (
    CleanEngineeringModel,
    Module,
    OoadClass,
    Operation,
    Property,
    Relationship,
)
from clean_engineering.class_model.update_report import ChildCollectionPair, UpdateReport


class MarkdownOoadClass(OoadClass):
    pass


class MarkdownModule(Module):
    def create_child_class(self, source: OoadClass) -> MarkdownOoadClass:
        return MarkdownOoadClass(name=source.name, sequential_order=source.sequential_order)


class MarkdownCleanEngineeringModel(CleanEngineeringModel):

    def create_child_module(self, source: Module) -> MarkdownModule:
        return MarkdownModule(name=source.name, sequential_order=source.sequential_order)

    # ------------------------------------------------------------------
    # Uniform callable surface
    # ------------------------------------------------------------------

    @classmethod
    def parse(cls, text: str) -> "MarkdownCleanEngineeringModel":
        model = cls(name="", sequential_order=1)
        module_order = 1

        # Split on H1 (`# Heading`) — each block is one module
        h1_blocks = re.split(r"(?m)^(?=#\s)", text)
        for block in h1_blocks:
            block = block.strip()
            if not block:
                continue
            m = re.match(r"^#\s+(.+)", block)
            if not m:
                continue
            module_name = m.group(1).strip()
            body_after_h1 = block[m.end():].lstrip("\n")

            module = MarkdownModule(name=module_name, sequential_order=module_order)
            module_order += 1

            # Description: everything before the first `##` heading
            h2_split = re.split(r"(?m)^(?=##\s)", body_after_h1, maxsplit=1)
            pre_h2 = h2_split[0].strip()
            classes_text = h2_split[1] if len(h2_split) > 1 else ""

            if pre_h2:
                module.description = pre_h2

            # Parse classes from `##` sub-sections
            class_order = 1
            for class_block in re.split(r"(?m)^(?=##\s)", classes_text):
                class_block = class_block.strip()
                if not class_block:
                    continue
                cm = re.match(r"^##\s+(.+)", class_block)
                if not cm:
                    continue
                class_name = cm.group(1).strip()
                class_body = class_block[cm.end():].lstrip("\n")
                oclass = _parse_class(class_name, class_body, class_order, MarkdownOoadClass)
                module.classes.append(oclass)
                class_order += 1

            model.modules.append(module)
        return model

    @classmethod
    def render(cls, canonical: CleanEngineeringModel, previous: Optional[str] = None) -> str:
        parts: List[str] = []
        for module in canonical.modules:
            parts.append(_render_module(module))
        return "\n".join(parts)

    @classmethod
    def sync(cls, text: str, canonical: CleanEngineeringModel) -> UpdateReport:
        return canonical.translate_from(cls.parse(text))

    @classmethod
    def from_workspace(cls, root: Path) -> Optional["MarkdownCleanEngineeringModel"]:
        for path in sorted(root.glob("**/*.md")):
            text = path.read_text(encoding="utf-8", errors="ignore")
            if "clean_engineering.clean_engineering:CleanEngineering" in text and "@toolset-manifest" in text:
                return cls.parse(text)
        return None


# ------------------------------------------------------------------
# Render helpers
# ------------------------------------------------------------------

def _render_module(module: Module) -> str:
    lines: List[str] = [f"# {module.name}", ""]
    if module.description:
        lines.append(module.description)
        lines.append("")
    for oclass in module.classes:
        lines.append(_render_class(oclass))
    return "\n".join(lines)


def _render_class(oclass: OoadClass) -> str:
    lines: List[str] = [f"## {oclass.name}", ""]
    if oclass.intent:
        lines.append(oclass.intent)
        lines.append("")
    params = ", ".join(
        f"{p.name}: {p.type_hint}" if p.type_hint else p.name
        for p in oclass.properties
    )
    if oclass.properties or oclass.operations:
        lines.append(f"{oclass.name}({params})")
        lines.append("------")
        for prop in oclass.properties:
            lines.append(f"{prop.name}: {prop.type_hint}" if prop.type_hint else prop.name)
        lines.append("----")
        for op in oclass.operations:
            op_params = ", ".join(op.parameters)
            ret = f": {op.return_type}" if op.return_type else ""
            prefix = "- " if op.name.startswith("_") else ""
            lines.append(f"{prefix}{op.name}({op_params}){ret}")
    lines.append("")
    return "\n".join(lines)


# ------------------------------------------------------------------
# Parse helpers
# ------------------------------------------------------------------

def _parse_class(name: str, body: str, order: int, cls: type) -> OoadClass:
    parts6 = re.split(r"(?m)^-{6}\s*$", body, maxsplit=1)
    pre6 = parts6[0] if parts6 else ""
    post6 = parts6[1] if len(parts6) > 1 else ""

    intent = ""
    for line in pre6.splitlines():
        stripped = line.strip()
        if stripped and not re.match(r"^\w[\w\s]*\(", stripped):
            intent = stripped
            break

    parts4 = re.split(r"(?m)^-{4}\s*$", post6, maxsplit=1)
    props_text = parts4[0] if parts4 else ""
    ops_text = parts4[1] if len(parts4) > 1 else ""

    return cls(
        name=name,
        sequential_order=order,
        intent=intent,
        properties=_parse_properties(props_text),
        operations=_parse_operations(ops_text),
    )


def _parse_properties(text: str) -> List[Property]:
    props = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("-{"):
            continue
        m = re.match(r"^(\w+):\s*(.+)", stripped)
        if m:
            props.append(Property(name=m.group(1), type_hint=m.group(2).strip()))
        elif re.match(r"^\w+$", stripped):
            props.append(Property(name=stripped))
    return props


def _parse_operations(text: str) -> List[Operation]:
    ops = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        private = stripped.startswith("- ")
        body = stripped[2:].strip() if private else stripped
        m = re.match(r"^(_?\w+)\(([^)]*)\)(?::\s*(.+))?", body)
        if m:
            op_name = ("_" if private and not m.group(1).startswith("_") else "") + m.group(1)
            params = [p.strip() for p in m.group(2).split(",") if p.strip()]
            ret = (m.group(3) or "").strip()
            ops.append(Operation(name=op_name, parameters=params, return_type=ret))
    return ops
