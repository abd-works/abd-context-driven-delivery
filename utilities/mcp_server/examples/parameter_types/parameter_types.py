"""Typed parameters for MCP JSON Schema binding specs."""
from __future__ import annotations

from collections.abc import Mapping, Sequence

from tools.tool import agent_tool, toolset


@toolset
class ParameterTypes:
    """Echo typed arguments so MCP schema and invocation can be observed."""

    @agent_tool
    def echo(
        self,
        text: str,
        count: int,
        ratio: float,
        flag: bool,
        items: list[str],
        fields: dict[str, str],
        untyped_items: list,
        untyped_fields: dict,
        counted_items: list[int],
        flagged_items: list[bool],
        measured_items: list[float],
        nested_items: list[list[str]],
        record_items: list[dict[str, str]],
        counted_fields: dict[str, int],
        listed_fields: dict[str, list[int]],
        optional_text: str | None = None,
        optional_count: int | None = None,
        optional_flag: bool | None = None,
        optional_ratio: float | None = None,
        optional_items: list[str] | None = None,
        optional_fields: dict[str, str] | None = None,
        text_or_count: str | int = "",
    ) -> dict[str, object]:
        """Return the arguments as a record."""
        return {
            "text": text,
            "count": count,
            "ratio": ratio,
            "flag": flag,
            "items": items,
            "fields": fields,
            "untyped_items": untyped_items,
            "untyped_fields": untyped_fields,
            "counted_items": counted_items,
            "flagged_items": flagged_items,
            "measured_items": measured_items,
            "nested_items": nested_items,
            "record_items": record_items,
            "counted_fields": counted_fields,
            "listed_fields": listed_fields,
            "optional_text": optional_text,
            "optional_count": optional_count,
            "optional_flag": optional_flag,
            "optional_ratio": optional_ratio,
            "optional_items": optional_items,
            "optional_fields": optional_fields,
            "text_or_count": text_or_count,
        }

    @agent_tool
    def echo_sequence(self, value: Sequence[str]) -> list[str]:
        """Return a sequence as a list."""
        return list(value)

    @agent_tool
    def echo_mapping(self, value: Mapping[str, int]) -> dict[str, int]:
        """Return a mapping as a dict."""
        return dict(value)

    @agent_tool
    def echo_unannotated(self, value) -> object:
        """Return an unannotated argument."""
        return value
