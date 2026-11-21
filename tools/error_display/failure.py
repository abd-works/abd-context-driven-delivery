"""*Failure*: something a person or the agent ran that did not work, shown the same way wherever it happened.

Every failure says what failed and why, the context it failed in, and offers Fix, which sends both to the chat to find
the cause and fix it. A failure of a known *FailureKind*, such as a file a page could not show, also lists the most
common causes of that kind, which Fix shows the person and sends with the failure, so the chat checks them first. The
chat bar shows one above its line until it is fixed or dismissed; an app outside Python builds the same shape from the
TypeScript this class's language adapter generates, so no failure is shown differently.
"""
from __future__ import annotations

import json

from harness.agent_tools import agent_toolset
from harness.agent_tools.agent_tools import agent_tool
from harness.installation.data_class import data_field, language_adapter
from harness.mcp.mcp_annotations import mcp

# The slash command of space/session's debug_session skill, which the chat bar's Fix buttons start too
# (harness/chat-ui/pane/hooks/shared/debug-command.ts): it captures what went wrong, then fixes it.
FIX_COMMAND = "/space-session-debug-session"


class FailureKindUnknownError(ValueError):
    """A failure described with a kind no failure has, which names the kind and the kinds there are."""

    def __init__(self, kind: str, known: list[str]) -> None:
        super().__init__(f"No kind of failure is called {kind}: the kinds are {', '.join(known)}")
        self.kind = kind


class FailureKind:
    """One kind of failure a page or an action meets, with the causes it most often has, the likeliest first."""

    def __init__(self, name: str, title: str, causes: tuple[str, ...] = ()) -> None:
        self.name = name
        self.title = title
        self.causes = causes

    def checks(self) -> str:
        """What the chat is told to check first: each cause, numbered; nothing for a kind with no known causes."""
        if not self.causes:
            return ""
        numbered = " ".join(f"{number}. {cause}" for number, cause in enumerate(self.causes, start=1))
        return f" The most common causes of {self.title}, to check first: {numbered}"


class FailureKinds:
    """Every kind of failure whose common causes are known, found by the name a page or an action gives its failure."""

    def __init__(self, *kinds: FailureKind) -> None:
        self._kinds = {kind.name: kind for kind in kinds}
        self._unnamed = FailureKind("", "this failure")

    def named(self, name: str) -> FailureKind:
        """The kind called name; a failure that names no kind has no known causes."""
        if not name:
            return self._unnamed
        if name not in self._kinds:
            raise FailureKindUnknownError(name, list(self._kinds))
        return self._kinds[name]


FAILURE_KINDS = FailureKinds(
    FailureKind(
        "file_display",
        "a file that cannot be shown",
        (
            "The file was moved, renamed or deleted after the page listed it: list the files again and open it from the new list.",
            "The file sits outside the session's roots, which the session refuses to read: check the session's workpath and each practice's root.",
            "The file is not text the viewer can read, such as a binary file or one not written in UTF-8, or it is too long for the viewer.",
            "The project folder the page was opened on is gone, such as a ticket's worktree closed since the page opened.",
            "The cdd server stopped, or runs older code than the page, so it does not know the tool the page called: restart it, or install again so the language adapters match.",
        ),
    ),
    FailureKind(
        "missing_link",
        "a link to a file or heading that is not there",
        (
            "The link's path is written from the wrong folder: a link is read from the folder of the file that holds it.",
            "The file or the heading was renamed and the link still names the old one.",
            "The heading's anchor is spelled differently from the heading: lower case, spaces as dashes, punctuation left out.",
            "The file the link names has not been generated yet: the fidelity that writes it has not run, or wrote it under another root.",
            "The link leads outside the session's roots, which the session never reads.",
        ),
    ),
    FailureKind(
        "graph_view",
        "a graph view that fails",
        (
            "A file the graph reads does not parse in its language, or has a shape its practice does not expect, so the read stops at it.",
            "The cdd server restarted or ran out of time while it read the graph, as it can on a large working copy.",
            "The session's saved graph (graph.json in the session's folder) was written by an older version or was cut off half way.",
            "The node filter names a node type, a connector or a rule the graph no longer offers.",
            "A listed file was moved or deleted since the graph read it, so a node's lines are no longer where the graph holds them.",
        ),
    ),
    FailureKind(
        "render",
        "a render action that fails",
        (
            "The file to render is empty, is not there, or sits outside the session's roots.",
            "The file does not follow its fidelity's template, so the format adapter reads nothing to draw.",
            "The format asked for is not one the fidelity offers.",
            "A drawing already saved beside the file was changed by hand in a way the adapter cannot read back.",
            "The board in Claude was never recorded for the whiteboard, so there is nothing to publish onto.",
        ),
    ),
    FailureKind(
        "generate",
        "a generate action that fails",
        (
            "The practice is turned off for the session, or its fidelity has no root to write under.",
            "A path the action was given is not there, or sits outside the session's roots.",
            "A template or an example the fidelity names is missing from the install: install CDD again.",
            "The cdd server runs older code than the installed skills, so the action and its rules disagree: restart it.",
            "The source the fidelity generates from, such as the story map or the model, is missing or does not follow its own template.",
        ),
    ),
    FailureKind(
        "session_roots",
        "session roots that are wrong or missing",
        (
            "No root is chosen for the practice, or the folder a fidelity's root names does not exist yet.",
            "The session's workpath in its session.json names a folder that was moved or deleted.",
            "The roots were chosen in another checkout or worktree, so their paths lead nowhere in this one.",
            "The practice is turned off for the session, so its files are not listed.",
            "The page was opened on a project folder other than the one the session works in.",
        ),
    ),
)


@language_adapter(language="typescript")
@agent_toolset
class Failure:
    """One failure as a person sees it: what failed with the reason it gave, the context it failed in, and the most
    common causes of its kind."""

    def __init__(self, failure: str = "", context: str = "", kind: FailureKind | None = None) -> None:
        self._failure = failure
        self._context = context
        self._kind = kind or FAILURE_KINDS.named("")

    @classmethod
    @mcp
    @agent_tool
    def describe(cls, failure: str, context: str, kind: str = "") -> Failure:
        """The failure as it is shown: failure says what failed and the reason it gave, context what was being done
        and where, such as the action pressed and the tool it called, and kind which kind of failure it is, one of
        file_display, missing_link, graph_view, render, generate or session_roots, none when it is none of these. It
        answers with the most common causes of that kind and the command its Fix sends to the chat."""
        return cls(failure, context, FAILURE_KINDS.named(kind))

    @property
    @data_field
    def failure(self) -> str:
        return self._failure

    @property
    @data_field
    def context(self) -> str:
        return self._context

    @property
    @data_field
    def kind(self) -> str:
        return self._kind.name

    @property
    @data_field
    def causes(self) -> list[str]:
        """The most common causes of this kind of failure, the likeliest first; none for a failure of no known kind."""
        return list(self._kind.causes)

    @property
    @data_field
    def fix_command(self) -> str:
        """What Fix sends to the chat: the debug session command with the fix chosen and, as its details, the failure,
        its context and the causes to check first."""
        details = f"Failure: {self._failure} Context: {self._context}{self._kind.checks()}"
        return f"{FIX_COMMAND} choice=fix details={json.dumps(details)}"
