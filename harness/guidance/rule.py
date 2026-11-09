"""Honor each rule against the current context."""
from __future__ import annotations

import fnmatch
import re
import functools
from pathlib import Path
from typing import TYPE_CHECKING, Any, Iterator

from harness.agent_tools.agent_tools import (
    agent_instructions,
    collect,
    agent_toolset,
    instructions,
    published_where_held,
)
from harness.annotations.annotation import hosted_only
from harness.annotations.name import Name
from harness.installation.data_class import data_field
from harness.markdown.markdown import MarkdownCollection, MarkdownText
from harness.hooks.hooks import Hook, hook

if TYPE_CHECKING:
    from harness.hooks.hook_server import HookPayload

class AppliesTo:
    """Which edited files a rules section applies to, as the YAML fence in the practice markdown says: every file
    (``alwaysApply``), or the files a comma-separated list of glob patterns matches."""

    def __init__(self, always_apply: bool | None = None, globs: str = "") -> None:
        self.always_apply = always_apply
        self.globs = globs

    @property
    def patterns(self) -> list[str]:
        """Each glob pattern, without the quotes a fence may write around it."""
        return [pattern for part in str(self.globs or "").split(",") if (pattern := part.strip().strip("\"'"))]

    def matches(self, path: str) -> bool:
        """True when the rules apply to the edited file at path: every file for rules that always apply and name no
        pattern, else a file one of the patterns matches."""
        if not path:
            return False
        if self.always_apply and not self.patterns:
            return True
        posix = Path(path).as_posix()
        return any(self._pattern_matches(posix, Path(path).name, pattern) for pattern in self.patterns)

    def _pattern_matches(self, posix: str, name: str, pattern: str) -> bool:
        if Path(posix).match(pattern) or fnmatch.fnmatch(posix, pattern):
            return True
        # Path-scoped patterns must match the full path — not the filename alone.
        if "/" in pattern or pattern in {"*", "**"}:
            return False
        return fnmatch.fnmatch(name, pattern)

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
        return cls.from_value(MarkdownText(text).yaml_fields)


class Rule:
    def __init__(
        self,
        slug: str,
        body: str,
        fidelity: str | None = None,
        tag: str = "base",
    ) -> None:
        self._slug = slug
        self._body = body
        self.fidelity = fidelity
        self.tag = tag or "base"
        self.practice = ""
        self.pattern = ""
        self.shared = False

    @property
    @data_field
    def slug(self) -> str:
        """The rule's name, such as `hide-inner-details`."""
        return self._slug

    @property
    @data_field
    def body(self) -> str:
        """What the rule asks for, as its markdown says it."""
        return self._body

    def validate(self) -> str:
        return instructions(
            f"### `{self.slug}`",
            self.body,
            f"Evaluate the current context against this rule ({self.slug}):",
        )

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
            slug = Name(body).title_slug or "rule"
        return cls(slug=slug, body=body, fidelity=fidelity)


@hosted_only
@agent_toolset
class RulesCollection(MarkdownCollection):
    def __init__(
        self,
        entries: dict[str, Rule | RulesCollection] | None = None,
        applies_to: AppliesTo | None = None,
        parent: Any = None,
    ) -> None:
        super().__init__(dict(entries or {}), parent=parent)
        self._applies_to = applies_to if applies_to is not None else AppliesTo()

    @property
    def applies_to(self) -> AppliesTo:
        """Which edited files these rules apply to."""
        return self._applies_to

    @property
    def prose(self) -> str:
        """The rules as an agent reads them and an installed rules file holds them: their markdown without its
        ```yaml settings, which say where they apply."""
        return MarkdownText(self.markdown or "").without_yaml

    @functools.cached_property
    def injection(self) -> RuleInjection:
        """How these rules are handed to the agent after it edits a file, made once."""
        return RuleInjection(self, self.owner_practice)

    @published_where_held
    @hook("postToolUse", disabled=True)
    def inject_rules(self, payload: HookPayload) -> dict[str, Any]:
        """The rules that apply to the file the agent just edited, as context for its next step. The session notes
        them even while the hook is turned off, so its log still names the rules each edit was checked against."""
        return self.injection.after_edit(payload)

    @property
    def practice_key(self) -> str:
        """The folder name of the practice these rules belong to, such as `bdd`, as session log lines name it; empty
        when the rules belong to no practice."""
        practice = self.owner_practice
        return str(getattr(practice, "key", "") or "") if practice is not None else ""

    @property
    def fidelity_name(self) -> str:
        """The fidelity these rules belong to, such as `development`. A practice's shared rules belong to the fidelity
        the practice is working at, so a log line names where the edit was checked."""
        parent = self.parent
        if parent is None or parent is self.owner_practice:
            current = getattr(getattr(parent, "fidelities", None), "current", None)
            return str(getattr(current, "name", "") or "")
        return str(getattr(parent, "name", "") or "")

    @property
    def owner_practice(self) -> Any:
        """The practice these rules belong to: the one that holds them or the fidelity that holds them; none for rules
        no practice holds."""
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

    @classmethod
    def from_markdown(
        cls,
        text: str,
        fidelity: str | None = None,
        parent: Any = None,
    ) -> RulesCollection:
        applies_to = AppliesTo.from_markdown(text)
        entries: dict[str, Rule | RulesCollection] = {}
        for raw in MarkdownText(text).without_yaml.splitlines():
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

    @collect
    def validate(self) -> str: ...

    def scan(self, paths: Any) -> Any:
        return None


