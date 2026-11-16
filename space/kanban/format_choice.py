"""The format groups an action bar offers as chips, and which formats a chip stands for on the fidelities it acts on."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harness.guidance.guidance import FidelityGuidance
from harness.installation.data_class import data_field
from harness.markdown.format import Format

if TYPE_CHECKING:
    from space.session.file_manager import FileEntry


class FormatChoice:
    """*FormatChoice* is one chip of an action bar: a group of formats, the format each fidelity the bar acts on uses
    from it, how many of those fidelities offer it and have output in it already, and whether it is chosen for them in
    the session."""

    # A fidelity uses from a group the formats the session chose there; with none chosen, the project's default formats
    # in the group (drawio and whiteboard for a diagram), else its default format when the group holds it, else the
    # first format it offers there. A chip shows what the session keeps chosen (FidelitySessionOutput.chosen_formats),
    # so the chat bar, the board and the Story UI show one choice, and a chip standing for several formats does them all.

    def __init__(self, label: str, offering: list[tuple[FidelityGuidance, list[str], dict[str, list[FileEntry]]]]) -> None:
        self._label = label
        self._offering = offering

    @classmethod
    def offered_by(cls, read: list[tuple[FidelityGuidance, dict[str, list[FileEntry]]]]) -> list[FormatChoice]:
        """A chip for each group the fidelities offer, each fidelity read with its files, in the order the groups come."""
        offered = [name for fidelity, _ in read for name in fidelity.outputs]
        groups = [Format(name) for name in offered]
        labels = [label for label, _ in sorted(dict.fromkeys((format.group, format.group_order) for format in groups), key=lambda group: group[1])]
        return [cls(label, [(fidelity, in_group, files) for fidelity, files in read if (in_group := [name for name in fidelity.outputs if Format(name).group == label])]) for label in labels]

    @property
    @data_field
    def label(self) -> str:
        """The group, such as markdown or code, or a format in no group under its own name."""
        return self._label

    @property
    @data_field
    def formats(self) -> list[str]:
        """The formats each fidelity uses from the group, each once: what a command sends when the chip is picked, so
        the action runs once for each."""
        return list(dict.fromkeys(name for fidelity, in_group, _ in self._offering for name in self._used(fidelity, in_group)))

    @property
    @data_field
    def offered(self) -> int:
        """How many of the fidelities offer the group."""
        return len(self._offering)

    @property
    @data_field
    def made(self) -> int:
        """How many of the fidelities have a file in the group already."""
        return sum(1 for _, in_group, files in self._offering if any(entry.exists for name in in_group for entry in files.get(name, [])))

    @property
    @data_field
    def is_chosen(self) -> bool:
        """Whether every fidelity the chip covers has a format of the group chosen in the session: what the chip shows,
        the same choice the Story UI's toggles show."""
        return all(fidelity.session_output.chosen_from(in_group) for fidelity, in_group, _ in self._offering)

    def choose(self, is_chosen: bool) -> None:
        """Choose every format each fidelity the chip covers would use from the group, or leave out every format of the
        group chosen for it."""
        for fidelity, in_group, _ in self._offering:
            fidelity.session_output.choose_from(in_group, is_chosen)

    def _used(self, fidelity: FidelityGuidance, in_group: list[str]) -> list[str]:
        return fidelity.session_output.used_from(in_group)
