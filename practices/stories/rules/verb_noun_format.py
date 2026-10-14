"""verb-noun-format — from practices/stories/scanners on main (graph node names)."""

from __future__ import annotations

import re

from harness.graph.practice_rule import PracticeGraphRule

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
    "view", "vote", "wait", "browse", "request", "manage", "place",
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


class VerbNounFormat(PracticeGraphRule):
    slug = "verb-noun-format"
    node_types = ("Epic", "SubEpic", "Story")

    def check(self, node, context) -> list[str]:
        token = _first_token(node.name)
        kind = _classify(token)
        if kind == "verb":
            return []
        return [f"{node.type} {node.name!r}: name should start with a verb (got {kind})."]
