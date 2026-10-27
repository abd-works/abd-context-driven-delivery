"""GitHub backlog ticket helper used by Workflow."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from space.repo.repo import Repo, Ticket


@dataclass
class _CreatedWork:
    ticket: Ticket

    def as_dict(self, project_status: str = "") -> dict[str, str | int]:
        return {
            "number": self.ticket.number,
            "title": self.ticket.title,
            "url": self.ticket.url,
            "status": project_status,
        }


class WorkTicket:
    def __init__(self, repo: Repo, workflow: Any) -> None:
        self._repo = repo
        self._workflow = workflow

    def create(
        self,
        title: str,
        body: str,
        *,
        type: str = "",
        theme: str = "",
        status: str = "",
        infer_from: str = "",
    ) -> _CreatedWork:
        ticket = self._repo.create_ticket(title, body)
        if type:
            ticket.write_type(type)
        if theme:
            from space.repo.repo import issue_theme_label

            label = issue_theme_label(theme)
            if label:
                ticket.add_label(label)
        return _CreatedWork(ticket=ticket)


def format_session_ticket_context(repo: Repo, issue_number: int) -> tuple[str, dict[str, str]]:
    issue = repo.ticket(str(issue_number))
    if issue is None:
        return "", {}
    return issue.body or "", {"title": issue.title, "url": issue.url}
