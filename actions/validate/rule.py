"""Honor each rule against the current context."""
from __future__ import annotations

import fnmatch
import json
import re
from pathlib import Path
from typing import Any, Iterator

from harness.agent_tools.agent_tools import collect, agent_toolset, instructions, tools
from harness.markdown.markdown import MarkdownCollection
from harness.hooks.hooks import Hook
from prompt_echo.prompt_echo import echo

from actions.scan.scanner import Scanner

class AppliesTo:
    """Cursor attach data for a rules section — owned in the practice markdown fence."""

    def __init__(self, always_apply: bool | None = None, globs: str = "") -> None:
        self.always_apply = always_apply
        self.globs = globs

    @property
    def alwaysApply(self) -> bool | None:
        return self.always_apply

    @classmethod
    def from_value(cls, value: Any) -> AppliesTo:
        if isinstance(value, cls):
            return value
        if not isinstance(value, dict):
            return cls()
        always = value.get("alwaysApply", value.get("always_apply"))
        globs: Any = value.get("globs", "")
        if not isinstance(globs, str):
            globs = "" if globs is None else str(globs)
        always_apply = None
        if isinstance(always, bool):
            always_apply = always
        elif always not in (None, ""):
            always_apply = str(always).casefold() in {"true", "yes", "1"}
        return cls(always_apply=always_apply, globs=globs)

    @classmethod
    def from_markdown(cls, text: str) -> AppliesTo:
        from harness.markdown.markdown import yaml_fields

        return cls.from_value(yaml_fields(text))

    @classmethod
    def strip_fence(cls, text: str) -> str:
        from harness.markdown.markdown import strip_yaml_fences

        return strip_yaml_fences(text)


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
            self.scanner = Scanner(self.slug)

    def validate(self) -> str:
        text = instructions(
            f"Evaluate the current context against this rule ({self.slug}):",
            self.body,
        )
        if self.scanner is not None:
            tools(self.scanner.scan)
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


