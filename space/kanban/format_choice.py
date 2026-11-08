"""The format groups an action bar offers as chips, and which formats a chip stands for on the fidelities it acts on."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harness.guidance.guidance import FidelityGuidance
from harness.installation.destination import data_field
from harness.markdown.format import Format

if TYPE_CHECKING:
    from space.session.file_manager import FileEntry


class FormatGroup:
    """*FormatGroup* is one group a person picks formats by, such as code, with the formats it holds. The board sends
    every group, so the page orders a fidelity's files by group without a list of formats of its own."""

    def __init__(self, label: str, formats: tuple[str, ...]) -> None:
        self._label = label
        self._formats = formats

    @classmethod
    def every(cls) -> list[FormatGroup]:
        return [cls(label, formats) for label, formats in Format.GROUPS.items()]

    @property
    @data_field
    def label(self) -> str:
        return self._label

    @property
    @data_field
    def formats(self) -> list[str]:
        return list(self._formats)


class FormatChoice:
    """*FormatChoice* is one chip of an action bar: a group of formats, the format each fidelity the bar acts on uses
    from it, how many of those fidelities offer it and have output in it already, and whether the bar opens with it
    picked."""

    # A fidelity uses its default format from a group that holds it, else the first format it offers there. A bar
    # opens ready to run: on each group that holds a fidelity's default, unless output is already there in it.

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
        """The format each fidelity uses from the group, each once: what a command sends when the chip is picked."""
        return list(dict.fromkeys(self._used(fidelity, in_group) for fidelity, in_group, _ in self._offering))

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
    def starts_picked(self) -> bool:
        """Whether the bar opens with the chip picked: it holds a fidelity's default format and nothing is made in it."""
        return self.made == 0 and any(fidelity.default_format in in_group for fidelity, in_group, _ in self._offering)

    def _used(self, fidelity: FidelityGuidance, in_group: list[str]) -> str:
        return fidelity.default_format if fidelity.default_format in in_group else in_group[0]
