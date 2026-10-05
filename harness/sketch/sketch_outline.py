"""The sketch document — one section per practice, hierarchy carried by markdown headings."""

from __future__ import annotations


class SketchLens:
    """The section of a sketch that one practice writes."""

    stories: "SketchLens"
    clean_engineering: "SketchLens"
    domain_driven_design: "SketchLens"
    user_experience: "SketchLens"
    behavior_driven_development: "SketchLens"
    every: tuple["SketchLens", ...]

    def __init__(self, titles: tuple[str, ...]) -> None:
        self.titles = titles

    def opens(self, title: str) -> bool:
        """True when this title is the section heading or marker this practice writes under."""
        return title.strip().lower() in self.titles


SketchLens.stories = SketchLens(("stories:",))
SketchLens.clean_engineering = SketchLens(("ce:", "clean engineering:"))
SketchLens.domain_driven_design = SketchLens(("ddd:", "domain driven design:"))
SketchLens.user_experience = SketchLens(("ux:", "user experience:"))
SketchLens.behavior_driven_development = SketchLens(
    ("bdd:", "behavior driven development:")
)
SketchLens.every = (
    SketchLens.stories,
    SketchLens.clean_engineering,
    SketchLens.domain_driven_design,
    SketchLens.user_experience,
    SketchLens.behavior_driven_development,
)

_HORIZONTAL_RULES = {"---", "***", "___"}


class _Section:
    """Where one lens starts, where it ends, and the heading depth that opened it."""

    def __init__(self, first: int, last: int, depth: int) -> None:
        self.first = first
        self.last = last
        self.depth = depth


class SketchOutline:
    """A sketch whose hierarchy is carried by markdown headings above fenced detail.

    Each heading becomes one nesting level of `nesting_indent` spaces, so a practice
    reads the shape it already knows. Detail inside a fence keeps its own relative
    indentation under the heading that owns it."""

    def __init__(self, text: str, nesting_indent: int = 2) -> None:
        self._lines = text.splitlines()
        self._nesting_indent = nesting_indent

    def holds(self, lens: SketchLens) -> bool:
        """True when this sketch has a section for that practice."""
        return self._section_for(lens) is not None

    def body_for(self, lens: SketchLens) -> str:
        """That practice's section, flattened to indentation.

        A sketch that names no lens is a single section, so the whole document is its body."""
        section = self._section_for(lens)
        if section is None:
            if self._names_a_lens:
                return ""
            section = _Section(0, len(self._lines), 0)
        return self._flattened(section)

    @property
    def _names_a_lens(self) -> bool:
        return any(
            any(lens.opens(title) for lens in SketchLens.every)
            for _, _, title in self._outline
        )

    @property
    def _outline(self) -> list[tuple[int, int, str]]:
        """Every line outside a fence, as index, heading depth, and text."""
        found: list[tuple[int, int, str]] = []
        fenced = False
        for index, raw in enumerate(self._lines):
            stripped = raw.strip()
            if stripped.startswith("```"):
                fenced = not fenced
                continue
            if fenced or not stripped:
                continue
            depth = len(stripped) - len(stripped.lstrip("#"))
            found.append((index, depth, stripped[depth:].strip()))
        return found

    def _section_for(self, lens: SketchLens) -> _Section | None:
        outline = self._outline
        opening = next(
            ((index, depth) for index, depth, title in outline if lens.opens(title)),
            None,
        )
        if opening is None:
            return None
        index, depth = opening
        return _Section(index + 1, self._end_after(outline, index, depth), depth)

    def _end_after(self, outline: list[tuple[int, int, str]], index: int, depth: int) -> int:
        for other, other_depth, title in outline:
            if other <= index:
                continue
            if other_depth and other_depth <= depth:
                return other
            if any(lens.opens(title) for lens in SketchLens.every):
                return other
        return len(self._lines)

    def _flattened(self, section: _Section) -> str:
        base = self._base_depth(section)
        written: list[str] = []
        indent = 0
        fenced = False
        for raw in self._lines[section.first : section.last]:
            stripped = raw.strip()
            if stripped.startswith("```"):
                fenced = not fenced
                continue
            if not stripped:
                written.append("")
                continue
            if fenced:
                written.append(" " * indent + raw)
                continue
            if stripped in _HORIZONTAL_RULES:
                continue
            depth = len(stripped) - len(stripped.lstrip("#"))
            if not depth:
                written.append(" " * indent + raw)
                continue
            level = max(depth - base, 0)
            written.append(" " * (level * self._nesting_indent) + stripped[depth:].strip())
            indent = (level + 1) * self._nesting_indent
        return "\n".join(written) + "\n"

    def _base_depth(self, section: _Section) -> int:
        depths = [
            depth
            for index, depth, _ in self._outline
            if section.first <= index < section.last and depth
        ]
        return min(depths) if depths else section.depth + 1
