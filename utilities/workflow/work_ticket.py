"""Work ticket — workflow-facing GitHub issue with type, theme, and org types."""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING

import yaml

from git.git import Repo, Ticket, issue_theme_label

if TYPE_CHECKING:
    from workflow.workflow import Workflow


class WorkTicket:
    """A backlog item on the repo's project, constructed with that repo and workflow."""

    TYPES = ("Defect", "Small change", "Refactor", "Feature")
    TYPE_DEFINITIONS = {
        "Defect": (
            "Unexpected or wrong current behavior. The kit already should do this "
            "and does not."
        ),
        "Small change": (
            "A change to an existing feature, utility, or tool that adds or "
            "adjusts behavior. Those are all Small changes unless the addition "
            "is very large."
        ),
        "Refactor": (
            "Restructuring code and where things live without changing "
            "functionality: rename, move, lift to a base, split or merge "
            "overlap. Same behavior, different shape or location."
        ),
        "Feature": (
            "Standing up a new module — a new package/folder (utilities/, "
            "primitives/, context_tools/, …). Example: creating the CLI agent. "
            "A small change to an existing feature or utility is not a Feature; "
            "that has to be very large to count."
        ),
    }
    TYPE_GUIDE = (
        "Type the ticket from these definitions (user override wins):\n"
        "- Defect: Unexpected or wrong current behavior. The kit already should do this and does not.\n"
        "- Small change: A change to an existing feature, utility, or tool. "
        "Those are all Small changes unless the addition is very large.\n"
        "- Refactor: Changing code and where things are without changing functionality.\n"
        "- Feature: Standing up a new module (a new folder). Example: creating the CLI agent. "
        "Do not call a small change to an existing feature a Feature."
    )
    TYPE_ALIASES = {
        "defect": "Defect",
        "defects": "Defect",
        "bug": "Defect",
        "feature": "Feature",
        "features": "Feature",
        "small change": "Small change",
        "small-change": "Small change",
        "small changes": "Small change",
        "change": "Small change",
        "task": "Small change",
        "refactor": "Refactor",
        "refactors": "Refactor",
    }
    REQUIRED_TYPES = (
        ("Defect", "An unexpected problem or behavior", "red"),
        (
            "Small change",
            "A change to an existing feature, utility, or tool (unless very large)",
            "yellow",
        ),
        (
            "Refactor",
            "Restructure code and location without changing functionality",
            "purple",
        ),
        (
            "Feature",
            "Standing up a new module/folder (e.g. creating the CLI agent)",
            "blue",
        ),
    )
    THEMES = (
        "catalog-generator",
        "grill-context",
        "cli-agent",
        "improvement",
        "workflow",
        "workspace",
        "harness",
        "actions",
        "sketch",
        "tools",
        "base",
        "mcp-invocation-layer",
    )
    _DEFECT_MARKERS = (
        "defect",
        "bug",
        "mistake",
        "mistakes",
        "broken",
        "wrong work",
        "not asked",
        "skips",
        "stuffing",
        "fails",
        "error",
    )
    _REFACTOR_MARKERS = (
        "refactor",
        "rename",
        "overlap",
        "live on",
        "only override",
        "where things",
        "without changing",
        "lift to",
        "align",
    )
    _SMALL_CHANGE_MARKERS = (
        "small change",
        "announce",
    )
    _FEATURE_MARKERS = (
        "new module",
        "new package",
        "new folder",
        "new utility",
        "new primitive",
        "creating the",
        "create a new",
        "stand up",
        "standing up",
    )

    def __init__(
        self,
        repo: Repo,
        workflow: Workflow | None = None,
        issue: Ticket | None = None,
    ) -> None:
        self.repo = repo
        self.workflow = workflow
        self._issue = issue
        self._type = issue.issue_type if issue is not None else ""
        self._theme = self._theme_from_issue(issue)

    @staticmethod
    def _theme_from_issue(issue: Ticket | None) -> str:
        if issue is None:
            return ""
        for label in issue.labels:
            if label.startswith("theme:"):
                return label.split(":", 1)[1]
        return ""

    @property
    def issue(self) -> Ticket | None:
        return self._issue

    @property
    def number(self) -> int:
        return 0 if self._issue is None else self._issue.number

    @property
    def title(self) -> str:
        return "" if self._issue is None else self._issue.title

    @property
    def body(self) -> str:
        return "" if self._issue is None else self._issue.body

    @property
    def url(self) -> str:
        return "" if self._issue is None else self._issue.url

    @property
    def type(self) -> str:
        if self._type:
            return self._type
        if self._issue is not None:
            return self._issue.issue_type
        return ""

    @property
    def theme(self) -> str:
        return self._theme

    @property
    def state(self) -> str:
        if self._issue is None:
            return ""
        if self._issue.state is not None:
            return self._issue.state.name
        return self.repo._ticket_project_state.get(self._issue.number, "")

    @classmethod
    def resolve_type(cls, category: str) -> str:
        text = (category or "").strip()
        if not text:
            return ""
        key = " ".join(text.lower().replace("_", " ").replace("-", " ").split())
        if key in cls.TYPE_ALIASES:
            return cls.TYPE_ALIASES[key]
        for name in cls.TYPES:
            if name.lower() == text.lower():
                return name
        raise ValueError(
            f"unknown ticket type {category!r}; use defect, small change, refactor, or feature"
        )

    @classmethod
    def infer_type(cls, text: str) -> str:
        blob = (text or "").lower()
        if any(marker in blob for marker in cls._DEFECT_MARKERS):
            return "Defect"
        if any(marker in blob for marker in cls._REFACTOR_MARKERS):
            return "Refactor"
        if any(marker in blob for marker in cls._SMALL_CHANGE_MARKERS):
            return "Small change"
        if any(marker in blob for marker in cls._FEATURE_MARKERS):
            return "Feature"
        return "Small change"

    @classmethod
    def _workflow_packages_path(cls, repo_root: Path | str | None) -> Path | None:
        if not repo_root:
            return None
        path = Path(repo_root) / ".context" / "workflow-packages.yaml"
        return path if path.is_file() else None

    @classmethod
    def _package_entries(cls, repo_root: Path | str | None = None) -> list[dict[str, str]]:
        path = cls._workflow_packages_path(repo_root)
        if path is None:
            return []
        payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        packages = payload.get("packages") if isinstance(payload, dict) else None
        if not isinstance(packages, list):
            return []
        entries: list[dict[str, str]] = []
        for item in packages:
            if not isinstance(item, dict):
                continue
            location = str(item.get("location") or "").strip()
            theme = str(item.get("theme") or "").strip()
            layer = str(item.get("layer") or "").strip()
            if location and theme:
                entries.append(
                    {"location": location, "theme": theme, "layer": layer}
                )
        return entries

    @classmethod
    def infer_theme(cls, text: str, repo_root: Path | str | None = None) -> str:
        blob = (text or "").replace("\\", "/")
        for entry in cls._package_entries(repo_root):
            location = entry["location"]
            if location in blob:
                return entry["theme"]
            layer = entry.get("layer") or ""
            if layer and layer.lower() in blob.lower():
                return entry["theme"]
        for theme in sorted(cls.THEMES, key=len, reverse=True):
            pattern = rf"\b{theme.replace('-', '[- ]')}\b"
            if re.search(pattern, blob, re.IGNORECASE):
                return theme
        return ""

    def ensure_types(self) -> list[str]:
        """Create org issue types the repo is missing."""
        existing = {
            str(item.get("name", "")).lower()
            for item in self.repo.list_issue_types()
        }
        added: list[str] = []
        for name, description, color in self.REQUIRED_TYPES:
            self.repo.ensure_issue_type(name, description=description, color=color)
            if name.lower() not in existing:
                added.append(name)
        return added

    def set_type(self, category: str) -> WorkTicket:
        name = self.resolve_type(category)
        self._type = name
        if name and self._issue is not None:
            self._issue.set_type(name)
        return self

    def set_theme(self, theme: str) -> WorkTicket:
        slug = (theme or "").strip()
        if slug.lower().startswith("theme:"):
            slug = slug.split(":", 1)[1].strip()
        self._theme = slug
        if slug and self._issue is not None:
            self._issue.add_theme(slug)
        return self

    def create(
        self,
        title: str,
        body: str,
        *,
        type: str = "",
        theme: str = "",
        status: str = "Backlog",
        infer_from: str = "",
    ) -> WorkTicket:
        self.ensure_types()
        clue = infer_from or f"{title}\n{body}"
        resolved_type = self.resolve_type(type) if type.strip() else self.infer_type(clue)
        resolved_theme = theme.strip() or self.infer_theme(clue, repo_root=self.repo.root)
        if resolved_theme.lower().startswith("theme:"):
            resolved_theme = resolved_theme.split(":", 1)[1].strip()
        issue = self.repo.create_ticket(title, body)
        issue.set_status(status)
        self._issue = issue
        if resolved_type:
            self.set_type(resolved_type)
        if resolved_theme:
            self.set_theme(resolved_theme)
        return self

    def as_dict(self, project_status: str = "") -> dict[str, str | int]:
        status = project_status or self.state
        payload: dict[str, str | int] = {
            "number": self.number,
            "title": self.title,
            "body": self.body,
            "url": self.url,
            "project_status": status,
        }
        if self.theme:
            label = issue_theme_label(self.theme)
            payload["theme"] = label
            if self._issue is not None and self._issue.labels:
                payload["labels"] = ", ".join(self._issue.labels)
        if self.type:
            payload["category"] = self.type
            payload["type"] = self.type
        return payload


