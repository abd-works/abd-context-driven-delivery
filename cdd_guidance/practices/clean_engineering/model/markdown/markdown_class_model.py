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
  - A line ``---<<runs>>--> Git`` after the operations of ``Repo`` is a dependency: what the class does to
    another class at run time, labelled by that interaction.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
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
from cdd_guidance.practices.clean_engineering.model.type_refs import split_top_level


_HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
_CARD_HEADING = re.compile(r"^(#{2,6})\s+\*\*([^*]+)\*\*(.*?)\s*$")
_FENCE = re.compile(r"^\s*(```|~~~)")


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
            lines.extend(self._notes_under(operation.callees, operation.invariant_lines()))
        lines.append("------")
        for prop in self.properties:
            lines.append(self._property_line(prop))
            lines.extend(self._notes_under(prop.callees, prop.notes()))
        lines.append("----")
        for operation in methods:
            if is_interface_name(self.name) and operation.name.startswith("_"):
                continue
            lines.append(self._public_line(operation.render()))
            lines.extend(self._notes_under(operation.callees, operation.invariant_lines()))
        lines.extend(line for item in self.dependencies for line in item.lines())
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
    def read_card(cls, heading: ClassHeading, body: str, sequential_order: int) -> "MarkdownOoadClass":
        """The class a card shows: named and marked by its heading, filled from its body."""
        loaded = cls(name=heading.name, sequential_order=sequential_order)
        loaded.stereotypes = list(heading.stereotypes)
        loaded.bases = list(heading.bases)
        loaded.read_body(body)
        return loaded

    def read_body(self, body: str) -> None:
        """Read this class's card body: its intent, its constructor, its properties and operations, and the
        dependencies it names."""
        text_lines, dependencies = Relationship.split_off(body.splitlines())
        body = "\n".join(text_lines)
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

        props = self._read_properties(props_text)
        ops = self._read_operations(ops_text)
        for prop in props:
            prop.derive_relationship()
        if constructor_line:
            for constructor in self._read_operations(constructor_line):
                for note in constructor_notes:
                    constructor.add_invariant(note)
                ops.insert(0, constructor)
        self.intent = intent
        self.properties = props
        self.operations = ops
        for relationship in dependencies:
            self.place_relationship(relationship)


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


    def _read_properties(self, text: str) -> List[Property]:
        """The properties a card lists. ``+ << composition >> identity: Identity`` is a property whose stereotype
        names the relationship it stands for."""
        props: List[Property] = []
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if stripped.startswith("//"):
                if props:
                    props[-1].take_note(stripped[2:])
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
            prop = Property.from_signature(stripped)
            if prop is not None:
                if rel_kind:
                    prop.stereotype = rel_kind
                props.append(prop)
            elif re.match(r"^\w+$", stripped):
                props.append(Property(name=stripped))
        return props


    def _read_operations(self, text: str) -> List[Operation]:
        """The operations a card lists, with the call-graph arrows and invariant notes written under each."""
        ops: List[Operation] = []
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if stripped.startswith("//"):
                if ops:
                    ops[-1].add_invariant(stripped[2:])
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
            operation = Operation.from_signature(body)
            if operation is None:
                continue
            if private and not operation.name.startswith("_"):
                operation.name = f"_{operation.name}"
            ops.append(operation)
        return ops


