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
  - A line ``---<<stops>>--> RunningProcess`` after the operations is a dependency: what the class does to
    another class at run time, labelled by that interaction.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from cdd_guidance.practices.clean_engineering.model.call_graph import parse_arrow_line
from cdd_guidance.practices.clean_engineering.model.class_stereotypes import marks_in, without_marks
from cdd_guidance.practices.clean_engineering.model.base_class_model import (
    CleanEngineeringModel,
    Module,
    OoadClass,
    is_interface_name,
)
from cdd_guidance.practices.clean_engineering.model.operation import Operation
from cdd_guidance.practices.clean_engineering.model.property import Property
from cdd_guidance.practices.clean_engineering.model.field_types import Relationship
from cdd_guidance.practices.clean_engineering.model.property import append_invariant, invariant_lines, property_notes, take_property_note
from cdd_guidance.practices.clean_engineering.model.type_refs import domain_type_names, split_top_level


_HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
_CARD_HEADING = re.compile(r"^(#{2,6})\s+\*\*([^*]+)\*\*(.*?)\s*$")
_FENCE = re.compile(r"^\s*(```|~~~)")
# A dependency line: `---<<reads sections with>>--> MarkdownText`.
_DEPENDENCY = re.compile(r"^\s*-{3}<<\s*(?P<label>.+?)\s*>>-{2}>\s*(?P<target>[A-Za-z_][\w.]*)\s*$")


def _split_bases(text: str) -> List[str]:
    return [base.strip() for base in split_top_level(text) if base.strip()]


@dataclass
class ClassHeading:
    """A class heading as written: `Cart <<Aggregate Root>> : Basket, Auditable`, or a card's
    `**Cart** <<Entity>> — *Access Selfcare*`.

    The name comes first, then the class's stereotypes as `<<Mark>>`s, then its base classes after ` : `. A card may
    end with a note, which is kept as written so a card the model did not change reads the same."""

    name: str
    stereotypes: List[str] = field(default_factory=list)
    bases: List[str] = field(default_factory=list)
    note: str = ""

    @classmethod
    def read(cls, raw: str) -> "ClassHeading":
        text = raw.strip()
        bold = re.match(r"^\*\*([^*]+)\*\*", text)
        if bold is None:
            name, _, bases = without_marks(text.replace("**", "")).partition(" : ")
            return cls(name.strip(), marks_in(text), _split_bases(bases))
        rest = without_marks(text[bold.end():])
        bases, note = (rest[1:], "") if rest.startswith(":") else ("", rest)
        if " — " in bases:
            bases, note = bases.split(" — ", 1)[0], "— " + bases.split(" — ", 1)[1]
        return cls(bold.group(1).strip(), marks_in(text[bold.end():]), _split_bases(bases), note.strip())

    def text(self) -> str:
        return f"{self.name}{self._tail()}"

    def card_text(self) -> str:
        note = f" {self.note}" if self.note else ""
        return f"**{self.name}**{self._tail()}{note}"

    def _tail(self) -> str:
        marks = "".join(f" <<{item}>>" for item in self.stereotypes)
        bases = f" : {', '.join(self.bases)}" if self.bases else ""
        return f"{marks}{bases}"


class MarkdownOoadClass(OoadClass):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # The card this class was read from, the note on its heading, and the class as it read then.
        self._card: Optional[str] = None
        self._card_note = ""
        self._card_model = ""

    def render(self, known_names: Optional[List[str]] = None) -> str:
        lines: List[str] = [f"## {self.heading(known_names or []).text()}", ""]
        if self.intent:
            lines.extend([self.intent, ""])
        if self.properties or self.operations or self.dependencies:
            lines.extend(self._member_lines())
        lines.append("")
        return "\n".join(lines)

    def heading(self, known_names: List[str]) -> ClassHeading:
        """The class's heading: its stereotypes, then the bases its declaration names."""
        return ClassHeading(self.name, list(self.stereotypes), self.declared_bases(known_names), self._card_note)

    def _member_lines(self) -> List[str]:
        constructors = [operation for operation in self.operations if operation.name in {self.name, "constructor"}]
        methods = [operation for operation in self.operations if operation.name not in {self.name, "constructor"}]
        lines = [self._public_line(self._constructor_line(constructors))]
        for operation in constructors:
            lines.extend(self._notes_under(operation.callees, invariant_lines(operation)))
        lines.append("------")
        for prop in self.properties:
            lines.append(self._property_line(prop))
            lines.extend(self._notes_under(prop.callees, property_notes(prop)))
        lines.append("----")
        for operation in methods:
            if is_interface_name(self.name) and operation.name.startswith("_"):
                continue
            lines.append(self._public_line(operation.render()))
            lines.extend(self._notes_under(operation.callees, invariant_lines(operation)))
        lines.extend(f"---<<{item.label}>>--> {item.target}" for item in self.dependencies)
        return lines

    def _constructor_line(self, constructors: List[Operation]) -> str:
        if constructors:
            return self._constructor_signature(constructors[0])
        params = ", ".join(f"{prop.name}: {prop.type_hint}" if prop.type_hint else prop.name for prop in self.properties)
        return f"{self.name}({params})"

    def _notes_under(self, callees: List[str], notes: List[str]) -> List[str]:
        """The call-graph arrows and invariant notes written under a member, indented."""
        return [f"\t-> {callee}" for callee in callees] + [f"\t// {note}" for note in notes]

    def keep_card(self, card: str, heading: ClassHeading) -> None:
        """Remember the card this class was read from, so an unchanged class writes it back as is."""
        self._card = card
        self._card_note = heading.note
        self._card_model = self.render()

    def render_card(self, level: int) -> str:
        """The card as it was read while the class is unchanged; otherwise the card written from the model."""
        if self._card is not None and self.render() == self._card_model:
            return self._card
        body = self.render().split("\n", 1)[1]
        return f"{'#' * level} {self.heading([]).card_text()}\n{body}\n"

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
    def parse_body(cls, heading: ClassHeading, body: str, sequential_order: int) -> "MarkdownOoadClass":
        host = MarkdownCleanEngineeringModel(name="", sequential_order=1)
        host._class_order = sequential_order
        parsed = host._parse_class(heading.name, body)
        loaded = cls(name=parsed.name, sequential_order=sequential_order)
        loaded.stereotypes = list(heading.stereotypes)
        loaded.bases = list(heading.bases)
        loaded.intent = parsed.intent
        loaded.properties = parsed.properties
        loaded.operations = parsed.operations
        loaded.collaborators = list(parsed.collaborators)
        loaded.dependencies = list(parsed.dependencies)
        return loaded


