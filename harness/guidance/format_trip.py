"""FormatTrip. A fidelity's example taken to one of its formats and back, and what came back of it.

A practice owns its formats: each format a fidelity declares must return what went in, or say what it cannot hold and
where that content is kept. The trip renders the example into the format, renders that back into the format the
example is written in, and compares what came back, line by line, with the example as its own format writes it. A
fidelity names its example (``example``) and what each format leaves out (``leaves_out``) in its block of the
practice document.

What a render does to a file already there is the Render action's to keep, and its own specs': the trip asks only
what the format itself holds.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

from harness.guidance.practice_formats import ExistingText, RenderRequest
from harness.markdown.format import Format

if TYPE_CHECKING:
    from harness.guidance.guidance import FidelityGuidance

RETURNS_WHAT_WENT_IN = "returns what went in"
"""The format holds everything the example holds."""
NOT_HELD_BY_THIS_FORMAT = "not held by this format"
"""The format holds less than the example, or is never read back, and its fidelity says what it leaves out and where
that content is kept."""
HOLDS_LESS_UNSAID = "holds less and does not say what"
"""As above, but its fidelity names nothing it leaves out, so nobody who picks the format is told."""
FAILS_ON_THE_WAY = "fails on the way"
"""Writing the format, or reading it back, raised a failure."""
NO_EXAMPLE = "names no example"
"""The fidelity names no example in its practice document, so none of its formats was taken there and back."""


class ExampleNotThere(FileNotFoundError):
    """A fidelity names an example its practice's folder does not hold."""

    def __init__(self, named: str, folder: Path) -> None:
        super().__init__(f"the example {named} is not in {folder}")


@dataclass(frozen=True)
class TripOutcome:
    """What one trip came to: its status, the lines of the example that did not come back, what the fidelity says the
    format leaves out, and the failure raised on the way."""

    status: str
    lost: tuple[str, ...] = ()
    leaves_out: str = ""
    refused: str = ""

    @property
    def passes(self) -> bool:
        """Whether the format returns what went in, or its fidelity says what it does not hold."""
        return self.status in (RETURNS_WHAT_WENT_IN, NOT_HELD_BY_THIS_FORMAT)

    def __str__(self) -> str:
        return self.status


class FidelityExample:
    """The worked example a fidelity names in its practice document, by its path in the practice's folder: one file,
    read as its text and written in the format of its extension, or a folder of code, read as its files by their paths
    and written in the code format most of them are in."""

    def __init__(self, folder: Path, named: str, default_format: Format) -> None:
        self._folder = folder
        self._named = named
        self._default_format = default_format

    @property
    def path(self) -> Path:
        """Where the example is; raises *ExampleNotThere* when the practice's folder does not hold it."""
        path = self._folder / self._named
        if not path.exists():
            raise ExampleNotThere(self._named, self._folder)
        return path

    @property
    def content(self) -> str | dict[str, str]:
        path = self.path
        if path.is_file():
            return path.read_text(encoding="utf-8")
        files = sorted(file for file in path.rglob("*") if file.is_file() and "__pycache__" not in file.parts)
        return {file.relative_to(path).as_posix(): file.read_text(encoding="utf-8") for file in files}

    @property
    def written_in(self) -> Format:
        """The format of the file's extension; for a folder, the code format most of its files are written in, else
        the format the fidelity works in."""
        path = self.path
        if path.is_file():
            return Format.from_extension(path.suffix)
        written = [Format.from_extension(Path(name).suffix) for name in self.content if Path(name).suffix]
        code = [format for format in written if format.is_code]
        return max(dict.fromkeys(code), key=code.count) if code else self._default_format


FORMAT_FAILURES = (ValueError, LookupError, SyntaxError, NotImplementedError)
"""What a format raises when it cannot write or read back the content it is handed: a value it cannot hold or parse, a
name or key it cannot find, source it cannot parse, or a direction it does not go. A trip reports these as the format's
outcome; any other failure is a bug in the trip or the adapter, and is raised."""


