"""The addresses in Claude that things in one folder were published to, kept beside them in a JSON record: a design
canvas's versions in ``versions.json``. The next publish updates the same artifact, and a page opens the artifact
instead of the file."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from harness.installation.json_file import JsonFile, JsonFileUnreadable


class PublishedLinksUnreadable(JsonFileUnreadable):
    """The record of where a folder's files were published in Claude cannot be read. Nothing is recorded over it, since
    a record written then would hold one address and lose every other file's."""

    def message(self, path: Path, cause: Exception) -> str:
        return (f"{path} keeps the addresses in Claude this folder's files were published to, but is not a readable "
                f"JSON object ({cause}); repair or remove it, and nothing is recorded in it until then")


# The key an entry keeps its address under when it keeps more than the address beside it.
_LINK = "link"


class PublishedLinks:
    """Each published thing's address in Claude, by its name, in the order they were published, as one record keeps
    them: a design canvas's version folder. An entry is its address alone, or, when something is kept beside the
    address, an object holding the address under ``link`` and the rest beside it, such as the values a person accepted
    that a canvas version's screens leave out."""

    def __init__(self, record: JsonFile) -> None:
        self._record = record

    def all(self) -> Dict[str, str]:
        """Each address kept, by name; none while no record is kept. A record that cannot be read raises
        *PublishedLinksUnreadable*, naming the file."""
        kept = self._entries()
        return {str(name): str(entry.get(_LINK, "")) if isinstance(entry, dict) else str(entry) for name, entry in kept.items()}

    def beside(self, name: str) -> Dict[str, Any]:
        """What is kept beside name's address; nothing when its address was recorded alone."""
        entry = self._entries().get(name)
        return {key: value for key, value in entry.items() if key != _LINK} if isinstance(entry, dict) else {}

    def _entries(self) -> Dict[str, Any]:
        """Each entry the record keeps, by name, as it keeps it."""
        try:
            return dict(self._record.read())
        except JsonFileUnreadable as unreadable:
            raise PublishedLinksUnreadable(unreadable.path, unreadable.cause) from unreadable

    def of(self, name: str) -> Optional[str]:
        """The address name was published at; none while it was never published."""
        return self.all().get(name)

    def record(self, name: str, url: str, beside: Optional[Dict[str, Any]] = None) -> None:
        """Keep url as the address name was published at, with what beside holds kept next to it."""
        self._record.write({**self._entries(), name: {_LINK: url, **beside} if beside else url})

    def rename(self, name: str, new: str) -> None:
        """Keep name's address, and what is beside it, under new, the name the published thing now has, in the same
        place in the order."""
        self._record.write({(new if key == name else key): entry for key, entry in self._entries().items()})
