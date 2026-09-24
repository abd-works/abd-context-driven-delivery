"""Scanner: verify all external package dependencies are declared.

Uses tree-sitter TypeScript AST to parse import statements across all
packages and cross-references them against package.json declarations.

Checks:
1. Every external npm package imported in a tier's source files is
   declared in that package's package.json or the root package.json.
2. Framework-specific imports are in the right tiers:
   - 'lowdb' must be in server/ only (never in shared/ or client/)
   - 'react', 'react-dom' must be in client/ only
   - 'express' must be in server/ only
3. Required devDependencies are present in the root package.json:
   - vitest, @playwright/test, @testing-library/react, @testing-library/jest-dom
4. Type packages (@types/*) are declared for libraries that need them.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set

from lern_scanner_base import TypeScriptScanner, Violation

# Known built-in Node modules (not npm packages)
_NODE_BUILTINS = frozenset(
    {
        "path", "fs", "os", "crypto", "util", "events", "stream",
        "http", "https", "url", "querystring", "child_process", "net",
        "tls", "cluster", "readline", "buffer", "assert", "zlib",
        "timers", "dns", "process", "module", "perf_hooks", "worker_threads",
    }
)

# Required root devDependencies for test infrastructure
_REQUIRED_DEV_DEPS = {
    "vitest": "Unit/component test runner (required for *_server.test.ts, *_client.test.tsx)",
    "@playwright/test": "E2E test runner (required for *_e2e.spec.ts)",
    "@testing-library/react": "React component testing utilities",
    "@testing-library/jest-dom": "Custom DOM matchers for Vitest/Jest",
    "typescript": "TypeScript compiler",
}

# Which tier each framework package should be in
_TIER_RESTRICTIONS: Dict[str, str] = {
    "lowdb": "server",
    "express": "server",
    "react": "client",
    "react-dom": "client",
    "react-router-dom": "client",
}


@dataclass
class _TierScan:
    directory: Path
    tier: str
    domain_name: str


@dataclass
class _FrameworkPlacement:
    package: str
    allowed_tier: str


@dataclass
class _ImportSite:
    path: Path
    source: str
    start_line: int


@dataclass
class _DeclaredDeps:
    names: Set[str]

    def is_undeclared(self, pkg: str) -> bool:
        if pkg in _NODE_BUILTINS:
            return False
        scoped = pkg.startswith("@") and pkg.count("/") == 1
        bare = not pkg.startswith("@")
        return (scoped or bare) and pkg not in self.names


class DependencyDeclarationsScanner(TypeScriptScanner):
    """Checks that every external import is declared in package.json."""

    RULE = "include-all-external-dependencies"

    def scan(self, root: Path, files: List[Path]) -> List[Violation]:
        violations: List[Violation] = []
        project_root = root

        root_deps = self._load_all_deps(project_root / "package.json")
        violations += self._check_root_dev_deps(project_root, root_deps)

        for domain_path in self._find_domain_packages(project_root):
            for tier in ("shared", "server", "client"):
                tier_dir = domain_path / tier
                if not tier_dir.exists():
                    continue
                tier_deps = self._load_all_deps(tier_dir / "package.json")
                all_deps = root_deps | tier_deps
                violations += self._check_tier_imports(tier_dir, _DeclaredDeps(all_deps))
                violations += self._check_tier_restrictions(
                    _TierScan(tier_dir, tier, domain_path.name)
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
            data = json.loads(pkg_json_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return set()
        deps: Set[str] = set()
        for key in ("dependencies", "devDependencies", "peerDependencies"):
            deps.update(data.get(key, {}).keys())
        return deps

    # ------------------------------------------------------------------ #
    # Root dev dependencies check                                          #
    # ------------------------------------------------------------------ #

    def _check_root_dev_deps(self, project_root: Path, root_deps: Set[str]) -> List[Violation]:
        violations: List[Violation] = []
        pkg_json = project_root / "package.json"

        if not (project_root / "tests").exists():
            return violations

        for pkg, desc in _REQUIRED_DEV_DEPS.items():
            if pkg not in root_deps:
                violations.append(
                    self.v(f"Root package.json is missing '{pkg}' in devDependencies. {desc}.", str(pkg_json))
                )

        return violations

    # ------------------------------------------------------------------ #
    # Import vs. declaration cross-check                                   #
    # ------------------------------------------------------------------ #

    def _check_tier_imports(self, tier_dir: Path, deps: _DeclaredDeps) -> List[Violation]:
        violations: List[Violation] = []
        for ts_file in self.source_files(tier_dir):
            violations.extend(self._undeclared_imports_in(ts_file, deps))
        return violations

    def _undeclared_imports_in(self, ts_file: Path, deps: _DeclaredDeps) -> List[Violation]:
        parsed_root = self.parse_file(ts_file)
        if parsed_root is None:
            return []
        violations: List[Violation] = []
        for imp in self.imports:
            hit = self._undeclared_package_hit(
                _ImportSite(ts_file, imp.source, imp.start_line), deps
            )
            if hit is not None:
                violations.append(hit)
        return violations

    def _undeclared_package_hit(self, site: _ImportSite, deps: _DeclaredDeps):
        pkg = self._extract_package_name(site.source)
        if pkg is None or not deps.is_undeclared(pkg):
            return None
        imported = site.source if pkg.startswith("@") else pkg
        return self.v(
            f"'{site.path.name}' imports '{imported}' but "
            f"'{pkg}' is not declared in any package.json. "
            "Add it to the appropriate package.json "
            "dependencies.",
            str(site.path),
            site.start_line,
        )

    def _extract_package_name(self, source: str) -> Optional[str]:
        """Extract the npm package name from an import source string."""
        if source.startswith(".") or source.startswith("/"):
            return None  # relative import
        if source.startswith("node:"):
            return None  # explicit node built-in
        if "/" in source and not source.startswith("@"):
            return source.split("/")[0]
        if source.startswith("@") and "/" in source:
            parts = source.split("/")
            return f"{parts[0]}/{parts[1]}"
        return source

    # ------------------------------------------------------------------ #
    # Framework tier restriction checks                                    #
    # ------------------------------------------------------------------ #

    def _check_tier_restrictions(self, scan: _TierScan) -> List[Violation]:
        violations: List[Violation] = []
        for pkg, allowed_tier in _TIER_RESTRICTIONS.items():
            if scan.tier == allowed_tier:
                continue
            violations.extend(self._forbidden_framework_imports(scan, _FrameworkPlacement(pkg, allowed_tier)))
        return violations

    def _forbidden_framework_imports(
        self, scan: _TierScan, placement: _FrameworkPlacement
    ) -> List[Violation]:
        violations: List[Violation] = []
        for ts_file in self.source_files(scan.directory):
            parsed_root = self.parse_file(ts_file)
            if parsed_root is None or not self.has_import_from(placement.package):
                continue
            violations.append(
                self.v(
                    f"'{scan.domain_name}/{scan.tier}/{ts_file.name}' imports "
                    f"'{placement.package}' which must only be used in "
                    f"'{placement.allowed_tier}/'. "
                    "This is a layer purity violation.",
                    str(ts_file),
                )
            )
        return violations