class FormatTrip:
    """One fidelity's example, written in one of its formats, taken to its other formats and back. The example is
    text, or the files of a code format by their paths; a fidelity that names no example has none, and each of its
    formats comes to the outcome saying so."""

    def __init__(self, fidelity: FidelityGuidance, example: str | dict[str, str] | None, written_in: str) -> None:
        self._fidelity = fidelity
        self._example = example
        self._written_in = Format(written_in)

    @classmethod
    def of(cls, fidelity: FidelityGuidance) -> FormatTrip:
        """The trip of the example fidelity names; one with no example for a fidelity that names none."""
        if not fidelity.example:
            return cls(fidelity, None, "")
        example = FidelityExample(fidelity.module_dir, fidelity.example, fidelity.default_format)
        return cls(fidelity, example.content, str(_declared_for(fidelity, example.path) or example.written_in))

    @property
    def _offered(self) -> list[Format]:
        """The formats the fidelity declares in its outputs. An output named for what it holds, such as the story map's
        ``thin_slice``, is left out: its files are written in formats the fidelity declares beside it."""
        fidelity = self._fidelity
        return [Format(output) for output in fidelity.declared.outputs if Format(output).is_offered or output in fidelity.practice_guidance.formats]

    def through_each(self) -> dict[str, TripOutcome]:
        """The outcome of the trip through each format its fidelity declares, but the one the example is written in;
        with no example, each declared format with the outcome saying so, since a format nobody took there and back is
        not known to hold anything."""
        if self._example is None:
            return {str(format): TripOutcome(NO_EXAMPLE) for format in self._offered}
        return {str(format): self.through(str(format)) for format in self._offered if format != self._written_in}

    def through(self, format: str) -> TripOutcome:
        """The outcome of taking the example to format and back. What comes back is compared with the example as its
        own format writes it, so the spelling that format chooses, such as its quotes, is not counted as lost. A format
        nothing reads back, which refuses the read with ``NotImplementedError``, holds none of the example. A format
        that cannot write or read the example (one of ``FORMAT_FAILURES``) fails on the way; any other failure raises."""
        if self._example is None:
            return TripOutcome(NO_EXAMPLE)
        leaves_out = str(self._fidelity.leaves_out.get(str(Format(format)), "") or "")
        said = NOT_HELD_BY_THIS_FORMAT if leaves_out else HOLDS_LESS_UNSAID
        try:
            went_in = ExistingText(_text_of(self._rendered(self._written_in, self._example, self._written_in)))
            there = self._rendered(Format(format), self._example, self._written_in)
        except FORMAT_FAILURES as failure:
            return TripOutcome(FAILS_ON_THE_WAY, leaves_out=leaves_out, refused=f"{type(failure).__name__}: {failure}")
        if not went_in.lines_not_in(""):
            # An example its own format reads as nothing would pass every trip, having nothing to lose.
            return TripOutcome(FAILS_ON_THE_WAY, leaves_out=leaves_out, refused=f"{self._written_in} reads nothing from the example")
        try:
            back = self._rendered(self._written_in, there, Format(format))
        except NotImplementedError as never_read:
            return TripOutcome(said, tuple(went_in.lines_not_in("")), leaves_out, f"{type(never_read).__name__}: {never_read}")
        except FORMAT_FAILURES as failure:
            return TripOutcome(FAILS_ON_THE_WAY, leaves_out=leaves_out, refused=f"{type(failure).__name__}: {failure}")
        lost = went_in.lines_not_in(_text_of(back))
        return TripOutcome(said if lost else RETURNS_WHAT_WENT_IN, tuple(lost), leaves_out)

    def _rendered(self, format: Format, content: Any, source: Format) -> Any:
        return RenderRequest(format, content, source, fidelity=self._fidelity).render().content


def _declared_for(fidelity: FidelityGuidance, file: Path) -> Format | None:
    """The format fidelity declares files of this file's ending in, so a view in ``.tsx`` is TypeScript; none for a
    folder, an ending that names one of the practice's formats itself, or an ending no declared file has."""
    if not file.is_file() or Format.from_extension(file.suffix) in fidelity.practice_guidance.formats:
        return None
    declared = fidelity.declared
    named = (output for output in declared.outputs if any(str(path).endswith(file.suffix) for path in declared.paths_in(output)))
    return next((Format(output) for output in named if Format(output).is_offered), None)


def _text_of(content: Any) -> str:
    """content as one text; a format written as several files is read as their texts one after another."""
    return "\n".join(str(part) for part in content.values()) if isinstance(content, dict) else str(content)
