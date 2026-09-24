"""Scanner: view naming - React components end with View, domain-aligned stem.

Checks:
1. Every exported React component in ``client.tsx`` ends with 'View'.
2. No ad-hoc suffixes (Form, Panel, Container, Wrapper) on domain components.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import List

from lern_scanner_base import TypeScriptScanner, Violation

_EXPORT_COMPONENT_RE = re.compile(r"export\s+(?:default\s+)?(?:function|const)\s+([A-Z]\w+)")

_WRONG_SUFFIXES = frozenset(
    {"Form", "Panel", "Container", "Wrapper", "Page", "Widget", "Bar", "Sidebar", "Modal", "Drawer"}
)

# Not views — hooks/classes/helpers live in the same client.tsx file.
_NON_VIEW_PREFIXES = ("use",)


class ViewNamingScanner(TypeScriptScanner):
    """Check that client.tsx components follow the {Domain}View naming."""

    RULE = "consistent-view-naming"

    def scan(self, root: Path, files: List[Path]) -> List[Violation]:
        violations: List[Violation] = []

        for domain_path in self._find_domain_packages(root):
            violations += self._check_client(domain_path)

        return violations

    def _check_client(self, domain_path: Path) -> List[Violation]:
        client = self._client_file(domain_path)
        if client is None:
            return []
        content = self._read_file_content(client)
        if content is None:
            return []
        violations: List[Violation] = []
        for match in _EXPORT_COMPONENT_RE.finditer(content):
            hit = self._view_name_hit(client, match.group(1))
            if hit is not None:
                violations.append(hit)
        return violations

    def _view_name_hit(self, client: Path, comp_name: str):
        if any(comp_name.startswith(prefix) for prefix in _NON_VIEW_PREFIXES):
            return None
        if "Client" in comp_name or "Http" in comp_name or comp_name.endswith("View"):
            return None
        for suffix in _WRONG_SUFFIXES:
            if comp_name.endswith(suffix):
                base = comp_name[: -len(suffix)]
                return self.v(
                    f"Component '{comp_name}' in {client.name} uses "
                    f"suffix '{suffix}'. Rename to '{base}View' to "
                    "follow the consistent View naming convention.",
                    str(client),
                    severity="warning",
                )
        return self.v(
            f"Component '{comp_name}' in {client.name} does not "
            f"end with 'View'. Rename to '{comp_name}View'.",
            str(client),
            severity="warning",
        )
