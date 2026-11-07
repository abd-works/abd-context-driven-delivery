"""Markdown written as catalog HTML: guidance panels, module overviews, and markdown examples."""
from __future__ import annotations

import html
import re

_BULLET = re.compile(r"^\s*[-*]\s+")
_NUMBERED = re.compile(r"^\s*\d+\.\s+")
# Guides often use ❌/✅ as the bullet itself (no leading "- ").
_MARKED_BULLET = re.compile(r"^\s*([❌✅])\s+")
_BLOCK_START = re.compile(r"^(#{1,4}\s+|```|\s*[-*]\s+|\s*\d+\.\s+|\s*[❌✅]\s+|\s*\|)")
_HEADING = re.compile(r"^(#{1,4})\s+(.*)$")
_TABLE_LINE = re.compile(r"^\s*\|")
_TABLE_SEPARATOR = re.compile(r"^\s*\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)+\|?\s*$")
_RULE = re.compile(r"^\s*-{3,}\s*$")
_HARD_BREAK = re.compile(r"  +$")
_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_SAVED_LINK = re.compile(r"\x00L(\d+)\x00")
_CODE = re.compile(r"`([^`]+)`")
_STRONG = re.compile(r"\*\*([^*]+)\*\*")
_EMPHASIS = re.compile(r"(?<!\*)\*([^*]+)\*(?!\*)")
_GUIDANCE_SECTION = re.compile(r"(<h[1-4]>Guidance</h[1-4]>)(.*?)(?=<h[1-4]>|\Z)", re.DOTALL)
# Fidelity and rule files keep format, stage, and glob settings in yaml fences. The settings stay in the markdown; the
# catalog HTML shows the prose.
_SETTINGS_LANGUAGES = ("yaml", "yml")
_MISSING_GUIDANCE = "Guidance missing"


class MarkdownHtml:
    """Markdown as catalog HTML, written with the standard library alone: headings, lists, code, links, emphasis,
    hard breaks, and rules. Pipe tables are left out unless ``include_tables`` asks for them, so a fidelity overview's
    index table stays out of the page body; the workflow page shows its tables."""

    def __init__(self, text: str, *, include_tables: bool = False) -> None:
        self._text = text
        self._include_tables = include_tables

    @property
    def html(self) -> str:
        if not self._text or self._text == _MISSING_GUIDANCE:
            return f"<p>{html.escape(self._text or '')}</p>"
        return _MarkdownReading(self._text, self._include_tables).html()

    @property
    def guidance_html(self) -> str:
        """The HTML with the Guidance section's body marked, so its bold lead-ins can be coloured apart from Rules."""
        return _GUIDANCE_SECTION.sub(
            lambda match: f'{match.group(1)}<div class="fidelity-guidance-body">{match.group(2)}</div>', self.html
        )


