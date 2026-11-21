"""InstallDiagnostics - ``diagnostics.json`` in an IDE folder: what each install deployed, and the probes' sections;
Deployed, what a folder holds on each channel; and InstallDiagnosis, what one install deployed against the last."""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from harness.installation.json_file import JsonFile

if TYPE_CHECKING:
    from harness.installation.install_target import InstallTarget

_COLORS = ("green", "yellow", "red")
# How much of the deployed set may change between two installs before the change reads as a warning, then a failure.
_GREEN_SURFACE_CHANGE = 0.10
_YELLOW_SURFACE_CHANGE = 0.50


class Deployed:
    """What an IDE folder holds on each channel an install reports: the toolsets it deployed, its skills, commands,
    rules, agents, and language adapters, and what each registered channel published, such as the MCP operations and
    the hook operations."""

    CHANNELS = ("toolset", "skill", "command", "rules", "mcp", "hook", "agent", "language-adapter")

    def __init__(self, items: dict[str, list[str]]) -> None:
        self._items = {name: list(items.get(name, [])) for name in self.CHANNELS}

    @classmethod
    def of_folder(cls, target: InstallTarget, toolsets: list[str], published: dict[str, list[str]]) -> Deployed:
        """What target's folder holds, with the toolsets an install deployed there and what each registered channel
        published."""
        folder, layout = target.path, target.layout

        def files(folder_name: str, pattern: str) -> list[Path]:
            found = folder / folder_name
            return list(found.rglob(pattern)) if found.is_dir() else []

        return cls(
            {
                "toolset": list(toolsets),
                "skill": sorted({path.parent.name for path in files("skills", "SKILL.md")}),
                "command": sorted({path.stem for path in [*files("commands", "*.md"), *files("prompts", "*.md")]}),
                "rules": sorted(path.stem for path in files("rules", f"*{layout.rule_suffix}")),
                "mcp": sorted(published.get("mcp", [])),
                "hook": sorted(published.get("hook", [])),
                "agent": sorted({path.stem for path in files("agents", "*.md")}),
                "language-adapter": sorted(
                    path.relative_to(folder / "language-adapters").as_posix() for path in files("language-adapters", "*.ts")
                ),
            }
        )

    def items(self, channel: str) -> list[str]:
        """What the folder holds on channel."""
        return list(self._items[channel])

    def changes_since(self, last: Deployed | None) -> DeployedChanges:
        """What changed on each channel since last, the deployment of the last install; everything is new before the
        first."""
        return DeployedChanges(self, last)


class DeployedChanges:
    """What changed on each channel between the last install's deployment and this one's: the items added and removed,
    each channel's count before and after, and the colour of how much changed. The first install is green."""

    def __init__(self, current: Deployed, last: Deployed | None) -> None:
        self._current = current
        self._last = last
        self._baseline = last if last is not None else Deployed({})

    def added(self, channel: str) -> list[str]:
        return sorted(set(self._current.items(channel)) - set(self._baseline.items(channel)))

    def removed(self, channel: str) -> list[str]:
        return sorted(set(self._baseline.items(channel)) - set(self._current.items(channel)))

    @property
    def colour(self) -> str:
        """Green, yellow, or red by the share of the compared items, this install's and the last's, that changed."""
        if self._last is None:
            return "green"
        channels = Deployed.CHANNELS
        changed = sum(len(self.added(name)) + len(self.removed(name)) for name in channels)
        compared = sum(len(self._current.items(name)) + len(self._baseline.items(name)) for name in channels)
        ratio = changed / compared if compared else 0.0
        if ratio <= _GREEN_SURFACE_CHANGE:
            return "green"
        return "yellow" if ratio <= _YELLOW_SURFACE_CHANGE else "red"

    @property
    def report(self) -> str:
        """Each channel's count before and after, then every new and deleted item."""
        lines = ["installed"]
        for name in Deployed.CHANNELS:
            previous, current = len(self._baseline.items(name)), len(self._current.items(name))
            lines.append(f"{name} {previous} -> {current} (delta {current - previous})")
        for name in Deployed.CHANNELS:
            lines.extend(f"new {name}: {item}" for item in self.added(name))
            lines.extend(f"deleted {name}: {item}" for item in self.removed(name))
        return "\n".join(lines)


class InstallDiagnosis:
    """One install's diagnosis: what it deployed, what changed since the last install, and the status each registered
    channel reports, such as whether the cdd server runs. Its colour is a field, and its report is written from the
    fields, never read back."""

    def __init__(self, deployed: Deployed, changes: DeployedChanges, server_status: list[str]) -> None:
        self.deployed = deployed
        self.changes = changes
        self.server_status = server_status

    @property
    def colour(self) -> str:
        return self.changes.colour

    @property
    def is_red(self) -> bool:
        return self.colour == "red"

    @property
    def report(self) -> str:
        """The colour, what changed on each channel, and each registered channel's status."""
        return "\n".join([self.colour, self.changes.report, *self.server_status])


class InstallDiagnostics:
    """``diagnostics.json`` in one IDE folder. Each install appends its diagnosis: what it deployed on every channel,
    coloured by how much changed since the last install; the diagnostics probes write their own sections beside that
    history."""

    NAME = "diagnostics.json"

    def __init__(self, folder: Path) -> None:
        self.folder = folder
        self.path = folder / self.NAME
        self._file = JsonFile(self.path)

    def record(self, diagnosis: InstallDiagnosis) -> None:
        """Append diagnosis, with what its install deployed on each channel and its report, to the history."""
        colour = diagnosis.colour
        entry: dict[str, Any] = {"color": colour, "diagnostics": [{"name": "diagnose_install", "report": diagnosis.report, "color": colour}]}
        for name in Deployed.CHANNELS:
            items = diagnosis.deployed.items(name)
            entry[name] = {"count": len(items), "items": items}
        data = self._file.read()
        data["installs"] = [*(data.get("installs") or []), entry]
        self._file.write(data)

    def last_deployed(self) -> Deployed | None:
        """What the latest install recorded it deployed; none before the first install."""
        installs = self._file.read().get("installs") or []
        if not installs:
            return None
        latest = installs[-1]
        items: dict[str, list[str]] = {}
        for name in Deployed.CHANNELS:
            field = latest.get(name) or {}
            listed = field.get("items") if isinstance(field, dict) else field
            items[name] = [str(item) for item in listed or []]
        return Deployed(items)

    def write_section(self, section: str, results: dict[str, Any]) -> None:
        """Add or replace results in one top-level section, coloured by its worst result. The install history stays."""
        data = self._file.read()
        current = data.get(section)
        merged = {**(current if isinstance(current, dict) else {}), **results}
        colors = [value.get("color") for value in merged.values() if isinstance(value, dict) and value.get("color") in _COLORS]
        if colors:
            merged["color"] = max(colors, key=_COLORS.index)
        data[section] = merged
        self._file.write(data)

    def installed_items(self, channel: str) -> list[str]:
        """What the latest install deployed on one channel, such as ``mcp`` operation names or ``toolset``
        references; none before the first install."""
        last = self.last_deployed()
        return last.items(channel) if last is not None else []