class MarkdownModule(Module):
    """A module as a markdown model document writes it: its heading, the prose and bullets that describe it, and its
    class cards. Read from a card document, it keeps its own lines and each card where it stood, so it writes itself
    back as it was read."""

    class_type = MarkdownOoadClass

    _META_HEADINGS = frozenset({"seam", "dependencies", "modules fidelity", "purpose"})

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # Its heading line, its own lines in place, and each class card where it stood, as a card document wrote them;
        # none for a module no card document held.
        self._card_parts: Optional[list] = None
        self._card_name = ""

    def start_card(self, heading: str) -> None:
        """Begin the module as a card document writes it, under its heading line."""
        self._card_name = self.name
        self._card_parts = [heading]

    def add_line(self, line: str) -> None:
        """Keep a line the card document wrote in this module, where it stood."""
        self._card_parts.append(line)

    def add_card(self, card: str) -> None:
        """Read a bold class card the card document wrote in this module, and keep it where it stood."""
        class_heading = ClassHeading.read(card.split("\n", 1)[0].lstrip("#"))
        body = card.split("\n", 1)[1] if "\n" in card else ""
        loaded = MarkdownOoadClass.read_card(class_heading, body, len(self.classes) + 1)
        loaded.keep_card(card, class_heading)
        self.classes.append(loaded)
        self._card_parts.append(loaded)

    def read_body(self, body: str) -> None:
        """Read the text under the module's `#` heading: its description and bullets, then a `##` card per class."""
        split = re.split(r"(?m)^(?=##\s)", body, maxsplit=1)
        self.take_preamble(split[0].strip())
        class_order = 1
        for class_block in self._class_blocks(split[1] if len(split) > 1 else ""):
            heading = re.match(r"^#{2,3}\s+(.+)", class_block)
            class_heading = ClassHeading.read(heading.group(1)) if heading else None
            if class_heading is None or not class_heading.name or class_heading.name.lower().startswith("module "):
                continue
            self.classes.append(MarkdownOoadClass.read_card(class_heading, class_block[heading.end():].lstrip("\n"), class_order))
            class_order += 1

    def take_preamble(self, text: str) -> None:
        """The module's description, seam terms, and dependencies, from the prose and bullets under its heading."""
        if not text:
            return
        meta = ModuleMeta(text)
        self.description = meta.purpose or meta.leftover or text
        self.seam_terms = meta.seam_terms
        self.dependencies = meta.dependencies
        if meta.seam_terms and not self.seam:
            self.seam = ", ".join(meta.seam_terms)

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
        parts = self._card_parts
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

    def _class_blocks(self, classes_text: str) -> List[str]:
        """Each `##` class card under the module, or each `###` card a `##` group holds. A `##` heading that names a
        part of the module itself, such as its seam, describes the module."""
        blocks: List[str] = []
        for class_block in re.split(r"(?m)^(?=##\s)", classes_text):
            class_block = class_block.strip()
            heading = re.match(r"^##\s+(.+)", class_block) if class_block else None
            if heading is None:
                continue
            class_name = heading.group(1).strip()
            if class_name.lower() in self._META_HEADINGS:
                self._take_section(class_name.lower(), class_block[heading.end():])
            elif re.search(r"(?m)^###\s+\*\*", class_block):
                blocks.extend(nested.strip() for nested in re.split(r"(?m)^(?=###\s)", class_block) if nested.strip().startswith("###"))
            else:
                blocks.append(class_block)
        return blocks

    def _take_section(self, key: str, body: str) -> None:
        """A `##` section that describes the module: its modules-fidelity bullets, its seam, its dependencies, or its
        purpose."""
        if key == "modules fidelity":
            self._take_fidelity_bullets(ModuleMeta(body))
        elif key == "seam":
            self._take_seam(body)
        elif key == "dependencies":
            self._take_dependencies(body)
        elif key == "purpose":
            self.description = body.strip()

    def _take_seam(self, body: str) -> None:
        """A narrative seam section is kept as the seam's prose; its backticked names are its terms."""
        self.seam = body.strip()
        if not self.seam_terms:
            self.seam_terms = [term for term in re.findall(r"`([^`]+)`", body) if term.strip() and "." not in term]

    def _take_dependencies(self, body: str) -> None:
        """A "**Formal (modules):** a, b" line names them; else the section's first line lists them."""
        formal = re.search(r"\*\*Formal\s*\(modules\):\*\*\s*(.+)", body, re.IGNORECASE)
        first = next((line.strip() for line in body.splitlines() if line.strip()), "")
        self.dependencies = ModuleMeta.terms(formal.group(1) if formal else first)

    def _take_fidelity_bullets(self, meta: "ModuleMeta") -> None:
        if meta.purpose and not self.description:
            self.description = meta.purpose
        if meta.seam_terms:
            self.seam_terms = meta.seam_terms
            self.seam = self.seam or ", ".join(meta.seam_terms)
        if meta.dependencies:
            self.dependencies = meta.dependencies


