"""Assemble agent instructions from @markdown properties."""
from __future__ import annotations

import inspect
import re
from pathlib import Path
from typing import Any

from context_tools.agent_toolset.scan import RulesCollection, Scan
from primitives.markdown import Markdown, markdown


def format_rules(rules: RulesCollection | str | None) -> str:
    if rules is None:
        return ""
    if isinstance(rules, str):
        return rules.strip()
    return rules.formatted()


class ContextGuidance:
    default_format: str = ""
    name: str | None = None
    domain_slug: str | None = None
    _guidance_file: str = "skill"

    def __init__(
        self,
        format: str | None = None,
        path: str | None = None,
        session: str | None = None,
        workspace: Any = None,
    ) -> None:
        self.format = format if format is not None else self.default_format
        self.path = path
        self.session = session
        self.workspace = workspace
        self.scanner = Scan.bound_to(self)

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        g = getattr(cls, "guidance", None)
        fget = getattr(g, "fget", None)
        if fget is not None:
            fget._is_agent_instructions = True
            if getattr(cls, "publish_mcp", False):
                fget._mcp = True
        r = getattr(cls, "rules", None)
        rfget = getattr(r, "fget", None)
        if rfget is not None:
            rfget._rules = True

    @markdown("contexts")
    def context(self) -> str:
        """Contexts preamble for this host scope."""

    @markdown
    def guidance(self) -> str:
        """Guidance section body."""

    @markdown("shared rules")
    def rules(self) -> RulesCollection:
        """Shared rules as a collection."""

    @markdown
    def templates(self) -> dict[str, str]:
        """Format key to relative path under templates/."""

    def _template_text(self) -> str:
        mapping = self.templates
        if not mapping:
            return ""
        key = self.format or self.default_format
        if not key:
            return ""
        rel = mapping.get(key)
        if not rel:
            return ""
        class_dir = Path(inspect.getfile(type(self))).resolve().parent
        path = class_dir / rel
        if path.is_file():
            return path.read_text(encoding="utf-8").strip()
        return ""

    @property
    def instructions(self) -> str:
        parts = [
            (self.context or "").strip(),
            (self.guidance or "").strip(),
            format_rules(self.rules),
            self._template_text(),
        ]
        return "\n\n".join(part for part in parts if part)

    def guidance_text(self) -> str:
        return self.instructions


def _h2_blocks(text: str) -> list[tuple[str, str]]:
    pattern = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
    matches = list(pattern.finditer(text))
    blocks: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        blocks.append((match.group(1).strip(), text[match.end() : end].strip()))
    return blocks


def _h3_named(text: str, heading: str) -> str:
    pattern = re.compile(rf"^###\s+{re.escape(heading)}\s*$", re.MULTILINE | re.IGNORECASE)
    match = pattern.search(text)
    if not match:
        return ""
    rest = text[match.end() :]
    next_h = re.search(r"^###\s+\S", rest, re.MULTILINE)
    chunk = rest[: next_h.start()] if next_h else rest
    return chunk.strip()


def parse_fidelity_blocks(text: str) -> list[tuple[str, str]]:
    marker = re.search(r"^##\s+Fidelities\s*$", text, re.MULTILINE | re.IGNORECASE)
    if not marker:
        return []
    tail = text[marker.end() :]
    if not re.search(r"^##\s+", tail, re.MULTILINE):
        return []
    return [
        (name, body)
        for name, body in _h2_blocks(tail)
        if name.casefold() != "fidelities"
    ]


class GuidanceCollection(ContextGuidance):
    def __init__(self, entries: dict[str, ContextGuidance] | None = None) -> None:
        super().__init__()
        self.entries: dict[str, ContextGuidance] = dict(entries or {})

    def __iter__(self):
        return iter(self.entries.values())

    @property
    def context(self) -> str:  # type: ignore[override]
        return "\n\n".join(child.context for child in self if child.context)

    @property
    def guidance(self) -> str:  # type: ignore[override]
        return "\n\n".join(child.guidance for child in self if child.guidance)

    @property
    def rules(self) -> RulesCollection:  # type: ignore[override]
        return RulesCollection({key: child.rules for key, child in self.entries.items()})

    @property
    def templates(self) -> dict[str, str]:  # type: ignore[override]
        merged: dict[str, str] = {}
        for child in self:
            merged.update(child.templates or {})
        return merged

    @property
    def instructions(self) -> str:
        return "\n\n".join(child.instructions for child in self if child.instructions)


