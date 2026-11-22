"""Guidance selection — the stages, practices, and formats a session's work shows and acts on.

The chat bar's stage buttons, practice dots, and format chips, and the Files app's toggles, are all one selection the
session holds (``session.guidance``): which stages are selected, which practices the session works on, and which formats
are chosen for the fidelities those cover. A press changes it through ``Session.toggle_guidance``; every change raises
its version once, so a page waiting on ``Session.guidance_selection_after`` hears it at once. It writes the command an
action runs on its fidelities, the one place a command and its ``format=`` are written.
"""
from __future__ import annotations

import threading
import time
from typing import TYPE_CHECKING, Callable, ClassVar, Literal

from harness.guidance.action_catalogue import ACTION_CATALOGUE
from harness.guidance.stages import STAGES
from harness.installation.data_class import data_field
from space.session.practices.file_listing import FileListing
from harness.markdown.format import Format
from harness.process.answer_reads import HeldForAnswer

if TYPE_CHECKING:
    from harness.guidance.guidance import FidelityGuidance
    from space.session.practices.practice_session_output import PracticeSessionOutput
    from space.session.session import Session

# How long a page's waiting read of the guidance selection waits for a change before answering it unchanged, and how
# often it looks for a change another process wrote.
GUIDANCE_WAIT_SECONDS = 25
GUIDANCE_CHECK_SECONDS = 1.0
# Wakes every waiting read of a guidance selection this server changed, so none of them checks the disk in a loop.
_GUIDANCE_CHANGED = threading.Condition()

# The part of the selection a press toggles: a stage, a practice, or a format group.
SelectionPart = Literal["stage", "practice", "format"]


