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
from harness.markdown.markdown import MarkdownCollection, MarkdownText, Owner
from harness.hooks.hooks import Hook, hook

if TYPE_CHECKING:
    from harness.guidance.guidance import PracticeGuidance
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
    def from_value(cls, fence_fields: AppliesTo | dict[str, object] | None) -> AppliesTo:
        """Where rules apply as the fields of their ```yaml fence say it: ``alwaysApply`` and ``globs``."""
        if isinstance(fence_fields, cls):
            return fence_fields
        if not isinstance(fence_fields, dict):
            return cls()
        always = fence_fields.get("alwaysApply", fence_fields.get("always_apply"))
        globs: object = fence_fields.get("globs", "")
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
    def __init__(self, slug: str, body: str, fidelity: str | None = None) -> None:
        self._slug = slug
        self._body = body
        self.fidelity = fidelity
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
    def _from_bullet(cls, text: str, fidelity: str | None = None) -> Rule:
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
class RulesCollection(MarkdownCollection[Owner]):
    def __init__(
        self,
        entries: dict[str, Rule | RulesCollection] | None = None,
        applies_to: AppliesTo | None = None,
        parent: Owner | None = None,
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
    def inject_rules(self, tool_use: HookPayload) -> dict[str, Any]:
        """The rules that apply to the file the agent just edited, as context for its next step. The session notes
        them even while the hook is turned off, so its log still names the rules each edit was checked against."""
        return self.injection.after_edit(tool_use)

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
    def owner_practice(self) -> PracticeGuidance | None:
        """The practice these rules belong to: the one that holds them or the fidelity that holds them; none for rules
        no practice holds."""
        node = self.parent
        if node is None:
            return None
        return self._practice_on(node) or self._practice_on(getattr(node, "parent", None))

    def _practice_on(self, node: Owner | None) -> PracticeGuidance | None:
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
        parent: Owner | None = None,
    ) -> RulesCollection:
        applies_to = AppliesTo.from_markdown(text)
        entries: dict[str, Rule | RulesCollection] = {}
        for raw in MarkdownText(text).without_yaml.splitlines():
            stripped = raw.strip()
            if not re.match(r"^[-*]\s+", stripped):
                continue
            rule = Rule._from_bullet(stripped, fidelity=fidelity)
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


class RuleInjection:
    """How one collection of rules is handed to the agent after it edits a file: the rules of its practice that apply
    to the edited file, with the shared rules and those of every fidelity before the ones that matched, noted in the
    session's log, and the toast that says whose rules were injected. The collection holds one, made once."""

    def __init__(self, rules: RulesCollection, practice: PracticeGuidance | None) -> None:
        self._rules = rules
        # The practice the rules belong to, whose shared rules and fidelities' rules an edit is checked against; none
        # for rules no practice holds.
        self._practice = practice

    def after_edit(self, tool_use: HookPayload) -> dict[str, Any]:
        """The rules that apply to the file tool_use edits, as context for the agent's next step; nothing while the
        hook is disabled, though the session still notes which rules applied."""
        path = tool_use.edited_path() if tool_use.is_edit else ""
        collections = self._collections_for_path(path) if path else []
        if collections:
            self._note_session_injected_rules(tool_use, path, collections)
        parts = self._bodies(collections)
        if Hook.disabled_on(type(self._rules).inject_rules) or not parts:
            return {}
        body = self._inject_context(path, collections, parts)
        notice = self._read_only_notice(collections)
        if notice and (tool_use.get("conversation_id") or tool_use.get("workspace_roots")):
            return {"additional_context": body, "toast": notice}
        return {"additional_context": body}

    def _note_session_injected_rules(self, tool_use: HookPayload, path: str, collections: list[RulesCollection]) -> None:
        """Note collections in the log of the session open in the project the hook fired in, so that session's next log line
        names the rules the agent was given; nothing for a hook that names no project."""
        practice = self._practice
        if practice is None:
            return
        session = practice.session if practice.session is not None else tool_use.session
        if session is None:
            return
        for collection in collections:
            session.log.injected_rules.note(collection, path)

    def _rule_collections(self) -> list[RulesCollection]:
        practice = self._practice
        if practice is None:
            return [self._rules]
        collections = [practice.rules, *(fidelity.rules for fidelity in practice.fidelities)]
        return [collection for collection in collections if isinstance(collection, RulesCollection)]

    def _collections_for_path(self, path: str) -> list[RulesCollection]:
        collections = self._rule_collections()
        matched = [collection for collection in collections if collection.applies_to.matches(path)]
        if not matched:
            return []
        return self._unique_collections(self._matched_and_shared(collections, matched) + self._upstream_of(matched))

    def _matched_and_shared(
        self, collections: list[RulesCollection], matched: list[RulesCollection]
    ) -> list[RulesCollection]:
        return [collection for collection in collections if collection in matched or not collection.applies_to.patterns]

    def _unique_collections(self, collections: list[RulesCollection]) -> list[RulesCollection]:
        included: list[RulesCollection] = []
        seen: set[int] = set()
        for collection in collections:
            key = id(collection)
            if key in seen:
                continue
            seen.add(key)
            included.append(collection)
        return included

    def _upstream_of(self, matched: list[RulesCollection]) -> list[RulesCollection]:
        practice = self._practice
        if practice is None:
            return []
        fidelities = practice.fidelities
        names = list(fidelities.entries)
        indexes = []
        for collection in matched:
            name = getattr(collection.parent, "name", None)
            if name in names:
                indexes.append(names.index(name))
        if not indexes:
            return []
        last = max(indexes)
        return [fidelities[name].rules for name in names[:last]]

    def _bodies(self, collections: list[RulesCollection]) -> list[str]:
        return [body for collection in collections if (body := (collection.markdown or "").strip())]

    def _matched_globs(self, collections: list[RulesCollection]) -> list[str]:
        return list(dict.fromkeys(pattern for collection in collections for pattern in collection.applies_to.patterns))

    def _inject_echo_instruction(self, path: str, collections: list[RulesCollection]) -> str:
        """What tells the agent it just edited path and is to fix what the rules after it find; rules reach it only
        after an edit, so there is always one to name."""
        lines = [
            f"You just edited {self._edited_label(path)}.",
            "The full rule text follows.",
            "Fix any violations from the edit you just made.",
        ]
        for pattern in self._matched_globs(collections):
            lines.append(pattern)
        return "\n".join(lines)

    def _read_only_notice(self, collections: list[RulesCollection]) -> str:
        return "\n".join(self._chat_lines(collections))

    def _chat_lines(self, collections: list[RulesCollection]) -> list[str]:
        practice = self._practice
        lines: list[str] = []
        for collection in collections:
            parent = collection.parent
            if parent is None or parent is practice:
                continue
            skill = getattr(parent, "slug", None)
            if isinstance(skill, str) and skill.strip():
                line = f"rules injected for {skill.strip()}"
                if line not in lines:
                    lines.append(line)
        if lines:
            return lines
        if practice is not None and practice.slug.strip():
            return [f"rules injected for {practice.slug.strip()}"]
        return ["rules injected"]

    def _edited_label(self, path: str) -> str:
        file = Path(path)
        parent = file.parent.name
        if not parent:
            return file.name
        sep = "\\" if "\\" in path else "/"
        return f"{parent}{sep}{file.name}"

    def _inject_context(self, path: str, collections: list[RulesCollection], parts: list[str]) -> str:
        preamble = self._inject_echo_instruction(path, collections).strip()
        rules = "\n\n".join(parts).strip()
        if preamble and rules:
            return f"{preamble}\n\n{rules}"
        return preamble or rules