class PracticeGuidance(ContextGuidance):
    def __init__(
        self,
        format: str | None = None,
        path: str | None = None,
        session: str | None = None,
        workspace: Any = None,
    ) -> None:
        super().__init__(format=format, path=path, session=session, workspace=workspace)
        self.fidelities = GuidanceCollection()
        self.fidelity: str | None = None
        class_dir = Path(inspect.getfile(type(self))).resolve().parent
        for rule in self.rules:
            rule.bind_scanner(class_dir)

    @property
    def rules(self) -> RulesCollection:  # type: ignore[override]
        text = Markdown.from_label(self, "shared rules").extract()
        collection = RulesCollection.from_markdown(text)
        class_dir = Path(inspect.getfile(type(self))).resolve().parent
        for rule in collection:
            rule.bind_scanner(class_dir)
        return collection

    @markdown
    def examples(self) -> str:
        """Examples folder content — not part of instructions."""

    @property
    def instructions(self) -> str:
        base = ContextGuidance.instructions.fget(self)  # type: ignore[misc]
        extra = self.fidelities.instructions if self.fidelities.entries else ""
        return "\n\n".join(part for part in (base, extra) if part)

    def attach_fidelities(self, entries: dict[str, ContextGuidance]) -> None:
        self.fidelities = GuidanceCollection(entries)

    def load_fidelities_from_markdown(self) -> None:
        class_dir = Path(inspect.getfile(type(self))).resolve().parent
        slug = self.domain_slug or class_dir.name
        md_path = class_dir / f"{slug}.md"
        if not md_path.is_file():
            return
        text = md_path.read_text(encoding="utf-8")
        blocks = parse_fidelity_blocks(text)
        entries: dict[str, ContextGuidance] = {}
        prior: list[tuple[str, str]] = []
        for name, body in blocks:
            child = FidelityGuidance(
                name=name,
                practice_guidance=self,
                default_format=self.default_format,
            )
            child.domain_slug = self.domain_slug
            child._block = body
            child._prior = list(prior)
            entries[name] = child
            prior.append((name, body))
        self.attach_fidelities(entries)
        if self.fidelity and self.fidelity in entries:
            child = entries[self.fidelity]
            self.format = child.default_format or self.format


class FidelityGuidance(ContextGuidance):
    _guidance_file = "command"

    def __init__(
        self,
        name: str,
        stage: str = "",
        default_format: str = "",
        practice_guidance: PracticeGuidance | None = None,
    ) -> None:
        super().__init__(format=default_format)
        self.name = name
        self.stage = stage
        self.default_format = default_format
        self.practice_guidance = practice_guidance
        self.fidelity = name
        if practice_guidance is not None and self.domain_slug is None:
            self.domain_slug = practice_guidance.domain_slug
        self._block = ""
        self._prior: list[tuple[str, str]] = []

    @property
    def context(self) -> str:  # type: ignore[override]
        parts = [body for _name, body in self._prior]
        return "\n\n".join(parts)

    @property
    def guidance(self) -> str:  # type: ignore[override]
        named = _h3_named(self._block, "Guidance")
        return named or self._block

    @property
    def rules(self) -> RulesCollection:  # type: ignore[override]
        text = _h3_named(self._block, "Rules")
        return RulesCollection.from_markdown(text, fidelity=self.name)

    @property
    def templates(self) -> dict[str, str]:  # type: ignore[override]
        mapping = dict(super().templates or {})
        return {key: rel for key, rel in mapping.items() if self.name.replace(" ", "_") in key or True}

    @property
    def instructions(self) -> str:
        parts = [
            self.context.strip(),
            self.guidance.strip(),
            format_rules(self.rules),
            self._template_text(),
        ]
        return "\n\n".join(part for part in parts if part)

