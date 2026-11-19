"""The name a new card's folder or file gets from its title, and the refusals of a title that gives no usable name."""

from __future__ import annotations

from harness.annotations.name import Name

# A ticket's name is its session folder, its branch, and part of every path in its worktree, so a long one meets
# Windows' path limit; a new card's name stops here.
NAME_LENGTH_LIMIT = 64


class TitleNamesNothingError(ValueError):
    """Raised when a new card's title holds no Latin letter or digit, such as an empty title or one in another script:
    its name, made from those, would be empty. It carries the title."""

    def __init__(self, title: str) -> None:
        super().__init__(f"the title {title!r} gives no name: a title needs at least one letter a to z or one digit")
        self.title = title


class TitleTooLongError(ValueError):
    """Raised when the name made from a new card's title is longer than a folder and a branch can safely be. It carries
    the title, the name, and the limit."""

    def __init__(self, title: str, name: str, limit: int) -> None:
        super().__init__(f"the title {title!r} makes a name of {len(name)} characters; shorten it to {limit} or fewer")
        self.title = title
        self.name = name
        self.limit = limit


class TicketNameTakenError(ValueError):
    """Raised when a new ticket's title makes the name of a session the repository already has, main included. It
    carries the title and the name, so the person gives the new work another title."""

    def __init__(self, title: str, name: str) -> None:
        super().__init__(f"a ticket named {name} already exists; give {title!r} another title")
        self.title = title
        self.name = name


class BacklogItemTakenError(ValueError):
    """Raised when a new backlog item's title makes the file name of an idea already in the Backlog, which holds the
    only copy of that idea. It carries the title and that file."""

    def __init__(self, title: str, file: str) -> None:
        super().__init__(f"the Backlog already keeps an idea in {file}; give {title!r} another title")
        self.title = title
        self.file = file


class CardName:
    """*CardName* is the name a new card gets from its title: `pet-visits` for `Pet visits`, which names a ticket's
    session folder and branch, or a backlog item's file. Made from the title a person gave."""

    def __init__(self, title: str) -> None:
        self._title = title

    def for_new_card(self) -> str:
        """The name, refused when the title gives none or one too long, before any folder, file, or branch is made."""
        name = Name(self._title).title_slug
        if not name:
            raise TitleNamesNothingError(self._title)
        if len(name) > NAME_LENGTH_LIMIT:
            raise TitleTooLongError(self._title, name, NAME_LENGTH_LIMIT)
        return name