class MarkdownModule(Module):
    def get_next_class_from_file(self) -> MarkdownOoadClass:
        class_block = self._class_blocks.pop(0)
        heading = re.match(r"^#{2,3}\s+(.+)", class_block)
        class_heading = ClassHeading.read(heading.group(1)) if heading else ClassHeading("")
        body = class_block[heading.end():].lstrip("\n") if heading else class_block
        return MarkdownOoadClass.parse_body(class_heading, body, len(self.classes) + 1)

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

    def render_cards(self, module_level: int, card_level: int) -> str:
        """The module as it was read: its own text in place, each class card where it stood,
        and a class the document did not have after the last card."""
        parts = getattr(self, "_card_parts", None)
        if parts is None:
            parts = [f"{'#' * module_level} {self.name}\n", "\n"]
            if self.description:
                parts.extend([self.description.rstrip("\n") + "\n", "\n"])
        elif self.name != self._card_name:
            parts = [f"{'#' * module_level} {self.name}\n", *parts[1:]]
        written = []
        out: List[str] = []
        for part in parts:
            if isinstance(part, str):
                out.append(part)
            elif any(loaded is part for loaded in self.classes):
                out.append(part.render_card(card_level))
                written.append(part)
        for loaded in self.classes:
            if not any(loaded is done for done in written):
                out.append(loaded.render_card(card_level))
        return "".join(out)


