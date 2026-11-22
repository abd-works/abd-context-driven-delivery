"""An aggregate's own lines, as every DDD text format writes them: what it keeps true, its root line with what the root
is and the members under it, its arcs under `Integrations:`, and the events under `emits events:` and `consumes
events:`. A markdown map writes them under the aggregate's `###` heading, and a sketch inside the aggregate's fence, so
both read and write them through *AggregateLines*."""

from __future__ import annotations

from cdd_guidance.practices.ddd.model.building_blocks import plain_name
from cdd_guidance.practices.ddd.model.nodes import Aggregate, Integration

_INTEGRATIONS = "Integrations:"
_EMITS = "emits events:"
_CONSUMES = "consumes events:"


class AggregateLines:
    """The lines of one aggregate that are its own, read into it and written from it."""

    def __init__(self, aggregate: Aggregate) -> None:
        self._aggregate = aggregate

    def read(self, lines: list[str]) -> None:
        """Read the aggregate's own lines: the rule it keeps true, its root line with what the root is, the members
        under it, its integrations, and its events; then make its root card, when it holds cards, its root. An
        aggregate drawn as class cards has no root line, so each of its own lines says what it keeps true."""
        aggregate = self._aggregate
        root_line = ""
        described: list[str] = []
        members: list[str] = []
        emitted: list[str] = []
        index = 0
        while index < len(lines):
            line = lines[index].strip().lower()
            if line.startswith(_INTEGRATIONS.lower()):
                index = self._read_integrations(lines, index)
            elif line.startswith((_EMITS, _CONSUMES)):
                index = self._read_events(lines, index, emitted)
            else:
                root_line = self._read_own_line(lines[index], members, described) or root_line
                index += 1
        root_name, _, root_says = root_line.partition(" - ")
        aggregate.description = "\n".join(described)
        aggregate.open_root(plain_name(root_name) or aggregate.name, members, emitted)
        aggregate.root.intent = root_says.strip()
        aggregate.take_root_card()
        aggregate.load_root()

    def _read_own_line(self, raw: str, members: list[str], described: list[str]) -> str:
        """Read one line that is neither an integration nor an event: a member under the root, or a line that says
        what the aggregate keeps true. Answers the line when it is the root's own, `Root - what it is`."""
        line = raw.strip()
        if " - " in line and not raw.startswith(" ") and not self._aggregate.classes:
            return raw
        if raw.startswith("  ") and line and not line.startswith("-"):
            members.append(raw.split("//", 1)[0].strip())
        elif self._says_what_it_keeps_true(raw):
            described.append(line)
        return ""

    def _says_what_it_keeps_true(self, raw: str) -> bool:
        """A line of the aggregate's own, at the margin, with words on it: neither a rule that parts sections nor the
        root named alone."""
        line = raw.strip()
        return bool(line) and not raw.startswith((" ", "\t")) and bool(line.strip("-")) and plain_name(line) != self._aggregate.name

    def _read_events(self, lines: list[str], index: int, emitted: list[str]) -> int:
        """The `- Event` lines under an `emits events:` or `consumes events:` line; those it emits go to emitted.
        Returns the line after them."""
        emits = lines[index].strip().lower().startswith("emits")
        index += 1
        while index < len(lines) and lines[index].strip().startswith("-"):
            (emitted if emits else self._aggregate.consumed_events).append(plain_name(lines[index].strip()[1:]))
            index += 1
        return index

    def _read_integrations(self, lines: list[str], index: int) -> int:
        # The arcs are the lines indented under `Integrations:`; the first line back at its indent ends them.
        heading_indent = _indent(lines[index])
        end = index + 1
        while end < len(lines) and (not lines[end].strip() or _indent(lines[end]) > heading_indent):
            end += 1
        self._aggregate.integrations.extend(Integration.read_arcs(lines[index + 1:end]))
        return end

    def integration_lines(self) -> list[str]:
        """The aggregate's arcs, the events its root emits, and the events it reacts to, under `Integrations:`,
        `emits events:`, and `consumes events:`."""
        aggregate = self._aggregate
        written: list[str] = []
        if aggregate.integrations:
            written.append(_INTEGRATIONS)
            written.extend(f"  {line}" for item in aggregate.integrations for line in item.lines())
            written.append("")
        if aggregate.events:
            written.append(_EMITS)
            written.extend(f"  - {event.name}" for event in aggregate.events)
        if aggregate.consumed_events:
            written.append(_CONSUMES)
            written.extend(f"  - {name}" for name in aggregate.consumed_events)
        if aggregate.events or aggregate.consumed_events:
            written.append("")
        return written


def _indent(raw: str) -> int:
    return len(raw) - len(raw.lstrip())
