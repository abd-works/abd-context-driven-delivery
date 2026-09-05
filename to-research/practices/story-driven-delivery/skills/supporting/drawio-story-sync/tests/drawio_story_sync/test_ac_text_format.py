"""Acceptance criteria display + plain extraction for exploration diagrams."""

from __future__ import annotations

from drawio_story_sync.ac_text_format import (
    canonical_ac_key,
    format_ac_diagram_html,
    plain_ac_from_cell_value,
)


def test_format_strips_ordinals_adds_when_then_structure() -> None:
    raw = "1. WHEN the *shell* loads THEN open main AND show tree ---"
    html = format_ac_diagram_html(raw)
    assert "1." not in html
    assert "<b>WHEN</b>" in html
    assert "<br/><b>THEN</b>" in html
    assert "<br/><b>AND</b>" in html


def test_plain_from_html_matches_canonical_of_numbered_graph_string() -> None:
    numbered = (
        '1. WHEN the *application shell* starts THEN the system proceeds ---'
    )
    html = format_ac_diagram_html(numbered)
    plain_cell = plain_ac_from_cell_value(html)
    assert plain_cell.startswith("WHEN ")
    assert canonical_ac_key(html) == canonical_ac_key(numbered)


def test_format_normalizes_keyword_markdown() -> None:
    raw = "**WHEN** x **THEN** y"
    html = format_ac_diagram_html(raw)
    assert "**" not in html
    assert "<b>WHEN</b>" in html and "<b>THEN</b>" in html


def test_format_renders_markdown_italics_as_html_i() -> None:
    raw = "1. WHEN the customer uses the *Search Bar* THEN the *Search Results* update"
    html = format_ac_diagram_html(raw)
    assert "<i>Search Bar</i>" in html
    assert "<i>Search Results</i>" in html
    assert "*Search Bar*" not in html
    assert canonical_ac_key(html) == canonical_ac_key(raw)

