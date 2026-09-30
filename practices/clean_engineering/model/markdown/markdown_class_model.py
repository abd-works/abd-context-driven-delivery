"""Markdown channel for the CleanEngineering model.

Format (language + modules/model markdown, module-first):

    # ModuleName

    *ModuleName* is [description - what it is, its boundary, collaborators, seam, constraint].

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

Relationships:
  - Property lines with ``<< composition|aggregation|association >>`` become edges.
  - Operation return types and PascalCase parameter types also become edges
    (default association). An optional stereotype on the op line applies to
    the return type (e.g. ``+ << composition >> continueToForm(): PortabilityForm``).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import List, Optional

_repo = Path(__file__).resolve().parents[3]
if str(_repo) not in sys.path:
    sys.path.insert(0, str(_repo))

from practices.clean_engineering.model.base_class_model import OoadNode
from practices.clean_engineering.model.base_class_model import (
    CleanEngineeringModel,
    Module,
    OoadClass,
    Operation,
    Property,
    Relationship,
    companion_interface_name,
    is_interface_name,
)
from practices.clean_engineering.model.property import append_invariant, invariant_lines, property_notes, take_property_note
from practices.clean_engineering.model.update_report import ChildCollectionPair, UpdateReport


def _class_heading_name(raw: str) -> str:
    name = re.sub(r"<<[^>]+>>", "", raw)
    name = name.replace("**", "").strip()
    if " : " in name:
        name = name.split(" : ", 1)[0].strip()
    return name


class MarkdownOoadClass(OoadClass):
    def load_property_field(self, source: Property) -> Property:
        loaded = Property(name=source.name)
        loaded.update_self(source)
        return loaded

    def load_operation_field(self, source: Operation) -> Operation:
        loaded = Operation(name=source.name)
        loaded.update_self(source)
        return loaded

    def child_collections(self, source: OoadNode) -> List[ChildCollectionPair]:
        assert isinstance(source, OoadClass)
        return [
            ChildCollectionPair(self.properties, source.properties, self.load_property_field),
            ChildCollectionPair(self.operations, source.operations, self.load_operation_field),
        ]

    def update_self(self, source: OoadNode) -> None:
        assert isinstance(source, OoadClass)
        self.intent = source.intent
        self.collaborators = list(source.collaborators)

    def render(self, known_names: Optional[List[str]] = None) -> str:
        names = known_names or []
        heading = self.name
        iface = companion_interface_name(self.name, names)
        if iface:
            heading = f"{self.name} : {iface}"
        lines: List[str] = [f"## {heading}", ""]
        if self.intent:
            lines.append(self.intent)
            lines.append("")
        params = ", ".join(
            f"{property_row.name}: {property_row.type_hint}" if property_row.type_hint else property_row.name
            for property_row in self.properties
        )
        constructors = [
            operation for operation in self.operations
            if operation.name in {self.name, "constructor"}
        ]
        methods = [
            operation for operation in self.operations
            if operation.name not in {self.name, "constructor"}
        ]
        if self.properties or self.operations:
            signature = self._constructor_signature(constructors[0]) if constructors else f"{self.name}({params})"
            lines.append(self._public_line(signature))
            for operation in constructors:
                for callee in operation.callees:
                    lines.append(f"\t-> {callee}")
                for note in invariant_lines(operation):
                    lines.append(f"\t// {note}")
            lines.append("------")
            for property_row in self.properties:
                lines.append(self._property_line(property_row))
                for note in property_notes(property_row):
                    lines.append(f"\t// {note}")
            lines.append("----")
            for operation in methods:
                if is_interface_name(self.name) and operation.name.startswith("_"):
                    continue
                lines.append(self._public_line(operation.render()))
                for callee in operation.callees:
                    lines.append(f"\t-> {callee}")
                for note in invariant_lines(operation):
                    lines.append(f"\t// {note}")
        lines.append("")
        return "\n".join(lines)

    def _constructor_signature(self, operation: Operation) -> str:
        """Markdown names the constructor after the class. Code channels keep the word constructor."""
        body = operation.save()
        if operation.name == "constructor" and body.startswith("constructor"):
            return f"{self.name}{body[len('constructor'):]}"
        return body

    def _public_line(self, body: str) -> str:
        """Public members lead with +. A leading - is already the private mark."""
        if body.startswith("+") or body.startswith("-"):
            return body
        return f"+ {body}"

    def _property_line(self, prop: Property) -> str:
        """Public field, with << composition|aggregation|association >> when an edge names its type."""
        kind = (prop.stereotype or "").lower()
        if kind not in {"composition", "aggregation", "association"}:
            kind = self._relationship_kind(prop.type_hint)
        stereo = f"<< {kind} >> " if kind else ""
        return self._public_line(f"{stereo}{prop.save()}")

    def _relationship_kind(self, type_hint: str) -> str:
        if not type_hint:
            return ""
        by_target = {
            relationship.target: (relationship.kind or "").lower()
            for relationship in self.relationships
            if relationship.kind
        }
        for name in re.findall(r"\b([A-Z][A-Za-z0-9]*)\b", type_hint):
            kind = by_target.get(name, "")
            if kind in {"composition", "aggregation", "association"}:
                return kind
        return ""

    @classmethod
    def parse_body(cls, name: str, body: str, sequential_order: int) -> "MarkdownOoadClass":
        host = MarkdownCleanEngineeringModel(name="", sequential_order=1)
        host._class_order = sequential_order
        parsed = host._parse_class(name, body)
        loaded = cls(name=parsed.name, sequential_order=sequential_order)
        loaded.intent = parsed.intent
        loaded.properties = parsed.properties
        loaded.operations = parsed.operations
        loaded.collaborators = list(parsed.collaborators)
        return loaded


class MarkdownModule(Module):
    def get_next_class_from_file(self) -> MarkdownOoadClass:
        class_block = self._class_blocks.pop(0)
        heading = re.match(r"^#{2,3}\s+(.+)", class_block)
        class_name = _class_heading_name(heading.group(1)) if heading else ""
        body = class_block[heading.end():].lstrip("\n") if heading else class_block
        return MarkdownOoadClass.parse_body(class_name, body, len(self.classes) + 1)

    def load_class(self, source: OoadClass) -> MarkdownOoadClass:
        loaded = MarkdownOoadClass(name=source.name, sequential_order=source.sequential_order)
        loaded.update_self(source)
        return loaded

    def render(self) -> str:
        lines: List[str] = [f"# {self.name}", ""]
        if self.description:
            lines.append(self.description)
            lines.append("")
        terms = self.public_terms()
        modules_only = bool(self.dependencies or self.seam_terms) and not any(
            loaded.properties or loaded.operations for loaded in self.classes
        )
        if modules_only or (terms and not self.classes):
            if self.description:
                lines.append(f"- **Purpose:** {self.description.splitlines()[0].strip()}")
            if terms:
                lines.append(f"- **Seam (terms):** {', '.join(terms)}")
            if self.dependencies:
                lines.append(
                    f"- **Dependencies (one-way):** {', '.join(self.dependencies)}"
                )
            elif modules_only:
                lines.append("- **Dependencies (one-way):** *(none)*")
            lines.append("")
        known = [loaded.name for loaded in self.classes]
        for loaded in self.classes:
            lines.append(loaded.render(known_names=known))
        return "\n".join(lines)


class MarkdownCleanEngineeringModel(CleanEngineeringModel):

    def load_module(self, source: Module) -> MarkdownModule:
        loaded = MarkdownModule(name=source.name, sequential_order=source.sequential_order)
        loaded.update_self(source)
        return loaded

    def load_class(self, source: OoadClass) -> MarkdownOoadClass:
        loaded = MarkdownOoadClass(name=source.name, sequential_order=source.sequential_order)
        loaded.update_self(source)
        return loaded

    module_type = None

    def load_content(self) -> None:
        from pathlib import Path

        text = Path(self.path).read_text(encoding="utf-8")
        self._blocks = [block for block in re.split(r"(?m)^(?=#\s)", text) if block.strip()]
        self._block_index = 0
        self._module_order = 1

    def has_more_module(self) -> bool:
        return self._block_index < len(getattr(self, "_blocks", []))

    def get_next_module_from_file(self) -> "MarkdownModule":
        block = self._blocks[self._block_index].strip()
        self._block_index += 1
        heading = re.match(r"^#\s+(.+)", block)
        if heading is None:
            module = self.module_type(name="", sequential_order=self._module_order)
            self._module_order += 1
            return module
        body = block[heading.end():].lstrip("\n")
        module = self.module_type(name=heading.group(1).strip(), sequential_order=self._module_order)
        self._module_order += 1
        parts = re.split(r"(?m)^(?=##\s)", body, maxsplit=1)
        self._apply_module_preamble(module, parts[0].strip())
        classes_text = parts[1] if len(parts) > 1 else ""
        module._class_blocks = self._class_blocks_in(classes_text)
        return module

    def parse(self, text: str) -> "MarkdownCleanEngineeringModel":
        model = type(self)(name="", sequential_order=1)
        self._module_order = 1
        for block in re.split(r"(?m)^(?=#\s)", text):
            module = self._module_from_h1(block.strip())
            if module is None:
                continue
            model.modules.append(module)
            self._module_order += 1
        return model

    def _module_from_h1(self, block: str) -> MarkdownModule | None:
        if not block:
            return None
        heading = re.match(r"^#\s+(.+)", block)
        if not heading:
            return None
        body_after_h1 = block[heading.end():].lstrip("\n")
        module = MarkdownModule(name=heading.group(1).strip(), sequential_order=self._module_order)
        h2_split = re.split(r"(?m)^(?=##\s)", body_after_h1, maxsplit=1)
        self._apply_module_preamble(module, h2_split[0].strip())
        self._append_h2_classes(module, h2_split[1] if len(h2_split) > 1 else "")
        return module

    def _apply_module_preamble(self, module: MarkdownModule, pre_h2: str) -> None:
        if not pre_h2:
            return
        purpose, seam_terms, deps, leftover = self._parse_module_meta(pre_h2)
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

    def _class_blocks_in(self, classes_text: str) -> List[str]:
        blocks: List[str] = []
        for class_block in re.split(r"(?m)^(?=##\s)", classes_text):
            class_block = class_block.strip()
            heading = re.match(r"^##\s+(.+)", class_block) if class_block else None
            if heading is None:
                continue
            class_name = heading.group(1).strip()
            if class_name.lower() in self._MODULE_META_HEADINGS:
                self._section_heading = class_name
                continue
            if re.search(r"(?m)^###\s+\*\*", class_block):
                for nested in re.split(r"(?m)^(?=###\s)", class_block):
                    nested = nested.strip()
                    if nested.startswith("###"):
                        blocks.append(nested)
                continue
            blocks.append(class_block)
        return blocks

    def _append_h2_classes(self, module: MarkdownModule, classes_text: str) -> None:
        class_order = 1
        for class_block in self._class_blocks_in(classes_text):
            heading = re.match(r"^#{2,3}\s+(.+)", class_block)
            if heading is None:
                continue
            class_name = _class_heading_name(heading.group(1))
            if not class_name or class_name.lower().startswith("module "):
                continue
            module.classes.append(
                MarkdownOoadClass.parse_body(
                    class_name,
                    class_block[heading.end():].lstrip("\n"),
                    class_order,
                )
            )
            class_order += 1

    def render(self, canonical: Optional[CleanEngineeringModel] = None, previous: Optional[str] = None) -> str:
        if canonical is not None:
            self.translate_from(canonical)
        return "\n".join(module.render() for module in self.modules)

    def sync(self, text: str, canonical: CleanEngineeringModel) -> UpdateReport:
        return canonical.translate_from(self.parse(text))

    @classmethod
    def from_workspace(cls, root: Path) -> Optional["MarkdownCleanEngineeringModel"]:
        for path in sorted(root.glob("**/*.md")):
            text = path.read_text(encoding="utf-8", errors="ignore")
            if "practices.clean_engineering.clean_engineering:CleanEngineering" in text and "@toolset-manifest" in text:
                return cls().parse(text)
        return None

    _MODULE_META_HEADINGS = frozenset({
        "seam",
        "dependencies",
        "modules fidelity",
        "purpose",
    })


    def _parse_term_list(self, raw: str) -> List[str]:
        text = raw.strip()
        text = re.sub(r"^\*\(?none\)?\*$", "", text, flags=re.IGNORECASE).strip()
        if not text or text.lower() in {"*(none)*", "(none)", "none", "-", "-"}:
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


    def _parse_module_meta(self, text: str) -> tuple[str, List[str], List[str], str]:
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
                seam_terms = self._parse_term_list(m_seam.group(1))
            elif m_deps:
                deps = self._parse_term_list(m_deps.group(1))
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


    def _apply_module_section(self, module: Module, body: str) -> None:
        heading = self._section_heading
        key = heading.lower().strip()
        if key == "modules fidelity":
            purpose, seam_terms, deps, _leftover = self._parse_module_meta(body)
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
            # Narrative seam section - keep as seam prose; pull backticked names as terms
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
                module.dependencies = self._parse_term_list(formal.group(1))
            else:
                first = next((ln.strip() for ln in body.splitlines() if ln.strip()), "")
                module.dependencies = self._parse_term_list(first)
        elif key == "purpose":
            module.description = body.strip()

    def _parse_class(self, name: str, body: str) -> OoadClass:
        parts6 = re.split(r"(?m)^-{6}\s*$", body, maxsplit=1)
        pre6 = parts6[0] if parts6 else ""
        post6 = parts6[1] if len(parts6) > 1 else ""

        intent_lines: List[str] = []
        constructor_notes: List[str] = []
        constructor_line = ""
        seen_signature = False
        for line in pre6.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith("//"):
                if seen_signature:
                    constructor_notes.append(stripped[2:].strip())
                continue
            if stripped.startswith("->") or stripped.startswith("+") or stripped.startswith("-"):
                seen_signature = True
                if stripped.startswith("+") or stripped.startswith("-"):
                    constructor_line = stripped
                continue
            if re.match(r"^\w[\w\s]*\(", stripped):
                seen_signature = True
                constructor_line = stripped
                continue
            if not seen_signature:
                intent_lines.append(stripped)
        intent = "\n".join(intent_lines)

        parts4 = re.split(r"(?m)^-{4}\s*$", post6, maxsplit=1)
        props_text = parts4[0] if parts4 else ""
        ops_text = parts4[1] if len(parts4) > 1 else ""

        props, _rels = self._parse_properties_and_relationships(props_text)
        ops, _op_rels = self._parse_operations_and_relationships(ops_text)
        self._relationships_from_properties(props)
        if constructor_line:
            constructors, _ = self._parse_operations_and_relationships(constructor_line)
            for constructor in constructors:
                for note in constructor_notes:
                    append_invariant(constructor, note)
                ops.insert(0, constructor)
        return MarkdownOoadClass(
            name=name,
            sequential_order=self._class_order,
            intent=intent,
            properties=props,
            operations=ops,
        )


    _CE_STEREOTYPE_KINDS = {
        "composition": "composition",
        "aggregation": "aggregation",
        "association": "association",
    }


    def _strip_ce_prefix(self, line: str) -> tuple[str, str | None]:
        """Strip CE OOAD format prefix from a property/operation line.

        Handles lines like:
          + << composition >> identity: Identity
          + name: string
          + save(): void
          - privateOp(): void
        Returns (bare_line, stereotype_kind | None).
        stereotype_kind is one of "composition", "aggregation", "association" or None.
        """
        # Strip leading "+" (public) visibility marker used in CE OOAD markdown
        if line.startswith("+"):
            line = line[1:].strip()
        # Extract and strip UML stereotype annotation like "<< composition >>"
        kind: str | None = None
        m = re.match(r"^<<\s*(\w+)\s*>>\s*", line)
        if m:
            raw_kind = m.group(1).lower()
            kind = self._CE_STEREOTYPE_KINDS.get(raw_kind)
            line = line[m.end():].strip()
        return line, kind


    def _parse_properties_and_relationships(self, text: str) -> tuple[List[Property], List[Relationship]]:
        """Parse properties AND extract Relationship objects from CE OOAD stereotype annotations.

        A line like ``+ << composition >> identity: Identity`` produces both a
        Property(name="identity", type_hint="Identity") and a
        Relationship(kind="composition", target="Identity").
        """
        props: List[Property] = []
        rels: List[Relationship] = []
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if stripped.startswith("//"):
                if props:
                    take_property_note(props[-1], stripped[2:])
                continue
            if stripped.startswith("->"):
                continue
            original = stripped
            stripped, rel_kind = self._strip_ce_prefix(stripped)
            if "<<" in original and rel_kind is None:
                continue
            if not stripped:
                continue
            # Skip lines that look like operations
            if re.match(r"^_?\w+\s*\(", stripped):
                continue
            # Optional props may be written `name?: Type` or `name: Type | null`.
            m = re.match(r"^(\w+)\??:\s*(.+)", stripped)
            if m:
                prop_name = m.group(1)
                type_raw = m.group(2).strip()
                prop = Property(name=prop_name, type_hint=type_raw)
                if rel_kind:
                    prop.stereotype = rel_kind
                props.append(prop)
            elif re.match(r"^\w+$", stripped):
                props.append(Property(name=stripped))
        return props, rels


    def _parse_properties(self, text: str) -> List[Property]:
        props, _ = self._parse_properties_and_relationships(text)
        return props


    def _parse_operations(self, text: str) -> List[Operation]:
        ops, _ = self._parse_operations_and_relationships(text)
        return ops


    _NON_DOMAIN_TYPE_NAMES = frozenset({
        "String", "Number", "Boolean", "Void", "Any", "Unknown", "Object",
        "Record", "Array", "Promise", "Partial", "Omit", "Pick", "RegExp",
        "Date", "Error", "Map", "Set", "Readonly", "Required", "NonNullable",
        "Collection", "List", "Iterable", "Sequence", "Optional",
    })


    def _domain_type_names(self, type_raw: str) -> List[str]:
        """PascalCase type names from a CE type hint (returns, params, props)."""
        if not type_raw:
            return []
        names: List[str] = []
        for m in re.finditer(r"\b([A-Z][A-Za-z0-9]*)\b", type_raw):
            name = m.group(1)
            if name in self._NON_DOMAIN_TYPE_NAMES or name in names:
                continue
            names.append(name)
        return names


    def _relationships_from_properties(self, props: List[Property]) -> None:
        """A relationship is optional on the property. A primitive or a third-party type has none."""
        from practices.clean_engineering.model.property import bind_property_relationship

        for prop in props:
            bind_property_relationship(prop)

    def _dedupe_relationships(self, rels: List[Relationship]) -> List[Relationship]:
        """One edge per target; stronger ownership (composition > aggregation > association) wins."""
        rank = {"composition": 3, "aggregation": 2, "association": 1}
        best: dict[str, Relationship] = {}
        for rel in rels:
            kind = (rel.kind or "association").lower()
            if kind not in rank:
                kind = "association"
            prev = best.get(rel.target)
            if prev is None or rank[kind] > rank.get((prev.kind or "association").lower(), 1):
                best[rel.target] = Relationship(
                    kind=kind,
                    target=rel.target,
                    cardinality=rel.cardinality,
                    description=rel.description,
                )
        return list(best.values())


    def _parse_operations_and_relationships(self, 
        text: str,
    ) -> tuple[List[Operation], List[Relationship]]:
        """Parse operations and infer association edges from return/param types.

        Property stereotypes remain the place for composition/aggregation. Method
        signatures default to association so return types like ``viewPortability():
        Portability`` and params like ``portNumber(info: PortingInfo)`` become edges.
        An optional ``<< composition|aggregation|association >>`` on the op line
        applies to the return type only.
        """
        ops: List[Operation] = []
        rels: List[Relationship] = []
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if stripped.startswith("//"):
                if ops:
                    append_invariant(ops[-1], stripped[2:])
                continue
            if stripped.startswith("->"):
                if ops:
                    callee = stripped[2:].strip()
                    if callee and callee not in ops[-1].callees:
                        ops[-1].callees.append(callee)
                continue
            private = stripped.startswith("- ")
            body = stripped[2:].strip() if private else stripped
            body, ret_kind = self._strip_ce_prefix(body)
            m = re.match(r"^(_?\w+)\(([^)]*)\)(?::\s*(.+))?", body)
            if not m:
                continue
            op_name = ("_" if private and not m.group(1).startswith("_") else "") + m.group(1)
            params = [p.strip() for p in m.group(2).split(",") if p.strip()]
            ret = (m.group(3) or "").strip()
            ops.append(Operation(name=op_name, parameters=params, return_type=ret))

            kind = ret_kind or "association"
            for target in self._domain_type_names(ret):
                rels.append(Relationship(kind=kind, target=target))
            for param in params:
                # name: Type  or  name?: Type
                pm = re.match(r"^(\w+)\??:\s*(.+)$", param)
                if not pm:
                    continue
                for target in self._domain_type_names(pm.group(2)):
                    rels.append(Relationship(kind="association", target=target))
        return ops, rels


MarkdownCleanEngineeringModel.module_type = MarkdownModule
