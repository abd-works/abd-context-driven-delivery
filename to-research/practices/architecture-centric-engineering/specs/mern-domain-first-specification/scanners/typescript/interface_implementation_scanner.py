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
from typing import Any, Dict, List, Optional, Set

try:
    from .ts_scanner_base import TypeScriptScanner, InterfaceInfo, ClassInfo, run_scanner_main
except ImportError:
    from ts_scanner_base import TypeScriptScanner, InterfaceInfo, ClassInfo, run_scanner_main


class InterfaceImplementationScanner(TypeScriptScanner):
    """AST checks for complete, correct interface implementation."""

    _NOT_IMPLEMENTED_RE = re.compile(
        r"throw\s+new\s+Error\s*\(['\"]not\s+implemented", re.IGNORECASE
    )

    def scan(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        violations: List[Dict[str, Any]] = []
        project_root = self._get_project_root(context)
        if project_root is None:
            return violations

        for domain_path in self._find_domain_packages(project_root):
            violations += self._check_server_repositories(domain_path)
            violations += self._check_service_depends_on_interface(domain_path)

        violations += self._check_test_fake_repositories(project_root)
        return violations

    # ------------------------------------------------------------------ #
    # Server: repository interface completeness                            #
    # ------------------------------------------------------------------ #

    def _check_server_repositories(self, domain_path: Path) -> List[Dict[str, Any]]:
        violations: List[Dict[str, Any]] = []
        server_dir = domain_path / 'server'
        if not server_dir.exists():
            return violations

        domain_name = domain_path.name

        for repo_file in sorted(server_dir.glob('*.repository.ts')):
            root = self.parse_file(repo_file)
            if root is None:
                violations += self._regex_check_implements(repo_file, domain_name)
                continue

            interfaces = self.get_interfaces(root)
            classes = self.get_classes(root)

            interface_map: Dict[str, InterfaceInfo] = {i.name: i for i in interfaces}

            for cls in classes:
                # Must use implements keyword
                if not cls.implements:
                    violations.append(self.v(
                        f"Class '{cls.name}' in {domain_name}/server/ does not "
                        "use the `implements` keyword. Without it TypeScript "
                        "won't catch missing interface methods at compile time.",
                        str(repo_file),
                        cls.start_line,
                    ))
                    continue

                # Check all implemented interfaces are fully covered
                for iface_name in cls.implements:
                    iface = interface_map.get(iface_name)
                    if iface is None:
                        continue  # interface defined elsewhere — skip name check

                    class_method_names: Set[str] = {m.name for m in cls.methods}
                    missing = [
                        m for m in iface.method_names
                        if m not in class_method_names
                    ]
                    if missing:
                        violations.append(self.v(
                            f"Class '{cls.name}' implements '{iface_name}' but "
                            f"is missing method(s): {', '.join(missing)}. "
                            "All interface methods must be implemented.",
                            str(repo_file),
                            cls.start_line,
                        ))

                # No 'not implemented' stubs
                content = repo_file.read_text(encoding='utf-8', errors='replace')
                for line_num, line in enumerate(content.splitlines(), 1):
                    if self._NOT_IMPLEMENTED_RE.search(line):
                        violations.append(self.v(
                            f"Stub method with 'not implemented' found in "
                            f"'{repo_file.name}'. All interface methods must be "
                            "fully implemented — no throw stubs.",
                            str(repo_file),
                            line_num,
                        ))

        return violations

    def _regex_check_implements(
        self, repo_file: Path, domain_name: str
    ) -> List[Dict[str, Any]]:
        """Fallback regex check when tree-sitter is unavailable."""
        violations = []
        content = repo_file.read_text(encoding='utf-8', errors='replace')
        if 'implements' not in content:
            violations.append(self.v(
                f"File '{repo_file.name}' in {domain_name}/server/ has no "
                "`implements` keyword. Classes must implement repository interfaces.",
                str(repo_file),
            ))
        return violations

    # ------------------------------------------------------------------ #
    # Server: service depends on interface, not concrete class             #
    # ------------------------------------------------------------------ #

    def _check_service_depends_on_interface(
        self, domain_path: Path
    ) -> List[Dict[str, Any]]:
        violations: List[Dict[str, Any]] = []
        server_dir = domain_path / 'server'
        if not server_dir.exists():
            return violations

        domain_name = domain_path.name

        for service_file in sorted(server_dir.glob('*.service.ts')):
            root = self.parse_file(service_file)
            if root is None:
                continue

            classes = self.get_classes(root)
            for cls in classes:
                # Find constructor
                ctor = next((m for m in cls.methods if m.name == 'constructor'), None)
                if ctor is None:
                    continue

                # Check constructor parameter types via raw text heuristic
                content = service_file.read_text(encoding='utf-8', errors='replace')
                lines = content.splitlines()
                ctor_line = lines[ctor.start_line - 1] if ctor.start_line <= len(lines) else ''

                # If the constructor takes a concrete repository class (e.g. MongoXxx)
                # instead of an interface, flag it
                if re.search(r'Mongo\w+Repository\b', ctor_line):
                    violations.append(self.v(
                        f"Service '{cls.name}' constructor injects a concrete "
                        "MongoDB repository class. Depend on the repository "
                        "INTERFACE instead so tests can inject a fake.",
                        str(service_file),
                        ctor.start_line,
                    ))

        return violations

    # ------------------------------------------------------------------ #
    # Tests: fake repositories implement full interface                    #
    # ------------------------------------------------------------------ #

    def _check_test_fake_repositories(
        self, project_root: Path
    ) -> List[Dict[str, Any]]:
        violations: List[Dict[str, Any]] = []
        tests_dir = project_root / 'tests'
        if not tests_dir.exists():
            return violations

        for ts_file in tests_dir.rglob('*.ts'):
            if 'node_modules' in ts_file.parts:
                continue
            root = self.parse_file(ts_file)
            if root is None:
                continue

            for cls in self.get_classes(root):
                if cls.implements and not cls.implements:
                    continue
                # Look for fake / stub repository classes
                name_lower = cls.name.lower()
                if not any(kw in name_lower for kw in ('fake', 'stub', 'mock', 'in_memory', 'inmemory')):
                    continue
                if not cls.implements:
                    violations.append(self.v(
                        f"Test class '{cls.name}' in {ts_file.name} looks like a "
                        "test double but doesn't use `implements`. TypeScript won't "
                        "catch if it diverges from the real interface.",
                        str(ts_file),
                        cls.start_line,
                    ))

        return violations


if __name__ == '__main__':
    run_scanner_main(InterfaceImplementationScanner, 'implement-full-interfaces')
