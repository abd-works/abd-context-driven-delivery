"""verb-noun-format — every Epic / SubEpic / Story name is `<Verb> <Noun>`.

Reference implementation of the Workspace-based scanner contract.

- No text parsing: walks `workspace.story_map` (from core domain model).
- Names arrive clean (backticks stripped by the markdown adapter).
- Locations are `SourceLocation` stamps applied by the story-map loader.

Rule check:
- Name's first token must be a base-form verb (not a gerund, not a noun/adjective).
- Name must contain at least one noun-like token after the verb.

The verb list is a small deny/allow set — enough to catch the common failure
modes (gerunds like "Submitting", nominalisations like "Submission", pronouns like
"Customer" as first word). The AI-judge covers edge cases we don't encode here.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Iterator

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from stories.src.skill.scanners._base import ArtifactScanner, Violation, run  # noqa: E402


_GERUND_SUFFIX = re.compile(r"^[a-z]+ing$")
_NOMINALISATION_SUFFIX = re.compile(r"^[a-z]+(?:tion|sion|ment|ance|ence|ity|ness)$")

# Non-verb first tokens we've observed as failure modes. These are common actor
# nouns that read like verbs when a story is written "actor-first" instead of
# "verb-first". Real stories keep the actor as a **`Actor:`** prefix or in the
# outline's `(S) <actor> --> <verb-noun>` position — never in the story name.
_KNOWN_ACTOR_NOUNS = {
    "customer", "user", "system", "admin", "operator", "treasurer", "approver",
    "auditor", "merchant", "partner", "service", "api", "backend", "frontend",
    "database", "browser", "client", "server",
}

# A minimal allow-list of common English verbs that appear as first tokens in
# well-formed story names. Anything not on the deny-list AND not obviously
# gerund/nominalisation is accepted — this keeps the scanner conservative.
_KNOWN_VERBS = {
    "add", "allow", "approve", "assign", "attach", "block", "build", "cancel",
    "capture", "check", "clear", "close", "collect", "compare", "complete",
    "compose", "confirm", "connect", "convert", "create", "delete", "deliver",
    "deny", "deploy", "detect", "disable", "display", "download", "draft",
    "drop", "edit", "email", "enable", "enter", "expire", "export", "extend",
    "extract", "fetch", "filter", "fix", "flag", "generate", "grant", "group",
    "handle", "hide", "hold", "import", "index", "initiate", "invite", "issue",
    "join", "leave", "list", "load", "lock", "log", "map", "match", "merge",
    "move", "notify", "onboard", "open", "order", "pause", "pay", "post",
    "print", "process", "publish", "queue", "read", "record", "refresh",
    "refund", "register", "reject", "release", "remove", "rename", "render",
    "reply", "report", "reset", "resolve", "retry", "return", "revert",
    "review", "revoke", "route", "run", "save", "scan", "schedule", "search",
    "select", "send", "settle", "share", "show", "sign", "split", "start",
    "stop", "store", "submit", "subscribe", "sync", "toggle", "track",
    "translate", "trigger", "unlock", "update", "upload", "validate", "verify",
    "view", "vote", "wait",
}


def _first_token(name: str) -> str:
    """Return the leading word of a story-map name (lowercased, punctuation stripped)."""
    stripped = name.strip().strip("`").strip("*").strip()
    match = re.match(r"[A-Za-z][A-Za-z\-']*", stripped)
    return match.group(0).lower() if match else ""


def _classify_first_token(token: str) -> str:
    """Return one of: 'verb' | 'gerund' | 'nominalisation' | 'actor-noun' | 'unknown-noun'."""
    if not token:
        return "unknown-noun"
    if token in _KNOWN_VERBS:
        return "verb"
    if token in _KNOWN_ACTOR_NOUNS:
        return "actor-noun"
    if _GERUND_SUFFIX.match(token):
        return "gerund"
    if _NOMINALISATION_SUFFIX.match(token):
        return "nominalisation"
    return "unknown-noun"


class VerbNounFormatScanner(ArtifactScanner):
    """Enforce Verb + Noun structure on every story-map name."""
    rule = "verb-noun-format"
    kind = "quality"
    reads = ("story_map",)

    def scan(self) -> Iterator[Violation]:
        if not self.workspace.has_story_map():
            return
        story_map = self.workspace.story_map
        for epic in story_map.epics:
            yield from self._check_node(epic, "epic")
            for sub_epic in epic.sub_epics:
                yield from self._check_sub_epic(sub_epic)

    def _check_sub_epic(self, sub_epic) -> Iterator[Violation]:
        yield from self._check_node(sub_epic, "sub-epic")
        for nested in sub_epic.sub_epics:
            yield from self._check_sub_epic(nested)
        for story in sub_epic.stories:
            yield from self._check_node(story, "story")

    def _check_node(self, node, kind_label: str) -> Iterator[Violation]:
        name = getattr(node, "name", "") or ""
        token = _first_token(name)
        classification = _classify_first_token(token)

        if classification == "verb":
            # Ensure a noun follows the verb (at least one more word)
            remainder = name.strip().strip("`").split(None, 1)
            if len(remainder) < 2:
                yield Violation(
                    rule=self.rule,
                    message=f"{kind_label} {name!r}: verb without a noun",
                    location=self.location(getattr(node, "source", None), f"{kind_label} {name!r}"),
                    severity="warning",
                    hint="A story name is `<Verb> <Noun>` — add the object the verb acts on",
                )
            return

        if classification == "gerund":
            yield Violation(
                rule=self.rule,
                message=f"{kind_label} {name!r}: starts with gerund {token!r}",
                location=self.location(getattr(node, "source", None), f"{kind_label} {name!r}"),
                severity="warning",
                hint=f"Use base form: '{token[:-3]}' instead of '{token}'",
            )
            return

        if classification == "nominalisation":
            yield Violation(
                rule=self.rule,
                message=f"{kind_label} {name!r}: starts with nominalisation {token!r}",
                location=self.location(getattr(node, "source", None), f"{kind_label} {name!r}"),
                severity="warning",
                hint=f"Turn '{token}' back into a verb (e.g. Submit vs Submission)",
            )
            return

        if classification == "actor-noun":
            yield Violation(
                rule=self.rule,
                message=(
                    f"{kind_label} {name!r}: starts with actor noun {token!r}"
                ),
                location=self.location(getattr(node, "source", None), f"{kind_label} {name!r}"),
                severity="warning",
                hint=(
                    f"Actor belongs in the outline position "
                    f"'(S) {token.capitalize()} --> Verb Noun' — not in the story name"
                ),
            )
            return

        # unknown-noun — we don't know if it's a verb we haven't seen
        yield Violation(
            rule=self.rule,
            message=f"{kind_label} {name!r}: first token {token!r} is not a recognised verb",
            location=self.location(getattr(node, "source", None), f"{kind_label} {name!r}"),
            severity="info",
            hint=(
                "If this IS a verb, add it to _KNOWN_VERBS in verb-noun-format-scanner.py; "
                "otherwise rewrite the name to start with a verb"
            ),
        )


if __name__ == "__main__":
    sys.exit(run(VerbNounFormatScanner))
