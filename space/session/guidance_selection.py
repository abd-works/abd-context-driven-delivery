"""Guidance selection — the stages, practices, and formats a session's work shows and acts on.

The chat bar's stage buttons, practice dots, and format chips, and the Files app's toggles, are all one selection the
session holds: which stages are selected, which practices the session works on, and which formats are chosen for the
fidelities those cover. Every change goes through ``Session.update_guidance_selection`` and raises the selection's
version, so a page waiting on ``Session.guidance_selection_after`` hears it at once.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from harness.guidance.stages import STAGES
from harness.installation.data_class import data_field
from harness.markdown.format import Format

if TYPE_CHECKING:
    from harness.guidance.guidance import FidelityGuidance
    from space.session.practice_session_output import PracticeSessionOutput
    from space.session.session import Session


class StageSelection:
    """One stage of the approach, selected or not: its fidelities show and its work is acted on while it is."""

    def __init__(self, name: str, title: str, is_selected: bool) -> None:
        self._name = name
        self._title = title
        self._is_selected = is_selected

    @property
    @data_field
    def name(self) -> str:
        """The stage as a fidelity's **Stage:** names it, such as `discovery`: what a selection change names."""
        return self._name

    @property
    @data_field
    def title(self) -> str:
        """The stage as a board heads its column, such as `Discovery`."""
        return self._title

    @property
    @data_field
    def is_selected(self) -> bool:
        return self._is_selected


class PracticeSelection:
    """One practice, selected or not: selected is the session working on it, so its fidelities of the stages selected
    show and are acted on."""

    def __init__(self, output: PracticeSessionOutput) -> None:
        self._output = output

    @property
    @data_field
    def key(self) -> str:
        return self._output.name

    @property
    @data_field
    def short_name(self) -> str:
        return self._output.short_name

    @property
    @data_field
    def colour(self) -> str:
        return self._output.colour

    @property
    @data_field
    def is_selected(self) -> bool:
        return self._output.enabled


class FormatGroup:
    """One group of formats some fidelities offer, such as markdown, code, or a diagram's drawio and whiteboard, as each
    of them works in it in the session: chosen while every one of them has a format of the group chosen. The chat bar's
    format chips (*FormatSelection*) and an action bar's chips (*FormatChoice*, space/kanban) each show one."""

    def __init__(self, label: str, offering: list[FidelityGuidance]) -> None:
        self._label = label
        self._offering = list(offering)

    @classmethod
    def every(cls, fidelities: list[FidelityGuidance]) -> list[FormatGroup]:
        """A group for each group of formats the fidelities offer, in the order the groups come, each with the
        fidelities that offer it."""
        offered = [Format(name) for fidelity in fidelities for name in fidelity.outputs]
        labels = [label for label, _ in sorted(dict.fromkeys((each.group, each.group_order) for each in offered), key=lambda group: group[1])]
        return [cls(label, [fidelity for fidelity in fidelities if any(Format(name).group == label for name in fidelity.outputs)]) for label in labels]

    @property
    def label(self) -> str:
        return self._label

    @property
    def offering(self) -> list[FidelityGuidance]:
        return list(self._offering)

    @property
    def formats(self) -> list[str]:
        """The formats each fidelity uses from the group, each once: what an action sends while the group is chosen, the
        action running once for each."""
        return list(dict.fromkeys(name for fidelity in self._offering for name in fidelity.session_output.formats.used_from(self.in_group(fidelity))))

    @property
    def is_chosen(self) -> bool:
        return all(fidelity.session_output.formats.chosen_from(self.in_group(fidelity)) for fidelity in self._offering)

    def choose(self, is_chosen: bool) -> None:
        """Choose every format each fidelity offering the group would use from it, or leave out every one chosen."""
        for fidelity in self._offering:
            fidelity.session_output.formats.choose_from(self.in_group(fidelity), is_chosen)

    def in_group(self, fidelity: FidelityGuidance) -> list[str]:
        """The formats fidelity offers in the group."""
        return [name for name in fidelity.outputs if Format(name).group == self._label]


class FormatSelection:
    """One group of formats the selected fidelities offer, as the chat bar's format chips show it: selected while every
    one of them offering it has a format of the group chosen in the session."""

    def __init__(self, group: FormatGroup) -> None:
        self._group = group

    @property
    @data_field
    def label(self) -> str:
        return self._group.label

    @property
    @data_field
    def formats(self) -> list[str]:
        return self._group.formats

    @property
    @data_field
    def offered(self) -> int:
        """How many of the selected fidelities offer the group."""
        return len(self._group.offering)

    @property
    @data_field
    def is_selected(self) -> bool:
        return self._group.is_chosen

    def select(self, is_selected: bool) -> None:
        self._group.choose(is_selected)


class GuidanceSelection:
    """The session's guidance selection as it stands: each stage and practice selected or not, the formats the
    fidelities they cover offer, each selected or not, and those fidelities, with the version every change raises."""

    def __init__(self, session: Session) -> None:
        self._session = session
        saved = dict(session.record.fields.get(GUIDANCE_FIELD, {}))
        self._version = int(saved.get("version", 0))
        self._stages: list[str] | None = saved.get("stages")

    @property
    @data_field
    def version(self) -> int:
        """Raised by every change, so a page that drew version N waits for N + 1 and ignores any answer older."""
        return self._version

    @property
    @data_field
    def is_stage_chosen(self) -> bool:
        """Whether stages were ever selected for the session, none included: before that, a page selects the stage the
        session's ticket is in."""
        return self._stages is not None

    @property
    @data_field
    def stages(self) -> list[StageSelection]:
        chosen = self._stages or []
        return [StageSelection(stage.name, stage.title, stage.name in chosen) for stage in STAGES]

    @property
    @data_field
    def practices(self) -> list[PracticeSelection]:
        return [PracticeSelection(output) for output in self._outputs]

    @property
    @data_field
    def formats(self) -> list[FormatSelection]:
        return [FormatSelection(group) for group in FormatGroup.every(self.covered)]

    @property
    @data_field
    def fidelities(self) -> list[str]:
        """The fidelities the stages and practices selected translate to, by slug, in stage order: what the dots stand
        for, what an action runs on, and whose files a page lists. A filter with nothing selected filters nothing, so no
        stage selected means every stage, and no practice selected every practice."""
        return [fidelity.slug for fidelity in self.covered]

    @property
    def covered(self) -> list[FidelityGuidance]:
        stages = self._stages or [stage.name for stage in STAGES]
        outputs = [output for output in self._outputs if output.enabled] or self._outputs
        return [fidelity for stage in STAGES if stage.name in stages for output in outputs for fidelity in output.guidance.fidelities.entries.values() if fidelity.stage == stage.name]

    @property
    def stages_chosen(self) -> list[str]:
        return list(self._stages or [])

    @property
    def _outputs(self) -> list[PracticeSessionOutput]:
        return list(self._session.own_practices.values())


# Where session.json keeps the selection: the stages selected and the version. Practices are each practice's own
# ``enabled``, and formats each fidelity's own chosen formats, so every other reader of those sees the same choice.
GUIDANCE_FIELD = "guidance"
