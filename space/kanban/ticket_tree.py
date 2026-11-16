"""Where a ticket sits among its parent and its children, and the changes a person makes to that tree."""

from __future__ import annotations

from typing import TYPE_CHECKING

from space.kanban.board import Stage

if TYPE_CHECKING:
    from space.kanban.ticket import Ticket


class ParentMovesWithChildrenError(ValueError):
    """Raised when a person moves a ticket that has children: a parent takes the stage of its child furthest back."""

    def __init__(self, ticket: str) -> None:
        super().__init__(f"{ticket} has child tickets; a parent moves only with its children")


class NotAChildError(ValueError):
    """Raised when a ticket with no parent is pulled out of one."""

    def __init__(self, ticket: str) -> None:
        super().__init__(f"{ticket} has no parent to be pulled out of")


class ParentLoopError(ValueError):
    """Raised when a ticket would become its own parent, or a child of one of its own children."""

    def __init__(self, ticket: str, parent: str) -> None:
        super().__init__(f"{parent} cannot be the parent of {ticket}: it is {ticket} or one of its children")


class TicketTree:
    """*TicketTree* is where one ticket sits among the tickets its session names as parent and child: its ancestors,
    the tickets it may become a child of, whether it shows stacked inside its parent's card, and the changes a person
    makes to the tree, each kept in its session and committed on main and pushed."""

    def __init__(self, ticket: Ticket) -> None:
        self._ticket = ticket

    @property
    def ancestors(self) -> list[Ticket]:
        """Its parent, its parent's parent, and so on."""
        parent = self._ticket.parent
        return [parent, *parent.tree.ancestors] if parent is not None else []

    @property
    def is_stacked(self) -> bool:
        """Whether it shows inside its parent's card rather than as a card of its own: an open child, not pulled out, of
        an open parent."""
        ticket = self._ticket
        if ticket.is_pulled_out or ticket.is_closed:
            return False
        parent = ticket.parent
        return parent is not None and not parent.is_closed

    @property
    def parent_choices(self) -> list[str]:
        """The tickets a person can drop it on to make it their child: any on the board but its own parent, itself, and
        the tickets under it, which would make a loop."""
        ticket = self._ticket
        if ticket.is_main:
            return []
        # By name: its parent is a ticket of its own, never one of the board's ticket objects.
        parent_name = ticket.parent.name if ticket.parent is not None else None
        return [other.name for other in ticket.board.tickets if other.name != parent_name and self.can_be_child_of(other)]

    def can_be_child_of(self, parent: Ticket) -> bool:
        return self._ticket.name not in [parent.name, *(ancestor.name for ancestor in parent.tree.ancestors)]

    @property
    def furthest_back_child_stage(self) -> Stage | None:
        """The stage of its child furthest back on the board; none while no child of it is on a stage."""
        stages = self._ticket.board.stages
        staged = [column for column in (child.column for child in self._ticket.children) if isinstance(column, Stage)]
        return min(staged, key=stages.index) if staged else None

    def refuse_moving_a_parent(self) -> None:
        """A parent moves only with its children, so a person cannot move it on its own."""
        if self._ticket.children:
            raise ParentMovesWithChildrenError(self._ticket.name)

    def add_child(self, title: str) -> Ticket:
        """A child ticket titled title, a story In progress in Discovery, working where the ticket works."""
        ticket = self._ticket
        return ticket.board.placement.ticket_of(ticket.session.hierarchy.open_child(title, scope="story"))

    def pull_out(self) -> Ticket:
        """The ticket moving on the board as a card of its own, still keeping its parent."""
        ticket = self._ticket
        if ticket.parent is None:
            raise NotAChildError(ticket.name)
        ticket.session.hierarchy.mark_pulled_out()
        ticket.forget_reads()
        return ticket

    def reassign_parent(self, parent: Ticket | None) -> Ticket:
        """The ticket with parent as its parent, or none; either way no longer pulled out."""
        ticket = self._ticket
        if parent is not None and not self.can_be_child_of(parent):
            raise ParentLoopError(ticket.name, parent.name)
        ticket.session.hierarchy.set_parent(parent.session if parent is not None else None)
        ticket.forget_reads()
        return ticket
