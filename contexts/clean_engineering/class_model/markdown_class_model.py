"""Markdown channel for the CleanEngineering model.

Format (language companion + modules/model markdown, module-first):

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

_repo = Path(__file__).resolve().parents[3]
if str(_repo) not in sys.path:
    sys.path.insert(0, str(_repo))

from contexts.clean_engineering.class_model.base_class_model import OoadNode
from contexts.clean_engineering.class_model.base_class_model import (
    CleanEngineeringModel,
    Module,
    OoadClass,
    Operation,
    Property,
    Relationship,
    companion_interface_name,
    is_interface_name,
)
from contexts.clean_engineering.class_model.update_report import ChildCollectionPair, UpdateReport


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
                purpose, seam_terms, deps, leftover = _parse_module_meta(pre_h2)
                if purpose:
                    module.description = purpose
                elif leftover:
                    module.description = leftover
                else:
                    module.description = pre_h2
                module.seam_terms = seam_terms
                module.dependencies = deps
                if seam_terms and not module.seam:
                    module.seam = ", ".join(seam_terms)

            # Parse classes from `##` sub-sections (skip modules-fidelity meta headings)
            class_order = 1
            for class_block in re.split(r"(?m)^(?=##\s)", classes_text):
                class_block = class_block.strip()
                if not class_block:
                    continue
                cm = re.match(r"^##\s+(.+)", class_block)
                if not cm:
                    continue
                class_name = cm.group(1).strip()
                if class_name.lower() in _MODULE_META_HEADINGS:
                    _apply_module_section(module, class_name, class_block[cm.end():])
                    continue
                # "## FakeCart : ICart" / "## Cart : ICart" → class name only
                if " : " in class_name:
                    class_name = class_name.split(" : ", 1)[0].strip()
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
            if "contexts.clean_engineering.clean_engineering:CleanEngineering" in text and "@toolset-manifest" in text:
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
    terms = module.public_terms()
    # Modules-fidelity structured fields when present (and no typed class bodies yet)
    modules_only = bool(module.dependencies or module.seam_terms) and not any(
        c.properties or c.operations for c in module.classes
    )
    if modules_only or (terms and not module.classes):
        if module.description:
            lines.append(f"- **Purpose:** {module.description.splitlines()[0].strip()}")
        if terms:
            lines.append(f"- **Seam (terms):** {', '.join(terms)}")
        if module.dependencies:
            lines.append(
                f"- **Dependencies (one-way):** {', '.join(module.dependencies)}"
            )
        elif modules_only:
            lines.append("- **Dependencies (one-way):** *(none)*")
        lines.append("")
    known = [c.name for c in module.classes]
    for oclass in module.classes:
        lines.append(_render_class(oclass, known_names=known))
    return "\n".join(lines)


_MODULE_META_HEADINGS = frozenset({
    "seam",
    "dependencies",
    "modules fidelity",
    "purpose",
})


def _parse_term_list(raw: str) -> List[str]:
    text = raw.strip()
    text = re.sub(r"^\*\(?none\)?\*$", "", text, flags=re.IGNORECASE).strip()
    if not text or text.lower() in {"*(none)*", "(none)", "none", "—", "-"}:
        return []
    # Strip surrounding backticks per token
    parts = re.split(r"[,;]", text)
    out: List[str] = []
    for p in parts:
        term = p.strip().strip("`").strip()
        term = re.sub(r"^\*\*?|\*\*?$", "", term).strip()
        if term:
            out.append(term)
    return out


def _parse_module_meta(text: str) -> tuple[str, List[str], List[str], str]:
    """Parse Purpose / Seam / Dependencies bullets from a modules-fidelity block.

    Returns (purpose, seam_terms, dependencies, leftover_prose).
    """
    purpose = ""
    seam_terms: List[str] = []
    deps: List[str] = []
    leftover_lines: List[str] = []

    for line in text.splitlines():
        stripped = line.strip()
        m_purpose = re.match(r"^-?\s*\*\*Purpose:\*\*\s*(.+)$", stripped, re.IGNORECASE)
        m_seam = re.match(
            r"^-?\s*\*\*Seam(?:\s*\(terms\))?:\*\*\s*(.+)$", stripped, re.IGNORECASE
        )
        m_deps = re.match(
            r"^-?\s*\*\*Dependencies(?:\s*\(one-way\))?:\*\*\s*(.+)$",
            stripped,
            re.IGNORECASE,
        )
        m_build = re.match(r"^-?\s*\*\*Build order:\*\*", stripped, re.IGNORECASE)
        if m_purpose:
            purpose = m_purpose.group(1).strip()
        elif m_seam:
            seam_terms = _parse_term_list(m_seam.group(1))
        elif m_deps:
            deps = _parse_term_list(m_deps.group(1))
        elif m_build:
            continue
        elif re.match(r"^###\s+Module\s+", stripped, re.IGNORECASE):
            continue
        elif re.match(r"^##\s+Modules fidelity", stripped, re.IGNORECASE):
            continue
        else:
            leftover_lines.append(line)

    leftover = "\n".join(leftover_lines).strip()
    # Nested "### Module `path`" blocks often put purpose only in the bullet
    if not purpose and leftover:
        # Keep leftover as description when it is prose (not only bullets we already ate)
        prose = "\n".join(
            ln for ln in leftover.splitlines()
            if ln.strip() and not ln.strip().startswith("- **")
        ).strip()
        if prose:
            purpose = prose.splitlines()[0].strip() if not purpose else purpose
    return purpose, seam_terms, deps, leftover


def _apply_module_section(module: Module, heading: str, body: str) -> None:
    key = heading.lower().strip()
    if key == "modules fidelity":
        purpose, seam_terms, deps, _leftover = _parse_module_meta(body)
        if purpose and not module.description:
            module.description = purpose
        if seam_terms:
            module.seam_terms = seam_terms
            if not module.seam:
                module.seam = ", ".join(seam_terms)
        if deps:
            module.dependencies = deps
        return
    if key == "seam":
        # Narrative seam section — keep as seam prose; pull backticked names as terms
        module.seam = body.strip()
        if not module.seam_terms:
            module.seam_terms = [
                t for t in re.findall(r"`([^`]+)`", body)
                if t.strip() and "." not in t  # skip Check.resolve style
            ]
    elif key == "dependencies":
        # Prefer a "**Formal (modules):** a, b" line; else comma list on first line
        formal = re.search(
            r"\*\*Formal\s*\(modules\):\*\*\s*(.+)", body, re.IGNORECASE
        )
        if formal:
            module.dependencies = _parse_term_list(formal.group(1))
        else:
            first = next((ln.strip() for ln in body.splitlines() if ln.strip()), "")
            module.dependencies = _parse_term_list(first)
    elif key == "purpose":
        module.description = body.strip()


def _render_class(oclass: OoadClass, known_names: List[str] | None = None) -> str:
    known_names = known_names or []
    heading = oclass.name
    iface = companion_interface_name(oclass.name, known_names)
    if iface:
        heading = f"{oclass.name} : {iface}"
    elif is_interface_name(oclass.name):
        heading = oclass.name
    lines: List[str] = [f"## {heading}", ""]
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
            if is_interface_name(oclass.name) and op.name.startswith("_"):
                continue
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
