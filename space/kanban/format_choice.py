"""The format groups an action bar offers as chips, and which formats a chip stands for on the fidelities it acts on."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harness.guidance.guidance import FidelityGuidance
from harness.installation.data_class import data_field
from space.session.practices.guidance_selection import FormatGroup

if TYPE_CHECKING:
    from space.session.files.file_manager import FileEntry


class FormatChoice:
    """*FormatChoice* is one chip of an action bar: a group of formats, the format each fidelity the bar acts on uses
    from it, how many of those fidelities offer it and have output in it already, and whether it is chosen for them in
    the session."""

    # A fidelity uses from a group the formats the session chose there; with none chosen, every format of a diagram it
    # writes (the draw.io file and the Claude Whiteboard board), and for any other group the project's default formats
    # in it, else its default format when the group holds it, else the first format it offers there. A chip shows what
    # the session keeps chosen (FidelitySessionOutput.chosen_formats), so the chat bar, the board and the Story UI show
    # one choice, and a chip standing for several formats does them all.

    def __init__(self, group: FormatGroup, files: dict[str, dict[str, list[FileEntry]]]) -> None:
        self._group = group
        # Each fidelity's files by format, by the fidelity's slug.
        self._files = files

    @classmethod
    def offered_by(cls, read: list[tuple[FidelityGuidance, dict[str, list[FileEntry]]]]) -> list[FormatChoice]:
        """A chip for each group the fidelities offer, each fidelity read with its files, in the order the groups come."""
        files = {fidelity.slug: by_format for fidelity, by_format in read}
        return [cls(group, files) for group in FormatGroup.every([fidelity for fidelity, _ in read])]

    @property
    @data_field
    def label(self) -> str:
        """The group, such as markdown or code, or a format in no group under its own name."""
        return self._group.label

    @property
    @data_field
    def formats(self) -> list[str]:
        """The formats each fidelity uses from the group, each once: what a command sends when the chip is picked, so
        the action runs once for each."""
        return self._group.formats

    @property
    @data_field
    def offered(self) -> int:
        """How many of the fidelities offer the group."""
        return len(self._group.offering)

    @property
    @data_field
    def made(self) -> int:
        """How many of the fidelities have a file in the group already."""
        return sum(1 for fidelity in self._group.offering if any(entry.exists for name in self._group.in_group(fidelity) for entry in self._files.get(fidelity.slug, {}).get(name, [])))

    @property
    @data_field
    def is_chosen(self) -> bool:
        """Whether every fidelity the chip covers has a format of the group chosen in the session, and for a diagram
        each format of it the fidelity writes: what the chip shows, the same choice the Story UI's toggles show."""
        return self._group.is_selected

    def choose(self, is_chosen: bool) -> None:
        """Choose every format each fidelity the chip covers would use from the group, or leave out every format of the
        group chosen for it."""
        self._group.choose(is_chosen)
