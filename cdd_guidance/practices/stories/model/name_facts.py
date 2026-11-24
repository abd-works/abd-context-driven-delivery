"""What a story node's name, file and children say about it, as the story map's rules read them: whether the name opens
with a verb, a generic handler, an actor, a gerund or a nominalisation, whether its file is named in camel case, and
whether its children fit the band of its layer (*NameFacts*)."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from harness.graph.graph import Source

    from cdd_guidance.practices.stories.model.story_map import ChildBand, StoryNode

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
    "comment", "compare", "complete", "compose", "confirm", "connect", "convert", "create",
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


def _names_generic_handler(name: str) -> bool:
    """A generic verb such as Handle or Process followed by its object: the name hides what happens."""
    words = (name or "").split()
    return len(words) > 1 and words[0].lower() in _GENERIC_VERBS and words[1][:1].isalpha()


def _file_name_facts(source: Optional["Source"]) -> tuple[str, bool]:
    """The name of the file source names, and whether it is named in camel case."""
    relative = str(getattr(source, "file", "") or "") if source is not None else ""
    name = relative.replace("\\", "/").rsplit("/", 1)[-1]
    return name, _camel_case(name)


def _camel_case(name: str) -> bool:
    if not name or name == "." or _KEBAB_FILE.match(name):
        return False
    return bool(_CAMEL_FILE.search(name) or re.search(r"[A-Z]", name.split(".")[0]))



class NameFacts:
    """The facts the story map's rules read about one story node, which the node holds as a part
    (``StoryNode.name_facts``) and the graph saves as the node's own: how its name opens (``opening_token``,
    ``opening_class``), the file it was read from and whether that file is named in camel case (``artifact_name``,
    ``camel_case_path``), how many children it holds against the band of its layer (``child_count``, ``child_label``,
    ``child_target``, ``child_band``), and three a node judges from its place in the map: whether its name hides what
    happens behind a generic handler (``generic_handler``), repeats a later sibling's (``near_duplicate``), or opens
    with the verb all its stories share (``shared_verb``). Each kind of node loads them when its map loads
    (``load_map_facts``); until then they are empty."""

    graph_facts = (
        "opening_token", "opening_class", "child_count", "child_label", "child_band", "child_target", "near_duplicate",
        "generic_handler", "shared_verb", "artifact_name", "camel_case_path",
    )

    def __init__(self, node: StoryNode) -> None:
        self._node = node
        self.opening_token = ""
        self.opening_class = ""
        self.artifact_name = ""
        self.camel_case_path = False
        self.child_count = 0
        self.child_label = "children"
        self.child_target = ""
        self.child_band = ""
        self.generic_handler = False
        self.near_duplicate = False
        self.shared_verb = ""

    def load(self, children: int, band: ChildBand | None = None, label: str = "children") -> None:
        """Read what the node's name and file say, and count its children, labelled by band when its layer has one,
        else by label: past band's limits the count is an error; a node of no layer that is sized, such as a story,
        holds no band and passes. What the node judges from its place in the map starts empty (``judge``)."""
        self.opening_token, self.opening_class = opening_of(self._node.name)
        self.artifact_name, self.camel_case_path = _file_name_facts(getattr(self._node, "source", None))
        self.child_count = children
        self.child_label = band.label if band is not None else label
        self.child_target = band.written if band is not None else ""
        self.child_band = "" if band is None or band.holds(children) else "error"
        self.judge()

    def judge(self, generic_handler: bool = False, near_duplicate: bool = False, shared_verb: str = "") -> None:
        """Keep what the node judges from its name and its place in the map."""
        self.generic_handler = generic_handler
        self.near_duplicate = near_duplicate
        self.shared_verb = shared_verb

    @property
    def opens_with_generic_handler(self) -> bool:
        """Whether the node's name opens with a generic verb such as Handle or Process followed by its object."""
        return _names_generic_handler(self._node.name)
