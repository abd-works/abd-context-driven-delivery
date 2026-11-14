"""What a story node's name and file say about it, as the story map's rules read them: whether the name opens with a
verb, a generic handler, an actor, a gerund or a nominalisation, whether it names a one-time task, and whether its file
is named in camel case."""

from __future__ import annotations

import re
_GENERIC_VERBS = frozenset({"handle", "process", "manage", "perform", "do", "execute", "run"})
_ACTOR_NOUNS = frozenset({
    "customer", "user", "system", "admin", "operator", "treasurer", "approver",
    "auditor", "merchant", "partner", "service", "api", "backend", "frontend",
    "database", "browser", "client", "server",
})
_VERBS = frozenset({
    "access", "activate", "add", "allow", "apply", "approve", "assign",
    "attach", "authenticate", "authorize", "block", "browse", "build", "cancel",
    "capture", "change", "check", "choose", "clear", "close", "collect",
    "compare", "complete", "compose", "confirm", "connect", "convert", "create",
    "delete", "deliver", "deny", "deploy", "detect", "determine", "disable",
    "display", "download", "draft", "drop", "edit", "email", "enable", "enter",
    "expire", "export", "extend", "extract", "fetch", "filter", "fix", "flag",
    "generate", "get", "grant", "group", "hide", "hold", "import", "index",
    "initiate", "invite", "issue", "join", "know", "leave", "list", "load", "lock",
    "log", "map", "match", "merge", "move", "notify", "onboard", "open",
    "order", "pause", "pay", "pick", "place", "post", "print", "provide",
    "publish", "purchase", "query", "queue", "read", "record", "redeem", "refresh",
    "refund", "register", "reject", "release", "remove", "rename", "render",
    "reply", "report", "request", "reset", "resolve", "retry", "return",
    "revert", "review", "revoke", "route", "save", "scan", "schedule", "search",
    "select", "send", "serve", "set", "settle", "share", "show", "sign",
    "split", "start", "stop", "store", "submit", "subscribe", "sync", "toggle",
    "track", "translate", "trigger", "unlock", "update", "upload", "use",
    "validate", "verify", "view", "vote", "wait",
})
_GERUND = re.compile(r"^[a-z]+ing$")
_NOMINALISATION = re.compile(r"^[a-z]+(?:tion|sion|ment|ance|ence|ity|ness)$")
_KEBAB_FILE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*\.(md|ts|tsx|js|jsx)$")
_CAMEL_FILE = re.compile(r"[A-Z][a-zA-Z0-9]*(?:Story|Test|Spec)")
_ONE_OFF = re.compile(r"\b(once|one[- ]time|initial setup|bootstrap only|migrate legacy)\b", re.IGNORECASE)
# What a first word is, in the order a word is checked: the first set or pattern that holds it names its class.
_OPENINGS = (
    ("generic-verb", _GENERIC_VERBS.__contains__),
    ("verb", _VERBS.__contains__),
    ("actor-noun", _ACTOR_NOUNS.__contains__),
    ("gerund", _GERUND.match),
    ("nominalisation", _NOMINALISATION.match),
)


def opening_of(name: str) -> tuple[str, str]:
    """The first word of name, lower case, and its class: a single word, a generic verb, a verb, an actor noun, a
    gerund, a nominalisation, unlisted, or an unknown noun for a name that opens with no word."""
    stripped = (name or "").strip().strip("`").strip("*").strip()
    match = re.match(r"[A-Za-z][A-Za-z\-']*", stripped)
    token = match.group(0).lower() if match else ""
    # One word ("CartStuff") has no object to follow a verb, whatever the word is.
    if stripped and len(stripped.split()) == 1:
        return token, "single-word"
    return token, _class_of(token)


def _class_of(token: str) -> str:
    if not token:
        return "unknown-noun"
    # A word the verb list lacks is not evidence of a noun ("Carry Plan ..."); only the classes listed are flagged.
    return next((label for label, holds in _OPENINGS if holds(token)), "unlisted")


def opens_with_verb(name: str) -> bool:
    """The name's first word is a verb the story map knows, generic or not."""
    token = next(iter((name or "").split()), "").lower()
    return token in _VERBS or token in _GENERIC_VERBS


def names_generic_handler(name: str) -> bool:
    """A generic verb such as Handle or Process followed by its object: the name hides what happens."""
    words = (name or "").split()
    return len(words) > 1 and words[0].lower() in _GENERIC_VERBS and words[1][:1].isalpha()


def names_one_time_task(name: str) -> bool:
    """The name says the work happens once, such as an initial setup or a migration."""
    return bool(_ONE_OFF.search(name or ""))


def file_name_facts(source: object) -> tuple[str, bool]:
    """The name of the file source names, and whether it is named in camel case."""
    relative = str(getattr(source, "file", "") or "") if source is not None else ""
    name = relative.replace("\\", "/").rsplit("/", 1)[-1]
    return name, _camel_case(name)


def _camel_case(name: str) -> bool:
    if not name or name == "." or _KEBAB_FILE.match(name):
        return False
    return bool(_CAMEL_FILE.search(name) or re.search(r"[A-Z]", name.split(".")[0]))

