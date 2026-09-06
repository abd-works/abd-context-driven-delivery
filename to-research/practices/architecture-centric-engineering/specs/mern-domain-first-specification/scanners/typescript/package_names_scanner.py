"""Scanner: validate npm package names and import path consistency.

Checks:
1. All package.json files under packages/ have valid npm scoped names
   following @scope/domain-tier pattern (no multiple slashes, no generics).
2. No placeholder scope names: @project, @acme, @app, @example, @myapp.
3. All TypeScript import statements that use the project @scope match a
   declared package name in some package.json (no phantom imports).
4. Import paths do not use filesystem-style multi-slash paths
   (e.g. @scope/domain/tier — invalid npm).
5. Each tier package's package.json name derives tier from folder name:
   shared → *-shared, server → *-server, client → *-client.
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


_PLACEHOLDER_SCOPES = frozenset({
    '@project', '@acme', '@app', '@example', '@myapp',
    '@your-app', '@yourapp', '@todo', '@sample', '@demo',
})

_VALID_SCOPE_RE = re.compile(r'^@[a-z0-9][a-z0-9\-\.]*$')
_VALID_PACKAGE_NAME_RE = re.compile(
    r'^@[a-z0-9][a-z0-9\-\.]*\/[a-z0-9][a-z0-9\-\.]*$'
)
_MULTI_SLASH_IMPORT_RE = re.compile(r"from\s+['\"](@[^'\"]+/[^'\"]+/[^'\"]+)['\"]")


class PackageNamesScanner(TypeScriptScanner):
    """Checks npm package names and TypeScript import path consistency."""

    def scan(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        violations: List[Dict[str, Any]] = []
        project_root = self._get_project_root(context)
        if project_root is None:
            return violations

        # Collect all declared package names
        declared_names: Set[str] = set()
        pkg_violations, declared_names = self._check_package_jsons(project_root)
        violations += pkg_violations

        # Check TypeScript import paths reference real packages
        violations += self._check_import_paths(project_root, declared_names)

        return violations

    # ------------------------------------------------------------------ #
    # package.json validation                                              #
    # ------------------------------------------------------------------ #

    def _check_package_jsons(
        self, project_root: Path
    ) -> tuple[List[Dict[str, Any]], Set[str]]:
        violations: List[Dict[str, Any]] = []
        declared_names: Set[str] = set()
        packages_dir = project_root / 'packages'
        if not packages_dir.exists():
            return violations, declared_names

        for pkg_json in sorted(packages_dir.rglob('package.json')):
            if 'node_modules' in pkg_json.parts:
                continue
            try:
                data = json.loads(pkg_json.read_text(encoding='utf-8'))
            except (json.JSONDecodeError, OSError):
                continue

            name: Optional[str] = data.get('name', '')
            if not name:
                continue

            declared_names.add(name)

            # Also register sub-path exports as valid import targets
            exports = data.get('exports', {})
            if isinstance(exports, dict):
                for export_key in exports:
                    if export_key != '.' and export_key.startswith('./'):
                        sub_path = export_key[2:]  # strip './'
                        declared_names.add(f'{name}/{sub_path}')

            # Placeholder scope check
            for placeholder in _PLACEHOLDER_SCOPES:
                if name.startswith(placeholder):
                    violations.append(self.v(
                        f"Package '{name}' uses a generic placeholder scope "
                        f"'{placeholder}'. Derive the scope from the "
                        "application's business purpose (e.g. @pawplace, "
                        "@taskflow, @shopfront).",
                        str(pkg_json),
                    ))
                    break

            # Multiple-slash check (only for the package name itself, not exports)
            if name.count('/') > 1:
                violations.append(self.v(
                    f"Package name '{name}' contains multiple slashes. "
                    "npm only allows @scope/name — flatten with hyphens: "
                    f"'{name.replace('/', '-', 1)}'.",
                    str(pkg_json),
                ))
                continue

            # Pattern check: must be @scope/domain-tier
            if name.startswith('@') and not _VALID_PACKAGE_NAME_RE.match(name):
                violations.append(self.v(
                    f"Package name '{name}' is not a valid scoped npm name. "
                    "Use @scope/domain-tier with lowercase letters and hyphens.",
                    str(pkg_json),
                ))

            # Tier name consistency: folder name should match tier suffix
            folder = pkg_json.parent
            tier_folder = folder.name  # e.g. 'shared', 'server', 'client'
            if tier_folder in ('shared', 'server', 'client'):
                expected_suffix = f'-{tier_folder}'
                if not name.endswith(expected_suffix):
                    violations.append(self.v(
                        f"Package in '{tier_folder}/' folder is named '{name}' "
                        f"but should end with '{expected_suffix}' to follow "
                        "@scope/domain-tier convention.",
                        str(pkg_json),
                    ))

        return violations, declared_names

    # ------------------------------------------------------------------ #
    # Import path validation                                               #
    # ------------------------------------------------------------------ #

    def _check_import_paths(
        self, project_root: Path, declared_names: Set[str]
    ) -> List[Dict[str, Any]]:
        violations: List[Dict[str, Any]] = []
        if not declared_names:
            return violations

        # Determine the project scope (e.g. @pawplace)
        scopes: Set[str] = {
            name.split('/')[0]
            for name in declared_names
            if name.startswith('@')
        }

        packages_dir = project_root / 'packages'
        tests_dir = project_root / 'tests'

        search_dirs = []
        if packages_dir.exists():
            search_dirs.append(packages_dir)
        if tests_dir.exists():
            search_dirs.append(tests_dir)

        for search_dir in search_dirs:
            for ts_file in self.get_all_source_files(search_dir):
                root = self.parse_file(ts_file)
                if root is None:
                    continue
                for imp in self.get_imports(root):
                    src = imp.source
                    if not src.startswith('@'):
                        continue
                    # Multi-slash import — exempt if declared as a sub-path export
                    if src.count('/') > 1:
                        if src in declared_names:
                            continue  # declared via package.json exports field
                        violations.append(self.v(
                            f"Import path '{src}' contains multiple slashes — "
                            "this is not a valid npm package name. "
                            "Use the flat @scope/domain-tier package name, "
                            "or declare sub-path exports in package.json.",
                            str(ts_file),
                            imp.start_line,
                        ))
                        continue
                    # Check scope belongs to this project
                    scope = src.split('/')[0]
                    if scope not in scopes:
                        continue
                    # Package must be declared
                    if src not in declared_names:
                        violations.append(self.v(
                            f"Import '{src}' references an undeclared package "
                            f"(not found in any package.json). Declared packages: "
                            f"{', '.join(sorted(declared_names))}.",
                            str(ts_file),
                            imp.start_line,
                        ))

        return violations


if __name__ == '__main__':
    run_scanner_main(PackageNamesScanner, 'use-valid-package-names')
