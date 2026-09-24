"""Workspace domain — work session guidance family at model fidelity."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from harness.guidance.rule import AppliesTo, Rule, RulesCollection
from git.git import GitConnectError, GitRepo, Repo
from harness.guidance.guidance import PracticeGuidance
from harness.markdown import markdownCollection
from harness.agent_tools.agent_tools import agent_tool, agent_toolset
from harness.mcp.mcp_server import Mcp


class TurnCommit:
    """Git commit produced by a turn — ``name`` is the commit subject line."""

    def __init__(
        self,
        name: str = "",
        branch: str = "",
        sha: str = "",
        context_tool: str = "",
        action: str = "",
        utility: str = "",
        subject: str = "",
    ) -> None:
        self.name = name
        self.branch = branch
        self.sha = sha
        self.context_tool = context_tool
        self.action = action
        self.utility = utility
        self.subject = subject

    @property
    def session_name(self) -> str:
        return self.branch


class WorkSession:
    """One named work session — owns guidance and announced turns."""

    # 1 WorkSession composes 1 WorkSessionGuidance
    # turn() never records correction or mistake
    # turn() force a commit

    def __init__(
        self,
        name: str,
        guidance: WorkSessionGuidance | None = None,
    ) -> None:
        # / create a new folder in .sessions/{name}
        self._name = name
        self._root = Repo(Path.cwd()).find_root()
        if self._root is None:
            raise GitConnectError("work session lives at the repository root")
        self.folder.mkdir(parents=True, exist_ok=True)
        self._guidance = guidance or WorkSessionGuidance(work_session=self)
        self._open_turn: Turn | None = None
        self._completed_turns: list[str] = []

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def folder(self) -> Path:
        return self._root / ".sessions" / self._name

    @property
    def guidance(self) -> WorkSessionGuidance:
        return self._guidance

    @property
    def open_turn(self) -> Turn | None:
        return self._open_turn

    @property
    def git(self) -> GitRepo:
        return GitRepo(self._root)

    @property
    def completed_turns(self) -> list[str]:
        return list(self._completed_turns)

    def turn(self) -> Turn:
        # /turn announces a new turn
        # increments turn age for inclusion and exclude
        # -> turn.turn
        self._open_turn = Turn(work_session=self)
        change = self._open_turn.turn()
        if change is not None:
            self._completed_turns.append(change.sha)
        return self._open_turn


class WorkSessionGuidance(PracticeGuidance):
    """Work guidelines file for a work session."""

    # rules section is a WorkSessionRulesCollection

    def __init__(self, work_session: WorkSession) -> None:
        self._work_session = work_session
        self.module_dir = work_session.folder

    def _guidelines_path(self) -> Path:
        return self._work_session.folder / "work-guidelines.md"

    @property
    def path(self) -> Path:
        return self._guidelines_path()

    @markdownCollection("work-guidelines")
    def rules(self) -> WorkSessionRulesCollection:
        """Work session rules from work-guidelines.md."""


class WorkSessionRulesCollection(RulesCollection):
    """Session rules: add, band, and inject by guidance and fidelity."""

    # changing inclusion, exclude, or detail leaves rules on the collection
    # the next inject_rules uses the new settings

    def __init__(
        self,
        entries: dict[str, Rule | RulesCollection] | None = None,
        applies_to: Any = None,
        parent: Any = None,
    ) -> None:
        super().__init__(entries, applies_to=applies_to, parent=parent)
        self.priority_inclusion = 1
        self.relevant_inclusion = 2
        self.context_inclusion = 3
        self.exclude = 5
        self.priority_detail = "examples"
        self.relevant_detail = "examples"
        self.context_detail = "slug"

    @classmethod
    def from_markdown(
        cls,
        text: str,
        fidelity: str | None = None,
        parent: Any = None,
    ) -> WorkSessionRulesCollection:
        applies_to = AppliesTo.from_markdown(text)
        entries: dict[str, Rule | RulesCollection] = {}
        current: WorkSessionRule | None = None
        for raw in AppliesTo.strip_fence(text).splitlines():
            stripped = raw.strip()
            if re.match(r"^[-*]\s+", stripped):
                rule = WorkSessionRule.from_bullet(stripped, fidelity=fidelity)
                entries[rule.slug] = rule
                current = rule
                continue
            if current is not None:
                current.apply_field(raw)
        collection = cls(entries, applies_to=applies_to, parent=parent)
        collection.markdown = text
        return collection

    def formatted(self) -> str:
        lines = ["#### Rules", ""]
        for rule in self:
            if isinstance(rule, WorkSessionRule):
                lines.extend(rule.to_markdown().splitlines())
            else:
                lines.append(f"- **{rule.slug}** — {rule.body}")
            lines.append("")
        return "\n".join(lines).rstrip() + "\n"

    def add(self, work_session_rule: WorkSessionRule) -> WorkSessionRule:
        # no matching base rule → insert new WorkSessionRule
        # matching base rule → add the example, star += 1, move up when highest star
        # guidance and fidelity may both be set, guidance only (practice-wide), or neither (global)
        # -> self._matching_work_session_rule
        # -> self._matching_practice_rule
        # -> self._place_by_star
        matching = self._matching_work_session_rule(work_session_rule)
        if matching is not None:
            for example in work_session_rule.examples:
                matching.examples.add(example)
            matching.star += 1
            matching.last_fail = 1
            self._place_by_star(matching)
            self._write()
            return matching
        self._apply_practice_rule(work_session_rule)
        if work_session_rule.star == 0:
            work_session_rule.star = 1
        work_session_rule.last_fail = 1
        self.entries[work_session_rule.slug] = work_session_rule
        self._place_by_star(work_session_rule)
        self._write()
        return work_session_rule

    def _apply_practice_rule(self, work_session_rule: WorkSessionRule) -> None:
        practice_rule = self._matching_practice_rule(work_session_rule)
        if practice_rule is None:
            return
        if not work_session_rule.slug:
            work_session_rule.slug = practice_rule.slug
        if not work_session_rule.body:
            work_session_rule.body = practice_rule.body

    def _matching_work_session_rule(
        self, work_session_rule: WorkSessionRule
    ) -> WorkSessionRule | None:
        found = self.entries.get(work_session_rule.slug)
        if isinstance(found, WorkSessionRule):
            return found
        return None

    def _matching_practice_rule(self, work_session_rule: WorkSessionRule) -> Rule | None:
        # -> practiceGuidance.rules
        if not work_session_rule.slug:
            return None
        practice = self._practice_guidance(work_session_rule)
        if practice is None:
            return None
        for bag in self._practice_rule_bags(practice):
            found = bag.entries.get(work_session_rule.slug)
            if isinstance(found, Rule):
                return found
        return None

    def _practice_rule_bags(self, practice: PracticeGuidance) -> list[RulesCollection]:
        bags = [practice.rules]
        fidelities = getattr(practice, "fidelities", None)
        if fidelities is None:
            return bags
        for child in fidelities:
            child_rules = getattr(child, "rules", None)
            if isinstance(child_rules, RulesCollection):
                bags.append(child_rules)
        return bags

    def _practice_guidance(self, work_session_rule: WorkSessionRule) -> PracticeGuidance | None:
        name = work_session_rule.guidance
        if not name:
            return None
        from harness.agent_tools.agent_tools import AgentToolSet

        module = name.replace("-", "_")
        class_name = "".join(part.title() for part in module.split("_"))
        return AgentToolSet.instantiate(
            f"practices.{module}.{module}:{class_name}"
        )

    def _place_by_star(self, work_session_rule: WorkSessionRule) -> None:
        ranked = sorted(
            (
                rule
                for rule in self.entries.values()
                if isinstance(rule, WorkSessionRule)
            ),
            key=lambda rule: rule.star,
            reverse=True,
        )
        self.entries = {rule.slug: rule for rule in ranked}

    def inject_rules(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        # practice rules being injected this turn
        # called from HookServer after handlers merge
        # -> self._matching_rules
        # -> self._merge_injected
        # -> self._band
        # -> self._render
        # -> self._write_last_chat_injected
        matching = self._matching_rules(payload)
        injected = ((payload or {}).get("additional_context") or "").strip()
        if injected:
            body = self._merge_injected(injected, matching)
        else:
            body = "\n\n".join(
                self._render(rule, self._detail_for(rule)) for rule in matching
            )
        self._write_last_chat_injected(body)
        return {"additional_context": body}

    def _write_last_chat_injected(self, body: str) -> None:
        destination = self._last_chat_injected_path()
        if destination is None:
            return
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(body, encoding="utf-8")

    def _last_chat_injected_path(self) -> Path | None:
        path = getattr(self.parent, "path", None)
        if path is None:
            return None
        return Path(path).parent / "last-chat-injected-rules.md"

    def _merge_injected(
        self, injected: str, matching: list[WorkSessionRule]
    ) -> str:
        overwrite_slugs = {rule.slug for rule in matching}
        parts = [
            self._render(rule, self._detail_for(rule)) for rule in matching
        ]
        remaining = self._without_slugs(injected, overwrite_slugs)
        if remaining:
            parts.append(remaining)
        return "\n\n".join(part for part in parts if part)

    def _without_slugs(self, injected: str, slugs: set[str]) -> str:
        lines: list[str] = []
        skip_indent = False
        for line in injected.splitlines():
            stripped = line.strip()
            if re.match(r"^[-*]\s+", stripped):
                skip_indent = Rule.from_bullet(stripped).slug in slugs
                if skip_indent:
                    continue
            elif skip_indent and line[:1].isspace():
                continue
            else:
                skip_indent = False
            if not skip_indent:
                lines.append(line)
        return "\n".join(lines).strip()

    def _matching_rules(
        self, payload: dict[str, Any] | None = None
    ) -> list[WorkSessionRule]:
        # match when rule.guidance is empty or equals that generate's guidance
        # and rule.fidelity is empty or equals that generate's fidelity
        # last fail at exclude turns ago or older → not injected
        # same match for specific, practice-wide, and global
        data = payload or {}
        guidances = self._names(
            data.get("injected_practices") or data.get("guidance")
        )
        fidelities = self._names(
            data.get("injected_fidelities") or data.get("fidelity")
        )
        injected_slugs = self._injected_slugs(
            (data.get("additional_context") or "").strip()
        )
        matched = [
            rule
            for rule in self
            if isinstance(rule, WorkSessionRule)
            and rule.last_fail < self.exclude
            and self._in_injected_set(rule, injected_slugs, guidances, fidelities)
        ]
        matched.sort(key=lambda rule: rule.star, reverse=True)
        return matched

    def _in_injected_set(
        self,
        rule: WorkSessionRule,
        injected_slugs: set[str],
        guidances: list[str],
        fidelities: list[str],
    ) -> bool:
        if injected_slugs and rule.slug in injected_slugs:
            return self._tags_match(rule, guidances, fidelities) or not guidances
        return self._tags_match(rule, guidances, fidelities)

    def _injected_slugs(self, injected: str) -> set[str]:
        slugs: set[str] = set()
        for line in injected.splitlines():
            stripped = line.strip()
            if re.match(r"^[-*]\s+", stripped):
                slugs.add(Rule.from_bullet(stripped).slug)
        return slugs

    def _names(self, value: Any) -> list[str]:
        if value is None or value == "":
            return []
        if isinstance(value, str):
            return [value]
        return [str(item) for item in value if item]

    def _tags_match(
        self,
        rule: WorkSessionRule,
        guidances: list[str] | str | None,
        fidelities: list[str] | str | None,
    ) -> bool:
        names = self._names(guidances)
        fidelity_names = self._names(fidelities)
        guidance_ok = not rule.guidance or rule.guidance in names
        fidelity_ok = not rule.fidelity or rule.fidelity in fidelity_names
        return guidance_ok and fidelity_ok

    def _band(self, work_session_rule: WorkSessionRule) -> str:
        # priority | relevant | context from inclusion counts and turn age
        age = work_session_rule.last_fail
        if age <= self.priority_inclusion:
            return "priority"
        if age <= self.relevant_inclusion:
            return "relevant"
        if age <= self.context_inclusion:
            return "context"
        return "excluded"

    def _detail_for(self, work_session_rule: WorkSessionRule) -> str:
        band = self._band(work_session_rule)
        return {
            "priority": self.priority_detail,
            "relevant": self.relevant_detail,
            "context": self.context_detail,
        }.get(band, "slug")

    def _render(self, work_session_rule: WorkSessionRule, detail: str) -> str:
        # examples | body | slug
        if detail == "examples":
            parts = [work_session_rule.body]
            for example in work_session_rule.examples:
                parts.append(example.mistake)
                parts.append(example.correction)
            return "\n".join(part for part in parts if part)
        if detail == "body":
            return work_session_rule.body
        return f"{work_session_rule.slug} ★{work_session_rule.star}"

    def _write(self) -> None:
        text = self.formatted()
        self.markdown = text
        path = getattr(self.parent, "path", None)
        if path is None:
            return
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(text, encoding="utf-8")


class Example:
    """One captured wrong version and its correction."""

    def __init__(self, mistake: str = "", correction: str = "") -> None:
        self.mistake = mistake
        self.correction = correction


class Examples:
    """Examples on a work session rule — each entry is a mistake and a correction."""

    def __init__(self, entries: list[Example] | None = None) -> None:
        self.entries = list(entries or [])

    def add(self, example: Example) -> Example:
        self.entries.append(example)
        return example

    def __iter__(self):
        return iter(self.entries)

    def __len__(self) -> int:
        return len(self.entries)

    def __getitem__(self, index: int) -> Example:
        return self.entries[index]


class WorkSessionRule(Rule):
    """A session rule tagged for a practice generate, with star and examples."""

    # empty guidance and empty fidelity → global
    # guidance set, fidelity empty → practice-wide

    def __init__(
        self,
        slug: str = "",
        body: str = "",
        guidance: str | None = None,
        fidelity: str | None = None,
        star: int = 0,
        examples: list[Example] | Examples | None = None,
        last_fail: int = 0,
    ) -> None:
        super().__init__(slug=slug, body=body, fidelity=fidelity)
        self._guidance = guidance
        self.star = star
        self.examples = (
            examples if isinstance(examples, Examples) else Examples(examples)
        )
        self.last_fail = last_fail

    @property
    def guidance(self) -> str | None:
        return self._guidance

    @guidance.setter
    def guidance(self, value: str | None) -> None:
        self._guidance = value

    @classmethod
    def from_bullet(cls, text: str, fidelity: str | None = None) -> WorkSessionRule:
        parsed = Rule.from_bullet(text, fidelity=fidelity)
        return cls(slug=parsed.slug, body=parsed.body, fidelity=parsed.fidelity)

    @classmethod
    def from_markdown(cls, text: str, fidelity: str | None = None) -> WorkSessionRule:
        lines = text.splitlines()
        rule = cls.from_bullet(lines[0] if lines else "", fidelity=fidelity)
        for line in lines[1:]:
            rule.apply_field(line)
        return rule

    def apply_field(self, line: str) -> None:
        field = self._field(line)
        if field is None:
            return
        name, value = field
        if name == "star":
            self.star = int(value or "0")
        elif name == "guidance":
            self.guidance = value or None
        elif name == "fidelity":
            self.fidelity = value or None
        elif name == "mistake":
            self.examples.add(Example(mistake=value))
        elif name == "correction":
            if self.examples:
                self.examples[-1].correction = value
            else:
                self.examples.add(Example(correction=value))
        elif name == "last-fail":
            self.last_fail = int(value or "0")

    @staticmethod
    def _field(line: str) -> tuple[str, str] | None:
        if not line[:1].isspace() or ":" not in line:
            return None
        name, value = line.strip().split(":", 1)
        name = name.strip()
        if name not in (
            "star",
            "guidance",
            "fidelity",
            "mistake",
            "correction",
            "last-fail",
        ):
            return None
        return name, value.strip()

    def to_markdown(self) -> str:
        lines = [f"- `{self.slug}` — {self.body}"]
        if self.star:
            lines.append(f"  star: {self.star}")
        if self.guidance:
            lines.append(f"  guidance: {self.guidance}")
        if self.fidelity:
            lines.append(f"  fidelity: {self.fidelity}")
        if self.last_fail:
            lines.append(f"  last-fail: {self.last_fail}")
        for example in self.examples:
            if example.mistake:
                lines.append(f"  mistake: {example.mistake}")
            if example.correction:
                lines.append(f"  correction: {example.correction}")
        return "\n".join(lines)


@agent_toolset
class Turn:
    """An announced work-session turn."""

    # record_mistake and record_correction are to be implemented

    def __init__(self, work_session: WorkSession | None = None) -> None:
        self._work_session = work_session
        self.mistakes: list[Any] = []
        self.correction: Any = None
        self.change_commit: TurnCommit | None = None

    @property
    def work_session(self) -> WorkSession | None:
        return self._work_session

    @Mcp
    @agent_tool
    def turn(self) -> TurnCommit | None:
        # /turn commits the current checkout
        # -> self._commit
        return self._commit()

    def _commit(self) -> TurnCommit | None:
        git = self._git()
        sha = git.commit(
            [str(git.root)],
            self._commit_message(),
            untracked=True,
        )
        change = TurnCommit(
            name=self._commit_message(),
            branch=git.current_branch,
            sha=sha,
        )
        self.change_commit = change
        return change

    def _git(self) -> GitRepo:
        session = self.work_session
        if session is not None:
            return session.git
        root = Repo(Path.cwd()).find_root()
        if root is None:
            raise GitConnectError("work session lives at the repository root")
        return GitRepo(root)

    def _commit_message(self) -> str:
        return "turn: checkpoint"

    def record_mistake(self) -> None:
        # ★ to be implemented
        ...

    def record_correction(self) -> None:
        # ★ to be implemented
        # later: -> self._add_work_session_rule
        ...

    def _add_work_session_rule(self) -> WorkSessionRule:
        # ★ to be implemented
        # -> work_session.guidance.rules.add
        ...