class ModuleMeta:
    """<<Value Object>> The Purpose, Seam, and Dependencies bullets of a modules-fidelity block, and the prose left
    beside them."""

    _PURPOSE = re.compile(r"^-?\s*\*\*Purpose:\*\*\s*(.+)$", re.IGNORECASE)
    _SEAM = re.compile(r"^-?\s*\*\*Seam(?:\s*\(terms\))?:\*\*\s*(.+)$", re.IGNORECASE)
    _DEPENDENCIES = re.compile(r"^-?\s*\*\*Dependencies(?:\s*\(one-way\))?:\*\*\s*(.+)$", re.IGNORECASE)
    # Lines that frame the bullets and say nothing of the module: a build order, a nested module's or the block's heading.
    _FRAMING = re.compile(r"^-?\s*\*\*Build order:\*\*|^###\s+Module\s+|^##\s+Modules fidelity", re.IGNORECASE)

    def __init__(self, text: str) -> None:
        self.purpose = ""
        self.seam_terms: List[str] = []
        self.dependencies: List[str] = []
        leftover: List[str] = []
        for line in text.splitlines():
            if not self._take_bullet(line.strip()):
                leftover.append(line)
        self.leftover = "\n".join(leftover).strip()
        # A nested "### Module `path`" block often puts its purpose only in its prose.
        prose = [line.strip() for line in self.leftover.splitlines() if line.strip() and not line.strip().startswith("- **")]
        self.purpose = self.purpose or (prose[0] if prose else "")

    @staticmethod
    def terms(raw: str) -> List[str]:
        """The terms a bullet lists, separated by commas or semicolons, without their backticks and bold; none for
        `*(none)*`."""
        text = re.sub(r"^\*\(?none\)?\*$", "", raw.strip(), flags=re.IGNORECASE).strip()
        if text.lower() in {"*(none)*", "(none)", "none", "-"}:
            return []
        found = (re.sub(r"^\*\*?|\*\*?$", "", part.strip().strip("`").strip()).strip() for part in re.split(r"[,;]", text))
        return [term for term in found if term]

    def _take_bullet(self, stripped: str) -> bool:
        """Keep the bullet this line is; true when the line is a bullet or framing, false for prose."""
        purpose, seam, dependencies = (pattern.match(stripped) for pattern in (self._PURPOSE, self._SEAM, self._DEPENDENCIES))
        if purpose:
            self.purpose = purpose.group(1).strip()
        elif seam:
            self.seam_terms = self.terms(seam.group(1))
        elif dependencies:
            self.dependencies = self.terms(dependencies.group(1))
        return bool(purpose or seam or dependencies or self._FRAMING.match(stripped))


