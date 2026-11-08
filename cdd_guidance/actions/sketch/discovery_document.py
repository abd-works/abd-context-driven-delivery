"""The document a practice writes at discovery fidelity from a sketch: the front matter naming its artifact, a heading
with the sketch's title, the sketch's sources, then the practice's own body. Stories' story map and DDD's bounded
context map both write one, so its header is written in one place."""

from __future__ import annotations

import re
from typing import List

_TITLE = "# "
_SECTION = "## "
_SOURCE = "source:"
_SKETCH_SUFFIX = re.compile(r"\s+sketch\s*$", re.IGNORECASE)
_TRAILING_SEPARATOR = re.compile(r"[\s\-–—€”]+$")
_UNTITLED = "Product / Feature Name"
_NO_SOURCES = "see engagement sketch"


class DiscoveryDocument:
    """A discovery document written from a sketch, read once: its artifact (`story-map`), its heading (`Story Map`),
    and the title and sources the sketch's header gives, which is the lines above its first practice section."""

    def __init__(self, artifact: str, heading: str, sketch: str) -> None:
        self.artifact = artifact
        self.heading = heading
        self.title = _UNTITLED
        self.sources = _NO_SOURCES
        self._read_header(sketch)

    def lines(self, body: str) -> List[str]:
        """The document: front matter, the `# {heading} — {title}` line, the sources, a rule, then body."""
        return [
            "---",
            "fidelity: [discovery]",
            f"artifact: [{self.artifact}]",
            "format: md",
            "---",
            "",
            f"# {self.heading} — {self.title}",
            "",
            f"**Sources / context:** {self.sources}",
            "",
            "---",
            "",
            body.rstrip(),
            "",
        ]

    def _read_header(self, sketch: str) -> None:
        for line in sketch.splitlines():
            stripped = line.strip()
            if stripped.startswith(_SECTION):
                return
            if stripped.startswith(_TITLE):
                titled = _SKETCH_SUFFIX.sub("", stripped[len(_TITLE):].strip()).strip()
                self.title = _TRAILING_SEPARATOR.sub("", titled).strip() or titled
            elif stripped.lower().startswith(_SOURCE):
                self.sources = stripped.split(":", 1)[1].strip()