class MarkdownCleanEngineeringModel(CleanEngineeringModel):

    def load_module(self, source: Module) -> MarkdownModule:
        loaded = MarkdownModule(name=source.name, sequential_order=source.sequential_order)
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
        module._class_blocks = self._class_blocks_in(module, classes_text)
        return module

    def parse(self, text: str) -> "MarkdownCleanEngineeringModel":
        headings = self._headings(text)
        card_levels = [level for _index, level, raw in headings if _CARD_HEADING.match(raw)]
        if card_levels and min(card_levels) - 2 >= 2:
            return self._parse_card_document(text, headings, min(card_levels))
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

    def _class_blocks_in(self, module: Module, classes_text: str) -> List[str]:
        blocks: List[str] = []
        for class_block in re.split(r"(?m)^(?=##\s)", classes_text):
            class_block = class_block.strip()
            heading = re.match(r"^##\s+(.+)", class_block) if class_block else None
            if heading is None:
                continue
            class_name = heading.group(1).strip()
            if class_name.lower() in self._MODULE_META_HEADINGS:
                self._apply_module_section(module, class_name, class_block[heading.end():])
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
        for class_block in self._class_blocks_in(module, classes_text):
            heading = re.match(r"^#{2,3}\s+(.+)", class_block)
            if heading is None:
                continue
            class_heading = ClassHeading.read(heading.group(1))
            if not class_heading.name or class_heading.name.lower().startswith("module "):
                continue
            parsed = MarkdownOoadClass.parse_body(class_heading, class_block[heading.end():].lstrip("\n"), class_order)
            module.classes.append(parsed)
            class_order += 1

    def _headings(self, text: str) -> List[tuple]:
        """(line index, level, line) for each heading outside a fenced block."""
        found = []
        fenced = False
        for index, line in enumerate(text.splitlines()):
            if _FENCE.match(line):
                fenced = not fenced
                continue
            heading = _HEADING.match(line)
            if heading and not fenced:
                found.append((index, len(heading.group(1)), line))
        return found

    def _parse_card_document(self, text: str, headings: List[tuple], card_level: int) -> "MarkdownCleanEngineeringModel":
        """A document title over modules, resource groups, and bold class cards, each one level
        deeper (`#` title, `##` module, `###` group, `####` card). A module is a heading at the
        module level with a card under it; every other line stays where it was written."""
        module_level = card_level - 2
        model = type(self)(name="", sequential_order=1)
        model._card_levels = (module_level, card_level)
        model._card_parts = []
        heading_at = {index: level for index, level, _raw in headings}
        module_starts = self._module_starts(headings, module_level, card_level)
        lines = text.splitlines(keepends=True)
        module: Optional[MarkdownModule] = None
        card: List[str] = []

        def close_card() -> None:
            if card and module is not None:
                self._append_card(module, "".join(card))
            card.clear()

        for index, line in enumerate(lines):
            level = heading_at.get(index)
            if level is not None and level <= module_level:
                close_card()
                module = None
                if index in module_starts:
                    module = MarkdownModule(name=_HEADING.match(line).group(2), sequential_order=len(model.modules) + 1)
                    module._card_name = module.name
                    module._card_parts = [line]
                    model.modules.append(module)
                    model._card_parts.append(module)
                    self._apply_module_preamble(module, self._preamble_after(lines, index, heading_at))
                    continue
            elif level is not None and level <= card_level and module is not None:
                close_card()
                if level == card_level and _CARD_HEADING.match(line):
                    card.append(line)
                    continue
            elif card:
                card.append(line)
                continue
            (module._card_parts if module is not None else model._card_parts).append(line)
        close_card()
        return model

    def _module_starts(self, headings: List[tuple], module_level: int, card_level: int) -> set:
        starts = set()
        current = None
        for index, level, raw in headings:
            if level <= module_level:
                current = index if level == module_level else None
            elif current is not None and level == card_level and _CARD_HEADING.match(raw):
                starts.add(current)
        return starts

    def _preamble_after(self, lines: List[str], start: int, heading_at: dict) -> str:
        end = next((index for index in sorted(heading_at) if index > start), len(lines))
        return "".join(lines[start + 1:end]).strip()

    def _append_card(self, module: MarkdownModule, card: str) -> None:
        class_heading = ClassHeading.read(card.split("\n", 1)[0].lstrip("#"))
        body = card.split("\n", 1)[1] if "\n" in card else ""
        loaded = MarkdownOoadClass.parse_body(class_heading, body, len(module.classes) + 1)
        loaded.keep_card(card, class_heading)
        module.classes.append(loaded)
        module._card_parts.append(loaded)

    def _render_cards(self) -> str:
        module_level, card_level = self._card_levels
        out: List[str] = []
        written = []
        for part in self._card_parts:
            if isinstance(part, str):
                out.append(part)
            elif any(module is part for module in self.modules):
                out.append(part.render_cards(module_level, card_level))
                written.append(part)
        for module in self.modules:
            if not any(module is done for done in written):
                out.append(module.render_cards(module_level, card_level))
        return "".join(out)

    def render(self, canonical: Optional[CleanEngineeringModel] = None, previous: Optional[str] = None) -> str:
        if getattr(canonical, "_card_parts", None) is not None:
            return canonical._render_cards()
        if canonical is not None:
            self.translate_from(canonical)
        if getattr(self, "_card_parts", None) is not None:
            return self._render_cards()
        return "\n".join(module.render() for module in self.modules)

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


    def _apply_module_section(self, module: Module, heading: str, body: str) -> None:
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
        dependencies = [
            Relationship(target=found.group("target"), kind="dependency", label=found.group("label"))
            for found in (_DEPENDENCY.match(line) for line in body.splitlines()) if found
        ]
        body = "\n".join(line for line in body.splitlines() if not _DEPENDENCY.match(line))
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
            relationships=dependencies,
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
                if props:
                    props[-1].callees.append(stripped[2:].strip())
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


    def _relationships_from_properties(self, props: List[Property]) -> None:
        """A relationship is optional on the property. A primitive or a third-party type has none."""

        for prop in props:
            prop.derive_relationship()

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
            if stripped.startswith("->") or stripped.startswith("→"):
                if ops:
                    arrow = parse_arrow_line(stripped)
                    callee = arrow[1] if arrow else stripped[2:].strip()
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
            params = split_top_level(m.group(2))
            ret = (m.group(3) or "").strip()
            ops.append(Operation(name=op_name, parameters=params, return_type=ret))

            kind = ret_kind or "association"
            for target in domain_type_names(ret):
                rels.append(Relationship(kind=kind, target=target))
            for param in params:
                # name: Type  or  name?: Type
                pm = re.match(r"^(\w+)\??:\s*(.+)$", param)
                if not pm:
                    continue
                for target in domain_type_names(pm.group(2)):
                    rels.append(Relationship(kind="association", target=target))
        return ops, rels


MarkdownCleanEngineeringModel.module_type = MarkdownModule
