"""Catalog pages — HTML from each Guidance @markdown property."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

from harness.markdown import HTML, Markdown


class Catalog(HTML):
    def __init__(self, text: str = "") -> None:
        super().__init__(text)
        self.pages: dict[str, str] = {}

    @classmethod
    def from_registry(cls, guidance: Iterable[Any] | None = None) -> Catalog:
        catalog = cls()
        for item in list(guidance or ()):
            catalog._add_guidance(item)
        return catalog

    def _add_guidance(self, guidance: Any) -> None:
        slug = getattr(guidance, "context_index_key", None) or type(guidance).__name__
        for label in ("context", "guidance", "examples"):
            try:
                md = Markdown.from_label(guidance, "overview" if label == "context" else label)
                page = md.html()
            except Exception:
                continue
            if str(page).strip():
                self.pages[f"{slug}-{label}"] = str(page)
        fidelities = getattr(guidance, "fidelities", None)
        entries = getattr(fidelities, "entries", {}) if fidelities is not None else {}
        for name, child in entries.items():
            html = HTML.from_markdown(getattr(child, "guidance", "") or "")
            self.pages[f"{slug}-{name}"] = str(html)

    def generate_catalog(self, out_root: Path) -> None:
        root = Path(out_root)
        root.mkdir(parents=True, exist_ok=True)
        for name, body in self.pages.items():
            (root / f"{name}.html").write_text(body, encoding="utf-8")
