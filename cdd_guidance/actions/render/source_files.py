"""The files a render reads, and the one format they are read in."""
from __future__ import annotations

from pathlib import Path

from harness.guidance.documents import files_read_from, is_text
from harness.guidance.guidance import FidelityGuidance
from harness.guidance.practice_formats import PracticeFormats
from harness.markdown.format import Format

# A saved graph, which a render reads as data, whatever the name of its file says.
SAVED_GRAPH_SUFFIX = ".json"
_SKETCH = Format("sketch")
_MARKDOWN = Format("markdown")


class SourceFormatRefused(ValueError):
    """A render was asked to read files in a format they are not in, or in one the fidelity reads none of: read so, a
    markdown document is parsed as Python and refused as code that does not parse, which names no file."""

    def __init__(self, reason: str, files: dict[Path, Format]) -> None:
        named = ", ".join(f"{file.name} ({format or 'no format'})" for file, format in files.items())
        super().__init__(f"{reason}: {named}")
        self.files = files


class SourceFiles:
    """The files the paths of one render name, each in the format its name says it is in: a sketch by the ending its
    name carries (``orders-sketch.md``), any other file by its extension. A folder holds the text files a document read
    from it is made of. A saved graph is read as data by the render itself, so its name gives no format."""

    def __init__(self, sources: list[Path], worked: object) -> None:
        self._sources = sources
        self._worked = worked

    def format_read_in(self, named: str | None) -> str | None:
        """The format the files are read in: named, the one the call gives, which every file named directly must be in;
        else the one their names say, the same for all of them. Refused by name when a file is in another format than
        the call gives, when the files are in different formats, or when the fidelity reads none of them. None for a
        saved graph, which the render reads as data."""
        if named:
            self._refuse_other_than(Format(named))
            return named
        found = self._format_of_files()
        if found:
            self._refuse_unread(found)
        return found or None

    def _refuse_other_than(self, named: Format) -> None:
        """Refuse when a file the call names directly is, by its name, in another format than named. A sketch is
        markdown, so a sketch read as markdown, or markdown read as a sketch, is in the format named."""
        files = {source: self._format_of(source) for source in self._sources if source.is_file()}
        other = {file: format for file, format in files.items() if format and not self._is_read_as(format, named)}
        if other:
            raise SourceFormatRefused(f"the render was asked to read {named}, and these files are not in it", other)

    def _is_read_as(self, format: Format, named: Format) -> bool:
        return format == named or {format, named} <= {_SKETCH, _MARKDOWN}

    def _format_of_files(self) -> Format:
        """The one format the files are in by their names; for a folder holding files in several formats, the one the
        fidelity works in, when it is among them. Refused when they are in several."""
        files = {file: self._format_of(file) for source in self._sources for file in self._files_of(source)}
        found = {format for format in files.values() if format}
        works_in = getattr(self._worked, "format", Format())
        if len(found) > 1 and any(source.is_dir() for source in self._sources) and works_in in found:
            return works_in
        if len(found) > 1:
            raise SourceFormatRefused("the render was asked to read files in different formats, so no one format reads them all", files)
        return next(iter(found), Format())

    def _refuse_unread(self, found: Format) -> None:
        """Refuse when the fidelity rendered at reads no file in found."""
        formats = self._rendering_formats()
        if formats is None or found in formats:
            return
        files = {source: found for source in self._sources}
        raise SourceFormatRefused(f"{self._worked.slug} reads no {found} file; it reads {', '.join(sorted(formats))}", files)

    def _rendering_formats(self) -> PracticeFormats | None:
        """The formats that read the fidelity's files: its practice's, else those of its Clean Engineering companion,
        which renders for a practice with no adapters of its own. None when neither has any, or for guidance that is no
        fidelity, which says nothing about what it reads."""
        if not isinstance(self._worked, FidelityGuidance):
            return None
        formats = self._worked.practice_guidance.formats
        companion = self._worked.clean_engineering
        if not len(formats) and companion is not None:
            formats = companion.practice_guidance.formats
        return formats if len(formats) else None

    def _files_of(self, source: Path) -> list[Path]:
        """The files a source is read from: itself, or the text files of a folder."""
        return [source] if source.is_file() else [file for file in files_read_from(source) if is_text(file)]

    def _format_of(self, file: Path) -> Format:
        """The format file's name says it is in; none for a saved graph."""
        if file.suffix == SAVED_GRAPH_SUFFIX:
            return Format()
        return _SKETCH if _SKETCH.names(file) else Format.from_extension(file.suffix)
