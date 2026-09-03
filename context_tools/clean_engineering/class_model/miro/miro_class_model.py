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
from html import escape
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


def _plain_class_name(name: str) -> str:
    """Return the Mermaid identifier portion of a decorated OOAD class name."""
    plain = re.sub(r"\*+", "", name)
    plain = re.sub(r"<<[^>]+>>", "", plain)
    plain = re.sub(r"\s+extends\s+.+$", "", plain, flags=re.IGNORECASE)
    return plain.strip()


def _class_id(name: str) -> str:
    """Return a stable Mermaid-safe identifier for a class name."""
    identifier = re.sub(r"\W+", "_", _plain_class_name(name)).strip("_")
    if identifier and identifier[0].isdigit():
        identifier = f"class_{identifier}"
    return identifier or "UnnamedClass"


def _class_stereotypes(name: str) -> List[str]:
    return [stereotype.strip() for stereotype in re.findall(r"<<([^>]+)>>", name)]


def _extends_base_name(name: str) -> Optional[str]:
    undecorated = re.sub(r"\*+|<<[^>]+>>", "", name)
    match = re.search(r"\bextends\s+([A-Za-z_]\w*)", undecorated, re.IGNORECASE)
    return match.group(1) if match else None


def _module_label(name: str) -> str:
    for separator in (" — ", " – ", " - ", "—", "–"):
        if separator in name:
            return name.split(separator, 1)[0].strip()
    return name.strip()


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
        diagrams = cls._extract_diagrams(text)
        if not diagrams:
            return cls(name="", sequential_order=1)
        mermaid_src = diagrams[0][1]
        if _is_mermaid_modules(mermaid_src):
            return cls._parse_modules(mermaid_src)

        model = cls(name=diagrams[0][0].get("data-system", ""), sequential_order=1)
        for element, source in diagrams:
            parsed = cls._parse_classes(
                source,
                module_name=element.get("data-module", ""),
            )
            model.modules.extend(parsed.modules)
        return model

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
        """Generate one Mermaid class diagram widget per canonical module."""
        modules = [module for module in canonical.modules if module.classes]
        if not modules:
            return cls._wrap_diagram(
                "classDiagram", f"{canonical.name or 'System'} - Class Diagram"
            )

        all_classes = list(canonical.classes)
        class_by_id = {_class_id(oclass.name): oclass for oclass in all_classes}
        module_by_id = {
            _class_id(oclass.name): module.name
            for module in modules
            for oclass in module.classes
        }
        relationships = cls._class_relationships(all_classes, class_by_id)

        diagrams: List[Tuple[str, str]] = []
        for module in modules:
            local_ids = [_class_id(oclass.name) for oclass in module.classes]
            local_set = set(local_ids)
            import_ids: set[str] = set()
            for source_id, target_id, kind in relationships:
                if source_id in local_set and target_id not in local_set:
                    import_ids.add(target_id)
                elif (
                    kind == "inheritance"
                    and target_id in local_set
                    and source_id not in local_set
                ):
                    import_ids.add(source_id)

            visible_ids = local_set | import_ids
            lines: List[str] = ["classDiagram"]
            for class_id in local_ids + sorted(import_ids):
                oclass = class_by_id[class_id]
                imported = class_id in import_ids
                marker = "imported" if imported else "local"
                lines.append(f"    %% {marker}: {class_id}")
                lines.append(f"    class {class_id} {{")
                if imported:
                    source_module = _module_label(module_by_id.get(class_id, "other"))
                    lines.append(f"        <<from {source_module}>>")
                for stereotype in _class_stereotypes(oclass.name):
                    lines.append(f"        <<{stereotype}>>")
                properties = oclass.properties[:4] if imported else oclass.properties
                for prop in properties:
                    lines.append(f"        +{prop.type_hint or 'object'} {prop.name}")
                if not imported:
                    for operation in oclass.operations:
                        parameters = ", ".join(operation.parameters)
                        lines.append(
                            f"        +{operation.name}({parameters}) "
                            f"{operation.return_type or 'void'}"
                        )
                lines.append("    }")

            for source_id, target_id, kind in relationships:
                if source_id not in visible_ids or target_id not in visible_ids:
                    continue
                arrow = cls._REL_ARROWS.get(kind, "-->")
                if kind == "inheritance":
                    lines.append(f"    {target_id} {arrow} {source_id}")
                else:
                    lines.append(f"    {source_id} {arrow} {target_id} : {kind}")

            diagrams.append((module.name, "\n".join(lines)))

        return cls._wrap_class_diagrams(diagrams, canonical.name or "System")

    @classmethod
    def _class_relationships(
        cls,
        classes: List[OoadClass],
        class_by_id: Dict[str, OoadClass],
    ) -> List[Tuple[str, str, str]]:
        relationships: List[Tuple[str, str, str]] = []
        aliases = {
            alias: class_id
            for class_id, oclass in class_by_id.items()
            for alias in (oclass.name, _plain_class_name(oclass.name))
        }
        for oclass in classes:
            source_id = _class_id(oclass.name)
            for relationship in oclass.relationships:
                target_id = aliases.get(relationship.target)
                if target_id is None:
                    continue
                item = (source_id, target_id, relationship.kind or "association")
                if item not in relationships:
                    relationships.append(item)
            base_name = _extends_base_name(oclass.name)
            target_id = aliases.get(base_name or "")
            item = (source_id, target_id or "", "inheritance")
            if target_id and item not in relationships:
                relationships.append(item)
        return relationships

    @classmethod
    def _parse_classes(
        cls,
        mermaid_src: str,
        module_name: str = "",
    ) -> "MiroCleanEngineeringModel":
        """Parse a Mermaid classDiagram back into a class model."""
        model = cls(name="", sequential_order=1)
        module = MiroModule(name=module_name, sequential_order=1)
        model.modules.append(module)
        order = 1
        id_to_class: Dict[str, MiroOoadClass] = {}

        # Parse class blocks
        class_block_re = re.compile(
            r"class\s+(\w+)\s*\{([^}]*)\}", re.MULTILINE | re.DOTALL
        )
        prop_re = re.compile(r"\+(.+?)\s+(\w+)\s*$")
        op_re = re.compile(r"\+(\w+)\((.*)\)\s+(.+?)\s*$")
        local_names = set(
            re.findall(r"^\s*%%\s+local:\s+(\w+)\s*$", mermaid_src, re.MULTILINE)
        )

        for m in class_block_re.finditer(mermaid_src):
            name = m.group(1)
            if local_names and name not in local_names:
                continue
            body = m.group(2)
            props: List[Property] = []
            ops: List[Operation] = []
            for line in body.splitlines():
                line = line.strip()
                if not line:
                    continue
                op_m = op_re.match(line)
                if op_m:
                    parameters = [
                        parameter.strip()
                        for parameter in op_m.group(2).split(",")
                        if parameter.strip()
                    ]
                    ops.append(
                        Operation(
                            name=op_m.group(1),
                            parameters=parameters,
                            return_type=op_m.group(3),
                        )
                    )
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
            if arrow == "<|--":
                src_name, tgt_name = tgt_name, src_name
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
    def _wrap_class_diagrams(
        cls,
        diagrams: List[Tuple[str, str]],
        system_name: str,
    ) -> str:
        elements: List[str] = []
        for index, (module_name, mermaid) in enumerate(diagrams):
            escaped_mermaid = escape(mermaid, quote=False)
            escaped_module = escape(module_name, quote=True)
            escaped_system = escape(system_name, quote=True)
            # Miro reports the requested foreignObject bounds, not the UML content's
            # rendered bounds. Leave enough horizontal room for that overflow while
            # keeping related module diagrams together in one readable row.
            x = 1000 + (index * 3500)
            y = 2000
            element_id = f"CleanEngineering-{_module_id(module_name)}"
            title = escape(f"{module_name} - Class Diagram", quote=True)
            elements.append(
                f'  <foreignObject id="{element_id}" x="{x}" y="{y}" '
                f'width="1600" height="900" data-type="diagram" '
                f'data-title="{title}" data-module="{escaped_module}" '
                f'data-system="{escaped_system}">{escaped_mermaid}</foreignObject>'
            )
        return (
            "<?xml version='1.0' encoding='utf-8'?>\n"
            '<svg xmlns="http://www.w3.org/2000/svg">\n'
            + "\n".join(elements)
            + "\n</svg>"
        )

    @classmethod
    def _extract_mermaid(cls, text: str) -> Optional[str]:
        """Extract Mermaid source from a canvas-composer SVG string."""
        diagrams = cls._extract_diagrams(text)
        return diagrams[0][1] if diagrams else None

    @classmethod
    def _extract_diagrams(cls, text: str) -> List[Tuple[ET.Element, str]]:
        """Extract every Mermaid diagram widget from a canvas-composer SVG."""
        try:
            root_el = ET.fromstring(
                text.split("\n", 1)[1] if text.startswith("<?") else text
            )
        except ET.ParseError:
            return []

        diagrams: List[Tuple[ET.Element, str]] = []
        for el in root_el.iter():
            tag = el.tag.split("}")[-1] if "}" in el.tag else el.tag
            if tag == "foreignObject" and el.get("data-type") == "diagram":
                diagrams.append((el, (el.text or "").strip()))
        return diagrams
