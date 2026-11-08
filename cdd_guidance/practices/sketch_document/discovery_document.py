"""The document a practice writes at discovery fidelity from a sketch: the front matter naming its artifact, a heading
with the sketch's title, the sketch's sources, then the practice's own body. Stories' story map and DDD's bounded
context map both write one, so its header is written in one place."""

from __future__ import annotations

from typing import List

from cdd_guidance.practices.sketch_document.sketch_outline import SketchOutline

_UNTITLED = "Product / Feature Name"
_NO_SOURCES = "see engagement sketch"


class DiscoveryDocument:
    """A discovery document written from a sketch: its artifact (`story-map`), its heading (`Story Map`), and the title
    and sources the sketch's header gives, read by the sketch's *SketchOutline*, so the header is where its practice
    sections say it is."""

    def __init__(self, artifact: str, heading: str, sketch: str) -> None:
        outline = SketchOutline(sketch)
        self.artifact = artifact
        self.heading = heading
        self.title = outline.title or _UNTITLED
        self.sources = outline.sources or _NO_SOURCES

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