class RuleInjection:
    """How one collection of rules is handed to the agent after it edits a file: the rules of its practice that apply
    to the edited file, with the shared rules and those of every fidelity before the ones that matched, noted in the
    session's log, and the toast that says whose rules were injected. The collection holds one, made once."""

    def __init__(self, rules: RulesCollection, practice: Any) -> None:
        self._rules = rules
        # The practice the rules belong to, whose shared rules and fidelities' rules an edit is checked against; none
        # for rules no practice holds.
        self._practice = practice

    def after_edit(self, payload: HookPayload) -> dict[str, Any]:
        """The rules that apply to the file payload's edit names, as context for the agent's next step; nothing while
        the hook is disabled, though the session still notes which rules applied."""
        path = payload.edited_path() if payload.is_edit else ""
        bags = self._bags_for_path(path) if path else []
        if bags:
            self._note_session_injected_rules(payload, path, bags)
        parts = self._bodies(bags)
        if Hook.disabled_on(type(self._rules).inject_rules) or not parts:
            return {}
        body = self._inject_context(path, bags, parts, payload)
        notice = self._read_only_notice(bags)
        if notice and (payload.get("conversation_id") or payload.get("workspace_roots")):
            return {"additional_context": body, "toast": notice}
        return {"additional_context": body}

    def _note_session_injected_rules(self, payload: HookPayload, path: str, bags: list[RulesCollection]) -> None:
        """Note bags in the log of the session open in the project the hook fired in, so that session's next log line
        names the rules the agent was given; nothing for a hook that names no project."""
        practice = self._practice
        if practice is None:
            return
        session = practice.session if practice.session is not None else payload.session
        if session is None:
            return
        for bag in bags:
            session.log.injected_rules.note(bag, path)

    def _rule_bags(self) -> list[RulesCollection]:
        practice = self._practice
        if practice is None:
            return [self._rules]
        bags: list[RulesCollection] = []
        shared = getattr(practice, "rules", None)
        if isinstance(shared, RulesCollection):
            bags.append(shared)
        fidelities = getattr(practice, "fidelities", None)
        if fidelities is None:
            return bags or [self._rules]
        for child in fidelities:
            child_rules = getattr(child, "rules", None)
            if isinstance(child_rules, RulesCollection):
                bags.append(child_rules)
        return bags

    def _bags_for_path(self, path: str) -> list[RulesCollection]:
        bags = self._rule_bags()
        matched = [bag for bag in bags if bag.applies_to.matches(path)]
        if not matched:
            return []
        return self._unique_bags(self._matched_and_shared(bags, matched) + self._upstream_of(matched))

    def _matched_and_shared(
        self, bags: list[RulesCollection], matched: list[RulesCollection]
    ) -> list[RulesCollection]:
        return [bag for bag in bags if bag in matched or not bag.applies_to.patterns]

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
        practice = self._practice
        fidelities = getattr(practice, "fidelities", None) if practice is not None else None
        names = list(getattr(fidelities, "entries", {}) or {})
        if not names:
            return []
        indexes = []
        for bag in matched:
            name = getattr(bag.parent, "name", None)
            if name in getattr(fidelities, "entries", {}):
                indexes.append(names.index(name))
        if not indexes:
            return []
        last = max(indexes)
        return [fidelities[name].rules for name in names[:last]]

    def _bodies(self, bags: list[RulesCollection]) -> list[str]:
        return [body for bag in bags if (body := (bag.markdown or "").strip())]

    def _matched_globs(self, bags: list[RulesCollection]) -> list[str]:
        return list(dict.fromkeys(pattern for bag in bags for pattern in bag.applies_to.patterns))

    def _inject_echo_instruction(self, path: str, bags: list[RulesCollection], hook_payload: HookPayload | None = None) -> str:
        if hook_payload is None or not hook_payload.is_edit:
            return ""
        lines = [
            f"You just edited {self._edited_label(path)}.",
            "The full rule text follows.",
            "Fix any violations from the edit you just made.",
        ]
        for pattern in self._matched_globs(bags):
            lines.append(pattern)
        return "\n".join(lines)

    def _read_only_notice(self, bags: list[RulesCollection]) -> str:
        return "\n".join(self._chat_lines(bags))

    def _chat_lines(self, bags: list[RulesCollection]) -> list[str]:
        practice = self._practice
        lines: list[str] = []
        for bag in bags:
            parent = bag.parent
            if parent is None or parent is practice:
                continue
            skill = getattr(parent, "slug", None)
            if isinstance(skill, str) and skill.strip():
                line = f"rules injected for {skill.strip()}"
                if line not in lines:
                    lines.append(line)
        if lines:
            return lines
        if practice is not None:
            slug = getattr(practice, "slug", None)
            if isinstance(slug, str) and slug.strip():
                return [f"rules injected for {slug.strip()}"]
        return ["rules injected"]

    def _edited_label(self, path: str) -> str:
        file = Path(path)
        parent = file.parent.name
        if not parent:
            return file.name
        sep = "\\" if "\\" in path else "/"
        return f"{parent}{sep}{file.name}"

    def _inject_context(
        self, path: str, bags: list[RulesCollection], parts: list[str], hook_payload: HookPayload | None = None
    ) -> str:
        preamble = self._inject_echo_instruction(path, bags, hook_payload).strip()
        rules = "\n\n".join(parts).strip()
        if preamble and rules:
            return f"{preamble}\n\n{rules}"
        return preamble or rules