class _MarkdownReading:
    """One pass over the lines of a markdown text, block by block; made for that one reading."""

    def __init__(self, text: str, include_tables: bool) -> None:
        self._lines = text.replace("\r\n", "\n").split("\n")
        self._include_tables = include_tables
        self._index = 0
        self._out: list[str] = []
        self._open_list: str | None = None

    def html(self) -> str:
        while self._index < len(self._lines):
            self._read_block(self._lines[self._index])
        self._close_list()
        return "\n".join(self._out)

    def _read_block(self, line: str) -> None:
        if line.strip().startswith("```"):
            self._close_list()
            self._read_code(line.strip()[3:].strip())
        elif _TABLE_LINE.match(line):
            self._close_list()
            self._read_table()
        elif _HEADING.match(line):
            self._close_list()
            level, text = _HEADING.match(line).groups()
            self._out.append(f"<h{len(level)}>{self._inline(text.strip())}</h{len(level)}>")
            self._index += 1
        elif _BULLET.match(line):
            self._read_item("ul", _BULLET)
        elif _MARKED_BULLET.match(line):
            self._start_list("ul")
            self._out.append(f"<li>{self._inline(line.strip())}</li>")
            self._index += 1
        elif _NUMBERED.match(line):
            self._read_item("ol", _NUMBERED)
        else:
            self._read_prose(line)

    def _read_prose(self, line: str) -> None:
        self._close_list()
        if not line.strip():
            self._index += 1
        elif _RULE.match(line):
            self._out.append("<hr>")
            self._index += 1
        else:
            self._read_paragraph()

    def _read_code(self, language: str) -> None:
        self._index += 1
        code: list[str] = []
        while self._index < len(self._lines) and not self._lines[self._index].strip().startswith("```"):
            code.append(self._lines[self._index])
            self._index += 1
        closed = self._index < len(self._lines)
        self._index += 1
        if language.lower() in _SETTINGS_LANGUAGES:
            return
        language_attribute = f' class="language-{html.escape(language)}"' if language and closed else ""
        self._out.append(f"<pre><code{language_attribute}>{html.escape(chr(10).join(code))}</code></pre>")

    def _read_table(self) -> None:
        if not self._include_tables:
            while self._index < len(self._lines) and (
                _TABLE_LINE.match(self._lines[self._index]) or not self._lines[self._index].strip()
            ):
                self._index += 1
            return
        rows: list[list[str]] = []
        while self._index < len(self._lines) and _TABLE_LINE.match(self._lines[self._index]):
            rows.append([cell.strip() for cell in self._lines[self._index].strip().strip("|").split("|")])
            self._index += 1
        data = [row for row in rows if not _TABLE_SEPARATOR.match("|" + "|".join(row) + "|")]
        if data:
            self._out.append(self._table(data))

    def _table(self, rows: list[list[str]]) -> str:
        header, *body = rows
        parts = ['<table class="catalog-md-table">']
        parts.append("<thead><tr>" + "".join(f"<th>{self._inline(cell)}</th>" for cell in header) + "</tr></thead>")
        if body:
            parts.append("<tbody>")
            for row in body:
                cells = (row + [""] * len(header))[: len(header)]
                parts.append("<tr>" + "".join(f"<td>{self._inline(cell)}</td>" for cell in cells) + "</tr>")
            parts.append("</tbody>")
        parts.append("</table>")
        return "\n".join(parts)

    def _read_item(self, kind: str, marker: re.Pattern[str]) -> None:
        self._start_list(kind)
        item = marker.sub("", self._lines[self._index], count=1)
        self._index += 1
        continued: list[str] = []
        while self._index < len(self._lines) and self._continues_item(self._lines[self._index]):
            continued.append(self._lines[self._index].strip())
            self._index += 1
        self._out.append(f"<li>{'<br>'.join(self._inline(chunk) for chunk in [item, *continued])}</li>")

    def _continues_item(self, line: str) -> bool:
        return line.startswith(("  ", "\t")) and bool(line.strip()) and not _BULLET.match(line) and not _NUMBERED.match(line)

    def _read_paragraph(self) -> None:
        lines = [self._lines[self._index]]
        self._index += 1
        while self._index < len(self._lines) and self._continues_paragraph(self._lines[self._index]):
            lines.append(self._lines[self._index])
            self._index += 1
        parts: list[str] = []
        for index, raw in enumerate(lines):
            if index:
                parts.append("<br>" if _HARD_BREAK.search(lines[index - 1].rstrip("\r")) else " ")
            parts.append(self._inline(raw.strip()))
        self._out.append(f"<p>{''.join(parts)}</p>")

    def _continues_paragraph(self, line: str) -> bool:
        return bool(line.strip()) and not _BLOCK_START.match(line) and not _RULE.match(line)

    def _start_list(self, kind: str) -> None:
        if self._open_list != kind:
            self._close_list()
            self._out.append(f"<{kind}>")
            self._open_list = kind

    def _close_list(self) -> None:
        if self._open_list:
            self._out.append(f"</{self._open_list}>")
            self._open_list = None

    def _inline(self, text: str) -> str:
        """Code, bold, emphasis, and links in one line. Links are set aside first, so a URL is never formatted, and
        their labels get the same formatting as the line."""
        links: list[tuple[str, str]] = []

        def set_aside(match: re.Match) -> str:
            links.append((match.group(1), match.group(2)))
            return f"\x00L{len(links) - 1}\x00"

        def restore(match: re.Match) -> str:
            label, href = links[int(match.group(1))]
            return f'<a href="{html.escape(href, quote=True)}">{self._formatted(html.escape(label))}</a>'

        return _SAVED_LINK.sub(restore, self._formatted(html.escape(_LINK.sub(set_aside, text))))

    def _formatted(self, escaped: str) -> str:
        return _EMPHASIS.sub(r"<em>\1</em>", _STRONG.sub(r"<strong>\1</strong>", _CODE.sub(r"<code>\1</code>", escaped)))
