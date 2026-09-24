"""Scanner: validate npm package names and import path consistency.

Checks:
1. All package.json files under packages/ have valid npm scoped names
   following @scope/domain-tier pattern (no multiple slashes, no generics).
2. No placeholder scope names: @project, @acme, @app, @example, @myapp.
3. All TypeScript import statements that use the project @scope match a
   declared package name in some package.json (no phantom imports).
4. Import paths do not use filesystem-style multi-slash paths
   (e.g. @scope/domain/tier - invalid npm).
5. One domain package named ``@scope/domain`` with subpath exports
   ``./<domain>-server`` and ``./<domain>-client`` (not separate *-shared/*-server/*-client packages).
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Set, Tuple

from lern_scanner_base import TypeScriptScanner, Violation

_PLACEHOLDER_SCOPES = frozenset(
    {
        "@project", "@acme", "@app", "@example", "@myapp",
        "@your-app", "@yourapp", "@todo", "@sample", "@demo",
    }
)

_VALID_PACKAGE_NAME_RE = re.compile(r"^@[a-z0-9][a-z0-9\-\.]*\/[a-z0-9][a-z0-9\-\.]*$")


@dataclass
class _DeclaredPackages:
    names: Set[str]
    scopes: Set[str]


class PackageNamesScanner(TypeScriptScanner):
    """Checks npm package names and TypeScript import path consistency."""

    RULE = "use-valid-package-names"

    def scan(self, root: Path, files: List[Path]) -> List[Violation]:
        violations: List[Violation] = []
        project_root = root

        pkg_violations, declared_names = self._check_package_jsons(project_root)
        violations += pkg_violations
        violations += self._check_import_paths(project_root, declared_names)

        return violations

    # ------------------------------------------------------------------ #
    # package.json validation                                              #
    # ------------------------------------------------------------------ #

    def _check_package_jsons(self, project_root: Path) -> Tuple[List[Violation], Set[str]]:
        violations: List[Violation] = []
        declared_names: Set[str] = set()
        packages_dir = project_root / "packages"
        if not packages_dir.exists():
            return violations, declared_names

        for pkg_json in sorted(packages_dir.rglob("package.json")):
            if "node_modules" in pkg_json.parts:
                continue
            try:
                data = json.loads(pkg_json.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue

            name: Optional[str] = data.get("name", "")
            if not name:
                continue

            declared_names.add(name)

            exports = data.get("exports", {})
            if isinstance(exports, dict):
                for export_key in exports:
                    if export_key != "." and export_key.startswith("./"):
                        sub_path = export_key[2:]
                        declared_names.add(f"{name}/{sub_path}")

            for placeholder in _PLACEHOLDER_SCOPES:
                if name.startswith(placeholder):
                    violations.append(
                        self.v(
                            f"Package '{name}' uses a generic placeholder scope "
                            f"'{placeholder}'. Derive the scope from the "
                            "application's business purpose (e.g. @pawplace, "
                            "@taskflow, @shopfront).",
                            str(pkg_json),
                        )
                    )
                    break

            if name.count("/") > 1:
                violations.append(
                    self.v(
                        f"Package name '{name}' contains multiple slashes. "
                        "npm only allows @scope/name - flatten with hyphens: "
                        f"'{name.replace('/', '-', 1)}'.",
                        str(pkg_json),
                    )
                )
                continue

            if name.startswith("@") and not _VALID_PACKAGE_NAME_RE.match(name):
                violations.append(
                    self.v(
                        f"Package name '{name}' is not a valid scoped npm name. "
                        "Use @scope/domain-tier with lowercase letters and hyphens.",
                        str(pkg_json),
                    )
                )

            # Feature packages nest domain modules; skip process-boot-only dirs.
            parent_name = folder.parent.name if folder.parent else ""
            if parent_name == "packages":
                for legacy_suffix in ("-shared", "-server", "-client"):
                    if name.endswith(legacy_suffix):
                        violations.append(
                            self.v(
                                f"Package '{name}' uses the legacy tier suffix "
                                f"'{legacy_suffix}'. Use one feature package "
                                f"'@{name.split('/')[0][1:]}/{folder.name}' with "
                                "nested domain folders and subpath exports.",
                                str(pkg_json),
                            )
                        )
                        break

        return violations, declared_names

    # ------------------------------------------------------------------ #
    # Import path validation                                               #
    # ------------------------------------------------------------------ #

    def _check_import_paths(self, project_root: Path, declared_names: Set[str]) -> List[Violation]:
        if not declared_names:
            return []
        declared = _DeclaredPackages(
            names=declared_names,
            scopes={name.split("/")[0] for name in declared_names if name.startswith("@")},
        )
        violations: List[Violation] = []
        for ts_file in self._scoped_search_files(project_root):
            violations.extend(self._undeclared_scoped_imports(ts_file, declared))
        return violations

    def _scoped_search_files(self, project_root: Path) -> List[Path]:
        files: List[Path] = []
        for folder in (project_root / "packages", project_root / "tests"):
            if folder.exists():
                files.extend(self.get_all_source_files(folder))
        return files

    def _undeclared_scoped_imports(
        self, ts_file: Path, declared: _DeclaredPackages
    ) -> List[Violation]:
        parsed_root = self.parse_file(ts_file)
        if parsed_root is None:
            return []
        violations: List[Violation] = []
        for imp in self.get_imports(parsed_root):
            hit = self._scoped_import_hit(ts_file, imp, declared)
            if hit is not None:
                violations.append(hit)
        return violations

    def _scoped_import_hit(self, ts_file: Path, imp, declared: _DeclaredPackages):
        src = imp.source
        if not src.startswith("@"):
            return None
        if src.count("/") > 1:
            if src in declared.names:
                return None
            return self.v(
                f"Import path '{src}' contains multiple slashes - "
                "this is not a valid npm package name. "
                "Use the flat @scope/domain-tier package name, "
                "or declare sub-path exports in package.json.",
                str(ts_file),
                imp.start_line,
            )
        if src.split("/")[0] not in declared.scopes or src in declared.names:
            return None
        return self.v(
            f"Import '{src}' references an undeclared package "
            f"(not found in any package.json). Declared packages: "
            f"{', '.join(sorted(declared.names))}.",
            str(ts_file),
            imp.start_line,
        )