class CardDocument:
    """A model document of bold class cards under modules and resource groups, each one level deeper (`#` title, `##`
    module, `###` group, `####` card), as it was read: its lines in place, with each module where it stood, so the
    model writes it back as it was. A module is a heading at the module level with a card under it."""

    def __init__(self, model: "MarkdownCleanEngineeringModel", card_level: int) -> None:
        self._model = model
        self._card_level = card_level
        self._module_level = card_level - 2
        self._parts: list = []
        # The document's lines, the level of each heading by its line, and the module headings with a card under them.
        self._lines: List[str] = []
        self._heading_at: dict = {}
        self._starts: set = set()
        # The module and the card the reading is in.
        self._module: Optional[MarkdownModule] = None
        self._card: List[str] = []

    def read(self, text: str, headings: List[tuple]) -> None:
        """Read the document's modules and cards; every other line stays where it was written."""
        self._lines = text.splitlines(keepends=True)
        self._heading_at = {index: level for index, level, _raw in headings}
        self._starts = self._module_starts(headings)
        for index, line in enumerate(self._lines):
            self._take(index, line)
        self._close()

    def _take(self, index: int, line: str) -> None:
        level = self._heading_at.get(index)
        if level is not None and level <= self._module_level:
            self._close()
            self._module = self._module_at(index) if index in self._starts else None
            if self._module is None:
                self._parts.append(line)
        elif level is not None and self._module is not None and level <= self._card_level:
            self._close()
            self._open_card(level, line)
        else:
            self._keep(line)

    def _open_card(self, level: int, line: str) -> None:
        """A heading inside a module: a bold card at the card level opens a card; any other stays in the module."""
        if level == self._card_level and _CARD_HEADING.match(line):
            self._card.append(line)
        else:
            self._module.add_line(line)

    def _keep(self, line: str) -> None:
        """A line that is no heading: part of the card the reading is in, else of its module, else of the document."""
        if self._card:
            self._card.append(line)
        else:
            (self._module.add_line if self._module is not None else self._parts.append)(line)

    def render(self) -> str:
        """The document as it was read, each module written in place, then any module it did not have."""
        out: List[str] = []
        written = []
        for part in self._parts:
            if isinstance(part, str):
                out.append(part)
            elif any(module is part for module in self._model.modules):
                out.append(part.render_cards(self._module_level, self._card_level))
                written.append(part)
        for module in self._model.modules:
            if not any(module is done for done in written):
                out.append(module.render_cards(self._module_level, self._card_level))
        return "".join(out)

    def _module_at(self, index: int) -> MarkdownModule:
        """The module whose heading is the line at index, with the preamble under its heading."""
        heading = self._lines[index]
        module = MarkdownModule(name=_HEADING.match(heading).group(2), sequential_order=len(self._model.modules) + 1)
        module.start_card(heading)
        self._model.modules.append(module)
        self._parts.append(module)
        end = next((later for later in sorted(self._heading_at) if later > index), len(self._lines))
        module.take_preamble("".join(self._lines[index + 1:end]).strip())
        return module

    def _close(self) -> None:
        """End the card the reading is in, giving it to its module."""
        if self._card and self._module is not None:
            self._module.add_card("".join(self._card))
        self._card = []

    def _module_starts(self, headings: List[tuple]) -> set:
        starts = set()
        current = None
        for index, level, raw in headings:
            if level <= self._module_level:
                current = index if level == self._module_level else None
            elif current is not None and level == self._card_level and _CARD_HEADING.match(raw):
                starts.add(current)
        return starts


class MarkdownCleanEngineeringModel(CleanEngineeringModel):
    module_type = MarkdownModule

    def __init__(self, name: str = "", sequential_order: int = 1, graph=None) -> None:
        super().__init__(name, sequential_order, graph)
        # The card document it was read from; none for a plain model document.
        self._cards: Optional[CardDocument] = None

    def parse(self, text: str) -> "MarkdownCleanEngineeringModel":
        headings = self._headings(text)
        card_levels = [level for _index, level, raw in headings if _CARD_HEADING.match(raw)]
        self.modules = []
        self._cards = None
        if card_levels and min(card_levels) - 2 >= 2:
            self._cards = CardDocument(self, min(card_levels))
            self._cards.read(text, headings)
            return self
        for block in re.split(r"(?m)^(?=#\s)", text):
            heading = re.match(r"^#\s+(.+)", block.strip())
            if heading is None:
                continue
            module = MarkdownModule(name=heading.group(1).strip(), sequential_order=len(self.modules) + 1)
            module.read_body(block.strip()[heading.end():].lstrip("\n"))
            self.modules.append(module)
        return self

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

    def render(self, canonical: Optional[CleanEngineeringModel] = None) -> str:
        """Write this model; handed another model, a markdown one writes itself and any other is translated in first."""
        if canonical is not None and canonical is not self:
            if isinstance(canonical, MarkdownCleanEngineeringModel):
                return canonical.render()
            self.translate_from(canonical)
        if self._cards is not None:
            return self._cards.render()
        return "\n".join(module.render() for module in self.modules)
