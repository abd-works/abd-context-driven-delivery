"""Scanner: route handlers must delegate to domain-server, not repository directly.

Flags router factories in ``*-server.ts`` (and legacy ``*.routes.ts``) whose
handlers call ``repo.*`` inline instead of delegating to a server-side domain
class. When the server tier is one file, only lines inside ``router.*``
handler callbacks are checked — ``repo.findAll()`` on the repository class or
server domain class is fine.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import List, Tuple

from mern_scanner_base import MERNScanner
from scan.violation import Violation


class RouteDelegationScanner(MERNScanner):
    """Checks route handlers delegate to domain-server rather than calling repo directly."""

    RULE = "delegate-routes-to-domain-server"

    REPO_CALL = re.compile(r"\b(?:repo|repository)\.\w+\(", re.IGNORECASE)
    SHARED_DOMAIN_IN_ROUTE = re.compile(
        r"new\s+\w+\s*\([^)]*\)\s*\.\s*(?:filter|search|map|reduce)\w*\(",
    )
    ROUTER_HANDLER = re.compile(r"router\.(get|post|put|patch|delete)\s*\(")

    def scan(self, root: Path, files: List[Path]) -> List[Violation]:
        violations: List[Violation] = []
        project_root = root

        for routes_file in project_root.rglob("*.routes.ts"):
            if "node_modules" in routes_file.parts or "examples" in routes_file.parts:
                continue
            violations.extend(self._check_file(routes_file, handlers_only=False))

        for router_file in project_root.rglob("*Router.ts"):
            if "node_modules" in router_file.parts or "examples" in router_file.parts:
                continue
            violations.extend(self._check_file(router_file, handlers_only=False))

        for server_file in project_root.rglob("*-server.ts"):
            if "node_modules" in server_file.parts or "examples" in server_file.parts:
                continue
            violations.extend(self._check_file(server_file, handlers_only=True))

        return violations

    def _check_file(self, path: Path, *, handlers_only: bool) -> List[Violation]:
        content = self._read_file_content(path)
        if content is None:
            return []
        if handlers_only and not self.ROUTER_HANDLER.search(content):
            return []

        lines = content.splitlines()
        if handlers_only:
            ranges = self._handler_line_ranges(content)
            if not ranges:
                return []
            check_lines = [
                (i, lines[i - 1])
                for start, end in ranges
                for i in range(start, end + 1)
                if 1 <= i <= len(lines)
            ]
        else:
            check_lines = list(enumerate(lines, start=1))

        violations: List[Violation] = []
        for i, line in check_lines:
            stripped = line.strip()
            if stripped.startswith("//"):
                continue
            if self.REPO_CALL.search(line):
                violations.append(
                    self.v(
                        "Route handler calls repository directly - delegate to "
                        "server-side domain class instead.",
                        str(path),
                        i,
                    )
                )
            if self.SHARED_DOMAIN_IN_ROUTE.search(line):
                violations.append(
                    self.v(
                        "Route handler applies shared domain logic inline - "
                        "move to server-side domain class.",
                        str(path),
                        i,
                    )
                )
        return violations

    def _handler_line_ranges(self, content: str) -> List[Tuple[int, int]]:
        """Return 1-based (start, end) line ranges for each router.* callback body."""
        ranges: List[Tuple[int, int]] = []
        for match in self.ROUTER_HANDLER.finditer(content):
            # Find the opening '{' of the handler callback after the match.
            brace = content.find("{", match.end())
            if brace < 0:
                continue
            depth = 0
            end = brace
            for i in range(brace, len(content)):
                ch = content[i]
                if ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        end = i
                        break
            start_line = content[:brace].count("\n") + 1
            end_line = content[:end].count("\n") + 1
            ranges.append((start_line, end_line))
        return ranges
