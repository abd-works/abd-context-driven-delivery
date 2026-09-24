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

from practices.clean_engineering.model.base_class_model import (
    CleanEngineeringModel,
    Module,
    OoadClass,
    Operation,
    Property,
    Relationship,
)
from practices.clean_engineering.model.diagram.diagram_node import (
    ContainmentForest,
    is_modules_view,
    module_tab_label,
    path_parent,
)
from practices.clean_engineering.model.diagram.geometry import Geometry
from practices.clean_engineering.model.miro.diagram_node import (
    MiroClass,
    MiroImportedClass,
    MiroModule,
    Page,
)
from practices.clean_engineering.model.update_report import UpdateReport

class MiroCleanEngineeringModel(CleanEngineeringModel):

    def load_module(self, source: Module) -> MiroModule:
        loaded = MiroModule(name=source.name, sequential_order=source.sequential_order)
        loaded.update_self(source)
        loaded.classes = list(source.classes)
        return loaded

    def load_class(self, source: OoadClass) -> MiroClass:
        loaded = MiroClass(name=source.name, sequential_order=source.sequential_order)
        loaded.update_self(source)
        return loaded

    def _imported_class(self, source: OoadClass, from_module: str = '') -> MiroImportedClass:
        loaded = MiroImportedClass(
            name=source.name,
            sequential_order=source.sequential_order,
            from_module=from_module,
        )
        loaded.update_self(source)
        return loaded

    def _is_modules_view(self, canonical: CleanEngineeringModel) -> bool:
        return is_modules_view(canonical)

    def _is_mermaid_modules(self, source: str) -> bool:
        stripped = source.strip()
        return stripped.startswith("flowchart") or stripped.startswith("graph")




    # ------------------------------------------------------------------
    # Uniform callable surface
    # ------------------------------------------------------------------

    def render(
        self,
        canonical: CleanEngineeringModel,
        previous: Optional[str] = None,
    ) -> str:
        if self._is_modules_view(canonical):
            return self._render_modules(canonical)
        return self._render_classes(canonical)

    def parse(self, text: str) -> "MiroCleanEngineeringModel":
        """Parse a canvas-composer SVG back into a MiroCleanEngineeringModel.

        Extracts the Mermaid source from the foreignObject body and delegates
        to _parse_modules or _parse_classes based on the diagram header.
        """
        diagrams = self._extract_diagrams(text)
        if not diagrams:
            return type(self)(name="", sequential_order=1)
        mermaid_src = diagrams[0][1]
        if self._is_mermaid_modules(mermaid_src):
            return self._parse_modules(mermaid_src)

        model = type(self)(name=diagrams[0][0].get("data-system", ""), sequential_order=1)
        for element, source in diagrams:
            parsed = self._parse_classes(
                source,
                module_name=element.get("data-module", ""),
            )
            model.modules.extend(parsed.modules)
        return model

    def sync(
        self,
        text: str,
        canonical: "MiroCleanEngineeringModel",
    ) -> UpdateReport:
        return canonical.translate_from(self.parse(text))

    # ------------------------------------------------------------------
    # Modules view
    # ------------------------------------------------------------------

    def _render_modules(self, canonical: CleanEngineeringModel) -> str:
        forest = ContainmentForest.build(canonical.modules, synthesize_parents=False)
        nodes = {m.name: self.load_module(m) for m in canonical.modules}
        lines: List[str] = ["flowchart LR"]
        for name in forest.roots:
            node = nodes[name]
            kids = [nodes[c] for c in forest.children_of.get(name, []) if c in nodes]
            if kids:
                lines.append(f'    subgraph {node.mermaid_id()}["{node.mermaid_label()}"]')
                for child in kids:
                    lines.append(f'        {child.mermaid_id()}["{child.mermaid_label()}"]')
                lines.append("    end")
            else:
                lines.append(f'    {node.mermaid_id()}["{node.mermaid_label()}"]')
        for name, node in nodes.items():
            parent = path_parent(name)
            for dep in node.external_deps():
                if dep == parent:
                    continue
                dep_node = nodes.get(dep)
                dep_id = dep_node.mermaid_id() if dep_node else MiroModule(name=dep, sequential_order=0).mermaid_id()
                lines.append(f"    {node.mermaid_id()} --> {dep_id}")
        title = f"{canonical.name or 'System'} - Modules"
        return self._wrap_diagram("\n".join(lines), title)

    def _parse_modules(self, mermaid_src: str) -> "MiroCleanEngineeringModel":
        """Parse a Mermaid flowchart back into a module model."""
        model = type(self)(name="", sequential_order=1)
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

    def _render_classes(self, canonical: CleanEngineeringModel) -> str:
        modules = [module for module in canonical.modules if module.classes]
        if not modules:
            return self._wrap_diagram(
                "classDiagram", f"{canonical.name or 'System'} - Class Diagram"
            )

        all_classes = list(canonical.classes)
        class_nodes = {self.load_class(oclass).mermaid_id(): self.load_class(oclass) for oclass in all_classes}
        class_by_id = {cid: node for cid, node in class_nodes.items()}
        module_by_id = {
            self.load_class(oclass).mermaid_id(): module.name
            for module in modules
            for oclass in module.classes
        }
        relationships = self._class_relationships(all_classes, class_by_id)

        page = Page(canonical.name or "System")
        for index, module in enumerate(modules):
            local_nodes = [self.load_class(oclass) for oclass in module.classes]
            local_ids = [node.mermaid_id() for node in local_nodes]
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
                oclass_node = class_by_id[class_id]
                if class_id in import_ids:
                    imported = self._imported_class(
                        oclass_node, module_tab_label(module_by_id.get(class_id, "other"))
                    )
                    lines.extend(imported.mermaid_lines())
                else:
                    lines.extend(oclass_node.mermaid_lines())

            for source_id, target_id, kind in relationships:
                if source_id not in visible_ids or target_id not in visible_ids:
                    continue
                arrow = self._REL_ARROWS.get(kind, "-->")
                if kind == "inheritance":
                    lines.append(f"    {target_id} {arrow} {source_id}")
                else:
                    lines.append(f"    {source_id} {arrow} {target_id} : {kind}")

            placed = self.load_module(module)
            placed.geometry = Geometry(1000 + index * 3500, 2000, 1600, 900)
            page.place(placed, "\n".join(lines))
        return page.svg()

    def _class_relationships(
        self,
        classes: List[OoadClass],
        class_by_id: Dict[str, MiroClass],
    ) -> List[Tuple[str, str, str]]:
        relationships: List[Tuple[str, str, str]] = []
        aliases = {
            alias: class_id
            for class_id, oclass in class_by_id.items()
            for alias in (oclass.name, oclass.display_name())
        }
        for oclass in classes:
            node = self.load_class(oclass)
            source_id = node.mermaid_id()
            for relationship in oclass.relationships:
                target_id = aliases.get(relationship.target)
                if target_id is None:
                    continue
                item = (source_id, target_id, relationship.kind or "association")
                if item not in relationships:
                    relationships.append(item)
            base_name = node.extends_base_name()
            target_id = aliases.get(base_name or "")
            item = (source_id, target_id or "", "inheritance")
            if target_id and item not in relationships:
                relationships.append(item)
        return relationships

    def _parse_classes(
        self,
        mermaid_src: str,
        module_name: str = "",
    ) -> "MiroCleanEngineeringModel":
        """Parse a Mermaid classDiagram back into a class model."""
        model = type(self)(name="", sequential_order=1)
        module = MiroModule(name=module_name, sequential_order=1)
        model.modules.append(module)
        order = 1
        id_to_class: Dict[str, MiroClass] = {}

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
            oclass = MiroClass(
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
            kind = self._ARROW_TO_KIND.get(arrow, "association")
            already = any(
                r.target == tgt_name for r in src_cls.relationships
            )
            if not already:
                src_cls.relationships.append(Relationship(target=tgt_name, kind=kind))

        return model

    # ------------------------------------------------------------------
    # SVG wrapping
    # ------------------------------------------------------------------

    def _wrap_diagram(self, mermaid: str, title: str) -> str:
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

    def _extract_mermaid(self, text: str) -> Optional[str]:
        """Extract Mermaid source from a canvas-composer SVG string."""
        diagrams = self._extract_diagrams(text)
        return diagrams[0][1] if diagrams else None

    def _extract_diagrams(self, text: str) -> List[Tuple[ET.Element, str]]:
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
