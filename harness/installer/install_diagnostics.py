"""InstallDiagnostics - ``diagnostics.json`` in an IDE folder: what each install deployed, and the probes' sections."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from harness.hooks.hooks import HookInstallation
from harness.installation.ide_layout import IdeLayout

_COLORS = ("green", "yellow", "red")
# How much of the deployed set may change between two installs before the change reads as a warning, then a failure.
_GREEN_SURFACE_CHANGE = 0.10
_YELLOW_SURFACE_CHANGE = 0.50


class InstallDiagnostics:
    """``diagnostics.json`` in one IDE folder. Each install appends what it deployed on every channel, coloured by how
    much changed since the last install; the diagnostics probes write their own sections beside that history."""

    NAME = "diagnostics.json"
    CHANNELS = ("toolset", "skill", "command", "rules", "mcp", "hook", "agent", "language-adapter")

    def __init__(self, folder: Path, layout: IdeLayout) -> None:
        self.folder = folder
        self.path = folder / self.NAME
        self._layout = layout

    def channels_in_folder(self, toolsets: list[str], mcp_names: list[str]) -> dict[str, list[str]]:
        """What the folder holds on each channel, with the toolsets and MCP operations the install deployed."""
        return {
            "toolset": list(toolsets),
            "skill": sorted({path.parent.name for path in self._files("skills", "SKILL.md")}),
            "command": sorted({path.stem for path in [*self._files("commands", "*.md"), *self._files("prompts", "*.md")]}),
            "rules": sorted(path.stem for path in self._files("rules", f"*{self._layout.rule_suffix}")),
            "mcp": sorted(mcp_names),
            "hook": HookInstallation(self._layout.ide, self.folder).registered_operations,
            "agent": sorted({path.stem for path in self._files("agents", "*.md")}),
            "language-adapter": sorted(
                path.relative_to(self.folder / "language-adapters").as_posix() for path in self._files("language-adapters", "*.ts")
            ),
        }

    def compared(self, actual: dict[str, list[str]]) -> tuple[str, str]:
        """The colour of actual against the last install, and the report of what changed on each channel."""
        last = self._latest_install_channels()
        baseline = last if last is not None else {name: [] for name in self.CHANNELS}
        added = {name: sorted(set(actual.get(name, [])) - set(baseline.get(name, []))) for name in self.CHANNELS}
        removed = {name: sorted(set(baseline.get(name, [])) - set(actual.get(name, []))) for name in self.CHANNELS}
        color = "green" if last is None else self._surface_color(added, removed, actual, baseline)
        lines = ["installed"]
        for name in self.CHANNELS:
            previous, current = len(baseline.get(name, [])), len(actual.get(name, []))
            lines.append(f"{name} {previous} -> {current} (delta {current - previous})")
        for name in self.CHANNELS:
            lines.extend(f"new {name}: {item}" for item in added[name])
            lines.extend(f"deleted {name}: {item}" for item in removed[name])
        return color, "\n".join(lines)

    def record_install(self, actual: dict[str, list[str]], report: str, color: str) -> None:
        """Append this install, with what it deployed on each channel and its report, to the history."""
        entry: dict[str, Any] = {"color": color, "diagnostics": [{"name": "diagnose_install", "report": report, "color": color}]}
        for name in self.CHANNELS:
            items = actual.get(name, [])
            entry[name] = {"count": len(items), "items": items}
        data = self._read()
        data["installs"] = [*(data.get("installs") or []), entry]
        self._write(data)

    def write_section(self, section: str, results: dict[str, Any]) -> None:
        """Add or replace results in one top-level section, coloured by its worst result. The install history stays."""
        data = self._read()
        current = data.get(section)
        merged = {**(current if isinstance(current, dict) else {}), **results}
        colors = [value.get("color") for value in merged.values() if isinstance(value, dict) and value.get("color") in _COLORS]
        if colors:
            merged["color"] = max(colors, key=_COLORS.index)
        data[section] = merged
        self._write(data)

    def installed_items(self, channel: str) -> list[str]:
        """What the latest install deployed on one channel, such as ``mcp`` operation names or ``toolset``
        references; none before the first install."""
        installs = self._read().get("installs") or []
        if not installs:
            return []
        return [str(item) for item in (installs[-1].get(channel) or {}).get("items") or []]

    def _latest_install_channels(self) -> dict[str, list[str]] | None:
        installs = self._read().get("installs") or []
        if not installs:
            return None
        latest = installs[-1]
        channels: dict[str, list[str]] = {}
        for name in self.CHANNELS:
            field = latest.get(name) or {}
            items = field.get("items") if isinstance(field, dict) else field
            channels[name] = [str(item) for item in items or []]
        return channels

    def _surface_color(
        self,
        added: dict[str, list[str]],
        removed: dict[str, list[str]],
        actual: dict[str, list[str]],
        baseline: dict[str, list[str]],
    ) -> str:
        changed = sum(len(items) for items in added.values()) + sum(len(items) for items in removed.values())
        total = sum(len(actual.get(name, [])) + len(baseline.get(name, [])) for name in self.CHANNELS)
        ratio = changed / total if total else 0.0
        if ratio <= _GREEN_SURFACE_CHANGE:
            return "green"
        return "yellow" if ratio <= _YELLOW_SURFACE_CHANGE else "red"

    def _files(self, folder_name: str, pattern: str) -> list[Path]:
        folder = self.folder / folder_name
        return list(folder.rglob(pattern)) if folder.is_dir() else []

    def _read(self) -> dict[str, Any]:
        if not self.path.is_file():
            return {}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _write(self, data: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