class UnknownSelectionPart(ValueError):
    """A press named a part of the guidance selection there is none of: the parts are stage, practice, and format."""

    def __init__(self, part: str) -> None:
        super().__init__(f"no part {part!r} of the guidance selection; the parts are stage, practice, and format")
        self.part = part


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
    of them works in it in the session: chosen while every one of them has a format of the group chosen, and for a
    diagram every format of it the fidelity writes. The chat bar's format chips read it as it is, and an action bar's
    chips (*FormatChoice*, space/kanban) each show one."""

    def __init__(self, label: str, offering: list[FidelityGuidance]) -> None:
        self._label = label
        self._offering = list(offering)

    @classmethod
    def every(cls, fidelities: list[FidelityGuidance]) -> list[FormatGroup]:
        """A group for each group of formats the fidelities offer, in the order the groups come, each with the
        fidelities that offer it."""
        offered = [Format(name) for fidelity in fidelities for name in fidelity.session_output.offered_formats]
        labels = [label for label, _ in sorted(dict.fromkeys((each.group, each.group_order) for each in offered), key=lambda group: group[1])]
        return [cls(label, [fidelity for fidelity in fidelities if any(Format(name).group == label for name in fidelity.session_output.offered_formats)]) for label in labels]

    @property
    @data_field
    def label(self) -> str:
        return self._label

    @property
    def offering(self) -> list[FidelityGuidance]:
        return list(self._offering)

    @property
    @data_field
    def offered(self) -> int:
        """How many of the fidelities offer the group."""
        return len(self._offering)

    @property
    @data_field
    def formats(self) -> list[str]:
        """The formats each fidelity uses from the group, each once: what an action sends while the group is chosen, the
        action running once for each."""
        return list(dict.fromkeys(name for fidelity in self._offering for name in fidelity.session_output.formats.used_from(self.in_group(fidelity))))

    @property
    @data_field
    def is_selected(self) -> bool:
        """Whether the group is chosen for every fidelity offering it."""
        return all(fidelity.session_output.formats.is_chosen_from(self.in_group(fidelity)) for fidelity in self._offering)

    def choose(self, is_chosen: bool) -> None:
        """Choose every format each fidelity offering the group would use from it, or leave out every one chosen."""
        for fidelity in self._offering:
            fidelity.session_output.formats.choose_from(self.in_group(fidelity), is_chosen)

    def in_group(self, fidelity: FidelityGuidance) -> list[str]:
        """The formats fidelity offers in the group."""
        return [name for name in fidelity.session_output.offered_formats if Format(name).group == self._label]


class GuidanceSelection:
    """The session's guidance selection, which the session holds and which changes itself: each stage and practice
    selected or not, the formats the fidelities they cover offer, each selected or not, those fidelities, the command
    each action runs on them, and the version every change raises. Each answer reads it from the session's record as it
    is then."""

    # The stage the session's ticket stands in, which the board keeps and registers how to read
    # (``start_on_ticket_stage_with``): before anyone chose stages, the selection shows that stage selected, so turning
    # every stage off later shows none. None registered, as in a process that loads no board, there is no such stage.
    _ticket_stage: ClassVar[Callable[[Session], str]] = staticmethod(lambda session: "")

    def __init__(self, session: Session) -> None:
        self._session = session
        # The ticket's stage, read once for each answer: reading it reads the board.
        self._ticket_stage_read: HeldForAnswer[str] = HeldForAnswer()

    @classmethod
    def start_on_ticket_stage_with(cls, stage_of: Callable[[Session], str]) -> None:
        """Have every selection read the stage a session's ticket stands in through stage_of, such as `Discovery`."""
        cls._ticket_stage = staticmethod(stage_of)

    @property
    @data_field
    def version(self) -> int:
        """Raised by every change, so a page that drew version N waits for N + 1 and ignores any answer older."""
        return self._session.record.fields.guidance.version

    @property
    @data_field
    def is_stage_chosen(self) -> bool:
        """Whether stages were ever selected for the session, none included: before that, the stage the session's ticket
        is in shows selected."""
        return self._session.record.fields.guidance.stages is not None

    @property
    @data_field
    def stages(self) -> list[StageSelection]:
        chosen = self._chosen_stages or []
        return [StageSelection(stage.name, stage.title, stage.name in chosen) for stage in STAGES]

    @property
    @data_field
    def covered_stages(self) -> list[str]:
        """The titles of the stages the selection covers, in the board's order: those selected, every stage while none
        is, as the chat bar heads its dots and the stages whose fidelities it shows."""
        chosen = self._chosen_stages or [stage.name for stage in STAGES]
        return [stage.title for stage in STAGES if stage.name in chosen]

    @property
    @data_field
    def practices(self) -> list[PracticeSelection]:
        return [PracticeSelection(output) for output in self._outputs]

    @property
    @data_field
    def formats(self) -> list[FormatGroup]:
        return FormatGroup.every(self.covered)

    @property
    @data_field
    def fidelities(self) -> list[str]:
        """The fidelities the stages and practices selected translate to, by slug, in stage order: what the dots stand
        for, what an action runs on, and whose files a page lists. A filter with nothing selected filters nothing, so no
        stage selected means every stage, and no practice selected every practice."""
        return [fidelity.slug for fidelity in self.covered]

    @property
    @data_field
    def commands(self) -> dict[str, str]:
        """The command a chat runs for each action on a fidelity, on the fidelities selected, with the formats chosen for
        an action that takes them."""
        return self.commands_on(self.covered)

    @property
    def covered(self) -> list[FidelityGuidance]:
        stages = self._chosen_stages or [stage.name for stage in STAGES]
        outputs = [output for output in self._outputs if output.enabled] or self._outputs
        return [fidelity for stage in STAGES if stage.name in stages for output in outputs for fidelity in output.guidance.fidelities.entries.values() if fidelity.stage == stage.name]

    def command(self, action: str, fidelities: list[FidelityGuidance] | None = None) -> str:
        """The command that runs action on fidelities (the ones selected when none are given) in this session."""
        return self.commands_on(self.covered if fidelities is None else fidelities)[action]

    def commands_on(self, fidelities: list[FidelityGuidance]) -> dict[str, str]:
        """The command that runs each action on a fidelity on fidelities in this session, one command for them all so
        the chat works on them in one turn. Each names the session, because the chat that runs it can have another
        session open; an action that takes formats names the formats chosen for them in the session (``format=``), and
        any other works in the format each fidelity keeps."""
        named = " ".join(fidelity.slug for fidelity in fidelities)
        session = self._session.session_file_from_project
        formats = list(dict.fromkeys(name for group in FormatGroup.every(fidelities) if group.is_selected for name in group.formats))
        taking = {action.name for action in ACTION_CATALOGUE.taking_formats}
        chosen = f" format={','.join(formats)}" if formats else ""
        return {
            action.name: f"/actions-{action.name} {named} session={session}{chosen if action.name in taking else ''}"
            for action in ACTION_CATALOGUE.on_fidelities
        }

    def listing(self, linked: list[str]) -> FileListing:
        """What a page lists of the session's files for this selection and linked, the fidelities its link names."""
        return FileListing(self, linked, self._session.is_repository)

    def toggle(self, part: SelectionPart, name: str) -> GuidanceSelection:
        """Select the stage, practice, or format group called name beside those selected, or no longer; before anyone
        chose stages, a stage toggles beside the one the session's ticket stands in."""
        if part == "stage":
            self.select(_toggled([stage.name for stage in self.stages if stage.is_selected], name), None, None)
        elif part == "practice":
            self.select(None, _toggled([practice.key for practice in self.practices if practice.is_selected], name), None)
        elif part == "format":
            self.select(None, None, _toggled([group.label for group in self.formats if group.is_selected], name))
        else:
            raise UnknownSelectionPart(part)
        return self

    def select(self, stages: list[str] | None, practices: list[str] | None, formats: list[str] | None) -> None:
        """Select exactly these stages, practices, and format groups, each list in place of what was selected and a list
        left out unchanged, in one write of the session's record, raising the version once for the whole change."""
        groups = {group.label: group for group in self.formats} if formats is not None else {}
        chosen_formats = self._format_fields(groups, formats or [])

        def selected(fields) -> None:
            if practices is not None:
                for output in self._outputs:
                    fields.practice(output.name).enabled = output.name in practices
            if stages is not None:
                fields.guidance.stages = [stage for stage in STAGES.names if stage in stages]
            for (practice, fidelity), chosen in chosen_formats.items():
                fields.practice(practice).fidelity(fidelity).formats = chosen

        self._session.record.update(selected, f"guidance stages {stages}, practices {practices}, formats {formats}")
        self.changed()

    def _format_fields(self, groups: dict[str, FormatGroup], formats: list[str]) -> dict[tuple[str, str], list[str]]:
        """The formats each fidelity offering a group keeps chosen once exactly the groups called formats are chosen,
        by its practice and name: a group chosen adds what each fidelity would use from it, one left out takes away
        what each has chosen from it."""
        chosen: dict[tuple[str, str], list[str]] = {}
        for label, group in groups.items():
            is_chosen = label in formats
            if group.is_selected == is_chosen:
                continue
            for fidelity in group.offering:
                key = (fidelity.practice_guidance.key, fidelity.name)
                kept = chosen.get(key, list(fidelity.session_output.chosen_formats))
                in_group = group.in_group(fidelity)
                wanted = fidelity.session_output.formats.wanted_from(in_group)
                chosen[key] = [name for name in kept if name not in in_group] + (wanted if is_chosen else [])
        return chosen

    def changed(self) -> None:
        """Raise the version, so every page waiting on it hears the change."""
        version = self._on_disk() + 1
        self._session.record.update(lambda fields: setattr(fields.guidance, "version", version), f"guidance version {version}")
        with _GUIDANCE_CHANGED:
            _GUIDANCE_CHANGED.notify_all()

    def wait_past(self, version: int) -> None:
        """Return once the version is past version: at once when it already is, else as soon as a change raises it, else
        after GUIDANCE_WAIT_SECONDS with it unchanged."""
        deadline = time.monotonic() + GUIDANCE_WAIT_SECONDS
        while self._on_disk() <= version and time.monotonic() < deadline:
            # Woken at once by a change this server makes; a change another process writes is seen within a check.
            with _GUIDANCE_CHANGED:
                _GUIDANCE_CHANGED.wait(min(GUIDANCE_CHECK_SECONDS, max(0.0, deadline - time.monotonic())))
        self._session.record.read_again()

    def _on_disk(self) -> int:
        """The version as session.json holds it now, read past this answer's reads: another call raises it."""
        return self._session.record.fields_on_disk.guidance.version

    @property
    def _chosen_stages(self) -> list[str] | None:
        """The stages selected; before anyone chose, the one the session's ticket stands in, when it stands in one."""
        saved = self._session.record.fields.guidance.stages
        if saved is not None:
            return saved
        stage = STAGES.of(self._ticket_stage_read.get(self._session.answer, lambda: self._ticket_stage(self._session)).lower())
        return [stage.name] if stage is not None else None

    @property
    def _outputs(self) -> list[PracticeSessionOutput]:
        return list(self._session.own_practices.values())


def _toggled(names: list[str], name: str) -> list[str]:
    """The names with name taken out while it is in them, else put in."""
    return [each for each in names if each != name] if name in names else [*names, name]
