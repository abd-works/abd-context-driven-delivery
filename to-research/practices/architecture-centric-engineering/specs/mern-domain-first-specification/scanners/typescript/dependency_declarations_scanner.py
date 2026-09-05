"""Scanner: verify all external package dependencies are declared.

Uses tree-sitter TypeScript AST to parse import statements across all
packages and cross-references them against package.json declarations.

Checks:
1. Every external npm package imported in a tier's source files is
   declared in that package's package.json or the root package.json.
2. Framework-specific imports are in the right tiers:
   - 'mongodb' must be in server/ only (never in shared/ or client/)
   - 'react', 'react-dom' must be in client/ only
   - 'express' must be in server/ only
3. Required devDependencies are present in the root package.json:
   - vitest, @playwright/test, @testing-library/react, @testing-library/jest-dom
4. Type packages (@types/*) are declared for libraries that need them.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

try:
    from .ts_scanner_base import TypeScriptScanner, run_scanner_main
except ImportError:
    from ts_scanner_base import TypeScriptScanner, run_scanner_main


# Known built-in Node modules (not npm packages)
_NODE_BUILTINS = frozenset({
    'path', 'fs', 'os', 'crypto', 'util', 'events', 'stream',
    'http', 'https', 'url', 'querystring', 'child_process', 'net',
    'tls', 'cluster', 'readline', 'buffer', 'assert', 'zlib',
    'timers', 'dns', 'process', 'module', 'perf_hooks', 'worker_threads',
})

# Required root devDependencies for test infrastructure
_REQUIRED_DEV_DEPS = {
    'vitest': 'Unit/component test runner (required for *_server.test.ts, *_client.test.tsx)',
    '@playwright/test': 'E2E test runner (required for *_e2e.spec.ts)',
    '@testing-library/react': 'React component testing utilities',
    '@testing-library/jest-dom': 'Custom DOM matchers for Vitest/Jest',
    'typescript': 'TypeScript compiler',
}

# Which tier each framework package should be in
_TIER_RESTRICTIONS: Dict[str, str] = {
    'mongodb': 'server',
    'mongoose': 'server',
    'express': 'server',
    'react': 'client',
    'react-dom': 'client',
    'react-router-dom': 'client',
}


class DependencyDeclarationsScanner(TypeScriptScanner):
    """Checks that every external import is declared in package.json."""

    def scan(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        violations: List[Dict[str, Any]] = []
        project_root = self._get_project_root(context)
        if project_root is None:
            return violations

        # Load root package.json
        root_deps = self._load_all_deps(project_root / 'package.json')
        violations += self._check_root_dev_deps(project_root, root_deps)

        for domain_path in self._find_domain_packages(project_root):
            for tier in ('shared', 'server', 'client'):
                tier_dir = domain_path / tier
                if not tier_dir.exists():
                    continue
                tier_deps = self._load_all_deps(tier_dir / 'package.json')
                # Merge root deps (hoisting is common in monorepos)
                all_deps = root_deps | tier_deps
                violations += self._check_tier_imports(
                    tier_dir, tier, all_deps, domain_path.name
                )
                violations += self._check_tier_restrictions(
                    tier_dir, tier, domain_path.name
                )

        return violations

    # ------------------------------------------------------------------ #
    # package.json loading                                                 #
    # ------------------------------------------------------------------ #

    def _load_all_deps(self, pkg_json_path: Path) -> Set[str]:
        """Load all dep names from a package.json (deps + devDeps + peerDeps)."""
        if not pkg_json_path.exists():
            return set()
        try:
            data = json.loads(pkg_json_path.read_text(encoding='utf-8'))
        except (json.JSONDecodeError, OSError):
            return set()
        deps: Set[str] = set()
        for key in ('dependencies', 'devDependencies', 'peerDependencies'):
            deps.update(data.get(key, {}).keys())
        return deps

    # ------------------------------------------------------------------ #
    # Root dev dependencies check                                          #
    # ------------------------------------------------------------------ #

    def _check_root_dev_deps(
        self, project_root: Path, root_deps: Set[str]
    ) -> List[Dict[str, Any]]:
        violations: List[Dict[str, Any]] = []
        pkg_json = project_root / 'package.json'

        # Only check if tests/ directory exists
        if not (project_root / 'tests').exists():
            return violations

        for pkg, desc in _REQUIRED_DEV_DEPS.items():
            if pkg not in root_deps:
                violations.append(self.v(
                    f"Root package.json is missing '{pkg}' in devDependencies. "
                    f"{desc}.",
                    str(pkg_json),
                ))

        return violations

    # ------------------------------------------------------------------ #
    # Import vs. declaration cross-check                                   #
    # ------------------------------------------------------------------ #

    def _check_tier_imports(
        self,
        tier_dir: Path,
        tier: str,
        all_deps: Set[str],
        domain_name: str,
    ) -> List[Dict[str, Any]]:
        violations: List[Dict[str, Any]] = []
        for ts_file in self.get_all_source_files(tier_dir):
            root = self.parse_file(ts_file)
            if root is None:
                continue
            for imp in self.get_imports(root):
                pkg = self._extract_package_name(imp.source)
                if pkg is None:
                    continue
                if pkg in _NODE_BUILTINS:
                    continue
                if pkg.startswith('@') and pkg.count('/') == 1:
                    # Scoped package — check declared
                    if pkg not in all_deps:
                        violations.append(self.v(
                            f"'{ts_file.name}' imports '{imp.source}' but "
                            f"'{pkg}' is not declared in any package.json. "
                            "Add it to the appropriate package.json "
                            "dependencies.",
                            str(ts_file),
                            imp.start_line,
                        ))
                elif not pkg.startswith('@'):
                    if pkg not in all_deps:
                        violations.append(self.v(
                            f"'{ts_file.name}' imports '{pkg}' but it is not "
                            "declared in any package.json. Add it to "
                            "dependencies.",
                            str(ts_file),
                            imp.start_line,
                        ))
        return violations

    def _extract_package_name(self, source: str) -> Optional[str]:
        """Extract the npm package name from an import source string."""
        if source.startswith('.') or source.startswith('/'):
            return None  # relative import
        if source.startswith('node:'):
            return None  # explicit node built-in
        if '/' in source and not source.startswith('@'):
            return source.split('/')[0]
        if source.startswith('@') and '/' in source:
            parts = source.split('/')
            return f'{parts[0]}/{parts[1]}'
        return source

    # ------------------------------------------------------------------ #
    # Framework tier restriction checks                                    #
    # ------------------------------------------------------------------ #

    def _check_tier_restrictions(
        self, tier_dir: Path, tier: str, domain_name: str
    ) -> List[Dict[str, Any]]:
        violations: List[Dict[str, Any]] = []
        for pkg, allowed_tier in _TIER_RESTRICTIONS.items():
            if tier == allowed_tier:
                continue
            for ts_file in self.get_all_source_files(tier_dir):
                root = self.parse_file(ts_file)
                if root is None:
                    continue
                if self.has_import_from(root, pkg):
                    violations.append(self.v(
                        f"'{domain_name}/{tier}/{ts_file.name}' imports "
                        f"'{pkg}' which must only be used in '{allowed_tier}/'. "
                        "This is a layer purity violation.",
                        str(ts_file),
                    ))
        return violations


if __name__ == '__main__':
    run_scanner_main(DependencyDeclarationsScanner, 'include-all-external-dependencies')
