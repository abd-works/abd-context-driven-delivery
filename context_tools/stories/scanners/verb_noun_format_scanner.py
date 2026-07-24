"""verb-noun-format — Epic / SubEpic / Story names are `<Verb> <Noun>`."""

from __future__ import annotations

import re

from story_workspace_base import StoryWorkspaceScanner

_GERUND_SUFFIX = re.compile(r"^[a-z]+ing$")
_NOMINALISATION_SUFFIX = re.compile(r"^[a-z]+(?:tion|sion|ment|ance|ence|ity|ness)$")

_KNOWN_ACTOR_NOUNS = {
    "customer", "user", "system", "admin", "operator", "treasurer", "approver",
    "auditor", "merchant", "partner", "service", "api", "backend", "frontend",
    "database", "browser", "client", "server",
}

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
    "view", "vote", "wait", "browse", "request", "manage", "place", "place",
}


def _first_token(name: str) -> str:
    stripped = name.strip().strip("`").strip("*").strip()
    match = re.match(r"[A-Za-z][A-Za-z\-']*", stripped)
    return match.group(0).lower() if match else ""


def _classify(token: str) -> str:
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


class VerbNounFormatScanner(StoryWorkspaceScanner):
    def scan_workspace(self, workspace):
        if not workspace.has_story_map():
            return
        for epic in workspace.story_map.epics:
            yield from self._check_node(epic, "epic")
            for sub in epic.sub_epics:
                yield from self._walk_sub(sub)

    def _walk_sub(self, sub):
        yield from self._check_node(sub, "sub-epic")
        for nested in sub.sub_epics:
            yield from self._walk_sub(nested)
        for story in sub.stories:
            yield from self._check_node(story, "story")

    def _check_node(self, node, kind_label: str):
        name = getattr(node, "name", "") or ""
        token = _first_token(name)
        classification = _classify(token)
        loc = self.loc(node, f"{kind_label} {name!r}")

        if classification == "verb":
            if len(name.strip().strip("`").split(None, 1)) < 2:
                yield self.violation(
                    f"{kind_label} {name!r}: verb without a noun",
                    location=loc,
                    severity="warning",
                )
            return
        if classification == "gerund":
            yield self.violation(
                f"{kind_label} {name!r}: starts with gerund {token!r}",
                location=loc,
                severity="warning",
            )
            return
        if classification == "nominalisation":
            yield self.violation(
                f"{kind_label} {name!r}: starts with nominalisation {token!r}",
                location=loc,
                severity="warning",
            )
            return
        if classification == "actor-noun":
            yield self.violation(
                f"{kind_label} {name!r}: starts with actor noun {token!r}",
                location=loc,
                severity="warning",
            )
            return
        yield self.violation(
            f"{kind_label} {name!r}: first token {token!r} is not a recognised verb",
            location=loc,
            severity="info",
        )
