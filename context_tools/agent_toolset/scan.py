"""Honor each rule against the current context."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Iterator


class Scanner:
    def __init__(self, rule: Rule) -> None:
        self.rule = rule

    def scan(self, file_path: Path) -> list:
        return []


class Rule:
    def __init__(self, slug: str, body: str, fidelity: str | None = None) -> None:
        self.slug = slug
        self.body = body
        self.fidelity = fidelity
        self.scanner: Scanner | None = None

    def bind_scanner(self, module_dir: Path | None) -> None:
        if module_dir is None:
            return
        script = module_dir / "scanners" / f"{self.slug}_scanner.py"
        if script.is_file():
            self.scanner = Scanner(self)

    def validate(self) -> str:
        from primitives.agentic_toolset import instructions

        text = instructions(
            f"Evaluate the current context against this rule ({self.slug}):",
            self.body,
        )
        if self.scanner is not None:
            text = text + "\nRun the scanner for this rule."
        return text

    @classmethod
    def from_bullet(cls, text: str, fidelity: str | None = None) -> Rule:
        line = text.strip().lstrip("-*").strip()
        slug = ""
        body = line
        named = re.match(r"\*\*`?([^`*]+)`?\*\*\s*[—:-]\s*(.+)$", line)
        if named:
            slug = named.group(1).strip()
            body = named.group(2).strip()
        else:
            coded = re.match(r"`([^`]+)`\s*[—:-]\s*(.+)$", line)
            if coded:
                slug = coded.group(1).strip()
                body = coded.group(2).strip()
        if not slug:
            slug = re.sub(r"[^a-z0-9]+", "-", body.casefold()).strip("-") or "rule"
        return cls(slug=slug, body=body, fidelity=fidelity)


class RulesCollection:
    def __init__(self, entries: dict[str, Rule | RulesCollection] | None = None) -> None:
        self.entries: dict[str, Rule | RulesCollection] = dict(entries or {})

    @classmethod
    def from_markdown(cls, text: str, fidelity: str | None = None) -> RulesCollection:
        entries: dict[str, Rule | RulesCollection] = {}
        for raw in text.splitlines():
            stripped = raw.strip()
            if stripped.startswith(("-", "*")):
                rule = Rule.from_bullet(stripped, fidelity=fidelity)
                entries[rule.slug] = rule
        return cls(entries)

    def __iter__(self) -> Iterator[Rule]:
        for value in self.entries.values():
            if isinstance(value, RulesCollection):
                yield from value
            else:
                yield value

    def __getitem__(self, key: str) -> Rule | RulesCollection:
        return self.entries[key]

    def formatted(self) -> str:
        lines = []
        for rule in self:
            lines.append(f"- **{rule.slug}** — {rule.body}")
        return "\n".join(lines)

    def validate(self) -> str:
        parts = [child.validate() for child in self.entries.values()]
        return "\n\n".join(part for part in parts if part)

    def scan(self, paths: Any) -> Any:
        return None


class Scan:
    def __init__(self, host: Any) -> None:
        self.host = host

    @classmethod
    def bound_to(cls, host: Any) -> Scan:
        return cls(host)

    def scan(self, paths: Any) -> Any:
        rules = getattr(self.host, "rules", None)
        if rules is None:
            return None
        return rules.scan(paths)
