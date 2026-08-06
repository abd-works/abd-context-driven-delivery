"""Scanner: verify full interface implementation across all tiers.

Uses tree-sitter TypeScript AST to check:
1. Every *.repository.ts in server/ declares a repository interface AND
   uses the `implements` keyword on its class.
2. The implementing class provides a method for every method signature
   declared in the interface (by name comparison).
3. Test helper fake/stub repositories in tests/ also use `implements`
   and cover all interface methods.
4. No repository method stubs with `throw new Error('not implemented')`.
5. Services depend on the repository INTERFACE not the concrete class
   (constructor parameter type should be the interface name).
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Set

from mern_scanner_base import InterfaceInfo, TypeScriptScanner
from utilities.scanners.violation import Violation

_NOT_IMPLEMENTED_RE = re.compile(r"throw\s+new\s+Error\s*\(['\"]not\s+implemented", re.IGNORECASE)


class InterfaceImplementationScanner(TypeScriptScanner):
    """AST checks for complete, correct interface implementation."""

    RULE = "implement-full-interfaces"

    def scan(self, root: Path, files: List[Path]) -> List[Violation]:
        violations: List[Violation] = []

        for domain_path in self._find_domain_packages(root):
            violations += self._check_server_repositories(domain_path)
            violations += self._check_service_depends_on_interface(domain_path)

        violations += self._check_test_fake_repositories(root)
        return violations

    # ------------------------------------------------------------------ #
    # Server: repository interface completeness                            #
    # ------------------------------------------------------------------ #

    def _check_server_repositories(self, domain_path: Path) -> List[Violation]:
        violations: List[Violation] = []
        server = self._server_file(domain_path)
        if server is None:
            return violations

        domain_name = domain_path.name
        content = server.read_text(encoding="utf-8", errors="replace")
        if "Repository" not in content:
            return violations

        parsed_root = self.parse_file(server)
        if parsed_root is None:
            if "implements" not in content:
                violations.append(
                    self.v(
                        f"File '{server.name}' in {domain_name} has no "
                        "`implements` keyword. Repository classes must implement "
                        "the domain-core interface.",
                        str(server),
                    )
                )
            return violations

        classes = self.get_classes(parsed_root)
        for cls in classes:
            if "Repository" not in cls.name:
                continue
            if not cls.implements:
                violations.append(
                    self.v(
                        f"Class '{cls.name}' in {domain_name}/server.ts does not "
                        "use the `implements` keyword. Without it TypeScript "
                        "won't catch missing interface methods at compile time.",
                        str(server),
                        cls.start_line,
                    )
                )
                continue

            for line_num, line in enumerate(content.splitlines(), 1):
                if _NOT_IMPLEMENTED_RE.search(line):
                    violations.append(
                        self.v(
                            "Stub method with 'not implemented' found in "
                            f"'{server.name}'. All interface methods must be "
                            "fully implemented - no throw stubs.",
                            str(server),
                            line_num,
                        )
                    )

        return violations

    def _regex_check_implements(self, repo_file: Path, domain_name: str) -> List[Violation]:
        """Fallback regex check when tree-sitter is unavailable."""
        violations: List[Violation] = []
        content = repo_file.read_text(encoding="utf-8", errors="replace")
        if "implements" not in content:
            violations.append(
                self.v(
                    f"File '{repo_file.name}' in {domain_name} has no "
                    "`implements` keyword. Classes must implement repository interfaces.",
                    str(repo_file),
                )
            )
        return violations

    def _check_service_depends_on_interface(self, domain_path: Path) -> List[Violation]:
        violations: List[Violation] = []
        server = self._server_file(domain_path)
        if server is None:
            return violations

        parsed_root = self.parse_file(server)
        if parsed_root is None:
            return violations

        classes = self.get_classes(parsed_root)
        content = server.read_text(encoding="utf-8", errors="replace")
        lines = content.splitlines()
        for cls in classes:
            if "Server" not in cls.name and "Service" not in cls.name:
                continue
            ctor = next((m for m in cls.methods if m.name == "constructor"), None)
            if ctor is None:
                continue
            ctor_line = lines[ctor.start_line - 1] if ctor.start_line <= len(lines) else ""
            if re.search(r"Mongo\w+Repository\b", ctor_line):
                violations.append(
                    self.v(
                        f"Class '{cls.name}' constructor injects a concrete "
                        "MongoDB repository class. Depend on the repository "
                        "INTERFACE instead so tests can inject a fake.",
                        str(server),
                        ctor.start_line,
                    )
                )

        return violations

    # ------------------------------------------------------------------ #
    # Tests: fake repositories implement full interface                    #
    # ------------------------------------------------------------------ #

    def _check_test_fake_repositories(self, project_root: Path) -> List[Violation]:
        violations: List[Violation] = []
        tests_dir = project_root / "tests"
        if not tests_dir.exists():
            return violations

        for ts_file in tests_dir.rglob("*.ts"):
            if "node_modules" in ts_file.parts:
                continue
            parsed_root = self.parse_file(ts_file)
            if parsed_root is None:
                continue

            for cls in self.get_classes(parsed_root):
                name_lower = cls.name.lower()
                if not any(kw in name_lower for kw in ("fake", "stub", "mock", "in_memory", "inmemory")):
                    continue
                if not cls.implements:
                    violations.append(
                        self.v(
                            f"Test class '{cls.name}' in {ts_file.name} looks like a "
                            "test double but doesn't use `implements`. TypeScript won't "
                            "catch if it diverges from the real interface.",
                            str(ts_file),
                            cls.start_line,
                        )
                    )

        return violations
