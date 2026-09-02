"""Miro diagram channel for the CleanEngineering model.

Two visual fidelities share this channel (auto-detected on render/parse):

**Modules view** (modules fidelity):
  - Each Module is one Mermaid flowchart node labelled with name, purpose,
    and seam terms.
  - Path nesting (``powers/attack`` inside ``powers``) is modelled as a
    Mermaid ``subgraph`` — mirroring DrawIO's containment parent attribute.
  - Dependency edges are directed arrows (A --> B means A depends on B).
  - Child->path-parent edges are omitted (containment already expresses that).

**Class view** (model+ fidelity):
  - Each OoadClass becomes a Mermaid ``classDiagram`` class block with
    properties and operations.
  - Relationships as Mermaid arrows keyed by ``kind``.

render() returns a canvas-composer SVG (foreignObject data-type="diagram" with
Mermaid body) that can be posted to a Miro board via canvas_create_from_svg.
parse() extracts the Mermaid source from the SVG and reconstructs the model.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Tuple

from context_tools.clean_engineering.class_model.base_class_model import (
    CleanEngineeringModel,
    Module,
    OoadClass,
    Operation,
    Property,
    Relationship,
)
from context_tools.clean_engineering.class_model.update_report import UpdateReport


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _module_id(name: str) -> str:
    """Convert a module path name to a Mermaid-safe node identifier."""
    return re.sub(r"[^a-zA-Z0-9]", "_", name)


def _path_parent(name: str) -> Optional[str]:
    """Return the parent path prefix, or None for top-level names."""
    idx = name.rfind("/")
    return name[:idx] if idx != -1 else None


def _is_modules_view(canonical: CleanEngineeringModel) -> bool:
    """True when the model is module-boundary detail only (no typed class members).

    Mirrors DrawIOCleanEngineeringModel._is_modules_view exactly.
    """
    if not canonical.modules:
        return False
    for oclass in canonical.classes:
        if oclass.properties or oclass.operations:
            return False
        if any(r.kind for r in oclass.relationships):
            return False
    if any(m.dependencies or m.seam_terms for m in canonical.modules):
        return True
    return False


def _is_mermaid_modules(source: str) -> bool:
    """True when the Mermaid source begins with a flowchart header."""
    stripped = source.strip()
    return stripped.startswith("flowchart") or stripped.startswith("graph")


# ---------------------------------------------------------------------------
# Channel node types (same factory-chain pattern as DrawIO)
# ---------------------------------------------------------------------------

class MiroOoadClass(OoadClass):
    pass


class MiroModule(Module):
    def create_child_class(self, source: OoadClass) -> MiroOoadClass:
        return MiroOoadClass(name=source.name, sequential_order=source.sequential_order)


class MiroCleanEngineeringModel(CleanEngineeringModel):

    def create_child_module(self, source: Module) -> MiroModule:
        return MiroModule(name=source.name, sequential_order=source.sequential_order)

    def create_child_class(self, source: OoadClass) -> MiroOoadClass:
        return MiroOoadClass(name=source.name, sequential_order=source.sequential_order)

    # ------------------------------------------------------------------
    # Uniform callable surface
    # ------------------------------------------------------------------

    @classmethod
    def render(
        cls,
        canonical: CleanEngineeringModel,
        previous: Optional[str] = None,
        keep_positioning: bool = False,
    ) -> str:
        if _is_modules_view(canonical):
            return cls._render_modules(canonical)
        return cls._render_classes(canonical)

    @classmethod
    def parse(cls, text: str) -> "MiroCleanEngineeringModel":
        """Parse a canvas-composer SVG back into a MiroCleanEngineeringModel.

        Extracts the Mermaid source from the foreignObject body and delegates
        to _parse_modules or _parse_classes based on the diagram header.
        """
        mermaid_src = cls._extract_mermaid(text)
        if mermaid_src is None:
            return cls(name="", sequential_order=1)
        if _is_mermaid_modules(mermaid_src):
            return cls._parse_modules(mermaid_src)
        return cls._parse_classes(mermaid_src)

    @classmethod
    def sync(
        cls,
        text: str,
        canonical: "MiroCleanEngineeringModel",
    ) -> UpdateReport:
        return canonical.translate_from(cls.parse(text))

    # ------------------------------------------------------------------
    # Modules view
    # ------------------------------------------------------------------

    @classmethod
    def _render_modules(cls, canonical: CleanEngineeringModel) -> str:
        """Generate a Mermaid flowchart for the module dependency graph."""
        system_name = canonical.name or "System"
        modules = canonical.modules

        # Build containment map: child_name → parent_name (only when parent is in model)
        known_names = {m.name for m in modules}
        child_of: Dict[str, str] = {}
        for m in modules:
            p = _path_parent(m.name)
            if p and p in known_names:
                child_of[m.name] = p

        # Group children by parent
        children_of: Dict[str, List[Module]] = {m.name: [] for m in modules}
        roots: List[Module] = []
        for m in modules:
            if m.name in child_of:
                parent_name = child_of[m.name]
                children_of[parent_name].append(m)
            else:
                roots.append(m)

        lines: List[str] = ["flowchart LR"]

        # Render roots: those with children become subgraphs
        for m in modules:
            if m.name in child_of:
                continue  # rendered inside parent's subgraph
            if children_of[m.name]:
                # Has nested children — render as subgraph
                lines.append(
                    f'    subgraph {_module_id(m.name)}'
                    f'["{cls._module_label(m)}"]'
                )
                for child in children_of[m.name]:
                    lines.append(
                        f'        {_module_id(child.name)}'
                        f'["{cls._module_label(child)}"]'
                    )
                lines.append("    end")
            else:
                lines.append(
                    f'    {_module_id(m.name)}["{cls._module_label(m)}"]'
                )

        # Render dependency edges (skip child->path-parent; containment covers it)
        for m in modules:
            parent_name = child_of.get(m.name)
            for dep in m.dependencies:
                if dep == parent_name:
                    continue  # containment — no edge needed
                dep_id = _module_id(dep)
                lines.append(f"    {_module_id(m.name)} --> {dep_id}")

        mermaid = "\n".join(lines)
        title = f"{system_name} - Modules"
        return cls._wrap_diagram(mermaid, title)

    @classmethod
    def _module_label(cls, m: Module) -> str:
        """Build the multi-line Mermaid label for a module node."""
        parts = [m.name]
        if m.description:
            # Truncate long descriptions
            desc = m.description[:90] if len(m.description) > 90 else m.description
            parts.append(desc)
        if m.seam_terms:
            parts.append("---")
            for term in m.seam_terms:
                parts.append(f"\u2022 {term}")
        return "\\n".join(parts)

    @classmethod
    def _parse_modules(cls, mermaid_src: str) -> "MiroCleanEngineeringModel":
        """Parse a Mermaid flowchart back into a module model."""
        model = cls(name="", sequential_order=1)
        order = 1

        # Extract system name from title comment if present (e.g. %% System - Modules)
        title_m = re.search(r"%%\s*(.+?)\s*-\s*Modules?", mermaid_src)
        if title_m:
            model.name = title_m.group(1).strip()

        # Parse subgraph declarations to find nesting
        # subgraph id["label"] ... end
        subgraph_re = re.compile(
            r"subgraph\s+(\w+)\[\"([^\"]+)\"\]", re.MULTILINE
        )
        node_re = re.compile(
            r"^\s{0,8}(\w+)\[\"([^\"]+)\"\]", re.MULTILINE
        )
        edge_re = re.compile(
            r"(\w+)\s*-->\s*(\w+)", re.MULTILINE
        )

        id_to_module: Dict[str, MiroModule] = {}

        def _parse_label(raw_label: str) -> Tuple[str, str, List[str]]:
            """Decode \\n-separated label into (name, purpose, seam_terms)."""
            parts = raw_label.replace("\\n", "\n").split("\n")
            name = parts[0].strip()
            purpose = ""
            terms: List[str] = []
            in_terms = False
            for part in parts[1:]:
                p = part.strip()
                if p == "---":
                    in_terms = True
                    continue
                if in_terms and p.startswith("\u2022 "):
                    terms.append(p[2:].strip())
                elif not in_terms and p:
                    purpose = p
            return name, purpose, terms

        # Collect all nodes (both subgraph headers and plain nodes)
        seen_ids: set = set()
        for m in subgraph_re.finditer(mermaid_src):
            mid, label = m.group(1), m.group(2)
            if mid in seen_ids:
                continue
            seen_ids.add(mid)
            name, purpose, terms = _parse_label(label)
            if not name:
                continue
            module = MiroModule(
                name=name, sequential_order=order,
                description=purpose, seam_terms=terms,
            )
            model.modules.append(module)
            id_to_module[mid] = module
            order += 1

        for m in node_re.finditer(mermaid_src):
            mid, label = m.group(1), m.group(2)
            if mid in seen_ids or mid in ("LR", "TD", "RL", "BT"):
                continue
            seen_ids.add(mid)
            name, purpose, terms = _parse_label(label)
            if not name:
                continue
            module = MiroModule(
                name=name, sequential_order=order,
                description=purpose, seam_terms=terms,
            )
            model.modules.append(module)
            id_to_module[mid] = module
            order += 1

        # Parse dependency edges
        for m in edge_re.finditer(mermaid_src):
            src_id, tgt_id = m.group(1), m.group(2)
            src_mod = id_to_module.get(src_id)
            tgt_mod = id_to_module.get(tgt_id)
            if src_mod is None or tgt_mod is None:
                continue
            if tgt_mod.name not in src_mod.dependencies:
                src_mod.dependencies.append(tgt_mod.name)

        return model

    # ------------------------------------------------------------------
    # Class view
    # ------------------------------------------------------------------

    _REL_ARROWS = {
        "inheritance": "<|--",
        "composition": "*--",
        "aggregation": "o--",
        "association": "-->",
    }
    _ARROW_TO_KIND = {v: k for k, v in _REL_ARROWS.items()}

    @classmethod
    def _render_classes(cls, canonical: CleanEngineeringModel) -> str:
        """Generate a Mermaid classDiagram for the model."""
        lines: List[str] = ["classDiagram"]

        all_classes: List[OoadClass] = list(canonical.classes)
        for m in canonical.modules:
            for c in m.classes:
                if c not in all_classes:
                    all_classes.append(c)

        for oclass in all_classes:
            lines.append(f"    class {oclass.name} {{")
            for prop in oclass.properties:
                type_hint = prop.type_hint or "object"
                lines.append(f"        +{type_hint} {prop.name}")
            for op in oclass.operations:
                ret = op.return_type or "void"
                lines.append(f"        +{op.name}() {ret}")
            lines.append("    }")

        for oclass in all_classes:
            for rel in oclass.relationships:
                arrow = cls._REL_ARROWS.get(rel.kind or "association", "-->")
                lines.append(
                    f"    {oclass.name} {arrow} {rel.target} : {rel.kind or 'association'}"
                )

        mermaid = "\n".join(lines)
        system_name = canonical.name or "System"
        title = f"{system_name} - Class Diagram"
        return cls._wrap_diagram(mermaid, title)

    @classmethod
    def _parse_classes(cls, mermaid_src: str) -> "MiroCleanEngineeringModel":
        """Parse a Mermaid classDiagram back into a class model."""
        model = cls(name="", sequential_order=1)
        module = MiroModule(name="", sequential_order=1)
        model.modules.append(module)
        order = 1
        id_to_class: Dict[str, MiroOoadClass] = {}

        # Parse class blocks
        class_block_re = re.compile(
            r"class\s+(\w+)\s*\{([^}]*)\}", re.MULTILINE | re.DOTALL
        )
        prop_re = re.compile(r"\+(\S+)\s+(\w+)\s*$")
        op_re = re.compile(r"\+(\w+)\(\)\s+(\S+)\s*$")

        for m in class_block_re.finditer(mermaid_src):
            name = m.group(1)
            body = m.group(2)
            props: List[Property] = []
            ops: List[Operation] = []
            for line in body.splitlines():
                line = line.strip()
                if not line:
                    continue
                op_m = op_re.match(line)
                if op_m:
                    ops.append(Operation(name=op_m.group(1), return_type=op_m.group(2)))
                    continue
                prop_m = prop_re.match(line)
                if prop_m:
                    props.append(Property(name=prop_m.group(2), type_hint=prop_m.group(1)))
            oclass = MiroOoadClass(
                name=name, sequential_order=order,
                properties=props, operations=ops,
            )
            module.classes.append(oclass)
            id_to_class[name] = oclass
            order += 1

        # Parse relationships
        rel_re = re.compile(
            r"(\w+)\s+(<\|--|o--|[*]--|-->|<\.\.|\.\.[>|])\s+(\w+)"
        )
        for m in rel_re.finditer(mermaid_src):
            src_name, arrow, tgt_name = m.group(1), m.group(2), m.group(3)
            src_cls = id_to_class.get(src_name)
            if src_cls is None:
                continue
            kind = cls._ARROW_TO_KIND.get(arrow, "association")
            already = any(
                r.target == tgt_name for r in src_cls.relationships
            )
            if not already:
                src_cls.relationships.append(Relationship(target=tgt_name, kind=kind))

        return model

    # ------------------------------------------------------------------
    # SVG wrapping
    # ------------------------------------------------------------------

    @classmethod
    def _wrap_diagram(cls, mermaid: str, title: str) -> str:
        """Wrap Mermaid source in a canvas-composer SVG foreignObject."""
        escaped = (
            mermaid
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
        return (
            "<?xml version='1.0' encoding='utf-8'?>\n"
            '<svg xmlns="http://www.w3.org/2000/svg">\n'
            f'  <foreignObject id="CleanEngineering-model" x="0" y="0" '
            f'width="1600" height="900" data-type="diagram" '
            f'data-title="{title}">'
            f"{escaped}"
            f"</foreignObject>\n"
            "</svg>"
        )

    @classmethod
    def _extract_mermaid(cls, text: str) -> Optional[str]:
        """Extract Mermaid source from a canvas-composer SVG string."""
        try:
            root_el = ET.fromstring(
                text.split("\n", 1)[1] if text.startswith("<?") else text
            )
        except ET.ParseError:
            return None

        for el in root_el.iter():
            tag = el.tag.split("}")[-1] if "}" in el.tag else el.tag
            if tag == "foreignObject" and el.get("data-type") == "diagram":
                return (el.text or "").strip()
        return None