def format_session_ticket_context(
    repo: Repo, ticket_number: int
) -> tuple[str, str]:
    """Build session.md body and contexts refs for a ticket and linked sub-issues.

    When the ticket is a parent, include every direct child. When it is a child,
    include the parent and all siblings so the session has the full group.
    """
    issue = repo.ticket(str(ticket_number))
    if issue is None:
        return "", ""

    tickets: list[Ticket] = []
    seen: set[int] = set()

    def add(candidate: Ticket | None) -> None:
        if candidate is None or candidate.number in seen:
            return
        seen.add(candidate.number)
        tickets.append(candidate)

    add(issue)
    if issue.sub_issue_numbers:
        for child_number in sorted(issue.sub_issue_numbers):
            add(repo.ticket(str(child_number)))
    elif issue.parent_number is not None:
        parent = repo.ticket(str(issue.parent_number))
        add(parent)
        if parent is not None and parent.sub_issue_numbers:
            for child_number in sorted(parent.sub_issue_numbers):
                add(repo.ticket(str(child_number)))

    lines = ["## Tickets", ""]
    refs: list[str] = []
    for ticket in tickets:
        refs.append(f"#{ticket.number}")
        lines.append(f"### #{ticket.number} — {ticket.title}")
        lines.append("")
        if ticket.url:
            lines.append(ticket.url)
            lines.append("")
        body = (ticket.body or "").strip()
        if body:
            lines.append(body)
        else:
            lines.append(
                "*(Issue body empty on GitHub — title is the requirement.)*"
            )
        lines.append("")

    return "\n".join(lines).rstrip() + "\n", " ".join(refs)
