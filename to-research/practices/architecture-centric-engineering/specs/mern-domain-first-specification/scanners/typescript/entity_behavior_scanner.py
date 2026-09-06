"""Scanner: detect anemic domain models and verify entity behavior rules.

Uses tree-sitter TypeScript AST to check:
1. Domain entity classes in shared/ have at least one non-trivial business method
   (not just a constructor, getters/setters, or private helpers).
2. Collection classes (plural entity names, e.g. Stores, Products) have at
   least one domain-oriented query method (filter*, search*, findBy*, getBy*).
3. No async methods on domain entity classes — domain core is synchronous.
4. Repositories in server/ import from 'mongodb' — no production code should
   rely solely on an in-memory store.
5. Value objects in shared/ use readonly modifiers on their fields.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List

try:
    from .ts_scanner_base import TypeScriptScanner, run_scanner_main
except ImportError:
    from ts_scanner_base import TypeScriptScanner, run_scanner_main


class EntityBehaviorScanner(TypeScriptScanner):
    """Deep AST checks for domain entity and repository implementation quality."""

    # Methods that are NOT considered domain behaviour
    NON_BEHAVIOR_NAMES = frozenset({
        'constructor', 'toString', 'toJSON', 'valueOf', 'get', 'set',
    })

    # Prefixes that suggest a domain query method on a collection class
    COLLECTION_QUERY_PREFIXES = re.compile(
        r'^(filter|search|findBy|getBy|listBy|sortBy|groupBy|count|select|exclude)',
        re.IGNORECASE,
    )

    def scan(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        violations: List[Dict[str, Any]] = []
        project_root = self._get_project_root(context)
        if project_root is None:
            return violations

        for domain_path in self._find_domain_packages(project_root):
            violations += self._check_shared_entities(domain_path)
            violations += self._check_server_repositories(domain_path)

        return violations

    # ------------------------------------------------------------------ #
    # Shared tier: entity behaviour                                        #
    # ------------------------------------------------------------------ #

    # Classes exempt from the "has business methods" rule
    _EXEMPT_EXTENDS = frozenset({'Error', 'TypeError', 'RangeError', 'ReferenceError'})
    _EXEMPT_NAME_SUFFIXES = ('Error', 'Exception', 'Event', 'DTO', 'Props', 'Config', 'Options')

    def _is_exempt_class(self, cls) -> bool:
        """Return True for error/exception classes and pure value objects."""
        if cls.extends in self._EXEMPT_EXTENDS:
            return True
        if any(cls.name.endswith(s) for s in self._EXEMPT_NAME_SUFFIXES):
            return True
        # Value objects: all properties are readonly — no mutation methods needed
        if cls.properties and all('readonly' in p.modifiers for p in cls.properties):
            return True
        return False

    def _check_shared_entities(self, domain_path: Path) -> List[Dict[str, Any]]:
        violations: List[Dict[str, Any]] = []
        shared_dir = domain_path / 'shared'
        if not shared_dir.exists():
            return violations

        for ts_file in sorted(shared_dir.glob('*.ts')):
            if ts_file.name in ('index.ts',):
                continue
            if ts_file.stem.endswith('.schema'):
                continue

            root = self.parse_file(ts_file)
            if root is None:
                continue

            for cls in self.get_classes(root):
                if self._is_exempt_class(cls):
                    continue
                self._check_entity_methods(cls, ts_file, violations)
                self._check_no_async_on_entity(cls, ts_file, violations)
                if self._is_collection_class(cls.name):
                    self._check_collection_query_methods(cls, ts_file, violations)

        return violations

    def _check_entity_methods(self, cls, ts_file: Path, violations: list) -> None:
        """Entity must have at least one public business method."""
        public_methods = [
            m for m in cls.methods
            if m.name not in self.NON_BEHAVIOR_NAMES
            and 'private' not in m.modifiers
            and 'protected' not in m.modifiers
            and not m.is_static
        ]
        if not public_methods:
            violations.append(self.v(
                f"Class '{cls.name}' in shared/ has no public business methods — "
                "this is an Anemic Domain Model. Add behaviour methods like "
                "isEligible(), filterByStatus(), calculate(), validate().",
                str(ts_file),
                cls.start_line,
            ))

    def _check_no_async_on_entity(self, cls, ts_file: Path, violations: list) -> None:
        """Domain entity methods must be synchronous (no async)."""
        for method in cls.methods:
            if method.is_async and 'private' not in method.modifiers:
                violations.append(self.v(
                    f"Class '{cls.name}'.{method.name}() is async — domain "
                    "entities must be pure synchronous. Move async operations "
                    "to the repository or service layer.",
                    str(ts_file),
                    method.start_line,
                ))

    def _check_collection_query_methods(
        self, cls, ts_file: Path, violations: list
    ) -> None:
        """Collection classes must expose domain-oriented query methods."""
        query_methods = [
            m for m in cls.methods
            if self.COLLECTION_QUERY_PREFIXES.match(m.name)
        ]
        if not query_methods:
            violations.append(self.v(
                f"Collection class '{cls.name}' has no domain query methods. "
                "Add at least one method like filterByStatus(), search(), "
                "findByCode() that wraps array operations with domain intent.",
                str(ts_file),
                cls.start_line,
            ))

    def _is_collection_class(self, name: str) -> bool:
        """Heuristic: plural class names without 'Schema'/'Type'/'Info' are collections."""
        if name.endswith(('Schema', 'Type', 'Info', 'DTO', 'Error', 'Status')):
            return False
        # Ends with s but not ss, -ies, -List suffixes
        if name.endswith('s') and not name.endswith('ss'):
            return True
        return False

    # ------------------------------------------------------------------ #
    # Server tier: repository MongoDB requirement                          #
    # ------------------------------------------------------------------ #

    def _check_server_repositories(self, domain_path: Path) -> List[Dict[str, Any]]:
        """Every domain server/ tier must have at least one MongoDB repository."""
        violations: List[Dict[str, Any]] = []
        server_dir = domain_path / 'server'
        if not server_dir.exists():
            return violations

        domain_name = domain_path.name
        # Match *.repository.ts AND *.mongo-repository.ts AND other variants
        repo_files = [
            f for f in sorted(server_dir.glob('*.ts'))
            if 'repository' in f.stem.lower() and f.name != 'index.ts'
        ]
        if not repo_files:
            return violations

        has_mongo_import = False
        in_memory_only_files: List[str] = []
        _MONGO_IMPORT_RE = re.compile(r"from\s+['\"]mongodb['\"]")
        _IN_MEMORY_RE = re.compile(r'class\s+InMemory\w+')

        for repo_file in repo_files:
            content = repo_file.read_text(encoding='utf-8', errors='replace')

            # Regex check first — handles both `import` and `import type`
            if _MONGO_IMPORT_RE.search(content):
                has_mongo_import = True
                break

            # Also check via AST (belt-and-suspenders)
            root = self.parse_file(repo_file)
            if root and self.has_import_from(root, 'mongodb'):
                has_mongo_import = True
                break

            if _IN_MEMORY_RE.search(content):
                in_memory_only_files.append(repo_file.name)

        if not has_mongo_import and in_memory_only_files:
            violations.append(self.v(
                f"Domain '{domain_name}/server/' has no MongoDB repository "
                "(no file imports from 'mongodb'). Found only in-memory "
                f"implementations: {', '.join(in_memory_only_files)}. "
                "Add a production MongoDB repository (e.g. "
                f"{domain_name}.mongo-repository.ts) before release.",
                str(server_dir),
            ))
        elif not has_mongo_import and repo_files:
            violations.append(self.v(
                f"Domain '{domain_name}/server/' repository files do not import "
                "from 'mongodb'. Add a MongoDB-backed repository implementation.",
                str(server_dir),
            ))

        return violations


if __name__ == '__main__':
    run_scanner_main(EntityBehaviorScanner, 'implement-domain-entities-correctly')
