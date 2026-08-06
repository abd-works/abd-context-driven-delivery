"""Scanner: cross-layer method naming - same domain verb in every layer.

Checks:
1. For each domain method in the domain core, a matching method exists server-side.
2. HTTP client functions match the domain method name (not CRUD generics).
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import List, Set

from mern_scanner_base import TypeScriptScanner
from utilities.scanners.violation import Violation

_CRUD_GENERICS = frozenset(
    {
        "create", "read", "update", "delete", "get", "set", "list",
        "find", "fetch", "save", "remove", "add", "modify", "patch",
    }
)

_METHOD_RE = re.compile(r"(?:async\s+)?(\w+)\s*\([^)]*\)\s*(?::\s*[^{]+)?\s*\{")
_EXPORT_FUNCTION_RE = re.compile(r"export\s+(?:async\s+)?function\s+(\w+)")


class CrossLayerNamingScanner(TypeScriptScanner):
    """Check that domain method names are consistent across all layers."""

    RULE = "cross-layer-method-naming"

    def scan(self, root: Path, files: List[Path]) -> List[Violation]:
        violations: List[Violation] = []

        for domain_path in self._find_domain_packages(root):
            violations += self._check_domain(domain_path)

        return violations

    def _check_domain(self, domain_path: Path) -> List[Violation]:
        violations: List[Violation] = []

        shared_methods = self._extract_shared_methods(domain_path)
        if not shared_methods:
            return violations

        server_methods = self._extract_server_methods(domain_path)
        http_functions = self._extract_http_functions(domain_path)

        for method in shared_methods:
            base = method.lower()
            if base in _CRUD_GENERICS:
                continue

            if server_methods and method not in server_methods:
                for srv_method in server_methods:
                    if srv_method.lower() in _CRUD_GENERICS and base not in _CRUD_GENERICS:
                        violations.append(
                            self.v(
                                f"Domain method '{method}' in domain core has no matching "
                                f"server method. Server uses CRUD-generic "
                                f"'{srv_method}' instead. Rename to '{method}'.",
                                str(domain_path / "server.ts"),
                                severity="warning",
                            )
                        )
                        break

            if http_functions and method not in http_functions:
                for fn in http_functions:
                    if fn.startswith("fetch") and method in fn.lower():
                        violations.append(
                            self.v(
                                f"Domain method '{method}' in domain core has no matching "
                                f"HTTP client function. Client uses 'fetch'-prefixed "
                                f"'{fn}' instead. Rename to '{method}'.",
                                str(self._client_file(domain_path) or domain_path / "client.tsx"),
                                severity="warning",
                            )
                        )
                        break

        return violations

    def _extract_shared_methods(self, domain_path: Path) -> Set[str]:
        methods: Set[str] = set()
        core = self._domain_core_file(domain_path)
        if core is None:
            return methods
        content = self._read_file_content(core)
        if content is None:
            return methods
        for m in _METHOD_RE.finditer(content):
            name = m.group(1)
            if name[0].islower() and not name.startswith("constructor"):
                methods.add(name)
        return methods

    def _extract_server_methods(self, domain_path: Path) -> Set[str]:
        methods: Set[str] = set()
        server = self._server_file(domain_path)
        if server is None:
            return methods
        content = self._read_file_content(server)
        if content is None:
            return methods
        for m in _METHOD_RE.finditer(content):
            name = m.group(1)
            if name[0].islower() and not name.startswith("constructor"):
                methods.add(name)
        return methods

    def _extract_http_functions(self, domain_path: Path) -> Set[str]:
        fns: Set[str] = set()
        client = self._client_file(domain_path)
        if client is None:
            return fns
        content = self._read_file_content(client)
        if content is None:
            return fns
        for m in _EXPORT_FUNCTION_RE.finditer(content):
            fns.add(m.group(1))
        return fns
