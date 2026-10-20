"""Format validation lines (ported from agile_bots validation_report_formatter)."""

from __future__ import annotations

from pathlib import Path
from typing import Any


class ValidationReportFormatter:
    def __init__(
        self,
        workspace_directory: Path,
        *,
        link_from_directory: Path | None = None,
    ) -> None:
        self.workspace_directory = workspace_directory.resolve()
        self.link_from_directory = (
            link_from_directory.resolve() if link_from_directory is not None else None
        )

    def format_violation_line(self, violation: dict[str, Any]) -> list[str]:
        location = violation.get("location", "unknown")
        message = violation.get("violation_message", "No message")
        severity = violation.get("severity", "error")
        line_number = violation.get("line_number")
        graph_tag = " **[graph rule]**" if violation.get("graph_rule") else ""
        icon = "[X]" if severity == "error" else "[!]" if severity == "warning" else "[i]"
        location_link = self.create_file_link(str(location), line_number)
        formatted_message = self.format_violation_message(str(message))
        if "\n" not in formatted_message:
            return [
                f"- {icon} **{severity.upper()}**{graph_tag} - {location_link}: {formatted_message}"
            ]
        parts = formatted_message.split("\n")
        lines = [
            f"- {icon} **{severity.upper()}**{graph_tag} - {location_link}: {parts[0]}"
        ]
        for part in parts[1:]:
            if part.strip().startswith("```"):
                lines.append(f"    {part}")
            elif part.strip() == "":
                lines.append("")
            else:
                lines.append(f"  {part}")
        return lines

    def format_violation_message(self, message: str) -> str:
        return message

    def create_file_link(self, location: str, line_number: int | None) -> str:
        if not location or location == "unknown":
            return f"`{location}`"
        try:
            file_path = Path(location)
            if not file_path.is_absolute() and self.workspace_directory:
                file_path = (self.workspace_directory / file_path).resolve()
            rel = self._display_path(file_path)
            href = self._href_for_file(file_path, line_number)
            return f"[{rel}]({href})"
        except (OSError, ValueError):
            name = Path(location.replace("\\", "/")).name
            return f"`{name}`"

    def _href_for_file(self, file_path: Path, line_number: int | None) -> str:
        """Absolute path with #L line, e.g. C:\\...\\account.ts#L287 (markdown preview)."""
        href = str(file_path.resolve())
        if line_number is not None:
            href = f"{href}#L{line_number}"
        return href

    def _display_path(self, file_path: Path) -> str:
        return self.get_relative_path(file_path).replace("\\", "/")

    def get_relative_path(self, file_path: Path) -> str:
        try:
            if file_path.is_absolute():
                return str(file_path.relative_to(self.workspace_directory))
            return str(file_path)
        except ValueError:
            return file_path.name