@agent_toolset
class RulesCollection(MarkdownCollection):
    def __init__(
        self,
        entries: dict[str, Rule | RulesCollection] | None = None,
        applies_to: AppliesTo | None = None,
        parent: Any = None,
    ) -> None:
        super().__init__(dict(entries or {}), parent=parent)
        applies = applies_to if applies_to is not None else AppliesTo()
        self.always_apply = applies.always_apply
        self.glob = applies.globs

    @property
    def appliesTo(self) -> AppliesTo:
        return AppliesTo(always_apply=self.always_apply, globs=self.glob)

    @echo
    @Hook("postToolUse")
    def inject_rules(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        from prompt_echo.prompt_echo import PromptEcho

        data = payload or {}
        path = self._payload_path(data)
        bags = self._bags_for_path(path) if path else []
        parts, labels = self._bodies(bags)
        if not parts:
            return {}
        body = "\n\n".join(parts)
        PromptEcho().show_ide_toast(
            PromptEcho().inject_rules_toast("chat edit", labels),
            roots=data.get("workspace_roots"),
        )
        return {"additional_context": body}

    def _payload_path(self, data: dict[str, Any]) -> str:
        raw = data.get("tool_input") or {}
        if isinstance(raw, str):
            try:
                raw = json.loads(raw)
            except json.JSONDecodeError:
                return ""
        if not isinstance(raw, dict):
            return ""
        return str(raw.get("path") or raw.get("file_path") or raw.get("target_notebook") or "")

    def _owner_practice(self) -> Any:
        node = self.parent
        if node is None:
            return None
        return self._practice_on(node) or self._practice_on(getattr(node, "parent", None))

    def _practice_on(self, node: Any) -> Any:
        if node is None:
            return None
        practice = getattr(node, "practice_guidance", None)
        if practice is not None:
            return practice
        if getattr(node, "fidelities", None) is not None:
            return node
        return None

    def _rule_bags(self) -> list[RulesCollection]:
        practice = self._owner_practice()
        if practice is None:
            return [self]
        bags: list[RulesCollection] = []
        shared = getattr(practice, "rules", None)
        if isinstance(shared, RulesCollection):
            bags.append(shared)
        fidelities = getattr(practice, "fidelities", None)
        if fidelities is None:
            return bags or [self]
        for child in fidelities:
            child_rules = getattr(child, "rules", None)
            if isinstance(child_rules, RulesCollection):
                bags.append(child_rules)
        return bags

    def _bags_for_path(self, path: str) -> list[RulesCollection]:
        bags = self._rule_bags()
        matched = [bag for bag in bags if bag.matches(path)]
        if not matched:
            return []
        return self._unique_bags(self._matched_and_shared(bags, matched) + self._upstream_of(matched))

    def _matched_and_shared(
        self, bags: list[RulesCollection], matched: list[RulesCollection]
    ) -> list[RulesCollection]:
        return [bag for bag in bags if bag in matched or not str(bag.glob or "").strip()]

    def _unique_bags(self, bags: list[RulesCollection]) -> list[RulesCollection]:
        included: list[RulesCollection] = []
        seen: set[int] = set()
        for bag in bags:
            key = id(bag)
            if key in seen:
                continue
            seen.add(key)
            included.append(bag)
        return included

    def _upstream_of(self, matched: list[RulesCollection]) -> list[RulesCollection]:
        practice = self._owner_practice()
        fidelities = getattr(practice, "fidelities", None) if practice is not None else None
        names = list(getattr(fidelities, "entries", {}) or {})
        if not names:
            return []
        indexes = []
        for bag in matched:
            name = getattr(bag.parent, "name", None) or getattr(bag.parent, "fidelity", None)
            if name in getattr(fidelities, "entries", {}):
                indexes.append(names.index(name))
        if not indexes:
            return []
        last = max(indexes)
        return [fidelities[name].rules for name in names[:last]]

    def _bodies(self, bags: list[RulesCollection]) -> tuple[list[str], list[str]]:
        parts: list[str] = []
        labels: list[str] = []
        for bag in bags:
            body = (bag.markdown or "").strip()
            if not body:
                continue
            parts.append(body)
            parent = bag.parent
            if parent is None:
                labels.append(type(bag).__name__)
            else:
                labels.append(getattr(parent, "name", None) or type(parent).__name__)
        return parts, labels

    def matches(self, path: str) -> bool:
        if not path:
            return False
        if self.always_apply and not str(self.glob or "").strip():
            return True
        if not self.glob:
            return False
        posix = Path(path).as_posix()
        name = Path(path).name
        for pattern in (part.strip().strip("\"'") for part in self.glob.split(",")):
            if self._pattern_matches(posix, name, pattern):
                return True
        return False

    def _pattern_matches(self, posix: str, name: str, pattern: str) -> bool:
        if not pattern:
            return False
        if Path(posix).match(pattern) or fnmatch.fnmatch(posix, pattern):
            return True
        leaf = pattern.rsplit("/", 1)[-1]
        if leaf in {"", "*", "**"}:
            return False
        return fnmatch.fnmatch(name, leaf)

    @classmethod
    def from_markdown(
        cls,
        text: str,
        fidelity: str | None = None,
        parent: Any = None,
    ) -> RulesCollection:
        applies_to = AppliesTo.from_markdown(text)
        entries: dict[str, Rule | RulesCollection] = {}
        for raw in AppliesTo.strip_fence(text).splitlines():
            stripped = raw.strip()
            if not re.match(r"^[-*]\s+", stripped):
                continue
            rule = Rule.from_bullet(stripped, fidelity=fidelity)
            entries[rule.slug] = rule
        collection = cls(entries, applies_to=applies_to, parent=parent)
        collection.markdown = text
        return collection

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

    def format_rules(self) -> str:
        return self.formatted()

    @collect
    def validate(self) -> str: ...

    def scan(self, paths: Any) -> Any:
        return None
