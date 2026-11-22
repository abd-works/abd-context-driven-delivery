"""The addresses in Claude that files in one folder were published to, kept beside them in a JSON record: a design
canvas's versions in ``versions.json``, and each ``.whiteboard`` file's board in ``whiteboards.json``. The next
publish updates the same artifact, and a page opens the artifact instead of the file."""

from __future__ import annotations

from typing import Dict, Optional

from harness.installation.json_file import JsonFile, JsonFileUnreadable


class PublishedLinks:
    """Each published thing's address in Claude, by its name, in the order they were published, as one record keeps
    them: a design canvas's version folder, or a whiteboard file's name."""

    def __init__(self, record: JsonFile) -> None:
        self._record = record

    def all(self) -> Dict[str, str]:
        """Each address kept, by name; none when the record keeps none, or holds something that is no record of
        them."""
        try:
            kept = self._record.read()
        except JsonFileUnreadable:
            return {}
        return {str(name): str(url) for name, url in kept.items()}

    def of(self, name: str) -> Optional[str]:
        """The address name was published at; none while it was never published."""
        return self.all().get(name)

    def named_at(self, url: str) -> Optional[str]:
        """The name published at url; none when nothing this record keeps was published there."""
        return next((name for name, kept in self.all().items() if kept == url), None)

    def record(self, name: str, url: str) -> None:
        """Keep url as the address name was published at."""
        self._record.write({**self.all(), name: url})

    def rename(self, name: str, new: str) -> None:
        """Keep name's address under new, the name the published thing now has, in the same place in the order."""
        self._record.write({(new if key == name else key): url for key, url in self.all().items()})
