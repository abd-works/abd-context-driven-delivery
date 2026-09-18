"""Catalog pages — HTML from each host @markdown property."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

from harness.markdown import HTML, Markdown


class Catalog(HTML):
    def __init__(self, text: str = "") -> None:
        super().__init__(text)
        self.pages: dict[str, str] = {}

    @classmethod
    def from_registry(cls, hosts: Iterable[Any] | None = None) -> Catalog:
        catalog = cls()
        for host in list(hosts or ()):
            catalog._add_host(host)
        return catalog

    def _add_host(self, host: Any) -> None:
        slug = getattr(host, "domain_slug", None) or type(host).__name__
        for label in ("context", "guidance", "examples"):
            try:
                md = Markdown.from_label(host, "overview" if label == "context" else label)
                page = md.html()
            except Exception:
                continue
            if str(page).strip():
                self.pages[f"{slug}-{label}"] = str(page)
        fidelities = getattr(host, "fidelities", None)
        entries = getattr(fidelities, "entries", {}) if fidelities is not None else {}
        for name, child in entries.items():
            html = HTML.from_markdown(getattr(child, "guidance", "") or "")
            self.pages[f"{slug}-{name}"] = str(html)

    def generate_catalog(self, out_root: Path) -> None:
        root = Path(out_root)
        root.mkdir(parents=True, exist_ok=True)
        for name, body in self.pages.items():
            (root / f"{name}.html").write_text(body, encoding="utf-8")
