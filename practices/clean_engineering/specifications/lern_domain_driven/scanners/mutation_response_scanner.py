"""Scanner: mutation response shape - all mutations return the same snapshot type.

Checks:
1. Route handlers that handle POST/PUT/DELETE call res.json() with a
   consistent return type (not { success: true } patterns).
2. HTTP client mutation functions all declare the same return type.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import List

from lern_scanner_base import TypeScriptScanner, Violation

_RES_JSON_RE = re.compile(r"res\.(?:status\(\d+\)\.)?json\(\s*(\{[^}]*\}|\w+)")
_SUCCESS_PATTERN_RE = re.compile(r"\{\s*(?:success|message|ok|status)\s*:")
_RETURN_TYPE_RE = re.compile(r":\s*Promise<(\w+)>")


class MutationResponseScanner(TypeScriptScanner):
    """Check that all mutations return a consistent aggregate snapshot."""

    RULE = "standard-mutation-response"

    def scan(self, root: Path, files: List[Path]) -> List[Violation]:
        violations: List[Violation] = []

        for domain_path in self._find_domain_packages(root):
            violations += self._check_server_routes(domain_path)
            violations += self._check_http_client(domain_path)

        return violations

    def _check_server_routes(self, domain_path: Path) -> List[Violation]:
        server = self._server_file(domain_path)
        if server is None:
            return []
        content = self._read_file_content(server)
        if content is None:
            return []
        return self._success_envelope_hits(server, content)

    def _success_envelope_hits(self, server: Path, content: str) -> List[Violation]:
        violations: List[Violation] = []
        for match in _RES_JSON_RE.finditer(content):
            if not _SUCCESS_PATTERN_RE.match(match.group(1)):
                continue
            violations.append(
                self.v(
                    "Route returns { success/message/ok } instead of "
                    "an aggregate snapshot. All mutations must return the "
                    "same snapshot type.",
                    str(server),
                    content[: match.start()].count("\n") + 1,
                    severity="error",
                )
            )
        return violations

    def _check_http_client(self, domain_path: Path) -> List[Violation]:
        client = self._client_file(domain_path)
        if client is None:
            return []
        content = self._read_file_content(client)
        if content is None:
            return []
        mutation_types = {m.group(1) for m in _RETURN_TYPE_RE.finditer(content) if m.group(1) != "void"}
        if len(mutation_types) <= 1:
            return []
        return [
            self.v(
                f"HTTP client in {client.name} returns multiple different "
                f"types from mutations: {sorted(mutation_types)}. All "
                "mutations on the same aggregate should return the same "
                "snapshot type.",
                str(client),
                severity="warning",
            )
        ]
