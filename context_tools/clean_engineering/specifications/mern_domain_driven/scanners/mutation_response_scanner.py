"""Scanner: mutation response shape - all mutations return the same snapshot type.

Checks:
1. Route handlers that handle POST/PUT/DELETE call res.json() with a
   consistent return type (not { success: true } patterns).
2. HTTP client mutation functions all declare the same return type.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import List, Set

from mern_scanner_base import TypeScriptScanner
from scan.violation import Violation

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
        violations: List[Violation] = []
        server = self._server_file(domain_path)
        if server is None:
            return violations

        content = self._read_file_content(server)
        if content is None:
            return violations

        for m in _RES_JSON_RE.finditer(content):
            response_arg = m.group(1)
            if _SUCCESS_PATTERN_RE.match(response_arg):
                line_num = content[: m.start()].count("\n") + 1
                violations.append(
                    self.v(
                        "Route returns { success/message/ok } instead of "
                        "an aggregate snapshot. All mutations must return the "
                        "same snapshot type.",
                        str(server),
                        line_num,
                        severity="error",
                    )
                )

        return violations

    def _check_http_client(self, domain_path: Path) -> List[Violation]:
        violations: List[Violation] = []
        client = self._client_file(domain_path)
        if client is None:
            return violations

        content = self._read_file_content(client)
        if content is None:
            return violations

        return_types: Set[str] = set()
        for m in _RETURN_TYPE_RE.finditer(content):
            return_types.add(m.group(1))

        mutation_types = {t for t in return_types if t != "void"}
        if len(mutation_types) > 1:
            violations.append(
                self.v(
                    f"HTTP client in {client.name} returns multiple different "
                    f"types from mutations: {sorted(mutation_types)}. All "
                    "mutations on the same aggregate should return the same "
                    "snapshot type.",
                    str(client),
                    severity="warning",
                )
            )

        return violations
